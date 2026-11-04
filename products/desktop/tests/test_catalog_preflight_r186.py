"""R186: six-product pre-release catalog hard hold and accessibility checks."""
from __future__ import annotations

import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

import catalog_preflight_r186 as gate


def catalog() -> str:
    top = ('<!-- wp:group {"align":"wide","layout":{"type":"constrained"}} -->\n'
           '<div class="wp-block-group alignwide">\n'
           '<h1 class="wp-block-heading">Tools for work that cannot afford guesswork.</h1>\n'
           '<p><strong>Release status:</strong> Products below are in active development. '
           'No downloads are available until builds pass testing, security review and verification. '
           'Initial platform: Windows 64-bit.</p>\n'
           '<h2>Free desktop utilities</h2>\n')
    chunks = []
    for index, (app, status) in enumerate(gate.APPS):
        if index == 4:
            chunks.append('<h2>Professional editions</h2>')
        chunks.append(f'<h3>{app}</h3><p>Private offline review tool.</p><p><strong>{status}</strong></p>')
    tail = ('<h2>Pilot with us</h2><p>Operators can contact us.</p>'
            '<p><a href="https://finalvestige.com/contact/">Contact Final Vestige about a pilot</a></p>'
            '<p>These applications are aids for review, not a substitute for accountants, '
            'auditors, attorneys or organizational approvals. '
            'Do not use pre-release builds with sensitive production data.</p>'
            '</div><!-- /wp:group -->')
    return top + ''.join(chunks) + tail


class CatalogPreflightR186(unittest.TestCase):
    def assert_rejected(self, raw) -> None:
        with self.assertRaises(gate.CatalogPreflightError):
            gate.verify_catalog(raw)

    def test_valid_static_catalog_passes_without_approval(self):
        result = gate.verify_catalog(catalog().encode())
        self.assertEqual(result['result'], 'PASS_STATIC_DRAFT_ONLY')
        self.assertEqual((result['apps'], result['free'], result['premium']), (6, 4, 2))
        self.assertFalse(result['downloads_verified'])
        self.assertFalse(result['premium_access_verified'])
        self.assertFalse(result['qd_approved'])
        self.assertFalse(result['site_publication_authorized'])

    def test_deterministic_report(self):
        raw = catalog().encode()
        self.assertEqual(gate.verify_catalog(raw), gate.verify_catalog(raw))

    def test_reject_untrusted_input_type(self):
        self.assert_rejected(catalog())

    def test_reject_invalid_utf8(self):
        self.assert_rejected(catalog().encode() + b'\xff')

    def test_reject_oversize(self):
        self.assert_rejected(catalog().encode() + b' ' * gate.MAX_CATALOG_BYTES)

    def test_reject_nul(self):
        self.assert_rejected(catalog().encode() + b'\x00')

    def test_reject_script(self):
        self.assert_rejected(catalog().replace('<h2>Pilot with us</h2>', '<script>fetch("/private")</script><h2>Pilot with us</h2>').encode())

    def test_reject_iframe(self):
        self.assert_rejected(catalog().replace('<h2>Pilot with us</h2>', '<iframe src="https://example.com"></iframe><h2>Pilot with us</h2>').encode())

    def test_reject_form(self):
        self.assert_rejected(catalog().replace('<h2>Pilot with us</h2>', '<form action="/pay"></form><h2>Pilot with us</h2>').encode())

    def test_reject_image_tracking(self):
        self.assert_rejected(catalog().replace('<h2>Pilot with us</h2>', '<img src="https://tracker.test/pixel"><h2>Pilot with us</h2>').encode())

    def test_reject_inline_event_handler(self):
        self.assert_rejected(catalog().replace('<h1 ', '<h1 onclick="alert(1)" ', 1).encode())

    def test_reject_data_attribute(self):
        self.assert_rejected(catalog().replace('<h1 ', '<h1 data-premium-token="x" ', 1).encode())

    def test_reject_external_premium_link(self):
        self.assert_rejected(catalog().replace(gate.CONTACT_URL, 'https://download.test/GrantAuditStudioPro.exe').encode())

    def test_reject_external_free_download(self):
        self.assert_rejected(catalog().replace(gate.CONTACT_URL, 'https://finalvestige.com/free/LedgerDiffLite.exe').encode())

    def test_reject_additional_download_anchor(self):
        self.assert_rejected(catalog().replace('</div>', '<a href="https://finalvestige.com/contact/">Download now</a></div>').encode())

    def test_reject_download_attribute(self):
        self.assert_rejected(catalog().replace('<a href=', '<a download="GrantAuditStudioPro.exe" href=').encode())

    def test_reject_duplicate_attribute(self):
        self.assert_rejected(catalog().replace('<a href=', '<a href="https://finalvestige.com/contact/" href=').encode())

    def test_reject_fake_product_name(self):
        self.assert_rejected(catalog().replace('<h3>SpendMap Lite</h3>', '<h3>SpendMap Pro</h3>').encode())

    def test_reject_missing_sixth_app(self):
        self.assert_rejected(catalog().replace('<h3>ProcureGuard Studio Pro</h3>', '').encode())

    def test_reject_false_release_claim(self):
        self.assert_rejected(catalog().replace('No downloads are available until builds pass testing, security review and verification.', 'Download now.').encode())

    def test_reject_free_status_promoted_to_available(self):
        self.assert_rejected(catalog().replace('FREE · IN DEVELOPMENT', 'FREE · AVAILABLE NOW', 1).encode())

    def test_reject_premium_status_promoted_to_public(self):
        self.assert_rejected(catalog().replace('PREMIUM · PRIVATE DEVELOPMENT PREVIEW', 'PREMIUM · PUBLIC DOWNLOAD', 1).encode())

    def test_reject_no_human_review_disclaimer(self):
        self.assert_rejected(catalog().replace('not a substitute for accountants, auditors, attorneys or organizational approvals.', 'fully automated decisions are always correct.').encode())

    def test_reject_removed_private_data_warning(self):
        self.assert_rejected(catalog().replace('Do not use pre-release builds with sensitive production data.', '').encode())

    def test_reject_heading_level_mismatch(self):
        self.assert_rejected(catalog().replace('<h2>Professional editions</h2>', '<h3>Professional editions</h3>').encode())

    def test_reject_truncated_script_tag(self):
        self.assert_rejected((catalog() + '<script').encode())

    def test_reject_processing_instruction(self):
        self.assert_rejected(catalog().replace('<h2>Pilot with us</h2>', '<?php echo 1 ?><h2>Pilot with us</h2>').encode())

    def test_reject_unknown_doctype(self):
        self.assert_rejected(('<!DOCTYPE html>' + catalog()).encode())

    def test_reject_unclosed_markup(self):
        self.assert_rejected(catalog().replace('</div><!-- /wp:group -->', '<!-- /wp:group -->').encode())

    def test_reject_bidi_override(self):
        self.assert_rejected(catalog().replace('SpendMap Lite', 'SpendMap\u202e Lite').encode())

    def test_reject_hidden_comment_payload(self):
        self.assert_rejected(catalog().replace('<!-- /wp:group -->', '<!-- secret download path --><!-- /wp:group -->').encode())

    def test_reject_hidden_gutenberg_json_premium_link(self):
        injected = '<!-- wp:paragraph {"href":"https://leak.test/GrantAuditStudioPro.exe"} -->'
        self.assert_rejected(catalog().replace('<!-- /wp:group -->', injected + '<!-- /wp:group -->').encode())

    def test_reject_unknown_gutenberg_custom_block(self):
        injected = '<!-- wp:custom-html -->'
        self.assert_rejected(catalog().replace('<!-- /wp:group -->', injected + '<!-- /wp:group -->').encode())

    def test_accept_gutenberg_block_comments_and_entities(self):
        good = catalog().replace('No downloads are available', 'No downloads are available')
        self.assertEqual(gate.verify_catalog(good.encode())['contact_links'], 1)

    def test_cli_no_file_leaks_no_publication(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'catalog.html'
            path.write_bytes(catalog().encode())
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(gate.main([str(path)]), 0)
            self.assertIn('QD/launch HOLD', output.getvalue())
            path.write_text('<script>secret</script>')
            error = io.StringIO()
            with redirect_stderr(error):
                self.assertEqual(gate.main([str(path)]), 1)
            self.assertNotIn(str(path), error.getvalue())
            self.assertNotIn('secret', error.getvalue())

    def test_cli_first_read_atime_change_is_not_source_mutation(self):
        # Real-world atime advances on an otherwise unchanged source file.
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'catalog.html'
            path.write_bytes(catalog().encode())
            os.utime(path, (1, 1))
            with redirect_stdout(io.StringIO()):
                self.assertEqual(gate.main([str(path)]), 0)

    def test_cli_symlink_rejected_without_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'private.html'
            target.write_bytes(catalog().encode())
            link = Path(tmp) / 'catalog.html'
            try:
                link.symlink_to(target)
            except (OSError, NotImplementedError):
                return  # filesystem cannot create symlink; other tests still run
            with redirect_stderr(io.StringIO()):
                self.assertEqual(gate.main([str(link)]), 1)
            self.assertEqual(target.read_bytes(), catalog().encode())

    def test_actual_catalog_when_checkout_present(self):
        source = Path(__file__).resolve().parents[1] / 'site' / 'software-catalog.gutenberg.html'
        if source.exists():
            self.assertEqual(gate.verify_catalog(source.read_bytes())['apps'], 6)


if __name__ == '__main__':
    unittest.main()
