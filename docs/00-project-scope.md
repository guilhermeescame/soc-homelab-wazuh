# Chapter 1 Scope: Core SOC Visibility

This document is the contract for Chapter 1: what it must deliver, what stays out, and what "done" means. The architecture and technology context live in the [README](../README.md); execution status lives in the [Roadmap](../ROADMAP.md).

Chapter 1 builds the minimum monitoring workflow: firewall, network, identity, and endpoint telemetry collected in Wazuh, exercised by controlled tests, and investigated with documented evidence. Detection engineering and automated response come later — first the data has to be trustworthy.

## Environment summary

The lab is three network areas on a single ESXi host: the physical network (ESXi management and the FortiGate WAN interface), the SOC Network (monitored systems and security platforms), and the isolated Attack Network (Kali Linux, no physical uplink). The FortiGate is the only routed path between the Attack and SOC networks, and every test targets systems owned by the lab.

A few constraints shape what this chapter can promise:

- the FortiGate Evaluation license allows at most three firewall policies, which limits how finely traffic can be separated;
- Wazuh runs as a single all-in-one node, adequate for lab scale but not for production ingestion;
- Suricata is a passive sensor, so its visibility depends on the capture interface and virtual switch configuration — traffic denied before reaching the monitored path may appear only in FortiGate logs;
- the lab validates monitoring behavior at small scale, not enterprise traffic volume.

The complete infrastructure reference — ESXi resources, virtual networking, VM inventory, IP plan, and traffic paths — is documented in the [Infrastructure Baseline](./01-infrastructure-baseline.md).

## Telemetry sources

| Source | Telemetry | Collection path |
|---|---|---|
| Active Directory | Windows Security Events, including authentication activity | Wazuh Agent |
| Windows 10 | Windows system, application, and security events | Wazuh Agent |
| Debian Desktop | Linux system and authentication logs | Wazuh Agent |
| FortiGate | Firewall traffic and system logs | Syslog to Wazuh |
| Suricata | Network alerts and protocol events from `eve.json` | Local file collection through the Wazuh Agent |

Sysmon is deliberately absent from this baseline — it belongs to the detection engineering chapter.

## Validation scenarios

| ID | Activity | What it must prove | Required evidence |
|---|---|---|---|
| UC-01 | Network discovery from Kali Linux | Reconnaissance traffic crossing the Attack-to-SOC boundary is visible in Suricata, FortiGate, and the corresponding Wazuh records. | Test context, FortiGate traffic log, Suricata event, Wazuh record, investigation conclusion |
| UC-02 | Repeated authentication failures against Active Directory | Native Windows authentication failures are collected and available for investigation in Wazuh. | Test context, Windows Security Event, Wazuh event or alert, event timeline, investigation conclusion |

Firewall allow and deny tests support the infrastructure baseline but do not count as separate investigation scenarios.

## Acceptance criteria

Chapter 1 closes when every item below holds:

- [x] The FortiGate isolates the SOC Network from the Attack Network.
- [x] Kali reaches SOC Network systems only through an authorized firewall policy.
- [x] Wazuh receives and correctly identifies telemetry from Active Directory, Windows 10, Debian, Suricata, and FortiGate.
- [x] Suricata captures and records test traffic reaching the monitored network.
- [x] UC-01 produces the expected FortiGate, Suricata, and Wazuh records.
- [ ] UC-02 produces the expected Windows Security Events and Wazuh records.
- [ ] Each scenario has reviewed evidence and a written investigation report.
- [ ] Software versions and relevant configuration dependencies are documented.
- [ ] Known visibility gaps and technical limitations are documented.
- [ ] Published evidence contains no credentials, tokens, personal data, or unnecessary infrastructure details.

## Evidence requirements

Each scenario must connect the test activity to the telemetry it produced. The evidence set includes the date, scope, and systems involved; the activity performed; the relevant records from the original source and from Wazuh; expected versus observed results; and the investigation conclusion, including any visibility gaps.

Everything published goes through sanitization first: screenshots and event excerpts are reviewed to remove credentials, personal data, and infrastructure details that don't need to be public.

Investigation reports follow a STAR structure when it improves clarity:

- **Situation** — lab context and the activity under investigation;
- **Task** — what the investigation set out to confirm;
- **Action** — the test performed, the telemetry reviewed, the analysis done;
- **Result** — observed events, detection outcome, conclusion, and identified gaps.

## Out of scope

Excluded from Chapter 1:

- high availability, clustering, or production-scale architecture;
- internet-facing lab services;
- real malware execution;
- tests against public or third-party systems;
- complete infrastructure automation;
- Sysmon deployment and tuning;
- suspicious PowerShell execution scenarios;
- custom Wazuh rules and decoders;
- false-positive tuning for custom detections;
- MITRE ATT&CK coverage mapping;
- dedicated SOAR platforms;
- Wazuh Active Response or automatic containment.

## Related documentation

- [README](../README.md) — project introduction, architecture, and technology choices.
- [Project Roadmap](../ROADMAP.md) — milestones, current focus, and status.
