"""R217 bounded, deterministic, synthetic transport security regression tests."""
import hashlib
import importlib.util
from pathlib import Path
import unittest

P = Path(__file__).resolve().parents[1] / 'tools' / 'r217_transport_semantics_guard.py'
spec = importlib.util.spec_from_file_location('r217_transport', P)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


def html(n):
    return (f'<!-- wp:html --><div class="pa"><header><ul class="pa-chips"><li>Draft: not public</li>'
            f'<li>Safety review pending</li></ul></header><div class="pa-shell">'
            f'<div class="pa-body"><p>Plan {n} uses <a href="#src-1">[1]</a> and '
            f'<a href="#src-2">[2]</a>.</p></div></div><section class="pa-sources">'
            f'<ol><li id="src-1"><a href="https://www.ready.gov/plan">Official</a></li>'
            f'<li id="src-2"><a href="https://www.cdc.gov/">CDC</a></li></ol></section>'
            f'<section class="pa-review">Pending. Human safety review required.</section>'
            f'</div><!-- /wp:html -->').encode()


def healthy():
    docs = {n: {c: html(n) for c in ('wp', 'preview')} for n in (7, 20)}
    prev = {'schema': g.PARENT_SCHEMA, 'state': g.HOLD, 'errors': [],
            'source_claim_review': 'REQUIRED', 'independent_qd_pass': False,
            'publication_authorized': False, 'medical_safety_verified': False,
            'transports': [{'article': n, 'channel': c, 'sha256': hashlib.sha256(docs[n][c]).hexdigest(),
                            'exposure_gate': g.HOLD} for n in (7, 20) for c in ('wp', 'preview')]}
    assert g.evaluate(prev, docs)['state'] == g.HOLD
    return prev, docs


def changed(change, number=7, channel='wp'):
    prev, docs = healthy()
    docs[number][channel] = change(docs[number][channel].decode()).encode()
    entry = next(x for x in prev['transports'] if x['article'] == number and x['channel'] == channel)
    entry['sha256'] = hashlib.sha256(docs[number][channel]).hexdigest()
    return g.evaluate(prev, docs)


class BaselineTests(unittest.TestCase):
    def test_legitimate_draft_is_hold(self):
        p, d = healthy(); out = g.evaluate(p, d)
        self.assertEqual(out['state'], g.HOLD)
        self.assertEqual(len(out['transports']), 4)
        self.assertFalse(out['publication_authorized'])
        self.assertFalse(out['independent_qd_pass'])
        self.assertFalse(out['medical_safety_verified'])
    def test_healthy_is_deterministic(self):
        p, d = healthy(); self.assertEqual(g.evaluate(p, d), g.evaluate(p, d))
    def test_rejects_upstream_qd_pass(self):
        p, d = healthy(); p['state'] = 'QD_PASS'; self.assertEqual(g.evaluate(p, d)['state'], g.INVALID)
    def test_rejects_forged_approval_flags(self):
        for k in ('independent_qd_pass', 'publication_authorized', 'medical_safety_verified'):
            with self.subTest(k=k):
                p, d = healthy(); p[k] = True
                self.assertEqual(g.evaluate(p, d)['state'], g.INVALID)
    def test_rejects_missing_claim_review(self):
        p, d = healthy(); p['source_claim_review'] = 'COMPLETE'
        self.assertEqual(g.evaluate(p, d)['state'], g.INVALID)
    def test_digest_drift(self):
        p, d = healthy(); d[7]['wp'] = b'changed'
        self.assertIn('receipt drift', ' '.join(g.evaluate(p, d)['errors']))
    def test_duplicate_parent_receipt(self):
        p, d = healthy(); p['transports'][1] = p['transports'][0]
        self.assertEqual(g.evaluate(p, d)['state'], g.INVALID)
    def test_missing_transport(self):
        p, d = healthy(); del d[20]['preview']
        self.assertEqual(g.evaluate(p, d)['state'], g.INVALID)
    def test_invalid_utf8_rejected(self):
        p, d = healthy(); d[7]['wp'] = b'\xff'; p['transports'][0]['sha256'] = hashlib.sha256(b'\xff').hexdigest()
        self.assertEqual(g.evaluate(p, d)['state'], g.INVALID)
    def test_missing_id_rejected(self):
        o = changed(lambda s: s.replace('id="src-1"', 'id="lost"'))
        self.assertIn('unresolved document fragment', ' '.join(o['errors']))
    def test_unrelated_unique_id_is_allowed(self):
        o = changed(lambda s: s.replace('<div class="pa">', '<div class="pa" id="unique">'))
        self.assertEqual(o['state'], g.HOLD, o)
    def test_rejects_document_wide_duplicate_id(self):
        o = changed(lambda s: s.replace('<header>', '<span id="src-1"></span><header>'))
        self.assertEqual(o['state'], g.INVALID)
        self.assertIn('duplicate or empty document-wide id', ' '.join(o['errors']))
    def test_rejects_preempting_source_id_in_outside_element(self):
        o = changed(lambda s: s.replace('id="src-1"', 'id="src-1"', 1).replace('<li id="src-1">', '<li id="src-1">')
                               .replace('<div class="pa">', '<div class="pa"><span id="src-1"></span>'))
        self.assertEqual(o['state'], g.INVALID)
    def test_false_assurance_split_by_inline_span(self):
        o = changed(lambda s: s.replace('Safety review pending', 'Approved <span>for</span> publication'))
        self.assertEqual(o['state'], g.INVALID)
    def test_false_assurance_with_linebreak(self):
        o = changed(lambda s: s.replace('Safety review pending', 'Approved<br>for publication'))
        self.assertEqual(o['state'], g.INVALID)


ATTACKS = [
    ('duplicate_href_http_first', lambda s: s.replace('href="https://www.ready.gov/plan"', 'href="http://attacker.invalid" href="https://www.ready.gov/plan"')),
    ('duplicate_href_javascript_first', lambda s: s.replace('href="https://www.ready.gov/plan"', 'href="javascript:alert(1)" href="https://www.ready.gov/plan"')),
    ('duplicate_href_casefold', lambda s: s.replace('href="https://www.ready.gov/plan"', 'HREF="http://bad.invalid" href="https://www.ready.gov/plan"')),
    ('duplicate_style_hide', lambda s: s.replace('class="pa-body"', 'class="pa-body" style="display:none" style=""')),
    ('duplicate_aria_hide', lambda s: s.replace('class="pa-sources"', 'class="pa-sources" aria-hidden="true" aria-hidden="false"')),
    ('duplicate_id', lambda s: s.replace('id="src-1"', 'id="bad" id="src-1"')),
    ('duplicate_class', lambda s: s.replace('class="pa-review"', 'class="pa-review" class="safe"')),
    ('duplicate_target', lambda s: s.replace('href="#src-1"', 'target="_top" target="_blank" href="#src-1"')),
    ('duplicate_rel', lambda s: s.replace('href="https://www.ready.gov/plan"', 'rel="noopener" rel="bad" href="https://www.ready.gov/plan"')),
    ('orphan_citation_id', lambda s: s.replace('href="#src-1"', 'href="#nonexistent"')),
    ('malformed_fragment', lambda s: s.replace('href="#src-1"', 'href="#"')),
    ('hijack_by_non_source', lambda s: s.replace('<li id="src-1">', '<li id="different">').replace('<header>', '<span id="src-1"></span><header>')),
    ('hijack_by_non_li', lambda s: s.replace('<li id="src-1">', '<div id="src-1">').replace('</a></li><li id="src-2">', '</a></div><li id="src-2">')),
    ('duplicate_unrelated_id', lambda s: s.replace('<header>', '<span id="foobar"></span><span id="foobar"></span><header>')),
    ('empty_id', lambda s: s.replace('<header>', '<span id=""></span><header>')),
    ('hidden_approved_spaces', lambda s: s.replace('Safety review pending', 'Approved  for publication')),
    ('hidden_approved_tab', lambda s: s.replace('Safety review pending', 'Approved\tfor publication')),
    ('hidden_approved_newline', lambda s: s.replace('Safety review pending', 'Approved\nfor publication')),
    ('hidden_ready_spaces', lambda s: s.replace('Safety review pending', 'Ready   to publish')),
    ('hidden_qd_double_spaces', lambda s: s.replace('Safety review pending', 'QD     PASS')),
    ('hidden_medical_spaces', lambda s: s.replace('Safety review pending', 'Medical    safety verified')),
    ('hidden_publication_authorized', lambda s: s.replace('Human safety review required', 'Publication\n authorized')),
    ('hidden_approved_review', lambda s: s.replace('Human safety review required', 'Approved    for publication')),
]


class MutationTests(unittest.TestCase):
    pass


def make_test(label, transform, n, c):
    def test(self):
        output = changed(transform, number=n, channel=c)
        self.assertEqual(output['state'], g.INVALID, f'{label} {n}/{c}: {output}')
    return test


for i, (label, transform) in enumerate(ATTACKS):
    for n in (7, 20):
        for c in ('wp', 'preview'):
            setattr(MutationTests, f'test_{i:02}_{label}_{n}_{c}', make_test(label, transform, n, c))


if __name__ == '__main__':
    unittest.main()
