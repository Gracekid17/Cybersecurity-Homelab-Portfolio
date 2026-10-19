# Lab 04 — System Security Plan & Control Assessment

2026-10-19 · @Gracekid

## Executive summary

I wrote a System Security Plan (SSP) for `lab03-target` and assessed it in a GRC platform against a tailored set of 23 NIST SP 800-53 Rev 5 controls. Of the 23, 14 are implemented, 8 are partially implemented and 1 is planned. All 9 gaps are tracked in the POA&M.

**Objective:** take the hardened system from Lab 03 through the RMF documentation and assessment steps. That means categorizing it, defining its boundary, selecting and tailoring controls, writing an implementation statement for each one, linking evidence, and recording the gaps as POA&M items.

| Result | Controls | Share |
|---|---|---|
| Implemented (Compliant) | 14 | 61% |
| Partially implemented | 8 | 35% |
| Planned (Non compliant) | 1 | 4% |
| **Total assessed** | **23** | |

**Evidence:** 6 evidence records are linked to the controls 35 times in CISO Assistant. I verified every link against the exported audit report. CP-10 has no evidence because it isn't implemented.

**POA&M:** two new items came out of the assessment (POA&M-020 for MFA and POA&M-021 for logging). A third finding on the scanner (POA&M-022) was opened and closed on the same day.

**Frameworks:** NIST SP 800-37 Rev 2 (RMF steps: Categorize, Select, Implement, Assess), NIST SP 800-53 Rev 5, FIPS 199.

## Deliverables

| File | What it is |
|---|---|
| [`SSP-lab03-target.md`](SSP-lab03-target.md) | The System Security Plan: categorization, boundary, inventory, ports and services, tailoring, 23 implementation statements, contingency objectives, continuous monitoring, risk acceptances, POA&M |
| [`control-matrix.csv`](control-matrix.csv) | One row per control: status, result, implementation statement, evidence, related POA&M |
| `evidence/lab04-ciso-assistant-audit-posture-assessed.pdf` | Audit report exported from CISO Assistant, trimmed to the pages with the 23 assessed controls |

## Environment

| Component | Detail |
|---|---|
| System assessed | `lab03-target` (SYS-001), Ubuntu Server 24.04.5 LTS, 10.0.5.4 on `LabNet` |
| Supporting asset | Kali Linux GVM scanner, 10.0.5.5 |
| GRC platform | CISO Assistant Community (intuitem), self-hosted in Docker Desktop on WSL Ubuntu, `https://localhost:8443` |
| Framework library | NIST SP 800-53 revision 5 (1,189 requirements, including enhancements) |
| Categorization | FIPS 199 Low / Low / Low |

## Methodology

I worked in five steps, and each step produced evidence before I moved to the next.

1. **Set up the GRC platform.** Restarted CISO Assistant (the containers had been removed but the images and data were still there) and created the records in order: domain `Cybersecurity-Homelab` (DOM-001), perimeter `LabNet – lab03-target` (SYS-001), primary asset `lab03-target` (AST-001) with C/I/A set to Low and RTO 24 h / RPO 24 h / MTD 72 h, supporting asset `Kali-GVM-Scanner` (AST-002), the 800-53 Rev 5 framework, and the audit ASMT-001.
2. **Tailor the control set.** Started from the 800-53 Low baseline and kept the 23 base controls that Labs 01–04 produced direct evidence for. Policy controls ("-1"), PE and PS were excluded. The reasons are in SSP Section 7.
3. **Verify before writing.** Before writing a statement, I checked the system instead of assuming. On `lab03-target`, auditd was inactive, journald and rsyslog were active, and unattended-upgrades was enabled. On the scanner, the time zone and NTP had reverted after the rebuild, so I fixed them (POA&M-022).
4. **Assess in CISO Assistant.** For each of the 23 controls I set Result and Status, pasted the implementation statement into the observation field, and linked evidence records that point to the published evidence on GitHub.
5. **Export and check.** Exported the audit report and the requirements data, and checked them against the matrix: 23 results, 35 evidence links, and no sensitive data in the report.

## Assessment results

| Family | Implemented | Partially implemented | Planned |
|---|---|---|---|
| AC — Access Control | AC-3, AC-6, AC-7, AC-8, AC-12, AC-17 | AC-2 | |
| AU — Audit and Accountability | | AU-2, AU-12 | |
| CA — Assessment, Authorization, Monitoring | CA-5 | CA-7 | |
| CM — Configuration Management | CM-2, CM-6, CM-8 | CM-7 | |
| CP — Contingency Planning | | | CP-10 |
| IA — Identification and Authentication | IA-5 | IA-2 | |
| RA — Risk Assessment | RA-5 | RA-3 | |
| SC — System and Communications Protection | | SC-7 | |
| SI — System and Information Integrity | SI-2, SI-7 | | |

The full implementation statements are in SSP Section 8.

## POA&M updates

Numbering continues from Lab 03 (POA&M-013 to 019). The Lab 02 items (POA&M-004 to 012) are for the old scanner and Metasploitable2, which are outside this SSP's boundary, so they stay in the master POA&M.

| ID | Weakness | Control | Severity | Planned action | Scheduled completion | Status |
|---|---|---|---|---|---|---|
| POA&M-020 | No MFA for privileged SSH access | IA-2(1) | Medium | Require an SSH key plus password, or key plus TOTP, for `gsarfo`; keep `gvmscan` key-only | 2026-11-30 | Open |
| POA&M-021 | No auditd, centralized log collection, or log review | AU-2, AU-12, CA-7 | Medium | Lab 05: deploy log collection and analysis, define a review cadence, evaluate auditd | Lab 05 | Open |
| POA&M-022 | Rebuilt scanner reverted to America/New_York with NTP inactive; the POA&M-012 fix was lost in the rebuild | AU-8, CM-2 | Low | Set the time zone to America/Chicago and enable NTP; verify with `timedatectl` | 2026-10-19 | **Closed 2026-10-19.** Evidence: `lab04-02-kali-time-sync.png` |

**Re-baseline needed (master POA&M):** POA&M-005 (Metasploitable2 backdoored services, Critical) was due 2026-10-01 and is overdue. It needs a new date and a reason, for example: "rebuild deferred to the Metasploitable hardening lab; host remains isolated."

## Lessons learned

- **Rebuilding a system can undo its remediations.** The scanner's time-sync fix from Lab 02 was gone after the rebuild. Supporting assets need their own documented baseline too.
- **Check before you write.** Three statements depended on facts I hadn't confirmed: auditd, journald and unattended-upgrades. Checking them on the system changed two control results and strengthened a third.
- **Search results can mislead.** A browser search of a large HTML report returned "not found" for rules that were present, because the page hadn't fully loaded. A direct command on the system was faster and gave a clearer answer.
- **Assessment status is not control status.** CP-10's assessment is Done even though the control is Non compliant. The gap goes in the POA&M, not into an unfinished assessment.
- **Tailoring has to be documented.** Leaving 1,166 requirements unassessed is defensible only because the SSP explains why. The tool's summary page ("Compliant on 1.2% of 1189") shows what the result looks like without that context.
- **Evidence has a shelf life.** Evidence records carry expiry dates (scan evidence after 30 days, risk memos at their review dates), so the GRC tool flags when evidence goes stale. That supports CA-7.
- **A GRC tool doesn't replace the documents.** CISO Assistant holds the assessment record and the evidence links. The SSP explains the system and the reasoning behind each decision. A real authorization package needs both.

## Evidence index

Evidence lives in `04-System-Security-Plan/evidence/`. Lab 03 evidence is linked from its own folder, not copied.

| File | Content | Supports |
|---|---|---|
| step1a-domain.png | Domain `Cybersecurity-Homelab` created | Setup |
| step1b-perimeter.png | Perimeter SYS-001 | Authorization boundary |
| step1c-assets.png | AST-001 and AST-002 with dependency | CM-8 |
| step1d-framework.png | NIST SP 800-53 Rev 5 loaded | Control selection |
| step1e-audit.png | Audit ASMT-001 | CA-2 (self-assessment) |
| step3-audit-results.png | Compliance chart: 14 / 8 / 1 | Results |
| step4-associated-evidences.png | Evidence-to-control mapping | Evidence traceability |
| lab04-01-logging-patching.png | auditd inactive; journald and rsyslog active; unattended-upgrades enabled (2026-10-19 19:21 UTC) | AU-2, AU-12, SI-2 |
| lab04-02-kali-time-sync.png | Scanner time zone and NTP before and after the fix | AU-8, POA&M-022 |
| lab04-ciso-assistant-audit-posture-assessed.pdf | Exported audit report, 23 assessed controls | All |

**Do not publish:** CISO Assistant login details or screenshots that show passwords.

- [x] Set up CISO Assistant records (domain, perimeter, assets, framework, audit)
- [x] Verify logging and patching on `lab03-target`; fix scanner time sync
- [x] Assess 23 controls with implementation statements
- [x] Link evidence (35 links, verified against the export)
- [x] Export the audit report and check it for sensitive data
- [x] Write the SSP and control matrix
- [ ] Upload the SSP, matrix, README and evidence to GitHub
- [ ] Update the main README lab index: Lab 04 complete
- [ ] Re-baseline POA&M-005 in the master POA&M
