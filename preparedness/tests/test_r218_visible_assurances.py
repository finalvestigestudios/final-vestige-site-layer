"""R218 authentic R217-source patch: fail-closed rendered notice text tests.

Synthetic only. No safety, clinical, source or publication PASS is possible.
"""
import hashlib
import importlib.util
from pathlib import Path
import unittest

P = Path(__file__).resolve().parents[1] / 'tools' / 'r217_transport_semantics_guard.py'
spec = importlib.util.spec_from_file_location('r217_guard_r218', P)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


def sample(article):
    return (f'<!-- wp:html --><div class="pa"><header><ul class="pa-chips">'
            f'<li>Draft: not public</li><li>Safety review pending</li></ul></header>'
            f'<div class="pa-body"><p>Claim for {article} is unreviewed. '
            f'<a href="#src-1">[1]</a></p></div>'
            f'<section class="pa-sources"><ol><li id="src-1">'
            f'<a href="https://www.ready.gov/plan">Source</a></li></ol></section>'
            f'<section class="pa-review"><p>Pending. Independent safety review required.</p>'
            f'</section></div><!-- /wp:html -->').encode('utf-8')


def baseline():
    docs = {n: {c: sample(n) for c in ('wp', 'preview')} for n in (7, 20)}
    prev = {'schema': g.PARENT_SCHEMA, 'state': g.HOLD, 'errors': [],
            'source_claim_review': 'REQUIRED', 'independent_qd_pass': False,
            'publication_authorized': False, 'medical_safety_verified': False,
            'transports': [{'article': n, 'channel': c, 'sha256': hashlib.sha256(docs[n][c]).hexdigest(),
                            'exposure_gate': g.HOLD} for n in (7, 20) for c in ('wp', 'preview')]}
    assert g.evaluate(prev, docs)['state'] == g.HOLD
    return prev, docs


def mutation(context, transformed, article=7, channel='wp'):
    previous, documents = baseline()
    old = documents[article][channel].decode('utf-8')
    if context == 'chips':
        old_token = 'Safety review pending'
    elif context == 'review':
        old_token = 'Independent safety review required'
    else:
        raise ValueError(context)
    assert old.count(old_token) == 1
    changed = old.replace(old_token, transformed)
    documents[article][channel] = changed.encode('utf-8')
    for row in previous['transports']:
        if (row['article'], row['channel']) == (article, channel):
            row['sha256'] = hashlib.sha256(documents[article][channel]).hexdigest()
    return g.evaluate(previous, documents)


ATTACKS = [
    ('inline_span', 'App<span>roved</span> for publication'),
    ('inline_strong', 'Ready <strong>to</strong> publish'),
    ('inline_inside_word', 'App<strong>rov</strong>ed for publication'),
    ('split_each_word', 'Pub<span>lic</span>ation <b>auth</b>orized'),
    ('comment_inside_word', 'Appr<!--editor-->oved for publication'),
    ('comment_between_words', 'Medical<!-- note --> safety verified'),
    ('nested_inline', 'Q<strong>D <em>PA</em>SS</strong>'),
    ('linebreak', 'Ready<br>to publish'),
    ('linebreak_selfclosing', 'QD<br/>PASS'),
    ('newline', 'Approved\nfor publication'),
    ('tab', 'Publication\t authorized'),
    ('two_spaces', 'Medical  safety verified'),
    ('nbsp', 'Approved&nbsp;for publication'),
    ('numeric_nbsp', 'Approved&#160;for publication'),
    ('soft_hyphen', 'App&shy;roved for publication'),
    ('zero_width', 'App\u200broved for publication'),
    ('zero_width_joiner', 'Medical\u200d safety verified'),
    ('word_joiner', 'Publication\u2060 authorized'),
    ('fullwidth', 'Ａｐｐｒｏｖｅｄ for publication'),
    ('mixed_entities', 'App&#114;oved&#32;for publication'),
    ('heading_bold', '<em>Publication</em> <strong>authorized</strong>'),
    ('inline_sup', 'QD <sup>PA</sup>SS'),
]


class R218Baseline(unittest.TestCase):
    def test_held_is_only_positive(self):
        prev, docs = baseline()
        result = g.evaluate(prev, docs)
        self.assertEqual(result['state'], g.HOLD)
        self.assertFalse(result['independent_qd_pass'])
        self.assertFalse(result['publication_authorized'])
        self.assertFalse(result['medical_safety_verified'])
        self.assertEqual(len(result['transports']), 4)

    def test_repeat_determinism(self):
        a, b = baseline()
        self.assertEqual(g.evaluate(a, b), g.evaluate(a, b))

    def test_original_r217_checks_preserved(self):
        for s in ('<span id="src-1"></span>', '<b id=""/>'):
            with self.subTest(s=s):
                old, docs = baseline()
                text = docs[7]['wp'].decode().replace('<header>', s + '<header>')
                docs[7]['wp'] = text.encode()
                old['transports'][0]['sha256'] = hashlib.sha256(docs[7]['wp']).hexdigest()
                self.assertEqual(g.evaluate(old, docs)['state'], g.INVALID)

    def test_safe_cross_inline_nonsensical_words_remain_hold(self):
        for candidate in ('Pract<span>ice</span> your contacts',
                          'Status: <em>Draft</em> and review pending',
                          'A<strong>pp</strong>licant should review sources'):
            with self.subTest(text=candidate):
                self.assertEqual(mutation('review', candidate)['state'], g.HOLD)

    def test_block_boundary_does_not_combine_into_word(self):
        for candidate in ('App</p><p>roved for publication',
                          'Pub<div>lication authorized</div>'):
            with self.subTest(text=candidate):
                # Full structural parse may reject the first fragment if nesting is wrong,
                # but it must never result in a false publication PASS.
                self.assertIn(mutation('review', candidate)['state'], (g.HOLD, g.INVALID))

    def test_source_receipts_unchanged(self):
        original, docs = baseline()
        original['transports'][1]['sha256'] = '0' * 64
        self.assertEqual(g.evaluate(original, docs)['state'], g.INVALID)


class R218Mutations(unittest.TestCase):
    pass


def create_test(context, name, payload, article, channel):
    def test(self):
        output = mutation(context, payload, article=article, channel=channel)
        self.assertEqual(output['state'], g.INVALID,
                         f'{context}/{name}/{article}/{channel}: {output}')
        self.assertTrue(output['errors'])
    return test


for idx, (label, value) in enumerate(ATTACKS):
    for scope in ('chips', 'review'):
        for a in (7, 20):
            for c in ('wp', 'preview'):
                setattr(R218Mutations, f'test_{idx:02}_{label}_{scope}_{a}_{c}',
                        create_test(scope, label, value, a, c))


if __name__ == '__main__':
    unittest.main()
