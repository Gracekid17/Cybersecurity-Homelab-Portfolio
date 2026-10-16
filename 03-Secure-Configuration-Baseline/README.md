# Lab 03 — Secure Configuration Baseline & Re-scan

2026-10-08 · updated 2026-10-16 · @Gracekid

## Executive summary

Hardening raised the CIS Level 1 Server score on `lab03-target` from 68.83 to 96.59, and every one of the 112 baseline failures now has a documented disposition. The target is 100% dispositioned, not 100% passing: the profile contains mutually exclusive firewall rules, so a perfect score is not achievable.

**Objective:** establish, measure, and document a secure configuration baseline for one Ubuntu server, and decide for each gap whether to remediate it, accept the risk, or mark it not applicable.

| Measure | Baseline | After (CIS L1 Server) | After (tailored baseline) |
|---|---|---|---|
| Score (OpenSCAP default scoring) | 68.83 | 96.59 | 97.58 |
| Rules passed | 231 | 348 | 346 |
| Rules failed | 112 | Open question: count not captured | 4 |
| Not applicable | 65 | — | 48 |
| Pending OS updates | 50 (35 security) | 0 | 0 |

**Disposition of the 112 baseline failures:** 102 remediate, 7 not applicable, 3 risk accepted. After remediation, 4 residual findings remained: 1 fixed by command after the re-scan and 3 moved to the POA&M.

**Authenticated vulnerability scan (2026-10-16):** a credentialed GVM scan of `lab03-target` logged in over SSH as the dedicated `gvmscan` account and ran local security checks against the hardened system. It found **0 Critical, 0 High, 2 Medium, 1 Low**. The Low finding (TCP timestamps) was remediated and a rescan confirmed it gone; the two Medium findings are CPU hardware flaws whose mitigation is inherited from the host and are risk-accepted. This closes **POA&M-002**, 15 days ahead of its October 31 date.

**Frameworks:** NIST SP 800-53 Rev 5 (CM-2, CM-6, CM-7, RA-5, RA-5(5), CA-7, SI-2), NIST SP 800-171 Rev 2 (3.4.1, 3.4.2, 3.4.6, 3.4.7), ISO/IEC 27001:2022 (A.8.9).

## Environment and scope

One system is in scope: a purpose-built Ubuntu Server VM, assessed and hardened from a separate Kali scanner on an isolated lab network.

| Component | Detail |
|---|---|
| Target system | `lab03-target`, Ubuntu Server 24.04.5 LTS, kernel 6.8.0-146-generic |
| Target hardware (VM) | VirtualBox, 2 vCPU, 2048 MB RAM (reduced to 1024 MB for the authenticated scans to fit the 8 GB host), 25 GB disk, legacy BIOS boot, LVM, no disk encryption |
| Target build | Default server install, OpenSSH server, installer security updates; no snaps |
| Scanner | Kali Linux VM, 3 vCPU, 4096 MB RAM; rebuilt 2026-10-15 after the original VM crashed. 10.0.5.5 (originally 10.0.5.3) |
| Vulnerability scanner | GVM 25.04.0 (Kali package), gvmd 26.24.0, OSPd-OpenVAS 22.10.5, web interface (GSA) 26.17.0 |
| Vulnerability feed | Greenbone Community Feed, NVT version 202610150602, 190,247 NVTs loaded |
| Scan account | `gvmscan` on the target: SSH password credential, listed in `AllowUsers`, used only by GVM |
| Network | VirtualBox NAT Network `LabNet`, 10.0.5.0/24, DHCP; target at 10.0.5.4 |
| Assessment tool | OpenSCAP 1.3.9 (`openscap-scanner`, `openscap-utils`) |
| Benchmark content | SCAP Security Guide 0.1.82, `ssg-ubuntu2404-ds.xml` |
| Profile | CIS Ubuntu Linux 24.04 LTS Benchmark v1.0.0 (2024-08-26), Level 1 – Server |

**Out of scope:** the Kali scanner, the Metasploitable2 and MemForensicsLab VMs, and the Windows host running the GRC platform.

**Why Ubuntu 24.04 and not 26.04:** the ComplianceAsCode project had no CIS profile for Ubuntu 26.04 at the time of the lab, because CIS had not yet published a 26.04 benchmark. Staying on 24.04 was a deliberate decision, and the in-place upgrade offer to 26.04.1 was declined for the same reason.

## Configuration Baseline Standard

All Ubuntu 24.04 servers must be configured to the CIS Level 1 – Server benchmark, as tailored and approved below, and verified by automated scan.

**1. Purpose.** Define the minimum secure configuration for Linux servers so that settings are consistent, measurable, and auditable (NIST SP 800-53 CM-2, CM-6; NIST SP 800-171 3.4.1, 3.4.2; ISO/IEC 27001:2022 A.8.9).

**2. Scope.** Applies to every Ubuntu Server 24.04 LTS system the organization operates. Workstations and other operating systems are covered by separate baselines.

**3. Standard.**

- The approved baseline is the CIS Ubuntu Linux 24.04 LTS Benchmark v1.0.0, Level 1 – Server, delivered through SCAP Security Guide content.
- Deviations from the benchmark are allowed only when recorded in the tailoring file (`lab03-tailoring.xml`, profile `lab03_cis_l1_server_tailored`) and the deviation register, each with a justification.
- A risk-accepted deviation also requires a signed risk acceptance memo with compensating controls and a review date.
- New Linux OS versions are not deployed until a benchmark and SCAP content exist for them.

**4. Verification.**

- Each system is scanned against the tailored profile before entering service, after any significant change, and at least monthly.
- A failed rule must be remediated, added to the POA&M with a target date, or formally dispositioned.
- Scan results (HTML report and XML results) are retained as evidence.

**5. Roles.** The system owner maintains the baseline and approves deviations. The system administrator applies configurations. The security analyst runs verification scans and maintains the deviation register and POA&M.

## Methodology

The lab ran in six phases, each producing evidence before the next began.

1. **Scope.** Built a dedicated target VM, verified the build (`hostnamectl`, SSH socket listening on port 22), and took the snapshot "Clean install – pre-hardening" with 35 security updates pending. Moved the scanner and target onto `LabNet` and confirmed connectivity (4/4 pings, 0% loss). Verified the target's ED25519 host key fingerprint on first SSH connection.
2. **Baseline assessment.** Installed OpenSCAP and SSG 0.1.82, confirmed the `cis_level1_server` profile, and scanned. The scan of 343 applicable rules took 71 seconds. Result: 231 pass, 112 fail, score 68.83.
3. **Triage.** Extracted the 112 failures into a worksheet with a Python script (`failed_rules.py`), grouped them into five themes, and recorded a decision and justification for each. Findings were verified with commands before deciding, which exposed one scanner false positive.
4. **Remediation.** Took the snapshot "Pre-remediation – triage complete". Encoded the 10 deviations in a tailoring file, generated a 398-fix remediation script from it, reviewed the script, and ran it inside `tmux` with a full log. Applied manual fixes the script could not make, patched the OS, and rebooted twice to confirm persistence.
5. **Verification.** Re-scanned against both the original CIS profile (comparable to baseline) and the tailored profile (compliance with the approved baseline). On 2026-10-16, ran an authenticated GVM scan from Kali (Full and fast, SSH credential `gvmscan`), remediated its one Low finding, and rescanned to confirm. A delta report compares the two scans. This closed POA&M-002.
6. **Documentation.** This document, the triage worksheet, the tailoring file, and the evidence set.

**Change safeguards used during remediation:** snapshot before change, script review before execution, `sshd -t` and `visudo -c` validation before restarts, a second SSH session to test access before closing the first, and a root shell held open while editing sudo and SSH configuration.

## Triage summary and deviation register

Of 112 baseline failures, 102 were remediated and 10 became documented deviations. The full rule-by-rule worksheet is `lab03-triage.csv`.

**Failures by severity:** 4 high, 92 medium, 12 low, 4 unrated. Two groups, `sysctl` (23) and `sshd` (16), held over a third of all failures and were fixed through a few configuration files.

| Batch | Groups | Rules | Outcome |
|---|---|---|---|
| High severity | grub2, empty passwords (local and SSH) | 4 | 3 remediate, 1 not applicable |
| A. SSH hardening | sshd (excluding the high-severity rule) | 15 | All remediate |
| B. Kernel and network | sysctl, kernel modules | 29 | All remediate |
| C. Accounts and authentication | accounts, sudo, root path, firewall rules | 24 | 18 remediate, 3 accept, 3 not applicable |
| D. Files, mounts, partitions | file permissions, /dev/shm, /tmp, AppArmor boot | 16 | All remediate |
| E. Services, packages, monitoring | AIDE, AppArmor, banners, ufw, logging, cleartext clients | 24 | 21 remediate, 3 not applicable |
| **Total** |  | **112** | **102 remediate, 7 not applicable, 3 accept** |

### Deviation register

Each deviation below is excluded from the tailored profile and enforced by the tailoring file, so the generated remediation script cannot apply it.

| Rule ID | Decision | Justification |
|---|---|---|
| accounts_maximum_age_login_defs | Accept risk | Organization follows NIST SP 800-63B: no forced periodic password change. See risk acceptance memo. |
| accounts_password_set_max_life_existing | Accept risk | Same decision as above, applied to existing accounts. |
| account_disable_post_pw_expiration | Accept risk | Only takes effect after password expiry, which is not enforced. Inactive accounts are handled by periodic account review (AC-2). |
| grub2_uefi_password | Not applicable | System boots in legacy BIOS mode (verified: `/sys/firmware/efi` absent). `grub2_password` covers the BIOS boot loader. Scanner false positive. |
| set_nftables_base_chain | Not applicable | ufw is the chosen firewall; CIS directs that only one firewall method be configured. |
| set_nftables_loopback_traffic | Not applicable | As above. |
| set_nftables_table | Not applicable | As above. |
| nftables_rules_permanent | Not applicable | As above. |
| service_nftables_enabled | Not applicable | As above. |
| package_ufw_removed | Not applicable | Contradicts `check_ufw_active`. Both cannot pass; ufw was chosen. |

**Assumption:** the password-aging deviations assume the system is not in PCI DSS scope. PCI DSS 4.0 requires 90-day changes for password-only accounts, so these deviations would not hold for an in-scope system.

## Risk acceptance memo: password aging

The organization accepts the risk of not enforcing periodic password expiration on `lab03-target`, in line with NIST SP 800-63B, until the review date below.

| Field | Entry |
|---|---|
| System | `lab03-target` (Ubuntu Server 24.04.5 LTS) |
| Rules affected | `accounts_maximum_age_login_defs`, `accounts_password_set_max_life_existing`, `account_disable_post_pw_expiration` |
| Benchmark requirement | CIS Level 1 requires a maximum password age and disabling of accounts after password expiry |
| Risk | A compromised password remains valid until it is changed, rather than expiring on a schedule |
| Likelihood / impact | Low / Moderate |
| Approved by | @Gracekid, System Owner |
| Review date | 2027-10-07 |

**Rationale.** NIST SP 800-63B advises against forced periodic changes because they push users toward predictable patterns, such as incrementing a number or season. It requires a change only when there is evidence of compromise. Scheduled expiration therefore adds little protection and reduces password quality.

**Compensating controls.**

- Minimum password length of 14 or more and quality checks through `pam_pwquality` (IA-5(1)).
- Password reuse prevented through `pam_pwhistory` (IA-5(1)).
- Account lockout after repeated failed attempts through `pam_faillock` (AC-7).
- SSH limited to named users through `AllowUsers`, with root login disabled (AC-17, AC-6).
- Periodic review of accounts to disable inactive ones (AC-2).
- Mandatory password change on any evidence of compromise.

**Conditions.** This acceptance is void if the system enters PCI DSS scope, which requires 90-day changes for password-only accounts, or if any compensating control is removed. It must be re-evaluated at the review date.

## Authenticated vulnerability scan (GVM)

The OpenSCAP scans prove configuration compliance; the GVM scan checks the hardened system for known vulnerabilities from the inside. Logging in matters: unauthenticated scans only probe what the network exposes, while a credentialed scan reads installed packages and kernel state directly.

| Item | Baseline scan | Rescan |
|---|---|---|
| Report ID | ae19ce9a-52bf-4c28-a983-ae73d36a8708 | 282c9ad4-17c8-4111-b40a-038d3c9d0552 |
| Scan window (UTC) | 2026-10-16 12:22–12:44 | 2026-10-16 13:09–13:32 |
| Scan config | Full and fast, All IANA assigned TCP, alive test "Consider Alive" | Same |
| Authentication | SSH as `gvmscan`: **successful** ("SSH Login Successful For Authenticated Checks", "Authenticated Scan / LSC Info Consolidation") | **Successful** |
| Packages visible to scanner | ~729 (`dpkg -l` as `gvmscan`) | Same |
| Critical / High | 0 / 0 | 0 / 0 |
| Medium / Low | 2 / 1 | 2 / 0 |
| Highest severity | 5.5 (Medium) | 5.5 (Medium) |
| Scan errors | 0 | 1 (see limitation below) |

### Findings and disposition

| Finding | Severity | Disposition | Result |
|---|---|---|---|
| Missing Linux kernel mitigations: Processor MMIO Stale Data (INTEL-SA-00615) | 5.5 Medium | Accept risk, inherited from the host platform | Same in rescan; POA&M-016 |
| Missing Linux kernel mitigations: Speculative Store Bypass (SSB) | 5.5 Medium | Accept risk, inherited from the host platform | Same in rescan; POA&M-017 |
| TCP Timestamps Information Disclosure | 2.6 Low | Remediate | Disabled `net.ipv4.tcp_timestamps`; delta report shows the finding **Gone** |

**Why the CPU findings are inherited.** Both are processor hardware flaws. Their fixes depend on CPU microcode and on the hypervisor exposing mitigation features to guests, and both come from the Windows host and VirtualBox, not from Ubuntu. The guest kernel correctly reports itself vulnerable because VirtualBox does not pass those mitigations through. As with a cloud customer inheriting physical security from the provider, responsibility sits with the underlying platform.

**Scan limitation.** In the rescan, the NVT "SSH Brute Force Logins With Default Credentials" timed out after 900 seconds. The SSH hardening (limited authentication attempts, login delays) and `pam_faillock` slow every guess, which is the control working as intended (AC-7). The same check completed in the baseline scan with no finding, and `faillock` showed no failures recorded against `gsarfo` or `gvmscan` afterward. The feed did not include EPSS scores, so findings carry no exploit-likelihood rating.

## Risk acceptance memo: inherited CPU mitigations

The organization accepts the risk of the two missing CPU mitigations on `lab03-target`, because remediation sits with the host platform, until the review date below.

| Field | Entry |
|---|---|
| System | `lab03-target` (Ubuntu Server 24.04.5 LTS, VirtualBox guest) |
| Findings | Missing kernel mitigations for Processor MMIO Stale Data (INTEL-SA-00615) and Speculative Store Bypass, each 5.5 Medium |
| Risk | Malicious code already running on the guest could use speculative-execution side channels to read data it should not access |
| Likelihood / impact | Low / Moderate (exploitation needs local code execution; the lab network is isolated and the target runs no untrusted workloads) |
| Responsibility | Inherited: host CPU microcode (Windows host, BIOS/firmware) and hypervisor (VirtualBox) |
| Approved by | @Gracekid, System Owner |
| Review date | 2027-04-16, or sooner on a host BIOS, CPU, or VirtualBox change |

**Compensating controls.**

- Keep the host's BIOS/firmware, Windows updates (which deliver microcode), and VirtualBox current (SI-2).
- Run no untrusted code on the target; SSH limited to named accounts through `AllowUsers` (AC-17, AC-6).
- Lab network isolated on `LabNet` (SC-7).
- Rescan after any host platform change; close the acceptance if the findings clear.

**Conditions.** This acceptance is void if the target begins hosting untrusted or multi-tenant workloads, or if it moves to a platform where the operator controls microcode and hypervisor settings.

## POA&M updates

Three residual OpenSCAP findings move to the POA&M (POA&M-013 to 015). The authenticated GVM scan on 2026-10-16 closed POA&M-002 from Lab 01 and added four items (POA&M-016 to 019). Numbering continues from Lab 02 (POA&M-004 to 012).

| ID | Weakness | Control | Severity | Planned action | Scheduled completion | Status |
|---|---|---|---|---|---|---|
| POA&M-002 | Vulnerability scans run unauthenticated, missing host-level findings | RA-5(5) | Moderate | Run authenticated GVM scan from Kali against `lab03-target` using SSH credentials; add any scan account to `AllowUsers` | 2026-10-31 | **Closed 2026-10-16.** Scan authenticated as `gvmscan`; evidence: auth-evidence PDF, screenshots 01–02 |
| POA&M-013 | ufw allows all outbound traffic by default (`set_ufw_default_rule`) | SC-7(5) | Medium | Build an egress allow-list (DNS, NTP, HTTP/HTTPS for updates), test updates and time sync, then set default deny outbound | 2026-11-30 | Open |
| POA&M-014 | A listening port lacks a matching firewall rule, likely SSH on IPv6 (`ufw_rules_for_open_ports`) | SC-7 | Medium | Confirm with `ss -tlnp`; either bind SSH to IPv4 only or add an explicit IPv6 rule; re-scan | 2026-11-15 | Open |
| POA&M-015 | Some AppArmor profiles not in enforce or complain mode (`all_apparmor_profiles_in_enforce_complain_mode`) | AC-3(3), CM-7 | Medium | Run `aa-status` to identify the profiles; Ubuntu 24.04 ships some as unconfined by design. Test complain mode, or document as an accepted deviation | 2026-11-30 | Open |
| POA&M-016 | Missing kernel mitigation: Processor MMIO Stale Data (INTEL-SA-00615) | SI-2, SC-39 | Medium | Inherited from host. Keep host firmware, microcode, and VirtualBox current; rescan after platform changes | 2027-04-16 | Risk accepted |
| POA&M-017 | Missing kernel mitigation: Speculative Store Bypass | SI-2, SC-39 | Medium | As POA&M-016 | 2027-04-16 | Risk accepted |
| POA&M-018 | GVM accepts any password for its own users (password policy empty in `/etc/gvm/pwpolicy.conf`) | IA-5(1) | Low | Configure the password policy file to match the organization's standard; change the GVM admin password | 2026-11-15 | Open |
| POA&M-019 | No documented break-glass procedure for hardened systems; the only administrator was locked out and recovery needed rescue media | CP-10, AC-2 | Medium | Write a recovery runbook (GRUB password escrow, emergency account, rescue ISO location); test it on `lab03-target` | 2026-11-30 | Open |

**Closed after GVM rescan:** TCP Timestamps Information Disclosure (2.6 Low), found and fixed 2026-10-16 by setting `net.ipv4.tcp_timestamps = 0` in `/etc/sysctl.d/60-tcp-timestamps.conf` (CM-6, SC-7). The delta report marks it Gone.

**Closed after re-scan:** `permissions_local_var_log` failed because log files created during remediation (AIDE, sudo log) had group-write or world permissions. Fixed by removing those permissions from all files under `/var/log` with `find` and `chmod`, verified by command.

## Change log and operational impacts

Every change was made after a snapshot and verified before the next one; three changes had side effects that are now documented. Entries from 2026-10-15 onward cover the scanner rebuild and the authenticated scan.

| Date (UTC) | Change | Verification and impact |
|---|---|---|
| 2026-10-16 | Disabled TCP timestamps via `/etc/sysctl.d/60-tcp-timestamps.conf` | `sysctl net.ipv4.tcp_timestamps` returns 0; persists across reboots. GVM rescan and delta report confirm the finding is gone. |
| 2026-10-16 | Reset `gsarfo` and `gvmscan` passwords from Ubuntu rescue media (chroot); cleared the `gsarfo` lockout with `faillock --reset` | The account had locked after 4 failed logins and GRUB editing is password-protected, so boot-time recovery was blocked by design. New passwords met the `pam_pwquality` policy. Shell history cleared afterward. |
| 2026-10-16 | Target RAM reduced from 2048 MB to 1024 MB (ISO temporarily removed and memory restored after rescue) | Allowed the target and scanner to run together on the 8 GB host. |
| 2026-10-16 | GVM credential `lab03-gvmscan-ssh`, target `lab03-target-auth` (10.0.5.4), and task "Lab03 Authenticated Scan" created | SSH login from Kali as `gvmscan` tested manually first; `dpkg -l` returned ~729 packages. |
| 2026-10-15 | Kali scanner rebuilt from the 2026.2 VirtualBox image on `LabNet`; GVM installed and set up | `gvm-check-setup`: installation OK. Initial feed import took about 6 h 44 min for the SCAP CPE scoring step alone. |
| 2026-10-15 | Refreshed PostgreSQL collation after the glibc 2.42 → 2.43 upgrade; created the `gvmd` database | Resolved the collation-mismatch error that stopped `gvm-setup`. |
| 2026-10-08 | /tmp mounted as tmpfs (512 MB, nosuid, nodev, noexec) via /etc/fstab | Single mount confirmed after reboot. Made three previously not-applicable /tmp mount-option rules applicable; options set at the same time. |
| 2026-10-07 | OS patched (apt upgrade) | Pending updates 43 to 0. No new kernel. Deferred service restarts cleared by reboot. |
| 2026-10-07 | GRUB superuser grubadmin with PBKDF2 password; normal boot unrestricted; recovery entries disabled | Boots without a password; editing entries requires it. A first attempt left recovery mode unrestricted and was corrected. A GRUB package update could overwrite /etc/grub.d/10_linux, so re-scan after updates. |
| 2026-10-07 | SSH AllowUsers gsarfo added to 00-complianceascode-hardening.conf | Second-session login succeeded. Any new SSH account, including a GVM scan account, must be added. |
| 2026-10-07 | /snap/bin removed from sudo secure_path (/etc/sudoers.d/10-secure-path) | visudo check parsed OK; sudo whoami returned root. |
| 2026-10-07 | Remediation script applied (398 rules, about 10 minutes) | SSH banner, hardened ciphers, idle timeout of about 15 minutes, firewall active with SSH allowed only from 10.0.5.0/24. |
| 2026-10-07 | ufw rule added before remediation: SSH from 10.0.5.0/24 | Prevented lockout when the script enabled the firewall. |
| 2026-10-07 | OpenSCAP, unzip, curl installed for assessment | Updated shared libraries such as libcurl; recorded as assessment footprint. |

**Operational impacts:**

- **New software:** Postfix was installed as a dependency of AIDE. Verified listening on loopback only (IPv4 and IPv6 port 25), so it adds no network attack surface.
- **Disk:** root volume use rose from 41% to 63% of 11.21 GB, mostly from SSG content and the AIDE database.
- **Lockout behavior:** failed passwords, including mistyped sudo passwords, now count toward account lockout.
- **File permissions:** the stricter umask makes root-created files unreadable to other users, so scan outputs need chown before review.

## Lessons learned and control mapping

The main lesson: compliance is a set of documented decisions, not a score. A default install met only about two-thirds of the benchmark, and the benchmark itself calls its content a catalog, not a checklist.

- **New is not secure.** A freshly installed, fully default server scored 68.83 and was already 35 security updates behind.
- **Secure by default is not secure by evidence.** Several settings, such as rejecting empty SSH passwords, were already the default but failed because they were not explicitly configured. Auditors need the setting on record.
- **Scanners produce false positives.** The UEFI boot loader rule failed on a BIOS system. Verifying with a command before deciding kept a wrong remediation out of the plan.
- **Benchmarks can contradict themselves.** The profile requires ufw to be both active and removed, so the realistic target is 100% dispositioned.
- **The same rule can need opposite decisions on different systems.** IP forwarding was disabled on this server but must stay enabled on the Docker host running the GRC platform.
- **Fixes have side effects.** Remediation installed Postfix, made new /tmp rules applicable, and changed how failed passwords behave. A re-scan and a careful review caught each one.
- **Verify the fix, not just the command.** The first GRUB change left recovery mode open. Checking the generated boot configuration exposed the gap.
- **Frameworks interact.** CIS and NIST SP 800-63B disagree on password expiration, and PCI DSS would override the chosen position.
- **Hardening can lock out the defender.** The lockout policy and GRUB password both worked exactly as designed, and together they blocked the only administrator. A hardened system needs a tested break-glass procedure and kept recovery media (POA&M-019).
- **Prove the scan was authenticated.** A credentialed scan that fails to log in still finishes and looks normal. The evidence is the "SSH Login Successful" result and the Auth indicator, not the task status.
- **Size the scanner.** On a 4 GB VM, the first GVM feed import took over six hours, mostly one database update. A scanner that cannot keep its feed current cannot support continuous monitoring (CA-7), so capacity belongs in tool planning.
- **Not every finding is the system's to fix.** The CPU mitigations depend on the host and hypervisor. Recognizing inherited responsibility avoids chasing a fix the guest cannot make.
- **Read the delta direction.** GVM's delta report labels results relative to whichever report is selected first; comparing in the wrong order showed a fixed finding as "new".

### Control mapping

| Remediation area | NIST SP 800-53 Rev 5 | NIST SP 800-171 Rev 2 | ISO/IEC 27001:2022 |
|---|---|---|---|
| Secure baseline and settings | CM-2, CM-6 | 3.4.1, 3.4.2 | A.8.9 |
| Unused services, packages, kernel modules | CM-7 | 3.4.6, 3.4.7 | A.8.9 |
| Patching | SI-2 | 3.14.1 | A.8.8 |
| Vulnerability and compliance scanning | RA-5 | 3.11.2 | A.8.8 |
| SSH and remote access | AC-17, SC-8, SC-13 | 3.1.12, 3.13.8 | A.8.20, A.8.24 |
| Passwords and lockout | IA-5(1), AC-7 | 3.5.7, 3.5.8, 3.1.8 | A.5.17 |
| Least privilege, sudo, su | AC-6 | 3.1.5, 3.1.7 | A.8.2 |
| Session timeout and login banner | AC-12, AC-8 | 3.1.11, 3.1.9 | A.8.5 |
| Firewall and network parameters | SC-7 | 3.13.1, 3.13.6 | A.8.20 |
| Logging and time sync | AU-2, AU-8, AU-9, AU-12 | 3.3.1, 3.3.7, 3.3.8 | A.8.15, A.8.17 |
| File integrity monitoring (AIDE) | SI-7 | 3.14.6 | A.8.16 |
| Boot loader protection | AC-3 | 3.1.1 | A.8.9 |
| Authenticated vulnerability scanning | RA-5, RA-5(5) | 3.11.2 | A.8.8 |
| Find → fix → verify (rescan and delta) | CA-7, RA-5 | 3.12.3 | A.8.8 |
| Inherited CPU mitigations (host microcode, hypervisor) | SI-2, SC-39 | 3.14.1 | A.8.8 |
| Recovery and break-glass access | CP-10, AC-2 | 3.1.1 | A.5.29 |

## Evidence index

Evidence lives in `03-Secure-Configuration-Baseline/evidence/`. The first table lists the OpenSCAP files from the hardening phase; the second lists the authenticated-scan evidence added on 2026-10-16.

### OpenSCAP hardening evidence

| File | Content | Location |
|---|---|---|
| lab03-baseline-report.html | Baseline OpenSCAP report (68.83) | Kali, ~/lab03-evidence |
| lab03-baseline-results.xml | Baseline machine-readable results | Kali, ~/lab03-evidence |
| lab03-triage.csv | 112 failures with decisions and justifications | Kali, ~/lab03-evidence |
| failed_rules.py | Script that extracts failed rules to CSV | Kali, ~/lab03-evidence |
| lab03-tailoring.xml | Approved baseline: CIS L1 Server minus 10 deviations | Target, home folder |
| lab03-remediate.sh | Generated remediation script (398 fixes) | Target, home folder |
| lab03-remediation.log | Full output of the remediation run | Target, home folder |
| lab03-pending-updates.txt | Updates pending before patching | Target, home folder |
| lab03-patching.log | Output of the patch run | Target, home folder |
| lab03-after-report.html | After scan, original CIS profile (96.59) | Target, home folder |
| lab03-after-results.xml | After scan results, original profile | Target, home folder |
| lab03-after-tailored-report.html | After scan, tailored profile (97.58) | Target, home folder |
| lab03-after-tailored-results.xml | After scan results, tailored profile | Target, home folder |
| lab03-after-fails.csv | The 4 residual failures | Target, home folder |

### Authenticated GVM scan evidence (2026-10-16)

| File | Content | Supports |
|---|---|---|
| lab03-gvm-scan-baseline-2026-10-16.pdf | Full baseline scan report (2 Medium, 1 Low) | RA-5 |
| lab03-gvm-baseline-auth-evidence-2026-10-16.pdf | Baseline report filtered to the authentication results | RA-5(5), POA&M-002 |
| lab03-gvm-scan-rescan-2026-10-16.pdf | Rescan report after the TCP timestamps fix (2 Medium) | RA-5 |
| lab03-gvm-delta-baseline-vs-rescan.pdf | Delta report: TCP Timestamps Gone, CPU findings Same | CA-7 |
| 01-auth-scan-ssh-login-success.png | SSH Login Successful and LSC Info Consolidation results | RA-5(5) |
| 02-auth-scan-hosts-auth.png | Hosts tab with the Auth indicator for 10.0.5.4 | RA-5(5) |
| 03-delta-tcp-timestamps-gone.png | Delta results view | CA-7 |
| 03b-delta-report-comparison-info.png | Which two reports the delta compares | CA-7 |
| 04-tcp-timestamps-disabled.png | `sysctl net.ipv4.tcp_timestamps = 0` | CM-6, SC-7 |
| 05-faillock-lockout-ac7.png | Console lockout after 4 failed logins | AC-7 |
| 06-pwquality-rejections-ia5.png | Weak passwords rejected by policy | IA-5(1) |
| 07-grub-password-prompt.png | GRUB edit requires a password | AC-3 |
| 08-ssh-allowusers.png | `AllowUsers gsarfo gvmscan` | AC-3, AC-17 |
| 09-sysctl-baseline-persisted.png | Hardened kernel network settings still in effect | CM-6 |
| 10-gvm-check-setup-ok.png | Rebuilt scanner passes its health check | RA-5 |

**Screenshots to include (hardening phase):** build verification (`hostnamectl`, SSH socket), LabNet ping, baseline Evaluation Characteristics and Compliance and Scoring, the three verification commands for the high-severity rules, the second-session SSH login with banner, `ufw status verbose`, and the single /tmp tmpfs mount after reboot.

**Do not publish:** any screenshot or file showing the GRUB PBKDF2 hash or `/boot/grub/grub.cfg` contents, and any credentials, including the GVM setup output that prints the admin password and any login screen with a password visible.

- [ ] Copy the ten target files to Kali with scp
- [ ] Upload all evidence to the GitHub repo
- [x] Run the authenticated GVM scan to close POA&M-002
- [x] Upload the GVM scan PDFs and screenshots to `evidence/`
- [ ] Snapshot `lab03-target` as "post-remediation – auth-scan complete (2026-10-16)"
- [ ] Update the main README lab index: Lab 03 complete, POA&M-002 closed
