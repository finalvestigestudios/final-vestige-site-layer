"""Fail-closed semantic binding of R186 independent Preparedness gate receipts.

Structural audit only. Neither syntactically correct receipts nor local tests
represent independent source, clinical, food-safety, privacy or QD approval.
"""
from __future__ import annotations

import re

HOLD = 'DRAFT_HARD_HOLD'
SCHEMAS = {
    'r174': 'fv-preparedness-r174-rendered-citation-custody-v1',
    'r175': 'fv-preparedness-r175-link-custody-v1',
    'r177': 'fv-preparedness-r177-safety-excerpt-custody-v1',
    'r178': 'fv-preparedness-r178-35-safety-state-custody-v1',
    'r179': 'fv-preparedness-r179-source-use-crosswalk-v1',
    'r180': 'fv-preparedness-r180-unresolved-decision-packet-v1',
    'r182': 'fv-preparedness-r182-semantic-reconciliation-v1',
    'r184': None,  # Original R184 report has no versioned schema.
    'r185': None,  # Original R185 report has no versioned schema.
}
REQUIRED_FALSE = {
    'r174': ('qualified_source_review', 'food_safety_approved', 'independent_qd_pass',
             'commercial_offer_verified', 'publication_authorized'),
    'r175': ('independent_source_review', 'medical_food_safety_approved',
             'independent_qd_pass', 'commercial_offer_verified', 'publication_authorized'),
    'r177': ('publication_authorized', 'independent_qd_pass', 'qualified_source_review',
             'medical_safety_approved', 'food_safety_approved'),
    'r178': ('publication_authorized', 'independent_qd_pass',
             'qualified_safety_review_complete', 'medical_safety_approved',
             'food_safety_approved', 'source_claims_independently_adjudicated',
             'commercial_product_verified'),
    'r179': ('publication_authorized', 'qualified_safety_review_complete',
             'independent_qd_pass', 'human_source_claim_review_complete',
             'commercial_product_verified', 'word_press_ready'),
    'r180': ('historical_approved_labels_verified', 'source_equivalence_verified',
             'qualified_safety_review_complete', 'independent_qd_pass',
             'publication_authorized', 'commercial_product_verified', 'wordpress_ready'),
    'r182': ('publication_authorized', 'independent_qd_pass', 'native_build_executed',
             'independent_qa_prs_merge_authorized'),
    'r184': ('independent_qa_verified', 'wordpress_publication_performed'),
    'r185': ('independent_qd_verified', 'merchant_offer_verified', 'wordpress_published'),
}
COUNTS = {
    'r174': {'article_count': 35, 'rendered_citations': 2000,
             'rendered_source_uses': 385, 'draft_export_bytes_checked': True},
    'r175': {'articles': 35, 'export_compared': True},
    'r177': {'check_export_requested': True},
    'r178': {'article_count': 35, 'citations': 2000, 'source_use': 385,
             'structural_receipt_only': True, 'human_reviewer_required': True},
    'r179': {'article_count': 35, 'citation_occurrences': 2000,
             'article_source_relationships': 385, 'source_inventory_records': 244,
             'unique_source_ids': 225},
    'r180': {'article_count': 35, 'citation_occurrences': 2000,
             'authored_source_uses': 385, 'review_tickets_pending': 21,
             'family_source_decisions_pending': 11, 'jerky_claim_decisions_pending': 10,
             'legacy_aggregate_source_decisions_pending': 75,
             'shared_literal_url_groups_pending': 32,
             'legacy_counts_overlap_not_additive': True},
    'r182': {},
    'r184': {'articles_checked': 35, 'citation_occurrences_checked': 2000},
    'r185': {'tool_count': 6, 'source_rows': 67, 'citation_occurrences': 173},
}
QA_HEADS = {
    '157': '7d1ae6b8ef93d10cfb6810987672360885e9c1aa',
    '169': 'e9cd7766dac59d47ab467d8945269b9146c2aef5',
    '973': '4d40996a559b0124d74a9bb3bdcd481ad1992aa8',
}
# An extra positive field cannot smuggle an unreviewed approval into a valid packet.
HIGH_RISK_BOOL = frozenset({
    'publication_authorized', 'publication_allowed', 'wordpress_published',
    'wordpress_publication_performed', 'independent_qa_verified',
    'independent_qd_pass', 'independent_qd_verified', 'qualified_safety_review_complete',
    'qualified_source_review', 'independent_source_review', 'qualified_food_safety_review',
    'medical_safety_approved', 'food_safety_approved', 'medical_food_safety_approved',
    'commercial_offer_verified', 'commercial_product_verified', 'merchant_offer_verified',
    'paid_checkout_enabled', 'customer_conversion_verified',
    'source_claims_independently_adjudicated', 'human_source_claim_review_complete',
    'historical_approved_labels_verified', 'source_equivalence_verified',
    'word_press_ready', 'wordpress_ready', 'independent_qa_prs_merge_authorized',
})


def _no_hidden_clearance(obj, location='receipt'):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key in HIGH_RISK_BOOL and value is not False:
                raise ValueError(f'{location}.{key}: explicit false required')
            _no_hidden_clearance(value, location + '.' + str(key))
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            _no_hidden_clearance(value, f'{location}[{i}]')


def verify_contract(label: str, receipt: dict) -> None:
    """Raise ValueError on missing/forged identity, evidence or review hold."""
    if label not in SCHEMAS or not isinstance(receipt, dict):
        raise ValueError('unknown gate or non-object receipt')
    if receipt.get('state') != HOLD:
        raise ValueError(f'{label}: receipt must remain draft hard hold')
    schema = SCHEMAS[label]
    if receipt.get('schema') != schema:
        raise ValueError(f'{label}: wrong or missing producer schema')
    if receipt.get('errors') or receipt.get('error') or receipt.get('reason'):
        raise ValueError(f'{label}: underlying gate reports an error')
    _no_hidden_clearance(receipt)
    for name in REQUIRED_FALSE[label]:
        if receipt.get(name) is not False:
            raise ValueError(f'{label}: {name} missing or falsely cleared')
    for name, expected in COUNTS[label].items():
        actual = receipt.get(name)
        if type(actual) is not type(expected) or actual != expected:
            raise ValueError(f'{label}: {name} evidence drift')
    if label == 'r177':
        rows = receipt.get('files')
        if (not isinstance(rows, list) or len(rows) != 4 or
            {(x.get('slug'), x.get('stage')) for x in rows if isinstance(x, dict)} != {
                ('household-emergency-plan', 'source'),
                ('household-emergency-plan', 'wordpress_draft'),
                ('three-day-kit', 'source'), ('three-day-kit', 'wordpress_draft')
            } or any(x.get('structural_status') != 'REVIEW_HOLD' for x in rows)):
            raise ValueError('r177: four safety/source and export observations required')
    elif label == 'r178':
        if (len(receipt.get('legacy_approved_unverified', [])) != 2 or
            len(receipt.get('not_required_editorial_hold', [])) != 4):
            raise ValueError('r178: six historical review exceptions missing')
    elif label == 'r182':
        if receipt.get('qa_prs') != QA_HEADS:
            raise ValueError('r182: unpinned independent PR identities')
        digest = receipt.get('content_custody_sha256', '')
        if not isinstance(digest, str) or not re.fullmatch('[0-9a-f]{64}', digest):
            raise ValueError('r182: missing content custody digest')
