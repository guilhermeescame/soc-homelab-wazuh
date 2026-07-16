# Chapter 1 Closure: Core SOC Visibility

This document closes Chapter 1. It confirms the success criteria are met, gathers the software versions and configuration dependencies in one place, lists the limitations, and records what the work taught. It is the deliverable of milestone C1-10.

The chapter's goals are in the [Scope](./00-project-scope.md); per-milestone status is in the [Roadmap](../ROADMAP.md). This document reviews the chapter as a whole and does not repeat what those cover.

## What the chapter delivered

Chapter 1 built the minimum monitoring workflow — firewall, network, identity, and endpoint telemetry centralized in Wazuh — and proved it with two investigations instead of calling it done at install time.

The workflow now runs end to end. The FortiGate segments the three networks and logs what crosses between them ([C1-03](./02-fortigate-segmentation.md)). Every monitored system reports to Wazuh as an active agent ([C1-04](./03-wazuh-agent-onboarding.md)), the firewall sends its logs by syslog ([C1-05](./04-fortigate-telemetry.md)), and the Suricata sensor watches the SOC segment passively ([C1-06](./05-suricata-sensor.md)) and forwards its events to the SIEM ([C1-07](./06-suricata-wazuh-integration.md)). Two controlled tests exercised the whole chain: a network scan in [UC-01](../investigations/UC-01/report.md) and a credential brute force in [UC-02](../investigations/UC-02/report.md), each traced from the attacker's action to the record it left in Wazuh.

## Success criteria review

Each acceptance criterion from the scope, and where it was met:

| Criterion | Met by |
|---|---|
| The FortiGate isolates the SOC Network from the Attack Network | Segmentation tests T1–T5 and the implicit deny ([C1-03](./02-fortigate-segmentation.md)) |
| Kali reaches SOC systems only through an authorized policy | `Attack-to-SOC` is the single allowed path; everything else hits the implicit deny ([C1-03](./02-fortigate-segmentation.md)) |
| Wazuh receives and identifies telemetry from all five sources | Agents for AD, Windows 10, Debian, and Suricata ([C1-04](./03-wazuh-agent-onboarding.md)); FortiGate by syslog ([C1-05](./04-fortigate-telemetry.md)); Suricata's `eve.json` by the host agent ([C1-07](./06-suricata-wazuh-integration.md)) |
| Suricata captures and records test traffic | Passive capture of a Kali-to-Windows flow the sensor is not part of ([C1-06](./05-suricata-sensor.md)) |
| UC-01 produces the expected FortiGate, Suricata, and Wazuh records | Scan traced across all three sources ([UC-01](../investigations/UC-01/report.md)) |
| UC-02 produces the expected Windows Security Events and Wazuh records | 4625 failures collected and correlated ([UC-02](../investigations/UC-02/report.md)) |
| Each scenario has reviewed evidence and a written investigation report | Both scenarios documented in STAR form with reviewed screenshots |
| Software versions and configuration dependencies are documented | Consolidated below |
| Known visibility gaps and technical limitations are documented | Consolidated below |
| Published evidence contains no credentials, personal data, or unnecessary infrastructure | Sanitization review below |

Every item holds. Chapter 1 is complete.

## Software versions and configuration dependencies

The versions the chapter was built and validated on:

| Component | Version |
|---|---|
| Hypervisor | VMware ESXi 6.7.0 (build 20191204001, customized image) |
| Firewall | FortiGate / FortiOS 7.4.12 (Evaluation) |
| SIEM | Wazuh 4.14.6 (all-in-one: manager, indexer, dashboard) |
| Wazuh agents | 4.14.6 (MSI on Windows, `.deb` on Linux) |
| Network IDS | Suricata 8.0.6 (AF_PACKET mode) |
| Suricata ruleset | ET Open via `suricata-update` — 52,003 rules loaded |
| Wazuh / Suricata hosts | Ubuntu Server 24.04 |
| Domain controller | Windows Server 2022 |
| Windows endpoint | Windows 10 Pro |
| Linux endpoint | Debian 13.5 |
| Attack host | Kali Linux 2026.2 (Nmap 7.99, netexec) |

A few configuration choices matter more than the rest. Change one and part of the pipeline stops working:

- promiscuous mode set to **Accept** on the `LAN Soc` port group lets the Suricata interface see traffic addressed to other hosts; without it there is no passive capture;
- a `tmpfiles.d` rule recreates `/run/suricata/` at boot so the Suricata service can open its control socket;
- NAT is **disabled** on the `Attack-to-SOC` policy so the logs keep the real source address; the investigations depend on it;
- the FortiGate sends syslog over UDP 514 to Wazuh, which accepts it through a dedicated `<remote>` block scoped to `allowed-ips 10.10.10.1`, separate from the agent listener;
- the SOC-NIDS agent reads `eve.json` through a `<localfile>` block with `log_format json`;
- the domain controller needs Audit Logon failure auditing enabled for the 4625 events in UC-02; it is on by default.

## Known limitations and visibility gaps

The chapter has real limitations. Listing them is part of closing it honestly.

**Infrastructure.** One physical NIC carries WAN, management, and lab traffic, so there is no out-of-band management path. The onboard Realtek adapter needs a community driver in a customized ESXi image, which is unsupported, and ESXi 6.7 is past end of support. These are accepted because the host has no internet access.

**Firewall.** The Evaluation license allows three policies, and all three are in use; any new segmentation need means changing an existing rule. Admin access to the FortiGate is open on all three interfaces, including the Attack Network, for lab convenience. And `Attack-to-SOC` allows all traffic on purpose — the SOC is exposed to the Attack Network so that attacks cross the boundary and get logged.

**Telemetry.** Syslog over UDP can drop events without warning. The promiscuous port group shows the whole segment to every VM in `LAN Soc`, not just the sensor — closer to a SPAN port than a hardware TAP. Suricata only sees traffic that reaches the monitored segment, so anything the FortiGate denies first appears only in the firewall logs. Capturing inside a virtual switch also produces steady stream-engine noise that inflates event counts and would need tuning on a real sensor.

**Detection.** The clearest gap is the distance between visible and actionable. Individual events usually sit below the alert threshold. UC-01's full scan never rose above `Informational` and would not have alerted anyone on its own; UC-02's repeated failures did escalate, but only because a correlation rule caught the repetition. Correlation is what makes telemetry actionable, and building it is detection-engineering work for Chapter 2. Time is a related gap: the sources ran on different clocks, so correlating them by time still needs manual conversion. A production SOC puts every source on UTC and a shared NTP reference.

**Scope of the scenarios.** Both tests gave the attacker advantages a real one would have to earn — UC-02 targeted a username known in advance instead of discovered. The scenarios prove the telemetry works, not that the lab would stop a real attacker.

## Lessons learned

Seeing an attack and being alerted to it are different things, and the gap between them is the real work. The two scenarios showed it plainly: the scan stayed at low severity, while the brute force raised an alert only because a rule counted the repeated failures. Coverage is not detection.

Separating installed from proven was worth the effort. Testing each milestone with a known event, instead of assuming the pipeline worked, caught problems a checklist would miss — like the Suricata service that started but could not open its socket. That is the same habit an analyst uses: generate an event and go find it.

The constraints helped. The three-policy limit forced clear choices about which paths get a rule and which rely on the implicit deny. And passive monitoring has hard edges — the sensor only sees its own segment — which is why firewall, sensor, and endpoint telemetry together cover more than any one source alone.

## Evidence sanitization

Every screenshot was reviewed before commit. The lab uses private IP ranges already listed in the IP plan, so internal addresses are not sensitive. Personal VMs unrelated to the lab are blurred in the ESXi captures. No credentials or passwords appear in any published evidence: the `svc-test` account is disposable, its real password stays in a local file excluded by `.gitignore`, and the passwords shown in the UC-02 command are the attacker's wrong guesses. The hostnames and the `adserver.local` domain are lab-internal.

## Outcome and what comes next

Chapter 1 delivered what it promised: reliable telemetry from firewall, network, identity, and endpoints, centralized in Wazuh and validated by two investigations. The lab can see attacker activity crossing its boundary and record it accurately.

What it cannot do yet is decide — turn that visibility into alerts worth acting on. That is Chapter 2: Sysmon, custom Wazuh rules, false-positive tuning, and mapping detections to MITRE ATT&CK. Visibility came first because detection engineering is built on top of it.
