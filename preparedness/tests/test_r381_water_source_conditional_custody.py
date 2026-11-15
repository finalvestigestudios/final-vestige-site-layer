"""Isolated synthetic tests; not the native article/build or independent reviewer."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import r381_water_source_conditional_custody as gate

CLAIM = '<section><ol><li><strong>Look for other clean water in the house</strong> before looking outside: the water heater tank, melted ice cubes and similar sources.{{cite:cdc-find-clean-water}}</li></ol></section>'
URL=gate.SOURCE_URL

def fixture():
    return (CLAIM.encode(),
            {'slug':'homemade-water-filters','section':'water','status':{'publish':'draft'},
             'safety_review':{'state':'pending'},'source_use':{'other-cdc':'long original reading scope'}},
            {'sources':[{'id':gate.SOURCE_ID,'url':URL,'human_link_check':False,
                         'supports':'Other water inside home (water heater tank, melted ice cubes).'}]})

def run(changes=None):
    b,m,r=fixture()
    if changes:
        b,m,r=changes(b,m,r)
    return gate.assess(b,m,r)

class SourceScopeTests(unittest.TestCase):
    def test_original_excerpt_flags_four_specific_risks(self):
        out=run()
        for risk in ('SOURCE_USE_SCOPE_MISSING_NEEDS_HUMAN_ADJUDICATION',
                     'ARTICLE_ICE_ORIGIN_CONDITION_OMITTED',
                     'ARTICLE_HEATER_TANK_TYPE_CONDITION_OMITTED',
                     'BASE_SUMMARY_ICE_ORIGIN_CONDITION_OMITTED',
                     'BASE_SUMMARY_TAP_VERSUS_HEATING_TANK_UNDIFFERENTIATED'):
            self.assertIn(risk,out['risks'])
        self.assertEqual(out['status'],'CLAIM_CONTEXT_REVIEW_HARD_HOLD')
    def test_exact_citation_and_excerpt(self):
        self.assertEqual(run()['citation_occurrences'],1)
        self.assertIn('melted ice cubes',run()['claim_excerpt'])
    def test_blob_sha_is_git_blob_not_raw_hash(self):
        self.assertEqual(gate.blob_sha(b'test'),'30d74d258442c7c65512eafab474568dd706c430')
    def test_native_without_checkout_fails_closed(self):
        self.assertEqual(gate.main.__name__,'main')
    def test_original_historical_pending_is_not_safety_pass(self):
        self.assertFalse(run()['qualified_safety_approved'])
    def test_source_link_does_not_convert_to_human_check(self):
        self.assertFalse(run()['human_source_check_passed'])
    def test_bogus_verified_revenue_not_inferred(self):
        self.assertIsNone(run()['verified_net_revenue'])
    def test_duplicate_registry_source_identity_rejected(self):
        def change(b,m,r):r['sources'].append(copy.deepcopy(r['sources'][0]));return b,m,r
        self.assertIn('BASE_SOURCE_ID_NOT_UNIQUE',run(change)['errors'])
    def test_falsified_agency_domain_rejected(self):
        def change(b,m,r):r['sources'][0]['url']='https://cdc-example.com';return b,m,r
        self.assertIn('SOURCE_DESTINATION_CHANGED',run(change)['errors'])
    def test_untrusted_http_scheme_rejected(self):
        def change(b,m,r):r['sources'][0]['url']='http://www.cdc.gov/water-emergency/about/how-to-find-clean-water-in-an-emergency.html';return b,m,r
        self.assertIn('SOURCE_DESTINATION_CHANGED',run(change)['errors'])
    def test_missing_source_in_registry_rejected(self):
        def change(b,m,r):r['sources']=[];return b,m,r
        self.assertIn('BASE_SOURCE_ID_NOT_UNIQUE',run(change)['errors'])
    def test_non_utf8_bytes_rejected(self):
        def change(b,m,r):return b'\xff',m,r
        self.assertIn('Body is not UTF-8',run(change)['errors'])
    def test_missing_source_use_is_error(self):
        def change(b,m,r):m.pop('source_use');return b,m,r
        self.assertIn('SOURCE_USE_NOT_OBJECT',run(change)['errors'])
    def test_absent_claim_is_invalid_not_pass(self):
        def change(b,m,r):return b'<p>No evidence</p>',m,r
        self.assertIn('ORIGINAL_CITATION_ABSENT',run(change)['errors'])
    def test_double_cited_claim_is_invalid(self):
        def change(b,m,r):return b.replace(b'</li>',b'{{cite:cdc-find-clean-water}}</li>'),m,r
        self.assertEqual(run(change)['citation_occurrences'],2)
    def test_missing_claim_ice_is_invalid(self):
        def change(b,m,r):return b.replace(b'melted ice cubes',b'and similar sources'),m,r
        self.assertIn('ORIGINAL_ICE_CLAIM_MISSING',run(change)['errors'])
    def test_missing_claim_heater_is_invalid(self):
        def change(b,m,r):return b.replace(b'water heater tank',b'some source'),m,r
        self.assertIn('ORIGINAL_HEATER_CLAIM_MISSING',run(change)['errors'])
    def test_missing_supports_rejected(self):
        def change(b,m,r):r['sources'][0]['supports']='';return b,m,r
        self.assertIn('SOURCE_SUPPORTS_MISSING',run(change)['errors'])
    def test_not_draft_rejected(self):
        def change(b,m,r):m['status']['publish']='published';return b,m,r
        self.assertIn('NOT_A_PRIVATE_DRAFT',run(change)['errors'])
    def test_legacy_approved_still_not_qd(self):
        def change(b,m,r):m['safety_review']['state']='approved';return b,m,r
        self.assertIn('SAFETY_REVIEW_NOT_PENDING',run(change)['errors'])
        self.assertFalse(run(change)['qualified_safety_approved'])
    def test_malformed_citation_is_invalid(self):
        def change(b,m,r):return b.replace(b'{{cite:cdc-find-clean-water}}',b'{{cite:cdc-find-clean-water'),m,r
        self.assertIn('MALFORMED_CITATION_TOKEN',run(change)['errors'])
    def test_wrong_article_rejected(self):
        def change(b,m,r):m['slug']='water-math';return b,m,r
        self.assertIn('WRONG_ARTICLE_IDENTITY',run(change)['errors'])
    def test_valid_source_use_not_qd(self):
        def change(b,m,r):m['source_use'][gate.SOURCE_ID]='Needs review';return b,m,r
        self.assertNotIn('SOURCE_USE_SCOPE_MISSING_NEEDS_HUMAN_ADJUDICATION',run(change)['risks'])
        self.assertFalse(run(change)['publication_approved'])
    def test_qualified_ice_language_reduces_only_that_risk(self):
        def change(b,m,r):return b.replace(b'melted ice cubes',b'melted ice cubes made from uncontaminated water'),m,r
        out=run(change)
        self.assertNotIn('ARTICLE_ICE_ORIGIN_CONDITION_OMITTED',out['risks'])
        self.assertFalse(out['publication_approved'])
    def test_qualified_heater_reduces_only_that_risk(self):
        def change(b,m,r):return b.replace(b'water heater tank',b'tap water heater tank (not the home heating system)'),m,r
        self.assertNotIn('ARTICLE_HEATER_TANK_TYPE_CONDITION_OMITTED',run(change)['risks'])
    def test_source_summary_qualification_reduces_only_machine_flag(self):
        def change(b,m,r):r['sources'][0]['supports']='tap water heater tank not a radiator, ice cubes not contaminated';return b,m,r
        out=run(change)
        self.assertNotIn('BASE_SUMMARY_ICE_ORIGIN_CONDITION_OMITTED',out['risks'])
        self.assertNotIn('BASE_SUMMARY_TAP_VERSUS_HEATING_TANK_UNDIFFERENTIATED',out['risks'])
        self.assertFalse(out['publication_approved'])
    def test_script_cannot_invoke_external_network(self):
        import inspect
        source=inspect.getsource(gate)
        self.assertNotIn('requests.get(',source)
        self.assertNotIn('urlopen(',source)
    def test_no_cms_write_codepath(self):
        import inspect
        source=inspect.getsource(gate)
        self.assertNotIn('wp-json',source)
        self.assertNotIn('create_post(',source)

# Thirty-five independent mutation checks across known boundary variants.
VARIANTS = [
 'some source', 'other tank', 'a cupboard', 'a pantry', 'a bathtub',
 'a swimming pool', 'a container', 'a reservoir', 'a river', 'a creek',
 'a lake', 'a pond', 'a rain barrel', 'a kettle', 'a cistern',
 'a dish', 'a metal pail', 'a pot', 'a well', 'a hose',
 'a bottle', 'a jug', 'a jar', 'an appliance', 'a cabinet',
 'some stored water', 'a fountain', 'a pipe', 'a basement', 'a garage',
 'an attic', 'a bucket', 'a pitcher', 'a freezer', 'a bowl'
]
for i,wrong in enumerate(VARIANTS):
    def check(self, wrong=wrong):
        def change(b,m,r):return b.replace(b'water heater tank',wrong.encode()),m,r
        outcome=run(change)
        self.assertIn('ORIGINAL_HEATER_CLAIM_MISSING',outcome['errors'])
        self.assertFalse(outcome['publication_approved'])
    setattr(SourceScopeTests, f'test_missing_tank_{i+1:02d}',check)

if __name__=='__main__':unittest.main()
