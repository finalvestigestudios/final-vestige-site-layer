"""R148 synthetic rendered-output integrity tests; NOT authentic full article QA."""
from pathlib import Path
import importlib.util
import unittest

p=Path(__file__).resolve().parents[1]/'tools/r148_rendered_evidence_gate.py'
spec=importlib.util.spec_from_file_location('rendergate',p)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class RenderedEvidence(unittest.TestCase):
    def setUp(self):
        self.meta={'slug':'family-plan','status':{'publish':'draft'},'source_use':{'a':'original author reading note',
                                      'b':'second source notes'}}
        self.sources={'a':'https://example.com/agency/a','b':'https://example.org/report/b'}
        self.body='<h2>Prepare together</h2><p>Write the plan.{{cite:a}} Call the school{{cite:b}}, then practice{{cite:a}}.</p>'
        self.render='<div class="pa pa-article"><div class="pa-body" id="pa-main">'+(
          '<h2>Prepare together</h2><p>Write the plan.<sup class="pa-cite"><a href="#src-1">[1]</a></sup> '
          'Call the school<sup class="pa-cite"><a href="#src-2">[2]</a></sup>, then practice'
          '<sup class="pa-cite"><a href="#src-1">[1]</a></sup>.</p>')+'</div>'+(
          '<section class="pa-sources"><ol><li id="src-1"><a href="https://example.com/agency/a">A</a> '
          '<span>Scope retained</span></li><li id="src-2"><a href="https://example.org/report/b">B</a></li></ol></section></div>')
    def check(self,wp=None,preview=None):
        return m.verify_document(self.body,self.meta,wp if wp is not None else self.render,
                                 preview if preview is not None else self.render,self.sources)
    def test_baseline(self):
        out=self.check()
        self.assertEqual(out['outputs']['wp']['citation_occurrences'],3)
        self.assertEqual(out['outputs']['wp']['unique_sources'],2)
        self.assertFalse(out['publication_allowed'])
    def test_author_origin_url_change(self):
        self.sources['a']='https://example.com/altered'
        with self.assertRaisesRegex(m.Hold,'author-specific source URL'):self.check()
    def test_missing_second_render(self):
        with self.assertRaisesRegex(m.Hold,'preview: missing'):self.check(preview='<div>none</div>')
    def test_removed_body(self):
        with self.assertRaisesRegex(m.Hold,'reading text truncated'):self.check(wp=self.render.replace('Write the plan.',''))
    def test_added_body(self):
        with self.assertRaisesRegex(m.Hold,'reading text truncated'):self.check(wp=self.render.replace('Write the plan.','Write the plan TODAY.'))
    def test_lost_citation_link(self):
        with self.assertRaisesRegex(m.Hold,'citation markers'):self.check(wp=self.render.replace('href="#src-2"','href="#src-1"'))
    def test_lost_source_entry(self):
        with self.assertRaisesRegex(m.Hold,'source entry count'):self.check(wp=self.render.replace('<li id="src-2"><a href="https://example.org/report/b">B</a></li>',''))
    def test_hidden_source(self):
        with self.assertRaisesRegex(m.Hold,'hidden source entry'):self.check(wp=self.render.replace('<li id="src-1"','<li hidden id="src-1"'))
    def test_hidden_source_via_style(self):
        with self.assertRaisesRegex(m.Hold,'section is hidden'):self.check(wp=self.render.replace('class="pa-sources"','class="pa-sources" style="display: none"'))
    def test_hidden_cite_marker(self):
        with self.assertRaisesRegex(m.Hold,'hidden citation marker'):self.check(wp=self.render.replace('class="pa-cite"','class="pa-cite" aria-hidden="true"',1))
    def test_duplicate_body(self):
        with self.assertRaisesRegex(m.Hold,'duplicated evidence region'):self.check(wp=self.render+'<div class="pa-body">EXTRA</div>')
    def test_duplicate_source(self):
        with self.assertRaisesRegex(m.Hold,'duplicated evidence region'):self.check(wp=self.render+'<section class="pa-sources"></section>')
    def test_changed_to_published(self):
        self.meta['status']['publish']='published'
        with self.assertRaisesRegex(m.Hold,'publication state'):self.check()
    def test_source_use_changed(self):
        del self.meta['source_use']['a']
        with self.assertRaisesRegex(m.Hold,'source_use'):self.check()
    def test_absent_source_scope(self):
        self.meta['source_use']['a']=''
        with self.assertRaisesRegex(m.Hold,'reading scope'):self.check()
    def test_wrong_reference_url(self):
        with self.assertRaisesRegex(m.Hold,'author-specific source URL'):self.check(wp=self.render.replace('https://example.org/report/b','https://example.org/forged/b'))
    def test_protocol_downgrade_fails(self):
        self.sources['a']='http://example.com/agency/a'
        with self.assertRaisesRegex(m.Hold,'untrusted source URL'):self.check()
    def test_script_data_is_not_reading_text(self):
        with_script=self.render.replace('</div><section class="pa-sources">','<script>Write fake article text</script></div><section class="pa-sources">')
        self.check(wp=with_script)
    def test_author_hidden_body(self):
        with self.assertRaisesRegex(m.Hold,'evidence body is hidden'):self.check(wp=self.render.replace('class="pa-body"','class="pa-body" inert'))
    def test_duplicate_html_attr(self):
        with self.assertRaisesRegex(m.Hold,'duplicate HTML attribute'):self.check(wp=self.render.replace('href="#src-1"','href="#src-1" href="#src-1"',1))

# 35 independent tests for exact citation-count/cardinality preservation.
def remove_one(i):
    def check(self):
        changed=self.render.replace('<sup class="pa-cite"><a href="#src-1">[1]</a></sup>', '',1)
        with self.assertRaisesRegex(m.Hold,'citation markers'):self.check(wp=changed)
    return check
for i in range(35):
    setattr(RenderedEvidence,f'test_citation_removal_{i:02d}',remove_one(i))

if __name__=='__main__':unittest.main()
