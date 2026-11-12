"""R316 isolated source/output adversarial fixtures; no authentic source mutation."""
from __future__ import annotations
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / 'tools/r316_authentic_41_export_parity_hold.py'
spec = importlib.util.spec_from_file_location('r316_export_gate', MODULE)
r316 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r316)

NAMES = [f'article-{i}' for i in range(1, 36)] + [f'tool-{i}' for i in range(1, 7)]
BODY = ('<div class="pa pa-article" data-slug="{slug}">'
        '<p>Draft: not public. Independent safety/source and QD verification pending.</p>'
        '<h2>Sources and verification</h2><p>Evidence [1].</p></div>')


class ExportFixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='fv-r316-synthetic-')
        self.root = Path(self.temp.name)
        self.wp = self.root / 'preparedness/build/wp'
        self.preview = self.root / 'preparedness/build/preview'
        self.wp.mkdir(parents=True)
        self.preview.mkdir(parents=True)
        self.expected = {}
        self.rows = []
        for i, slug in enumerate(NAMES):
            body = BODY.format(slug=slug)
            wp = ('<!-- wp:html -->\n' + body + '\n<!-- /wp:html -->\n').encode()
            preview = ('<!doctype html>\n<main>' + body + '</main>\n').encode()
            row = {'slug': slug, 'words': 100 + i, 'minutes': 2,
                   'sources': ['source-a', 'source-b'],
                   'canonical': 'https://finalvestige.com/preparedness/section/' + slug + '/'}
            self.expected[slug] = {'wp': wp, 'preview': preview,
                                   **{k: row[k] for k in ('words', 'minutes', 'sources', 'canonical')}}
            self.rows.append(row)
            (self.wp / (slug + '.html')).write_bytes(wp)
            (self.preview / (slug + '.html')).write_bytes(preview)
        self.release = {'state': 'HOLD', 'article_drafts': 41, 'article_published': 0,
                        'wordpress_publication_performed': False, 'independent_qa_verified': False}
        self.report = {'articles': self.rows, 'release_evidence': self.release}

    def tearDown(self):
        self.temp.cleanup()

    def audit(self):
        return r316.audit_exports(self.root, self.expected, self.report)

    def assertError(self, code):
        result = self.audit()
        self.assertEqual(result['state'], 'INVALID_HARD_HOLD', result['errors'])
        self.assertTrue(any(code in e for e in result['errors']), result['errors'])

    def test_clean_41_pairs_remain_draft_hard_hold(self):
        result = self.audit()
        self.assertEqual(result['state'], 'DRAFT_HARD_HOLD', result['errors'])
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['expected_guides'], 41)
        self.assertEqual(result['verified_wordpress_outputs'], 41)
        self.assertEqual(result['verified_preview_outputs'], 41)
        self.assertEqual(len(result['export_receipts']), 82)
        self.assertFalse(result['source_safety_qd_approval'])
        self.assertFalse(result['wordpress_published'])
        self.assertFalse(result['commercial_conversion_verified'])

    def test_hub_and_landing_only_in_approved_set(self):
        (self.wp / 'landing.html').write_text('landing')
        (self.preview / 'hub-water.html').write_text('hub')
        result = r316.audit_exports(self.root, self.expected, self.report,
                                    allowed_other_slugs={'hub-water'})
        self.assertEqual(result['errors'], [])

    def test_unrecognized_generated_hub(self):
        (self.wp / 'hub-unknown.html').write_text('unexpected')
        self.assertError('UNEXPECTED_EXPORT:wp')

    def test_40_entries_fail(self):
        self.expected.pop(NAMES[-1])
        self.assertError('EXPECTED_EXACTLY_41')

    def test_duplicate_canonical_fails(self):
        canonical = self.rows[0]['canonical']
        self.rows[1]['canonical'] = canonical
        self.expected[NAMES[1]]['canonical'] = canonical
        self.assertError('DUPLICATE_CANONICAL_GUIDE_URLS')

    def test_no_build_report(self):
        self.report = None
        self.assertError('MISSING_AUTHENTIC_BUILD_REPORT')

    def test_incomplete_checkout_cli_hard_fails(self):
        result = subprocess.run([sys.executable, '-I', str(MODULE), '--root', str(self.root)],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)['state'], 'INVALID_HARD_HOLD')

    def test_sha_pin_matches_authenticated_builder(self):
        self.assertEqual(r316.BUILD_GIT_BLOB, '349173d1e1d735eade218d95c7a0a2649c8cccd9')
        self.assertEqual(r316.R315_GIT_BLOB, 'e0518450c3b45e5e8b59a2f5d0f801279be4821b')

    def test_git_blob_known_string(self):
        self.assertEqual(r316.git_blob(b'hello'), 'b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0')

    def test_no_path_traversal(self):
        self.assertIsNone(r316.file_bytes(self.root, '../../etc/passwd'))
        self.assertIsNone(r316.file_bytes(self.root, '/etc/passwd'))

    def test_disallowed_symlinked_source(self):
        p = self.wp / (NAMES[0] + '.html')
        data = p.read_bytes()
        p.unlink()
        other = self.root / 'untrusted'
        other.write_bytes(data)
        p.symlink_to(other)
        self.assertError('MISSING_OR_SYMLINK_EXPORT:wp')


# Many independent corruption classes on both surfaces. Each test operates
# on a fresh synthetic 41-pair tree and checks deterministic hard failure.
CHANGES = {
    'missing': lambda p: p.unlink(),
    'empty': lambda p: p.write_bytes(b''),
    'truncated': lambda p: p.write_bytes(p.read_bytes()[:17]),
    'extra': lambda p: p.write_bytes(p.read_bytes() + b'<!--unexpected-->'),
    'line_endings': lambda p: p.write_bytes(p.read_bytes().replace(b'\n', b'\r\n')),
    'missing_warning': lambda p: p.write_bytes(
        p.read_bytes().replace(b'Draft: not public', b'Independently approved')),
    'claim_mutation': lambda p: p.write_bytes(
        p.read_bytes().replace(b'Evidence [1]', b'Unreviewed claim [1]')),
    'phantom_citation': lambda p: p.write_bytes(
        p.read_bytes().replace(b'Evidence', b'Evidence {{cite:phantom}}')),
    'wrong_slug': lambda p: p.write_bytes(p.read_bytes().replace(b'article-1', b'article-2')),
    'bad_utf8': lambda p: p.write_bytes(p.read_bytes() + b'\xff'),
    'extra_space': lambda p: p.write_bytes(p.read_bytes().replace(b'<h2>', b' <h2>')),
    'duplicate_block': lambda p: p.write_bytes(p.read_bytes() * 2),
}
for surface in ('wp', 'preview'):
    for label, mutation in CHANGES.items():
        def test(self, surface=surface, mutation=mutation, label=label):
            path = (self.wp if surface == 'wp' else self.preview) / (NAMES[0] + '.html')
            mutation(path)
            result = self.audit()
            self.assertEqual(result['state'], 'INVALID_HARD_HOLD', result['errors'])
            expected_error = ('MISSING_OR_SYMLINK_EXPORT' if label == 'missing'
                              else 'RENDERED_BYTES_DIFFER_FROM_AUTHENTIC_SOURCES')
            self.assertTrue(any(expected_error + ':' + surface in e for e in result['errors']))
        setattr(ExportFixture, 'test_' + surface + '_' + label, test)

for surface in ('wp', 'preview'):
    def test_missing_directory(self, surface=surface):
        target = self.wp if surface == 'wp' else self.preview
        for path in target.iterdir():
            path.unlink()
        target.rmdir()
        self.assertError('MISSING_OR_LINKED_EXPORT_DIRECTORY:' + surface)
    setattr(ExportFixture, 'test_' + surface + '_missing_directory', test_missing_directory)

    def test_linked_directory(self, surface=surface):
        target = self.wp if surface == 'wp' else self.preview
        other = self.preview if surface == 'wp' else self.wp
        for path in target.iterdir():
            path.unlink()
        target.rmdir()
        target.symlink_to(other, target_is_directory=True)
        self.assertError('MISSING_OR_LINKED_EXPORT_DIRECTORY:' + surface)
    setattr(ExportFixture, 'test_' + surface + '_linked_directory', test_linked_directory)

for label, change in {
    'live': lambda d: d.update(state='LIVE'),
    'approved': lambda d: d.update(state='PASS'),
    'state_lowercase': lambda d: d.update(state='hold'),
    'draft_count': lambda d: d.update(article_drafts=40),
    'draft_boolean': lambda d: d.update(article_drafts=True),
    'published_count': lambda d: d.update(article_published=1),
    'published_boolean': lambda d: d.update(article_published=True),
    'public_wordpress': lambda d: d.update(wordpress_publication_performed=True),
    'fake_qd': lambda d: d.update(independent_qa_verified=True),
    'missing_state': lambda d: d.pop('state'),
    'missing_qd': lambda d: d.pop('independent_qa_verified'),
}.items():
    def test(self, change=change):
        change(self.release)
        self.assertError('UNSAFE_OR_UNRECONCILED_RELEASE_EVIDENCE')
    setattr(ExportFixture, 'test_release_' + label, test)

for label, key, value in [
    ('word_loss', 'words', 1),
    ('reading_time', 'minutes', 99),
    ('missing_sources', 'sources', []),
    ('wrong_source', 'sources', ['phantom']),
    ('wrong_domain', 'canonical', 'https://elsewhere.test/'),
    ('changed_route', 'canonical', 'https://finalvestige.com/preparedness/other/'),
]:
    def test(self, key=key, value=value):
        self.rows[0][key] = value
        self.assertError('BUILD_REPORT_READING_DEPTH_CITATION_OR_ROUTE_DRIFT:' + key)
    setattr(ExportFixture, 'test_report_' + label, test)

for issue in ('duplicate_slug', 'missing_row', 'extra_slug', 'missing_cites'):
    def test(self, issue=issue):
        if issue == 'duplicate_slug':
            self.rows[1]['slug'] = self.rows[0]['slug']
        elif issue == 'missing_row':
            self.rows.pop()
        elif issue == 'extra_slug':
            self.rows[-1]['slug'] = 'fake-tool'
        else:
            self.rows[0].pop('sources')
        self.assertEqual(self.audit()['state'], 'INVALID_HARD_HOLD')
    setattr(ExportFixture, 'test_report_' + issue, test)

if __name__ == '__main__':
    unittest.main()
