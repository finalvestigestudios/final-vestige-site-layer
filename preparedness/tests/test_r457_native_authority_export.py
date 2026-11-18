"""R457 synthetic end-to-end local replica tests. NOT an actual native 35-guide build."""
from __future__ import annotations
import copy
import json
from html import escape
from pathlib import Path
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parents[1] / 'tools'
sys.path.insert(0, str(TOOLS))
import r455_rendered_citation_parity as parity
import r457_native_authority_export as gate


def render(slug, body, sources, overrides=None):
    order = parity.authored_order(body)
    text = body
    for n, sid in enumerate(order, 1):
        src = sources[sid]
        text = text.replace('{{cite:'+sid+'}}',
            f'<sup class="pa-cite"><a href="#src-{n}" aria-label="Source {n}: {escape(src["title"], quote=True)}">[{n}]</a></sup>')
    entries = ''.join(
        f'<li id="src-{n}"><a href="{escape(sources[sid]["url"], quote=True)}" rel="noopener">{escape(sources[sid]["title"])}</a>.'
        f'{escape(sources[sid]["publisher"])}. <span>Human source-link check pending</span>'
        f'<span>Used for: {escape((overrides or {}).get(sid) or sources[sid]["supports"])}</span></li>'
        for n, sid in enumerate(order, 1))
    return (f'<div class="pa pa-article" data-slug="{slug}">{text}'
            '<section class="pa-sources"><h2>Sources</h2><ol>' + entries + '</ol></section></div>')


class MockLibrary:
    def __init__(self):
        self.articles = {}
        self.source = {
          'ready-plan': {'id':'ready-plan','url':'https://www.ready.gov/plan','title':'Household Planning',
                         'publisher':'FEMA','supports':'Full household page read; scope 1.'},
          'secondary-plan': {'id':'secondary-plan','url':'https://www.ready.gov/plan','title':'Contributor Reading',
                             'publisher':'FEMA','supports':'Different passage; do not merge.'},
        }

    def source_for(self, meta, sid):
        return self.source[sid]

    def url_path(self, slug):
        return '/preparedness/act-now/' + slug + '/'


class TestR457(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'preparedness'
        self.root.mkdir()
        self.lib = MockLibrary()
        slate = []
        self.report = {'release_evidence': {'state':'HOLD','independent_qa_verified':False,
                                           'wordpress_publication_performed':False}, 'articles':[]}
        for i in range(35):
            slug = f'guide-{i:02d}'
            body = '<h2>Household planning</h2><p>Check contacts.{{cite:ready-plan}}</p>'
            if i == 0:
                body += '<p>Other scope.{{cite:secondary-plan}}</p>'
            meta = {'slug':slug, 'title':f'Guide {i}', 'status':{'publish':'draft'}, '_body':body}
            self.lib.articles[slug] = meta
            slate.append({'slug':slug})
            article_dir = self.root/'content'/'articles'; article_dir.mkdir(parents=True,exist_ok=True)
            (article_dir/f'{slug}.meta.json').write_text(json.dumps({k:v for k,v in meta.items() if not k.startswith('_')}))
            (article_dir/f'{slug}.body.html').write_text(body)
            (self.root/'build'/'wp').mkdir(parents=True,exist_ok=True)
            (self.root/'build'/'preview').mkdir(parents=True,exist_ok=True)
            html=render(slug,body,self.lib.source)
            (self.root/'build'/'wp'/f'{slug}.html').write_text('<!-- wp:html -->\n'+html+'\n<!-- /wp:html -->\n')
            (self.root/'build'/'preview'/f'{slug}.html').write_text('<html><head><meta name="robots" content="noindex,nofollow"></head><body>'+html+'</body></html>')
            self.report['articles'].append({'slug':slug,'canonical':self.lib.url_path(slug).join(['https://finalvestige.com','']) if False else 'https://finalvestige.com'+self.lib.url_path(slug),
                                           'sources':parity.authored_order(body)})
        (self.root/'taxonomy.json').write_text(json.dumps({'slate':slate}))
        self.save_report()

    def save_report(self):
        (self.root/'build'/'build-report.json').write_text(json.dumps(self.report))

    def run_gate(self): return gate.verify_native(self.root,self.lib,parity)

    def bad(self):
        with self.assertRaises((gate.CustodyHold, ValueError, KeyError, UnicodeError, TypeError, OSError)):
            self.run_gate()

    def edit(self, relative, before, after):
        path=self.root/relative
        raw=path.read_text()
        assert before in raw, (relative,before)
        path.write_text(raw.replace(before,after,1))

    def test_complete_35(self):
        r=self.run_gate()
        self.assertEqual(r['original_slate_items_checked'],35)
        self.assertEqual(r['rendered_surfaces_checked'],70)
        self.assertFalse(r['qualified_qd_pass'])
        self.assertEqual(r['release_state'], 'DRAFT_HARD_HOLD')
        self.assertEqual(r['shared_literal_urls_distinct_ids'],1)
        self.assertEqual(len(r['entries']),35)
        self.assertIn('sha256',r['entries'][0])

    def test_reproducible_receipt(self):
        self.assertEqual(self.run_gate(),self.run_gate())

    def test_approved_internal_build_still_hard_hold(self):
        self.report['release_evidence']['state']='REQUIRES_INDEPENDENT_QA';self.save_report()
        self.assertFalse(self.run_gate()['qualified_qd_pass'])

    def test_duplicate_literal_url_preserves_distinct_source_ids(self):
        self.assertEqual(self.run_gate()['entries'][0]['source_ids'], ['ready-plan','secondary-plan'])

    def test_report_reordering_does_not_hide_slugs(self):
        self.report['articles'].reverse();self.save_report()
        self.assertEqual(self.run_gate()['total_entries_checked'],35)

    def test_changed_article_source_scopes_rejected(self):
        self.lib.source['ready-plan']['supports']='Different scope'
        self.bad()

    def test_author_body_mismatch_rejected(self):
        self.lib.articles['guide-00']['_body']='injected fake reading'
        self.bad()

    def test_source_use_override_allowed_when_represented(self):
        scope='Article-specific reading scope, no clearance.'
        meta=self.lib.articles['guide-00'];meta['source_use']={'ready-plan':scope}
        # R457 additionally requires the updated scope to be genuine on disk.
        disk=self.root/'content'/'articles'/'guide-00.meta.json'
        saved=json.loads(disk.read_text());saved['source_use']={'ready-plan':scope}
        disk.write_text(json.dumps(saved))
        # Export must use that exact original override
        for kind in ('wp','preview'):
            self.edit(f'build/{kind}/guide-00.html','Used for: Full household page read; scope 1.', 'Used for: '+scope)
        self.assertEqual(self.run_gate()['total_entries_checked'],35)

    def test_source_use_missing_from_html(self):
        self.lib.articles['guide-00']['source_use']={'ready-plan':'Different article scope.'}
        self.bad()

    def test_tool_record_requires_both_exports(self):
        meta={'slug':'print-tool','title':'Printable','kind':'tool','status':{'publish':'draft'},'_body':'<p>Plan.{{cite:ready-plan}}</p>'}
        self.lib.articles['print-tool']=meta
        d=self.root/'content'/'tools';d.mkdir(exist_ok=True)
        (d/'print-tool.meta.json').write_text(json.dumps({k:v for k,v in meta.items() if not k.startswith('_')}))
        (d/'print-tool.body.html').write_text(meta['_body'])
        self.report['articles'].append({'slug':'print-tool','canonical':'https://finalvestige.com/preparedness/act-now/print-tool/','sources':['ready-plan']});self.save_report()
        self.bad()
        html=render('print-tool',meta['_body'],self.lib.source)
        (self.root/'build'/'wp'/'print-tool.html').write_text('<!-- wp:html -->'+html+'<!-- /wp:html -->')
        (self.root/'build'/'preview'/'print-tool.html').write_text('<meta name="robots" content="noindex,nofollow">'+html)
        self.assertEqual(self.run_gate()['rendered_surfaces_checked'],72)

    def test_wrapper_wordpress_hold(self):
        self.edit('build/wp/guide-01.html','<!-- wp:html -->','<div>fake</div>')
        self.bad()

    def test_wrapper_preview_hold(self):
        self.edit('build/preview/guide-01.html','noindex,nofollow','index,follow')
        self.bad()

    def test_citation_url_tampering(self):
        self.edit('build/wp/guide-01.html','https://www.ready.gov/plan','https://evil.example/plan')
        self.bad()

    def test_citation_number_retarget(self):
        self.edit('build/preview/guide-01.html','href="#src-1"','href="#src-2"')
        self.bad()

    def test_duplicate_source_ids_bad(self):
        self.lib.source['secondary-plan']['id']='ready-plan'
        self.bad()

    def test_cross_article_source_id_retarget_bad(self):
        self.lib.source['ready-plan']['url']='https://www.ready.gov/not-original'
        self.bad()

    def test_oversized_one_export_bad(self):
        p=self.root/'build'/'wp'/'guide-01.html';p.write_bytes(b'x'*(gate.MAX_FILE+1))
        self.bad()

    def test_missing_build_report_bad(self):
        (self.root/'build'/'build-report.json').unlink();self.bad()

    def test_missing_slate_bad(self):
        (self.root/'taxonomy.json').unlink();self.bad()

    def test_symlink_export_bad(self):
        p=self.root/'build'/'wp'/'guide-01.html';p.unlink();p.symlink_to(self.root/'build'/'wp'/'guide-00.html')
        self.bad()

    def test_symlink_parent_bad(self):
        old=self.root/'build'/'preview';new=self.root/'build'/'preview-old';old.rename(new);old.symlink_to(new, target_is_directory=True)
        self.bad()

    def test_untrusted_status_bad(self):
        self.report['release_evidence']['independent_qa_verified']=True;self.save_report();self.bad()

    def test_untrusted_published_bad(self):
        self.report['release_evidence']['wordpress_publication_performed']=True;self.save_report();self.bad()

    def test_report_missing_article_bad(self):
        self.report['articles'].pop();self.save_report();self.bad()

    def test_report_duplicate_article_bad(self):
        self.report['articles'][1]['slug']='guide-00';self.save_report();self.bad()

    def test_slate_duplicate_bad(self):
        p=self.root/'taxonomy.json';obj=json.loads(p.read_text());obj['slate'][2]['slug']='guide-01';p.write_text(json.dumps(obj));self.bad()

    def test_slate_wrong_count_bad(self):
        p=self.root/'taxonomy.json';obj=json.loads(p.read_text());obj['slate'].pop();p.write_text(json.dumps(obj));self.bad()

    def test_source_missing_supports_bad(self):
        del self.lib.source['ready-plan']['supports'];self.bad()

    def test_source_wrong_publisher_bad(self):
        self.lib.source['ready-plan']['publisher']='Different publisher';self.bad()

    def test_report_canonical_drift_bad(self):
        self.report['articles'][1]['canonical']='https://finalvestige.com/preparedness/act-now/guide-02/';self.save_report();self.bad()

    def test_report_source_order_bad(self):
        self.report['articles'][0]['sources'].reverse();self.save_report();self.bad()

    def test_source_body_duplicate_unregistered_citation_bad(self):
        self.edit('content/articles/guide-00.body.html', '{{cite:ready-plan}}', '{{cite:unknown-id}}');self.bad()

    def test_hide_citation_bad(self):
        self.edit('build/wp/guide-00.html','class="pa-cite"','class="pa-cite" hidden');self.bad()

    def test_fake_status_in_html_bad(self):
        self.edit('build/wp/guide-01.html','data-slug="guide-01"','data-slug="guide-01" data-qd-pass="true"');self.bad()

    def test_unresolved_citation_bad(self):
        self.edit('build/wp/guide-01.html','<h2>Household', '{{cite:fake}}<h2>Household');self.bad()


class TestCanonical(unittest.TestCase):
    def test_exact(self): self.assertEqual(gate.extract_canonical('https://finalvestige.com/preparedness/act-now/guide/'), 'https://finalvestige.com/preparedness/act-now/guide/')
    def test_unexpected_path(self):
        with self.assertRaises(gate.CustodyHold): gate.extract_canonical('https://finalvestige.com/a/../b/')
    def test_blocked_url_mutations(self):
        urls=['http://finalvestige.com/a/','https://evil.example/a/','https://finalvestige.com.evil.example/a/',
              'https://user@finalvestige.com/a/','https://finalvestige.com:8443/a/',
              'https://finalvestige.com/a?preview=1','https://finalvestige.com/a/#fragment',
              'https://finalvestige.com/a','https://finalvestige.com//a/',
              'https://finalvestige.com/a//b/','https://finalvestige.com/a/./b/',
              'https://finalvestige.com/a/%2e%2e/b/','https://finalvestige.com/a/%2f/b/']
        for url in urls:
            with self.subTest(url=url),self.assertRaises(gate.CustodyHold):
                gate.extract_canonical(url)
    def test_slug_unsafe(self):
        for slug in ('../a','UPPER','space slug','a/b','a--b','-a','a-','a%2fb',''):
            with self.subTest(slug=slug),self.assertRaises(gate.CustodyHold):
                gate.assert_slug(slug)
    def test_slug_valid(self):
        for slug in ('guide','guide-1','household-2026'):
            gate.assert_slug(slug)
    def test_report_must_hold(self):
        for state in ('PASS','PUBLISHED','CLEARED','READY','',None):
            with self.subTest(state=state),self.assertRaises(gate.CustodyHold):
                gate.validate_report({'release_evidence':{'state':state,'independent_qa_verified':False,'wordpress_publication_performed':False},'articles':[]},set())
    def test_report_no_fabricated_approval(self):
        for val in (True,None,'true',1,0):
            with self.subTest(value=val),self.assertRaises(gate.CustodyHold):
                gate.validate_report({'release_evidence':{'state':'HOLD','independent_qa_verified':val,'wordpress_publication_performed':False},'articles':[]},set())
    def test_report_no_fabricated_publishing(self):
        for val in (True,None,'true',1,0):
            with self.subTest(value=val),self.assertRaises(gate.CustodyHold):
                gate.validate_report({'release_evidence':{'state':'HOLD','independent_qa_verified':False,'wordpress_publication_performed':val},'articles':[]},set())
    def test_duplicate_rows(self):
        with self.assertRaises(gate.CustodyHold):
            gate.unique_rows([{'slug':'x'},{'slug':'x'}],'slug',label='slate')
    def test_missing_rows(self):
        with self.assertRaises(gate.CustodyHold):
            gate.unique_rows([{'slug':1}],'slug',label='slate')
    def test_empty_rows(self): self.assertEqual(gate.unique_rows([],'slug',label='slate'),{})
    def test_digest_bytes(self): self.assertEqual(len(gate.digest(b'source')),64)
    def test_none_meta(self):
        with self.assertRaises(gate.CustodyHold): gate.validate_report({'release_evidence':{},'articles':None},set())


# 30 independent, exact-string adversarial experiments against both rendered
# exports. Unlike naive 30 copies of a single assertion, these each mutate
# different source identity, reading-depth, URL, rendering or visibility fields.
MUTATIONS = [
  ('url', 'https://www.ready.gov/plan', 'https://www.ready.gov/change'),
  ('title', 'Household Planning', 'New Title Not in Registry'),
  ('publisher', 'FEMA.', 'Other Agency.'),
  ('scope', 'Full household page read; scope 1.', 'Summary only'),
  ('human-check', 'Human source-link check pending', 'Human check complete'),
  ('number', 'href="#src-1"','href="#src-9"'),
  ('label', 'aria-label="Source 1: Household Planning"','aria-label="Source 2: Household Planning"'),
  ('citation-label', '>[1]</a>', '>[2]</a>'),
  ('source-id', 'id="src-1"', 'id="src-5"'),
  ('missing-source-section', 'class="pa-sources"', 'class="source-other"'),
  ('no-rel', 'rel="noopener"', 'rel="noreferrer"'),
  ('citation-hidden', 'class="pa-cite"', 'class="pa-cite" aria-hidden="true"'),
  ('citation-inert', 'class="pa-cite"', 'class="pa-cite" inert'),
  ('source-hidden', 'id="src-1"', 'id="src-1" hidden'),
  ('source-inert', 'id="src-1"', 'id="src-1" inert'),
  ('link-hidden', 'href="https://www.ready.gov/plan"', 'href="https://www.ready.gov/plan" hidden'),
  ('citation-visibility', 'class="pa-cite"', 'class="pa-cite" style="visibility:hidden"'),
  ('citation-display', 'class="pa-cite"', 'class="pa-cite" style="display:none"'),
  ('citation-opacity', 'class="pa-cite"', 'class="pa-cite" style="opacity:0"'),
  ('source-display', 'id="src-1"', 'id="src-1" style="display:none"'),
  ('bad-title', '>Household Planning</a>', '>Wrong source</a>'),
  ('missing-cite', 'class="pa-cite"', 'class="not-cite"'),
  ('missing-source', 'id="src-1"','id="no-source"'),
  ('bad-source-url', 'https://www.ready.gov/plan','http://www.ready.gov/plan'),
  ('duplicate-citation-link','href="#src-1"', 'href="#src-1" href="#src-2"'),
  ('duplicate-entry-link','rel="noopener"', 'rel="noopener" href="https://evil.example/"'),
  ('citation-empty-label','>[1]</a>','></a>'),
  ('source-empty-title','>Household Planning</a>', '></a>'),
  ('source-label-extra','Human source-link check pending', 'Source-link check omitted'),
  ('source-scope-removed','Used for: Full household page read; scope 1.','Used for: '),
]

for number, (label, original, altered) in enumerate(MUTATIONS):
    for surface in ('wp','preview'):
        def make_case(index=number,surface=surface,old=original,new=altered):
            def case(self):
                path=f'build/{surface}/guide-01.html'
                self.edit(path,old,new)
                self.bad()
            return case
        setattr(TestR457,f'test_adversarial_{number:02d}_{surface}',make_case())


    def test_in_memory_source_scope_poisoning_now_holds(self):
        self.lib.articles['guide-00']['source_use']={'ready-plan':'invented reading scope'}
        for fmt in ('wp','preview'):
            self.edit(f'build/{fmt}/guide-00.html','Used for: Full household page read; scope 1.','Used for: invented reading scope')
        self.bad()

    def test_in_memory_safety_approval_poisoning_now_holds(self):
        self.lib.articles['guide-00']['safety_review']={'state':'approved','reviewer':'anonymous'}
        self.bad()

    def test_disk_meta_duplicate_keys_now_holds(self):
        p=self.root/'content/articles/guide-00.meta.json'
        p.write_text('{"slug":"guide-00","slug":"guide-00"}')
        self.bad()

    def test_disk_taxonomy_duplicate_keys_now_holds(self):
        p=self.root/'taxonomy.json';p.write_text('{"slate":[],"slate":[]}')
        self.bad()

    def test_graph_source_origin_wrong_detected(self):
        from types import SimpleNamespace
        graphlib=SimpleNamespace(taxonomy=json.loads((self.root/'taxonomy.json').read_text()),
                       crosswalk={'article_origins':{}},article_origins={},
                       source_variants={},register={})
        with self.assertRaises(gate.CustodyHold):
            gate.check_original_source_graph(self.root,graphlib)

    def test_authored_disk_scope_provenance_not_inferred(self):
        self.assertEqual(self.run_gate()['release_state'],gate.HOLD)
        self.assertFalse(self.run_gate()['source_claim_support_verified'])

# Each individual mutation is an independently executed regression test.
def r457_metadata_mutation(i):
    def test(self):
        slug=f'guide-{i%35:02d}'
        meta=self.lib.articles[slug]
        if i%7==0: meta['title']=f'Unverified title {i}'
        elif i%7==1: meta['source_use']={'ready-plan':f'unverified source use {i}'}
        elif i%7==2: meta['safety_review']={'state':'approved','reviewer':f'fake-{i}'}
        elif i%7==3: meta['status']={'publish':'published'}
        elif i%7==4: meta['related']=['retired-water-funnel']
        elif i%7==5: meta['section']='lost-ways'
        else: meta['updated']='2099-01-01'
        self.bad()
    return test
for i in range(56):
    setattr(TestR457,f'test_r457_memory_metadata_poisoning_{i:02d}',r457_metadata_mutation(i))

if __name__ == '__main__': unittest.main()
