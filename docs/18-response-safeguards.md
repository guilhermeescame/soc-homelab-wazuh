# Response Safeguards and Operational Risks

The Active Response is the first part of this lab that acts without a person in the loop. Up to now the lab observed, decoded, and alerted, and a human chose what to do next. A rule that adds a firewall block on its own can also get it wrong on its own, and on a domain controller the fallout from a wrong block spreads to everything that depends on the DC. The risks below, and the guardrails already in place against them, are written down now — before UC-04 puts the response through a full cycle — so the test has something deliberate to check.

The mechanisms are built and evidenced in the [enrichment](./15-cdb-enrichment.md), [Active Response](./16-active-response.md), and [notification](./17-discord-notifications.md) milestones. This document does not rebuild them; it collects, across those three, the ways the response could go wrong and what holds it in check. Status is tracked in the [Roadmap](../ROADMAP.md).

## Blocking the wrong source

The main risk is a block landing on a source that should never have been blocked — a legitimate host caught by a false positive and cut off from the domain controller on its own. Three things sit between an authentication failure and a mistaken block.

The response never fires on a raw failure. It triggers on rule 100110, which only raises its level when the source address is missing from the known-hosts list. A mistyped password from a domain host stays at the base rule 60122 and never reaches the response — the [Active Response test](./16-active-response.md) showed this directly, with failures from a listed host producing no block.

That list is also the response's allow-list. Every host the lab expects to authenticate is on it, so a legitimate source cannot meet rule 100110's condition to begin with. The management workstation went on the list before the response was armed, so an operator mistyping a login cannot block their own access.

The timeout covers what the first two miss. A block that should not have happened still clears itself after 180 seconds with no one intervening, so the damage from a wrong block is measured in minutes.

## Keeping management reachable

A block that caught the management path would lock the lab out of its own infrastructure, and recovering could mean console access to the DC — reason enough to keep that path clear by design. Two things do. The management workstation (192.168.16.65) is on the known-hosts list, so a failed logon from it raises only the base rule. And because the `MGMT-to-SOC` path applies no NAT, the workstation reaches the DC with its real address, matching the list entry directly instead of arriving translated and slipping past. Routine RDP administration runs outside the criterion the response acts on, so it never comes near the trigger.

## Response storms

A brute force fires the rule many times in quick succession, and a naive response would act on each one, stacking identical firewall rules and overlapping timeouts until the response engine worked against itself. Wazuh handles this on its own. On a repeat trigger for an address already blocked, the response checks its active keys, sees the address is handled, and stops instead of adding a duplicate — eight alerts in the Active Response test left one firewall rule and one timeout. The guard is built into Wazuh rather than added here, but the response leans on it, so it belongs in this list. Its evidence is in the [Active Response document](./16-active-response.md).

## Blast radius on a domain controller

A firewall rule on a domain controller touches a machine the whole domain relies on, so the response stays as small as a working block allows. It drops one source address, inbound only, on the single host that raised the alert, and only for the length of the timeout. Outbound traffic is untouched, accounts stay enabled, and nothing propagates to other hosts. A host-firewall block was chosen over anything heavier for this reason, and it stops at the DC instead of extending to the network edge.

## Reaction latency

One property of the response has no safeguard, because none is possible. The block is reactive: the event travels to the manager, the rule evaluates, the response returns to the agent, and the firewall rule is written. That loop is slower than a fast burst of attempts, so the burst that triggers the block finishes before the block exists. Containment reaches the next attempt, not the one that set it off, which the [Active Response test](./16-active-response.md) made visible. For the sustained or repeated attacks the response is built for, that is enough; catching the first attempt would take inline blocking, which the lab does not run. It is recorded here as a known property of a reactive design.

## Notification volume

Notifications have no deduplication like the response does. Eight firings of the rule send eight messages, one per alert. That is fine at the volume this lab produces. Somewhere busier, the channel would need rate limiting or aggregation to stay readable. The filter also works by severity — level 12 and up — so the channel receives any high-severity built-in rule alongside the two custom detections. Both points are covered as gaps in the [notification milestone](./17-discord-notifications.md); neither is harmful here, and both would matter at scale.

## Secret handling and external dependency

The Discord webhook URL can post to the channel, so it is handled as a credential — kept in `ossec.conf` on the manager alone, out of the repository and out of screenshots, and replaced if it ever leaks. The notification path is also the only part of the response chain that leaves the network, since it depends on the manager reaching `discord.com`. If that egress fails, the alert is still in Wazuh and the block still fires; only the message goes missing. Detection and response need nothing beyond the manager and its agents.

## Residual risk accepted

Some risk survives all of the above. The response trusts the known-hosts list completely, so an address wrongly added to it is never blocked, and the list is edited by hand. An attacker who switches to a new address returns as a fresh unknown source and is blocked again, though the switch itself is not stopped. And the chain depends on one field of one event type, so an attack that leaves no usable source address gives the response nothing to work with. These are the edges of a single-technique response at lab scale, and the chapter leaves them as they are.

## Safeguard summary

| Risk | Safeguard | Exercised in UC-04? |
|---|---|---|
| Block a legitimate source | Response fires only on the enriched rule; known-hosts allow-list; timeout auto-reversal | To confirm |
| Lock out the management path | Management host on the list; `MGMT-to-SOC` without NAT; RDP path outside the trigger | To confirm |
| Response storm from a burst | Native active-response deduplication (one block per address) | To confirm |
| Overreach on the domain controller | Minimal action — one address, inbound, host firewall, timed | To confirm |
| Reaction latency (operational limit) | None — reactive by design; contains the next attempt | To confirm |
| Notification flood | Documented gap; severity filter; rate limiting deferred | To confirm |
| Webhook exposure / egress loss | Secret kept off the repository; rotation on exposure; core chain independent of egress | n/a |

UC-04 re-runs the UC-02 brute force against this hardened pipeline, and is where the first five rows are actually tested.
