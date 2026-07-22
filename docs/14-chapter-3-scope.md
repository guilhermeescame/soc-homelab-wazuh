# Chapter 3 Scope: Response and Automation

By the end of Chapter 2 the lab detects — rule 100100 fires on a suspicious PowerShell execution, tuned against false positives and mapped to ATT&CK. What happens after the alert is still nothing. It lands on a dashboard at level 12 and waits, with no distinction between a known host and a stranger, no containment, and no message to anyone. Chapter 3 builds the acting half: enrichment that separates known sources from unknown ones, a Wazuh Active Response small enough to stay reversible, a notification channel out of the dashboard — and one re-run of a Chapter 1 attack to prove the whole cycle.

Architecture and context stay in the [README](../README.md), execution status in the [Roadmap](../ROADMAP.md); this document is the contract for what the chapter must deliver.

## Starting point

The chapter stands on what the first two validated: the full telemetry pipeline from Chapter 1, and Chapter 2's detection work — the download-cradle rule on Script Block Logging, plus the built-in authentication rules that UC-02 exercised. The [Chapter 1](./07-chapter-1-closure.md) and [Chapter 2](./13-chapter-2-closure.md) closures record the versions and configuration dependencies underneath; nothing from that baseline gets rebuilt or re-tested here.

Two constraints carry over. Wazuh remains a single all-in-one node, so whatever response actions cost in performance is only measured at lab scale. And the telemetry sources still lack a shared clock — it did not block single-source detection and will not block single-source response, but it stays on record.

## Two alerts, two roles

The chapter has two validated detection chains to build on, and they get different jobs.

The **authentication-failure chain** (UC-02: SMB brute force against the domain controller, Windows Event 4625 into Wazuh's built-in rules) drives enrichment and Active Response. Its alerts carry a structured `srcip` field, which is exactly what a CDB lookup keys on and what the stock Active Response scripts consume. The response mechanism gets proven on the chain where it fits cleanly.

The **download-cradle chain** (rule 100100, from Chapter 2) drives notifications. Its interesting data — the host the payload was fetched from — sits inside the free text of `scriptBlockText`, not in a structured field. Extracting it would take a custom integration script doing its own parsing; forcing that into the first response milestone would prove the parsing, not the response. So the 100100 alert triggers the notification path, where the alert's content matters more than its field structure, and the structured-field limitation goes on record here instead of being engineered around.

## What the chapter adds

Three mechanisms, in dependency order:

| Mechanism | What it does | Where |
|---|---|---|
| CDB list enrichment | A list of known lab hosts on the manager; a child rule raises authentication failures from an unknown source to a higher level. Same event, different severity, depending on who is behind it. | Wazuh manager |
| Active Response | The `netsh` response blocks the offending `srcip` in the Windows Firewall of the attacked endpoint — the domain controller — and a configured timeout removes the block automatically. Triggered only by the elevated rule, never by ordinary authentication noise. | Wazuh agent on SOC-AD |
| Discord notifications | A custom integration script on the manager forwards alerts at level 12 and above to a Discord webhook. Small, committed to the repository, and the only custom code the chapter needs. | Wazuh manager |

Enrichment comes first because the Active Response fires on the rule the CDB list elevates. The same list of known hosts doubles as the response's first safeguard — a management IP on the list can never trip the block.

Notifications went to Discord after weighing the alternatives. Slack has native integrator support but no workspace exists for this lab; e-mail would require an authenticated SMTP relay in front of Wazuh's mail daemon — more infrastructure and a stored credential for a worse result. Discord costs one small translation script and a webhook URL that never enters the repository.

Containment happens at the host, not at the edge. Blocking the attacker on the FortiGate through its API would be closer to production practice, but it means custom scripting, an API token, and working around the three-policy license cap — too much machinery for the first response milestone. The edge block is recorded as the natural next step, not attempted here.

## Validation scenario

| ID | Activity | What it must prove | Required evidence |
|---|---|---|---|
| UC-04 | The UC-02 SMB brute force, re-run from Kali against the hardened pipeline | The full cycle: the attack raises an elevated alert, the Active Response blocks the source mid-attack, the block expires on its own, and the notification arrives. Detection to containment to reversal, each step observable. | Attack context, elevated Wazuh alert, firewall rule present on the DC, attack traffic dying mid-run, firewall rule gone after timeout, Discord message received |

One scenario is enough, and which one matters. UC-04 is the same attack the lab could only watch in Chapter 1 — re-running it measures the project's progress with the project's own test. The cradle chain needs no scenario of its own: its notification path is a single step, validated inside the notifications milestone (C3-04) with a controlled re-execution of the UC-03 cradle. A STAR report on one screenshot would be formalism, not investigation.

## Safeguards before automation

Automated response is the first thing this lab does that can cause harm by itself — a wrong block on a domain controller affects the whole domain, not one host. So the chapter documents its safeguards and operational risks *before* running UC-04, not after: the known-hosts whitelist, the elevated-rule-only trigger, the automatic timeout, the management path that stays outside the response's reach, and the webhook exposure. UC-04 then doubles as the test that the safeguards hold in practice.

## Acceptance criteria

The chapter closes when all of this holds:

- [ ] A CDB list of known lab hosts exists on the manager, and a child rule raises authentication failures from unknown sources; both behaviors (known source, unknown source) are tested with evidence.
- [ ] The `netsh` Active Response triggers on the elevated rule only, blocks the offending source on the domain controller, and the timeout removes the block automatically; both the block and the reversal are observed.
- [ ] Alerts at level 12 and above reach Discord through the custom integration; a notification is received for both the elevated authentication rule and rule 100100.
- [ ] Response safeguards and operational risks are documented before UC-04 runs.
- [ ] UC-04 has reviewed evidence for every step of the cycle — elevated alert, active block, contained attack, automatic reversal, received notification — and a written STAR investigation report.
- [ ] The child rule, the sanitized CDB list, and the integration script are committed to the repository with the reasoning behind them.
- [ ] Software versions and configuration dependencies added in this chapter are documented.
- [ ] Known limitations and gaps are documented.
- [ ] Published evidence contains no credentials, tokens, webhook URLs, personal data, or unnecessary infrastructure details.

## Evidence requirements

The discipline carries over unchanged — controlled tests, expected versus observed results, sanitized screenshots, STAR reports where the structure helps. One sanitization rule is new: the Discord webhook URL is a write credential to the channel, so it never appears in any committed file or screenshot, and documents reference it as a placeholder.

## Out of scope

The chapter leaves out:

- containment at the network edge (FortiGate API blocking) — recorded as future work;
- SOAR platforms and orchestration tooling (Shuffle, n8n, and similar) — the automation here is Wazuh-native;
- external reputation or threat-intelligence lookups — the lab's RFC1918 addresses have nothing useful to look up;
- parsing the download host out of rule 100100's script block text — the custom-integration cost is named above and deferred;
- new detection content beyond the CDB child rule (FortiGate, Suricata, and Sysmon detections stay as delivered);
- response actions on the Windows 10 or Debian endpoints — one responding agent, understood properly, before any repetition.

## Related documentation

- [README](../README.md) — project introduction, architecture, and technology choices.
- [Project Roadmap](../ROADMAP.md) — milestones, current focus, and status.
- [Chapter 2 Closure](./13-chapter-2-closure.md) — the validated detection this chapter builds on.
- [UC-02 Investigation](../investigations/UC-02/report.md) — the attack UC-04 re-runs against the hardened pipeline.
