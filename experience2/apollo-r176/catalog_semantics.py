"""R176 | exact-source-gated, no-CSS-readable catalog caution.

Staging-only transformer. Runs R175's verified correction first; changes solely
that correction's markup. Fails closed if source is different. No WP writes.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

SIBLING = Path(__file__).resolve().parents[1] / 'apollo-r175'
if str(SIBLING) not in sys.path:
    sys.path.insert(0, str(SIBLING))
try:
    from verified_catalog_label import rewrite as r175_rewrite, REPLACEMENT as R175, blob, LINKS, sha, PINNED_BLOB
except ImportError:
    # Local archive-only fixture testing; production CI must use repo sibling.
    from verified_catalog_label import rewrite as r175_rewrite, REPLACEMENT as R175, blob, LINKS, sha, PINNED_BLOB

R176 = (
    '<div class="fv-ex2-ledger__recordid" data-fvx-r175-catalog-review="unverified">'
    'NASA crew-training photograph. '
    '<p class="fv-ex2-catalog-warning"><strong>Catalog identification not verified.</strong> '
    'S67-19766 is a reported ID, but the linked NASA archive page does not confirm '
    'that this identifier belongs to this photograph.</p></div>'
)


def integrate(r174_html: str, *, expected_blob: str = PINNED_BLOB) -> tuple[str, dict]:
    if blob(r174_html) != expected_blob:
        raise ValueError('STAGING HOLD: R174 source differs from pinned Git blob')
    r175_html, r175_audit = r175_rewrite(r174_html, expected_blob=expected_blob)
    if r175_html.count(R175) != 1 or R176 in r175_html:
        raise ValueError('STAGING HOLD: R175 catalog notice absent or ambiguous')
    links = LINKS.findall(r175_html)
    upgraded = r175_html.replace(R175, R176, 1)
    if upgraded.replace(R176, R175, 1) != r175_html:
        raise ValueError('STAGING HOLD: transformation not exactly reversible')
    if LINKS.findall(upgraded) != links or upgraded.count('data-fvx-record') != r175_html.count('data-fvx-record'):
        raise ValueError('STAGING HOLD: changed historical source or record inventory')
    if any(upgraded.count(k) != r175_html.count(k) for k in ('<script', '<style', '<form', 'data-fvx-r174-media-custody=')):
        raise ValueError('STAGING HOLD: unexpected executable or provenance change')
    if len(links) != 14 or upgraded.count('data-fvx-r174-media-custody=') != 6:
        raise ValueError('STAGING HOLD: incomplete authentic Research Desk source')
    return upgraded, {
        'status': 'BUILT_NOT_INSTALLED',
        'source_r174_git_blob': blob(r174_html),
        'source_r175_sha256': sha(r175_html),
        'candidate_r176_sha256': sha(upgraded),
        'records': 6, 'original_links': len(links),
        'diff_scope': 'one existing record-01 catalog notice',
        'link_destinations_changed': False,
        'external_scripts_added': False, 'commerce_links_added': False,
        'no_js_css_dependency_for_notice': False,
        'paid_media_rights_verified': False, 'wp_staging_accepted': False,
        'attributed_revenue_verified': False,
    }


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('r174_source', type=Path, help='Exact source in experience2/apollo-r174')
    parser.add_argument('candidate_out',type=Path)
    args=parser.parse_args()
    out,receipt=integrate(args.r174_source.read_text(encoding='utf8'))
    args.candidate_out.parent.mkdir(exist_ok=True,parents=True)
    args.candidate_out.write_text(out,encoding='utf8')
    args.candidate_out.with_suffix('.audit.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n',encoding='utf8')
    print(json.dumps(receipt,sort_keys=True))

if __name__=='__main__':
    main()
