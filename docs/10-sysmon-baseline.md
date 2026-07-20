# Sysmon Telemetry Baseline

Milestone C2-03 closes the distance between having Sysmon installed and knowing what it actually produces. An hour of ordinary use on SOC-WIN10 was measured and investigated, and a second controlled event — this time involving network telemetry — was traced from the endpoint to the manager.

The pipeline this builds on is documented in the [Sysmon Deployment](./09-sysmon-deployment.md); the reasoning for measuring normal before writing rules is in the [Chapter 2 Scope](./08-chapter-2-scope.md). Status is tracked in the [Roadmap](../ROADMAP.md).

## The measurement window

The window ran on 2026-07-16, from 14:30 to 15:30 local time, while the endpoint was used normally — some browsing, applications opened and closed, files deleted, a few pings. Counting was done on the endpoint itself with `Get-WinEvent`. Sysmon recorded 753 events in that hour:

| Event ID | What it records | Count |
|---|---|---|
| 1 | Process creation | 596 |
| 11 | File created | 79 |
| 22 | DNS query | 29 |
| 13 | Registry value set | 24 |
| 3 | Network connection | 12 |
| 12 | Registry key created or deleted | 8 |
| 15 | File stream created (Mark of the Web) | 4 |
| 8 | CreateRemoteThread | 1 |

## What the numbers say

Most of the hour belongs to one binary. GoogleUpdater's `updater.exe` accounts for 458 of the 596 process creations — 77% — and nothing else in the top ten passes 33 occurrences. Normal on this endpoint means an updater checking on itself every few seconds, with browsers and system processes making up the rest. A rule that treats frequent process creation as suspicious would page someone all day here, which puts `updater.exe` first on the tuning list when C2-06 comes around.

The single Event ID 8 took longer to close. CreateRemoteThread appears in the SwiftOnSecurity configuration because injection techniques use it, and registering "one occurrence" without asking who fired it would defeat the purpose of a baseline. The full history of the event on this endpoint came down to two patterns. `dwm.exe` opens threads in `csrss.exe` under `Window Manager\DWM-1`, repeatedly and always from the same start address — the Desktop Window Manager doing its job. And Defender's `MpCmdRun.exe` once received a console control signal through `KERNELBASE.dll!CtrlRoutine`, which is how Windows delivers a Ctrl+C to a console process. Both are ordinary. The gain is for the future: if an Event ID 8 ever shows up here with a different source, it has no crowd to hide in.

## The controlled event

The deployment milestone traced a `notepad.exe` to the manager, which proved transport and little else. The coming PowerShell scenario will lean on network telemetry, so this validation traced that instead. A single `Invoke-WebRequest` to `http://testmynids.org/uid/index.html` produced two events on the endpoint — the DNS query for the domain (Event ID 22) and the TCP connection to port 80 (Event ID 3), both from `powershell.exe` — and both arrived in the manager archives decoded and attributed to SOC-WIN10. The archives were enabled and reverted the same way as in the [deployment](./09-sysmon-deployment.md), for the same level-0 reason.

Reusing the [C1-07 test URL](./06-suricata-wazuh-integration.md) means the same request now exists in two independent telemetry layers. Suricata saw an HTTP exchange on the wire; Sysmon saw `powershell.exe` make it, and under which user. When an investigation needs to tie a network alert to the process behind it, that seam is where the two meet.

| Check | Expected | Observed | Evidence |
|---|---|---|---|
| Baseline measured | Event distribution over a defined window | 753 events in sixty minutes across eight event types | [01-baseline-counts.png](./img/10-baseline/01-baseline-counts.png) |
| Dominant processes identified | Top ten images for Event ID 1 | `updater.exe` with 458 of 596; browsers and system processes fill the tail | [02-baseline-top-images.png](./img/10-baseline/02-baseline-top-images.png) |
| Controlled event on the endpoint | Events 22 and 3 from `powershell.exe` | DNS query for `testmynids.org` and TCP 80 to CloudFront, image `powershell.exe` | [03-controlled-ps-events-local.png](./img/10-baseline/03-controlled-ps-events-local.png) |
| Controlled event on the manager | Both events decoded and attributed | `eventID` 22 and 3 in the archives, agent SOC-WIN10 | [04-wazuh-archives-ps-network.png](./img/10-baseline/04-wazuh-archives-ps-network.png) |
| Event ID 8 origin | Identified and benign | `dwm.exe → csrss.exe` recurring, plus Defender's `MpCmdRun.exe` via `CtrlRoutine` | [05-event8-createremotethread.png](./img/10-baseline/05-event8-createremotethread.png) |

## Known limitations

- An hour of light interactive use is a snapshot. Heavier Office or development work would reshape the distribution, and a production baseline would watch days, not sixty minutes.
- The counts were taken on the endpoint. On the manager side the level-0 mappings still swallow everything — nothing here raises an alert until C2-05 — and the archives only ran long enough to trace the controlled event.
- Whatever the endpoint did not do during the window has no baseline. The first scheduled task at an odd hour or the first remote logon will look new, because for this dataset it is.

## Evidence

Screenshots supporting this document, sanitized before publication:

| File | What it shows |
|---|---|
| `img/10-baseline/01-baseline-counts.png` | Event count by ID over the measurement window |
| `img/10-baseline/02-baseline-top-images.png` | The ten most frequent Event ID 1 images, led by `updater.exe` |
| `img/10-baseline/03-controlled-ps-events-local.png` | Events 22 and 3 from `powershell.exe` in the local Sysmon channel |
| `img/10-baseline/04-wazuh-archives-ps-network.png` | The same events decoded in the manager archives, attributed to SOC-WIN10 |
| `img/10-baseline/05-event8-createremotethread.png` | The Event ID 8 history with both benign source patterns |
