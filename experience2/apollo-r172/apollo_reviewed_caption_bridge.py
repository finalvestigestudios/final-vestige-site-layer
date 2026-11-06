"""R172: explicitly review R171 caption changes without weakening R169/R170.

Builds ONLY an offline, pinned WordPress editor preview. The original post is
never edited, and a synthetic witness is possible only for unit tests (not CLI).
An R172 pass is *not* installed WordPress or release acceptance.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EX2 = HERE.parent
# The predecessor modules are independent additive PR directories. This shim
# makes the chain runnable from a clean checkout without an editable install.
for folder in ("apollo-r166", "apollo-r167", "apollo-r168", "apollo-r169", "apollo-r170", "apollo-r171"):
    location = str(EX2 / folder)
    if location not in sys.path:
        sys.path.insert(0, location)

from apollo_caption_readability import transform as reflow_captions, NASA_LINKS, digest  # noqa: E402
from apollo_executable_custody_gate import preflight as r170_preflight, validate_executable, slices, SCRIPT, STYLE, surfaces  # noqa: E402
from apollo_source_conversion_gate import verify as verify_editorial  # noqa: E402
from wp_source_custody_gate import WITNESS  # noqa: E402
from wp_block_pack import START, END  # noqa: E402

MARKER = 'FV_APOLLO_R172_REVIEWED_CAPTIONS_V1'
CAPTION_CSS = EX2 / 'apollo-r171' / 'apollo_caption_readability.css'
CAPTION_MODULE = EX2 / 'apollo-r171' / 'apollo_caption_readability.py'
EXPECTED_CAPTION_MODULE_SHA256 = 'c7b88c83b92a4842a7d202847e775a9cbe8be7e709826815b66142df7d6c6e1a'


def _sha(value: str) -> str:
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def _css_block() -> str:
    css = CAPTION_CSS.read_text(encoding='utf-8')
    # CSS must remain the reviewed R171 implementation; drift is a new review.
    if _sha(css) != '11b810d6398bdd09c3878124a1d846776cef6ac481cccfe409b6681f7de242e0':
        raise ValueError('HOLD: reviewed R171 CSS SHA-256 drift')
    if any(token in css.lower() for token in ('@import', 'url(', 'expression(', '</style', '<script')):
        raise ValueError('HOLD: unexpected CSS external asset or executable surface')
    return '\n<!-- ' + MARKER + ' -->\n<style>\n' + css + '\n</style>\n'


def reviewed_extension(staged_r170: str) -> tuple[str, dict]:
    """Only exact R171 figcaption normalization + one scoped CSS block is allowed."""
    if hashlib.sha256(CAPTION_MODULE.read_bytes()).hexdigest() != EXPECTED_CAPTION_MODULE_SHA256:
        raise ValueError('HOLD: R171 caption transformer implementation drift')
    if MARKER in staged_r170:
        raise ValueError('HOLD: R172 already applied')
    changed, r171 = reflow_captions(staged_r170)
    if len(r171['captions']) != 3:
        raise ValueError('HOLD: expected three independently attested captions')
    if not changed.rstrip().endswith(END):
        raise ValueError('HOLD: Gutenberg editor final block is not closed')
    last = changed.rfind(END)
    last_start = changed.rfind(START)
    if last_start < 0 or last < last_start:
        raise ValueError('HOLD: final Gutenberg boundary invalid')
    if '<script>' not in changed[last_start:last]:
        raise ValueError('HOLD: final Gutenberg executable block drift')
    output = changed[:last] + _css_block() + changed[last:]
    if output.count(MARKER) != 1:
        raise ValueError('HOLD: duplicate R172 marker')
    return output, r171


def verify_reviewed(before: str, staged_r170: str, candidate: str) -> dict:
    """An intentional, narrow exception: no changed legacy code, links or copy.

    The golden R170 output MUST first pass unchanged R169+R170 verifiers.
    R172 only allows R171's three exact caption shapes and one exact CSS style.
    Any independent mutation is a HOLD, including an apparently innocuous CTA.
    """
    baseline = validate_executable(before, staged_r170)
    approved, caption_receipt = reviewed_extension(staged_r170)
    if candidate != approved:
        raise ValueError('HOLD: output differs from exact R170 + R171 approved changes')
    verify_editorial(before, candidate)
    if candidate.count(START) != before.count(START) or candidate.count(END) != before.count(END):
        raise ValueError('HOLD: Gutenberg block count drift')
    if slices(SCRIPT, candidate) != slices(SCRIPT, staged_r170):
        raise ValueError('HOLD: unexpected JavaScript drift')
    base_styles, after_styles = slices(STYLE, staged_r170), slices(STYLE, candidate)
    if after_styles != base_styles + [('', '\n' + CAPTION_CSS.read_text(encoding='utf-8') + '\n')]:
        raise ValueError('HOLD: CSS baseline or reviewed R171 style changed')
    surface_before, surface_after = surfaces(staged_r170), surfaces(candidate)
    if surface_before.triggers != surface_after.triggers:
        raise ValueError('HOLD: event handler surface drift')
    if surface_before.structural != surface_after.structural:
        raise ValueError('HOLD: new script/form/frame/meta/linked source surface')
    if any(candidate.count(u) != before.count(u) for u in NASA_LINKS):
        raise ValueError('HOLD: NASA archive citation drift')
    return {
        'gate': 'R172_EXACT_REVIEWED_CAPTIONS_OFFLINE_PASS',
        'base_r170_gate': baseline['gate'],
        'original_editor_sha256': _sha(before),
        'r170_preview_sha256': _sha(staged_r170),
        'reviewed_preview_sha256': _sha(candidate),
        'caption_origins_sha256': [c['before_sha256'] for c in caption_receipt['captions']],
        'caption_results_sha256': [c['after_sha256'] for c in caption_receipt['captions']],
        'reviewed_css_sha256': _sha(CAPTION_CSS.read_text(encoding='utf-8')),
        'caption_count': 3,
        'unchanged_script_count': len(slices(SCRIPT, candidate)),
        'nasa_source_links_preserved': len(NASA_LINKS),
        'additional_tracking_scripts': 0,
        'additional_forms_or_iframes': 0,
        'approved_for_publish': False,
        'wordpress_writes': 0,
        'site_staging_qa': 'NOT_EXECUTED',
        'genuine_axe': 'NOT_EXECUTED',
        'production_cwv': 'NOT_MEASURED',
        'paid_orders_and_net_revenue': 'NOT_VERIFIED',
    }


def build_preview(before: str, witness: dict | None = None) -> tuple[str, dict]:
    """Use strict pinned production witness unless tests explicitly supply a fixture."""
    staged, receipt = r170_preflight(before, WITNESS if witness is None else witness)
    proposed, _ = reviewed_extension(staged)
    receipt['r172'] = verify_reviewed(before, staged, proposed)
    return proposed, receipt


if __name__ == '__main__':
    import argparse
    cli = argparse.ArgumentParser(description='R172 offline-only pinned Gutenberg preview (NEVER publishes)')
    cli.add_argument('pinned_raw_editor_content', type=Path)
    cli.add_argument('preview_output', type=Path)
    args = cli.parse_args()
    src = args.pinned_raw_editor_content.read_text(encoding='utf-8')
    preview, audit = build_preview(src)  # CLI cannot override witness
    args.preview_output.parent.mkdir(parents=True, exist_ok=True)
    args.preview_output.write_text(preview, encoding='utf-8')
    args.preview_output.with_suffix('.audit.json').write_text(json.dumps(audit, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps(audit['r172'], sort_keys=True))
