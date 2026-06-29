# Security Policy 🛡️

## 🔒 Our Commitment
While **System Breach Protocol** simulates tactical network intrusions and mainframe exploits, the security of the actual codebase, user authentication terminal, and execution environment is treated with real-world priority. We are dedicated to ensuring a secure platform for all operators.

---

## ⚠️ Supported Versions
Only the current mainline release branch actively receives security updates and vulnerability patches. 

| Version | Supported          |
| ------- | ------------------ |
| v1.x    | ✅ Supported       |
| < v1.0  | ❌ End of Life     |

---

## 📨 Reporting a Vulnerability

If you discover a legitimate security vulnerability within the Pygame simulation loops, local database user profiles, or asset pipelines, please do not open a public GitHub issue. 

### Reporting Pipeline
1. Email your technical findings directly to: **tom@deller.co**
2. **Required Scope Info:**
   * Detailed breakdown of the vulnerability.
   * Steps to reproduce the exploit state (e.g., triggering uncontrolled memory leaks or breaking the local login database verification).
   * A brief Proof of Concept (PoC) script or description.

### Response Window
* **Acknowledgment:** I aim to acknowledge all valid reports within 48 hours.
* **Remediation:** A target timeline for an upstream patch will be coordinated with the reporter.

---

## 🏗️ Local Code Execution Security

Because **System Breach Protocol** runs entirely locally as an offline terminal engine, standard security practices apply:

* **Volatile Memory:** Temporary terminal values, active session counters, and glitch state frames are held strictly within volatile runtime RAM and are completely flushed by Pygame on `sys.exit()`.
* **Database Sanitation:** User profile creations handled via the login terminal are stored locally. Do not reuse real-world sensitive passwords for your local operative usernames.
* **Executable Verification:** If downloading the packaged standalone binary (`System Breach Protocol.exe`), verify that the file source matches the official repository release tags to ensure no third-party modifications to `main.py`.

## 🛡️ Executable Integrity & Antivirus Flags

* **Unsigned Executables**: Because System Breach Protocol is an independent open-source game, the Windows `.exe` files provided in the Releases are currently unsigned. 
* **Current Security Audit (v1.0.0)**: As of the latest release build, 70 out of 74 major antivirus engines have cleared the executable as entirely safe. Industry standards like Kaspersky, BitDefender, Sophos, and Malwarebytes consistently return a clean, undetected status. 
* **[View Latest VirusTotal Audit Report](https://www.virustotal.com/gui/file/dd89ab3fcdfa00fe9941257af567f23731d3bdec6923d73dd5b9f3d829ce3aed?nocache=1)**
* **Heuristic False Positives**: PyInstaller bundles the compressed Python runtime environment along with internal game scripts and images (`/assets`) into a single binary wrapper. Because this binary unpacks its data to volatile runtime directories on launch, a few automated machine-learning engines flag it as a generic threat (such as Microsoft's automated `Wacapew.C!ml` tag). These are false positives common to compiled, unsigned open-source Python applications.
* **Integrity Verification**: We strongly recommend verifying the SHA-256 Checksum provided in the release notes before running the standalone application:
  ```text
  SHA256: DD89AB3FCDFA00FE9941257AF567F23731D3BDEC6923D73DD5B9F3D829CE3AED
  ```
  
* **Manual Independent Auditing:** If your security profile restricts running unsigned binaries, you are highly encouraged to audit the raw source code locally or compile your own clean standalone binary from source using main.spec or System Breach Protocol.spec alongside the setup steps detailed in the README.md.

## 🛠️ Pre-Release Audit Checklist (Internal Maintenance)

To maintain structural runtime safety and prevent upstream package supply-chain compromises, the following checks must occur prior to generating production builds:

* **Vulnerability Assessment:** Execute a dependency audit on the active environment before building binaries:

```bash
pip-audit
```

* **Version Pinning:** Lock production dependencies explicitly to frozen versions inside `requirements.txt`.

* **Immutability Enforcement:** Avoid arbitrary "floating" versions (e.g., pygame>=2.5.0) in distribution environments to prevent malicious third-party upstream updates from embedding themselves into future .spec builds.