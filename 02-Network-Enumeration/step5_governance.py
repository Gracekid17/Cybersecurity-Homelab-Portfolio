#!/usr/bin/env python3
"""
step5_governance.py - Lab 02, Step 5 (CM-8 governance review)
Records the system owner's decisions in the asset inventory:
  - fills governance fields for the scanned asset (AST-001)
  - adds components the network scan could not list (scanner, gateway, DHCP)
Safe to re-run: existing rows are updated, not duplicated.
"""
import csv
from pathlib import Path

INV = Path("inventory/asset-inventory.csv")
OWNER = "Gideon Sarfo-Nyantakyi (lab owner)"

# Decisions for the asset the scanner found (fields to fill in)
UPDATES = {
    "AST-001": {
        "hostname": "metasploitable",
        "system_owner": OWNER,
        "component_role": "Internal web server (assessment target)",
        "criticality": "Moderate",
        "in_boundary": "Yes",
        "authorized": "Yes",
        "notes": "Hostname verified from login prompt and Nmap service info (no DNS in lab). "
                 "30 open TCP services; 28 not in authorized PPS baseline (see POA&M). "
                 "IP assigned by DHCP; track by MAC.",
    },
}

# Components the network scan could not list
NEW_ROWS = [
    {
        "asset_id": "AST-002", "ip_address": "10.0.2.15", "mac_address": "08:00:27:A1:6F:47",
        "nic_vendor": "Oracle VirtualBox virtual NIC", "hostname": "kali",
        "os_detected": "Kali Linux (host-reported)", "os_accuracy_pct": "",
        "open_port_count": "0", "open_services": "None network-exposed (verified with ss -tulpn)",
        "system_owner": OWNER, "component_role": "Vulnerability scanner / assessment workstation",
        "criticality": "Moderate", "in_boundary": "Yes", "authorized": "Yes",
        "last_scanned": "Tue Sep 29 2026 (host-based check)",
        "notes": "Omitted from Nmap output because --open hides hosts with no open ports. "
                 "Holds scan results (sensitive). Ollama service disabled - see POA&M-004.",
    },
    {
        "asset_id": "AST-003", "ip_address": "10.0.2.1", "mac_address": "52:54:00:12:35:00",
        "nic_vendor": "QEMU virtual NIC", "hostname": "",
        "os_detected": "Not assessed", "os_accuracy_pct": "",
        "open_port_count": "", "open_services": "Not assessed",
        "system_owner": "VirtualBox (hypervisor-provided)", "component_role": "Virtual NAT gateway",
        "criticality": "N/A", "in_boundary": "No", "authorized": "Yes",
        "last_scanned": "Tue Sep 29 12:26 2026 (discovery only)",
        "notes": "Out of boundary: provided and managed by the hypervisor. Documented, not assessed. "
                 "Default route per ip route.",
    },
    {
        "asset_id": "AST-004", "ip_address": "10.0.2.2", "mac_address": "08:00:27:BF:D5:24",
        "nic_vendor": "Oracle VirtualBox virtual NIC", "hostname": "",
        "os_detected": "Not assessed", "os_accuracy_pct": "",
        "open_port_count": "", "open_services": "Not assessed",
        "system_owner": "VirtualBox (hypervisor-provided)", "component_role": "DHCP server (NAT Network)",
        "criticality": "N/A", "in_boundary": "No", "authorized": "Yes",
        "last_scanned": "Tue Sep 29 12:26 2026 (discovery only)",
        "notes": "Initially unidentified; verified as DHCP server via dhcp_server_identifier "
                 "(nmcli). Out of boundary: hypervisor-provided.",
    },
]

with open(INV, newline="", encoding="utf-8") as fh:
    reader = csv.DictReader(fh)
    fields = reader.fieldnames
    rows = list(reader)

by_id = {r["asset_id"]: r for r in rows}
for asset_id, changes in UPDATES.items():
    if asset_id in by_id:
        by_id[asset_id].update(changes)
    else:
        print(f"[!] {asset_id} not found - check the inventory file")

for new in NEW_ROWS:
    if new["asset_id"] in by_id:
        by_id[new["asset_id"]].update(new)
    else:
        rows.append(new)
        by_id[new["asset_id"]] = new

rows.sort(key=lambda r: r["asset_id"])
with open(INV, "w", newline="", encoding="utf-8") as fh:
    writer = csv.DictWriter(fh, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

print(f"[+] Inventory updated: {len(rows)} components")
for r in rows:
    print(f"    {r['asset_id']}  {r['ip_address']:<10}  boundary={r['in_boundary']:<3}  {r['component_role']}")
