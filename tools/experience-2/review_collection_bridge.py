#!/usr/bin/env python3
"""Review-only patch for the published FV seven-chapter homepage editor export.

No WordPress/network writes. Fails closed on source or guide drift. Never use
the resulting local HTML as an approved Gutenberg/production replacement.
"""
import argparse
import hashlib
import json
from pathlib import Path

EXIT = '''<section class="fv-hf__exit" aria-label="Continue exploring Final Vestige">
        <p>THE ARCHIVE DOESN'T END HERE.</p>
        <a href="https://finalvestige.com/blog/">Investigations <span aria-hidden="true">↗</span></a>
        <a href="https://finalvestige.com/accountability/">The Public Record <span aria-hidden="true">↗</span></a>
        <a href="https://finalvestige.com/free-resources/">Research Library <span aria-hidden="true">↗</span></a>
        <a href="https://finalvestige.com/focus/">Free Focus Fieldbook <span aria-hidden="true">↗</span></a>
      </section>'''
BRIDGE = '''
        <p class="fv-hf__commerce-bridge"><span class="fv-hf__commerce-kicker">PHYSICAL RECORD · OPTIONAL PARTNER GUIDE</span><a href="/mini-museum-history-collectibles/">Explore the Mini Museum collecting guide <span aria-hidden="true">↗</span></a><span class="fv-hf__commerce-note">What to check before considering a specimen. Sponsored links are disclosed on the guide.</span></p>'''
STYLE = '''
<style id="fv-ex2-collection-bridge-review">
/* Review-only commercial bridge: no tracking, dynamic layout, or merchant links. */
.fv-hf .fv-hf__exit > .fv-hf__commerce-bridge {
 grid-column:1 / -1; min-width:0; border-top:1px solid var(--hf-line);
 margin:0; padding:18px 0 0; display:flex; flex-wrap:wrap; align-items:center;
 gap:8px 18px; color:var(--hf-muted); font:500 14px/1.55 var(--hf-sans);
 letter-spacing:normal; overflow-wrap:anywhere;
}
.fv-hf .fv-hf__exit .fv-hf__commerce-kicker {
 color:var(--hf-gold); font:700 11px/1.5 var(--hf-sans);
 letter-spacing:.07em;
}
.fv-hf .fv-hf__exit .fv-hf__commerce-bridge a {
 min-height:44px; display:inline-flex; align-items:center; gap:.4em;
 color:var(--hf-ink); text-decoration:underline; text-underline-offset:3px;
 font:700 14px/1.55 var(--hf-sans);
}
.fv-hf .fv-hf__exit .fv-hf__commerce-bridge a:hover {color:var(--hf-gold)}
.fv-hf .fv-hf__exit .fv-hf__commerce-bridge a:focus-visible {
 outline:3px solid var(--hf-gold); outline-offset:3px;
}
.fv-hf .fv-hf__exit .fv-hf__commerce-note {font:500 13px/1.5 var(--hf-sans)}
@media (max-width:600px) {
 .fv-hf .fv-hf__exit > .fv-hf__commerce-bridge {align-items:flex-start; flex-direction:column; gap:8px}
}
</style>'''
CHAPTER_IDS = ('fv-hf-title', 'fv-hf-chronicle', 'fv-hf-evidence',
               'fv-hf-inquiry', 'fv-hf-method-title', 'fv-hf-observer',
               'fv-hf-mind-title')
GUIDE_LINK = '/mini-museum-history-collectibles/'


def digest(s):
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


def invariants(src):
    return {'exact_exit': src.count(EXIT) == 1,
            'no_existing_commerce_bridge': 'fv-hf__commerce-bridge' not in src,
            'original_four_exit_links': EXIT.count('<a href=') == 4,
            '72_margins': src.count('class="fv-margin-strip__item"') == 72,
            'native_jetpack': src.count('<!-- wp:jetpack/subscriptions') == 1,
            'seven_chapters': all(src.count('id="' + a + '"') == 1 for a in CHAPTER_IDS),
            'original_focus': 'https://finalvestige.com/focus/' in src and '/focus/' in src,
            'original_published_merchant_link_absent': GUIDE_LINK not in src}


def verify_guide(guide):
    return {
        'guide_mentions_product': 'Mini Museum' in guide,
        'guide_has_affiliate_disclosure': 'Affiliate disclosure:' in guide,
        'guide_uses_sponsored_rel': 'rel="sponsored noopener noreferrer"' in guide,
        'guide_has_expected_awin_creative': 's=4236132&amp;v=89949&amp;q=552988&amp;r=3055117' in guide,
    }


def patch(src, guide):
    pre = invariants(src)
    linked = verify_guide(guide)
    if not all(pre.values()) or not all(linked.values()):
        raise ValueError('HOLD: source/partner guide drift; ' + json.dumps({'source': pre, 'guide': linked}))
    candidate = src.replace(EXIT, EXIT.replace('      </section>', BRIDGE + '\n      </section>') + STYLE, 1)
    restored = candidate.replace(BRIDGE + '\n', '', 1).replace(STYLE, '', 1)
    assert restored == src
    assert candidate.count(GUIDE_LINK) == 1
    assert candidate.count('class="fv-margin-strip__item"') == 72
    assert candidate.count('<!-- wp:jetpack/subscriptions') == 1
    return candidate, {'source_checks': pre, 'destination_checks': linked,
                       'original_sha256': digest(src), 'candidate_sha256': digest(candidate),
                       'original_bytes': len(src.encode()), 'candidate_bytes': len(candidate.encode()),
                       'byte_perfect_restore': restored == src,
                       'new_affiliate_links': 0, 'new_scripts': 0,
                       'real_paid_conversions': 'NOT VERIFIED',
                       'hosted_browser': 'NOT EXECUTED',
                       'owner_release_approval': 'NOT GRANTED'}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--homepage', required=True, help='Read-only raw WordPress editor export (UTF-8).')
    p.add_argument('--guide', required=True, help='Read-only raw WordPress Mini Museum guide export.')
    p.add_argument('--output', required=True, help='Local draft output; never a WP API endpoint.')
    p.add_argument('--report', required=True, help='Local JSON evidence report.')
    a = p.parse_args()
    hp, gd = Path(a.homepage), Path(a.guide)
    o = Path(a.output)
    for path in (hp, gd):
        if not path.exists() or not path.is_file():
            p.error(f'INPUT_MISSING: {path}')
    if o.resolve() in (hp.resolve(), gd.resolve()):
        p.error('NO_SOURCE_OVERWRITE')
    result, report = patch(hp.read_text(encoding='utf-8'), gd.read_text(encoding='utf-8'))
    o.write_text(result, encoding='utf-8')
    Path(a.report).write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({'status': 'REVIEW_ONLY', **report}, indent=2))


if __name__ == '__main__':
    main()
