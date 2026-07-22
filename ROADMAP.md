# Project Roadmap

The single reference for what is done, what is in progress, and what comes next. For the context behind the lab — architecture, technology choices, goals — see the [README](./README.md).

## Current focus

**Chapter 3 – Response and Automation** · next: C3-02 CDB list enrichment

## How status is tracked

The model separates *installed* from *proven*. A milestone only reaches **Validated** after its success criteria are met and the supporting evidence has been reviewed.

| Status | Meaning |
|---|---|
| Planned | Not started. |
| In Progress | Started, outcome not yet complete. |
| Implemented | Configured and running, but formal validation is still pending. |
| Partially Validated | Some expected results confirmed; success criteria not fully met. |
| Validated | Success criteria met and evidence reviewed. |
| Deferred | Belongs to a later chapter. |

## Chapter 1 – Core SOC Visibility

Goal: reliable telemetry from firewall, network, identity, and endpoints, centralized in Wazuh and validated through two investigation scenarios.

| ID | Milestone | Done when | Status |
|---|---|---|---|
| C1-01 | Project foundation and scope | Scope, boundaries, success criteria, and documentation approach are reviewed and stored in the repository. | Validated |
| C1-02 | Infrastructure baseline | ESXi resources, virtual networking, VM inventory, IP plan, traffic paths, and known limitations are documented and reviewed. | Validated |
| C1-03 | FortiGate segmentation baseline | Interfaces and firewall policies are documented; allowed and denied traffic paths are tested, logged, and supported by reviewed evidence. | Validated |
| C1-04 | Wazuh Agent onboarding | Active Directory, Windows 10, Debian, and Suricata report as active agents, each correctly identified in Wazuh. | Validated |
| C1-05 | FortiGate telemetry integration | FortiGate syslog is received, identified, and available for investigation in Wazuh. | Validated |
| C1-06 | Suricata sensor validation | The capture interface is configured and Suricata records controlled traffic in `eve.json`. | Validated |
| C1-07 | Suricata and Wazuh integration | Wazuh ingests `eve.json` through the host agent and identifies the expected Suricata events. | Validated |
| C1-08 | UC-01: Network discovery | A controlled discovery test from Kali produces the expected Suricata and FortiGate telemetry. Evidence and a STAR-based investigation report are reviewed. | Validated |
| C1-09 | UC-02: Authentication failures | Controlled authentication failures against Active Directory produce the expected Windows Security Events and Wazuh alerts. Evidence and a STAR-based investigation report are reviewed. | Validated |
| C1-10 | Chapter 1 review and closure | Evidence is sanitized, limitations and lessons learned are recorded, and the chapter success criteria are reviewed. | Validated |

## Chapter 2 – Endpoint and Detection Engineering

Goal: turn visibility into detection — Sysmon telemetry on the Windows endpoint, a custom rule validated against a controlled scenario, tuned against false positives, and mapped to MITRE ATT&CK.

| ID | Milestone | Done when | Status |
|---|---|---|---|
| C2-01 | Chapter scope and acceptance criteria | Scope, boundaries, success criteria, and the detection workflow are reviewed and stored in the repository. | Validated |
| C2-02 | Sysmon deployment on Windows 10 | Sysmon runs with a documented configuration, and Wazuh receives and correctly identifies its events. | Validated |
| C2-03 | Sysmon telemetry validation | A controlled test event is traced end to end, and the endpoint's normal baseline behavior is documented. | Validated |
| C2-04 | UC-03: Suspicious PowerShell execution | The controlled scenario produces the expected Sysmon telemetry in Wazuh. Evidence and a STAR-based investigation report are reviewed. | Validated |
| C2-05 | Custom Wazuh detection rule | At least one custom rule alerts on the UC-03 activity; the rule is committed with the reasoning behind its conditions. | Validated |
| C2-06 | False-positive review and tuning | The rule has run against normal endpoint activity, with false positives documented and the tuning re-tested. | Validated |
| C2-07 | MITRE ATT&CK mapping | Each validated detection is mapped to the technique it covers — and to what it misses. | Validated |
| C2-08 | Chapter 2 review and closure | Evidence is sanitized, limitations and lessons learned are recorded, and the chapter success criteria are reviewed. | Validated |

## Chapter 3 – Response and Automation

Goal: turn detection into action — alert enrichment that separates known hosts from unknown ones, a small and reversible Active Response, controlled notifications, and the full cycle validated by re-running a Chapter 1 attack. The design decisions behind the milestones are in the [Chapter 3 Scope](./docs/14-chapter-3-scope.md).

| ID | Milestone | Done when | Status |
|---|---|---|---|
| C3-01 | Chapter scope and acceptance criteria | Scope, boundaries, success criteria, and the response workflow are reviewed and stored in the repository. | Validated |
| C3-02 | CDB list enrichment | A list of known lab hosts exists on the manager, and a child rule raises authentication failures from unknown sources; both behaviors are tested with reviewed evidence. | Planned |
| C3-03 | Active Response on the domain controller | The `netsh` response triggers on the elevated rule only, blocks the offending source, and the timeout reverses it; block and reversal observed in a controlled test. | Planned |
| C3-04 | Discord notifications | Alerts at level 12 and above reach Discord through a committed custom integration; notifications received for the elevated rule and for rule 100100. | Planned |
| C3-05 | Response safeguards | Operational risks and their mitigations are documented and reviewed before UC-04 runs. | Planned |
| C3-06 | UC-04: Full response cycle | The UC-02 brute force re-run produces the elevated alert, the active block, the contained attack, the automatic reversal, and the notification — each step with evidence. STAR report reviewed. | Planned |
| C3-07 | Chapter 3 review and closure | Evidence is sanitized, limitations and lessons learned are recorded, and the chapter success criteria are reviewed. | Planned |
