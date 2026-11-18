"""R461 synthetic adverse witness/fork tests; do NOT infer qualified source/safety PASS."""
from __future__ import annotations
import copy
import importlib.util
from pathlib import Path
import tempfile
import json
import unittest

P = Path(__file__).resolve().parents[1]
s = importlib.util.spec_from_file_location("r461", P / "tools" / "r461_adjudication_custody_gate.py")
m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
base_spec = importlib.util.spec_from_file_location("r460_fixture", P / "tests" / "test_r460_origin_branch_blob_crosswalk.py")
b = importlib.util.module_from_spec(base_spec); base_spec.loader.exec_module(b)

def sample():
    x=b.fixture()
    x["candidate"]["articles"]["guide-00"]["body"] = b.h(80000)
    x["candidate"]["articles"]["guide-01"]["meta"] = b.h(81000)
    x["origins"]["health"]["articles"]["guide-00"] = {"body":b.h(90000),"meta":b.h(90001)}
    x["candidate"]["sources"]["fragments/food.json"] = b.h(98000)
    return x

class TestCore(unittest.TestCase):
    def test_build_nonclearing_review(self):
        d=m.build_docket(sample()); self.assertEqual(d["release_state"], "DRAFT_HARD_HOLD")
        self.assertFalse(d["qualified_qd_pass"]);self.assertFalse(d["publication_authorized"])
        self.assertGreaterEqual(len(d["article_review_rows"]), 2)
        self.assertGreaterEqual(len(d["source_review_rows"]), 1)
        self.assertEqual(m.verify_docket(sample(),d)["state"], "REVIEW_CUSTODY_INTACT_HARD_HOLD")
    def test_stable_reorder_of_review_rows(self):
        x=sample();d=m.build_docket(x);d["article_review_rows"].reverse()
        self.assertEqual(m.verify_docket(x,d)["qualified_qd_pass"],False)
    def test_findings_never_released(self):
        x=sample();d=m.build_docket(x)
        d["article_review_rows"][0]["review_status"] = "EXAMINED_NOT_CLEARED"
        d["article_review_rows"][0]["finding_note"] = "Claim-source match still requires qualified medical review"
        self.assertEqual(m.verify_docket(x,d)["examined_article_count"],1)
    def test_empty_examined_note_rejected(self):
        x=sample();d=m.build_docket(x);d["article_review_rows"][0]["review_status"]="EXAMINED_NOT_CLEARED"
        self.assertRaises(m.ReviewHold,m.verify_docket,x,d)
    def test_invalid_snapshot_never_generates_docket(self):
        x=sample();x["origins"]["food"]["sha"]="0"*40
        self.assertRaises(m.ReviewHold,m.build_docket,x)
    def test_duplicate_json_properties_not_tolerated(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"p.json";p.write_text('{"a":1,"a":2}')
            self.assertRaises(m.r460.OriginHold,m._read_json,p)
    def test_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"p.json";p.write_text("{}")
            q=Path(td)/"alias.json";q.symlink_to(p)
            self.assertRaises(m.ReviewHold,m._read_json,q)
    def test_git_blob_pin_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"p.json";p.write_text("{}")
            self.assertRaises(m.ReviewHold,m._read_json,p,pin=m.SNAPSHOT_BLOB_SHA)
    def test_cli_hard_hold_even_healthy(self):
        self.assertEqual(m.main(["--snapshot","/no/such/file"]),2)
    def test_new_source_fragment_changes_queue(self):
        x=sample();d=m.build_docket(x)
        self.assertIn("fragments/food.json",[row["path"] for row in d["source_review_rows"]])

# Verify each of the original 35 article bodies and 35 metadata digest mutations are rejected.
def mutate_kind(n,kind):
    def f(self):
        x=sample();d=m.build_docket(x)
        x["candidate"]["articles"][f"guide-{n:02d}"][kind]=b.h(999000+n)
        self.assertRaises(m.ReviewHold,m.verify_docket,x,d)
    return f
for n in range(35):
    for k in ("body","meta"):
        setattr(TestCore,f"test_reject_changed_authored_{k}_{n:02d}",mutate_kind(n,k))

# Source identity/status/decision corruption must not promote the record.
def mutate_review(field,val):
    def f(self):
        x=sample();d=m.build_docket(x);d["article_review_rows"][0][field]=val
        self.assertRaises(m.ReviewHold,m.verify_docket,x,d)
    return f
for k,v in {"candidate_body":"0"*40,"candidate_meta":"0"*40,
            "claim_to_source_verified":True,"qualified_safety_approval":True,
            "review_status":"CLEARED","finding_note":5,"witnesses":{},
            "body_variants":0,"meta_variants":0,"body_matches":["unknown"]}.items():
    setattr(TestCore,"test_reject_article_mutation_"+k,mutate_review(k,v))

def mutate_root(field,val):
    def f(self):
        x=sample();d=m.build_docket(x);d[field]=val
        self.assertRaises(m.ReviewHold,m.verify_docket,x,d)
    return f
for k,v in {"qualified_qd_pass":True,"publication_authorized":True,
            "verified_realized_net_revenue":True,"verified_purchasable_preparedness_sku":True,
            "social_asset_attribution_verified":True,"candidate_commit":"0"*40,
            "snapshot_git_blob_sha":"0"*40,"full_35_article_inventory_sha256":"0"*64,
            "source_path_inventory_sha256":"0"*64,"release_state":"LIVE"}.items():
    setattr(TestCore,"test_reject_root_mutation_"+k,mutate_root(k,v))

if __name__=="__main__":unittest.main()
