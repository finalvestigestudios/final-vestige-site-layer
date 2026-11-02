"""Read-only, fail-closed cross-lane partner and Jetpack authority report.

NO SEND / NO EXTERNAL REQUEST / NO SUBSCRIBER DATA / NO MERCHANT LINK ACTIVATION.
This script checks only the shape of a human-entered public *review ledger*.
It cannot authenticate merchant approval, native email rendering or legal compliance.
"""
from __future__ import annotations
import argparse
import html
import json
import pathlib
import re
from typing import Any

HERE = pathlib.Path(__file__).resolve().parent
SCHEMA = "fv-dispatch-r77-authority-review-v1"
COMMON = ("final_manuscript_approval", "editorial_factcheck",
          "subscriber_eligibility_verified", "verified_fv_postal_address",
          "actual_jetpack_native_preview", "actual_received_email",
          "working_unsubscribe", "dispatch_signup_notice_approved",
          "founder_send_approval")
OFFER_GATES = ("partner_accepted", "email_channel_permission",
               "named_product_permission", "approved_link_format",
               "published_guide_url_verified", "product_claims_reviewed",
               "current_terms_verified", "purchaser_data_reviewed",
               "near_offer_disclosure_verified")
OFFERS = {"zen12": ("03", 687,
                    "1afb0a27c692df9ef25c556f4a25fa5d01f8c735",
                    "85a9a095120a5e1678788ac930a571d5e9de0a71"),
          "total_focus": ("05", 692,
                          "94ea3c6004d643afa201860ab1879a1cdd4e5920",
                          "d942800ca553c172f5d4735287da2782134d34a8")}
ORDER = ("01", "02", "03", "04", "05", "06")

class EvidenceError(ValueError):
    """Reject malformed or privacy-bearing ledger input."""

def keys(obj: Any, required: set[str], where: str) -> None:
    if not isinstance(obj, dict) or set(obj) != required:
        raise EvidenceError(f"{where}: exactly these keys required: {', '.join(sorted(required))}")

def boolean(obj: Any, name: str) -> None:
    if type(obj) is not bool:
        raise EvidenceError(f"{name} must be a boolean")

def nonnegative_integer(obj: Any, name: str) -> None:
    if type(obj) is not int or obj < 0:
        raise EvidenceError(f"{name} must be a nonnegative integer")

def validate(snapshot: Any) -> dict:
    keys(snapshot, {"schema", "observed_utc", "newsletter", "common_gates", "offers"}, "root")
    if snapshot["schema"] != SCHEMA:
        raise EvidenceError("wrong schema")
    if not isinstance(snapshot["observed_utc"], str) or not re.fullmatch(
        r"20[0-9]{2}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z",
        snapshot["observed_utc"]):
        raise EvidenceError("invalid UTC observation date")
    n = snapshot["newsletter"]
    keys(n, {"enabled", "auto_send", "email_format", "sender_name", "reply_to",
             "recent_sends", "counts", "email_eligible_count",
             "welcome_fieldbook_configured", "welcome_delivery_verified"}, "newsletter")
    for field in ("enabled", "auto_send", "welcome_fieldbook_configured", "welcome_delivery_verified"):
        boolean(n[field], "newsletter." + field)
    if n["email_format"] not in ("excerpt", "full") or n["reply_to"] not in ("no-reply", "author", "comment"):
        raise EvidenceError("invalid newsletter format/reply")
    if n["sender_name"] != "Final Vestige":
        raise EvidenceError("unexpected sender name")
    nonnegative_integer(n["recent_sends"], "recent_sends")
    keys(n["counts"], {"total", "confirmed", "unconfirmed", "suppressed"}, "counts")
    for k,v in n["counts"].items():
        nonnegative_integer(v, "counts." + k)
    if n["email_eligible_count"] is not None:
        nonnegative_integer(n["email_eligible_count"], "email_eligible_count")
    keys(snapshot["common_gates"], set(COMMON), "common_gates")
    for k,v in snapshot["common_gates"].items():
        boolean(v, "common_gates." + k)
    keys(snapshot["offers"], set(OFFERS), "offers")
    for name, row in snapshot["offers"].items():
        keys(row, {"issue", "draft_pr", "draft_commit", "guide_blob", *OFFER_GATES},
             "offer." + name)
        if (row["issue"], row["draft_pr"], row["draft_commit"], row["guide_blob"]) != OFFERS[name]:
            raise EvidenceError("offer provenance mismatch: " + name)
        for k in OFFER_GATES:
            boolean(row[k], "offer." + name + "." + k)
    # Returning data is NOT certifying any entered evidence: this is a source ledger only.
    return snapshot

def report(snapshot: dict) -> dict:
    data = validate(snapshot)
    shared = [k for k in COMMON if not data["common_gates"][k]]
    offers = {}
    for name,row in data["offers"].items():
        false_gates = [k for k in OFFER_GATES if not row[k]]
        offers[name] = {"issue": row["issue"], "draft_pr": row["draft_pr"],
                        "unverified_gates": false_gates,
                        "review_status": "HOLD_MERCHANT" if false_gates else "HOLD_EXTERNAL_AUTHENTICITY"}
    issues = [{"number": i, "classification": "commercial" if i in ("03","05") else "editorial",
               "release_status": "HOLD_UNSENT",
               "additional_status": offers["zen12" if i == "03" else "total_focus"]["review_status"] if i in ("03","05") else None}
              for i in ORDER]
    return {"schema": SCHEMA, "as_of_utc": data["observed_utc"], "campaign_status": "HOLD_UNSENT",
            "send_authorized": False, "email_eligible_count": data["newsletter"]["email_eligible_count"],
            "reported_subscriber_total": data["newsletter"]["counts"]["total"],
            "nonadditive_subscriber_counts": True, "shared_unverified_gates": shared,
            "offers": offers, "issues": issues, "human_review_required": True,
            "limits": "Ledger checks do not verify evidence authenticity, rendering, consent, merchant rights or legal compliance."}

def plain(result: dict) -> str:
    lines = ["FINAL VESTIGE DISPATCH — R77 / HOLD_UNSENT", "NO EMAIL, TEST SEND, PUBLISH, OR SETTINGS CHANGE.",
             "As of: " + result["as_of_utc"], "All six editions: HOLD_UNSENT; #03/#05: additional partner hold.",
             "Verified eligible audience: UNKNOWN" if result["email_eligible_count"] is None
             else "Eligible audience (unverified human-input count): " + str(result["email_eligible_count"]),
             "Nonadditive subscriber total: " + str(result["reported_subscriber_total"]),
             "Shared missing evidence: " + ", ".join(result["shared_unverified_gates"])]
    for name in OFFERS:
        offer = result["offers"][name]
        lines.append(name + " / Issue " + offer["issue"] + " / " + offer["review_status"] +
                     " / missing: " + ", ".join(offer["unverified_gates"]))
    lines.extend(["Neither purchase receipts nor public affiliate signup certify our rights.",
                  "This output is REVIEW ONLY, never an authorization to send."])
    return "\n".join(lines) + "\n"

def html_report(result: dict) -> str:
    rows = "".join("<tr><th scope='row'>%s</th><td>%s</td><td>%s</td></tr>" %
        (html.escape(x["number"]), html.escape(x["classification"]), html.escape(x["release_status"]))
        for x in result["issues"])
    holds = "".join("<li>%s</li>" % html.escape(x) for x in result["shared_unverified_gates"])
    return """<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Final Vestige · Dispatch R77 · HOLD</title>
<style>body{font:16px/1.6 system-ui;background:#090a0a;color:#f4efe6;max-width:850px;padding:24px;margin:auto}
a{color:#c7a66c} h1{line-height:1.14}h2{margin-top:2rem}table{border-collapse:collapse;width:100%}
th,td{padding:10px;text-align:left;border-bottom:1px solid #555}th{color:#e3c695}
.notice{padding:18px;border-left:6px solid #c7a66c;background:#191818}
:focus-visible{outline:3px solid white;outline-offset:3px}
@media(max-width:620px){th,td{padding:7px;font-size:.88rem;overflow-wrap:anywhere}}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}</style>
<main><h1>Dispatch campaign — HOLD_UNSENT</h1>
<p class="notice"><strong>All six issues blocked.</strong> Issues 03 and 05 have additional merchant holds.
Review software cannot authorize sending.</p><p>As of %s. Active email-eligible audience not established.</p>
<h2>Per-issue release status</h2><table><caption>Original four editorial / two commercial pilot</caption>
<thead><tr><th scope="col">Issue</th><th scope="col">Category</th><th scope="col">Status</th></tr></thead><tbody>%s</tbody></table>
<h2>Shared missing evidence</h2><ul>%s</ul>
<h2>External rights</h2><p>Zen12 and Total Focus have unpublished independent guide drafts, but no verified
Final Vestige-specific affiliate email rights, approved links or published permitted guide URLs.</p>
<p>No purchaser or subscriber data are included. No tracking pixels, scripts, merchant destinations, or
automatic send controls exist in this static reviewer. Offline UI is not proof of Jetpack inbox rendering.</p>
</main></html>""" % (html.escape(result["as_of_utc"]), rows, holds)

def main() -> None:
    parser = argparse.ArgumentParser(description="R77 source-ledger reviewer (read-only; never send)")
    parser.add_argument("--input", type=pathlib.Path, default=HERE / "evidence_snapshot.json")
    parser.add_argument("--format", choices=("json","text","html"), default="text")
    args = parser.parse_args()
    result = report(json.loads(args.input.read_text(encoding="utf-8")))
    print(json.dumps(result, indent=2) if args.format=="json"
          else html_report(result) if args.format=="html" else plain(result), end="")

if __name__ == "__main__":
    main()
