"""R337: private six-app release report must be byte-exact before publication.

Real temporary files only; no customer data, premium binaries or Windows EXEs.
"""
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import report_evidence as evidence


class StreamProxy:
    """Forward an owned binary stream but inject a deliberate write/read fault."""
    def __init__(self, stream, *, write_mode='normal', read_fault=False, enter_fault=False):
        self.stream = stream
        self.write_mode = write_mode
        self.read_fault = read_fault
        self.enter_fault = enter_fault

    def __getattr__(self, key):
        return getattr(self.stream, key)

    def __enter__(self):
        if self.enter_fault:
            raise RuntimeError('PRIVATE_CLIENT_PATH')
        self.stream.__enter__()
        return self

    def __exit__(self, *args):
        return self.stream.__exit__(*args)

    def write(self, payload):
        if self.write_mode == 'short':
            return self.stream.write(payload[:3])
        if self.write_mode == 'lied':
            self.stream.write(payload[:3])
            return len(payload)
        if self.write_mode == 'corrupt':
            self.stream.write(b'X' + payload[1:])
            return len(payload)
        if self.write_mode == 'boolean':
            self.stream.write(payload)
            return True
        if self.write_mode == 'string':
            self.stream.write(payload)
            return str(len(payload))
        if self.write_mode == 'subclass':
            class FakeInt(int):
                pass
            self.stream.write(payload)
            return FakeInt(len(payload))
        return self.stream.write(payload)

    def read(self, n=-1):
        if self.read_fault:
            raise OSError('PRIVATE_CLIENT_PATH')
        return self.stream.read(n)


class ReportEvidenceExactStageR337(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory(prefix='r337-private-financial-')
        self.addCleanup(t.cleanup)
        self.root = Path(t.name)
        self.dest = self.root / 'verification.json'
        self.payload = {
            'schema': 1, 'status': 'integrity_only',
            'release_authorized': False,
            'premium_entitlement_verified': False,
            'codesigning_verified': False, 'malware_scan_verified': False,
            'artifacts': ['LedgerDiffLite.exe', 'InvoiceTwinScout.exe',
                          'SpendMapLite.exe', 'PolicyDeltaDesk.exe',
                          'GrantAuditStudioPro.exe', 'ProcureGuardStudioPro.exe'],
        }

    def stage_names(self):
        return sorted(p.name for p in self.root.glob('.fvs-candidate-report-*'))

    def assert_rejected_privately(self):
        with self.assertRaises(evidence.ReportEvidenceError) as ctx:
            evidence.publish_report(self.dest, self.payload)
        self.assertFalse(self.dest.exists())
        self.assertEqual(self.stage_names(), [])
        self.assertNotIn(str(self.root), str(ctx.exception))
        self.assertNotIn('PRIVATE_CLIENT_PATH', str(ctx.exception))
        self.assertIsNone(ctx.exception.__cause__)

    def proxy_fdopen(self, *, write_mode='normal', read_fault=False, enter_fault=False):
        original = os.fdopen
        def fake(fd, mode, *args, **kw):
            stream = original(fd, mode, *args, **kw)
            return StreamProxy(stream, write_mode=write_mode,
                               read_fault=read_fault, enter_fault=enter_fault)
        return patch.object(evidence.os, 'fdopen', side_effect=fake)

    def test_exact_json_readback_and_lf(self):
        evidence.publish_report(self.dest, self.payload)
        self.assertEqual(json.loads(self.dest.read_text('utf-8')), self.payload)
        expected = (json.dumps(self.payload, sort_keys=True, indent=2,
                               ensure_ascii=True, allow_nan=False) + '\n').encode()
        self.assertEqual(self.dest.read_bytes(), expected)
        self.assertEqual(self.stage_names(), [])

    def test_repeated_publication_is_byte_deterministic(self):
        evidence.publish_report(self.dest, self.payload)
        second = self.root / 'another.json'
        evidence.publish_report(second, self.payload)
        self.assertEqual(self.dest.read_bytes(), second.read_bytes())

    def test_private_posix_mode(self):
        if os.name == 'nt':
            self.skipTest('Windows ACL mode bits are not POSIX permissions')
        evidence.publish_report(self.dest, self.payload)
        self.assertEqual(self.dest.stat().st_mode & 0o077, 0)

    def test_exclusive_target_protects_existing_evidence(self):
        self.dest.write_bytes(b'customer-preserved')
        with self.assertRaises(evidence.ReportEvidenceError):
            evidence.publish_report(self.dest, self.payload)
        self.assertEqual(self.dest.read_bytes(), b'customer-preserved')
        self.assertEqual(self.stage_names(), [])

    def test_short_actual_write_fails_before_any_link(self):
        with self.proxy_fdopen(write_mode='short'):
            self.assert_rejected_privately()

    def test_lying_write_count_fails_on_readback(self):
        with self.proxy_fdopen(write_mode='lied'):
            self.assert_rejected_privately()

    def test_same_length_corruption_fails_on_readback(self):
        with self.proxy_fdopen(write_mode='corrupt'):
            self.assert_rejected_privately()

    def test_boolean_write_count_fails_closed(self):
        with self.proxy_fdopen(write_mode='boolean'):
            self.assert_rejected_privately()

    def test_string_write_count_fails_closed(self):
        with self.proxy_fdopen(write_mode='string'):
            self.assert_rejected_privately()

    def test_int_subclass_write_count_fails_closed(self):
        with self.proxy_fdopen(write_mode='subclass'):
            self.assert_rejected_privately()

    def test_readback_failure_is_redacted(self):
        with self.proxy_fdopen(read_fault=True):
            self.assert_rejected_privately()

    def test_context_entry_failure_disposes_stream(self):
        with self.proxy_fdopen(enter_fault=True):
            self.assert_rejected_privately()

    def test_fsync_failure_is_redacted(self):
        with patch.object(evidence.os, 'fsync', side_effect=OSError('PRIVATE_CLIENT_PATH')):
            self.assert_rejected_privately()

    def test_fdopen_oserror_closes_unadopted_descriptor(self):
        self._check_fdopen_fault(OSError('PRIVATE_CLIENT_PATH'), propagate=False)

    def test_fdopen_runtimeerror_closes_unadopted_descriptor(self):
        self._check_fdopen_fault(RuntimeError('PRIVATE_CLIENT_PATH'), propagate=False)

    def test_fdopen_keyboard_interrupt_closes_unadopted_descriptor(self):
        self._check_fdopen_fault(KeyboardInterrupt(), propagate=True)

    def _check_fdopen_fault(self, fault, *, propagate):
        original_mkstemp = tempfile.mkstemp
        opened = []
        def mkstemp(*args, **kw):
            fd, path = original_mkstemp(*args, **kw)
            opened.append(fd)
            return fd, path
        with patch.object(evidence.tempfile, 'mkstemp', side_effect=mkstemp), \
             patch.object(evidence.os, 'fdopen', side_effect=fault):
            if propagate:
                with self.assertRaises(KeyboardInterrupt):
                    evidence.publish_report(self.dest, self.payload)
            else:
                self.assert_rejected_privately()
        self.assertEqual(len(opened), 1)
        with self.assertRaises(OSError):
            os.fstat(opened[0])
        self.assertFalse(self.dest.exists())
        self.assertEqual(self.stage_names(), [])

    def test_hardlink_failure_preserves_target_and_redacts(self):
        with patch.object(evidence.os, 'link', side_effect=OSError('PRIVATE_CLIENT_PATH')):
            self.assert_rejected_privately()

    def test_non_json_data_cannot_publish_anything(self):
        for invalid in ({'x': object()}, {'x': float('nan')}):
            with self.subTest(invalid=type(next(iter(invalid.values()))).__name__):
                old = self.payload
                self.payload = invalid
                try:
                    self.assert_rejected_privately()
                finally:
                    self.payload = old


if __name__ == '__main__':
    unittest.main()
