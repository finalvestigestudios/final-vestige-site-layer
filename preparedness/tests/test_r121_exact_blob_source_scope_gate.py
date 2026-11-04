"""R121 synthetic 35-article / 13-change custody mutations; no shared writes."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / "tools" / "r121_exact_blob_source_scope_gate.py"
SPEC = importlib.util.spec_from_file_location("r121", PATH)
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)
SLUGS = [f"synthetic-article-{i:02d}" for i in range(35)]
CHANGED = SLUGS[:13]

def fixture():
    blobs, before, after, rows = {}, {}, {}, []
    def blob(value):
        data = value.encode() if isinstance(value, str) else value
        h = gate.oid_bytes(data)
        blobs[h] = data
        return h
    for slug in SLUGS:
        old = "<p>" + slug + " first source {{cite:base-source}} next {{cite:other-source}}</p>"
        new = old.replace("</p>", " added source {{cite:extra-source}}</p>") if slug in CHANGED else old
        meta = {"slug":slug,"status":{"publish":"draft"},
                "safety_review":{"state":"pending"},
                "source_use":{"base-source":"author interpretation", "other-source":"author interpretation"}}
        later = copy.deepcopy(meta)
        if slug in CHANGED:
            later["source_use"]["extra-source"] = "author interpretation"
        for mapping, body, md in ((before,old,meta),(after,new,later)):
            mapping[slug+".body.html"] = blob(body)
            mapping[slug+".meta.json"] = blob(json.dumps(md))
        if slug in CHANGED:
            rows.append({"slug":slug,"approval":"UNREVIEWED",
                         "before_git_blob":before[slug+".body.html"],
                         "after_git_blob":after[slug+".body.html"],
                         "before_word_count":10,"after_word_count":15,
                         "before_citation_count":2,"after_citation_count":3,
                         "citation_sequence_changed":True,
                         "occurrence_changes":[{"source_id":"extra-source","before":0,"after":1}],
                         "context_examples":[]})
    heads=[{"role":"baseline","sha":"a"*40,"article_files":before},
           {"role":"candidate","sha":"b"*40,"article_files":after}]
    heads += [{"role":"contributor","sha":str(i+1)*40,"cluster":str(i)} for i in range(7)]
    snap={"schema":"fv-preparedness-r117-nine-snapshot-article-source-git-custody-HOLD-v1",
          "issue":136,"business_issue":820,"snapshots":heads,
          "governance":{"release_state":"HOLD","may_publish":False,"may_merge":False,
                        "medical_safety_verified":False,"merchant_offer_verified":False,
                        "independent_QD_PASS":False}}
    def part(items):
        return {"schema":"r120-partial-citation-context-HOLD-v1","issue":136,
                "base_sha":"a"*40,"candidate_sha":"b"*40,"rows":items}
    return snap,[part(rows[:7]),part(rows[7:])],blobs

def review(snap,parts,blobs):
    return gate.audit(snap,parts,lambda oid:blobs[oid])

def update_meta(snap,blobs,slug,transform):
    tree=snap["snapshots"][1]["article_files"]
    key=slug+".meta.json"
    original=json.loads(blobs[tree[key]])
    transform(original)
    encoded=json.dumps(original).encode()
    sha=gate.oid_bytes(encoded)
    blobs[sha]=encoded
    tree[key]=sha

class Integrity(unittest.TestCase):
    def test_complete_corpus_remains_hold(self):
        s,p,b=fixture()
        r=review(s,p,b)
        self.assertEqual((r["article_count"],r["changed_body_count"]),(35,13))
        self.assertEqual((r["source_occurrences_original"],r["source_occurrences_candidate"]),(70,83))
        self.assertEqual(r["state"],"HOLD")
        self.assertFalse(r["release_authorized"])
        self.assertFalse(r["QD_PASS"])
        self.assertEqual(r["blockers"],[])
    def test_deterministic_order(self):
        s,p,b=fixture()
        first=review(s,p,b)
        p[0]["rows"].reverse()
        self.assertEqual(first,review(s,p,b))
    def test_published_article_rejected(self):
        s,p,b=fixture()
        update_meta(s,b,SLUGS[0],lambda m:m["status"].update(publish="publish"))
        with self.assertRaisesRegex(gate.Hold,"UNAUTHORIZED_PUBLISH_STATE"):
            review(s,p,b)
    def test_safety_approval_change_reported(self):
        s,p,b=fixture()
        update_meta(s,b,SLUGS[0],lambda m:m["safety_review"].update(state="approved"))
        self.assertTrue(any(x["code"]=="SAFETY_REVIEW_STATE_CHANGED" for x in review(s,p,b)["blockers"]))
    def test_changed_blob_bytes_rejected(self):
        s,p,b=fixture()
        oid=s["snapshots"][0]["article_files"][SLUGS[0]+".body.html"]
        b[oid]=b"incorrect source evidence"
        with self.assertRaisesRegex(gate.Hold,"GIT_BLOB_IDENTITY_MISMATCH"):
            review(s,p,b)
    def test_forced_qd_status_rejected(self):
        s,p,b=fixture()
        s["governance"]["independent_QD_PASS"]=True
        with self.assertRaisesRegex(gate.Hold,"ILLEGAL_RELEASE_UPGRADE"):
            review(s,p,b)
    def test_unreviewed_context_required(self):
        s,p,b=fixture()
        p[0]["rows"].pop()
        with self.assertRaisesRegex(gate.Hold,"MISSING_CHANGED_BODY_CONTEXT"):
            review(s,p,b)
    def test_duplicate_metadata_json_key_rejected(self):
        with self.assertRaisesRegex(gate.Hold,"DUPLICATE_JSON_KEY"):
            gate.strict_json('{"slug":"one","slug":"two"}')

def missing_source_test(slug):
    def test(self):
        s,p,b=fixture()
        update_meta(s,b,slug,lambda m:m["source_use"].pop("base-source"))
        issues=review(s,p,b)["blockers"]
        self.assertIn(slug,[x["slug"] for x in issues if x["code"]=="MISSING_AUTHOR_SCOPED_SOURCE_USE"])
    return test

def source_delta_test(slug):
    def test(self):
        s,p,b=fixture()
        row=next(x for part in p for x in part["rows"] if x["slug"]==slug)
        row["occurrence_changes"][0]["after"]=2
        with self.assertRaisesRegex(gate.Hold,"SOURCE_OCCURRENCE_CROSSWALK_DRIFT"):
            review(s,p,b)
    return test

for i,slug in enumerate(SLUGS):
    setattr(Integrity,f"test_author_scope_{i:02d}",missing_source_test(slug))
for i,slug in enumerate(CHANGED):
    setattr(Integrity,f"test_source_delta_{i:02d}",source_delta_test(slug))
