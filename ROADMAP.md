# Project Roadmap

The single reference for what is done, what is in progress, and what comes next. For the context behind the lab — architecture, technology choices, goals — see the [README](./README.md).

## Current focus

**Chapter 2 – Endpoint and Detection Engineering** · in progress. Current milestone: **C2-01 – Chapter scope and acceptance criteria**

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
| C2-01 | Chapter scope and acceptance criteria | Scope, boundaries, success criteria, and the detection workflow are reviewed and stored in the repository. | In Progress |
| C2-02 | Sysmon deployment on Windows 10 | Sysmon runs with a documented configuration, and Wazuh receives and correctly identifies its events. | Planned |
| C2-03 | Sysmon telemetry validation | A controlled test event is traced end to end, and the endpoint's normal baseline behavior is documented. | Planned |
| C2-04 | UC-03: Suspicious PowerShell execution | The controlled scenario produces the expected Sysmon telemetry in Wazuh. Evidence and a STAR-based investigation report are reviewed. | Planned |
| C2-05 | Custom Wazuh detection rule | At least one custom rule alerts on the UC-03 activity; the rule is committed with the reasoning behind its conditions. | Planned |
| C2-06 | False-positive review and tuning | The rule has run against normal endpoint activity, with false positives documented and the tuning re-tested. | Planned |
| C2-07 | MITRE ATT&CK mapping | Each validated detection is mapped to the technique it covers — and to what it misses. | Planned |
| C2-08 | Chapter 2 review and closure | Evidence is sanitized, limitations and lessons learned are recorded, and the chapter success criteria are reviewed. | Planned |

## Chapter 3 – Response and Automation

Starts only after the Chapter 2 detection workflow is stable. All milestones are deferred until then:

- evaluate Wazuh Active Response in a controlled test;
- add basic alert enrichment;
- evaluate controlled notifications;
- implement a small, reversible automation workflow;
- document response safeguards and operational risks.
