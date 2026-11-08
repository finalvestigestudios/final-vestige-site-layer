"""Read-only edition-by-edition release-readiness check for The Dispatch.

Does NOT send email, create a post, change settings, import contacts, or declare
that any message is authorized to send. Evidence tokens are deliberately private
references, never underlying subscriber/account data.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SHARED_REQUIREMENTS = (
    'confirmed_unique_consented_audience',
    'newsletter_sender_and_per_post_toggle_reviewed',
    'full_vs_excerpt_delivery_decision_approved',
    'actual_jetpack_post_preview_reviewed',
    'founder_authorized_received_test_verified',
    'final_vestige_postal_address_in_received_commercial_mail',
    'functional_opt_out_in_received_mail',
    'final_content_audience_date_approval',
)
ISSUE_REQUIREMENTS = (
    'independent_source_check',
    'actual_cta_destination_reviewed',
    'mobile_subject_and_body_reviewed',
)
COMMERCIAL_REQUIREMENTS = (
    'inspire3_account_product_acceptance',
    'specific_email_marketing_permission',
    'product_page_and_merchant_terms_checked',
    'approved_tracking_destination_and_link_rules',
    'final_vestige_guide_published_and_accessible',
    'product_claims_evidence_and_disclosure_checked',
)
EXPECTED_COMMERCIAL = (3, 5)


def valid_attestation(value: Any) -> bool:
    """Treat mere booleans and empty 'proof' strings as unverified."""
    if not isinstance(value, dict) or value.get('verified') is not True:
        return False
    reviewer = value.get('reviewer_role')
    reference = value.get('private_evidence_reference')
    return (isinstance(reviewer, str) and len(reviewer.strip()) >= 4
            and isinstance(reference, str) and len(reference.strip()) >= 12
            and '\n' not in reference and '@' not in reference)


def inspect_campaign(manifest: dict, evidence: dict, ledger: dict) -> dict:
    errors: list[str] = []
    entries = manifest.get('issues')
    if manifest.get('status') != 'DRAFT_UNSENT_NO_SCHEDULING':
        errors.append('campaign_manifest_not_unsent')
    if not isinstance(entries, list) or len(entries) != 6:
        errors.append('exactly_six_editions_required')
        entries = []
    ids = [x.get('number') for x in entries if isinstance(x, dict)]
    if ids != [1, 2, 3, 4, 5, 6]:
        errors.append('noncanonical_edition_ids')
    for item in entries:
        if not isinstance(item, dict):
            errors.append('invalid_manifest_entry')
            continue
        if (item.get('number') in EXPECTED_COMMERCIAL) != (item.get('kind') == 'commercial-review-pending'):
            errors.append(f"edition_{item.get('number')}_type_drift")
        if item.get('publish_state') != 'hold' or item.get('merchant_affiliate_url') is not None:
            errors.append(f"edition_{item.get('number')}_publish_or_affiliate_activation")
    citations = ledger.get('entries', [])
    if not isinstance(citations, list) or [x.get('number') for x in citations if isinstance(x, dict)] != ids:
        errors.append('source_ledger_issue_mismatch')
    shared = evidence.get('shared', {})
    specifics = evidence.get('issues', {})
    rows = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        num = entry['number']
        kind = entry['kind']
        own = specifics.get(str(num), {})
        required = ISSUE_REQUIREMENTS + (COMMERCIAL_REQUIREMENTS if num in EXPECTED_COMMERCIAL else ())
        missing = [f'shared:{key}' for key in SHARED_REQUIREMENTS if not valid_attestation(shared.get(key))]
        missing += [f'issue:{key}' for key in required if not valid_attestation(own.get(key))]
        # The approved guide token is not a valid, navigable CTA. It must remain
        # a block even if every checklist field gets mechanically checked True.
        if kind == 'commercial-review-pending' and str(entry.get('editorial_cta', '')).startswith('[['):
            missing.append('issue:approved_guide_cta_still_placeholder')
        if not entry.get('subject') or not entry.get('preheader'):
            missing.append('issue:subject_or_preheader_missing')
        matching = next((x for x in citations if isinstance(x, dict) and x.get('number') == num), None)
        if not matching or matching.get('cta_expected') != entry.get('editorial_cta'):
            missing.append('issue:source_ledger_cta_not_in_sync')
        rows.append({
            'edition': num,
            'classification': kind,
            'status': 'BLOCKED' if missing or errors else 'HUMAN_REVIEW_CANDIDATE_ONLY',
            'missing_evidence': sorted(set(missing)),
            'send_authorized': False,
            'send_action_available': False,
        })
    return {
        'campaign_id': manifest.get('id'),
        'status': 'DRAFT_HOLD',
        'structural_errors': errors,
        'editions': rows,
        'editorial_review_candidates': [x['edition'] for x in rows if x['classification'] == 'editorial' and x['status'] == 'HUMAN_REVIEW_CANDIDATE_ONLY'],
        'commercial_review_candidates': [x['edition'] for x in rows if x['classification'] == 'commercial-review-pending' and x['status'] == 'HUMAN_REVIEW_CANDIDATE_ONLY'],
        'no_email_post_settings_list_or_tracking_changes': True,
        'authorized_to_send_anything': False,
        'human_approval_still_required': True,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--campaign-root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--evidence', type=Path, default=None)
    args = parser.parse_args(argv)
    root = args.campaign_root
    manifest = json.loads((root/'manifest.json').read_text(encoding='utf-8'))
    evidence = json.loads((args.evidence or root/'readiness'/'edition_attestations.json').read_text(encoding='utf-8'))
    ledger = json.loads((root/'readiness'/'canonical_cta_ledger.json').read_text(encoding='utf-8'))
    print(json.dumps(inspect_campaign(manifest,evidence,ledger),indent=2,ensure_ascii=False))
    return 0  # inspection is successful even when publication remains blocked

if __name__=='__main__':
    raise SystemExit(main())
