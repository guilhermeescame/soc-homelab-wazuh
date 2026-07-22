# Chapter 2 Closure: Endpoint and Detection Engineering

This document closes Chapter 2. It reviews the success criteria, maps the validated detection to MITRE ATT&CK, consolidates the versions and configuration the chapter added, records the limitations, and captures what the work taught. It is the deliverable of milestones C2-07 and C2-08.

The chapter's goals are in the [Scope](./08-chapter-2-scope.md); per-milestone status is in the [Roadmap](../ROADMAP.md). This closes the chapter as a whole and does not repeat what the individual documents cover.

## What the chapter delivered

Chapter 1 left the lab able to see. Its closure named the gap: individual events sit below the alert threshold, and turning telemetry into an alert is detection-engineering work. Chapter 2 did that work, end to end, for one technique.

Sysmon went onto the Windows endpoint with a documented configuration ([C2-02](./09-sysmon-deployment.md)), and its normal behaviour was measured before any rule was written ([C2-03](./10-sysmon-baseline.md)) — the hour that showed one updater generating 77% of process creations and an Event 8 that had to be investigated before it could be called benign. A controlled PowerShell download cradle ([UC-03](../investigations/UC-03/report.md)) gave the chapter something worth detecting, and confirmed the telemetry reached Wazuh while raising no alert. The first custom rule ([C2-05](./11-custom-detection-rule.md)) closed that gap, though not the way it was designed: the Sysmon command-line approach failed in this environment and the rule was rebuilt on PowerShell Script Block Logging. Running it against ordinary PowerShell ([C2-06](./12-rule-tuning.md)) exposed a false positive on benign `Invoke-Expression` and led to the tuning that keeps the cradle while dropping the noise.

## Success criteria review

Each acceptance criterion from the scope, and where it was met:

| Criterion | Met by |
|---|---|
| Sysmon runs with a documented configuration, identified in Wazuh | Deployment on SOC-WIN10, config pinned by hash ([C2-02](./09-sysmon-deployment.md)) |
| A controlled test event confirms the pipeline end to end | `notepad.exe` traced to the manager archives ([C2-02](./09-sysmon-deployment.md)) |
| UC-03 produces the expected Sysmon telemetry in Wazuh | Cradle traced across Event ID 1 and 3, decoded and attributed ([UC-03](../investigations/UC-03/report.md)) |
| A custom rule raises an alert on the UC-03 activity | Rule 100100 at level 12 via Script Block Logging ([C2-05](./11-custom-detection-rule.md)) |
| The rule is reviewed against normal activity; false positives and tuning documented | Benign `Invoke-Expression` false positive found and removed ([C2-06](./12-rule-tuning.md)) |
| Each validated detection is mapped to MITRE ATT&CK | Mapping below |
| UC-03 has reviewed evidence and a written investigation report | STAR report with end-to-end evidence ([UC-03](../investigations/UC-03/report.md)) |
| Software versions and configuration dependencies are documented | Consolidated below |
| Known detection gaps and limitations are documented | Consolidated below |
| Published evidence contains no credentials, personal data, or unnecessary infrastructure | Sanitization review below |

Every item holds. Chapter 2 is complete.

## MITRE ATT&CK mapping

The chapter produced one validated detection — rule 100100, the tuned download-cradle rule. It covers two techniques, and it is worth being just as clear about what it leaves untouched.

| Technique | Covered? | How |
|---|---|---|
| [T1059.001 — Command and Scripting Interpreter: PowerShell](https://attack.mitre.org/techniques/T1059/001/) | Yes | The rule reads the executed script block; the cradle runs its payload in memory through `IEX` / `Invoke-Expression` |
| [T1105 — Ingress Tool Transfer](https://attack.mitre.org/techniques/T1105/) | Yes | The rule requires a download method (`DownloadString`, `DownloadFile`, `Net.WebClient`) alongside the execution |

What the detection does **not** cover, and should not be read as covering:

- **Obfuscation ([T1027](https://attack.mitre.org/techniques/T1027/)).** The rule matches literal markers. A Base64-encoded command (`-enc`), a reflectively loaded method, or string concatenation that hides `DownloadString` would all evade it. Wazuh's built-in rule 91809 catches the `FromBase64String` case, but broad obfuscation handling is not part of this chapter.
- **Split download-and-execute.** A cradle that writes to disk and executes in a separate step falls between the rule's two conditions; catching it is a correlation problem, not a single-rule one.
- **Everything beyond this one behaviour.** The chapter validated the detection-engineering loop on a single technique. Persistence, credential access, lateral movement, and the rest of ATT&CK have no coverage here — collecting telemetry is not the same as detecting on it, and only the cradle has a validated rule.

Sysmon and Script Block Logging collect far more than rule 100100 acts on. Narrowing that distance one technique at a time is the work a real detection program never finishes — this chapter took the first step of it, not the whole journey.

## Software versions and configuration dependencies

What the chapter added, on top of the Chapter 1 baseline:

| Component | Version / setting |
|---|---|
| Endpoint EDR sensor | Sysmon 15.21 |
| Sysmon configuration | SwiftOnSecurity `sysmonconfig-export.xml`, rule config v4.50, hash `SHA256=055FEBC600E6D7448CDF3812307275912927A62B1F94D0D933B64B294BC87162` |
| PowerShell logging | Script Block Logging enabled (`EnableScriptBlockLogging = 1`) |
| Wazuh manager | `analysisd.decoder_order_size` raised from 256 to 1024 |
| Custom rule | Rule 100100 in `local_rules.xml`, chained to built-in 91802 |

A few of these are load-bearing — change one and the detection stops working:

- Script Block Logging must be enabled on the endpoint; without it there is no Event ID 4104 and nothing for the rule to read.
- The agent must collect the `Microsoft-Windows-PowerShell/Operational` channel through a `<localfile>` block, alongside the Sysmon channel.
- `decoder_order_size` was raised to 1024 while chasing the Sysmon command-line approach. The delivered rule uses Script Block Logging and no longer depends on it, but it is left at 1024 so the verbose Sysmon events keep decoding fully rather than tripping the manager's "too many fields" limit.
- The rule chains to `91802`, Wazuh's parent for PowerShell script-block events; the field is `win.eventdata.scriptBlockText`, the same field the built-in PowerShell ruleset uses.

## Known limitations and gaps

The chapter's limits are real, and naming them is part of closing it.

**Scope of detection.** One validated rule covering one technique pair, on one endpoint. Sysmon and Script Block Logging run on the Windows 10 machine only; the domain controller and the Linux endpoint have no endpoint detection. The rule matches literal markers and is evaded by obfuscation. This chapter proves the loop — baseline, detect, tune, map — not breadth.

**The Sysmon detour.** The download-cradle rule was first built against Sysmon's `commandLine` field and never fired. The bisection that followed ruled out the rule and pointed at the event: under the verbose SwiftOnSecurity configuration, the cradle's process-creation event did not reach rule evaluation the way simpler events did, while the archives still recorded it. Rather than dig further into the analysis engine, the detection moved to Script Block Logging, which is the recommended telemetry for PowerShell attacks anyway. The full account is in the [detection rule document](./11-custom-detection-rule.md).

**Tuning depth.** The false-positive review was one hour on one endpoint. A longer window, or a machine that legitimately uses `Net.WebClient` in installer or update scripts, could surface a case the current markers still catch — the next round of tuning, not a flaw in this one.

**Time correlation.** The Chapter 1 gap remains: the sources are not on a shared clock, so correlating endpoint and network telemetry by time still needs manual conversion. It did not block this chapter's single-source detection, but it would matter for correlation-based rules.

## Lessons learned

The hardest lesson came from the rule that would not fire. After every regex variation failed against a `commandLine` field that plainly held the string, the problem turned out to be the event never reaching the engine, not the pattern — and the fix was to change where the rule read from, moving to Script Block Logging, rather than keep rewriting it. A detection's source is as much a design choice as its logic.

None of the tuning would have been possible without measuring normal first. The baseline turned a raw event stream into something legible — the updater that any process rule has to survive, the lone Event 8 whose two benign sources meant a third would stand out — and gave the false-positive work something concrete to compare against.

Chapter 1 showed that seeing an attack and being alerted to it are different things; this chapter met the same limit from the other side. One tuned rule covers one technique, and the distance between what the sensors gather and what the rules catch is where a detection program spends most of its effort.

A smaller, practical point surfaced more than once: how a test is triggered changes the event it leaves behind. The cradle pasted into an open session and the same cradle launched as a fresh process were not the same event to the sensor, and a test that does not mirror how the real activity runs can send an investigation the wrong way.

## Evidence sanitization

Every screenshot was reviewed before commit. The lab uses private IP ranges already in the IP plan, so internal addresses are not sensitive. No credentials appear in any published evidence: the UC-03 payload is a one-line `Write-Host` served from an internal host, the download target is the lab's own Debian at 10.10.10.40, and the cradle carries no secrets. The hostnames and the `adserver.local` domain are lab-internal. The endpoint's factory hostname (`DESKTOP-CAG70U6`) shows in some captures and is harmless.

## Outcome and what comes next

Chapter 2 delivered what it promised: endpoint telemetry turned into a working detection. The lab now sees a suspicious PowerShell execution, alerts on it above the threshold, distinguishes it from benign scripting, and knows which ATT&CK techniques the alert speaks to — and which it does not.

What it does not do yet is respond. A validated detection is the input to that: Chapter 3 looks at small, reversible response and automation — Wazuh Active Response, alert enrichment, and controlled notifications — built on top of the detection this chapter proved.
