#!/usr/bin/env python3
"""Source-based and negative runtime controls; no network or external runtime install."""
from pathlib import Path
import importlib.util
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('engine', HERE / 'check_playground_runtime.py')
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)


class EngineVersionTests(unittest.TestCase):
    def test_minimum_supported_versions(self):
        self.assertIsNone(engine.verify_versions('v24.18.0', '11.16.0'))

    def test_higher_supported_versions(self):
        self.assertIsNone(engine.verify_versions('v25.0.0', '12.0.0'))

    def test_actual_failed_runner_versions_rejected(self):
        with self.assertRaisesRegex(ValueError, 'UNSUPPORTED_NODE_NPM_ENGINE'):
            engine.verify_versions('v22.23.4', '10.9.9')

    def test_older_node_rejected(self):
        with self.assertRaisesRegex(ValueError, 'UNSUPPORTED_NODE_NPM_ENGINE'):
            engine.verify_versions('v24.17.9', '11.16.0')

    def test_older_npm_rejected(self):
        with self.assertRaisesRegex(ValueError, 'UNSUPPORTED_NODE_NPM_ENGINE'):
            engine.verify_versions('v24.18.0', '11.15.9')

    def test_undocumented_prerelease_rejected(self):
        with self.assertRaisesRegex(ValueError, 'VERSION_UNREADABLE'):
            engine.verify_versions('v24.18.0-beta.1', '11.16.0')

    def test_unparseable_rejected(self):
        with self.assertRaisesRegex(ValueError, 'VERSION_UNREADABLE'):
            engine.verify_versions('unknown', '11.16.0')

    def test_pinned_expected_cli(self):
        self.assertIsNone(engine.verify_cli_argv(['npx', engine.CLI_SPEC, 'server']))

    def test_latest_cli_drift_rejected(self):
        with self.assertRaisesRegex(ValueError, 'UNPINNED_OR_UNEXPECTED_CLI'):
            engine.verify_cli_argv(['npx', '@wp-playground/cli@latest', 'server'])

    def test_untrusted_executable_rejected(self):
        with self.assertRaisesRegex(ValueError, 'UNPINNED_OR_UNEXPECTED_CLI'):
            engine.verify_cli_argv(['bash', '-c', 'echo', 'server'])


if __name__ == '__main__':
    unittest.main()
