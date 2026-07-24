#!/usr/bin/env python3
# SOC Home Lab - Wazuh -> Discord integration (C3-04)
# Deployed to /var/ossec/integrations/custom-discord.py on the Wazuh manager.
# Called by the integrator for alerts matching the <integration> filter in
# ossec.conf. Reads the alert, builds a Discord embed, and posts it to the
# webhook. The webhook URL is passed in by the manager (argv[3]) and never
# stored here.
import sys, json, ssl
from urllib import request

# The manager's bundled Python does not trust the system CA store by default,
# so HTTPS to Discord fails cert verification unless pointed at it explicitly.
CA_BUNDLE = "/etc/ssl/certs/ca-certificates.crt"  # Ubuntu system CA store


def main():
    # Wazuh integrator args: 1 = alert file, 2 = api_key (unused), 3 = hook_url
    alert_path = sys.argv[1]
    hook_url = sys.argv[3]

    with open(alert_path, encoding="utf-8") as f:
        alert = json.load(f)

    rule = alert.get("rule", {})
    level = rule.get("level", 0)
    rid = rule.get("id", "N/A")
    desc = rule.get("description", "N/A")
    agent = alert.get("agent", {}).get("name", "N/A")
    groups = ", ".join(rule.get("groups", [])) or "N/A"
    mitre = ", ".join(rule.get("mitre", {}).get("id", [])) or "N/A"

    data = alert.get("data", {})
    srcip = data.get("srcip") or data.get("win", {}).get("eventdata", {}).get("ipAddress", "N/A")
    ts = alert.get("timestamp", "")

    color = 15158332 if level >= 12 else 3447003  # red for >=12, blue otherwise

    payload = {
        "embeds": [{
            "title": f"Wazuh Alert - Rule {rid} (level {level})",
            "description": desc,
            "color": color,
            "fields": [
                {"name": "Agent", "value": agent, "inline": True},
                {"name": "Source IP", "value": str(srcip), "inline": True},
                {"name": "MITRE", "value": mitre, "inline": True},
                {"name": "Groups", "value": groups, "inline": False},
            ],
            "footer": {"text": f"SOC Home Lab - {ts}"},
        }]
    }

    body = json.dumps(payload).encode("utf-8")
    ctx = ssl.create_default_context(cafile=CA_BUNDLE)
    # A custom User-Agent is required: Discord's Cloudflare front rejects the
    # default urllib agent with HTTP 403.
    req = request.Request(hook_url, data=body, headers={
        "Content-Type": "application/json",
        "User-Agent": "SOClab-Wazuh/1.0",
    })
    request.urlopen(req, timeout=10, context=ctx)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"custom-discord error: {e}", file=sys.stderr)
        sys.exit(1)
