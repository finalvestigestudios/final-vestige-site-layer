import importlib.util
import json
import pathlib
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('r365_claim', ROOT.parent/'tools'/'r365_claim_neighborhood_custody.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

S='{{cite:agency-plan}}'
T='{{cite:agency-other}}'
BASE='''<h2 id="stage">Meet your household</h2><p>Discuss your household meeting point and share emergency contact information with everyone.{{cite:agency-plan}}</p><p>Store the contact information in a safe place for future reference.{{cite:agency-other}}</p>'''

def meta(slug='household-emergency-plan', **changes):
    x={'n':1,'slug':slug,'status':{'publish':'draft','editorial':'drafted'},
       'safety_review':{'state':'pending'}, 'source_use':{'agency-plan':'Household contact planning','agency-other':'Safe documentation'}}
    x.update(changes)
    return x

class ClaimTests(unittest.TestCase):
    def check(self,body=BASE,new=BASE,oldmeta=None,newmeta=None):
        return m.compare(oldmeta or meta(),newmeta or meta(),body,new)
    def test_01_identical(self):
        e,r,d=self.check();self.assertEqual(e,[]);self.assertEqual(r,[]);self.assertEqual(len(d['claim_matches']),2)
    def test_02_reordered_paragraphs_preserve_bindings(self):
        v='<p>Store the contact information in a safe place for future reference.{{cite:agency-other}}</p><p>Discuss your household meeting point and share emergency contact information with everyone.{{cite:agency-plan}}</p>'
        e,r,d=self.check(BASE,v);self.assertFalse(e);self.assertTrue(all(x['outcome']=='EXACT' for x in d['claim_matches']))
    def test_03_unrelated_claim_switch_holds(self):
        new=BASE.replace('Discuss your household meeting point and share emergency contact information with everyone.','Apple pies with nutmeg and cinnamon taste wonderful in the autumn.')
        e,r,d=self.check(new=new);self.assertTrue(any('REASSIGNED_UNRELATED' in x for x in e))
    def test_04_related_reword_requires_review(self):
        new=BASE.replace('Discuss your household meeting point and share emergency contact information with everyone.','Talk to household members about the family contact and safe meeting location.')
        e,r,d=self.check(new=new);self.assertIn('CITATION_CLAIM_CHANGED:agency-plan',r)
    def test_05_citation_removed(self):
        e,r,d=self.check(new=BASE.replace(S,''));self.assertIn('CITATION_COUNT_LOST:agency-plan',e)
    def test_06_count_same_but_different_claim(self):
        new=BASE.replace(S,'').replace('future reference.', 'future reference.'+S)
        e,r,d=self.check(new=new);self.assertTrue(any('CITATION_REASSIGNED' in s for s in e))
    def test_07_duplicate_in_one_claim(self):
        e,r,d=self.check(new=BASE.replace(S,S+S));self.assertIn('NEW_CITATION_OCCURRENCE_REVIEW:agency-plan',r)
    def test_08_new_source_citation_requires_declaration(self):
        e,r,d=self.check(new=BASE+ '<p>Other requirement.{{cite:not-registered}}</p>');self.assertIn('UNDECLARED_CITATION:not-registered',e)
    def test_09_old_undeclared_citation(self):
        e,r,d=self.check(oldmeta=meta(source_use={'agency-other':'something'}));self.assertIn('ORIGINAL_UNDECLARED_CITATION:agency-plan',e)
    def test_10_new_source_use_added_requires_review(self):
        nm=meta(source_use={**meta()['source_use'],'new-sid':'Source description'})
        e,r,d=self.check(newmeta=nm);self.assertIn('NEW_SOURCE_REVIEW:new-sid',r)
    def test_11_source_use_removed_holds(self):
        nm=meta(source_use={'agency-other':'Safe documentation'})
        e,r,d=self.check(newmeta=nm);self.assertIn('SOURCE_BINDING_REMOVED:agency-plan',e)
    def test_12_source_use_scope_changed_review(self):
        nm=meta(source_use={'agency-plan':'new reading scope','agency-other':'Safe documentation'})
        e,r,d=self.check(newmeta=nm);self.assertIn('SOURCE_SCOPE_CHANGED:agency-plan',r)
    def test_13_unchanged_source_provenance(self):
        e,r,d=self.check();self.assertFalse(any('SOURCE_' in x for x in e+r))
    def test_14_safety_modal_not_to_positive(self):
        old='<p>Do not use this container in an emergency.{{cite:agency-plan}}</p>'
        new='<p>Do use this container in an emergency.{{cite:agency-plan}}</p>'
        e,r,d=self.check(old,new);self.assertIn('SAFETY_MODALITY_CHANGED:agency-plan',r)
    def test_15_only_to_any(self):
        old='<p>Only use tested approaches for storage.{{cite:agency-plan}}</p>'
        new='<p>Use tested approaches for storage.{{cite:agency-plan}}</p>'
        e,r,d=self.check(old,new);self.assertIn('SAFETY_MODALITY_CHANGED:agency-plan',r)
    def test_16_must_to_may(self):
        old='<p>You must follow local officials.{{cite:agency-plan}}</p>'
        new='<p>You may follow local officials.{{cite:agency-plan}}</p>'
        e,r,d=self.check(old,new);self.assertIn('SAFETY_MODALITY_CHANGED:agency-plan',r)
    def test_17_section_changed_is_review(self):
        new=BASE.replace('<h2 id="stage">Meet your household</h2>', '<h2 id="other">Another section</h2>')
        e,r,d=self.check(new=new);self.assertIn('CITATION_SECTION_CHANGED:agency-plan',r)
    def test_18_meta_slug_drift(self):
        e,r,d=self.check(newmeta=meta(slug='other'));self.assertIn('SLUG_DRIFT',e)
    def test_19_meta_number_drift(self):
        e,r,d=self.check(newmeta=meta(n=2));self.assertIn('DOCUMENT_IDENTITY_DRIFT',e)
    def test_20_meta_kind_drift(self):
        e,r,d=self.check(newmeta=meta(kind='tool'));self.assertIn('DOCUMENT_IDENTITY_DRIFT',e)
    def test_21_bad_old_publish(self):
        e,r,d=self.check(oldmeta=meta(status={'publish':'published'}));self.assertIn('OLD_NOT_DRAFT',e)
    def test_22_bad_new_publish(self):
        e,r,d=self.check(newmeta=meta(status={'publish':'published'}));self.assertIn('NEW_NOT_DRAFT',e)
    def test_23_bad_safety(self):
        e,r,d=self.check(newmeta=meta(safety_review={'state':'safe'}));self.assertIn('NEW_INVALID_SAFETY',e)
    def test_24_missing_safety(self):
        e,r,d=self.check(oldmeta=meta(safety_review=None));self.assertIn('OLD_INVALID_SAFETY',e)
    def test_25_missing_source_uses(self):
        e,r,d=self.check(newmeta=meta(source_use=None));self.assertIn('NEW_INVALID_SOURCE_USE',e)
    def test_26_empty_scope(self):
        e,r,d=self.check(newmeta=meta(source_use={'agency-plan':'','agency-other':'Safe documentation'}));self.assertIn('NEW_INVALID_SOURCE_USE',e)
    def test_27_bad_meta_type(self):
        e,r,d=m.compare([],meta(),BASE,BASE);self.assertIn('INVALID_META',e)
    def test_28_bad_slug_format(self):
        e,r,d=self.check(oldmeta=meta(slug='../unsafe'));self.assertIn('SLUG_DRIFT',e)
    def test_29_json_duplicate_key(self):
        with self.assertRaises(ValueError):m.load_json('{"a":1,"a":2}')
    def test_30_json_valid(self):self.assertEqual(m.load_json('{"a":1}')['a'],1)
    def test_31_malformed_citation(self):
        e,r,d=self.check(new=BASE.replace(S,'{{cite:!bad}}'));self.assertIn('NEW_MALFORMED_CITATION_TOKEN',e)
    def test_32_in_attribute(self):
        e,r,d=self.check(new=BASE+ '<a data-cite="{{cite:agency-plan}}">Link</a>');self.assertIn('NEW_CITATION_IN_HTML_ATTRIBUTE',e)
    def test_33_in_script(self):
        e,r,d=self.check(new=BASE+'<script>const cite="{{cite:agency-plan}}";</script>');self.assertIn('NEW_HIDDEN_SCRIPT_CITATION',e)
    def test_34_in_style(self):
        e,r,d=self.check(new=BASE+'<style>x{content:"{{cite:agency-plan}}"}</style>');self.assertIn('NEW_HIDDEN_SCRIPT_CITATION',e)
    def test_35_unbalanced_p(self):
        e,r,d=self.check(new=BASE+'<p>no close');self.assertIn('NEW_UNCLOSED_CLAIM_BLOCK',e)
    def test_36_misnested_p(self):
        e,r,d=self.check(new=BASE+'</p>');self.assertIn('NEW_UNBALANCED_CLAIM_BLOCK',e)
    def test_37_html_fallback_cite(self):
        o,errs=m.occurrences('Plain {{cite:agency-plan}}');self.assertFalse(errs);self.assertEqual(o[0]['tag'],'unscoped')
    def test_38_multiple_original_repeats(self):
        old='<p>One family contact point for disasters.{{cite:agency-plan}}</p><p>One family contact point for disasters.{{cite:agency-plan}}</p>'
        new=old; e,r,d=self.check(old,new);self.assertFalse(e);self.assertEqual(len(d['claim_matches']),2)
    def test_39_two_claims_same_id_one_changed(self):
        old='<p>Take practical steps for household contact planning.{{cite:agency-plan}}</p><p>Keep practical documents safe at home.{{cite:agency-plan}}</p>'
        new=old.replace('Keep practical documents safe at home.','Store personal emergency contacts responsibly.')
        e,r,d=self.check(old,new);self.assertEqual(len(d['claim_matches']),2);self.assertIn('CITATION_CLAIM_CHANGED:agency-plan',r)
    def test_40_polariy_is_normalized(self):
        old='<p>Do NOT call except in an emergency.{{cite:agency-plan}}</p>'
        new='<p>Do not call except in an emergency.{{cite:agency-plan}}</p>'
        e,r,d=self.check(old,new);self.assertFalse(r)
    def test_41_svg_text_no_cite(self):
        o,errs=m.occurrences('<svg><text>decorative</text></svg>'+BASE);self.assertFalse(errs);self.assertEqual(len(o),2)
    def test_42_html_entity_decoding(self):
        o,errs=m.occurrences('<p>Give everyone the plan &amp; share contacts.{{cite:agency-plan}}</p>');self.assertFalse(errs);self.assertIn('share',o[0]['claim'])
    def test_43_large_body_rejected(self):
        with self.assertRaises(ValueError):m.occurrences('a'*500001)
    def test_44_body_none_rejected(self):
        e,r,d=m.compare(meta(),meta(),None,BASE);self.assertIn('INVALID_BODY',e)
    def test_45_no_checkout_hard_hold(self):
        out=m.audit('/some/nonexistent');self.assertEqual(out['status'],'INVALID_HARD_HOLD')
    def test_46_unsafe_ref(self):
        with tempfile.TemporaryDirectory() as p:
            (pathlib.Path(p)/'.git').mkdir()
            out=m.audit(p,'../outside');self.assertIn('UNSAFE_REF',out['errors'])
    def test_47_unverified_never_claims_permission(self):
        o=m.report([]);self.assertEqual(o['status'],'REVIEW_REQUIRED_HARD_HOLD');self.assertFalse(o['may_publish'])
    def test_48_error_never_claims_pass(self):
        o=m.report(['BAD']);self.assertEqual(o['status'],'INVALID_HARD_HOLD');self.assertFalse(o['qd_pass'])
    def test_49_net_revenue_false(self):self.assertFalse(m.report([])['net_revenue_verified'])
    def test_50_source_verified_false(self):self.assertFalse(m.report([])['source_verified'])
    def test_51_similarity_empty(self):self.assertEqual(m.common('',''),1)
    def test_52_similarity_unrelated(self):self.assertEqual(m.common('cats','dogs'),0)

class NativeSynthetic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.t=tempfile.TemporaryDirectory();cls.root=pathlib.Path(cls.t.name)
        def cmd(*a):return subprocess.check_output(['git','-C',str(cls.root),*a],stderr=subprocess.DEVNULL).decode().strip()
        cls.cmd=cmd
        cmd('init');cmd('config','user.email','test@example.invalid');cmd('config','user.name','local-test')
        for kind,count in [('articles',35),('tools',6)]:
            for i in range(count):
                slug=f'doc-{kind}-{i:02}'
                path=cls.root/'preparedness'/'content'/kind
                path.mkdir(parents=True,exist_ok=True)
                (path/(slug+'.meta.json')).write_text(json.dumps(meta(slug,n=i)),encoding='utf-8')
                (path/(slug+'.body.html')).write_text(BASE,encoding='utf-8')
        cmd('add','.');cmd('commit','-m','synthetic original')
        cls.original=cmd('rev-parse','HEAD')
        cls.sample=cls.root/'preparedness/content/articles/doc-articles-00.body.html'
        cls.sample.write_text(BASE.replace('Discuss your household meeting point and share emergency contact information with everyone.','Share your family household contact information at the agreed meeting location.'),encoding='utf-8')
        cmd('add','.');cmd('commit','-m','synthetic change')
    @classmethod
    def tearDownClass(cls):cls.t.cleanup()
    def test_53_original_pin_requires_match(self):
        with patch.object(m,'ORIGINAL','0'*40):self.assertEqual(m.audit(self.root)['status'],'INVALID_HARD_HOLD')
    def test_54_reads_all_41_documents(self):
        with patch.object(m,'ORIGINAL',self.original):
            r=m.audit(self.root)
        self.assertEqual(r['evidence'].get('authored_articles'),35)
        self.assertEqual(len(r['dockets']),41)
    def test_55_local_review_doesnt_claim_approval(self):
        with patch.object(m,'ORIGINAL',self.original):r=m.audit(self.root)
        self.assertFalse(r['safety_verified']);self.assertFalse(r['may_merge'])
    def test_56_unchanged_40_docs_remain_review_only(self):
        with patch.object(m,'ORIGINAL',self.original):r=m.audit(self.root)
        self.assertEqual(r['status'],'REVIEW_REQUIRED_HARD_HOLD')
    def test_57_original_claim_hash_in_docket(self):
        with patch.object(m,'ORIGINAL',self.original):r=m.audit(self.root)
        self.assertTrue(r['dockets'][0]['claim_matches'][0]['original_claim_sha256'])
    def test_58_untrusted_ref_rejected(self):
        with patch.object(m,'ORIGINAL',self.original):r=m.audit(self.root,'-bad')
        self.assertIn('UNSAFE_REF',r['errors'])

if __name__=='__main__': unittest.main()
