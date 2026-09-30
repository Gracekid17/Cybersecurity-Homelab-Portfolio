# 🛡️ Cybersecurity Homelab Portfolio

**Gideon Sarfo-Nyantakyi** | Aspiring GRC Analyst | ISSO | RMF Analyst  
📍 Waco, TX | 🔐 Active DoD Secret Security Clearance  
🎓 MS Cybersecurity Management – University of Illinois Springfield (Dec 2026) | GPA: 3.96  
📜 CompTIA Security+ CE | DoD FM Certification – Level 1

🔗 [LinkedIn](https://linkedin.com/in/gideon-sarfo-nyantakyi-535b55b7)

---

## Overview

This repository documents hands-on cybersecurity lab work conducted in a 
personal homelab environment running Kali Linux on VirtualBox. All labs are 
aligned to NIST SP 800-53 Rev. 5 controls and DoD RMF frameworks, targeting 
GRC, vulnerability management, and security operations competencies.

---

## 🖥️ Homelab Environment

| Component | Details |
|---|---|
| Host Machine | Lenovo IdeaPad, Intel i5-9300HF, 8GB RAM |
| Virtualization | Oracle VirtualBox |
| Primary OS | Kali Linux |
| Scanners | OpenVAS (Greenbone) GVM 26.17.0, Nmap 7.99|
| Frameworks | NIST SP 800-53 Rev. 5, NIST RMF, CMMC 2.0 |
| Target VM | Metasploitable 2 (intentionally vulnerable, isolated) |
| Lab Network | VirtualBox NAT Network "GRC-Lab" (10.0.2.0/24, IPv6 disabled) |

---

## 📁 Lab Index
| Lab | Title | Tools | NIST Controls | Status |
|---|---|---|---|---|
| 01 | [Vulnerability Assessment](01-Vulnerability-Assessment/) | OpenVAS GVM 26.17.0 | RA-5, SI-2, CA-7 | ✅ Complete |
| 02 | [Network Enumeration & Asset Inventory](02-Network-Enumeration/) | Nmap 7.99, Python, ss | CM-8, CM-7, SI-2, SC-45 | ✅ Complete |
| 03 | System Hardening & Verification Re-scan | Metasploitable 2, SCAP/STIG tools | CM-6, CM-7 | 🔲 Planned |
| 04 | System Security Plan (SSP) | NIST SP 800-53 Rev. 5 | PL-2, AC-1, IA-1 | 🔲 Planned |
| 05 | Continuous Monitoring & Log Analysis | Kali Linux logs | AU-6, CA-7, IR-4 | 🔲 Planned |


---

## 🎓 Academic Projects

| Project | Description |
|---|---|
| Blue Stripe Tech DoD Ready | RMF package for simulated DoD contractor (FISMA, CMMC 2.0, NIST SP 800-53) |
| Health Network BCP/BIA | Business continuity and impact analysis for healthcare organization |
| Mircom Ransomware Case Study | Incident response analysis and lessons learned |
| Network Footprinting Lab | Passive/active reconnaissance using OSINT tools |
| Asset Risk Analysis | Risk identification, likelihood/impact matrix, mitigation recommendations |

---

## 🏅 Certifications & Clearance

- ✅ CompTIA Security+ CE
- ✅ Active DoD Secret Security Clearance
- ✅ DoD FM Certification – Level 1
- ✅ Army Financial Management Certification
- 🔄 MS Cybersecurity Management (Dec 2026) – GPA 3.96

---

## 💼 Background

U.S. Army Veteran (MOS 36B – Financial Management Technician) with experience 
in financial operations, compliance, and audit at Fort Cavazos. Transitioning 
into cybersecurity GRC with hands-on RMF, FISMA, CMMC 2.0, and NIST SP 800-53 
experience through graduate coursework and self-directed homelab practice.
