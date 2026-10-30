"""Read-only, fail-closed preflight for The Dispatch pilot. No sends or site mutations.

The attestation file is deliberately non-sensitive and defaults to all unverified.
Passing this linter does not authorize publishing or replace a human email preview.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

REQUIRED_EVIDENCE = (
    'deduplicated_confirmed_consent',
    'merchant_zen12_affiliate_approval',
    'merchant_zen12_email_permission',
    'merchant_hypnosis_live_affiliate_approval',
    'merchant_hypnosis_live_email_permission',
    'merchant_links_and_checkout_terms_reviewed',
    'zen12_guide_live_and_reviewed',
    'hypnosis_live_guide_live_and_reviewed',
    'rendered_jetpack_preview_reviewed',
    'founder_authorized_test_recipient_and_test_received',
    'business_postal_address_in_rendered_commercial_email',
    'one_action_unsubscribe_in_received_email',
    'sender_headers_and_marketing_disclosure_reviewed',
    'campaign_specific_editor_email_toggle_reviewed',
    'founder_approved_final_content_audience_and_send_date',
)


def inspect(manifest: dict, attestations: dict, folder: Path) -> dict:
    blockers: list[str] = []
    errors: list[str] = []
    if manifest.get('status') != 'DRAFT_UNSENT_NO_SCHEDULING':
        errors.append('manifest_status_changed_from_unsent_draft')
    entries = manifest.get('issues')
    if not isinstance(entries, list) or len(entries) != 6:
        errors.append('campaign_must_have_six_issues')
        entries = entries if isinstance(entries, list) else []
    kinds = [i.get('kind') for i in entries if isinstance(i, dict)]
    if kinds.count('editorial') != 4 or kinds.count('commercial-review-pending') != 2:
        errors.append('campaign_must_remain_four_editorial_two_commercial_review')
    if any(i.get('merchant_affiliate_url') is not None for i in entries if isinstance(i, dict)):
        errors.append('unexpected_active_merchant_affiliate_url')
    numbers = [i.get('number') for i in entries if isinstance(i, dict)]
    if numbers != list(range(1, 7)):
        errors.append('campaign_issue_order_or_ids_invalid')

    for entry in entries:
        if not isinstance(entry, dict):
            errors.append('issue_entry_not_object')
            continue
        num = entry.get('number')
        slug = entry.get('slug')
        if not isinstance(num, int) or not isinstance(slug, str) or not re.fullmatch(r'[a-z0-9-]+', slug):
            errors.append('invalid_issue_name')
            continue
        prefix = f'{num:02d}-{slug}'
        path = folder / 'issues' / f'{prefix}.md'
        if not path.is_file():
            errors.append(f'{prefix}:source_missing')
            continue
        md = path.read_text(encoding='utf-8')
        if entry.get('publish_state') != 'hold' or 'UNSENT DRAFT' not in md:
            errors.append(f'{prefix}:not_explicitly_held')
        for field in ('subject', 'preheader'):
            if f'**{field.title()}:** {entry.get(field)}' not in md:
                errors.append(f'{prefix}:{field}_metadata_drift')
        if '[[VALID_POSTAL_ADDRESS_REQUIRED]]' not in md:
            errors.append(f'{prefix}:postal_hold_missing')
        if '[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]' not in md:
            errors.append(f'{prefix}:unsubscribe_hold_missing')
        if entry.get('kind') == 'commercial-review-pending':
            token = '[[APPROVED_ZEN12_WARMUP_GUIDE_URL_REQUIRED]]' if num == 3 else '[[APPROVED_HYPNOSIS_LIVE_WARMUP_GUIDE_URL_REQUIRED]]' if num == 5 else None
            if not token or entry.get('editorial_cta') != token or token not in md:
                errors.append(f'{prefix}:commercial_guide_not_safely_blocked')
            disclosure = md.find('**Commercial disclosure:**')
            cta = md.find(token) if token else -1
            if disclosure < 0 or cta < 0 or disclosure > cta:
                errors.append(f'{prefix}:commercial_disclosure_not_before_cta')
            for direct in ('https://zen12.com/', 'https://hypnosislive.com/'):
                if direct in md:
                    errors.append(f'{prefix}:live_seller_link_in_campaign_body')
    evidence = attestations.get('checks', {}) if isinstance(attestations, dict) else {}
    for item in REQUIRED_EVIDENCE:
        value = evidence.get(item)
        if not isinstance(value, dict) or value.get('verified') is not True:
            blockers.append(item)
        elif not isinstance(value.get('evidence_reference'), str) or len(value['evidence_reference'].strip()) < 8:
            blockers.append(item + ':missing_proof_reference')
    # This is a readiness aid, not an authorization system; never output a send command.
    return {
        'campaign': manifest.get('id'),
        'status': 'BLOCKED' if blockers or errors else 'REVIEW_READY_NOT_AUTHORIZED_TO_SEND',
        'blocking_evidence_gates': blockers,
        'structural_errors': errors,
        'ready_to_send': False,
        'site_writes_or_emails_performed': False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--campaign-root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--attestations', type=Path)
    parser.add_argument('--expect-blocked', action='store_true', help='CI mode: succeed only while explicitly held')
    args = parser.parse_args()
    root = args.campaign_root
    source = args.attestations or root / 'delivery' / 'release_attestations.json'
    manifest = json.loads((root / 'manifest.json').read_text(encoding='utf-8'))
    attestations = json.loads(source.read_text(encoding='utf-8'))
    report = inspect(manifest, attestations, root)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.expect_blocked:
        return 0 if report['status'] == 'BLOCKED' and not report['structural_errors'] else 1
    return 0 if report['status'] == 'REVIEW_READY_NOT_AUTHORIZED_TO_SEND' else 2


if __name__ == '__main__':
    raise SystemExit(main())
