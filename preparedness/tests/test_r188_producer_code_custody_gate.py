"""R188 synthetic source custody regression; NOT native/source/safety clearance."""
from __future__ import annotations

from importlib import util
import json
from pathlib import Path
import tempfile
import unittest

PATH = Path(__file__).resolve().parents[1] / 'tools/r188_producer_code_custody_gate.py'
if not PATH.is_file():
    PATH = Path(__file__).with_name('r188_producer_code_custody_gate.py')
spec = util.spec_from_file_location('r188_producer_code_custody_gate', PATH)
assert spec is not None and spec.loader is not None
r188 = util.module_from_spec(spec)
spec.loader.exec_module(r188)


def mock_tree(root: Path):
    p = root / 'preparedness'
    (p / 'tools').mkdir(parents=True)
    pins = {}
    for name in r188.PINS:
        data = ('# synthetic ' + name + '\n').encode('utf-8')
        (p / name).write_bytes(data)
        pins[name] = r188.git_blob(data)
    return p, pins


class ProducerAdmission(unittest.TestCase):
    def test_count(self):
        self.assertEqual(len(r188.PINS), 16)

    def test_production_pins_are_hex(self):
        self.assertTrue(all(len(s) == 40 and s == s.lower() for s in r188.PINS.values()))

    def test_git_blob_is_not_plain_hash(self):
        import hashlib
        payload = b'hello producer'
        self.assertNotEqual(r188.git_blob(payload), hashlib.sha1(payload).hexdigest())
        self.assertEqual(r188.git_blob(b'hello'), 'b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0')

    def test_valid_synthetic_tree_is_still_hold(self):
        with tempfile.TemporaryDirectory() as d:
            root, pins = mock_tree(Path(d))
            packet = r188.verify(root, pins)
            self.assertEqual(packet['state'], r188.HOLD)
            self.assertIs(packet['publication_authorized'], False)
            self.assertIs(packet['independent_qd_pass'], False)
            self.assertIs(packet['qualified_source_review'], False)
            self.assertIs(packet['native_build_executed'], False)
            self.assertEqual(packet['producer_count'], len(pins))

    def test_deterministic_manifest(self):
        with tempfile.TemporaryDirectory() as d:
            root,pins=mock_tree(Path(d))
            a=r188.verify(root,pins)
            b=r188.verify(root,dict(reversed(list(pins.items()))))
            self.assertEqual(a,b)

    def test_missing_root(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,'missing or symlinked'):
                r188.verify(Path(d)/'no-such-root',{'tools/a.py':'0'*40})

    def test_invalid_roster(self):
        with tempfile.TemporaryDirectory() as d:
            root,_ = mock_tree(Path(d))
            for invalid in ({},{'../etc/passwd':'a'*40}, {'tools/f.py':'not-sha'},
                            {'tools/a.py':True}, {'tools/a.py':'a'*39}):
                with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                    r188.verify(root,invalid)

    def test_no_unpinned_deletion_can_pass(self):
        with tempfile.TemporaryDirectory() as d:
            root,pins=mock_tree(Path(d))
            pins=dict(pins);pins.pop('tools/build.py')
            # The synthetic override is test-only. Production calls MUST use
            # hardcoded PINS; ensure it never uses mutable external manifests.
            self.assertEqual(len(r188.PINS),16)
            self.assertEqual(r188.verify(root,pins)['producer_count'],15)


def add_mutations():
    for n,relative in enumerate(r188.PINS):
        for change in ('bytes','removed','symlink'):
            def attack(self, relative=relative, change=change):
                with tempfile.TemporaryDirectory() as d:
                    root,pins=mock_tree(Path(d))
                    target=root/relative
                    if change=='bytes':
                        target.write_bytes(target.read_bytes()+b'# unauthorized change\n')
                    elif change=='removed':
                        target.unlink()
                    elif change=='symlink':
                        target.unlink();target.symlink_to(root/'tools/validate.py')
                    with self.assertRaisesRegex(ValueError,'producer'):
                        r188.verify(root,pins)
            setattr(ProducerAdmission,'test_detect_%02d_%s'%(n,change),attack)
add_mutations()

if __name__ == '__main__':unittest.main()
