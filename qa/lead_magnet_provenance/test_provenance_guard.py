"""Self-contained fixtures: never access the network, WordPress, or subscribers."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from provenance_guard import audit, main, pdf_facts


PDF_A = b"%PDF-1.4\noriginal reference\n%%EOF\n"
PDF_B = b"%PDF-1.4\nnew version with different content\n%%EOF\n"
HASH_A = hashlib.sha256(PDF_A).hexdigest()
HASH_B = hashlib.sha256(PDF_B).hexdigest()


def media(size=None, sha=None, media_id=1737, url="https://finalvestige.com/wp-content/uploads/2026/10/focus.pdf"):
    return {"id": media_id, "source_url": url, "media_details": {"filesize": size or len(PDF_A)},
            "caption": f"<p>52 pages; SHA256 {sha or HASH_A}</p>",
            "description": f"<p>SHA256 {sha or HASH_A}</p>"}


class OfflineProvenanceTests(unittest.TestCase):
    def test_wp_metadata_reuses_reference_digest_but_different_size(self):
        out = audit(media(size=599946), PDF_A)
        self.assertEqual(out["status"], "FAIL")
        self.assertIn("REFERENCE_DIGEST_REUSED_FOR_DIFFERENT_SIZE_ASSET", out["errors"])
        self.assertIn("HOSTED_PDF_BYTES_NOT_PROVIDED", out["warnings"])

    def test_same_size_without_hosted_bytes_is_hold(self):
        self.assertEqual(audit(media(), PDF_A)["status"], "HOLD")

    def test_exact_local_pdf_matches_claim_and_size(self):
        self.assertEqual(audit(media(), PDF_A, PDF_A)["status"], "PASS_LOCAL_BYTES")

    def test_hosted_copy_differs_from_published_digest(self):
        out = audit(media(size=len(PDF_B)), PDF_A, PDF_B)
        self.assertIn("HOSTED_COPY_SHA256_DISAGREES_WITH_PUBLISHED_CLAIM", out["errors"])

    def test_newer_release_with_correct_new_digest_not_required_to_match_reference(self):
        out = audit(media(size=len(PDF_B), sha=HASH_B), PDF_A, PDF_B)
        self.assertEqual(out["status"], "PASS_LOCAL_BYTES")
        self.assertIn("HOSTED_COPY_DIFFERS_FROM_ARCHIVED_REFERENCE_VERSION", out["warnings"])

    def test_metadata_claims_conflict(self):
        r = media()
        r["description"] = "SHA256 " + HASH_B
        self.assertIn("CONFLICTING_PUBLISHED_SHA256_CLAIMS", audit(r, PDF_A)["errors"])

    def test_no_sha_claim_is_hold_even_when_local_file_matches(self):
        r = media()
        r["description"] = "No hash"
        r["caption"] = "No hash"
        self.assertEqual(audit(r, PDF_A, PDF_A)["status"], "HOLD")

    def test_rejects_external_url_and_insecure_scheme(self):
        for url in ["http://finalvestige.com/file.pdf", "https://evil.example/file.pdf",
                    "https://user:pw@finalvestige.com/file.pdf", "https://finalvestige.com/file.txt"]:
            with self.subTest(url=url), self.assertRaises(ValueError):
                audit(media(url=url), PDF_A)

    def test_rejects_wrong_id(self):
        with self.assertRaises(ValueError):
            audit(media(media_id=1738), PDF_A)

    def test_wp_rendered_caption_dict_supported(self):
        r = media()
        r["caption"] = {"rendered": "<p>SHA256 " + HASH_A + "</p>"}
        self.assertEqual(audit({"data": r}, PDF_A)["status"], "HOLD")

    def test_rejects_missing_or_boolean_size(self):
        for size in [None, False, -1, "123"]:
            with self.subTest(size=size), self.assertRaises(ValueError):
                r = media()
                r["media_details"]["filesize"] = size
                audit(r, PDF_A)

    def test_rejects_pdf_signature_mismatch(self):
        r = audit(media(), b"not a PDF", b"not a PDF")
        self.assertIn("REFERENCE_PDF_SIGNATURE_INVALID", r["errors"])
        self.assertIn("HOSTED_COPY_PDF_SIGNATURE_INVALID", r["errors"])

    def test_hosted_byte_size_mismatch(self):
        r = audit(media(), PDF_A, PDF_B)
        self.assertIn("HOSTED_COPY_SIZE_DISAGREES_WITH_WP_RECORD", r["errors"])

    def test_cli_exit_fail_hold_and_pass(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ref = root / "ref.pdf"
            rec = root / "media.json"
            ref.write_bytes(PDF_A)
            rec.write_text(json.dumps(media(size=599946)))
            self.assertEqual(main(["--media", str(rec), "--reference", str(ref)]), 1)
            rec.write_text(json.dumps(media()))
            self.assertEqual(main(["--media", str(rec), "--reference", str(ref)]), 2)
            self.assertEqual(main(["--media", str(rec), "--reference", str(ref), "--hosted", str(ref)]), 0)

    def test_unparseable_input_returns_hold_not_false_pass(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ref = root / "ref.pdf"
            rec = root / "media.json"
            ref.write_bytes(PDF_A)
            rec.write_text("unparseable")
            self.assertEqual(main(["--media", str(rec), "--reference", str(ref)]), 2)

    def test_pdf_facts_records_digest_and_bytes(self):
        facts = pdf_facts(PDF_A)
        self.assertEqual(facts["bytes"], len(PDF_A))
        self.assertEqual(facts["sha256"], HASH_A)
        self.assertTrue(facts["pdf_signature"])


if __name__ == "__main__":
    unittest.main()
