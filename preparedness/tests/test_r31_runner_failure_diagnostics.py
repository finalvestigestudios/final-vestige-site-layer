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

if __name__ == '__main__':
    unittest.main()
