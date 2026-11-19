"""Adversarial R475 source/claim-scope tests: structural only, NEVER QD approval."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

BASE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("r475",BASE/"tools/r475_cdc_card_source_scope_gate.py")
gate=importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
MANIFEST=json.loads((BASE/"reviews/r475_cdc_2020_2025_child_card_claim_crosswalk.json").read_text())

class GateTests(unittest.TestCase):
    def test_baseline_is_structural_only(self):
        d=gate.check_crosswalk(copy.deepcopy(MANIFEST))
        self.assertEqual(d["state"],"E467_CDC_SOURCE_SCOPE_AND_CHILD_PRIVACY_HARD_HOLD")
        self.assertEqual(d["unadjudicated_decisions"],8)
        self.assertFalse(d["qualified_qd_pass"])
        self.assertIsNone(d["net_revenue_per_1000_sessions"])

    def test_duplicate_json_rejected(self):
        with self.assertRaises(gate.Hold):gate.strict_json(b'{"x":1,"x":2}')

    def test_nonstandard_float_rejected(self):
        with self.assertRaises(gate.Hold):gate.strict_json(b'{"x":NaN}')

    def test_json_root_rejected(self):
        with self.assertRaises(gate.Hold):gate.strict_json(b'[]')

    def test_git_blob(self):
        self.assertEqual(gate.git_blob(b"hello"),"b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0")

    def test_missing_native_holds(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(gate.Hold):gate.check_native(Path(tmp),MANIFEST)

    def test_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);(p/"data").write_text("x");(p/"link").symlink_to(p/"data")
            with self.assertRaises(gate.Hold):gate.read_pinned(p,"link",gate.git_blob(b"x"))

    def test_path_outside_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(gate.Hold):gate.read_pinned(Path(tmp),"../untrusted",gate.git_blob(b"x"))

    def test_cli_mandatory_hold_exit_two(self):
        with tempfile.TemporaryDirectory() as tmp:self.assertEqual(gate.main(["--root",tmp]),2)

def generate():
    mutations={}
    for k,v in (("schema","wrong"),("status","PUBLISHED"),("may_publish",True),("qualified_qd_pass",True),
                ("qualified_school_privacy_review",True),("native_35_article_build_pass",True),
                ("wordpress_private_export_parity_pass",True),("article_15_status","published"),
                ("tool_104_status","safety_passed"),("tool_102_distinct",False),
                ("review_only_last_checked","2025-01-01"),("review_by","2099-12-31")):
        mutations["top_"+k]=lambda m,k=k,v=v:m.__setitem__(k,v)
    for key in gate.FROZEN:
        mutations["evidence_"+key]=lambda m,k=key:m["evidence"].__setitem__(k,"badsha")
    for i in range(3):
        for k,v in (("id","other"),("url","https://invalid.example"),("published","2026-12-19"),("scope","catalog_record_only"),("origin","AI_GUESS"),("rights","unrestricted"),("citation_registered",True)):
            mutations[f"src_{i}_{k}"]=lambda m,i=i,k=k,v=v:m["sources"][i].__setitem__(k,v)
    for k in ("2020_child_backpack_fields","2020_guardian_wallet_fields"):
        mutations["pdf_field_"+k]=lambda m,k=k:m["sources"][0][k].pop()
    mutations["pdf_guardian_minimalized"]=lambda m:m["sources"][0].__setitem__("2020_guardian_wallet_fields",["phone"])
    mutations["pdf_false_historical_revision"]=lambda m:m["sources"][0].__setitem__("old_e466_catalog_only_is_historical",False)
    mutations["web_2025_field_loss"]=lambda m:m["sources"][1]["2025_page_explicit_fields"].pop()
    for k in ("2025_page_explicitly_lists_home_address","2025_address_is_prohibited","2025_address_is_required"):
        mutations["web_address_"+k]=lambda m,k=k:m["sources"][1].__setitem__(k,True)
    for k in ("card_grants_school_pickup_authority","school_emergency_contacts_must_stay_current","follow_authorized_pickup_instructions"):
        mutations["pickup_"+k]=lambda m,k=k:m["sources"][2].__setitem__(k,not m["sources"][2][k])
    for k in gate.CLAIMS:
        mutations["claim_"+k]=lambda m,k=k:m["claim_boundaries"].__setitem__(k,not m["claim_boundaries"][k])
    for i in range(8):
        for k,v in (("id","other"),("owner","AI"),("status","APPROVED"),("reviewer","model"),("signed_receipt","fabricated")):
            mutations[f"human_{i}_{k}"]=lambda m,i=i,k=k,v=v:m["human_decisions"][i].__setitem__(k,v)
    for k in MANIFEST["commercial_funnel"]:
        mutations["paid_"+k]=lambda m,k=k:m["commercial_funnel"].__setitem__(k,0 if k.endswith("sessions") else True)
    for name,change in mutations.items():
        def test(self,change=change):
            m=copy.deepcopy(MANIFEST);change(m)
            with self.assertRaises(gate.Hold):gate.check_crosswalk(m)
        setattr(GateTests,"test_mutation_"+name,test)
    return len(mutations)
MUTATIONS=generate()
if __name__=="__main__":unittest.main()
