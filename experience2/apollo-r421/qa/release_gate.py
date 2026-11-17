#!/usr/bin/env python3
"""Explicit unforgeable hard hold, pending governed staged evidence and owner approval."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
gates={
 'exact_remote_commit_source_qa':'NOT_EXECUTED',
 'real_navigated_staging_http':'BLOCKED',
 'genuine_axe_core':'UNAVAILABLE',
 'navigation_lcp_cls':'UNMEASURED',
 'manual_screenreader':'NOT_EXECUTED',
 'image_reuse_rights':'NOT_CERTIFIED',
 'verified_payable_educator_sku':'UNVERIFIED',
 'grok_published_asset_id':'UNVERIFIED',
 'merchant_confirmed_revenue':'NOT_COMPUTABLE',
 'independent_QD':'PENDING',
 'founder_release_approval':'PENDING'
}
(root/'QA').mkdir(exist_ok=True)
(root/'QA/release-gate.json').write_text(json.dumps({'release':'HARD_HOLD','gate_status':gates},indent=2)+'\n')
print('HARD HOLD: no staging navigation, axe/CWV, certified SKU, revenue or founder approval')
raise SystemExit(2)
