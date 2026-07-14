# FortiGate Segmentation Baseline

How the FortiGate separates the three network areas and what the firewall is expected to allow, deny, and log. This is the deliverable of milestone C1-03: the configuration documented here, plus the allow/deny tests that prove it behaves as described.

The underlying networks, IP plan, and host inventory are in the [Infrastructure Baseline](./01-infrastructure-baseline.md); status is tracked in the [Roadmap](../ROADMAP.md).

## Interfaces

| Port | Alias | IP/mask | Administrative access | Connected network |
|---|---|---|---|---|
| port1 | WAN | 192.168.16.244/24 | PING, HTTPS, SSH | Physical network |
| port2 | SOC-Network | 10.10.10.1/24 | PING, HTTPS, SSH | SOC Network |
| port3 | Attack-Network | 10.10.20.1/24 | PING, HTTPS, SSH | Attack Network |

Administrative access is currently enabled on all three interfaces, including port3 — which means Kali can reach the FortiGate's own management services. In a production design this would be closed; here it stays open for lab convenience and is listed under known limitations.

## Routing

The FortiGate holds a single static route: 0.0.0.0/0 via 192.168.16.1 on port1.

The management workstation reaches the SOC Network through a static route configured on the workstation itself — 10.10.10.0/24 via 192.168.16.244 — since the physical router knows nothing about the lab's internal networks.

## Firewall policies

The Evaluation license allows exactly three policies, and all three slots are in use:

| ID | Name | From → To | Source | Destination | Services | Action | NAT | Log |
|---|---|---|---|---|---|---|---|---|
| 1 | SOC-to-Internet | port2 → port1 | SOC-Network | all | ALL | ACCEPT | Yes | All Sessions |
| 2 | MGMT-to-SOC | port1 → port2 | MGMT-Workstation | SOC-Network | RDP, SSH, HTTPS, PING | ACCEPT | No | All Sessions |
| 3 | Attack-to-SOC | port3 → port2 | Attack-Network | SOC-Network | ALL | ACCEPT | No | All Sessions |
| — | Implicit Deny | any → any | all | all | ALL | DENY | — | Violation traffic enabled |

Everything not matched above hits the implicit deny, which logs violation traffic so that denied paths leave evidence.

Two of these policies deserve a word on intent:

- `Attack-to-SOC` allows ALL services on purpose. This is a detection lab: the goal is for attack traffic to cross the boundary, get logged by the FortiGate, and be seen by Suricata and Wazuh — not to be stopped at the edge. NAT is disabled so the telemetry records the real source address (10.10.20.10), which every UC-01 investigation will depend on.
- `MGMT-to-SOC` is the deliberate administration path: a single source object, four services, fully logged. Without it, every interaction with the SOC VMs would go through the ESXi console.

## Expected traffic matrix

What each path should do under the configuration above. This matrix is the test plan for the validation below.

| # | Path | Expected result | Decided by |
|---|---|---|---|
| 1 | Kali → SOC hosts (any service) | Allowed and logged | Policy 3 – Attack-to-SOC |
| 2 | Kali → internet | Denied and logged | Implicit deny |
| 3 | SOC hosts → internet | Allowed and logged | Policy 1 – SOC-to-Internet |
| 4 | SOC hosts → Attack Network | Denied and logged | Implicit deny |
| 5 | Management workstation → SOC hosts (RDP/SSH/HTTPS/PING) | Allowed and logged | Policy 2 – MGMT-to-SOC |
| 6 | Any other WAN source → SOC Network | Denied and logged | Implicit deny |

## Validation tests

All five tests behaved as the matrix predicts. Each log excerpt below was captured from Log & Report > Forward Traffic, filtered to the traffic of the test.

| Test | From | Action | Expected | Observed | Evidence |
|---|---|---|---|---|---|
| T1 | Kali (10.10.20.10) | `ping 10.10.10.10` and `ssh 10.10.10.10` | Allowed, logged by policy 3 | Allowed — both sessions accepted by `Attack-to-SOC (3)` | [t1-kali-para-soc.png](./img/02-fortigate/t1-kali-para-soc.png) |
| T2 | Kali (10.10.20.10) | `ping 8.8.8.8` | Denied, logged by implicit deny | Denied — every attempt logged by `Implicit Deny` | [t2-kali-internet.png](./img/02-fortigate/t2-kali-internet.png) |
| T3 | Windows 10 (10.10.10.30) | browse to an external site | Allowed, logged by policy 1 | Allowed — HTTPS sessions accepted by `SOC-to-Internet (1)` | [t3-soc-internet.png](./img/02-fortigate/t3-soc-internet.png) |
| T4 | Windows 10 (10.10.10.30) | `ping 10.10.20.10` | Denied, logged by implicit deny | Denied — every attempt logged by `Implicit Deny` | [t4-soc-para-attack.png](./img/02-fortigate/t4-soc-para-attack.png) |
| T5 | Management workstation | RDP to 10.10.10.30 | Allowed, logged by policy 2 | Allowed — sessions accepted by `MGMT-to-SOC (2)` | [t5-mgmt-rdp.png](./img/02-fortigate/t5-mgmt-rdp.png) |

Matrix row 6 is not tested separately: no other WAN host is under the lab's control, and the implicit deny behavior it describes is already exercised by T2 and T4.

## Known limitations

- FortiGate administrative access (PING, HTTPS, SSH) is reachable from all three networks, including the Attack Network.
- The three-policy budget is fully spent. Any future segmentation need — for example, splitting SOC traffic by service — requires removing or widening an existing policy.
-