"""R304 review-only synthetic controls; no actual WordPress or source edits."""
import importlib.util
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT=Path(__file__).resolve().parents[2]
p=ROOT/'preparedness/tools/r303_inline_semantic_aria_hold.py'
spec=importlib.util.spec_from_file_location('r304_patched_r303',p)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
prev=mod.load_predecessor(ROOT)

def pair(body):
    source='<section><h2>Reunification</h2><p>'+body+'{{cite:agency-one}}</p></section>'
    export='<div id="pa-main"><section><h2>Reunification</h2><p>'+body+'<sup class="pa-cite"><a href="#src-1">[1]</a></sup></p></section></div>'
    return source,export

def check(body):return mod.inline_compare(*pair(body),prev)

class Boundary(unittest.TestCase):
    def test_wbr(self):self.assertEqual(check('A<wbr>B'),[])
    def test_wbr_selfclosed(self):self.assertEqual(check('A<wbr/>B'),[])
    def test_wbr_mixed(self):self.assertEqual(check('A<wbr/><wbr>B'),[])
    def test_wbr_equivalent(self):
        a,b=pair('A<wbr/>B')
        self.assertEqual(mod.inline_compare(a,b.replace('<wbr/>','<wbr>'),prev),[])
    def test_wbr_explicit_close(self):self.assertIn('INLINE_VOID_CLOSED:wbr',check('A<wbr/></wbr>B'))
    def test_wbr_removed(self):
        a,b=pair('A<wbr/>B')
        self.assertIn('INLINE_MARKUP_OR_ARIA_DRIFT',mod.inline_compare(a,b.replace('<wbr/>',''),prev))
    def test_wbr_added(self):
        a,b=pair('A<wbr/>B')
        self.assertIn('INLINE_MARKUP_OR_ARIA_DRIFT',mod.inline_compare(a,b.replace('<wbr/>','<wbr/><wbr>'),prev))
    def test_wbr_attribute_drift(self):
        a,b=pair('A<wbr id="a"/>B')
        self.assertIn('INLINE_MARKUP_OR_ARIA_DRIFT',mod.inline_compare(a,b.replace('id="a"','id="b"'),prev))
    def test_generated_sup_missing_class_value_no_crash(self):
        a,b=pair('Plan')
        self.assertTrue(mod.inline_compare(a,b.replace('class="pa-cite"','class'),prev))
    def test_nullable_aria_rejected(self):self.assertIn('INLINE_VALUELESS_ATTRIBUTE:span:aria-label',check('<span aria-label>Plan</span>'))
    def test_duplicate_aria_rejected(self):self.assertIn('INLINE_DUPLICATE_ATTRIBUTE:span',check('<span aria-label="a" aria-label="b">Plan</span>'))
    def test_hidden_boolean_allowed(self):self.assertEqual(check('<span hidden>Plan</span>'),[])
    def test_inert_boolean_allowed(self):self.assertEqual(check('<span inert>Plan</span>'),[])
    def test_itemscope_boolean_allowed(self):self.assertEqual(check('<span itemscope>Plan</span>'),[])
    def test_export_altered_warning_rejected(self):
        a,b=pair('<strong>Warning</strong>')
        self.assertIn('INLINE_MARKUP_OR_ARIA_DRIFT',mod.inline_compare(a,b.replace('<strong>','').replace('</strong>',''),prev))
    def test_no_authentic_checkout_remains_hard_hold(self):
        with TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError,'PINNED_R302_PREDECESSOR_MISSING_OR_SYMLINK'):
                mod.run(Path(td))

class Matrix(unittest.TestCase):pass
TAGS=('strong','em','span','abbr','mark','time','small','b','i','cite','kbd','samp','var','sub','u','ins','del','bdi','data','q')
for i,tag in enumerate(TAGS):
    def absent(self,tag=tag):
        self.assertIn('INLINE_VALUELESS_ATTRIBUTE:'+tag+':aria-label',check(f'<{tag} aria-label>Text</{tag}>'))
    def repeated(self,tag=tag):
        self.assertIn('INLINE_DUPLICATE_ATTRIBUTE:'+tag,check(f'<{tag} role="a" role="b">Text</{tag}>'))
    def changed(self,tag=tag,i=i):
        a,b=pair(f'<{tag} aria-label="Source {i}">Text</{tag}>')
        self.assertIn('INLINE_MARKUP_OR_ARIA_DRIFT',mod.inline_compare(a,b.replace(f'Source {i}',f'Destination {i}'),prev))
    def softbreak(self,tag=tag):self.assertEqual(check(f'<{tag}>A<wbr/>B</{tag}>'),[])
    for suffix,fn in [('missing',absent),('duplicate',repeated),('drift',changed),('softbreak',softbreak)]:
        setattr(Matrix,f'test_{i:02d}_{suffix}',fn)

if __name__=='__main__':unittest.main()
