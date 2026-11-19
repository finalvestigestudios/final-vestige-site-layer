"""Synthetic mutations: R473 is a structural HOLD, never a safety opinion."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import r472_food_source_conflict_gate as prior
import r473_food_review_decision_gate as gate
MANIFEST = json.loads((ROOT / "reviews/r473_food_exposure_manifest.json").read_text())

META = {
    "n": 11, "slug": gate.ARTICLE, "status": {"publish":"draft"},
    "safety_review":{"state":"pending", "reviewer":None, "date":None},
    "source_use":{"nchfp-jerky":"Trichinella freezing; wild game"},
}

# Synthetic two-site hazardous wording exists ONLY in isolated tests.
# Do not publish, quote as safe instructions, or use as a real recipe.
SITES = (
    '<li>Wild game Trichinella freezing at 0°F for 30 days {{cite:nchfp-jerky}}</li>',
    '<tr><td>Trichinella wild game: freeze 0°F 30 days {{cite:nchfp-jerky}}</td></tr>',
)
BODY = "\n".join(SITES) + "\n" + "\n".join(
    "<p>" + a + "</p>" for a in gate.ANCHORS.values()
)

def check(body=BODY, meta=None, manifest=None):
    meta = copy.deepcopy(META if meta is None else meta)
    manifest = copy.deepcopy(MANIFEST if manifest is None else manifest)
    witness = prior.audit(body, meta)
    return gate.audit(body, meta, manifest, r472_result=witness)

class R473IsolatedSafetyTests(unittest.TestCase):
    def test_01_positive_structural_docket_still_holds(self):
        r = check()
        self.assertEqual(r["original_claim_exposures"], 12)
        self.assertEqual(r["source_version_witnesses"], 6)
        self.assertFalse(r["may_publish"])
        self.assertFalse(r["qualified_qd_pass"])

    def test_02_six_version_scope_semantics_cannot_be_swapped(self):
        for version in MANIFEST["source_versions"]:
            for key in ("published", "species_scope", "url", "review_state"):
                with self.subTest(version=version["id"], key=key):
                    d = copy.deepcopy(MANIFEST)
                    row = next(x for x in d["source_versions"] if x["id"] == version["id"])
                    row[key] = "false_universal_freezing_procedure"
                    with self.assertRaises(gate.ReleaseHold):
                        check(manifest=d)

    def test_03_twelve_independent_exposures_not_approvable_by_metadata(self):
        for id in gate.EXPECTED_IDS:
            for field, false_value in (
                ("review_state", "APPROVED"),
                ("qualified_reviewer", "invented"),
                ("review_date", "2026-11-18"),
                ("approved_replacement", "safe"),
                ("decision_evidence", "fake"),
            ):
                with self.subTest(id=id,field=field):
                    d=copy.deepcopy(MANIFEST)
                    target=next(x for x in d["exposures"] if x["id"] == id)
                    target[field]=false_value
                    with self.assertRaises(gate.ReleaseHold):
                        check(manifest=d)

    def test_04_all_named_exposure_anchors_required(self):
        for id, anchor in gate.ANCHORS.items():
            with self.subTest(id=id):
                with self.assertRaises(gate.ReleaseHold):
                    check(body=BODY.replace(anchor, "[redacted]"))

    def test_05_release_claims_forbidden(self):
        for field,bad in (("release","LIVE"),("may_publish",True),
                          ("qualified_qd_pass",True),
                          ("medical_or_food_safety_verified",True),
                          ("source_version_conflict_open",False)):
            with self.subTest(field=field):
                m=copy.deepcopy(MANIFEST);m[field]=bad
                with self.assertRaises(gate.ReleaseHold):check(manifest=m)

    def test_06_metadata_approval_forbidden(self):
        for transform in (
            lambda x:x["status"].update(publish="published"),
            lambda x:x["safety_review"].update(state="approved"),
            lambda x:x["safety_review"].update(reviewer="someone"),
            lambda x:x["safety_review"].update(date="2026-11-18"),
            lambda x:x["source_use"].pop("nchfp-jerky"),
        ):
            m=copy.deepcopy(META);transform(m)
            with self.assertRaises((gate.ReleaseHold, prior.SafetyHold)):check(meta=m)

    def test_07_both_freezer_claims_must_remain_under_review(self):
        for index in (0,1):
            with self.subTest(index=index):
                with self.assertRaises(prior.SafetyHold):
                    prior.audit(BODY.replace(SITES[index],""),copy.deepcopy(META))
        for site in SITES:
            with self.subTest(site=site[:20]):
                with self.assertRaises(prior.SafetyHold):
                    prior.audit(BODY.replace(site,site.replace("{{cite:nchfp-jerky}}","")),copy.deepcopy(META))

    def test_08_lineage_or_source_provenance_cannot_be_invented(self):
        for field in ("e463_original_redline_blob","e464_source_lineage_blob",
                      "e464_editorial_head","original_body_blob","original_metadata_blob"):
            m=copy.deepcopy(MANIFEST);m[field]="0"*40
            with self.assertRaises(gate.ReleaseHold):check(manifest=m)

    def test_09_duplicate_json_keys_rejected(self):
        with self.assertRaises(gate.ReleaseHold):
            gate.strict_json(b'{"release":"DRAFT_HARD_HOLD","release":"LIVE"}')
        with self.assertRaises(gate.ReleaseHold):
            gate.strict_json(b'{"a":{"approved":false,"approved":true}}')

    def test_10_original_source_version_count_cannot_change(self):
        m=copy.deepcopy(MANIFEST);m["source_versions"].pop()
        with self.assertRaises(gate.ReleaseHold):check(manifest=m)
        m=copy.deepcopy(MANIFEST);m["source_versions"][1]=m["source_versions"][0]
        with self.assertRaises(gate.ReleaseHold):check(manifest=m)

    def test_11_mutated_exposure_ids_and_order_are_rejected(self):
        for id in gate.EXPECTED_IDS:
            m=copy.deepcopy(MANIFEST)
            for e in m["exposures"]:
                if e["id"]==id:e["id"]="other";break
            with self.subTest(id=id), self.assertRaises(gate.ReleaseHold):check(manifest=m)
        m=copy.deepcopy(MANIFEST);m["exposures"].reverse()
        with self.assertRaises(gate.ReleaseHold):check(manifest=m)

    def test_12_symlink_and_git_identity_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/"normal.json").write_text('{"x":1}')
            with self.assertRaises(gate.ReleaseHold):
                gate.pinned(root,"normal.json","0"*40)
            (root/"alias.json").symlink_to(root/"normal.json")
            with self.assertRaises(gate.ReleaseHold):
                gate.pinned(root,"alias.json",gate.blob_sha((root/"normal.json").read_bytes()))

    def test_13_synthetic_parent_laundered_pass_rejected(self):
        altered=prior.audit(BODY,copy.deepcopy(META));altered["may_publish"]=True
        with self.assertRaises(gate.ReleaseHold):
            gate.audit(BODY,copy.deepcopy(META),copy.deepcopy(MANIFEST),r472_result=altered)

    def test_14_native_main_is_hard_hold_on_missing_checkout(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(gate.main(["--root",d]),2)

# Individually named cases, not just subTest counts, for auditable >=36 tests.
def make_disposition_test(exposure_id, key, bad):
    def case(self):
        manifest=copy.deepcopy(MANIFEST)
        e=next(x for x in manifest["exposures"] if x["id"]==exposure_id)
        e[key]=bad
        with self.assertRaises(gate.ReleaseHold):
            check(manifest=manifest)
    return case

for exposure_id in gate.EXPECTED_IDS:
    for key,bad in (("review_state","APPROVED"),
                    ("qualified_reviewer","invented"),
                    ("review_date","2026-11-18"),
                    ("approved_replacement","not independently checked"),
                    ("decision_evidence","bogus")):
        setattr(R473IsolatedSafetyTests, "test_exposure_"+exposure_id+"_"+key,
                make_disposition_test(exposure_id,key,bad))

def make_scope_test(version_id, field):
    def case(self):
        m=copy.deepcopy(MANIFEST)
        item=next(x for x in m["source_versions"] if x["id"]==version_id)
        item[field]="fabricated_universal_approval"
        with self.assertRaises(gate.ReleaseHold):check(manifest=m)
    return case

for version_id in gate.VERSION_SCOPE:
    for field in ("url","published","species_scope","review_state"):
        setattr(R473IsolatedSafetyTests,"test_scope_"+version_id+"_"+field,
                make_scope_test(version_id,field))

def make_anchor_test(exposure_id, anchor):
    def case(self):
        with self.assertRaises(gate.ReleaseHold):
            check(body=BODY.replace(anchor,"MISSING_OR_CHANGED_REVIEW_CONTEXT"))
    return case

for exposure_id,anchor in gate.ANCHORS.items():
    setattr(R473IsolatedSafetyTests,"test_anchor_"+exposure_id,
            make_anchor_test(exposure_id,anchor))

if __name__ == "__main__":unittest.main()
