"""Read a public-safe, aggregate snapshot. NEVER connects to WordPress or an inbox."""
import json
from pathlib import Path
from audience_contract import reconcile, release_decision, revenue_per_1000

BASE = Path(__file__).resolve().parent


def run():
    snapshot = json.loads((BASE / "REDACTED_LIVE_SOURCE_SNAPSHOT.json").read_text(encoding="utf-8"))
    if snapshot.get("no_personal_data") is not True or snapshot.get("no_writes_or_sends") is not True:
        raise ValueError("this is not an approved read-only sanitized snapshot")
    out = reconcile(snapshot["newsletter"], snapshot["subscribers"], snapshot["followers"])
    gate = release_decision(snapshot["issues"], snapshot["release_proof"])
    out["issues"] = gate["issues"]
    out["all_held"] = gate["all_held"]
    out["recent_sends_never_emailed"] = sum(x == "never_sent_opted_out" for x in snapshot["recent_send_statuses"])
    out["net_revenue_per_1000_qualified_humans"] = str(x) if (x := revenue_per_1000(None, None)) is not None else None
    return out


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
