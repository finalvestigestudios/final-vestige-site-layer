"""R296 strictly synthetic review-only regression suite, no publication acceptance."""
from __future__ import annotations
import contextlib
import copy
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT=Path(__file__).resolve().parents[1]/'tools'/'r296_reunion_claim_provenance_hold.py'
spec=importlib.util.spec_from_file_location('r296_hold',SCRIPT)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

NOTE='''<p class="pa-act-note"><strong>In an emergency,</strong> call 911 for anything life-threatening, and use text messages rather than calls for everything else when networks are busy.{{cite:shelter-ready-tech}} <strong>Private by design:</strong> what you type stays on this page. It is not sent or saved. Closing the tab clears it.</p>'''
NOSCRIPT='''<noscript><div><p>JavaScript is off. A blank card is shown below. The form below still works and prints. Only automatic reminders require JavaScript.</p></div></noscript>'''
BODY='<section><h2>What to do now</h2>'+NOTE+'</section>'+NOSCRIPT
META={'kind':'tool','n':104,'slug':'family-reunification-card','section':'field-tools',
      'status':{'publish':'draft'},'safety_review':{'state':'pending','reviewer':None,'date':None},
      'source_use':{'shelter-ready-tech':'Texts use less bandwidth'},
      'description':'A card. Nothing is stored.'}
R200={'state':'DRAFT_HARD_HOLD','artifact_count':35,'export_target_count_with_six_tools':41,
      'publication_authorized':False,'independent_qd_pass':False,'medical_safety_verified':False,
      'articles':[{'n':i,'slug':m.ARTICLE15_SLUG if i==15 else 's'+str(i),
        'route':'/preparedness/family-communication/family-communication-plan/' if i==15 else '/other/'+str(i)+'/'} for i in range(1,36)]}

def fixture():
    return {m.BODY:BODY.encode(), m.META:json.dumps(META).encode(),
            m.JS:b'// synthetic JS - not a privacy proof\n',m.R200:json.dumps(R200).encode()}

def examine_current(files):
    expected={k:m.git_blob(v) for k,v in files.items()}
    with patch.object(m,'EXPECTED',expected):return m.examine(files)

class R296HoldTests(unittest.TestCase):
    def setUp(self):self.files=fixture()
    def evaluate(self):return examine_current(self.files)
    def rewrite(self,path,obj):self.files[path]=json.dumps(obj).encode()
    def altered_meta(self,fn):
        x=json.loads(self.files[m.META]);fn(x);self.rewrite(m.META,x)
    def altered_r200(self,fn):
        x=json.loads(self.files[m.R200]);fn(x);self.rewrite(m.R200,x)
    def check_error(self,contains):
        r=self.evaluate();self.assertEqual(r['state'],'INVALID_HARD_HOLD',r)
        self.assertTrue(any(contains in e for e in r['errors']),r)
        for f in ('publication_authorized','independent_qd_pass','medical_safety_verified',
                  'privacy_approved','revenue_verified','paid_offer_approved'):
            self.assertIs(r[f],False)
    def check_hold(self):
        r=self.evaluate();self.assertEqual(r['state'],'DRAFT_HARD_HOLD',r)
        self.assertTrue(r['mechanical_witness_consistent']);self.assertEqual(len(r['hold_reasons']),7)
        self.assertEqual(len(r['official_source_candidates_not_self_approving']),3)
        self.assertEqual(r['emergency_note_citation_ids'],['shelter-ready-tech'])
        self.assertTrue(all(r['detected_known_risks'].values()))
        for k in ('publication_authorized','independent_qd_pass','medical_safety_verified',
                  'privacy_approved','revenue_verified','paid_offer_approved'):
            self.assertIs(r[k],False)
    def test_valid_authenticity_fixture_still_hold(self):self.check_hold()
    def test_official_sources_do_not_authorize_claims(self):
        self.assertTrue(all(x['review']=='human-claim-mapping-required' for x in m.SOURCE_REVIEW))
    def test_no_exit_zero_on_complete_synthetic_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for name,value in self.files.items():
                file=root/name;file.parent.mkdir(parents=True,exist_ok=True);file.write_bytes(value)
            with patch.object(m,'EXPECTED',{k:m.git_blob(v) for k,v in self.files.items()}),\
                 contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(m.main(['--repo-root',tmp]),2)
    def test_no_exit_zero_on_incomplete_fixture(self):
        with tempfile.TemporaryDirectory() as tmp,contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(m.main(['--repo-root',tmp]),1)
    def test_missing_act_note(self):
        self.files[m.BODY]=self.files[m.BODY].replace(b'pa-act-note',b'not-act-note')
        self.check_error('MISSING_ACT_NOTE')
    def test_missing_noscript(self):
        self.files[m.BODY]=self.files[m.BODY].replace(b'<noscript>',b'<broken>').replace(b'</noscript>',b'</broken>')
        self.check_error('MISSING_NOSCRIPT_WITNESS')
    def test_cite_not_in_act_note(self):
        self.files[m.BODY]=self.files[m.BODY].replace(b'{{cite:shelter-ready-tech}}',b'')
        self.check_error('EMERGENCY_NOTE_SOURCE_ID_DRIFT')
    def test_wrong_cite_id(self):
        self.files[m.BODY]=self.files[m.BODY].replace(b'{{cite:shelter-ready-tech}}',b'{{cite:fake}}')
        self.check_error('EMERGENCY_NOTE_SOURCE_ID_DRIFT')
    def test_double_cite_id(self):
        self.files[m.BODY]=self.files[m.BODY].replace(b'{{cite:shelter-ready-tech}}',b'{{cite:shelter-ready-tech}}{{cite:unknown}}')
        self.check_error('EMERGENCY_NOTE_SOURCE_ID_DRIFT')
    def test_wrong_911_scope_text(self):
        self.files[m.BODY]=self.files[m.BODY].replace(b'call 911 for anything life-threatening',b'call 911 for any emergency')
        self.check_error('SOURCE_RISK_WITNESS_NOT_REPRODUCED:911-threshold-too-narrow')
    def test_removed_blended_text(self):
        self.files[m.BODY]=self.files[m.BODY].replace(b'for everything else',b'for non-emergency family check-ins')
        self.check_error('SOURCE_RISK_WITNESS_NOT_REPRODUCED:emergency-nonemergency-text-blended')
    def test_removed_privacy_claim(self):
        self.files[m.BODY]=self.files[m.BODY].replace(b'It is not sent or saved.',b'This requires independent verification.')
        self.check_error('SOURCE_RISK_WITNESS_NOT_REPRODUCED:unverified-local-storage-guarantee')
    def test_removed_tab_claim(self):
        self.files[m.BODY]=self.files[m.BODY].replace(b'Closing the tab clears it.',b'Browser persistence unverified.')
        self.check_error('SOURCE_RISK_WITNESS_NOT_REPRODUCED:unverified-tab-close-guarantee')
    def test_removed_nojs_claim(self):
        self.files[m.BODY]=self.files[m.BODY].replace(b'form below still works and prints',b'No-JS behavior pending QA')
        self.check_error('SOURCE_RISK_WITNESS_NOT_REPRODUCED:unverified-noscript-form-function')
    def test_removed_meta_privacy_claim(self):
        self.altered_meta(lambda x:x.update(description='No retention claim currently approved'))
        self.check_error('UNVERIFIED_PRIVACY_METADATA_CLAIM_NOT_REPRODUCED')
    def test_changed_r200_release_state(self):
        self.altered_r200(lambda x:x.update(state='READY'))
        self.check_error('R200_SLATE_CUSTODY_INVALID')
    def test_wrong_r200_article_count(self):
        self.altered_r200(lambda x:x.update(artifact_count=34))
        self.check_error('R200_SLATE_CUSTODY_INVALID')
    def test_wrong_r200_export_count(self):
        self.altered_r200(lambda x:x.update(export_target_count_with_six_tools=40))
        self.check_error('R200_SLATE_CUSTODY_INVALID')
    def test_r200_missing_article15(self):
        self.altered_r200(lambda x:x.update(articles=[a for a in x['articles'] if a['n']!=15]))
        self.check_error('R200_ARTICLE15_CUSTODY_INVALID')
    def test_r200_wrong_article15_slug(self):
        self.altered_r200(lambda x:x['articles'][14].update(slug='wrong'))
        self.check_error('R200_ARTICLE15_CUSTODY_INVALID')
    def test_r200_wrong_article15_route(self):
        self.altered_r200(lambda x:x['articles'][14].update(route='/different/'))
        self.check_error('R200_ARTICLE15_CUSTODY_INVALID')
    def test_r200_duplicate_article15_n(self):
        self.altered_r200(lambda x:x['articles'][13].update(n=15))
        self.check_error('R200_ARTICLE15_CUSTODY_INVALID')
    def test_metadata_missing_source_use(self):
        self.altered_meta(lambda x:x.update(source_use={}))
        self.check_error('TOOL104_CITED_SOURCE_METADATA_CHANGED')
    def test_meta_source_use_wrong_type(self):
        self.altered_meta(lambda x:x.update(source_use=[]))
        self.check_error('TOOL104_CITED_SOURCE_METADATA_CHANGED')
    def test_html_unescape_does_not_infer_safety(self):
        self.files[m.BODY]=self.files[m.BODY].replace(b'It is not sent',b'It&nbsp;is not sent')
        self.check_hold()
    def test_html_tag_split_does_not_infer_safety(self):
        self.files[m.BODY]=self.files[m.BODY].replace(b'Closing the tab clears it.',b'Closing the <em>tab</em> clears it.')
        self.check_hold()
    def test_html_comments_not_used_as_text(self):
        self.assertNotIn('secret',m.text_of('public<!--secret-->text'))
    def test_script_content_not_used_as_text(self):
        self.assertNotIn('secret',m.text_of('visible<script>secret</script>'))
    def test_style_content_not_used_as_text(self):
        self.assertNotIn('secret',m.text_of('visible<style>secret</style>'))
    def test_git_blob_matches_exact_git_object_algorithm(self):
        self.assertEqual(m.git_blob(b'test'),'30d74d258442c7c65512eafab474568dd706c430')
    def test_missing_all_witnesses_invalid(self):
        r=m.examine({});self.assertEqual(r['state'],'INVALID_HARD_HOLD');self.assertEqual(len(r['errors']),4)
    def test_missing_one_witness_never_parsed(self):
        d=dict(self.files);d.pop(m.JS)
        with patch.object(m,'EXPECTED',{k:m.git_blob(v) for k,v in self.files.items()}):
            r=m.examine(d)
        self.assertEqual(r['state'],'INVALID_HARD_HOLD');self.assertEqual(r['detected_known_risks'],{})

def mutating_meta(field,value,expected_fragment):
    def test(self):
        self.altered_meta(lambda x:x.update({field:value}))
        self.check_error(expected_fragment)
    return test

for label,field,val,error in [
  ('wrong_kind','kind','article','TOOL104_IDENTITY_DRIFT'),
  ('wrong_n','n',103,'TOOL104_IDENTITY_DRIFT'),
  ('wrong_slug','slug','fake','TOOL104_IDENTITY_DRIFT'),
  ('wrong_section','section','other','TOOL104_PUBLICATION_STATE_INVALID'),
  ('missing_status','status',{},'TOOL104_PUBLICATION_STATE_INVALID'),
  ('published','status',{'publish':'published'},'TOOL104_PUBLICATION_STATE_INVALID'),
  ('safety_passed','safety_review',{'state':'passed','reviewer':None,'date':None},'TOOL104_SAFETY_REVIEW_NOT_PENDING'),
  ('safety_missing','safety_review',{},'TOOL104_SAFETY_REVIEW_NOT_PENDING'),
  ('safety_reviewer_present','safety_review',{'state':'pending','reviewer':'test','date':None},'TOOL104_SAFETY_REVIEW_NOT_PENDING'),
  ('safety_date_present','safety_review',{'state':'pending','reviewer':None,'date':'2026-11-11'},'TOOL104_SAFETY_REVIEW_NOT_PENDING'),
  ('fake_qd','independent_qd_pass',True,'UNAUTHORIZED_RELEASE_OR_SAFETY_FLAG'),
  ('fake_medical','medical_safety_verified',True,'UNAUTHORIZED_RELEASE_OR_SAFETY_FLAG'),
  ('fake_privacy','privacy_approved',True,'UNAUTHORIZED_RELEASE_OR_SAFETY_FLAG'),
  ('fake_publication','publication_authorized',True,'UNAUTHORIZED_RELEASE_OR_SAFETY_FLAG'),
]:setattr(R296HoldTests,'test_meta_'+label,mutating_meta(field,val,error))

for name in ('independent_qd_pass','medical_safety_verified','privacy_approved','publication_authorized'):
    def make(field):
        def test(self):self.altered_r200(lambda x:x.update({field:True}));self.check_error('UNAUTHORIZED_RELEASE_OR_SAFETY_FLAG')
        return test
    setattr(R296HoldTests,'test_r200_fake_'+name,make(name))

for path,tag in [(m.BODY,'BODY'),(m.META,'META'),(m.JS,'JS'),(m.R200,'R200')]:
    def make(path):
        def test(self):
            modified=dict(self.files);modified[path]+=b'\n'
            with patch.object(m,'EXPECTED',{k:m.git_blob(v) for k,v in self.files.items()}):
                result=m.examine(modified)
            self.assertEqual(result['state'],'INVALID_HARD_HOLD')
            self.assertIn('WITNESS_BLOB_CHANGED_REVIEW_REQUIRED:'+path,result['errors'])
        return test
    setattr(R296HoldTests,'test_pinned_witness_rejects_'+tag,make(path))

for field in ('n','slug','section','source_use','status','safety_review'):
    def make(field):
        def test(self):
            bad=self.files[m.META].replace(b'"'+field.encode()+b'"',b'"replaced_'+field.encode()+b'"',1)
            with patch.object(m,'EXPECTED',{k:m.git_blob(v) for k,v in self.files.items()}):
                result=m.examine({**self.files,m.META:bad})
            self.assertEqual(result['state'],'INVALID_HARD_HOLD')
        return test
    setattr(R296HoldTests,'test_any_unapproved_metadata_byte_change_'+field,make(field))

if __name__=='__main__':unittest.main()
