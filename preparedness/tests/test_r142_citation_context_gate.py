"""R142 isolated adversarial tests; never a substitute for source/safety QD."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import json

TOOL = Path(__file__).resolve().parents[1]/'tools'/'r142_citation_context_gate.py'
spec=importlib.util.spec_from_file_location('r142_gate',TOOL)
assert spec and spec.loader
m=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=m
spec.loader.exec_module(m)

def parse(html: str):
    return m.contexts(html.encode('utf-8'))

class PassageTests(unittest.TestCase):
    def test_simple(self):
        r=parse('<p>Water matters. {{cite:ready-water}}</p>')
        self.assertEqual(r[0]['id'],'ready-water')
        self.assertEqual(r[0]['excerpt'],'water matters.')
    def test_semantics_changed_same_id_and_count(self):
        a=parse('<p>Never use this method.{{cite:source-one}}</p>')
        b=parse('<p>Use this method.{{cite:source-one}}</p>')
        delta=m.compare_contexts(a,b)
        self.assertEqual((delta['lost_context_occurrences'],delta['added_context_occurrences']),(1,1))
    def test_identity_retarget_same_unchanged_text(self):
        a=parse('<li>Use official advice.{{cite:hist-food-nchfp-jerky}}</li>')
        b=parse('<li>Use official advice.{{cite:nchfp-jerky}}</li>')
        d=m.compare_contexts(a,b)
        self.assertEqual(d['changed_source_ids'],['hist-food-nchfp-jerky','nchfp-jerky'])
    def test_whitespace_canonical(self):
        a=parse('<p>Important  food <strong>safety</strong>.{{cite:fsis}}</p>')
        b=parse('<p>important food safety.{{cite:fsis}}</p>')
        self.assertEqual(m.compare_contexts(a,b)['lost_context_occurrences'],0)
    def test_nfc_unicode(self):
        a=parse('<p>Caf\u00e9 preparation{{cite:source}}</p>')
        b=parse('<p>Cafe\u0301 preparation{{cite:source}}</p>')
        self.assertEqual(m.compare_contexts(a,b)['added_context_occurrences'],0)
    def test_repeat_ids_preserved(self):
        r=parse('<p>Same passage{{cite:one}}{{cite:one}}</p>')
        self.assertEqual(len(r),2)
    def test_unsafe_unscoped(self):
        with self.assertRaises(ValueError):parse('<section>{{cite:abc}}</section>')
    def test_script_citation_not_counted_as_visible(self):
        with self.assertRaises(ValueError):parse('<script>{{cite:abc}}</script>')
    def test_invalid_source_name(self):
        with self.assertRaises(ValueError):parse('<p>x {{cite:bad.id}}</p>')
    def test_unbalanced_markup(self):
        with self.assertRaises(ValueError):parse('<p>x {{cite:sid}}')
    def test_no_citation_passage(self):
        with self.assertRaises(ValueError):parse('<p>{{cite:sid}}</p>')
    def test_empty_article_yields_empty_context(self):
        self.assertEqual(parse('<p>No sources</p>'),[])
    def test_nested_inline_tags(self):
        self.assertEqual(parse('<li><strong>Strong</strong> note {{cite:nfpa}}</li>')[0]['excerpt'],'strong note')
    def test_real_article_uses_list(self):
        self.assertEqual(parse('<section><ol><li>Kit{{cite:fema}}</li></ol></section>')[0]['id'],'fema')
    def test_section_citations_are_not_silent(self):
        with self.assertRaises(ValueError):parse('<div>{{cite:fema}}<p>Another{{cite:nfpa}}</p></div>')
    def test_duplicate_context_occurrences(self):
        a=parse('<p>text{{cite:s}}</p><p>text{{cite:s}}</p>')
        b=parse('<p>text{{cite:s}}</p>')
        self.assertEqual(m.compare_contexts(a,b)['lost_context_occurrences'],1)
    def test_blocks_are_indexed(self):
        a=parse('<h2>Intro</h2><p>text{{cite:s}}</p><li>more{{cite:a}}</li>')
        self.assertEqual([x['block_index'] for x in a],[1,2])
    def test_author_scoped_ids_not_alias(self):
        a=parse('<p>same{{cite:a-jerky}}</p>')
        b=parse('<p>same{{cite:b-jerky}}</p>')
        self.assertEqual(len(m.compare_contexts(a,b)['changed_source_ids']),2)
    def test_output_cannot_mark_approval(self):
        r=m.compare_contexts(parse('<p>x{{cite:foo}}</p>'),parse('<p>y{{cite:foo}}</p>'))
        self.assertEqual(r['human_review'],'UNREVIEWED_REQUIRED')
        self.assertNotIn('approved',r)
    def test_prevent_missing_R141_tool(self):
        with self.assertRaises(ValueError):m._load_parent(Path('/path/not/existing.py'))
    def test_unicode_requires_utf8(self):
        with self.assertRaises(UnicodeError):m.contexts(b'\xff')
    def test_no_possible_long_citation_hidden_in_attrs(self):
        with self.assertRaises(ValueError):parse('<p title="{{cite:foo}}">no evidence</p>')
    def test_compare_has_excerpts(self):
        d=m.compare_contexts(parse('<p>Sample{{cite:a}}</p>'),[])
        self.assertEqual(d['old_only'][0]['excerpt'],'sample')
    def test_source_count_addition(self):
        d=m.compare_contexts(parse('<p>A{{cite:one}}</p>'),parse('<p>A{{cite:one}}{{cite:two}}</p>'))
        self.assertEqual(d['added_context_occurrences'],1)


def install_mutations():
    for i in range(14):
        for kind in ('text','id','absence'):
            def create(n,what):
                def test(self):
                    a=parse(f'<li>Important instruction {n}{{{{cite:source-{n}}}}}</li>')
                    if what=='text': b=parse(f'<li>Different instruction {n}{{{{cite:source-{n}}}}}</li>')
                    elif what=='id': b=parse(f'<li>Important instruction {n}{{{{cite:alt-{n}}}}}</li>')
                    else:b=parse(f'<li>Important instruction {n}</li>')
                    d=m.compare_contexts(a,b)
                    self.assertGreater(d['lost_context_occurrences'],0)
                    self.assertEqual(d['human_review'],'UNREVIEWED_REQUIRED')
                return test
            setattr(PassageTests,f'test_mutation_{i:02d}_{kind}',create(i,kind))
install_mutations()

if __name__=='__main__':unittest.main()
