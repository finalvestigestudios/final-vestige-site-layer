"""Synthetic negative-control tests; DO NOT infer authentic full-site validation."""
import importlib.util
import json
import unittest
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / 'tools' / 'r248_family_card_field_crosswalk_hold.py'
spec = importlib.util.spec_from_file_location('r248', PATH)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


def fixture():
    lines = ', '.join('row("%s", c.%s)' % (label, key)
                      if key != 'meet2' else 'minimal ? null : row("If not, meet at", c.meet2)'
                      for key, label, _ in g.FIELDS[:6])
    tail = ', '.join('row("%s", c.%s)' % (label, key) for key, label, _ in g.FIELDS[6:])
    js = ('function rcClean(f) {return f;}\nfunction rcModel(fields, minimal) {\n'
          'var front = keep([' + lines + ']);\n'
          'var back = minimal\n ? keep([row("Reviewed", c.reviewed), { k: "Details", v: "'
          + g.EXTRA_MINIMAL + '" }])\n : keep([' + tail + ']);\n}\n')
    return {
        g.A: b'Our card keeps what you type on your own device.',
        g.T: ('<p>' + g.HTML_MINIMAL[0] + '</p><span>' + g.HTML_MINIMAL[1] + '</span>'
              + '<noscript>' + g.HTML_NOJS + '</noscript>'
              + '<p>what you type stays on this page. It is not sent or saved.</p>').encode(),
        g.M: json.dumps({'n':104, 'description':'Nothing is stored.',
                          'status':{'publish':'draft'},'safety_review':{'state':'pending'}}).encode(),
        g.J: js.encode(),
        g.C: b'function paCleanText(value,max) {return value;}',
    }


def pins(x):
    return {p:g.git_blob(v) for p,v in x.items()}


class ReviewOnlyMatrix(unittest.TestCase):
    def test_known_disclosure_hold(self):
        x=fixture(); doc=g.inspect(x,pins(x))
        self.assertEqual(doc['state'],g.HOLD)
        self.assertEqual((doc['full_field_count'],doc['minimal_field_count'],doc['minimal_excluded_field_count']), (13,6,7))
        self.assertEqual(len(doc['field_matrix']),13)
        self.assertEqual([z['field'] for z in doc['field_matrix'] if z['in_minimal']],
                         ['hhName','hhPhone','outName','outPhone','meet1','reviewed'])
        for flag in ('reader_disclosure_approved','privacy_certified','claims_adjudicated','medical_safety_verified',
                     'source_review_approved','independent_qd_pass','merchant_approved','release_authorized'):
            self.assertIs(doc[flag],False)

    def test_deterministic_order(self):
        x=fixture(); self.assertEqual(g.inspect(x,pins(x)), g.inspect(dict(reversed(list(x.items()))),pins(x)))

    def test_absent_or_extra_source(self):
        x=fixture(); y=x.copy(); y.pop(g.C)
        with self.assertRaisesRegex(ValueError,'roster'):g.inspect(y,pins(x))
        z=x.copy(); z['intruder']=b'bad'
        with self.assertRaisesRegex(ValueError,'roster'):g.inspect(z,pins(x))

    def test_duplicate_metadata(self):
        x=fixture(); x[g.M]=b'{"n":104,"n":104}'
        with self.assertRaisesRegex(ValueError,'duplicate'):g.inspect(x,pins(x))

    def test_nonfinite_metadata(self):
        x=fixture(); x[g.M]=b'{"n": NaN}'
        with self.assertRaisesRegex(ValueError,'invalid constant'):g.inspect(x,pins(x))

    def test_release_state_promotion_rejected(self):
        for change in ('publish','state'):
            x=fixture(); o=json.loads(x[g.M])
            if change=='publish':o['status']['publish']='publish'
            else:o['safety_review']['state']='approved'
            x[g.M]=json.dumps(o).encode()
            with self.subTest(change=change), self.assertRaisesRegex(ValueError,'safety/publish'):g.inspect(x,pins(x))


def variant(path,old,new,error):
    def check(self):
        x=fixture()
        if old not in x[path]:raise AssertionError('original witness absent')
        x[path]=x[path].replace(old,new,1)
        with self.assertRaisesRegex(ValueError,error):g.inspect(x,pins(x))
    return check


for idx,(field,label,_) in enumerate(g.FIELDS):
    setattr(ReviewOnlyMatrix,f'test_field_name_mutation_{idx:02d}',
            variant(g.J,('c.'+field).encode(),('c.CHANGED_'+field).encode(),'crosswalk'))
    setattr(ReviewOnlyMatrix,f'test_label_mutation_{idx:02d}',
            variant(g.J,('row("'+label+'"').encode(),('row("INACCURATE '+label+'"').encode(),'crosswalk'))


for idx,path in enumerate(g.SOURCES):
    def mismatched(self,path=path):
        x=fixture(); original=pins(x);x[path]+=b' --unexpected'
        with self.assertRaisesRegex(ValueError,'identity changed'):g.inspect(x,original)
    setattr(ReviewOnlyMatrix,f'test_git_source_identity_{idx:02d}',mismatched)


for idx,claim in enumerate(g.HTML_MINIMAL):
    setattr(ReviewOnlyMatrix,f'test_minimal_claim_changed_{idx:02d}',
            variant(g.T,claim.encode(),b'REDACTED','public-facing'))


bad_branches = [
    ('minimal ? null : row("If not, meet at", c.meet2)', 'row("If not, meet at", c.meet2)'),
    ('var back = minimal', 'var back = false'),
    (g.EXTRA_MINIMAL, 'Details are NOT in your plan.'),
]
for idx,(old,new) in enumerate(bad_branches):
    setattr(ReviewOnlyMatrix,f'test_minimal_switch_changed_{idx:02d}',
            variant(g.J,old.encode(),new.encode(),'minimal branch'))


for idx,(path,old,new,error) in enumerate([
    (g.T,g.HTML_NOJS,'The form is now hidden','minimal/noJS'),
    (g.T,'what you type stays on this page. It is not sent or saved.','It might be stored.','privacy assurance'),
    (g.A,'keeps what you type on your own device','uploads everything','privacy assurance'),
    (g.M,'Nothing is stored.','Data might be retained.','privacy assurance'),
    (g.C,'function paCleanText','function untrusted', 'sanitizer'),
    (g.J,'function rcClean','function untrusted', 'sanitizer'),
    (g.J,'function rcModel(fields, minimal)', 'function rcModel(fields)', 'rcModel'),
]):
    setattr(ReviewOnlyMatrix,f'test_guard_witness_{idx:02d}',
            variant(path,old.encode(),new.encode(),error))


if __name__=='__main__':unittest.main()
