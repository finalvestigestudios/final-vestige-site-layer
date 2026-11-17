"""R428 isolated synthetic regressions: Git environment cannot falsify R427 custody.

Runs only in disposable local git fixtures. No articles, URLs, source flags,
CMS, platform data or merchant APIs are accessed. PASS != QD/release PASS.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1] / 'tools'
TESTS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(TESTS))
import r427_execution_closure_gate as gate
from test_r427_execution_closure_gate import fixture, cmd

ENV_BASE = {'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONNOUSERSITE': '1'}
GIT_INJECTION_KEYS = (
    'GIT_DIR', 'GIT_WORK_TREE', 'GIT_COMMON_DIR', 'GIT_INDEX_FILE',
    'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES',
    'GIT_NAMESPACE', 'GIT_CEILING_DIRECTORIES', 'GIT_EXEC_PATH',
    'GIT_TEMPLATE_DIR', 'GIT_CONFIG_GLOBAL', 'GIT_CONFIG_SYSTEM',
    'GIT_CONFIG_PARAMETERS', 'GIT_CONFIG_COUNT', 'GIT_CONFIG_KEY_0',
    'GIT_CONFIG_VALUE_0', 'GIT_CONFIG_KEY_1', 'GIT_CONFIG_VALUE_1',
    'GIT_TRACE', 'GIT_TRACE_SETUP', 'GIT_TRACE_PERFORMANCE',
    'GIT_TRACE_PACKET', 'GIT_TRACE2', 'GIT_TRACE2_EVENT',
    'GIT_TRACE2_PERF', 'GIT_TRACE2_PARENT_NAME', 'GIT_TRACE_REFS',
    'GIT_TRACE_SHALLOW', 'GIT_TRACE_CURL', 'GIT_TRACE_CURL_NO_DATA',
    'GIT_TRACE2_CONFIG_PARAMS', 'GIT_TRACE2_ENV_VARS', 'GIT_SSH',
    'GIT_SSH_COMMAND', 'GIT_ASKPASS', 'GIT_PROXY_COMMAND',
    'GIT_EXTERNAL_DIFF', 'GIT_DIFF_OPTS', 'GIT_OPTIONAL_LOCKS_EXTRA',
    'GIT_FUTURE_UNKNOWN_VARIABLE',
)


class GitSandboxTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source, cls.base, cls.head = fixture()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.source)

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='r428-git-guard-'))
        self.repo = self.tmp/'repo'
        shutil.copytree(self.source, self.repo)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def audit(self, env=None):
        return gate.closure(self.repo, self.head, expected_base=self.base,
                            env=ENV_BASE if env is None else env)

    def test_unpoisoned_fixture_passes_structure_not_publication(self):
        result = self.audit()
        self.assertTrue(result['execution_input_closure_ok'], result)
        self.assertFalse(result['eligible'])
        self.assertFalse(result['publication_approved'])
        self.assertFalse(result['qualified_safety_approved'])
        self.assertFalse(result['paid_activation_approved'])
        self.assertEqual(result['source_claim_safety_review'], 'HUMAN_REVIEW_REQUIRED')

    def test_real_git_head_still_used(self):
        self.assertEqual(gate.git(self.repo, 'rev-parse', 'HEAD').decode(), self.head)

    def test_git_env_is_minimized(self):
        with patch.dict(os.environ, {'GIT_INDEX_FILE': '/nonexistent/forged-index',
                                    'GIT_TRACE': str(self.tmp/'trace')}, clear=False):
            safe = gate.sanitized_git_env()
        for key in ('GIT_INDEX_FILE', 'GIT_TRACE', 'GIT_CONFIG_COUNT',
                    'GIT_OBJECT_DIRECTORY', 'GIT_CONFIG_PARAMETERS'):
            self.assertNotIn(key, safe)
        self.assertEqual(safe['GIT_OPTIONAL_LOCKS'], '0')
        self.assertEqual(safe['GIT_CONFIG_GLOBAL'], os.devnull)
        self.assertEqual(safe['GIT_CONFIG_SYSTEM'], os.devnull)
        self.assertEqual(safe['GIT_TERMINAL_PROMPT'], '0')
        self.assertEqual(safe['GIT_NO_LAZY_FETCH'], '1')

    def test_external_git_trace_does_not_write_any_file(self):
        target = self.tmp/'git-trace-should-not-exist'
        with patch.dict(os.environ, {'GIT_TRACE': str(target)}, clear=False):
            result = self.audit()
        self.assertTrue(result['execution_input_closure_ok'], result)
        self.assertFalse(target.exists(), 'Git was invoked with untrusted tracing')

    def test_external_git_trace2_event_does_not_write(self):
        target = self.tmp/'trace2-event-should-not-exist'
        with patch.dict(os.environ, {'GIT_TRACE2_EVENT': str(target)}, clear=False):
            result = self.audit()
        self.assertTrue(result['execution_input_closure_ok'], result)
        self.assertFalse(target.exists())

    def test_external_git_trace_performance_does_not_write(self):
        target = self.tmp/'trace-performance-should-not-exist'
        with patch.dict(os.environ, {'GIT_TRACE_PERFORMANCE': str(target)}, clear=False):
            result = self.audit()
        self.assertTrue(result['execution_input_closure_ok'], result)
        self.assertFalse(target.exists())

    def test_external_wrong_git_dir_cannot_substitute_repo(self):
        with patch.dict(os.environ, {'GIT_DIR': str(self.tmp/'attacker-git')}, clear=False):
            result = self.audit()
        self.assertTrue(result['execution_input_closure_ok'], result)

    def test_external_wrong_worktree_cannot_substitute_repo(self):
        with patch.dict(os.environ, {'GIT_WORK_TREE': str(self.tmp/'attacker-worktree')}, clear=False):
            result = self.audit()
        self.assertTrue(result['execution_input_closure_ok'], result)

    def test_external_wrong_index_cannot_substitute_repo(self):
        with patch.dict(os.environ, {'GIT_INDEX_FILE': str(self.tmp/'attacker-index')}, clear=False):
            result = self.audit()
        self.assertTrue(result['execution_input_closure_ok'], result)

    def test_external_git_config_count_cannot_inject(self):
        override = {'GIT_CONFIG_COUNT': '1',
                    'GIT_CONFIG_KEY_0': 'core.fsmonitor',
                    'GIT_CONFIG_VALUE_0': 'true'}
        with patch.dict(os.environ, override, clear=False):
            result = self.audit()
        self.assertTrue(result['execution_input_closure_ok'], result)

    def test_external_git_config_global_ignored(self):
        hostile = self.tmp/'injected-global-config'
        hostile.write_text('[core]\nfsmonitor = true\n')
        with patch.dict(os.environ, {'GIT_CONFIG_GLOBAL': str(hostile)}, clear=False):
            result = self.audit()
        self.assertTrue(result['execution_input_closure_ok'], result)

    def test_local_fsmonitor_override_does_not_run_script(self):
        marker = self.tmp/'fsmonitor-ran'
        probe = self.tmp/'fsmonitor.sh'
        probe.write_text('#!/bin/sh\n: > '+str(marker)+'\nexit 0\n')
        probe.chmod(0o755)
        cmd(self.repo, 'config', 'core.fsmonitor', str(probe))
        result = self.audit()
        self.assertTrue(result['execution_input_closure_ok'], result)
        self.assertFalse(marker.exists(), 'repo config executed external fsmonitor')

    def test_rejects_malicious_git_input_even_with_clean_host(self):
        env = {**ENV_BASE, 'GIT_TRACE': str(self.tmp/'trace')}
        result = self.audit(env)
        self.assertFalse(result['execution_input_closure_ok'])
        self.assertIn('R427_GIT_ENV_OVERRIDE_GIT_TRACE', result['errors'])
        self.assertFalse(result['eligible'])
        self.assertFalse(result['publication_approved'])
        self.assertFalse((self.tmp/'trace').exists())

    def test_known_safe_ci_git_vars_only(self):
        env = {**ENV_BASE, 'GIT_TERMINAL_PROMPT': '0',
               'GIT_OPTIONAL_LOCKS': '0', 'GIT_CONFIG_NOSYSTEM': '1'}
        result = self.audit(env)
        self.assertTrue(result['execution_input_closure_ok'], result)
        self.assertFalse(result['eligible'])

    def test_report_deterministic_across_benign_git_vars(self):
        a = self.audit()
        b = self.audit({**ENV_BASE, 'GIT_TERMINAL_PROMPT': '0'})
        self.assertEqual(a['review_only_closure_sha256'], b['review_only_closure_sha256'])

    def test_untracked_python_still_holds(self):
        p = self.repo/'preparedness/tools/unsafe_shadow.py'
        p.write_text('malicious=True\n')
        result = self.audit()
        self.assertFalse(result['execution_input_closure_ok'])
        self.assertIn('R427_UNTRACKED_PYTHON_SOURCE', result['errors'])

    def test_modified_source_still_holds(self):
        p = self.repo/gate.REQUIRED[0]
        p.write_text('changed=True\n')
        result = self.audit()
        self.assertFalse(result['execution_input_closure_ok'])
        self.assertIn('R427_UNCOMMITTED_OR_UNTRACKED_WORKTREE', result['errors'])


for name in GIT_INJECTION_KEYS:
    def verify(self, name=name):
        result = self.audit({**ENV_BASE, name: 'attacker-controlled'})
        self.assertFalse(result['execution_input_closure_ok'], result)
        self.assertIn('R427_GIT_ENV_OVERRIDE_'+name, result['errors'])
        self.assertFalse(result['eligible'])
        self.assertFalse(result['publication_approved'])
        self.assertIsNone(result['review_only_closure_sha256'])
    setattr(GitSandboxTests, 'test_git_env_hold_'+name.lower(), verify)


if __name__ == '__main__':
    unittest.main()
