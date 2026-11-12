"""R311 synthetic adversarial source crosswalk; all writes isolated in TemporaryDirectory."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('r311', HERE/'tools'/'r311_cited_source_crosswalk_hold.py')
r311 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(r311)
r310 = r311.r310


def entry(sid, *, verified='2026-11-01', url=None, supports='Agency source claim'):
    return {'id': sid, 'url': url or 'https://www.ready.gov/' + sid,
            'title': 'Synthetic agency source', 'publisher': 'Synthetic agency',
            'kind': 'regulator', 'verified_on': verified,
            'human_link_check': False, 'supports': supports}


class SourceFixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='fv-r311-source-fixture-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.sources = {p: {'sources': []} for p in r311.SOURCES}
        self.sources['preparedness/sources/register.json']['sources'] = [entry('source-a'),entry('source-b',verified=None)]
        self.sources['preparedness/sources/fragments/start.json']['sources'] = [entry('source-b')]
        self.paths = {}
        for path, data in self.sources.items():
            target = self.root/path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(data), encoding='utf-8')
            self.paths[path] = target
        taxonomy = {'tools': [{'slug':slug, 'gate':True,'status':'drafted-pending-safety-review'}
                              for slug in r310.SLUGS],
                    'slate':[{'slug':'household-emergency-plan'}]}
        tax = self.root/r310.TAXONOMY
        tax.parent.mkdir(parents=True,exist_ok=True)
        tax.write_text(json.dumps(taxonomy),encoding='utf-8')
        for rel, value in ((r310.PREDECESSOR,'r309 synthetic fixture'),
                           (r311.PREDECESSOR, 'r310 synthetic fixture')):
            path = self.root/rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(value, encoding='utf-8')
        self.tools = {}
        for i, slug in enumerate(r310.SLUGS):
            body = self.root/f'preparedness/content/tools/{slug}.body.html'
            meta = self.root/f'preparedness/content/tools/{slug}.meta.json'
            body.parent.mkdir(parents=True,exist_ok=True)
            body.write_text('<article><p>{{cite:source-a}} {{cite:source-b}} {{link:household-emergency-plan|plan}}</p></article>', encoding='utf-8')
            meta.write_text(json.dumps({'kind':'tool','slug':slug,'n':101+i,
                                        'section':'field-tools','track':'modern',
                                        'status':{'editorial':'drafted','publish':'draft'},
                                        'safety_review':{'state':'pending','reviewer':None,'date':None},
                                        'source_use':{'source-a':'Source A claim','source-b':'Source B claim'}}),encoding='utf-8')
            self.tools[slug] = (body,meta)
        self.baseline_pins = self.pins()

    def pins(self):
        return {'source_pins':{p:r310.oid(t.read_bytes()) for p,t in self.paths.items()},
                'tool_pins':{slug:tuple(r310.oid(p.read_bytes()) for p in pair)
                             for slug,pair in self.tools.items()},
                'predecessor_oid':r310.oid((self.root/r311.PREDECESSOR).read_bytes()),
                'r310_predecessor_oid':r310.oid((self.root/r310.PREDECESSOR).read_bytes()),
                'taxonomy_oid':r310.oid((self.root/r310.TAXONOMY).read_bytes())}

    def run_audit(self, *, pin=True):
        return r311.audit(self.root, **self.baseline_pins if pin else self.pins())

    def expect(self, code):
        result = self.run_audit()
        self.assertTrue(any(e.startswith(code) for e in result['errors']),result)
        self.assertFalse(result['publication_authorized'])
        self.assertFalse(result['independent_qd_pass'])
        return result

    def edit(self,path,transform):
        data=json.loads(self.paths[path].read_text(encoding='utf-8'))
        transform(data)
        self.paths[path].write_text(json.dumps(data),encoding='utf-8')


class CrosswalkTests(SourceFixture):
    def test_valid_fixture_is_held_not_approved(self):
        r=self.run_audit()
        self.assertEqual(r['errors'],[])
        self.assertEqual(r['state'],'DRAFT_HARD_HOLD')
        self.assertEqual(r['total_source_use_links'],12)
        self.assertEqual(r['unique_cited_source_ids'],2)
        self.assertEqual(r['source_blobs_verified'],5)
        self.assertEqual(r['human_link_check_outstanding_ids'],['source-a','source-b'])
        self.assertIsNone(r['net_revenue_per_1000_qualified_sessions'])

    def test_r310_integrity_inherited(self):
        self.tools[r310.SLUGS[0]][1].write_text('{}',encoding='utf-8')
        self.expect('INHERITED_R310:')

    def test_no_real_source_verification_claim(self):
        r=self.run_audit()
        self.assertFalse(r['medical_safety_verified'])
        self.assertFalse(r['actual_41_wordpress_drafts_verified'])
        self.assertFalse(r['rights_cleared_paid_sku_verified'])
        self.assertIsNone(r['confirmed_paid_orders'])

    def test_missing_cited_source(self):
        self.edit('preparedness/sources/register.json', lambda v:v['sources'].pop(0))
        self.expect('CITED_SOURCE_NOT_REGISTERED:')

    def test_missing_source_fetch_verification(self):
        self.edit('preparedness/sources/fragments/start.json',lambda v:v['sources'][0].update(verified_on=None))
        self.expect('CITED_SOURCE_NOT_FETCH_VERIFIED:')

    def test_missing_source_support(self):
        self.edit('preparedness/sources/register.json',lambda v:v['sources'][0].update(supports=''))
        self.expect('CITED_SOURCE_SUPPORT_MISSING:')

    def test_duplicate_fetched_records_hard_hold_even_if_same_url(self):
        self.edit('preparedness/sources/fragments/shelter.json',
                  lambda v:v['sources'].append(entry('source-b',supports='Different attribution')))
        r=self.expect('DUPLICATE_FETCH_VERIFIED_SOURCE_REQUIRES_ADJUDICATION:source-b')
        self.assertEqual(r['duplicate_fetch_verified_ids'],['source-b'])

    def test_duplicate_fetched_records_with_different_url(self):
        self.edit('preparedness/sources/fragments/shelter.json',
                  lambda v:v['sources'].append(entry('source-b',url='https://www.cdc.gov/other')))
        self.expect('FETCH_VERIFIED_URL_CONFLICT:source-b')

    def test_register_upgrade_url_drift(self):
        self.edit('preparedness/sources/register.json',
                  lambda v:v['sources'][1].update(url='https://www.cdc.gov/changed'))
        self.expect('UPGRADE_URL_DRIFT_REQUIRES_REVIEW:source-b')

    def test_duplicate_in_single_fragment(self):
        self.edit('preparedness/sources/fragments/start.json',
                  lambda v:v['sources'].append(dict(v['sources'][0])))
        self.expect('DUPLICATE_ID_IN_SOURCE_FILE:')

    def test_invalid_source_date(self):
        self.edit('preparedness/sources/fragments/start.json',
                  lambda v:v['sources'][0].update(verified_on='2026-02-30'))
        self.expect('SOURCE_FETCH_DATE_INVALID:')

    def test_future_source_date(self):
        self.edit('preparedness/sources/fragments/start.json',
                  lambda v:v['sources'][0].update(verified_on='2035-01-01'))
        self.expect('SOURCE_FUTURE_FETCH_DATE:')

    def test_predecessor_drift_detected(self):
        (self.root/r311.PREDECESSOR).write_text('changed')
        self.expect('R310_PREDECESSOR_MISSING_OR_CHANGED')

    def test_taxonomy_drift_detected(self):
        (self.root/r310.TAXONOMY).write_text('{}')
        self.expect('INHERITED_R310:TAXONOMY_MISSING_OR_CHANGED')

    def test_tool_citation_crosswalk_preserves_slug(self):
        r=self.run_audit()
        self.assertEqual(set(x['tool_slug'] for x in r['crosswalk_entries']),set(r310.SLUGS))
        self.assertEqual(len([x for x in r['crosswalk_entries'] if x['source_id']=='source-b']),6)

    def test_nonobject_record_does_not_crash(self):
        self.edit('preparedness/sources/fragments/food.json', lambda v:v['sources'].append('invalid'))
        self.expect('SOURCE_RECORD_NOT_OBJECT:')

    def test_source_url_validation_rejects_userinfo(self):
        self.assertFalse(r311.source_url('https://token@example.com/secret'))

    def test_source_url_allows_https_standard(self):
        self.assertTrue(r311.source_url('https://www.ready.gov/plan'))

    def test_source_url_rejects_untrusted_schemes(self):
        for u in ('http://example.com','javascript:alert(1)','data:text/html,hello',
                  'file:///etc/passwd','//example.com','https://u:p@host/','https://example.invalid/x'):
            with self.subTest(u=u):self.assertFalse(r311.source_url(u))


# Named and isolated adversarial regressions; each fixture gets a new temp tree.
for i, source_path in enumerate(r311.SOURCES):
    def missing(self, p=source_path):
        self.paths[p].unlink()
        self.expect('SOURCE_FILE_MISSING_OR_SYMLINK:'+p)
    setattr(CrosswalkTests,f'test_missing_source_file_{i}',missing)
    def modified(self, p=source_path):
        self.paths[p].write_bytes(self.paths[p].read_bytes()+b' ')
        self.expect('SOURCE_FILE_GIT_BLOB_DRIFT:'+p)
    setattr(CrosswalkTests,f'test_modified_source_bytes_{i}',modified)
    def invalid_json(self, p=source_path):
        self.paths[p].write_text('{',encoding='utf-8')
        self.expect('SOURCE_FILE_INVALID_JSON:'+p)
    setattr(CrosswalkTests,f'test_invalid_json_source_{i}',invalid_json)
    def bad_layout(self, p=source_path):
        self.paths[p].write_text('{"sources":{}}',encoding='utf-8')
        self.expect('SOURCE_FILE_INVALID_SCHEMA:'+p)
    setattr(CrosswalkTests,f'test_bad_source_layout_{i}',bad_layout)
for i, slug in enumerate(r310.SLUGS):
    def wrong_use(self, s=slug):
        p=self.tools[s][1]; d=json.loads(p.read_text());d['source_use']={'missing-source':'unverified'}
        p.write_text(json.dumps(d));self.expect('CITED_SOURCE_NOT_REGISTERED:'+s)
    setattr(CrosswalkTests,f'test_missing_source_id_tool_{i}',wrong_use)
    def missing_tool(self, s=slug):
        self.tools[s][1].unlink();self.expect('INHERITED_R310:SOURCE_MISSING_OR_SYMLINK:')
    setattr(CrosswalkTests,f'test_missing_tool_metadata_{i}',missing_tool)
    def drift_tool(self, s=slug):
        p=self.tools[s][0];p.write_text(p.read_text()+'<!-- added -->')
        self.expect('INHERITED_R310:SOURCE_BLOB_CHANGED:')
    setattr(CrosswalkTests,f'test_changed_tool_body_{i}',drift_tool)
for i, url in enumerate(('ftp://host/file','http://www.ready.gov','javascript:void(0)',
                         'https://evil.invalid/','https://user@host/path',
                         'https://example.com/white space')):
    def badurl(self, u=url):
        self.edit('preparedness/sources/register.json',
                  lambda v:v['sources'][0].update(url=u))
        self.expect('SOURCE_URL_INVALID:')
    setattr(CrosswalkTests,f'test_bad_source_url_{i}',badurl)

if __name__=='__main__':
    unittest.main()
