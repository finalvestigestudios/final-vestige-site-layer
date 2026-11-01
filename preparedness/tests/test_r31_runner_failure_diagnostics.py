"""Fail-closed R31 diagnostic coverage for hosted machine HOLD without source leakage."""
from __future__ import annotations
import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import private_release_preflight as preflight

class Tests(unittest.TestCase):
    def get_logs(self, error):
        out, err = io.StringIO(), io.StringIO()
        with patch.object(preflight, 'execute', side_effect=error), \
             contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            status = preflight.main(['--repo-root', '/fake/checkout',
                                     '--expected-head', 'a' * 40])
        self.assertEqual(status, 2)
        return json.loads(out.getvalue()), json.loads(err.getvalue())

    def assert_safe(self, error, expected_gate):
        stdout, stderr = self.get_logs(error)
        self.assertEqual(stderr['gate'], 'R18_PRIVATE_PREFLIGHT_FAILURE')
        self.assertEqual(stderr['release_state'], 'HOLD')
        self.assertIs(stderr['may_publish'], False)
        self.assertEqual(stderr['machine_integrity_result'], 'INCOMPLETE_OR_FAILED')
        self.assertEqual(stderr['failed_step'], expected_gate)
        self.assertEqual(stderr['reason_sha256'], hashlib.sha256(str(error).encode()).hexdigest())
        self.assertNotIn('error', stderr)
        self.assertEqual(stdout['error'], str(error))
        self.assertEqual(stdout['release_state'], 'HOLD')
        self.assertIs(stdout['may_publish'], False)
        self.assertEqual(stdout['machine_integrity_result'], 'INCOMPLETE_OR_FAILED')
        self.assertEqual(stdout['schema_version'], 1)
        self.assertFalse(any(k in stderr for k in ('human_review_complete',
                         'qualified_safety_clearance', 'wordpress_publishing_performed')))

    def test_setup_status_safe(self):
        self.assert_safe(preflight.PreflightHold('trusted Git checkout required'),
                         'setup_or_checkout')

    def test_path_not_leaked(self):
        leak = '/private/auth/token/CUSTOMER_PERSONAL_FILE'
        _, stderr = self.get_logs(preflight.PreflightHold(leak))
        self.assertNotIn('CUSTOMER_PERSONAL_FILE', json.dumps(stderr))
        self.assertEqual(stderr['failed_step'], 'setup_or_checkout')

    def test_expected_no_qualified_clearance(self):
        out, err = self.get_logs(preflight.PreflightHold('publication denied'))
        self.assertNotIn('QD_PASS', json.dumps(out) + json.dumps(err))

for gate, _, _ in preflight.STEPS:
    def make(g):
        def case(self):
            self.assert_safe(preflight.PreflightHold(g + ': exit status 2'), g)
        return case
    setattr(Tests, 'test_step_'+gate, make(gate))

for i, exception in enumerate((ValueError('invalid input'), OSError('network failure'),
                               preflight.PreflightHold('Git HEAD drifted'),
                               preflight.PreflightHold('missing R14 manifest'),
                               preflight.PreflightHold('no native tests'),
                               preflight.PreflightHold('not a trusted source'))):
    def make(e):
        def case(self):
            self.assert_safe(e, 'setup_or_checkout')
        return case
    setattr(Tests, 'test_setup_failure_'+str(i), make(exception))


class NativeFailureClassification(unittest.TestCase):
    def classify(self, stderr, code=1):
        class P:
            returncode = code
            stdout = b""
        P.stderr = stderr
        def fake_run(*args, **kwargs):
            return P()
        step = preflight.Step('private_draft_build',
                              ('fake-python', '-I', '-B', 'preparedness/tools/build.py'),
                              'plain')
        with (patch.object(preflight, 'checked_root', return_value=Path('/tmp')),
              patch.object(preflight, 'git_check', return_value='a'*40),
              patch.object(preflight, 'commands', return_value=(step,))):
            with self.assertRaises(preflight.PreflightHold) as ctx:
                preflight.execute(Path('/tmp'), 'a'*40,
                                  run=fake_run, git_run=fake_run,
                                  python='fake-python')
        return str(ctx.exception)

    def test_safe_exception_name_and_line(self):
        err=(b'Traceback (most recent call last):\n'
             b'  File "/home/private/preparedness/tools/build.py", line 387, in build_article\n'
             b'    secret = sensitive_statement\n'
             b"KeyError: 'sensitive_patient_value'\n")
        msg = self.classify(err)
        self.assertIn('private_draft_build: exit status 1', msg)
        self.assertIn('; exception KeyError; source line 387', msg)
        self.assertNotIn('sensitive_', msg)
        self.assertNotIn('/home/private', msg)

    def test_claim_corpus_failure_reports_source_line_not_private_value(self):
        err=(b'Traceback (most recent call last):\n'
             b'  File "/home/runner/preparedness/tools/claim_corpus_release_gate.py", line 171, in audit_corpus\n'
             b'    raise ValueError("PRIVATE_CASE")\n'
             b'ValueError: PRIVATE_CASE\n')
        msg=self.classify(err)
        self.assertIn('exception ValueError; source line 171', msg)
        self.assertNotIn('PRIVATE_CASE', msg)

    def test_no_traceback_not_reported_as_exception(self):
        self.assertEqual(self.classify(b'ERROR unsafe source',2),
                         'private_draft_build: exit status 2')

    def test_non_allowlisted_exception_not_exposed(self):
        msg = self.classify(b'CustomPrivateDataError: private\n')
        self.assertEqual(msg,'private_draft_build: exit status 1')

    def test_unsafe_path_is_not_echoed(self):
        err=(b'  File "/customer/medical/preparedness/tools/build.py", '
             b'line 7, in main\nValueError: CUSTOMER PRIVATE 9988')
        msg=self.classify(err)
        self.assertIn('ValueError; source line 7',msg)
        self.assertNotIn('CUSTOMER',msg)
        self.assertNotIn('/customer/',msg)

    def test_non_utf8_traceback_fails_to_safe_category(self):
        msg=self.classify(b'\xff\xfe\x00')
        self.assertEqual(msg,'private_draft_build: exit status 1')

    def test_large_stderr_does_not_leak(self):
        msg=self.classify(b'A'*2_000_001)
        self.assertEqual(msg,'private_draft_build: exit status 1')

if __name__ == '__main__':
    unittest.main()
