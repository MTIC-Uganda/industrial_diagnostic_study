#!/usr/bin/env python3
"""
Best-effort WhatsApp group notifier for the MTIC upload pipeline.

process_upload.py runs detached on the box (ingest-staging.sh does
`setsid python3 scripts/process_upload.py &`), so its stdout goes to a log file
nobody watches — the operator uploads and then waits 10-20 minutes blind. This
posts a short "started" / "done" / "failed" line to the MTIC WhatsApp group so
the team sees progress instead of waiting in the dark. It reuses the same
whatsmeow bridge endpoint that promote_staging_to_prod.sh already posts to.

Two hard rules make this safe to wire into a live pipeline:

  1. OPT-IN. Does nothing unless MIDD_NOTIFY is truthy. Tests, CI and local runs
     leave it unset, so they never touch the network or slow down. Only the box
     ingest scripts set MIDD_NOTIFY=1.
  2. FAIL-SAFE. Never raises. Any problem (bridge down, timeout, non-2xx, bad
     input) is swallowed and logged, returning False. A notification issue must
     never break or delay an ingestion.

Config (env):
  MIDD_NOTIFY       enable when truthy (1/true/yes/on) — OFF by default
  MIDD_BRIDGE_URL   bridge send endpoint (default http://localhost:8080/api/send)
  MIDD_GROUP_JID    destination JID (default the MTIC group)
"""
import json
import os
import urllib.request

DEFAULT_BRIDGE = "http://localhost:8080/api/send"
DEFAULT_GROUP = "256775102684-1629659312@g.us"  # "Rincol reinvents yaka" (MTIC team)


def enabled():
    """True only when MIDD_NOTIFY is explicitly truthy."""
    return os.environ.get("MIDD_NOTIFY", "").strip().lower() in ("1", "true", "yes", "on")


def notify_group(message, recipient=None, timeout=10):
    """Post `message` to the MTIC WhatsApp group via the bridge.

    Best-effort: returns True only if the bridge accepted it (2xx); returns False
    when disabled or on any failure. Never raises.
    """
    if not enabled():
        return False
    url = os.environ.get("MIDD_BRIDGE_URL", DEFAULT_BRIDGE)
    to = recipient or os.environ.get("MIDD_GROUP_JID", DEFAULT_GROUP)
    payload = json.dumps({"recipient": to, "message": message}).encode("utf-8")
    req = urllib.request.Request(
        url, data=payload, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            ok = 200 <= resp.status < 300
            print(f"[midd_notify] sent={ok} -> {to[:20]}", flush=True)
            return ok
    except Exception as e:  # noqa: BLE001 - notifications must never break ingestion
        print(f"[midd_notify] skipped ({e.__class__.__name__}): {str(e)[:120]}", flush=True)
        return False
