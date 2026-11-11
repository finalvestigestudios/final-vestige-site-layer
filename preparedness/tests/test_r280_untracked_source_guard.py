"""R280: synthetic source-shadow and nested artifact rejection without real writes.

Source safety is mechanical only; every acceptable case remains DRAFT_HARD_HOLD.
"""
from __future__ import annotations
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from test_r279_live_slate_gate import g, manifest_and_tree


class R280(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.manifest = manifest_and_tree(self.root)

    def assert_held(self):
        result = g.check_tree(self.root, self.manifest)
        self.assertEqual(result['state'], g.HOLD)
        self.assertFalse(result['publication_authorized'])
        self.assertFalse(result['independent_qd_pass'])

    def assert_blocked(self, relative, contents='{}'):
        target = self.root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(contents)
        with self.assertRaisesRegex(ValueError, '(untracked source fragment|unexpected article/tool)'):
            g.check_tree(self.root, self.manifest)

    def test_pinned_baseline_held(self):
        self.assert_held()

    def test_prose_notes_permitted_without_safety_approval(self):
        (self.root/'sources/fragments/README.md').write_text('Notes are not approved source records.')
        self.assert_held()

    def test_manifest_writes_not_trusted_even_if_filenames_listed(self):
        self.assertEqual(g.audit(self.root)['state'], g.INVALID)

    def test_added_nested_markdown_is_not_source_data(self):
        f = self.root/'sources/fragments/worknotes/notes.md'
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text('Internal review only')
        self.assert_held()

    def test_added_source_symlink_rejected(self):
        target = self.root/'sources/fragments/shadow.json'
        target.symlink_to(self.root/'sources/fragments/start.json')
        with self.assertRaisesRegex(ValueError, 'symlink'):
            g.check_tree(self.root, self.manifest)

    def test_added_nested_source_symlink_rejected(self):
        target = self.root/'sources/fragments/other'
        target.symlink_to(self.root/'sources/fragments', target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'symlink'):
            g.check_tree(self.root, self.manifest)

    def test_added_article_symlink_rejected(self):
        target = self.root/'content/articles/stray.meta.json'
        target.symlink_to(self.root/'content/articles/article-01.meta.json')
        with self.assertRaisesRegex(ValueError, 'symlink'):
            g.check_tree(self.root, self.manifest)




SOURCE_EXT_CASES = [
    'sources/fragments/undocumented.json',
    'sources/fragments/UNTRACKED.JSON',
    'sources/fragments/shadow.jsonl',
    'sources/fragments/shadow.yaml',
    'sources/fragments/shadow.yml',
    'sources/fragments/shadow.csv',
    'sources/fragments/shadow.tsv',
    'sources/fragments/nested/undocumented.json',
    'sources/fragments/nested/nested/undocumented.JSON',
    'sources/fragments/nested/deep/undocumented.csv',
    'sources/fragments/.hidden.json',
    'sources/fragments/review/FIXTURE.json',
]
CONTENT_CASES = [
    'content/articles/stray.body.html',
    'content/articles/STRAY.BODY.HTML',
    'content/articles/nested/stray.body.html',
    'content/articles/nested/stray.meta.json',
    'content/tools/stray.meta.json',
    'content/tools/STRAY.META.JSON',
    'content/tools/nested/stray.body.html',
    'content/tools/nested/stray.meta.json',
]

for i, path in enumerate(SOURCE_EXT_CASES):
    def make(p):
        def test(self):
            self.assert_blocked(p)
        return test
    setattr(R280, 'test_reject_untracked_source_%02d' % (i+1), make(path))

for i, path in enumerate(CONTENT_CASES):
    def make(p):
        def test(self):
            self.assert_blocked(p)
        return test
    setattr(R280, 'test_reject_nested_or_casefolded_manuscript_%02d' % (i+1), make(path))


if __name__ == '__main__':
    unittest.main(verbosity=2)
