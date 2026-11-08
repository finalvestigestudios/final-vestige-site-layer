"""Zero-send, all-six Dispatch editorial-vs-legal-purpose guard.

Editorial mix is NOT a CAN-SPAM legal classification. No network, email,
WordPress, analytics, imports, or merchant activity. This tool never releases
an edition, even if its draft integrity checks pass.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

EDITORIAL = (1, 2, 4, 6)
OFFER = (3, 5)
POSTAL = '[[VALID_POSTAL_ADDRESS_REQUIRED]]'
OPT_OUT = '[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]'
GUIDES = {
    3: '[[APPROVED_ZEN12_WARMUP_GUIDE_URL_REQUIRED]]',
    5: '[[APPROVED_HYPNOSIS_LIVE_WARMUP_GUIDE_URL_REQUIRED]]',
}
SOURCE = 'https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business'


def header(text: str, key: str) -> str | None:
    m = re.search(r'^\*\*' + re.escape(key) + r':\*\*\s*(.+?)\s*$', text, re.M)
    return m.group(1).strip() if m else None


def inspect(manifest: dict, manuscripts: dict[int, str]) -> dict:
    """Check draft fidelity; report zero authorization regardless of the result.

    CAN-SPAM primary purpose needs message-specific review. All six remain
    potential marketing email for operational readiness, including editorials.
    """
    global_errors: list[str] = []
    if manifest.get('status') != 'DRAFT_UNSENT_NO_SCHEDULING':
        global_errors.append('manifest_not_draft_unsent')
    entries = manifest.get('issues')
    if not isinstance(entries, list) or [x.get('number') for x in entries if isinstance(x, dict)] != list(range(1, 7)) or len(entries) != 6:
        global_errors.append('not_exact_six_canonical_issues')
        entries = []
    if manifest.get('mix') != {'editorial': 4, 'commercial_review_pending': 2}:
        global_errors.append('four_two_plan_changed')
    result = []
    for entry in entries:
        n = entry['number']
        text = manuscripts.get(n, '')
        problems = []
        expected_kind = 'commercial-review-pending' if n in OFFER else 'editorial'
        if entry.get('kind') != expected_kind or header(text, 'Content type') != expected_kind:
            problems.append('edition_editorial_type_mismatch')
        if header(text, 'Subject') != entry.get('subject'):
            problems.append('subject_drift')
        if header(text, 'Preheader') != entry.get('preheader'):
            problems.append('preheader_drift')
        if 'STATUS: UNSENT DRAFT — DO NOT PUBLISH OR EMAIL' not in text:
            problems.append('internal_do_not_send_guard_missing')
        if entry.get('publish_state') != 'hold' or entry.get('merchant_affiliate_url') is not None:
            problems.append('publication_or_earning_link_activated')
        if text.count(POSTAL) != 1 or text.count(OPT_OUT) != 1:
            problems.append('draft_postal_or_unsubscribe_proof_placeholder_missing')
        if 'Pre-send compliance block' not in text:
            problems.append('presend_compliance_warning_missing')
        if n in OFFER:
            guide = GUIDES[n]
            if entry.get('editorial_cta') != guide or text.count(guide) != 1:
                problems.append('commercial_guide_hold_or_manifest_mismatch')
            match = re.search(r'^\*\*Commercial disclosure:\*\*(.+)$', text, re.M)
            if not match or 'commission' not in match.group(1).lower() or 'may' not in match.group(1).lower():
                problems.append('near_offer_conditional_commission_disclosure_missing')
            elif text.find('**Commercial disclosure:**') > text.find(guide):
                problems.append('affiliate_disclosure_after_guide_cta')
            elif text.find(guide) - text.find('**Commercial disclosure:**') > 750:
                problems.append('affiliate_disclosure_too_far_from_guide_cta')
        else:
            if entry.get('editorial_cta', '').startswith('[['):
                problems.append('editorial_cta_is_placeholder')
        result.append({
            'edition': n,
            'editorial_allocation': expected_kind,
            'can_spam_primary_purpose': 'UNDETERMINED_REQUIRES_MESSAGE_SPECIFIC_REVIEW',
            'conservative_postal_and_unsubscribe_proof_required': True,
            'received_mail_postal_verified': False,
            'functional_unsubscribe_verified': False,
            'received_jetpack_email_verified': False,
            'merchant_email_permission_verified': False if n in OFFER else None,
            'source_integrity': 'PASS_DRAFT_GUARDS_ONLY' if not problems else 'ERROR',
            'violations': sorted(set(problems)),
            'send_authorized': False,
            'release': 'HOLD_MERCHANT_AND_UNSENT' if n in OFFER else 'HOLD_UNSENT',
        })
    return {
        'source': SOURCE,
        'interpretive_scope': 'Conservative operational gate, not a legal opinion',
        'legal_finding': 'Editorial-versus-offer allocation cannot establish CAN-SPAM primary purpose or an exemption',
        'global_errors': sorted(set(global_errors)),
        'editions': result,
        'structural_integrity': not global_errors and len(result) == 6 and all(not x['violations'] for x in result),
        'all_six_must_have_received_mail_postal_and_optout_evidence': True,
        'all_six_hold': True,
        'email_sending_capability': False,
        'approval_cannot_be_recorded_by_this_tool': True,
    }


def read_campaign(root: Path) -> dict:
    m = json.loads((root / 'manifest.json').read_text(encoding='utf-8'))
    texts = {x['number']: (root / 'issues' / (f"{x['number']:02d}-" + x['slug'] + '.md')).read_text(encoding='utf-8') for x in m['issues']}
    return inspect(m, texts)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = p.parse_args(argv)
    report = read_campaign(args.root)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report['structural_integrity'] else 1  # 0 means valid DRAFT, NEVER send-safe.


if __name__ == '__main__':
    raise SystemExit(main())
