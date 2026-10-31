"""Source regression guards for the unpublished Victory Point chronicle lens."""
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
class ChronicleLensTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chron = (ROOT/'chronicle.html').read_text(encoding='utf-8')
        cls.index = (ROOT/'index.html').read_text(encoding='utf-8')
        cls.toolbar = (ROOT/'chronicle-lens.html').read_text(encoding='utf-8')
        cls.style = (ROOT/'chronicle-lens.css').read_text(encoding='utf-8')
        cls.script = (ROOT/'chronicle-lens.js').read_text(encoding='utf-8')

    def test_same_toolbar_both_templates(self):
        for doc in (self.chron, self.index):
            self.assertEqual(doc.count('data-fv-chronicle-lens hidden'),1)
            self.assertIn(self.toolbar.strip(),doc)
            for mode in ('original','addition','both'):
                self.assertEqual(doc.count('data-fv-chronicle-view="'+mode+'"'),1)

    def test_historical_text_and_sources_preserved(self):
        for doc in (self.chron, self.index):
            for text in ('“All well.”','“Terror and Erebus were deserted”','25th April 1848','26 April 1848','1847-05-28'):
                self.assertIn(text,doc)
            for url in ('https://www.historymuseum.ca/blog/a-very-special-piece-of-paper','https://www.rmg.co.uk/collections/objects/rmgc-object-504898'):
                self.assertIn(url,doc)

    def test_no_js_has_two_entries_and_native_note(self):
        for doc in (self.chron,self.index):
            self.assertIn('class="fv-hf__chronicle-entry fv-hf__chronicle-entry--first"',doc)
            self.assertIn('class="fv-hf__chronicle-entry fv-hf__chronicle-entry--second"',doc)
            self.assertNotIn('class="fv-hf__chronicle-entry fv-hf__chronicle-entry--first" hidden',doc)
            self.assertNotIn('class="fv-hf__chronicle-entry fv-hf__chronicle-entry--second" hidden',doc)
            self.assertIn('<details>',doc)

    def test_deferred_javascript_only(self):
        self.assertIn('href="./chronicle-lens.css"',self.index)
        self.assertIn('src="./chronicle-lens.js" defer',self.index)
        self.assertIn('const restore = () =>',self.script)
        self.assertIn('catch (error)',self.script)
        self.assertIn("setView('both')",self.script)
        self.assertIn('ArrowRight',self.script)
        self.assertIn('aria-pressed',self.script)

    def test_hiding_requires_explicit_view_and_print_restores(self):
        for mode in ('original','addition'):
            self.assertIn('data-fv-chronicle-mode="'+mode+'"',self.style)
        self.assertIn('@media print',self.style)
        self.assertIn('@media(prefers-reduced-motion:reduce)',self.style)

    def test_no_new_vendor_or_external_media(self):
        combined=(self.toolbar+self.style+self.script).lower()
        for token in ('<img','<iframe','http://','https://','inspire3','guaranteed','document.write','localstorage','fetch('):
            self.assertNotIn(token,combined)

if __name__=='__main__':
    unittest.main()
