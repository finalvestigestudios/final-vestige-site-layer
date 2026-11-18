"""R460: synthetic hostile-branch provenance tests; not original source claim approval."""
from __future__ import annotations
import copy
import importlib.util
from pathlib import Path
import unittest

F = Path(__file__).resolve().parents[1] / "tools" / "r460_origin_branch_blob_crosswalk.py"
S = importlib.util.spec_from_file_location("r460_crosswalk", F)
m = importlib.util.module_from_spec(S)
S.loader.exec_module(m)

def h(n):
    return f"{n:040x}"

def fixture():
    slugs = [f"guide-{n:02d}" for n in range(35)]
    candidate = {s: {"body": h(n+1), "meta": h(n+101)} for n,s in enumerate(slugs)}
    sources = {"register.json": h(900), "fragments/food.json": h(901)}
    origins = {}
    for i, (ident,(name,sha)) in enumerate(m.ORIGINS.items()):
        arts = {s:dict(candidate[s]) for j,s in enumerate(slugs) if j%9==i}
        # every candidate article must have at least one original body and metadata witness
        origins[ident] = {"branch": name, "sha": sha, "articles": arts,
                          "sources":{"register.json": h(900), "fragments/food.json": h(901)}}
    return {"schema":"r460-origin-blob-v1", "repository":m.REPO, "release_state":m.STATE,
            "qualified_qd_pass":False,"candidate":{"branch":m.CANDIDATE_BRANCH, "sha":m.CANDIDATE_SHA,
            "articles": candidate,"sources": sources}, "origins": origins, "review_refs":dict(m.REVIEW_REFS)}

class Contracts(unittest.TestCase):
    def test_clean_synthetic_is_still_hard_hold(self):
        r=m.analyze(fixture());self.assertEqual(r["state"],"REVIEW_REQUIRED_HARD_HOLD")
        self.assertFalse(r["qualified_qd_pass"]); self.assertEqual(r["article_count"],35)
        self.assertEqual(r["review_required_slugs"],[])
    def test_origin_variant_survives(self):
        x=fixture();orig=x["origins"];slug="guide-00";orig["health"]["articles"][slug]={"body":h(2999),"meta":h(3000)}
        out=m.analyze(x);self.assertIn(slug,out["body_variant_slugs"]);self.assertIn(slug,out["review_required_slugs"])
    def test_new_body_not_silently_approved(self):
        x=fixture();x["candidate"]["articles"]["guide-00"]["body"]=h(4000)
        self.assertIn("guide-00",m.analyze(x)["candidate_body_unmatched_slugs"])
    def test_new_metadata_not_silently_approved(self):
        x=fixture();x["candidate"]["articles"]["guide-00"]["meta"]=h(4000)
        self.assertIn("guide-00",m.analyze(x)["candidate_meta_unmatched_slugs"])
    def test_source_mutation_flagged(self):
        x=fixture();x["candidate"]["sources"]["register.json"]=h(4000)
        self.assertIn("register.json",m.analyze(x)["source_review_paths"])
    def test_added_composite_file_not_falsely_bad(self):
        x=fixture();x["candidate"]["sources"]["crosswalk.json"]=h(444)
        self.assertTrue(next(r for r in m.analyze(x)["source_rows"] if r["path"]=="crosswalk.json")["new_composite_file"])
    def test_deleted_contributor_article_rejected(self):
        x=fixture();x["candidate"]["articles"].pop("guide-00");self.assertRaises(m.OriginHold,m.analyze,x)
    def test_duplicate_json_property_rejected(self):
        self.assertRaises(m.OriginHold,m._no_duplicates,[("a",1),("a",2)])
    def test_bad_slug_rejected(self):
        x=fixture();x["candidate"]["articles"]["../escape"]=x["candidate"]["articles"].pop("guide-00")
        self.assertRaises(m.OriginHold,m.analyze,x)
    def test_qa_ref_change_rejected(self):
        x=fixture();x["review_refs"]["qa157"]=h(2);self.assertRaises(m.OriginHold,m.analyze,x)
    def test_extra_review_ref_rejected(self):
        x=fixture();x["review_refs"]["fake"] = h(2);self.assertRaises(m.OriginHold,m.analyze,x)
    def test_false_qd_rejected(self):
        x=fixture();x["qualified_qd_pass"] = True;self.assertRaises(m.OriginHold,m.analyze,x)
    def test_source_fragment_loss_rejected(self):
        x=fixture();x["candidate"]["sources"].pop("fragments/food.json");self.assertRaises(m.OriginHold,m.analyze,x)
    def test_orphan_pair_rejected(self):
        x=fixture();x["origins"]["food"]["articles"]["guide-00"].pop("meta");self.assertRaises(m.OriginHold,m.analyze,x)

# 70 independently counted mutation tests over 35 article pairs, both authored file identities.
def make_article_test(slug, kind):
    def test(self):
        x=fixture();x["candidate"]["articles"][slug][kind]="not-a-blob"
        self.assertRaises(m.OriginHold,m.analyze,x)
    return test
for n in range(35):
    for kind in ("body","meta"):
        setattr(Contracts, f"test_reject_corrupt_{kind}_guide_{n:02d}", make_article_test(f"guide-{n:02d}",kind))

# 9 separate original immutable ref changes must all HOLD.
def make_ref_test(ident):
    def test(self):
        x=fixture();x["origins"][ident]["sha"]="0"*40
        self.assertRaises(m.OriginHold,m.analyze,x)
    return test
for ident in m.ORIGINS:
    setattr(Contracts, f"test_reject_ref_drift_{ident}",make_ref_test(ident))

if __name__ == "__main__": unittest.main()
