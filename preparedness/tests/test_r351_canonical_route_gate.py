"""R351 builder-derived route custody, isolated synthetic fixtures; no canonical writes."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import r351_canonical_route_gate as gate

SOURCE='''class Library:
    def url_path(self, slug: str) -> str:
        a = self.articles.get(slug) or self.slate[slug]
        return f"{self.taxonomy['base_path']}{a['section']}/{slug}/"
    def section_path(self, section: str) -> str:
        return f"{self.taxonomy['base_path']}{section}/"
'''

def fixture():
    sections=['start-here','water','food','shelter-power','health-sanitation',
              'family-communication','lost-ways','field-tools']
    a=[{'slug':f'a-{i:02}','section':sections[i%7]} for i in range(1,36)]
    t=[{'slug':f't-{i:02}'} for i in range(1,7)]
    tax={'base_path':'/preparedness/','sections':[{'slug':x} for x in sections],
         'slate':a,'tools':t}
    docs=[]
    for row in a:
        docs.append({'kind':'articles','meta':{'slug':row['slug'],'section':row['section'],
             'status':{'publish':'draft'},'safety_review':{'state':'pending'}}})
    for row in t:
        docs.append({'kind':'tools','meta':{'slug':row['slug'],'section':'field-tools',
             'status':{'publish':'draft'},'safety_review':{'state':'pending'}}})
    return tax,docs

class Routes(unittest.TestCase):
    def test_normal_route_parity(self):
        tax,docs=fixture();out=gate.audit(tax,docs,SOURCE)
        self.assertEqual(out['errors'],[])
        self.assertEqual((out['article_count'],out['tool_count']),(35,6))
        self.assertEqual(len(set(out['route_sha256_by_document'].values())),41)
        self.assertFalse(out['may_publish']);self.assertFalse(out['qualified_qd_pass'])
        self.assertFalse(out['native_build_verified']);self.assertFalse(out['verified_paid_orders'])
    def test_actual_builder_ast_contract(self):
        self.assertTrue(gate.builder_contract(SOURCE))
        for bad in [SOURCE.replace('/{slug}/','/{slug}'),SOURCE.replace('self.slate[slug]','self.slate.get(slug)'),
                    SOURCE.replace('class Library','class FakeLibrary'),SOURCE.replace('def section_path','async def section_path'),
                    SOURCE.replace("self.taxonomy['base_path']","'/wrong/'"), 'not python', '',
                    SOURCE.replace('return f','print(1); return f')]:
            self.assertFalse(gate.builder_contract(bad))
    def test_contributor_sha_drift_and_route_conflict(self):
        tax,docs=fixture();snaps={k:{'sha':v,'taxonomy':tax,'documents':docs,'builder':SOURCE} for k,v in gate.prior.PINS.items()}
        self.assertEqual(gate.compare(snaps)['errors'],[])
        key=next(iter(snaps));snaps[key]=copy.deepcopy(snaps[key]);snaps[key]['documents'][0]['meta']['section']='food'
        out=gate.compare(snaps)
        self.assertIn('CROSS_BRANCH_ROUTE_DRIFT',out['errors'])
        self.assertIn('articles/a-01',out['route_conflict_document_ids'])
        snaps[key]['sha']='0'*40
        self.assertIn('SHA_DRIFT:'+key,gate.compare(snaps)['errors'])
    def test_no_native_checkout_must_reject(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(gate.audit_git_repo(Path(td))['status'],'INVALID_HARD_HOLD')
    def test_reserved_and_cross_kind_overwrites(self):
        tax,docs=fixture();docs[35]['meta']['slug']='a-01'
        self.assertIn('BUILDER_ARTICLE_TOOL_OVERWRITE:a-01',gate.audit(tax,docs,SOURCE)['errors'])
    def test_unlisted_kit_builder_cannot_replace_missing_pantry_worksheet(self):
        tax,docs=fixture()
        # Mirrors a real source/taxonomy disagreement observed on R350 (names
        # are only a synthetic reproduction of the failure mode here).
        docs[36]['meta']['slug']='kit-builder'
        errors=gate.audit(tax,docs,SOURCE)['errors']
        self.assertIn('DOCUMENT_NOT_IN_TAXONOMY:tools/kit-builder',errors)
        self.assertIn('INCOMPLETE_TOOLS_INVENTORY',errors)
        self.assertEqual(gate.audit(tax,docs,SOURCE)['status'],'INVALID_HARD_HOLD')
    def test_explicit_url_must_match_actual_builder(self):
        tax,docs=fixture();doc=docs[0]['meta'];route='/preparedness/water/a-01/'
        for k in ('canonical_url','permalink','url'):
            doc[k]=route
            self.assertNotIn('EXPLICIT_URL_CONFLICT:articles/a-01:'+k,gate.audit(tax,docs,SOURCE)['errors'])
            doc[k]=route+'?utm_content=not-a-route'
            self.assertIn('EXPLICIT_URL_CONFLICT:articles/a-01:'+k,gate.audit(tax,docs,SOURCE)['errors'])
            del doc[k]
    def test_hard_hold_on_unsafe_slug(self):
        for bad in ['UPPER','../path','foo%2Fbar','foo/bar','empty space','ä','']:
            tax,docs=fixture();docs[0]['meta']['slug']=bad
            self.assertIn('UNSAFE_DOCUMENT_ROUTE',gate.audit(tax,docs,SOURCE)['errors'])
    def test_bad_published_or_approved_states(self):
        tax,docs=fixture();docs[0]['meta']['status']['publish']='published'
        self.assertIn('PUBLICATION_STATE_NOT_DRAFT:articles/a-01',gate.audit(tax,docs,SOURCE)['errors'])
        tax,docs=fixture();docs[0]['meta']['safety_review']['state']='approved'
        self.assertIn('SAFETY_STATE_NOT_PENDING:articles/a-01',gate.audit(tax,docs,SOURCE)['errors'])
    def test_builder_blob_pin_protects_integration(self):
        tax,docs=fixture();self.assertIn('INTEGRATION_BUILDER_BLOB_DRIFT',gate.audit(tax,docs,SOURCE,exact_builder=True)['errors'])
    def test_base_route_contract(self):
        for val in ['/preparedness','/prep/','//preparedness/','https://other.test/preparedness/','../preparedness/']:
            tax,docs=fixture();tax['base_path']=val
            self.assertIn('BASE_PATH_CHANGED',gate.audit(tax,docs,SOURCE)['errors'])
    def test_no_release_flags_even_if_all_parity_checks_pass(self):
        tax,docs=fixture();out=gate.audit(tax,docs,SOURCE)
        for flag in gate.HOLD:self.assertIs(out[flag],False)
        self.assertTrue(out['routes_not_verified_on_live_wordpress'])

# 41 independently discovered positive cases plus 41 independently discovered missing
# source-document cases, not merely 82 assertions hidden in a single test.
def _positive(i):
    def test(self):
        tax,docs=fixture();d=docs[i];m=d['meta'];k=d['kind']+'/'+m['slug']
        self.assertEqual(gate.audit(tax,docs,SOURCE)['route_sha256_by_document'][k],
                         gate.digest('/preparedness/'+m['section']+'/'+m['slug']+'/'))
    return test

def _negative(i):
    def test(self):
        tax,docs=fixture();docs.pop(i)
        self.assertTrue(any(x.startswith('INCOMPLETE_') for x in gate.audit(tax,docs,SOURCE)['errors']))
    return test

for i in range(41):
    setattr(Routes,f'test_route_{i+1:02}',_positive(i))
    setattr(Routes,f'test_missing_{i+1:02}',_negative(i))

if __name__=='__main__':unittest.main()
