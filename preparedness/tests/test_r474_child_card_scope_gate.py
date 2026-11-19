"""R474 isolated adversarial custody tests. All assertions are structural, NOT safety review."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "tools/r474_child_card_scope_gate.py"
spec = importlib.util.spec_from_file_location("r474_child_card", SCRIPT)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
MANIFEST = json.loads((Path(__file__).resolve().parents[1] /
                      "reviews/r474_child_card_scope_manifest.json").read_text())


def setup():
    a = {"n": 15, "slug": gate.ARTICLE, "status":{"publish":"draft"},
         "safety_review":{"state":"pending","reviewer":None,"date":None},
         "source_use":{k:"older documented scope" for k in gate.REQUIRED_OLD_IDS}}
    t = copy.deepcopy(a);t["n"]=104;t["slug"]=gate.TOOL
    article = ("<strong>Keep it on paper, too.</strong> This is our caution, not an agency's. "
               "{{link:family-reunification-card|fold-over wallet card}} "
               "{{cite:shelter-cdc-reunification}} {{cite:shelter-ready-plan-form}}")
    tool = ("A printed card can be lost. Do not put a child's full name, "
            "a medical diagnosis or a password on it. "
            "First names or nicknames and phone numbers are usually enough. "
            "minimal version. School, childcare and care (left off the minimal version). "
            "{{cite:shelter-cdc-reunification}}")
    return [article, a, tool, t, copy.deepcopy(MANIFEST)]


class ReviewCustodyTests(unittest.TestCase):
    def test_original_synthetic_holds(self):
        d = gate.validate_originals(*setup())
        self.assertEqual(d["state"], "CHILD_CARD_CONTEXT_AND_CITATION_REVIEW_HARD_HOLD")
        self.assertFalse(d["may_publish"])
        self.assertFalse(d["qualified_qd_pass"])
        self.assertEqual(d["review_sources_unregistered"], 3)
        self.assertEqual(d["unadjudicated_decisions"], 8)

    def test_strict_duplicate_json(self):
        with self.assertRaises(gate.Hold):
            gate.strict_json(b'{"x":1,"x":2}')

    def test_strict_non_object(self):
        with self.assertRaises(gate.Hold):gate.strict_json(b'[]')

    def test_valid_sha_git_blob(self):
        self.assertEqual(gate.blob_sha(b"hello"), "b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0")

    def test_pinned_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(gate.Hold):gate.checked_file(Path(tmp),"notthere", "abcd")

    def test_pinned_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp);(path/"regular").write_text("hello");(path/"link").symlink_to(path/"regular")
            with self.assertRaises(gate.Hold):gate.checked_file(path,"link",gate.blob_sha(b"hello"))

    def test_pinned_wrong_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);(p/"evidence").write_text("fraud")
            with self.assertRaises(gate.Hold):gate.checked_file(p,"evidence",gate.blob_sha(b"original"))

    def test_pinned_correct_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);(p/"evidence").write_text("original")
            self.assertEqual(gate.checked_file(p,"evidence",gate.blob_sha(b"original")),b"original")

    def test_native_missing_original_holds(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(gate.Hold):gate.native(Path(tmp))

    def test_cli_always_returns_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(gate.main(["--root",tmp]),2)

    def test_original_unregistered_new_source(self):
        x=setup();x[1]["source_use"][gate.REVIEW_SOURCES[0][0]]="fabricated"
        with self.assertRaises(gate.Hold):gate.validate_originals(*x)

    def test_original_old_source_rebranded(self):
        x=setup();x[3]["source_use"]["shelter-cdc-reunification"]="2025 new child cards"
        with self.assertRaises(gate.Hold):gate.validate_originals(*x)

    def test_missing_new_url_read_depth(self):
        x=setup();x[4]["review_only_sources"][2]["read_scope"]="full_official_page"
        with self.assertRaises(gate.Hold):gate.validate_originals(*x)

    def test_review_only_token_laundered_article(self):
        x=setup();x[0]+="{{cite:"+gate.REVIEW_SOURCES[0][0]+"}}"
        with self.assertRaises(gate.Hold):gate.validate_originals(*x)

    def test_review_only_token_laundered_tool(self):
        x=setup();x[2]+="{{cite:"+gate.REVIEW_SOURCES[1][0]+"}}"
        with self.assertRaises(gate.Hold):gate.validate_originals(*x)

    def test_no_js_or_merchant_actions(self):
        self.assertNotIn("requests.", SCRIPT.read_text())
        self.assertNotIn("wordpress_post", SCRIPT.read_text())


def create_mutation_tests():
    mods={}
    # Fixed manifest and state tampering at every authority boundary.
    for key, bad in (
        ("schema","other"),("integration_parent_sha","deadbeef"),
        ("editorial_review_head_sha","deadbeef"),("editorial_e466_memo_blob","deadbeef"),
        ("original_blobs",{}),("article_number",99),("tool_number",102),
        ("tool_102_is_distinct",False),("release","PUBLISHED"),
        ("may_publish",True),("qualified_qd_pass",True),
        ("child_medical_advice_approved",True),("child_privacy_verified",True),
        ("school_pickup_rules_universal",True),("commercial_offer_approved",True),
        ("fema_pdf_original_publication","2025-06"),("fema_pdf_second_page_checked",True),
        ("review_only_sources",[]),("decisions",[])
    ):
        def f(x,k=key,v=bad):x[4][k]=v
        mods["manifest_"+key]=f
    for i in range(3):
        for key,bad in (("id","wrong"),("published","2026"),("url","https://example.org"),
                        ("read_scope","unlimited"),("citation_registered",True),
                        ("review_state","APPROVED")):
            def f(x,i=i,k=key,v=bad):x[4]["review_only_sources"][i][k]=v
            mods[f"review_source_{i}_{key}"]=f
    for i in range(8):
        for key,bad in (("id","changed"),("state","APPROVED"),("reviewer","self"),
                        ("evidence","unverified"),("approved_copy","safe"),("owner","AI")):
            def f(x,i=i,k=key,v=bad):x[4]["decisions"][i][k]=v
            mods[f"decision_{i}_{key}"]=f
    for key in ("paid_sku_authenticated","grok_published_asset_matched","realized_net_revenue_verified"):
        def f(x,k=key):x[4]["commercial_funnel"][k]=True
        mods["false_commerce_"+key]=f
