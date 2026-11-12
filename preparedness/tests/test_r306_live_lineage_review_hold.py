"""R306 adversarial synthetic-only tests; never alter the live source tree."""
from __future__ import annotations
import importlib.util
import copy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

HERE = Path(__file__).resolve().parents[2]
P = HERE / 'preparedness/tools/r306_live_lineage_review_hold.py'
spec = importlib.util.spec_from_file_location('fv_r306_lineage', P)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def specimen(base):
    content = base / 'preparedness/content/articles'
    content.mkdir(parents=True)
    original=[]; lines=[]
    for i in range(1,36):
        slug = f'article-{i:02d}'
        bchange = i <= 14
        mchange = i <= 9 or 15 <= i <= 17
        fb = (f'old text {i}').encode()
        ib = (f'changed text {i}' if bchange else f'old text {i}').encode()
        fm = (f'old metadata {i}').encode()
        im = (f'changed metadata {i}' if mchange else f'old metadata {i}').encode()
        (content / f'{slug}.body.html').write_bytes(ib)
        (content / f'{slug}.meta.json').write_bytes(im)
        original.append({'n': i, 'slug': slug, 'source_cluster':'start',
              'route':f'/preparedness/start-here/{slug}/','branch_sha': 'a'*40,
              'body_oid': mod.git_blob(fb), 'meta_oid': mod.git_blob(fm)})
        fmtonly = i in (10,11,12,13)
        status = ('FORMAT_ONLY_OBSERVED_QA_PENDING' if fmtonly else
             'CONTENT_CHANGE_UNADJUDICATED' if bchange else
             'METADATA_CHANGE_UNADJUDICATED' if mchange else
             'FROZEN_IDENTITY_ONLY_QA_PENDING')
        lines.append({'n':i,'slug':slug,'source_cluster':'start',
             'route':f'/preparedness/start-here/{slug}/','frozen_branch_sha':'a'*40,
             'frozen_body_blob':mod.git_blob(fb), 'integrated_body_blob':mod.git_blob(ib),
             'frozen_meta_blob':mod.git_blob(fm), 'integrated_meta_blob':mod.git_blob(im),
             'line_endings_only_observed':fmtonly, 'review_state':status})
    ledger={'schema':mod.SCHEMA, 'state':'DRAFT_HARD_HOLD','articles':lines,
      'publication_authorized':False,'independent_qd_pass':False,
      'medical_safety_verified':False,'privacy_verified':False,
      'paid_offer_approved':False,'all_41_native_exports_verified':False}
    return ledger, {'articles':original}


class BaselineContract(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.ledger,self.frozen=specimen(self.root)

    def check(self, want='INVALID_HARD_HOLD'):
        result=mod.audit(self.root,self.ledger,self.frozen)
        self.assertEqual(result['state'],want)
        self.assertFalse(result['publication_authorized'])
        self.assertFalse(result['independent_qd_pass'])
        self.assertFalse(result['medical_safety_verified'])
        self.assertFalse(result['all_41_native_exports_verified'])
        return result

    def test_01_valid_fixture_is_still_draft_hold(self):
        r=self.check('DRAFT_HARD_HOLD');self.assertEqual(r['errors'],[])
        self.assertEqual(r['integrated_file_blobs_verified'],70)
    def test_02_expected_body_changes(self):self.assertEqual(self.check('DRAFT_HARD_HOLD')['body_changes'],14)
    def test_03_expected_meta_changes(self):self.assertEqual(self.check('DRAFT_HARD_HOLD')['metadata_changes'],12)
    def test_04_expected_both_changes(self):self.assertEqual(self.check('DRAFT_HARD_HOLD')['both_changed'],9)
    def test_05_expected_format_count(self):self.assertEqual(self.check('DRAFT_HARD_HOLD')['line_endings_only_observed'],4)
    def test_06_empty_ledger(self):self.ledger['articles']=[];self.check()
    def test_07_empty_original(self):self.frozen['articles']=[];self.check()
    def test_08_duplicate_slug(self):self.ledger['articles'][1]=copy.deepcopy(self.ledger['articles'][0]);self.check()
    def test_09_duplicate_route(self):self.ledger['articles'][1]['route']=self.ledger['articles'][0]['route'];self.check()
    def test_10_published_claim(self):self.ledger['publication_authorized']=True;self.check()
    def test_11_fake_qd_pass(self):self.ledger['independent_qd_pass']=True;self.check()
    def test_12_fake_medical_review(self):self.ledger['medical_safety_verified']=True;self.check()
    def test_13_fake_privacy_review(self):self.ledger['privacy_verified']=True;self.check()
    def test_14_fake_checkout_approval(self):self.ledger['paid_offer_approved']=True;self.check()
    def test_15_fake_export_approval(self):self.ledger['all_41_native_exports_verified']=True;self.check()
    def test_16_wrong_schema(self):self.ledger['schema']='unknown';self.check()
    def test_17_fake_review_state(self):self.ledger['articles'][0]['review_state']='QD_PASS';self.check()
    def test_18_changed_original_blob(self):self.frozen['articles'][0]['body_oid']='b'*40;self.check()
    def test_19_changed_original_branch(self):self.frozen['articles'][0]['branch_sha']='b'*40;self.check()
    def test_20_changed_route(self):self.ledger['articles'][0]['route']='/other/article/';self.check()
    def test_21_changed_cluster(self):self.ledger['articles'][0]['source_cluster']='another';self.check()
    def test_22_changed_number(self):self.ledger['articles'][0]['n']=99;self.check()
    def test_23_odd_sha(self):self.ledger['articles'][0]['integrated_meta_blob']='notasha';self.check()
    def test_24_extra_file(self):
        (self.root/'preparedness/content/articles/extra.body.html').write_text('x');self.check()
    def test_25_missing_file(self):
        (self.root/'preparedness/content/articles/article-01.meta.json').unlink();self.check()
    def test_26_newline_only_on_unchanged(self):
        self.ledger['articles'][20]['line_endings_only_observed']=True;self.check()
    def test_27_fake_newline_only(self):
        self.ledger['articles'][0]['line_endings_only_observed']=True;self.check()
    def test_28_wrong_counts(self):
        self.ledger['articles'][0]['frozen_body_blob']=self.ledger['articles'][0]['integrated_body_blob'];self.check()
    def test_29_repeated_original_slug(self):
        self.frozen['articles'][1]['slug']=self.frozen['articles'][0]['slug'];self.check()
    def test_30_invalid_slug(self):self.ledger['articles'][0]['slug']='../bad';self.check()
    def test_31_missing_row(self):self.ledger['articles'].pop();self.check()
    def test_32_null_row(self):self.ledger['articles'][0]=None;self.check()
    def test_33_no_review_state(self):self.ledger['articles'][0].pop('review_state');self.check()
    def test_34_wrong_integrated_oid(self):self.ledger['articles'][0]['integrated_body_blob']='f'*40;self.check()
    def test_35_undefined_guard(self):self.ledger.pop('independent_qd_pass');self.check()
    def test_36_unknown_metadata_record(self):self.frozen['articles'][0]['slug']='missing';self.check()
    def test_37_wrong_draft_state(self):self.ledger['state']='PUBLISHED';self.check()
    def test_38_absent_schema_object(self):self.ledger=None;self.check()
    def test_39_absent_frozen_object(self):self.frozen=None;self.check()
    def test_40_incomplete_repo_hard_hold(self):
        with TemporaryDirectory() as d:self.assertEqual(mod.main(['--repo-root',d]),1)


def make_mutation_check(i):
    def test(self):
        row=self.ledger['articles'][i-1]
        file=self.root/'preparedness/content/articles'/f"{row['slug']}.body.html"
        file.write_bytes(file.read_bytes()+b'\n\nUNREVIEWED_MUTATION')
        r=self.check()
        self.assertIn('INTEGRATED_BLOB_MISMATCH',str(r['errors']))
    return test

for i in range(1,36):
    setattr(BaselineContract,f'test_mutated_article_{i:02d}_must_hard_hold',make_mutation_check(i))

if __name__=='__main__':unittest.main()
