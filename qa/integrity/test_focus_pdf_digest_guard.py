"""Local-only regression tests for cautious media checksum attribution."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from focus_pdf_digest_guard import check, _meta, main

BLOB=b"%PDF-1.7\n1 0 obj<<>>endobj\n%%EOF\n"
HASH=hashlib.sha256(BLOB).hexdigest()
URL=("https://finalvestige.com/wp-content/uploads/2026/10/"
     "Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf")

def metadata(sha=HASH):
    return {"id":1737,"source_url":URL,"mime_type":"application/pdf",
            "media_details":{"filesize":len(BLOB)},"description":"FVS Complete Edition; SHA256 "+sha}

class IntegrityTests(unittest.TestCase):
    def test_sane_metadata_parses(self):
        self.assertEqual(_meta(metadata())["metadata_sha256"],HASH)
    def test_metadata_wrapper_supported(self):
        self.assertEqual(_meta({"data":metadata()})["media_id"],1737)
    def test_wrong_media_id_rejected(self):
        m=metadata();m["id"]=44
        with self.assertRaises(ValueError):_meta(m)
    def test_wrong_host_rejected(self):
        m=metadata();m["source_url"]=URL.replace("finalvestige.com", "evil.example")
        with self.assertRaises(ValueError):_meta(m)
    def test_http_rejected(self):
        m=metadata();m["source_url"]=URL.replace("https", "http",1)
        with self.assertRaises(ValueError):_meta(m)
    def test_credentials_in_url_rejected(self):
        m=metadata();m["source_url"]=URL.replace("https://", "https://user:pass@")
        with self.assertRaises(ValueError):_meta(m)
    def test_wrong_pdf_name_rejected(self):
        m=metadata();m["source_url"]=URL.replace("Complete_Edition", "Draft_Edition")
        with self.assertRaises(ValueError):_meta(m)
    def test_conflicting_description_hashes_rejected(self):
        m=metadata();m["description"]+=" SHA256 "+"0"*64
        with self.assertRaises(ValueError):_meta(m)
    def test_claim_disagreement_not_called_public_failure(self):
        r=check(metadata(),"0"*64)
        self.assertEqual(r["result"],"CONFLICTING_DIGEST_CLAIMS")
        self.assertFalse(r["hosted_pdf_verified"])
    def test_claim_agreement_not_called_public_pass(self):
        r=check(metadata(),HASH)
        self.assertEqual(r["result"],"OBSERVED_CLAIM_AGREES_NOT_PUBLIC_PROOF")
        self.assertFalse(r["hosted_pdf_verified"])
    def test_missing_claim_is_inconclusive(self):
        m=metadata();m["description"]="A real PDF"
        self.assertEqual(check(m)["result"],"INSUFFICIENT_EVIDENCE")
    def test_bad_comparison_sha_rejected(self):
        with self.assertRaises(ValueError):check(metadata(),"bad hash")
    def test_valid_local_candidate_matches_but_does_not_verify_public(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"candidate.pdf";path.write_bytes(BLOB)
            r=check(metadata(),candidate_file=path)
            self.assertEqual(r["result"],"LOCAL_CANDIDATE_AGREES_NOT_PUBLIC_PROOF")
            self.assertFalse(r["hosted_pdf_verified"])
    def test_local_candidate_different_sha_with_same_size(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"candidate.pdf";path.write_bytes(BLOB.replace(b"1.7",b"1.6"))
            r=check(metadata(),candidate_file=path)
            self.assertEqual(r["result"],"LOCAL_CANDIDATE_DIFFERS_NOT_PUBLIC_PROOF")
            self.assertTrue(r["local_candidate"]["matches_recorded_size"])
    def test_invalid_local_pdf_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"candidate.pdf";path.write_bytes(b"not actually pdf")
            with self.assertRaises(ValueError):check(metadata(),candidate_file=path)
    def test_oversized_file_rejected_before_reading(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"big.pdf"
            with path.open("wb") as f:f.truncate(16*1024*1024+1)
            with self.assertRaises(ValueError):check(metadata(),candidate_file=path)
    def test_cli_no_public_pass_claim(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"wp.json";path.write_text(json.dumps(metadata()))
            with patch("builtins.print") as output:
                rc=main(["--media-json",str(path),"--independent-sha256","0"*64])
            self.assertEqual(rc,1)
            self.assertIn("CONFLICTING_DIGEST_CLAIMS",output.call_args.args[0])
    def test_cli_invalid_input_exit2(self):
        with patch("builtins.print") as output:
            rc=main(["--media-json","/nonexistent/path.json"])
        self.assertEqual(rc,2)
        self.assertIn("INVALID_EVIDENCE",output.call_args.args[0])

if __name__=="__main__": unittest.main()
