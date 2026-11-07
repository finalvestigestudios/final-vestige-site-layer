"""Review-only local WordPress Playground runtime reproducibility controls.

No npm, WordPress, theme, subscriber, or production site is touched here.
"""
import ast
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import run_local_wordpress_acceptance as mod

class RuntimeSourcePins(unittest.TestCase):
    def setUp(self):
        self.zip=Path('/tmp/fv-ex2-pinned.zip')

    def test_exact_documented_release_versions(self):
        self.assertEqual(mod.PLAYGROUND_CLI_VERSION, '3.1.55')
        self.assertEqual(mod.WORDPRESS_CORE_VERSION, '7.1.4')
        self.assertEqual(mod.PLAYGROUND_PHP_VERSION, '8.3')

    def test_invocation_is_pinned_not_latest(self):
        cmd=mod.playground_launch_command('/usr/local/bin/npx', 9400, 'http://127.0.0.1:9400/', self.zip)
        self.assertIn('@wp-playground/cli@3.1.55',cmd)
        self.assertIn('--wp=7.1.4',cmd)
        self.assertIn('--php=8.3',cmd)
        self.assertNotIn('@wp-playground/cli@latest',cmd)
        self.assertEqual(cmd[-1], '--blueprint='+str(self.zip.resolve()))
        self.assertEqual(cmd[3], 'server')

    def test_reject_prod_domain(self):
        with self.assertRaisesRegex(ValueError, 'REFUSE_NON_LOOPBACK_LAUNCH'):
            mod.playground_launch_command('npx',9400,'https://finalvestige.com/',self.zip)

    def test_reject_spoofed_loopback(self):
        with self.assertRaisesRegex(ValueError, 'REFUSE_NON_LOOPBACK_LAUNCH'):
            mod.playground_launch_command('npx',9400,'http://127.0.0.1.evil.example:9400/',self.zip)

    def test_reject_url_port_drift(self):
        with self.assertRaisesRegex(ValueError, 'REFUSE_NON_LOOPBACK_LAUNCH'):
            mod.playground_launch_command('npx',9401,'http://127.0.0.1:9400/',self.zip)

    def test_reject_out_of_range(self):
        with self.assertRaisesRegex(ValueError, 'REFUSE_PORT_OUTSIDE_REVIEW_RANGE'):
            mod.playground_launch_command('npx',9500,'http://127.0.0.1:9500/',self.zip)

    def test_safe_alternate_port(self):
        cmd=mod.playground_launch_command('npx',9470,'http://127.0.0.1:9470/',self.zip)
        self.assertIn('--port=9470',cmd)
        self.assertIn('--site-url=http://127.0.0.1:9470/',cmd)

    def test_original_blueprint_pin_is_unchanged(self):
        self.assertEqual(mod.BUNDLE_SHA256,'9833800a112027b17dfec154358d7b630e258feb581820b749ca26ab88ffe69d')
        self.assertEqual(mod.ASSEMBLER_COMMIT,'75faa8a1e0367a37c2638250a3c9ed0a0f8c0b7f')

    def test_reject_unreviewed_runtime_drift(self):
        # Tampering the pinned runtime raises an assertion in the regression gate.
        with patch.object(mod,'PLAYGROUND_CLI_VERSION','latest'):
            self.assertNotEqual(mod.playground_launch_command('npx',9400,'http://127.0.0.1:9400/',self.zip)[2],
                                '@wp-playground/cli@3.1.55')

    def test_no_source_content_changed(self):
        src=Path(mod.__file__).read_text()
        self.assertIn('def attest(bundle)',src)
        self.assertIn('wordpress_rest_identity(url, opener)',src)
        self.assertIn('refuse_occupied_port(port)',src)
        self.assertIn("'release':'HOLD'",src)

if __name__=='__main__':
    unittest.main()
