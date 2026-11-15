"""R377 adversarial test-only synthetic fixtures; never substitute for native build."""
from __future__ import annotations
import copy
import json
import pathlib
import re
import subprocess
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE/"tools"))
import r377_jerky_claim_source_custody as m

D = HERE/"audits"/"r377_jerky_source_conflict_HARD_HOLD.json"


def fixture():
    source_rows=[]; coll=[]
    for n in sorted(m.HELD_SOURCE_IDS):
        variants=[]
        for branch in ("original-food", "original-other"):
            variants.append(dict(branch=branch,fragment="preparedness/sources/fragments/food.json",
                source_blob="a"*40,id=n,url="https://example.org/"+n,
                publisher="Synthetic tests",kind="test",verified_on="2026-10-29",
                human_link_check=False,supports=f"synthetic scoped statement {n} {branch}",
                notes="synthetic read-scope retention"))
        source_rows.append(dict(id=n,requires_human_review=True,variants=copy.deepcopy(variants)))
        coll.append(dict(source_id=n,release_disposition="HUMAN_ADJUDICATION_REQUIRED_NO_AUTO_SELECT",
                         variants=copy.deepcopy(variants)))
    body=b"<p>Original disputed claim placeholder {{cite:nchfp-jerky}}</p>"
    meta={"n":11,"slug":"safe-jerky-dehydration","section":"food","track":"modern",
        "status":{"editorial":"drafted","publish":"draft"},
        "safety_review":{"state":"pending","reviewer":None,"date":None},
        "source_use":{"nchfp-jerky":"synthetic source purpose"}}
    pins=[{"branch":"original-food", "sha":"b"*40}]
    crosswalk={"repository":m.REPOSITORY,"schema_version":1,"release_state":"DRAFT_HARD_HOLD",
        "source_id_variants":source_rows}
    audit={"repository":m.REPOSITORY,"schema_version":1,"release_state":"DRAFT_HARD_HOLD",
        "source_crosswalk_git_blob":m.ORIGINAL_CROSSWALK_SHA,
        "object_manifest_git_blob":m.ORIGINAL_MANIFEST_SHA,"branch_pins":copy.deepcopy(pins),
        "semantic_conflict_docket":coll,"publication_approved":False,
        "qualified_emergency_safety_approved":False,"qualified_privacy_approved":False,
        "commercial_checkout_approved":False}
    manifest={"repository":m.REPOSITORY,"schema_version":1,"release_state":"DRAFT_HARD_HOLD",
        "branch_pins":pins}
    evidence=json.loads(D.read_text())
    return [body,meta,crosswalk,audit,manifest,evidence]


def run(doc):
    return m.validate(*doc,synthetic=True)


class CustodyTests(unittest.TestCase):
    def test_synthetic_baseline_still_hard_hold(self):
        out=run(fixture())
        self.assertEqual(out["status"],"SYNTHETIC_HARD_HOLD",out)
        self.assertFalse(out["publication_approved"])
        self.assertFalse(out["qualified_safety_approved"])
        self.assertFalse(out["paid_offer_approved"])
        self.assertIsNone(out["verified_net_revenue"])

    def test_cli_never_grants_release_on_missing_inputs(self):
        p=subprocess.run([sys.executable,str(HERE/"tools"/"r377_jerky_claim_source_custody.py"),
                        "/nonexistent","/nonexistent","/nonexistent","/nonexistent","/nonexistent","/nonexistent"],
                         capture_output=True,text=True)
        self.assertEqual(p.returncode,2)
        self.assertEqual(json.loads(p.stdout)["status"],"INVALID_HARD_HOLD")

    def test_original_sha_pinned_even_if_metadata_valid(self):
        out=m.validate(*fixture())
        self.assertEqual(out["status"],"INVALID_HARD_HOLD")
        self.assertTrue(any("Git identity drift" in e for e in out["errors"]))

    def test_deterministic_report(self):
        self.assertEqual(run(fixture()),run(fixture()))

    def test_git_blob_fingerprint(self):
        self.assertEqual(m.git_blob(b"hello"),"b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0")

    def test_citation_inventory(self):
        out=run(fixture())
        self.assertEqual(out["article_11_citation_occurrences"],1)

    def test_risks_detect_original_disputed_freezing(self):
        r=m.claim_risk_lines('<li>Pork and wild game: NCHFP says for Trichinella freeze them.</li>')
        self.assertEqual(r["wild_game_freezing"],[1])

    def test_risks_detect_whichever(self):
        self.assertEqual(m.claim_risk_lines('<p>Choose whichever method above.</p>')["method_choice"],[1])

    def test_risks_ignore_unrelated_freezing(self):
        self.assertFalse(m.claim_risk_lines("<p>Freeze strawberries for flavor.</p>")["wild_game_freezing"])

    def test_risks_ignore_script_text(self):
        self.assertFalse(m.claim_risk_lines("<script>whichever method</script>")["method_choice"])

    def test_warnings_do_not_claim_safe_recipe(self):
        t=D.read_text().lower()
        self.assertNotIn('"publication_approved": true',t)
        self.assertNotIn('"qualified_review": true',t)
        self.assertNotIn('"paid_offer_verified": true',t)


# Each adversarial fixture mutation gets its own real unittest test and assertion.
# No fixture changes can grant approval and test-mode always remains hard-held.
def add_case(name, mutate, expected):
    def case(self):
        doc=fixture()
        mutate(doc)
        out=run(doc)
        self.assertEqual(out["status"],"INVALID_HARD_HOLD",out)
        self.assertTrue(any(expected in e for e in out["errors"]),out["errors"])
        self.assertFalse(out["publication_approved"])
    setattr(CustodyTests,"test_adversarial_"+name,case)


CASES={
 "body_missing":(lambda d:d.__setitem__(0,b"<p>no source</p>"),"all article citations lost"),
 "body_unknown_cite":(lambda d:d.__setitem__(0,b"<p>{{cite:nchfp-jerky}}{{cite:missing-source}}</p>"),"lack original metadata"),
 "body_unpaired_cite":(lambda d:d.__setitem__(0,b"<p>{{cite:fsis-power-failure}}</p>"),"critical jerky citation removed"),
 "body_not_bytes":(lambda d:d.__setitem__(0,"not bytes"),"body must be byte-identical"),
 "body_bad_utf8":(lambda d:d.__setitem__(0,b"\xff{{cite:nchfp-jerky}}"),"body not UTF-8"),
 "n_changed":(lambda d:d[1].__setitem__("n",12),"article identity changed"),
 "slug_changed":(lambda d:d[1].__setitem__("slug","different"),"article identity changed"),
 "section_changed":(lambda d:d[1].__setitem__("section","history"),"article taxonomy changed"),
 "track_changed":(lambda d:d[1].__setitem__("track","historical"),"article taxonomy changed"),
 "editorial_approved":(lambda d:d[1]["status"].__setitem__("editorial","approved"),"draft editorial state"),
 "publish_live":(lambda d:d[1]["status"].__setitem__("publish","publish"),"draft editorial state"),
 "review_complete":(lambda d:d[1]["safety_review"].__setitem__("state","approved"),"unreviewed safety state"),
 "reviewer_forged":(lambda d:d[1]["safety_review"].__setitem__("reviewer","fictional"),"unreviewed safety state"),
 "review_date_forged":(lambda d:d[1]["safety_review"].__setitem__("date","2026-11-14"),"unreviewed safety state"),
 "source_use_removed":(lambda d:d[1].pop("source_use"),"source_use missing"),
 "source_use_extra":(lambda d:d[1]["source_use"].__setitem__("another-source","made up"),"source_use no longer cited"),
 "source_use_jerky_removed":(lambda d:d[1]["source_use"].pop("nchfp-jerky"),"critical jerky citation removed"),
 "crosswalk_repo":(lambda d:d[2].__setitem__("repository","wrong"),"crosswalk identity"),
 "crosswalk_schema":(lambda d:d[2].__setitem__("schema_version",2),"crosswalk identity"),
 "crosswalk_release":(lambda d:d[2].__setitem__("release_state","PASS"),"crosswalk identity"),
 "audit_repo":(lambda d:d[3].__setitem__("repository","wrong"),"audit identity"),
 "audit_schema":(lambda d:d[3].__setitem__("schema_version",0),"audit identity"),
 "audit_release":(lambda d:d[3].__setitem__("release_state","approved"),"audit identity"),
 "manifest_repo":(lambda d:d[4].__setitem__("repository","wrong"),"manifest identity"),
 "manifest_schema":(lambda d:d[4].__setitem__("schema_version",2),"manifest identity"),
 "manifest_release":(lambda d:d[4].__setitem__("release_state","APPROVED"),"manifest identity"),
 "branch_pin_removed":(lambda d:d[3].__setitem__("branch_pins",[]),"branch provenance diverges"),
 "crosswalk_blob_wrong":(lambda d:d[3].__setitem__("source_crosswalk_git_blob","a"*40),"upstream source Git identities"),
 "manifest_blob_wrong":(lambda d:d[3].__setitem__("object_manifest_git_blob","b"*40),"upstream source Git identities"),
 "publication_forged":(lambda d:d[3].__setitem__("publication_approved",True),"source audit asserted release"),
 "emergency_forged":(lambda d:d[3].__setitem__("qualified_emergency_safety_approved",True),"source audit asserted release"),
 "privacy_forged":(lambda d:d[3].__setitem__("qualified_privacy_approved",True),"source audit asserted release"),
 "commerce_forged":(lambda d:d[3].__setitem__("commercial_checkout_approved",True),"source audit asserted release"),
 "collision_removed":(lambda d:d[3]["semantic_conflict_docket"].pop(),"five original same-ID"),
 "collision_duplicate":(lambda d:d[3]["semantic_conflict_docket"].append(copy.deepcopy(d[3]["semantic_conflict_docket"][0])),"five original same-ID"),
 "crosswalk_duplicate":(lambda d:d[2]["source_id_variants"].append(copy.deepcopy(d[2]["source_id_variants"][0])),"crosswalk duplicate"),
 "evidence_slug":(lambda d:d[5].__setitem__("target_slug","made-up"),"R377 current article"),
 "evidence_release":(lambda d:d[5].__setitem__("release_state","PASSED"),"R377 current article"),
 "evidence_disposition":(lambda d:d[5].__setitem__("editorial_disposition","AUTO_SELECT"),"actionable advice not held"),
 "evidence_paid_offer":(lambda d:d[5].__setitem__("paid_offer_verified",True),"unverified offer"),
 "evidence_published":(lambda d:d[5].__setitem__("publication_approved",True),"unverified offer"),
 "evidence_links_removed":(lambda d:d[5].__setitem__("official_evidence",[]),"official source links"),
 "evidence_review_forged":(lambda d:d[5]["official_evidence"][0].__setitem__("qualified_review",True),"source unreviewed scope"),
 "evidence_scope_lost":(lambda d:d[5]["official_evidence"][1].__setitem__("reading_scope",""),"source unreviewed scope"),
}
for name,(mutate,expected) in CASES.items():
    add_case(name,mutate,expected)

# Preserve all five collision records independently; each original source has distinct provenance.
for index,sid in enumerate(sorted(m.HELD_SOURCE_IDS)):
    add_case(f"drop_collision_{sid.replace('-','_')}",
             lambda d,sid=sid:d[3]["semantic_conflict_docket"].__setitem__(slice(None),[r for r in d[3]["semantic_conflict_docket"] if r["source_id"]!=sid]),
             "five original same-ID")
    add_case(f"mutate_support_{sid.replace('-','_')}",
             lambda d,index=index:d[2]["source_id_variants"][index]["variants"][0].__setitem__("supports","fake replacement scope"),
             f"source reading-scope or contributor record tampered: {sid}")
    add_case(f"select_unreviewed_{sid.replace('-','_')}",
             lambda d,index=index:d[3]["semantic_conflict_docket"][index].__setitem__("release_disposition","AUTO_SELECT"),
             f"unreviewed source selected: {sid}")
    add_case(f"human_check_forged_{sid.replace('-','_')}",
             lambda d,index=index:d[2]["source_id_variants"][index]["variants"][0].__setitem__("human_link_check",True),
             f"source status/identity changed: {sid}")

for idx,ename in enumerate(m.EXPECTED_EXTERNAL):
    add_case(f"replace_official_link_{idx}",
        lambda d,idx=idx:d[5]["official_evidence"][idx].__setitem__("url","https://fake.example/"),
        "official source links changed")

if __name__=="__main__":
    unittest.main(verbosity=2)
