# SOC Home Lab: End-to-End Security Monitoring with Wazuh, Suricata, and FortiGate

A small Security Operations Center built from scratch on a dedicated VMware ESXi host. The lab combines firewall, network, identity, and endpoint telemetry into a single monitoring workflow — and documents every decision, limitation, and test result along the way.

**Current stage:** Chapter 1 – Core SOC Visibility. Milestone-level status lives in the [Roadmap](./ROADMAP.md).

## Why I built this

I come from NOC and cloud operations, where networking, infrastructure monitoring, virtualization, and troubleshooting were my day-to-day. This lab is how I point that experience at security operations: instead of just studying detection concepts, I build the monitoring pipeline myself and investigate what comes out of it.

It's my first structured SOC project, so the scope is deliberately small. Nothing gets added until what's already running is understood, tested, and documented.

## What the lab does

The core workflow, end to end:

1. Kali Linux generates controlled test activity from an isolated network.
2. FortiGate routes, filters, and logs the traffic between the Attack and SOC networks.
3. Suricata watches the monitored segment passively, while the endpoints produce system and identity telemetry.
4. Wazuh centralizes everything — it's where the investigation happens.
5. Each test scenario ends with reviewed evidence and a written investigation report.

Chapter 1 validates this workflow through two scenarios: network discovery from Kali (UC-01) and repeated authentication failures against Active Directory (UC-02). Their full definitions, required evidence, and acceptance criteria are in the [Chapter 1 Scope](./docs/00-project-scope.md).

## What this project demonstrates

Skills exercised across the lab, each backed by a document with evidence:

- **Network segmentation and firewall policy design** under a hard constraint — the evaluation license allows exactly three policies, and the design spends them deliberately.
- **SIEM deployment and telemetry pipelines** — agent enrollment, syslog ingestion, and file-based collection converging on a single Wazuh node.
- **Passive network monitoring** — IDS placement, capture interface design, and the virtual switch configuration that makes sniffing possible.
- **Evidence-based validation** — every milestone closes with controlled tests, expected-versus-observed results, and reviewed screenshots, not with "it's installed".
- **Virtualization and infrastructure operations** — ESXi networking, resource allocation, and the trade-offs of running a lab on one physical box.

## Architecture

The lab runs on a dedicated VMware ESXi 6.7 host: a 14-core Intel Xeon E5-2680 v4, 64 GB of RAM, an SSD, and a single physical network interface.

Only the external virtual switch has a physical uplink. The SOC and Attack networks are internal to the host, and the FortiGate is the only routed path between them.

Solid lines in the diagram are deployed and validated paths. The dashed line is the one telemetry integration still pending.

```mermaid
flowchart LR
    PHYSICAL["Physical Network and Internet"]

    subgraph ESXI["Dedicated VMware ESXi 6.7 Host"]
        WAN["WAN Soc<br/>vSwitch0 with uplink"]
        FG["FortiGate 7.4.12"]
        SOCNET["SOC Network<br/>vSwitch-Lab"]
        ATTACKNET["Attack Network<br/>vSwitch-Attack"]

        KALI["Kali Linux"]
        WAZUH["Wazuh All-in-One"]
        SURICATA["Suricata IDS"]
        AD["Active Directory"]
        WIN10["Windows 10"]
        DEBIAN["Debian Desktop"]

        WAN -->|"port1"| FG
        KALI --- ATTACKNET
        ATTACKNET -->|"port3"| FG
        FG -->|"port2"| SOCNET
        SOCNET --- WAZUH
        SOCNET --- SURICATA
        SOCNET --- AD
        SOCNET --- WIN10
        SOCNET --- DEBIAN
    end

    PHYSICAL --> WAN
    FG -->|"Syslog"| WAZUH
    AD -->|"Wazuh Agent"| WAZUH
    WIN10 -->|"Wazuh Agent"| WAZUH
    DEBIAN -->|"Wazuh Agent"| WAZUH
    SURICATA -.->|"eve.json via Wazuh Agent - planned"| WAZUH
```

## Technology choices

| Technology | Role in the lab |
|---|---|
| VMware ESXi 6.7 | Dedicated hypervisor. Keeps the internal networks isolated at the virtual switch level. |
| FortiGate 7.4.12 (Evaluation) | Routing, segmentation, and policy enforcement between the networks. The evaluation license caps the lab at three firewall policies — a real constraint the design works around. |
| Wazuh all-in-one (Ubuntu Server 24.04) | The central SIEM. Receives agent, syslog, and Suricata telemetry, and is the single place where events are analyzed. |
| Suricata (Ubuntu Server 24.04) | Passive network IDS on the monitored segment, exporting structured events through `eve.json`. |
| Active Directory + Windows 10 | Identity, authentication, and Windows endpoint telemetry. |
| Debian Desktop | Linux endpoint visibility. |
| Kali Linux | Source of controlled test traffic, kept inside the isolated Attack Network. |

## Design decisions worth a closer look

A few choices carry most of the lab's reasoning:

- **The Attack-to-SOC policy allows everything, on purpose.** This is a detection lab — attack traffic is supposed to cross the boundary and be seen, not stopped at the edge. NAT is disabled on that path so every log records the real source address. The [segmentation baseline](./docs/02-fortigate-segmentation.md) explains the trade-off.
- **Three firewall policies is all the license gives, and all three are spent.** Which paths earned a policy slot, and which rely on the implicit deny, is a design decision documented in the [same baseline](./docs/02-fortigate-segmentation.md).
- **The IDS captures on an interface with no IP address.** A promiscuous port group and a dedicated listen-only interface separate capture from management — the closest a virtual lab gets to a SPAN port. Details in the [sensor validation](./docs/05-suricata-sensor.md).
- **Kali is deliberately unmonitored.** The attack machine carries no agent, so its footprint in the SIEM is exactly what the defensive stack observes — nothing more. The reasoning is in the [agent onboarding](./docs/03-wazuh-agent-onboarding.md).

## Documentation

Each milestone produces one document, written as the work happens:

| Document | What it covers | Milestone |
|---|---|---|
| [Chapter 1 Scope](./docs/00-project-scope.md) | Boundaries, telemetry sources, validation scenarios, and acceptance criteria — the chapter's contract | C1-01 |
| [Infrastructure Baseline](./docs/01-infrastructure-baseline.md) | ESXi host, virtual networking, VM inventory, IP plan, and traffic paths | C1-02 |
| [FortiGate Segmentation Baseline](./docs/02-fortigate-segmentation.md) | Interfaces, firewall policies, expected traffic matrix, and the allow/deny tests that prove it | C1-03 |
| [Wazuh Agent Onboarding](./docs/03-wazuh-agent-onboarding.md) | Manager deployment, agent naming convention, enrollment, and verification | C1-04 |
| [FortiGate Telemetry Integration](./docs/04-fortigate-telemetry.md) | The syslog pipeline and the controlled event that validates decoding end to end | C1-05 |
| [Suricata Sensor Validation](./docs/05-suricata-sensor.md) | Capture design, sensor configuration, and the passive capture proof | C1-06 |
| [Project Roadmap](./ROADMAP.md) | Milestones, current focus, and status — the only place status lives | — |

## Repository structure

```
.
├── README.md            ← you are here
├── ROADMAP.md           ← milestone status
└── docs/
    ├── 00-project-scope.md
    ├── 01-infrastructure-baseline.md
    ├── 02-fortigate-segmentation.md
    ├── 03-wazuh-agent-onboarding.md
    ├── 04-fortigate-telemetry.md
    ├── 05-suricata-sensor.md
    └── img/             ← sanitized evidence, one folder per document
```

## Where the project is now

The infrastructure, segmentation, and telemetry pipeline are built and validated: every endpoint reports to Wazuh as an active agent, FortiGate logs arrive by syslog, and Suricata records the monitored segment in `eve.json`. What remains in Chapter 1 is connecting Suricata's output to Wazuh and running the two investigation scenarios.

Deployed is not the same as validated — each milestone only closes after documented testing and evidence review. Current focus and status live in the [Roadmap](./ROADMAP.md).

## What comes next

Once the core monitoring workflow is validated, the project moves into endpoint and detection engineering: Sysmon, custom Wazuh rules, false-positive analysis, and MITRE ATT&CK mapping. A later chapter will look at small, reversible response and automation workflows.

None of that starts before Chapter 1 closes.

## Safety and ethical boundaries

Every test targets systems owned by the lab, inside the isolated environment. Nothing faces the internet, no third-party systems are touched, and no real malware is used. Anything published — screenshots, configurations, events, log samples — is reviewed first to remove credentials, personal data, and unnecessary infrastructure details.

## Connect

- [GitHub](https://github.com/guilhermeescame)
- [LinkedIn](https://www.linkedin.com/in/guilherme-barbirato-escame-053bb6293/)
