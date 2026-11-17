#!/usr/bin/env python3
"""Fail closed on drift before staging QA; no writes to WP, merchants or analytics."""
import argparse
import hashlib
import json
from pathlib import Path

# Immutable original Git blobs, verified against GitHub 2026-11-17.
BLOBS = {
    'experience2/apollo-r440/staging-educator-intent.php': 'd1c9d499332d6059bd38842cc9cc66070591a97e',
    'experience2/apollo-r440/assets/educator-intent.css': '46066a94324d06550a1c756440a5c659b384de8b',
    'experience2/apollo-r440/assets/educator-intent.js': '967a43d37d1a1a58063a3fd5598a6c83e55d4558',
    'experience2/apollo-r440/product_evidence.json': '795893be79d49c87a30555e77c7f4999217a997c',
    'experience2/apollo-r439/staging-evidence-receipt.php': '7ee7a2c849d0deade84725f82e6c83eab6c46927',
    'experience2/apollo-r438/source_catalog.json': '60903bdcf67a1f6b22f92508d4dcc181c5f95c5a',
}
NEGATIVE_FLAGS = [
    'merchant_seller_identity_verified', 'specific_paid_sku_verified',
    'payment_checkout_verified', 'deliverable_fulfillment_verified',
    'original_content_rights_verified', 'nasamedia_rights_reviewed_for_product',
    'founder_approved_paid_launch', 'published_grok_asset_id_verified',
]

def inspect(repo: Path):
    failures, hashes = [], {}
    root = repo.resolve()
    for relative, expected in BLOBS.items():
        candidate = root
        for segment in Path(relative).parts:
            candidate = candidate / segment
            if candidate.is_symlink():
                failures.append(f'symlink: {relative}')
                break
        else:
            if not candidate.is_file() or not candidate.resolve().is_relative_to(root):
                failures.append(f'missing/outside root: {relative}')
                continue
            data = candidate.read_bytes()
            actual = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
            hashes[relative] = actual
            if actual != expected:
                failures.append(f'drift: {relative} expected {expected}, got {actual}')
    manifest_file = root / 'experience2/apollo-r440/product_evidence.json'
    if manifest_file.is_file() and not manifest_file.is_symlink():
        try:
            manifest = json.loads(manifest_file.read_text())
            if manifest.get('verification_status') != 'HOLD_NOT_SELLABLE':
                failures.append('commercial proof is not explicitly HOLD')
            if any(manifest.get(field) is not False for field in NEGATIVE_FLAGS):
                failures.append('commercial proof gained an unverified positive gate')
            if any(manifest.get(field) is not None for field in ('paid_checkout_url', 'verified_orders', 'realized_net_revenue')):
                failures.append('unverified checkout, order or revenue claim')
        except (ValueError, OSError) as exc:
            failures.append(f'commercial manifest unreadable: {exc.__class__.__name__}')
    else:
        failures.append('commercial manifest missing or symlinked')
    return {'status': 'PASS' if not failures else 'HOLD', 'source_count': len(BLOBS), 'git_blobs': hashes, 'failures': failures,
            'commercial_status': 'HOLD_NOT_SELLABLE', 'scope': 'local custody check only; not a commercial or live-site verification'}

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--repo-root', required=True)
    p.add_argument('--report')
    args = p.parse_args()
    result = inspect(Path(args.repo_root))
    report = json.dumps(result, sort_keys=True, indent=2) + '\n'
    if args.report: Path(args.report).write_text(report)
    print(report)
    raise SystemExit(result['status'] != 'PASS')

if __name__ == '__main__': main()
