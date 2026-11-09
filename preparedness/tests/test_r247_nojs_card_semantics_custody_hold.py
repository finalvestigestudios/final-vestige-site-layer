"""Synthetic negative-control cases for R247 (no native build claim)."""
import importlib.util
import json
import unittest
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / 'tools' / 'r247_nojs_card_semantics_custody_hold.py'
spec = importlib.util.spec_from_file_location('r247', PATH)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


def fixture():
    labels = ''.join('<p><b>' + x + ':</b> ______________</p>' for x in g.LABELS)
    return {
        g.A: b'A free card keeps what you type on your own device.',
        g.T: ('<noscript><div>' + g.CLAIM + '</div></noscript>\n'
              '<form id="rc"><input id="rc-hhName"></form>\n'
              '<noscript><div class="pa-printsheet"><div class="pa-foldcard">'
              + labels + '</div></div></noscript>\n'
              '<noscript><style>#rc, #rc-warn { display: none; }</style></noscript>').encode(),
        g.M: json.dumps({'n': 104, 'status': {'publish': 'draft'}, 'safety_review': {'state': 'pending'}}).encode(),
        g.J: (b'var front = keep([row("Household", c.hhName), row("Phone", c.hhPhone), '
              b'row("Out-of-area contact", c.outName), minimal ? null : row("If not, meet at", c.meet2)]);'),
    }


def pins(x):
    return {p: g.git_blob(b) for p, b in x.items()}


class NoJSReviewHold(unittest.TestCase):
    def test_original_synthetic_conflict_retained_as_hold(self):
        x = fixture()
        a = g.inspect(x, pins(x))
        self.assertEqual(a['state'], g.HOLD)
        self.assertEqual(a['blank_fallback_field_count'], 13)
        self.assertTrue(a['nojs_copy_conflicts_with_hidden_form'])
        for k in ('privacy_certified', 'claims_adjudicated', 'nojs_browser_print_verified',
                  'source_review_approved', 'independent_qd_pass', 'release_authorized',
                  'merchant_approved'):
            self.assertIs(a[k], False)

    def test_deterministic_reordered_dictionary(self):
        x = fixture()
        self.assertEqual(g.inspect(x, pins(x)), g.inspect(dict(reversed(list(x.items()))), pins(x)))

    def test_mismatched_original_pin_rejected(self):
        x = fixture()
        for path in g.SOURCES:
            with self.subTest(path=path):
                bad = x.copy(); bad[path] += b'!'
                with self.assertRaisesRegex(ValueError, 'identity changed'):
                    g.inspect(bad, pins(x))

    def test_strict_roster(self):
        x = fixture(); x['outside'] = b'UNKNOWN'
        with self.assertRaisesRegex(ValueError, 'four-source roster'):
            g.inspect(x, pins(x))

    def test_draft_and_pending_cannot_be_promoted(self):
        for field, val in [('publish', 'publish'), ('state', 'approved')]:
            with self.subTest(field=field):
                x = fixture(); m=json.loads(x[g.M]); m['status' if field=='publish' else 'safety_review'][field]=val
                x[g.M] = json.dumps(m).encode()
                with self.assertRaisesRegex(ValueError,'release state'):
                    g.inspect(x, pins(x))

    def test_invalid_file_bytes(self):
        x=fixture(); x[g.T] += b'\0'
        with self.assertRaisesRegex(ValueError,'source bytes'):
            g.inspect(x,pins(x))

    def test_text_disguised_in_untrusted_article(self):
        x=fixture(); x[g.A]=b'no privacy promise'
        with self.assertRaisesRegex(ValueError,'linked article privacy'):
            g.inspect(x,pins(x))


def mutated_test(path, old, new, expected):
    def test(self):
        x=fixture()
        if old not in x[path]:
            self.fail('mutation has no original witness')
        x[path]=x[path].replace(old,new,1)
        with self.assertRaisesRegex(ValueError,expected):
            g.inspect(x,pins(x))
    return test


for idx, label in enumerate(g.LABELS):
    setattr(NoJSReviewHold, f'test_missing_or_changed_fallback_label_{idx:02d}',
            mutated_test(g.T, ('<b>'+label+':</b>').encode(),
                         ('<b>'+label+' REMOVED:</b>').encode(), 'label inventory'))

css_bad = [
    '#rc { display: none; }', '#rc-warn { display: none; }',
    '#rc, #rc-warn { display: block; }', '#rc, #rc-warn { opacity: 0; }',
    '#rc, #rc-warn { display: none !important; }',
    '#rc, #rc-warn { display: table; }', '#rc, #rc-warn { visibility: hidden; }',
    '#rcc, #rc-warn { display: none; }', '#rc, #rc-other { display: none; }',
    '#rc, #rc-warn { display: none; color: red; }',
    '#rc #rc-warn { display: none; }', '#rc, #rc-warn { display: contents; }',
]
for idx, replacement in enumerate(css_bad):
    setattr(NoJSReviewHold, f'test_changed_css_witness_{idx:02d}',
            mutated_test(g.T,b'#rc, #rc-warn { display: none; }',replacement.encode(),
                         'copy/fallback/CSS'))

copy_bad = [
    'The form is unavailable.', 'Use the blank card.', 'The form is hidden.',
    'Fill out the paper version.', 'Nothing to print.', 'The form works.',
    'The form below might print.', 'No JavaScript is available.',
    'All data is saved.', 'Information is uploaded.',
    'The form below saves entries.', 'The form below may work.',
]
for idx, replacement in enumerate(copy_bad):
    setattr(NoJSReviewHold, f'test_changed_copy_witness_{idx:02d}',
            mutated_test(g.T,g.CLAIM.encode(),replacement.encode(), 'copy/fallback/CSS'))

structure_bad = [
    (g.T,b'<form id="rc">',b'<form id="new-form">','form identity'),
    (g.T,b'<form id="rc">',b'<form>','form identity'),
    (g.T,b'<form id="rc">',b'<div id="rc">','form identity'),
    (g.T,b'<noscript><style>',b'<style>','closing tag'),
    (g.T,b'</style></noscript>',b'</style>','block count'),
    (g.T,b'class="pa-foldcard"',b'class="pa-nocard"','copy/fallback/CSS'),
    (g.T,b'<div class="pa-foldcard">',b'<div class="pa-foldcard"><input>','interactive content'),
    (g.T,b'<div class="pa-foldcard">',b'<div class="pa-foldcard"><script>','block count'),
    (g.J,b'row("Household", c.hhName)',b'row("Hidden", c.hhName)','identifier witness'),
    (g.J,b'row("Phone", c.hhPhone)',b'row("Phone", c.none)','identifier witness'),
    (g.J,b'minimal ? null',b'false ? null','identifier witness'),
    (g.J,b'var front = keep([',b'var front = elsewhere([','model structure'),
]
for idx, (path, old, new, err) in enumerate(structure_bad):
    setattr(NoJSReviewHold, f'test_structural_drift_{idx:02d}',mutated_test(path,old,new,err))

if __name__ == '__main__':
    unittest.main()
