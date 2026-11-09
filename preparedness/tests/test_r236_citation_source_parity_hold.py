"""R236 synthetic 35-article source-use fixtures; never writes real manuscripts."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import r236_citation_source_parity_hold as gate


class SourceUseParityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / 'content/articles').mkdir(parents=True)
        self.roster = [{'n': n, 'slug': f'example-{n}'} for n in range(1,36)]
        for row in self.roster:
            n, slug = row['n'], row['slug']
            ids = ['general-guide']
            if n == 7: ids += ['cdc-find-clean-water'] * 2
            if n == 20: ids += ['start-ready-plan']
            (self.root / f'content/articles/{slug}.body.html').write_text(
                '<main>' + ''.join('{{cite:' + sid + '}}' for sid in ids) + '</main>')
            notes = {sid: 'Unverified author reading explanation, not safety approval' for sid in ids}
            (self.root / f'content/articles/{slug}.meta.json').write_text(json.dumps({
                'n': n, 'slug': slug, 'status': {'publish': 'draft'},
                'source_use': notes, 'safety_review': {'state': 'pending'}}))

    def tearDown(self): self.tmp.cleanup()

    def check(self): return gate.audit_parity(self.root, self.roster,
                       lambda root, rel: (root / rel).read_bytes())

    def test_35_originals_metadata_parity_still_holds(self):
        receipt = self.check()
        self.assertEqual(receipt['article_count'], 35)
        self.assertEqual(receipt['unreviewed_original_occurrences'], 3)
        self.assertEqual(receipt['source_use_missing_occurrences'], 0)
        for key in ('independent_qd_pass', 'source_review_approved',
                    'medical_safety_verified', 'release_authorized'):
            self.assertIs(receipt[key], False)

    def test_an_author_note_is_not_source_approval(self):
        r = self.check()
        self.assertTrue(r['source_use_parity_only_not_source_approval'])
        self.assertEqual(r['articles'][6]['unreviewed_original_citations'][0]['occurrences'], 2)
        self.assertEqual(r['articles'][19]['unreviewed_original_citations'][0]['occurrences'], 1)

    def mutate(self, n, kind):
        slug = self.roster[n-1]['slug']
        meta_path = self.root / f'content/articles/{slug}.meta.json'
        body_path = self.root / f'content/articles/{slug}.body.html'
        m = json.loads(meta_path.read_text())
        if kind == 'missing':
            m['source_use'].pop('general-guide')
        elif kind == 'blank':
            m['source_use']['general-guide'] = '    '
        elif kind == 'published':
            m['status']['publish'] = 'publish'
        elif kind == 'unreviewed':
            if n in (7, 20):
                body_path.write_text('<main>{{cite:general-guide}}</main>')
                return
        meta_path.write_text(json.dumps(m))

    def test_duplicate_json_key_rejected(self):
        p = self.root / 'content/articles/example-1.meta.json'
        p.write_text('{"n":1,"slug":"example-1","status":{"publish":"draft"},'
                     '"source_use":{},"source_use":{"general-guide":"note"}}')
        with self.assertRaisesRegex(ValueError, 'duplicate source-use JSON key'):self.check()

    def test_original_held_citation_deletion_rejected(self):
        for n in (7, 20):
            with self.subTest(n=n):
                p = self.root / f'content/articles/example-{n}.body.html'
                original = p.read_text()
                try:
                    self.mutate(n, 'unreviewed')
                    with self.assertRaisesRegex(ValueError, 'original citation hold changed'):self.check()
                finally: p.write_text(original)

    def test_nonfinite_metadata_rejected(self):
        p = self.root / 'content/articles/example-1.meta.json'
        p.write_text(p.read_text().replace('"n": 1', '"n": NaN'))
        with self.assertRaisesRegex(ValueError, 'nonfinite'):self.check()


def missing_note_case(n):
    def run(self):
        self.mutate(n, 'missing')
        with self.assertRaisesRegex(ValueError, 'source-use note omitted'):self.check()
    return run


def empty_note_case(n):
    def run(self):
        self.mutate(n, 'blank')
        with self.assertRaisesRegex(ValueError, 'blank source-use note'):self.check()
    return run


for n in range(1, 36):
    setattr(SourceUseParityTests, f'test_article_{n:02d}_missing_note_is_hold',missing_note_case(n))
    setattr(SourceUseParityTests, f'test_article_{n:02d}_blank_note_is_hold',empty_note_case(n))

if __name__ == '__main__': unittest.main()
