"""R172 synthetic-only adversarial tests; no medical/food/QD approval."""
import copy
import json
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import r172_jerky_alias_claim_gate as g


def fixture():
    ids = [('base',20,'nchfp-jerky',g.ROOT_URL),
           ('food',3,'nchfp-jerky',g.ROOT_URL),
           ('hist-food',14,g.ALIAS,g.SLASH_URL)]
    variants = [{'origin':o,'row_index':i,
                 'source':{'id':sid,'url':url,'human_link_check':False}}
                for o,i,sid,url in ids]
    group = {'url':g.ROOT_URL, 'canonical_url':g.ROOT_URL,
             'review_status':'pending-human-source-and-reading-scope-review',
             'reviewer':None,'reviewed_on':None,
             'variants':variants,
             'identities':[{'origin':o,'row_index':i,'id':sid} for o,i,sid,_ in ids]}
    quarantine = {'schema':'fv-preparedness-r171-source-variance-quarantine-v1',
       'state':g.HOLD,'human_source_equivalence_review_complete':False,
       'human_qualified_safety_approval':False,'independent_qd_pass':False,
       'publication_authorized':False,'commercial_offer_verified':False,
       'material_discrepancy':{'source_id':g.ALIAS,
        'crosswalk_group_url':g.ROOT_URL,'current_literal_fragment_url':g.SLASH_URL,
        'crosswalk_group_includes_id':True,'current_literal_group_includes_id':False}}
    crosswalk={'schema_version':1,
       'status':'DRAFT_CROSSWALK_ALL_SHARED_SOURCE_GROUPS_UNRESOLVED','groups':[group]}
    fragment={'sources':[{'id':'other-'+str(i)} for i in range(14)] +
              [copy.deepcopy(variants[2]['source'])]}
    metadata={
       'safe-jerky-dehydration':{'slug':'safe-jerky-dehydration','section':'food',
          'status':{'publish':'draft'},'source_use':{
          'nchfp-jerky':'Existing current guidance requires human review.'}},
       'pemmican-and-dried-meats':{'slug':'pemmican-and-dried-meats',
          'section':'lost-ways','status':{'publish':'draft'},'source_use':{
          g.ALIAS:'Historical interpretation needs qualified review.'}}
    }
    return [quarantine,crosswalk,fragment,metadata]


class TestR172(unittest.TestCase):
    def test_structural_fixture_still_draft_hold(self):
        r=g.audit(*fixture(),strict=False)
        self.assertEqual(r['state'],g.HOLD)
        self.assertFalse(r['alias_equivalence_verified'])
        self.assertFalse(r['food_safety_approved'])
        self.assertFalse(r['independent_qd_pass'])
        self.assertFalse(r['publication_authorized'])
        self.assertEqual(len(r['impacted_articles']),2)
    def test_deterministic_receipt(self):
        self.assertEqual(g.audit(*fixture(),strict=False)['impact_receipt_sha256'],
                         g.audit(*fixture(),strict=False)['impact_receipt_sha256'])
    def test_variant_list_order_is_irrelevant(self):
        f=fixture()
        f[1]['groups'][0]['variants'].reverse()
        f[1]['groups'][0]['identities'].reverse()
        self.assertEqual(g.audit(*f,strict=False)['state'],g.HOLD)
    def test_full_baseline_disallows_synthetic(self):
        with self.assertRaises(ValueError):g.audit(*fixture())
    def test_missing_full_checkout_returns_invalid_not_success(self):
        with tempfile.TemporaryDirectory() as d:
            with redirect_stdout(StringIO()) as buf:
                code=g.main(['--repo',d])
            self.assertEqual(code,2)
            receipt=json.loads(buf.getvalue())
            self.assertEqual(receipt['state'],'INVALID_HARD_HOLD')
            self.assertFalse(receipt['publication_authorized'])
    def test_pinned_missing_or_symlink_fails(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            with self.assertRaises(ValueError):g.pinned(p,'missing.json','0'*40)
            (p/'source.json').symlink_to('/etc/passwd')
            with self.assertRaises(ValueError):g.pinned(p,'source.json','0'*40)
    def test_change_to_original_body_protection_would_fail(self):
        self.assertIn('preparedness/docs/r161/body_custody.json',g.ORIGINAL)
        self.assertIn('preparedness/docs/r151/contributor-three-way.json',g.ORIGINAL)


def mutate_case(name, f):
    def run(self):
        s=fixture()
        f(s)
        with self.assertRaises((ValueError,TypeError,KeyError,AttributeError)):
            g.audit(*s,strict=False)
    run.__name__='test_reject_'+name
    setattr(TestR172,run.__name__,run)

MUTANTS={
 'quarantine_schema':lambda x:x[0].__setitem__('schema','wrong'),
 'quarantine_missing_schema':lambda x:x[0].pop('schema'),
 'quarantine_approval':lambda x:x[0].__setitem__('state','APPROVED'),
 'quarantine_human_equivalence':lambda x:x[0].__setitem__('human_source_equivalence_review_complete',True),
 'quarantine_human_equivalence_removed':lambda x:x[0].pop('human_source_equivalence_review_complete'),
 'quarantine_food_safety':lambda x:x[0].__setitem__('human_qualified_safety_approval',True),
 'quarantine_food_safety_string':lambda x:x[0].__setitem__('human_qualified_safety_approval','false'),
 'quarantine_qd_fabrication':lambda x:x[0].__setitem__('independent_qd_pass',True),
 'quarantine_publication_approval':lambda x:x[0].__setitem__('publication_authorized',True),
 'quarantine_offer_approval':lambda x:x[0].__setitem__('commercial_offer_verified',True),
 'quarantine_source_id':lambda x:x[0]['material_discrepancy'].__setitem__('source_id','wrong'),
 'quarantine_group_url':lambda x:x[0]['material_discrepancy'].__setitem__('crosswalk_group_url',g.SLASH_URL),
 'quarantine_fragment_url':lambda x:x[0]['material_discrepancy'].__setitem__('current_literal_fragment_url',g.ROOT_URL),
 'quarantine_original_roster_false':lambda x:x[0]['material_discrepancy'].__setitem__('crosswalk_group_includes_id',False),
 'quarantine_fragment_group_true':lambda x:x[0]['material_discrepancy'].__setitem__('current_literal_group_includes_id',True),
 'crosswalk_schema':lambda x:x[1].__setitem__('schema_version',2),
 'crosswalk_status_fake_approval':lambda x:x[1].__setitem__('status','APPROVED'),
 'crosswalk_no_groups':lambda x:x[1].__setitem__('groups',[]),
 'crosswalk_duplicate_group':lambda x:x[1]['groups'].append(copy.deepcopy(x[1]['groups'][0])),
 'crosswalk_group_url':lambda x:x[1]['groups'][0].__setitem__('url',g.SLASH_URL),
 'crosswalk_canonical_url':lambda x:x[1]['groups'][0].__setitem__('canonical_url',g.SLASH_URL),
 'crosswalk_group_approved':lambda x:x[1]['groups'][0].__setitem__('review_status','approved'),
 'crosswalk_reviewer_fabricated':lambda x:x[1]['groups'][0].__setitem__('reviewer','Q.D.'),
 'crosswalk_reviewed_on_fabricated':lambda x:x[1]['groups'][0].__setitem__('reviewed_on','2026-11-06'),
 'crosswalk_variant_removed':lambda x:x[1]['groups'][0]['variants'].pop(),
 'crosswalk_variant_extra':lambda x:x[1]['groups'][0]['variants'].append(copy.deepcopy(x[1]['groups'][0]['variants'][1])),
 'crosswalk_variant_origin':lambda x:x[1]['groups'][0]['variants'][0].__setitem__('origin','hist-food'),
 'crosswalk_variant_index':lambda x:x[1]['groups'][0]['variants'][0].__setitem__('row_index',1),
 'crosswalk_variant_id':lambda x:x[1]['groups'][0]['variants'][0]['source'].__setitem__('id','fraud'),
 'crosswalk_variant_url':lambda x:x[1]['groups'][0]['variants'][0]['source'].__setitem__('url',g.SLASH_URL),
 'crosswalk_variant_full_url':lambda x:x[1]['groups'][0]['variants'][2]['source'].__setitem__('url',g.ROOT_URL),
 'crosswalk_variant_human_approved':lambda x:x[1]['groups'][0]['variants'][1]['source'].__setitem__('human_link_check',True),
 'crosswalk_variant_link_null':lambda x:x[1]['groups'][0]['variants'][2]['source'].__setitem__('human_link_check',None),
 'crosswalk_id_removed':lambda x:x[1]['groups'][0]['identities'].pop(),
 'crosswalk_id_changed':lambda x:x[1]['groups'][0]['identities'][0].__setitem__('id','fake'),
 'crosswalk_id_origin':lambda x:x[1]['groups'][0]['identities'][2].__setitem__('origin','base'),
 'fragment_missing_sources':lambda x:x[2].pop('sources'),
 'fragment_missing_index_14':lambda x:x[2]['sources'].pop(),
 'fragment_alias_id':lambda x:x[2]['sources'][14].__setitem__('id','nchfp-jerky'),
 'fragment_alias_url':lambda x:x[2]['sources'][14].__setitem__('url',g.ROOT_URL),
 'fragment_alias_link':lambda x:x[2]['sources'][14].__setitem__('human_link_check',True),
 'fragment_alias_changed_title':lambda x:x[2]['sources'][14].__setitem__('title','New fabricated source'),
 'meta_missing':lambda x:x[3].clear(),
 'meta_slug_changed':lambda x:x[3]['safe-jerky-dehydration'].__setitem__('slug','wrong'),
 'meta_published':lambda x:x[3]['safe-jerky-dehydration']['status'].__setitem__('publish','publish'),
 'meta_url_duplicate':lambda x:x[3]['pemmican-and-dried-meats'].__setitem__('slug','safe-jerky-dehydration'),
 'meta_uses_missing':lambda x:x[3]['safe-jerky-dehydration'].pop('source_use'),
 'meta_uses_empty':lambda x:x[3]['safe-jerky-dehydration'].__setitem__('source_use',{}),
 'meta_explanation_empty':lambda x:x[3]['safe-jerky-dehydration']['source_use'].__setitem__('nchfp-jerky',''),
 'meta_impact_erased':lambda x:x[3]['safe-jerky-dehydration']['source_use'].clear(),
}

for name, fn in MUTANTS.items():
    mutate_case(name,fn)

if __name__=='__main__':
    unittest.main()
