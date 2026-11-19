"""Offline, fail-closed Final Vestige offer-to-revenue QA. No network or CMS writes."""
import json
import sys
from pathlib import Path

REQUIRED_SITES = ("home", "focus", "library", "collection", "dispatch")
GATED_COPY = (
    "with your free dispatch subscription",
    "free with the dispatch subscription",
    "free with email signup",
    "with the dispatch subscription",
)


def audit(snapshot):
    """Return privacy-safe QA decisions, never subscriber identities or raw content."""
    if not isinstance(snapshot, dict):
        raise ValueError("snapshot must be an object")
    pages = snapshot.get("pages", {})
    if not isinstance(pages, dict) or any(not isinstance(pages.get(k), str) for k in REQUIRED_SITES):
        raise ValueError("pages must contain five public-page text strings")
    obs = snapshot.get("observations", {})
    settings = snapshot.get("newsletter", {})
    if not isinstance(obs, dict) or not isinstance(settings, dict):
        raise ValueError("observations and newsletter must be objects")
    result = {}

    # A published/downloadable file, a form submit and a confirmed new lead are distinct.
    lead = obs.get("fresh_double_opt_in_verified") is True
    welcome = obs.get("welcome_received_verified") is True
    pdf = obs.get("pdf_bytes_verified") is True
    result["new_confirmed_lead"] = "PASS" if lead else "HOLD"
    result["welcome_and_pdf"] = "PASS" if lead and welcome and pdf else "HOLD"

    # Browser evidence is required. Source markup alone cannot certify download UX.
    direct = obs.get("direct_pdf_browser_verified") is True
    if not direct:
        result["direct_pdf_browser"] = "HOLD"
        result["cross_page_download_promise"] = "HOLD"
    else:
        result["direct_pdf_browser"] = "PASS"
        conflicting = any(
            phrase in pages[name].lower()
            for name in ("home", "library", "collection", "dispatch")
            for phrase in GATED_COPY
        )
        result["cross_page_download_promise"] = "REVIEW" if conflicting else "PASS"

    # Opt-out of automatic post emails alone does not disprove separately sent editions.
    promises_publish = "when we publish" in (pages["dispatch"] + pages["focus"]).lower()
    autonews = settings.get("email_new_posts_by_default") is True
    actual_send = obs.get("relevant_edition_send_verified") is True
    result["publication_email_promise"] = (
        "REVIEW" if promises_publish and not autonews and not actual_send else "PASS"
    )

    help_text = pages["focus"].lower()
    no_resubscribe = "do not need to sign up again" in help_text
    result["retry_signup_guidance"] = (
        "PASS" if no_resubscribe else "REVIEW" if "sign up again" in help_text else "HOLD"
    )

    # Never equate outbound clicks, form submissions, PDF downloads or followers to sales.
    humans = obs.get("qualified_human_sessions")
    gross, refunds, fees = (obs.get(k) for k in ("settled_gross", "settled_refunds", "settled_fees"))
    verified = obs.get("merchant_settlement_verified") is True
    amounts = (gross, refunds, fees)
    valid_amounts = all(type(n) in (int, float) and n >= 0 for n in amounts)
    valid_humans = type(humans) is int and humans > 0
    if verified and valid_amounts and valid_humans and refunds + fees <= gross:
        result["net_revenue_per_1000_humans"] = round(1000 * (gross - refunds - fees) / humans, 2)
        result["paid_revenue_evidence"] = "PASS"
    else:
        result["net_revenue_per_1000_humans"] = None
        result["paid_revenue_evidence"] = "HOLD"
    return result


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        raise SystemExit("usage: python focus_funnel_contract.py SANITIZED_SNAPSHOT.json")
    path = Path(args[0])
    output = audit(json.loads(path.read_text(encoding="utf-8")))
    print(json.dumps(output, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
