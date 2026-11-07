"""Synthetic/adversarial R181 integration preflight tests. NOT QD or safety approval."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

TOOL=Path(__file__).resolve().with_name('r181_contributor_intake_gate.py')
spec=importlib.util.spec_from_file_location('r181_gate',TOOL)
gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)


def fixture():
    return {'schema':gate.SCHEMA,'repo':gate.REPO,'state':gate.HOLD,
            'publication_authorized':False,'independent_qd_pass':False,
            'branches':[{'ref':name,'sha':sha,'ahead':0,'behind':0,'status':'identical'}
                        for name,sha in gate.BRANCHES.items()],
            'review_prs':[{'number':n,'head_sha':sha,'base_sha':gate.PR_BASES[n],
                           'state':'open','draft':True,'merged':False,
                           'files':sorted(gate.PR_FILES[n])} for n,sha in gate.PR_HEADS.items()],
            'corpus':{'branch_sha':'532198896128e612e88b3bee36c6368cb825e58b',
                      'article_meta':35,'article_bodies':35,'source_uses':385,
                      'citation_occurrences':2000,'all_draft':True,'unique_urls':True,
                      'qualified_safety_review':False,'independent_qd_pass':False,
                      'publication_authorized':False},
            'funnel':{'audience':'caregivers_school_pickup_reunification',
                      'free_guide':'household-emergency-plan',
                      'optional_tool':'family-reunification-card',
                      'paid_sku':None,'verified_paid_preparedness_sku':False,
                      'paid_checkout_enabled':False,'grok_asset_id':None,
                      'published_destination':None,'verified_orders':None,
                      'net_revenue_usd':None}}

class GateTests(unittest.TestCase):
    def setUp(self): self.f=fixture()
    def rejects(self, f):
        with self.assertRaises((ValueError, TypeError, KeyError)): gate.inspect(f)
    def test_valid_structural_gate_still_hold(self):
        r=gate.inspect(self.f)
        self.assertEqual(r['state'],gate.HOLD)
        self.assertFalse(r['publication_authorized'])
        self.assertFalse(r['commercial_offer_verified'])
        self.assertEqual(len(r['overlap_paths']),3)
    def test_deterministic_output(self):
        self.assertEqual(gate.inspect(self.f)['observation_sha256'],
                         gate.inspect(copy.deepcopy(self.f))['observation_sha256'])
    def test_order_of_branches_immaterial_to_admission(self):
        self.f['branches'].reverse();self.assertEqual(gate.inspect(self.f)['claude_branches_intact'],7)
    def test_missing_file_fail_closed(self):
        with tempfile.TemporaryDirectory() as t:
            p=subprocess.run([sys.executable,str(TOOL),'--observed',str(Path(t)/'missing')],capture_output=True,text=True)
            self.assertEqual(p.returncode,2);self.assertIn(gate.INVALID,p.stdout)
    def test_cli_held_with_fully_formed_synthetic_fixture(self):
        with tempfile.TemporaryDirectory() as t:
            inp=Path(t)/'in.json';out=Path(t)/'report.json';inp.write_text(json.dumps(self.f))
            p=subprocess.run([sys.executable,str(TOOL),'--observed',str(inp),'--output',str(out)],capture_output=True,text=True)
            self.assertEqual(p.returncode,2);self.assertEqual(json.loads(out.read_text())['state'],gate.HOLD)
    def test_invalid_json_cli(self):
        with tempfile.TemporaryDirectory() as t:
            inp=Path(t)/'bad.json';inp.write_text('{bad')
            p=subprocess.run([sys.executable,str(TOOL),'--observed',str(inp)],capture_output=True,text=True)
            self.assertEqual(p.returncode,2);self.assertEqual(json.loads(p.stdout)['state'],gate.INVALID)
    def test_each_branch_sha_tamper(self):
        for i in range(7):
            with self.subTest(i=i):
                f=fixture();f['branches'][i]['sha']='0'*40;self.rejects(f)
    def test_each_branch_ahead_drift(self):
        for i in range(7):
            with self.subTest(i=i):
                f=fixture();f['branches'][i]['ahead']=1;self.rejects(f)
    def test_each_branch_behind_drift(self):
        for i in range(7):
            with self.subTest(i=i):
                f=fixture();f['branches'][i]['behind']=1;self.rejects(f)
    def test_each_pr_head_drift(self):
        for i in range(3):
            with self.subTest(i=i):
                f=fixture();f['review_prs'][i]['head_sha']='0'*40;self.rejects(f)
    def test_each_pr_base_drift(self):
        for i in range(3):
            with self.subTest(i=i):
                f=fixture();f['review_prs'][i]['base_sha']='0'*40;self.rejects(f)
    def test_each_pr_merge_prohibited(self):
        for i in range(3):
            with self.subTest(i=i):
                f=fixture();f['review_prs'][i]['merged']=True;self.rejects(f)
    def test_each_pr_unexpected_file(self):
        for i in range(3):
            with self.subTest(i=i):
                f=fixture();f['review_prs'][i]['files'].append('index.php');self.rejects(f)
    def test_duplicate_branch(self):
        self.f['branches'][0]=self.f['branches'][1];self.rejects(self.f)
    def test_duplicate_pr(self):
        self.f['review_prs'][0]=self.f['review_prs'][1];self.rejects(self.f)
    def test_unexpected_branch(self):
        self.f['branches'][0]['ref']='claude/other';self.rejects(self.f)
    def test_wrong_repo(self):
        self.f['repo']='other/repo';self.rejects(self.f)
    def test_wrong_schema(self):
        self.f['schema']='unknown';self.rejects(self.f)
    def test_release_promotion(self):
        self.f['state']='READY';self.rejects(self.f)
    def test_article_count_tamper(self):
        self.f['corpus']['article_meta']=34;self.rejects(self.f)
    def test_body_count_tamper(self):
        self.f['corpus']['article_bodies']=34;self.rejects(self.f)
    def test_source_use_tamper(self):
        self.f['corpus']['source_uses']=384;self.rejects(self.f)
    def test_citation_count_tamper(self):
        self.f['corpus']['citation_occurrences']=1999;self.rejects(self.f)
    def test_route_duplicate(self):
        self.f['corpus']['unique_urls']=False;self.rejects(self.f)
    def test_article_published(self):
        self.f['corpus']['all_draft']=False;self.rejects(self.f)
    def test_source_review_fake(self):
        self.f['corpus']['qualified_safety_review']=True;self.rejects(self.f)
    def test_false_nested_review(self):
        self.f['review_prs'][0]['independent_qd_pass']=True;self.rejects(self.f)
    def test_free_guide_swap(self):
        self.f['funnel']['free_guide']='making-water-safer';self.rejects(self.f)
    def test_tool_swap(self):
        self.f['funnel']['optional_tool']='water-fieldbook';self.rejects(self.f)
    def test_unsupported_paid_sku(self):
        self.f['funnel']['paid_sku']='PRODUCT-999';self.rejects(self.f)
    def test_fake_verified_paid_sku(self):
        self.f['funnel']['verified_paid_preparedness_sku']=True;self.rejects(self.f)
    def test_paid_checkout_activation(self):
        self.f['funnel']['paid_checkout_enabled']=True;self.rejects(self.f)
    def test_unverified_grok_id(self):
        self.f['funnel']['grok_asset_id']='made-up';self.rejects(self.f)
    def test_unverified_destination(self):
        self.f['funnel']['published_destination']='https://finalvestige.com/test/';self.rejects(self.f)
    def test_unsupported_sales(self):
        self.f['funnel']['verified_orders']=7;self.rejects(self.f)
    def test_unsupported_net_revenue(self):
        self.f['funnel']['net_revenue_usd']=20;self.rejects(self.f)
    def test_missing_corpus(self):
        del self.f['corpus'];self.rejects(self.f)
    def test_missing_funnel(self):
        del self.f['funnel'];self.rejects(self.f)

if __name__=='__main__':unittest.main()
