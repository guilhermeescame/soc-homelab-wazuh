# Chapter 2 Scope: Endpoint and Detection Engineering

Chapter 1 left the lab able to see: firewall, network, identity, and endpoint telemetry, all landing in Wazuh. It also left a gap on record — most of what the lab sees never rises above informational, because nothing turns events into alerts. Chapter 2 works on that gap. Sysmon goes onto the Windows endpoint, a controlled PowerShell scenario gives the lab something worth detecting, and a custom Wazuh rule — written, tested against normal activity, and mapped to MITRE ATT&CK — turns the scenario's footprint into an alert.

This scope sets what the chapter must deliver and what stays out. Architecture and context live in the [README](../README.md); execution status lives in the [Roadmap](../ROADMAP.md).

## Starting point

Everything here builds on the pipeline Chapter 1 validated: active agents on every monitored endpoint, FortiGate syslog and Suricata's `eve.json` arriving in Wazuh, and a single logged policy between the Attack and SOC networks. The [Chapter 1 Closure](./07-chapter-1-closure.md) records the versions and configuration dependencies all of this rests on; none of it is rebuilt or re-tested in this chapter.

One Chapter 1 constraint follows the work here: Wazuh is still a single all-in-one node, so whatever a rule costs in performance is only measured at lab scale.

## What changes in the telemetry

Sysmon is the chapter's only new source, and it goes on the Windows 10 endpoint alone:

| Source | Telemetry | Collection path |
|---|---|---|
| Sysmon (Windows 10) | Process creation with full command line, network connections, and the other event types the chosen configuration enables | Windows Event Channel, through the existing Wazuh Agent |

One endpoint is enough. The Windows 10 machine is where the attack scenario runs, and a single deployment can be understood and tuned properly before the same work is repeated anywhere else. The domain controller is the obvious next candidate, but it waits until this one is stable.

The configuration starts from an established community baseline rather than a blank file. Which baseline, and what gets changed, is decided and documented in the deployment milestone (C2-02).

## Validation scenario

| ID | Activity | What it must prove | Required evidence |
|---|---|---|---|
| UC-03 | Controlled suspicious PowerShell execution on Windows 10 | The activity produces Sysmon telemetry visible in Wazuh, and a custom rule raises an alert on it — not just a record. | Test context, Sysmon event with command line, Wazuh alert from the custom rule, false-positive review, investigation conclusion |

Finding the telemetry is not enough this time. UC-03 closes only when a custom rule alerts on the activity, the rule has been run against normal system behavior, and the detection is mapped to the ATT&CK technique it covers.

## The detection engineering workflow

The chapter is built around a loop rather than a single rule: learn what the new telemetry looks like when nothing is wrong, run the controlled scenario and write a rule that catches its footprint, then run normal activity and fix what the rule flags wrongly, and finally record which ATT&CK technique the result covers — and which it does not. Every pass through the loop leaves evidence behind. A rule that was never tested against benign activity is not a validated detection.

## Acceptance criteria

Chapter 2 closes when every item below holds:

- [x] Sysmon runs on the Windows 10 endpoint with a documented configuration, and its events are received and correctly identified in Wazuh.
- [x] A controlled test event confirms the Sysmon pipeline end to end (expected versus observed).
- [x] UC-03 produces the expected Sysmon telemetry, visible in Wazuh.
- [ ] At least one custom Wazuh rule raises an alert on the UC-03 activity.
- [ ] The rule has been run against normal endpoint activity, with false positives and the applied tuning documented.
- [ ] Each validated detection is mapped to the MITRE ATT&CK technique(s) it covers.
- [ ] UC-03 has reviewed evidence and a written investigation report.
- [ ] Software versions and configuration dependencies added in this chapter are documented.
- [ ] Known detection gaps and limitations are documented.
- [ ] Published evidence contains no credentials, tokens, personal data, or unnecessary infrastructure details.

## Evidence requirements

Nothing changes in the discipline: controlled tests, expected versus observed results, sanitized screenshots, and STAR reports where the structure helps. Rule development adds one artifact — the rule file itself goes into the repository, along with the reasoning behind its conditions and thresholds.

## Out of scope

Excluded from Chapter 2:

- Sysmon on the domain controller or the Debian endpoint;
- real malware, or offensive tooling beyond the controlled PowerShell scenario;
- broad ATT&CK coverage mapping — only techniques exercised by validated detections are mapped;
- detection content for other sources (FortiGate and Suricata stay as delivered in Chapter 1);
- Wazuh Active Response, alert enrichment, notifications, and automation — all of Chapter 3.

## Related documentation

- [README](../README.md) — project introduction, architecture, and technology choices.
- [Project Roadmap](../ROADMAP.md) — milestones, current focus, and status.
- [Chapter 1 Closure](./07-chapter-1-closure.md) — the validated baseline this chapter builds on.
