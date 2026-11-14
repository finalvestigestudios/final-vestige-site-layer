"""R350 offline-only release and revenue evidence checks. No I/O outside local files."""
import json
from pathlib import Path

def audit(data):
    issues=data["issues"]; n=data["newsletter"]
    blockers=[]
    if len(issues)!=6 or [x["n"] for x in issues]!=list(range(1,7)):
        blockers.append("six_issue_integrity")
    if sum(x["kind"]=="editorial" for x in issues)!=4 or [x["n"] for x in issues if x["kind"]=="commercial"]!=[3,5]:
        blockers.append("four_two_mix")
    if any(x["status"] not in ("HOLD_UNSENT","HOLD_UNSENT_HOLD_MERCHANT") for x in issues):
        blockers.append("release_status")
    if any(x["kind"]=="commercial" and x["cta"] for x in issues):
        blockers.append("commercial_guide_activated")
    if any(v is True for offer in data["commercial_offers"].values() for v in offer.values()):
        blockers.append("merchant_attestation_unproved")
    if n["confirmed"]+n["unconfirmed"]>n["total"]:
        blockers.append("counts_overlap_no_addition")
    if n["eligible_email_recipients"] is None:
        blockers.append("eligible_recipients_unknown")
    if not data["release"]["publisher_postal_verified"]:
        blockers.append("publisher_postal_unknown")
    if not data["release"]["unsubscribe_verified"]:
        blockers.append("working_unsubscribe_unknown")
    if not data["release"]["native_preview_received"]:
        blockers.append("native_received_email_unknown")
    if not data["release"]["founder_final_approval"]:
        blockers.append("no_final_founder_approval")
    if not data["paid_outcomes"]["merchant_settled_orders"] is not None:
        blockers.append("settled_sales_unknown")
    if data["paid_outcomes"]["qualified_human_sessions"] is None:
        blockers.append("qualified_sessions_unknown")
    urls=[x["cta"] for x in issues if x["cta"]]
    duplicates=sorted({u for u in urls if urls.count(u)>1})
    return {"status":"HOLD_UNSENT","send_authorized":False,"blockers":blockers,
            "repeated_editorial_urls":duplicates,"net_revenue_per_1000":None}

if __name__=="__main__":
    print(json.dumps(audit(json.loads((Path(__file__).parent/"SIX_ISSUE_RELEASE_LEDGER.json").read_text())),indent=2))
