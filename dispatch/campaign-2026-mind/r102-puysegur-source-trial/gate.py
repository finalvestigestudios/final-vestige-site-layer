"""R102 review-only Puységur edition verifier. Never enables sends or CMS writes."""
from __future__ import annotations
import copy
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent
EXPECTED_CTA = "https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/"
REQUIRED_STOPS = (
    "[[VALID_POSTAL_ADDRESS_REQUIRED]]",
    "[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]",
)
FORBIDDEN_HTML = re.compile(r"<\s*(script|form|iframe|img|video|audio|object|embed|input)\b|\bon\w+\s*=|javascript:", re.I)
PERSONAL_EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
MERCHANT_HREF = re.compile(r'href\s*=\s*["\']https?://(?:www\.)?(?:zen12|inspire3|hypnosislive)\.', re.I)

def inspect(ledger=None, assets=None):
    """Return an immutable decision: CLOSED in all cases; diagnostics never authorize release."""
    if ledger is None:
        ledger = json.loads((ROOT / "source_and_release_ledger.json").read_text(encoding="utf-8"))
    if assets is None:
        assets = {
            "md": (ROOT / "02-puysegur-source-trial.md").read_text(encoding="utf-8"),
            "txt": (ROOT / "02-puysegur-source-trial.txt").read_text(encoding="utf-8"),
            "html": (ROOT / "02-puysegur-review.html").read_text(encoding="utf-8"),
        }
    errors = []
    def fail(label, condition):
        if condition:
            errors.append(label)

    fail("wrong_campaign", ledger.get("issue") != 174 or ledger.get("master_pr") != 175)
    fail("wrong_master_commit", ledger.get("master_sha") != "d57ccdba3aee8f065e143e101c2945f4f3d01647")
    fail("release_state", ledger.get("state") != "HOLD_UNSENT")
    fail("commercial_or_live_cta", ledger.get("cta", {}).get("is_affiliate") is not False
         or ledger.get("cta", {}).get("url") != EXPECTED_CTA
         or ledger.get("cta", {}).get("status") != "PUBLISHED_FIRST_PARTY")
    hold = ledger.get("hold", {})
    fail("unverified_approvals", not isinstance(hold, dict) or not hold or any(v is not False for v in hold.values()))
    delivery = ledger.get("delivery", {})
    fail("fake_jetpack_mime", delivery.get("html_preview_is_received_email") is not False
         or delivery.get("native_jetpack_preheader_field_verified") is not False)
    fail("missing_excerpt_mode", delivery.get("excerpt_mode_on") is not True)
    sources = ledger.get("sources", [])
    fail("sources_missing", not isinstance(sources, list) or len(sources) < 5)
    if isinstance(sources, list):
        fail("source_provenance", not any("catalogue.bnf.fr" in str(s.get("url", "")) for s in sources)
             or not any("jameslindlibrary" in str(s.get("url", "")) for s in sources)
             or not any("wellcomecollection" in str(s.get("url", "")) for s in sources))
    for key in ("md", "txt", "html"):
        body = assets.get(key, "")
        fail("missing_" + key, not isinstance(body, str) or len(body) < 4000)
        fail("email_leak_" + key, bool(PERSONAL_EMAIL.search(body)))
        fail("missing_legal_stop_" + key, not all(stop in body for stop in REQUIRED_STOPS))
        fail("missing_subject_" + key, ledger.get("subject_candidate", "") not in body)
        fail("missing_preheader_" + key, ledger.get("preheader_candidate", "") not in body)
        fail("missing_cta_" + key, EXPECTED_CTA not in body)
        fail("merchant_href_" + key, bool(MERCHANT_HREF.search(body)))
    html = assets.get("html", "")
    md = assets.get("md", "")
    txt = assets.get("txt", "")
    fail("unsafe_html", bool(FORBIDDEN_HTML.search(html)))
    fail("missing_html_language", '<html lang="en">' not in html)
    fail("missing_mobile_viewport", 'name="viewport"' not in html)
    fail("missing_html_table", 'role="presentation"' not in html)
    fail("missing_review_warning", "NOT AN ACTUAL JETPACK EMAIL" not in html)
    fail("multiple_primary_actions", html.count('>Examine the surviving file</a>') != 1)
    fail("narrative_short", len(re.findall(r"\b\w+\b", md)) < 620)
    fail("missing_commission_distinction", "different setting" not in md or "not a controlled trial" not in md)
    fail("missing_failure_reporting", "unsuccessful cure" not in md or "did not come true" not in md)
    fail("misleading_purchase", any(s in (md + txt).lower() for s in ("buy now", "clinically proven", "guaranteed income", "100% effective")))
    fail("wrong_mixture", ledger.get("role") != "issue02_editorial_optional")
    return {"decision": "HOLD_UNSENT", "errors": sorted(set(errors)), "checked": 3}

def main():
    print(json.dumps(inspect(), sort_keys=True))
    return 0 if not inspect()["errors"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
