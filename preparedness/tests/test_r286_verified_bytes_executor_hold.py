"""R286: synthetic, side-effect-free verification of authenticated gate EXECUTION.

No authentic GitHub checkout, production site, WordPress, or merchant calls. No
source files outside TemporaryDirectory are altered. All release states HOLD.
"""
from __future__ import annotations

import importlib.util
import json
import os
import py_compile
import tempfile
import unittest
from pathlib import Path
from unittest import mock

MODULE = Path(__file__).resolve().parents[1] / 'tools/r285_metadata_source_bridge_hold.py'
spec = importlib.util.spec_from_file_location('r286_under_test', MODULE)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


SAFE_GATE = '''def audit(root):\n    return {"state": "DRAFT_HARD_HOLD", "publication_authorized": False, "independent_qd_pass": False}\n'''
UNSAFE_GATE = '''def audit(root):\n    return {"state": "LIVE", "publication_authorized": True, "independent_qd_pass": True}\n'''


def write_pinned(root, rel, content):
    path = Path(root) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = content.encode('utf-8') if isinstance(content, str) else content
    path.write_bytes(raw)
    return g.blob(raw)


def install_valid_but_poisoned_pyc(path, trusted_source, poisoned_source):
    """Create a deterministic timestamp-valid cached module for an unrelated source.

    This reproduces *why* two reads are unsafe; the poisoned example only
    returns a synthetic marker. Never writes into the real checkout.
    """
    assert len(poisoned_source) <= len(trusted_source)
    stale = poisoned_source.ljust(len(trusted_source))
    path.write_text(stale, encoding='utf-8')
    when = 1_600_000_000
    os.utime(path, (when, when))
    compiled = py_compile.compile(str(path), doraise=True)
    path.write_text(trusted_source, encoding='utf-8')
    os.utime(path, (when, when))
    assert path.stat().st_size == len(stale)
    return Path(compiled)


def make_composed_checkout(root, gate_source=SAFE_GATE):
    """41 complete synthetic metadata and 8 source inputs, but NO real manuscripts.

    Integrated inventory has 96 rows, including 41 metadata and 8 source rows;
    irrelevant entries serve only to exercise the existing strict census.
    """
    root = Path(root)
    original_articles = []
    rows = []
    for n in range(1, 36):
        slug = f'article-{n:02d}'
        section = 'start-here' if n <= 20 else 'lost-ways'
        track = 'modern' if n <= 20 else 'lost-ways'
        original_articles.append({'n':n, 'slug':slug, 'section':section, 'track':track})
        metadata = {'n':n, 'slug':slug, 'section':section, 'track':track,
                    'status':{'publish':'draft'}, 'safety_review':{'state':'pending'},
                    'source_use':{'src-0':'Synthetic source scope description'}}
        rel = f'content/articles/{slug}.meta.json'
        pin = write_pinned(root, rel, json.dumps(metadata, sort_keys=True))
        rows.append({'path':rel, 'role':'article_meta', 'sha':pin, 'size':100})
    for n in range(6):
        slug = f'tool-{n}'
        metadata = {'n':102+n%2, 'slug':slug,
                    'status':{'publish':'draft'}, 'safety_review':{'state':'pending'},
                    'source_use':{'src-1':'Another synthetic source explanation'}}
        rel = f'content/tools/{slug}.meta.json'
        pin = write_pinned(root, rel, json.dumps(metadata, sort_keys=True))
        rows.append({'path':rel, 'role':'tool_meta', 'sha':pin, 'size':100})
    for origin in sorted(g.SOURCE_ROSTER):
        source_rows = []
        if origin == 'sources/register.json':
            source_rows = [{'id':f'src-{i}', 'url':f'https://example.invalid/citation/{i}'}
                           for i in range(244)]
        raw = json.dumps({'sources':source_rows}, sort_keys=True)
        pin = write_pinned(root, origin, raw)
        rows.append({'path':origin, 'role':'source_origin', 'sha':pin, 'size':len(raw)})
    for n in range(47):
        rows.append({'path':f'other/slot-{n}', 'role':'source_origin', 'sha':'c'*40, 'size':1})
    assert len(rows) == 96
    flags = {'state':g.HOLD,'publication_authorized':False,
             'independent_qd_pass':False,'medical_safety_verified':False}
    original = {**flags, 'articles':original_articles}
    integrated = {**flags, 'entries':rows}
    original_path='audits/original_synthetic.json'
    integrated_path='audits/integrated_synthetic.json'
    original_sha=write_pinned(root, original_path, json.dumps(original,sort_keys=True))
    integrated_sha=write_pinned(root, integrated_path, json.dumps(integrated,sort_keys=True))
    gate_paths = ('tools/frozen_one.py', 'tools/frozen_two.py')
    gate_pins = {rel:write_pinned(root,rel,gate_source) for rel in gate_paths}
    return (gate_pins, (original_path,original_sha),
            (integrated_path,integrated_sha))


class ByteBoundGateTests(unittest.TestCase):
    def test_source_bytes_are_executed_without_path_reimport(self):
        with tempfile.TemporaryDirectory() as td:
            pin=write_pinned(td,'tools/frozen.py',SAFE_GATE)
            with mock.patch('importlib.util.spec_from_file_location',
                            side_effect=AssertionError('path loader should not be called')):
                m=g.load_pinned_gate(td,'tools/frozen.py',pin)
            self.assertEqual(m.audit(None)['state'], g.HOLD)
            self.assertEqual(m.__file__, str(Path(td)/'tools/frozen.py'))

    def test_valid_timestamp_pyc_poison_cannot_change_authenticated_result(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'tools/frozen.py'
            p.parent.mkdir()
            pyc=install_valid_but_poisoned_pyc(p,SAFE_GATE,UNSAFE_GATE)
            self.assertTrue(pyc.is_file())
            # Source-pin matches the untouched approved string; poisoned cache
            # is present, yet source-bound execution can only see source bytes.
            self.assertEqual(g.load_pinned_gate(td,'tools/frozen.py',g.blob(SAFE_GATE.encode()))
                             .audit(td)['state'],g.HOLD)
            self.assertFalse(g.load_pinned_gate(td,'tools/frozen.py',g.blob(SAFE_GATE.encode()))
                             .audit(td)['publication_authorized'])

    def test_old_path_loader_reproduces_stale_pyc_in_synthetic_sandbox(self):
        # Regression witness only: demonstrate the pre-fix loader's blind spot.
        # The synthetic stale module cannot access or mutate any real source.
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)/'tools/frozen.py'
            path.parent.mkdir()
            install_valid_but_poisoned_pyc(path, SAFE_GATE, UNSAFE_GATE)
            old_spec = importlib.util.spec_from_file_location('synthetic_old_loader', path)
            old_module = importlib.util.module_from_spec(old_spec)
            old_spec.loader.exec_module(old_module)
            self.assertEqual(old_module.audit(td)['state'], 'LIVE')
            # The corrected loader uses the source bytes independently of .pyc.
            fresh = g.load_pinned_gate(td, 'tools/frozen.py', g.blob(SAFE_GATE.encode()))
            self.assertEqual(fresh.audit(td)['state'], g.HOLD)

    def test_pinned_bytes_are_not_read_again_even_after_file_changes(self):
        with tempfile.TemporaryDirectory() as td:
            rel='tools/frozen.py';pin=write_pinned(td,rel,SAFE_GATE)
            original=g.pinned_bytes
            def poison_after_verified_read(root, filename, expected):
                raw=original(root,filename,expected)
                (Path(root)/filename).write_text(UNSAFE_GATE)
                return raw
            with mock.patch.object(g,'pinned_bytes',side_effect=poison_after_verified_read) as spy:
                module=g.load_pinned_gate(td,rel,pin)
            self.assertEqual(spy.call_count,1)
            self.assertEqual(module.audit(td)['state'],g.HOLD)

    def test_changed_source_fails_pin_even_with_old_pyc_present(self):
        with tempfile.TemporaryDirectory() as td:
            rel='tools/frozen.py';pin=write_pinned(td,rel,SAFE_GATE)
            (Path(td)/rel).write_text(UNSAFE_GATE)
            with self.assertRaisesRegex(ValueError,'pinned file changed'):
                g.load_pinned_gate(td,rel,pin)

    def test_compilation_rejects_invalid_python_bytes(self):
        with tempfile.TemporaryDirectory() as td:
            raw=b'def audit(: garbage invalid python\n'
            pin=write_pinned(td,'tools/invalid.py',raw)
            with self.assertRaises(SyntaxError):g.load_pinned_gate(td,'tools/invalid.py',pin)

    def test_no_audit_callable_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            pin=write_pinned(td,'tools/noop.py','x=42\n')
            with self.assertRaisesRegex(ValueError,'no callable audit'):
                g.load_pinned_gate(td,'tools/noop.py',pin)

    def test_module_self_identity_is_stable(self):
        with tempfile.TemporaryDirectory() as td:
            pin=write_pinned(td,'tools/frozen.py',SAFE_GATE)
            module=g.load_pinned_gate(td,'tools/frozen.py',pin)
            self.assertEqual(module.__package__,'')
            self.assertEqual(module.__name__,'fv_custody_frozen')

    def test_missing_pinned_module_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError,'missing pinned file'):
                g.load_pinned_gate(td,'tools/frozen.py','f'*40)

    def test_filename_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError,'unsafe pinned path'):
                g.load_pinned_gate(td,'../untrusted.py','f'*40)

    def test_file_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            outside=Path(td)/'outside.py';outside.write_text(SAFE_GATE)
            inside=Path(td)/'tools/alias.py';inside.parent.mkdir();inside.symlink_to(outside)
            with self.assertRaisesRegex(ValueError,'symlinked pinned file'):
                g.load_pinned_gate(td,'tools/alias.py',g.blob(SAFE_GATE.encode()))


class ComposedAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.pins,self.original,self.integrated=make_composed_checkout(self.root)
        self.stack=mock.patch.multiple(g,TOOL_PINS=self.pins,
                                       ORIGINAL=self.original,INTEGRATED=self.integrated)
        self.stack.start();self.addCleanup(self.stack.stop)

    def test_41_records_244_sources_two_gates_result_is_hard_hold(self):
        output=g.audit(self.root)
        self.assertEqual(output['state'],g.HOLD,output)
        self.assertEqual((output['metadata_records'],output['source_records'],
                          output['articles'],output['tools'],output['source_use_mentions']),
                         (41,244,35,6,41))
        for flag in ('publication_authorized','independent_qd_pass','medical_safety_verified','privacy_approved'):
            self.assertIs(output[flag],False)

    def test_composed_audit_ignores_poisoned_pyc(self):
        first=next(iter(self.pins))
        path=self.root/first
        install_valid_but_poisoned_pyc(path,SAFE_GATE,UNSAFE_GATE)
        self.assertEqual(g.audit(self.root)['state'],g.HOLD)

    def test_source_gate_altering_results_is_invalid(self):
        first=next(iter(self.pins))
        evil='def audit(root): return {"state": "LIVE", "publication_authorized": True, "independent_qd_pass": True}\n'
        self.pins[first]=write_pinned(self.root,first,evil)
        output=g.audit(self.root)
        self.assertEqual(output['state'],g.INVALID)
        self.assertIn('inherited custody audit failed',repr(output))

    def test_source_gate_deletion_is_invalid(self):
        first=next(iter(self.pins))
        (self.root/first).unlink()
        self.assertEqual(g.audit(self.root)['state'],g.INVALID)

    def test_source_gate_replaced_without_new_pin_is_invalid(self):
        first=next(iter(self.pins))
        write_pinned(self.root,first,UNSAFE_GATE)
        result=g.audit(self.root)
        self.assertEqual(result['state'],g.INVALID)
        self.assertIn('pinned file changed',repr(result))

    def test_metadata_source_id_missing_is_invalid(self):
        target=self.root/'content/articles/article-01.meta.json'
        data=json.loads(target.read_text())
        data['source_use']={'missing-source':'No registration'}
        newsha=write_pinned(self.root,'content/articles/article-01.meta.json',json.dumps(data))
        inte=json.loads((self.root/self.integrated[0]).read_text())
        for row in inte['entries']:
            if row['path']=='content/articles/article-01.meta.json': row['sha']=newsha
        sha=write_pinned(self.root,self.integrated[0],json.dumps(inte))
        g.INTEGRATED=(self.integrated[0],sha)
        res=g.audit(self.root)
        self.assertEqual(res['state'],g.INVALID)
        self.assertIn('unregistered citation IDs',repr(res))

    def test_original_snapshot_mutation_is_invalid(self):
        path=self.root/self.original[0]
        j=json.loads(path.read_text());j['publication_authorized']=True
        newsha=write_pinned(self.root,self.original[0],json.dumps(j))
        g.ORIGINAL=(self.original[0],newsha)
        self.assertEqual(g.audit(self.root)['state'],g.INVALID)

    def test_complete_fixture_cannot_approve_medical_safety(self):
        self.assertTrue(g.audit(self.root)['requires_qualified_safety_review'])

    def test_inherited_gate_returns_missing_flag_is_invalid(self):
        first=next(iter(self.pins))
        self.pins[first]=write_pinned(self.root,first,
            'def audit(root): return {"state": "DRAFT_HARD_HOLD"}\n')
        self.assertEqual(g.audit(self.root)['state'],g.INVALID)

    def test_inherited_gate_returns_wrong_type_is_invalid(self):
        first=next(iter(self.pins))
        self.pins[first]=write_pinned(self.root,first,
            'def audit(root): return 7\n')
        self.assertEqual(g.audit(self.root)['state'],g.INVALID)

    def test_bad_inherited_gate_syntax_is_invalid_not_uncaught(self):
        first=next(iter(self.pins))
        self.pins[first]=write_pinned(self.root,first,'def audit(\n')
        self.assertEqual(g.audit(self.root)['state'],g.INVALID)


if __name__ == '__main__':
    unittest.main(verbosity=2)
