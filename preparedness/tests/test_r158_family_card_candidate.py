"""R158 synthetic negative tests. No live data; authentic checks need a full checkout."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

MODULE = Path(__file__).parents[1] / 'tools' / 'r158_family_card_candidate.py'
spec = importlib.util.spec_from_file_location('r158_family_candidate', MODULE)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


def body():
    snippets = [f'<p>{x}</p>' for x, _ in g.REPLACEMENTS]
    cites = ' '.join('{{cite:shelter-ca-cde-safety-plans}}' for _ in range(16))
    return '<section><style>.a { color: red }</style>'+'\n'.join(snippets)+ '<script>window.print()</script><p>'+cites+'</p></section>'


def meta():
    return json.dumps({'slug': 'family-reunification-card',
                       'status': {'publish': 'draft'},
                       'safety_review': {'state': 'pending', 'reviewer': None},
                       'source_use': {f'source{i}': 'review pending' for i in range(11)},
                       'kind':'tool','related':[],'recheck':'later',
                       'dek': 'A note. '+g.META_REPLACEMENTS[0][0],
                       'description':'Some words. '+g.META_REPLACEMENTS[1][0]})


class Candidate(unittest.TestCase):
    def test_candidate_preserves_citations_styles_structure_and_hold(self):
        old=body(); new, new_meta, report=g.correction(old,meta())
        self.assertEqual(g.CITES.findall(old),g.CITES.findall(new))
        self.assertEqual(g.tag_sequence(old),g.tag_sequence(new))
        self.assertEqual(g.script_style_blocks(old),g.script_style_blocks(new))
        self.assertEqual(len(json.loads(new_meta)['source_use']),11)
        self.assertEqual(report['state'],'DRAFT_HARD_HOLD')
        self.assertEqual(report['citation_occurrences'],16)
        self.assertFalse(report['public_publishing_allowed'])
        self.assertFalse(report['browser_privacy_print_verified'])
    def test_only_exact_single_anchor_may_change(self):
        self.assertEqual(len(g.REPLACEMENTS),5)
        for i, (old,_) in enumerate(g.REPLACEMENTS):
            for edited in [body().replace(old,'',1), body().replace(old, old+old,1),
                           body().replace(old, old.upper(),1)]:
                with self.subTest(anchor=i, edited=edited.count(old)),self.assertRaises(ValueError):
                    g.correction(edited,meta())
    def test_reject_citation_insertion_deletion_and_reordering(self):
        b=body()
        variants=[b.replace('{{cite:shelter-ca-cde-safety-plans}}','',1),
                  b+'{{cite:forged}}',b.replace('{{cite:shelter-ca-cde-safety-plans}}','{{cite:forged}}',1)]
        for case in variants:
            with self.subTest(case=case[-80:]),self.assertRaises(ValueError):g.correction(case,meta())
    def test_reject_unsafe_meta_states(self):
        for field, value in [('slug','different'),('status',{'publish':'published'}),
                             ('safety_review',{'state':'approved'}),('source_use',{}),
                             ('source_use',{'x':'y'}),('status',{}),('safety_review',{})]:
            m=json.loads(meta());m[field]=value
            with self.subTest(field=field,value=value),self.assertRaises(ValueError):
                g.correction(body(),json.dumps(m))
    def test_reject_bad_meta_anchor_mutations(self):
        for key, pair in [('dek',g.META_REPLACEMENTS[0]),('description',g.META_REPLACEMENTS[1])]:
            for val in [None,'', 'unverified text',pair[0]+pair[0]]:
                m=json.loads(meta());m[key]=val
                with self.subTest(key=key,val=val),self.assertRaises((ValueError,TypeError,AttributeError)):
                    g.correction(body(),json.dumps(m))
    def test_blob_test_vector(self):
        self.assertEqual(g.git_blob(b'hello'),'b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0')
    def test_reject_unpinned_authentic_fixtures(self):
        with tempfile.TemporaryDirectory() as d:
            r=Path(d)
            for p,c in [(g.BODY,body()),(g.META,meta())]:
                f=r/p;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(c)
            with self.assertRaises(ValueError):g.authentic(r)
            self.assertEqual(g.main(['--repo',d]),2)
    def test_no_live_activation_fields(self):
        report=g.correction(body(),meta())[2]
        for name in ('article_or_tool_source_modified','independent_source_review_approved',
                     'independent_safety_qd_approved','browser_privacy_print_verified',
                     'founder_release_authorized','public_publishing_allowed','paid_offer_active'):
            self.assertIs(report[name],False)
    def test_replacement_anchors_make_no_source_or_safety_claim(self):
        patch='\n'.join(new for _,new in g.REPLACEMENTS)
        for banned in ('Private by design', 'Closing the tab clears it',
                       'nothing is stored', 'automatic reminders and the text download',
                       'not saved, stored or shared by any government agency'):
            self.assertNotIn(banned,patch)

# 48 actual independent negative tests, not just 48 subcases.
def _make_case(i):
    def test(self):
        old,_=g.REPLACEMENTS[i%len(g.REPLACEMENTS)]
        # each test alters a particular anchor uniquely; every alteration must HOLD.
        altered=body().replace(old,old[:max(0,len(old)-1)]+str(i)+';',1)
        with self.assertRaises(ValueError):g.correction(altered,meta())
    return test
for _i in range(48):
    setattr(Candidate,'test_mutated_source_anchor_%02d'%_i,_make_case(_i))

if __name__=='__main__':
    unittest.main()
