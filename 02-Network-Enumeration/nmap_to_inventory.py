#!/usr/bin/env python3
"""
nmap_to_inventory.py
Convert Nmap XML output into a NIST SP 800-53 CM-8 system component inventory,
with an optional CM-7 comparison against an authorized ports/services baseline.

Usage:
  python3 nmap_to_inventory.py scans/02-inventory-scan.xml -o inventory
  python3 nmap_to_inventory.py scans/02-inventory-scan.xml -o inventory -b authorized-baseline.csv

Outputs (in the -o directory):
  asset-inventory.csv          one row per live host  (CM-8)
  service-inventory.csv        one row per open port   (CM-8 / CM-7)
  unauthorized-services.csv    services not in baseline (CM-7, only with -b)

Governance columns (owner, role, criticality, boundary, authorized) are left
blank on purpose: a scanner can discover components, but only a person can
decide who owns them and whether they belong in the authorization boundary.
"""
import argparse
import csv
import ipaddress
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ASSET_FIELDS = [
    "asset_id", "ip_address", "mac_address", "nic_vendor", "hostname",
    "os_detected", "os_accuracy_pct", "open_port_count", "open_services",
    "system_owner", "component_role", "criticality", "in_boundary",
    "authorized", "last_scanned", "notes",
]
SERVICE_FIELDS = [
    "asset_id", "ip_address", "port", "protocol", "service", "product",
    "version", "extra_info", "baseline_status", "justification",
]


def ip_sort_key(host):
    try:
        return ipaddress.ip_address(host["ip"])
    except ValueError:
        return ipaddress.ip_address("255.255.255.255")


def parse_nmap_xml(xml_path):
    try:
        root = ET.parse(xml_path).getroot()
    except (ET.ParseError, FileNotFoundError) as err:
        sys.exit(f"[!] Could not read {xml_path}: {err}")

    scan_meta = {
        "started": root.get("startstr", ""),
        "args": root.get("args", ""),
        "version": root.get("version", ""),
    }

    hosts = []
    for host in root.findall("host"):
        status = host.find("status")
        if status is None or status.get("state") != "up":
            continue

        ip = mac = vendor = ""
        for addr in host.findall("address"):
            kind = addr.get("addrtype")
            if kind in ("ipv4", "ipv6"):
                ip = addr.get("addr", "")
            elif kind == "mac":
                mac = addr.get("addr", "")
                vendor = addr.get("vendor", "")

        hn = host.find("hostnames/hostname")
        osmatch = host.find("os/osmatch")

        services = []
        for port in host.findall("ports/port"):
            state = port.find("state")
            if state is None or state.get("state") != "open":
                continue
            svc = port.find("service")
            attr = (lambda k: svc.get(k, "") if svc is not None else "")
            services.append({
                "port": port.get("portid", ""),
                "protocol": port.get("protocol", ""),
                "service": attr("name"),
                "product": attr("product"),
                "version": attr("version"),
                "extra_info": attr("extrainfo"),
            })

        hosts.append({
            "ip": ip,
            "mac": mac,
            "vendor": vendor,
            "hostname": hn.get("name", "") if hn is not None else "",
            "os": osmatch.get("name", "") if osmatch is not None else "",
            "os_accuracy": osmatch.get("accuracy", "") if osmatch is not None else "",
            "services": services,
        })

    hosts.sort(key=ip_sort_key)
    return scan_meta, hosts


def load_baseline(path):
    """Baseline CSV columns: ip_address,port,protocol,service,justification.
    Use * in ip_address to authorize a port/protocol on every host."""
    baseline = {}
    try:
        with open(path, newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                if not row.get("port"):
                    continue
                key = (row["ip_address"].strip(), row["port"].strip(),
                       row["protocol"].strip().lower())
                baseline[key] = row.get("justification", "").strip()
    except FileNotFoundError:
        sys.exit(f"[!] Baseline file not found: {path}")
    return baseline


def check_baseline(ip, svc, baseline):
    for key in ((ip, svc["port"], svc["protocol"]), ("*", svc["port"], svc["protocol"])):
        if key in baseline:
            return "Authorized", baseline[key]
    return "NOT IN BASELINE", ""


def main():
    ap = argparse.ArgumentParser(description="Nmap XML -> CM-8 inventory CSVs")
    ap.add_argument("xml", help="Nmap XML file (from -oX or -oA)")
    ap.add_argument("-o", "--outdir", default="inventory", help="output directory")
    ap.add_argument("-b", "--baseline", help="authorized ports/services baseline CSV")
    args = ap.parse_args()

    meta, hosts = parse_nmap_xml(args.xml)
    if not hosts:
        sys.exit("[!] No live hosts found in the XML. Check the scan scope.")

    baseline = load_baseline(args.baseline) if args.baseline else None
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    asset_rows, service_rows = [], []
    for i, h in enumerate(hosts, start=1):
        asset_id = f"AST-{i:03d}"
        asset_rows.append({
            "asset_id": asset_id,
            "ip_address": h["ip"],
            "mac_address": h["mac"],
            "nic_vendor": h["vendor"],
            "hostname": h["hostname"],
            "os_detected": h["os"],
            "os_accuracy_pct": h["os_accuracy"],
            "open_port_count": len(h["services"]),
            "open_services": "; ".join(
                f'{s["port"]}/{s["protocol"]} {s["service"]}' for s in h["services"]),
            "last_scanned": meta["started"],
        })
        for s in h["services"]:
            status, why = check_baseline(h["ip"], s, baseline) if baseline else ("", "")
            service_rows.append({"asset_id": asset_id, "ip_address": h["ip"],
                                 **s, "baseline_status": status, "justification": why})

    with open(outdir / "asset-inventory.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=ASSET_FIELDS)
        w.writeheader()
        w.writerows(asset_rows)

    with open(outdir / "service-inventory.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=SERVICE_FIELDS)
        w.writeheader()
        w.writerows(service_rows)

    print(f"[+] Scan started : {meta['started']}")
    print(f"[+] Nmap command : {meta['args']}")
    print(f"[+] Live hosts   : {len(asset_rows)}")
    print(f"[+] Open services: {len(service_rows)}")
    print(f"[+] Wrote {outdir/'asset-inventory.csv'} and {outdir/'service-inventory.csv'}")

    if baseline is not None:
        flagged = [r for r in service_rows if r["baseline_status"] == "NOT IN BASELINE"]
        with open(outdir / "unauthorized-services.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=SERVICE_FIELDS)
            w.writeheader()
            w.writerows(flagged)
        print(f"[!] Services not in baseline (CM-7 candidates): {len(flagged)}")
        print(f"[+] Wrote {outdir/'unauthorized-services.csv'}")


if __name__ == "__main__":
    main()
