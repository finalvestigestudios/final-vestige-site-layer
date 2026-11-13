"""R342 synthetic adversarial tests. Never touch canonical source directories."""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import r342_canonical_fixture_containment_hold as g


class R342StaticTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.root = Path(self.td.name) / 'repo'
        self.prep = self.root / 'preparedness'
        self.prep.mkdir(parents=True)
        for name in (*g.PROTECTED_DIRS, 'tests', 'build'):
            (self.prep / name).mkdir(parents=True, exist_ok=True)
        (self.prep / 'taxonomy.json').write_text('{}')
        self.guard = g.SourceMutationGuard(self.prep)

    def test_schema_and_hold(self):
        r = g.report([], {}, {}, {'executed': True, 'successful': True})
        self.assertEqual(r['state'], 'DRAFT_HARD_HOLD')
        self.assertFalse(any(r[k] for k in g.FINAL_HOLD_FIELDS))
        self.assertFalse(r['source_claim_support_verified'])

    def test_errors_never_pass(self):
        r = g.report(['NO_NATIVE'], {}, {})
        self.assertEqual(r['state'], 'INVALID_HARD_HOLD')
        self.assertIn('NO_NATIVE', r['errors'])

    def test_no_source_is_not_pass(self):
        r = g.run(self.root, require_native_witness=False)
        self.assertEqual(r['state'], 'INVALID_HARD_HOLD')
        self.assertTrue(r['errors'])

    def test_missing_native_witness_is_rejected(self):
        make_fake_source(self.prep)
        r = g.run(self.root, require_native_witness=True)
        self.assertEqual(r['state'], 'INVALID_HARD_HOLD')
        self.assertIn('R341_FROZEN_9_HEAD_SOURCE_WITNESS_FAILED', r['errors'])

    def test_snapshot_is_sorted_and_complete(self):
        make_fake_source(self.prep)
        x = g.inventory(self.prep)
        self.assertEqual(len(x), 84)
        self.assertEqual(list(x), sorted(x))
        self.assertEqual(len(x['taxonomy.json']), 64)

    def test_sha256_changes_with_content(self):
        make_fake_source(self.prep)
        x = g.inventory(self.prep)
        p = self.prep / 'content/articles/article-0.body.html'
        p.write_text('<h1>changed</h1>')
        y = g.inventory(self.prep)
        self.assertNotEqual(x, y)

    def test_missing_body_detected(self):
        make_fake_source(self.prep)
        (self.prep / 'content/articles/article-0.body.html').unlink()
        with self.assertRaisesRegex(ValueError, 'COVERAGE'):
            g.inventory(self.prep)

    def test_missing_meta_detected(self):
        make_fake_source(self.prep)
        (self.prep / 'content/tools/tool-0.meta.json').unlink()
        with self.assertRaisesRegex(ValueError, 'COVERAGE'):
            g.inventory(self.prep)

    def test_mismatched_slug_detected(self):
        make_fake_source(self.prep)
        p = self.prep / 'content/articles/article-0.meta.json'
        p.rename(self.prep / 'content/articles/other.meta.json')
        with self.assertRaisesRegex(ValueError, 'COVERAGE'):
            g.inventory(self.prep)

    def test_extra_article_detected(self):
        make_fake_source(self.prep)
        (self.prep / 'content/articles/sneaky.body.html').write_text('hi')
        with self.assertRaisesRegex(ValueError, 'COVERAGE'):
            g.inventory(self.prep)

    def test_source_symlink_rejected(self):
        make_fake_source(self.prep)
        target = self.prep / 'content/articles/article-0.body.html'
        symlink = self.prep / 'sources' / 'link.json'
        symlink.symlink_to(target)
        with self.assertRaisesRegex(ValueError, 'SYMLINK'):
            g.inventory(self.prep)

    def test_missing_source_register(self):
        make_fake_source(self.prep)
        (self.prep / 'sources/register.json').unlink()
        with self.assertRaisesRegex(ValueError, 'REQUIRED'):
            g.inventory(self.prep)

    def test_unknown_open_mode_is_not_accepted_as_readonly(self):
        self.assertTrue(g._write_open_mode(object(), None))

    def test_read_modes_not_blocked(self):
        for mode in ('r', 'rb', 'rt'):
            with self.subTest(mode=mode):
                self.assertFalse(g._write_open_mode(mode, None))

    def test_edit_modes_blocked(self):
        for mode in ('w','wb','a','a+','x','r+','x+b','wt','w+'):
            with self.subTest(mode=mode):
                self.assertTrue(g._write_open_mode(mode, None))

    def test_read_open_event_is_allowed(self):
        self.guard.inspect('open', (str(self.prep/'sources/register.json'), 'r', 0))
        self.assertFalse(self.guard.blocked)

    def test_write_open_event_is_denied(self):
        with self.assertRaisesRegex(PermissionError, 'BLOCKED'):
            self.guard.inspect('open', (str(self.prep/'sources/register.json'), 'w', 0))
        self.assertEqual(len(self.guard.blocked), 1)

    def test_read_os_open_is_allowed(self):
        self.guard.inspect('open', (str(self.prep/'sources/register.json'), None, os.O_RDONLY))
        self.assertFalse(self.guard.blocked)

    def test_write_os_open_is_denied(self):
        with self.assertRaises(PermissionError):
            self.guard.inspect('open', (str(self.prep/'sources/register.json'), None, os.O_WRONLY))

    def test_source_external_directory_is_allowed(self):
        self.guard.inspect('open', (str(self.prep/'build/temp.json'), 'w', os.O_CREAT))
        self.assertFalse(self.guard.blocked)

    def test_test_directory_is_allowed(self):
        self.guard.inspect('open', (str(self.prep/'tests/temp.txt'), 'w', os.O_CREAT))
        self.assertFalse(self.guard.blocked)

    def test_symlink_into_source_rejected(self):
        link = self.root / 'external-link'
        link.symlink_to(self.prep/'sources', target_is_directory=True)
        with self.assertRaises(PermissionError):
            self.guard.inspect('open', (str(link/'register.json'), 'w', os.O_CREAT))

    def test_symlink_out_of_source_rejected(self):
        link = self.prep / 'sources' / 'out'
        link.symlink_to(self.root/'external-link', target_is_directory=True)
        with self.assertRaises(PermissionError):
            self.guard.inspect('open', (str(link/'file.json'), 'w', os.O_CREAT))

    def test_path_traversal_into_source_rejected(self):
        with self.assertRaises(PermissionError):
            self.guard.inspect('open', (str(self.root/'x'/'..'/'preparedness/sources/register.json'), 'w', os.O_TRUNC))

    def test_relative_path_into_source_rejected(self):
        self.assertTrue(g.protected_target('preparedness/sources/register.json', self.prep, self.root))

    def test_file_descriptor_unknown_is_not_artificial_path(self):
        self.assertFalse(g.protected_target(8, self.prep))

    def test_source_directories_exact(self):
        self.assertEqual(g.PROTECTED_DIRS, ('content', 'sources', 'templates', 'assets'))

    def test_canonical_taxonomy_write_denied(self):
        with self.assertRaises(PermissionError):
            self.guard.inspect('open', (self.prep/'taxonomy.json', 'w', os.O_CREAT))

    def test_source_read_only_does_not_imply_qd(self):
        r = g.report([], {'a':'b'}, {'a':'b'}, {'executed': True, 'successful': True})
        self.assertEqual(r['state'], 'DRAFT_HARD_HOLD')
        self.assertFalse(r['may_publish'])

    def test_docstring_explicit_limits(self):
        self.assertIn('external child processes', g.__doc__)
        self.assertIn('human claim review', g.__doc__)


# Use distinct methods, not subTests, to force a broad mutation matrix into unittest counters.
EVENT_CASES = [
    ('open', ('w', os.O_CREAT)), ('open', ('a+', os.O_APPEND)),
    ('open', ('r+', os.O_RDWR)), ('open', (None, os.O_TRUNC)),
    ('open', (None, os.O_EXCL)), ('open', (None, os.O_WRONLY)),
    ('os.remove', ()), ('os.unlink', ()), ('os.rmdir', ()),
    ('os.mkdir', ()), ('os.chmod', ()), ('os.chown', ()),
    ('os.utime', ()), ('os.truncate', ()), ('os.chdir', ()),
    ('os.rename', ()), ('os.replace', ()), ('os.link', ()), ('os.symlink', ()),
]
PATHS = ['content/articles/article-0.body.html', 'content/tools/tool-0.meta.json',
         'sources/fragments/source.json', 'sources/register.json',
         'taxonomy.json', 'templates/template.html', 'assets/image.svg']


def make_mutation_case(event, config, rel):
    def case(self):
        p = self.prep / rel
        if event == 'open':
            args = (p, config[0], config[1])
        elif event in ('os.rename', 'os.replace', 'os.link', 'os.symlink'):
            args = (p, self.prep/'build'/'out.json')
        else:
            args = (p,)
        with self.assertRaisesRegex(PermissionError, 'BLOCKED'):
            self.guard.inspect(event, args)
        self.assertEqual(len(self.guard.blocked), 1)
    return case

for i, (event, config) in enumerate(EVENT_CASES):
    for j, rel in enumerate(PATHS):
        # 19 * 7 = 133 distinct source-mutation adversarial tests.
        setattr(R342StaticTests, f'test_fence_{i:02d}_{j:02d}', make_mutation_case(event, config, rel))


def make_fake_source(prep: Path):
    for rel in ('content/articles','content/tools','sources/fragments','tests','tools'):
        (prep/rel).mkdir(parents=True, exist_ok=True)
    (prep/'taxonomy.json').write_text('{"base_path":"/preparedness/"}')
    (prep/'sources/register.json').write_text('{"sources":[]}')
    for kind, count, prefix in [('articles',35,'article'), ('tools',6,'tool')]:
        for i in range(count):
            (prep/f'content/{kind}/{prefix}-{i}.body.html').write_text('<h1>Draft</h1>')
            (prep/f'content/{kind}/{prefix}-{i}.meta.json').write_text('{"status":"draft"}')


class R342IntegrationTests(unittest.TestCase):
    def execute_child(self, kind):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            prep = repo/'preparedness'
            make_fake_source(prep)
            (prep/'tools').mkdir(exist_ok=True)
            (prep/'tests').mkdir(exist_ok=True)
            tests = '\n'.join(
                ['import unittest', 'from pathlib import Path', 'class Example(unittest.TestCase):']
                + [f'    def test_{i:02d}(self): self.assertEqual({i}, {i})' for i in range(36)]
                + ([
                   '    def test_99_attack(self):',
                   '        target = Path(__file__).parents[1] / "sources" / "fragments" / "_dup_test.json"',
                   '        target.write_text("surprise")',
                  ] if kind=='write' else [
                   '    def test_99_attack(self):',
                   '        import os',
                   '        root = Path(__file__).parents[1]',
                   '        os.rename(root / "sources" / "register.json", root / "build" / "register.json")',
                  ] if kind=='rename' else []))
            (prep/'tests/test_fake.py').write_text(tests)
            script = Path(g.__file__)
            # Test-only invocation requires no real R341 witness; CLI defaults to strict true.
            code = ('import sys,json,pathlib;'
                    f'sys.path.insert(0,{str(script.parent)!r});'
                    'import r342_canonical_fixture_containment_hold as m;'
                    f'r=m.run(pathlib.Path({str(repo)!r}),True,"test_fake.py",False);'
                    'r.pop("source_sha256_manifest",None);print(json.dumps(r))')
            child = subprocess.run([sys.executable, '-I', '-c', code],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   text=True, timeout=40)
            self.assertEqual(child.returncode, 0, child.stderr)
            data=json.loads(child.stdout.strip().splitlines()[-1])
            return data

    def test_genuine_fixture_test_unaltered(self):
        data=self.execute_child('pass')
        self.assertEqual(data['state'], 'DRAFT_HARD_HOLD')
        self.assertEqual(data['tests']['count'],36)
        self.assertTrue(data['tests']['successful'])
        self.assertEqual(data['transient_source_write_attempts_blocked'],0)
        self.assertTrue(data['source_unchanged_after_tests'])
        self.assertFalse(data['may_publish'])

    def test_write_then_cleanup_cannot_happen(self):
        data=self.execute_child('write')
        self.assertEqual(data['state'],'INVALID_HARD_HOLD')
        self.assertEqual(data['tests']['count'],37)
        self.assertGreater(data['transient_source_write_attempts_blocked'],0)
        self.assertTrue(data['source_unchanged_after_tests'])
        self.assertIn('TRANSIENT_CANONICAL_SOURCE_MUTATION_ATTEMPT_DETECTED', data['errors'])

    def test_rename_canonical_input_is_blocked(self):
        data=self.execute_child('rename')
        self.assertEqual(data['state'],'INVALID_HARD_HOLD')
        self.assertGreater(data['transient_source_write_attempts_blocked'],0)
        self.assertTrue(data['source_unchanged_after_tests'])


if __name__=='__main__':
    unittest.main()
