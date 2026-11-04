"""R119 candidate + contributor synthetic tamper checks: no CMS, source writes, network or safety approvals."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

MOD=Path(__file__).resolve().parents[1]/"tools"/"r119_complete_delta_crosswalk_gate.py"
if not MOD.exists():
    MOD=Path(__file__).with_name("r119_complete_delta_crosswalk_gate.py")
spec=importlib.util.spec_from_file_location("r119",MOD)
gate=importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
A,B,C,D=(c*40 for c in "abcd")
SLUGS=["article-"+str(i) for i in range(35)]

def fixture():
    files={slug+ext:A for slug in SLUGS for ext in (".body.html",".meta.json")}
    src={"README.md":A,"food.json":A}
    orig={"role":"baseline","ref":"review/base","sha":A,
          "article_files":files,"source_fragments":src}
    new=copy.deepcopy(orig)
    new.update(role="candidate",ref="review/rc",sha=B)
    new["article_files"]["article-1.body.html"]=B
    names=sorted(gate.CLUSTERS)
    cs=[]
    for i, name in enumerate(names):
        c={"role":"contributor","cluster":name,"ref":"claude/"+name,
           "sha":str(i+1)*40,"article_files":{},"source_fragments":{"README.md":A}}
        c["article_files"][SLUGS[i]+".body.html"]= A
        c["article_files"][SLUGS[i]+".meta.json"]= A
        if i==0:c["article_files"]["article-0.body.html"]=C
        if i==1:c["source_fragments"]["food.json"]=C
        if i==1:c["source_fragments"]["README.md"]=A
        if i==2:c["article_files"]["article-2.meta.json"]=D
        cs.append(c)
    snapshot={"schema":gate.OLD_SCHEMA,"issue":136,"business_issue":820,
              "governance":{"release_state":"HOLD","may_publish":False,"may_merge":False,
                  "independent_QD_PASS":False,"medical_safety_verified":False,
                  "merchant_offer_verified":False},
              "snapshots":[orig,new]+cs}
    rows=[]
    for c in cs:
        for key,prefix in (("article_files",gate.ARTICLE_PREFIX),
                           ("source_fragments",gate.SOURCE_PREFIX)):
            for filename,oid in c[key].items():
                if oid==orig[key][filename]:continue
                rc_oid=new[key][filename]
                disposition=("EXACT_IN_RELEASE_CANDIDATE" if oid==rc_oid else
                             "RELEASE_CANDIDATE_RETAINS_BASELINE" if rc_oid==orig[key][filename]
                             else "RELEASE_CANDIDATE_DIFFERS_FROM_BOTH")
                rows.append({"cluster":c["cluster"],"contributor_head":c["sha"],
                             "path":prefix+filename,"kind":key,"contributor_git_blob":oid,
                             "frozen_original_git_blob":orig[key][filename],
                             "release_candidate_git_blob":rc_oid,"disposition":disposition,
                             "requires_human_source_or_safety_adjudication":True})
    groups={r["path"] for r in rows}
    work={"schema":gate.ORDER_SCHEMA,"issue":136,"business_issue":820,
          "release_state":"HOLD","may_publish":False,"may_merge":False,
          "independent_QD_PASS":False,"baseline_sha":A,"candidate_sha":B,
          "seven_contributor_heads":{c["cluster"]:c["sha"] for c in cs},
          "observation_count":len(rows),"unique_changed_paths":len(groups),
          "non_exact_candidate_observations":sum(r["disposition"]!="EXACT_IN_RELEASE_CANDIDATE" for r in rows),
          "overlapping_paths":[],"rows":rows}
    return snapshot,work

class ReviewGate(unittest.TestCase):
    def test_35_and_hold(self):
        s,w=fixture(); out=gate.build_crosswalk(s,w)
        self.assertEqual(out["article_count"],35)
        self.assertEqual(out["unique_changed_paths"],4)
        self.assertEqual(out["contributor_change_observations"],3)
        self.assertFalse(out["may_publish"])
        self.assertTrue(all(r["human_decision"]=="UNREVIEWED" for r in out["review_decisions"]))
        self.assertTrue(gate.verify_crosswalk(s,w,out)["all_unreviewed"])
    def test_deterministic_under_row_permutation(self):
        s,w=fixture(); before=gate.build_crosswalk(s,w)
        w["rows"].reverse()
        self.assertEqual(before,gate.build_crosswalk(s,w))
    def test_duplicate_json_keys_fail(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"bad.json";p.write_text('{"a":1,"a":2}')
            with self.assertRaisesRegex(gate.Hold,"DUPLICATE_JSON_KEY"):
                gate.strict_load(p)
    def test_prior_review_cannot_upgrade_hold(self):
        s,w=fixture(); cross=gate.build_crosswalk(s,w)
        cross["review_decisions"][0]["human_decision"]="APPROVED"
        with self.assertRaises(gate.Hold):gate.verify_crosswalk(s,w,cross)

def mutation(name, func):
    def test(self):
        s,w=fixture()
        func(s,w)
        with self.assertRaises((gate.Hold,KeyError,TypeError),msg=name):
            gate.build_crosswalk(s,w)
    setattr(ReviewGate,"test_reject_"+name,test)

for n, slug in enumerate(SLUGS):
    mutation("missing_original_metadata_%02d"%(n+1),
        lambda s,w,slug=slug:s["snapshots"][0]["article_files"].pop(slug+".meta.json"))

MUTATIONS={
 "wrong_snapshot_schema":lambda s,w:s.update(schema="fake"),
 "wrong_order_schema":lambda s,w:w.update(schema="fake"),
 "issue_scope":lambda s,w:w.update(issue=900),
 "business_scope":lambda s,w:s.update(business_issue=900),
 "approval_gov":lambda s,w:s["governance"].update(may_publish=True),
 "merge_gov":lambda s,w:w.update(may_merge=True),
 "false_QD":lambda s,w:w.update(independent_QD_PASS=True),
 "false_medical":lambda s,w:s["governance"].update(medical_safety_verified=True),
 "false_merchant":lambda s,w:s["governance"].update(merchant_offer_verified=True),
 "missing_snapshot":lambda s,w:s["snapshots"].pop(),
 "bad_roles":lambda s,w:s["snapshots"][1].update(role="production"),
 "duplicate_cluster":lambda s,w:s["snapshots"][2].update(cluster=s["snapshots"][3]["cluster"]),
 "duplicate_ref":lambda s,w:s["snapshots"][3].update(ref=s["snapshots"][4]["ref"]),
 "bad_sha":lambda s,w:s["snapshots"][0].update(sha="oops"),
 "missing_candidate_body":lambda s,w:s["snapshots"][1]["article_files"].pop("article-1.body.html"),
 "stray_body":lambda s,w:s["snapshots"][0]["article_files"].update({"extra.body.html":A,"extra.meta.json":A}),
 "unsafe_path":lambda s,w:s["snapshots"][0]["article_files"].update({"../bad.meta.json":A}),
 "unsafe_source":lambda s,w:s["snapshots"][0]["source_fragments"].update({"../oops.json":A}),
 "missing_source_readme":lambda s,w:s["snapshots"][0]["source_fragments"].pop("README.md"),
 "new_contributor_route":lambda s,w:s["snapshots"][2]["article_files"].update({"new.body.html":A,"new.meta.json":A}),
 "stale_original_blob":lambda s,w:s["snapshots"][0]["article_files"].update({"article-1.body.html":D}),
 "stale_workorder":lambda s,w:w["rows"][0].update(contributor_git_blob=B),
 "false_disposition":lambda s,w:w["rows"][0].update(disposition="APPROVED"),
 "false_row_approval":lambda s,w:w["rows"][0].update(requires_human_source_or_safety_adjudication=False),
 "missing_row":lambda s,w:w["rows"].pop(),
 "duplicated_row":lambda s,w:w["rows"].append(copy.deepcopy(w["rows"][0])),
 "wrong_row_count":lambda s,w:w.update(observation_count=100),
 "wrong_path_count":lambda s,w:w.update(unique_changed_paths=100),
 "wrong_nonexact_count":lambda s,w:w.update(non_exact_candidate_observations=100),
 "stale_head":lambda s,w:w.update(candidate_sha=D),
 "missing_head_map":lambda s,w:w["seven_contributor_heads"].pop("food"),
 "fake_overlap":lambda s,w:w.update(overlapping_paths=[{"path":"unknown"}]),
}
for name,fn in MUTATIONS.items():mutation(name,fn)


# R119: independent synthetic release-candidate-only coverage.
class CandidateOnlyBlindspotTests(unittest.TestCase):
    def test_candidate_only_body_never_disappears(self):
        s,w=fixture(); out=gate.build_crosswalk(s,w)
        rows={r["path"]:r for r in out["review_decisions"]}
        path=gate.ARTICLE_PREFIX+"article-1.body.html"
        self.assertEqual(out["candidate_only_blindspots"],[path])
        self.assertEqual(rows[path]["candidate_change_category"],
                         "CANDIDATE_ONLY_UNTRACKED_BY_R118")
        self.assertTrue(rows[path]["human_review_required"])
        self.assertEqual(rows[path]["human_decision"],"UNREVIEWED")
        self.assertFalse(out["may_publish"])
    def test_candidate_only_source_fragment_cannot_be_skipped(self):
        s,w=fixture()
        s["snapshots"][1]["source_fragments"]["start.json"]=D
        out=gate.build_crosswalk(s,w)
        p=gate.SOURCE_PREFIX+"start.json"
        self.assertIn(p,[r["path"] for r in out["review_decisions"]])
        self.assertIn(p,out["candidate_only_blindspots"])
        self.assertEqual(out["candidate_changed_files"],2)
        self.assertFalse(out["independent_QD_PASS"])
    def test_candidate_meta_only_is_p0(self):
        s,w=fixture()
        s["snapshots"][1]["article_files"]["article-1.meta.json"]=D
        out=gate.build_crosswalk(s,w)
        p=gate.ARTICLE_PREFIX+"article-1.meta.json"
        row=next(r for r in out["review_decisions"] if r["path"]==p)
        self.assertEqual(row["risk_priority"],"P0")
        self.assertEqual(row["human_decision"],"UNREVIEWED")
    def test_contributor_only_and_candidate_only_distinct(self):
        s,w=fixture(); out=gate.build_crosswalk(s,w)
        counts=out["review_count_by_category"]
        self.assertEqual(counts["CANDIDATE_ONLY_UNTRACKED_BY_R118"],1)
        self.assertEqual(counts["CANDIDATE_AND_CONTRIBUTOR"],0)
        self.assertEqual(counts["CONTRIBUTOR_ONLY_NOT_IN_CANDIDATE"],3)
    def test_candidate_changed_source_roster_rejected(self):
        s,w=fixture()
        s["snapshots"][1]["source_fragments"]["new.json"]=D
        with self.assertRaisesRegex(gate.Hold,"CANDIDATE_SOURCE_FRAGMENT_ROSTER_DRIFT"):
            gate.build_crosswalk(s,w)
    def test_candidate_removed_source_fragment_rejected(self):
        s,w=fixture()
        s["snapshots"][1]["source_fragments"].pop("food.json")
        with self.assertRaisesRegex(gate.Hold,"CANDIDATE_SOURCE_FRAGMENT_ROSTER_DRIFT"):
            gate.build_crosswalk(s,w)
    def test_reviewer_cannot_forge_candidate_only_approval(self):
        s,w=fixture();out=gate.build_crosswalk(s,w)
        row=next(r for r in out["review_decisions"] if
                 r["candidate_change_category"]=="CANDIDATE_ONLY_UNTRACKED_BY_R118")
        row["human_decision"]="APPROVED"
        with self.assertRaises(gate.Hold):gate.verify_crosswalk(s,w,out)
    def test_actual_35_article_snapshot_when_available(self):
        docs=Path(__file__).resolve().parents[1]/"docs"
        p=docs/"R117_NINE_SNAPSHOT_GIT_OBJECT_CUSTODY_HOLD.json"
        w=docs/"R117_SEVEN_BRANCH_SOURCE_CITATION_DIFF_WORKORDERS_HOLD.json"
        if not p.is_file() or not w.is_file():
            self.skipTest("exact repository evidence not present")
        o=gate.build_crosswalk(gate.strict_load(p),gate.strict_load(w))
        self.assertEqual(o["article_count"],35)
        self.assertEqual(o["contributor_change_observations"],24)
        self.assertEqual(o["candidate_changed_files"],28)
        self.assertEqual(len(o["candidate_only_blindspots"]),17)
        self.assertEqual(o["unique_changed_paths"],35)
        self.assertEqual(o["review_count_by_category"],
            {"CANDIDATE_ONLY_UNTRACKED_BY_R118":17,
             "CANDIDATE_AND_CONTRIBUTOR":11,
             "CONTRIBUTOR_ONLY_NOT_IN_CANDIDATE":7})

# Each original/candidate metadata pair is mandatory, including unchanged files.
for i,slug in enumerate(SLUGS):
    mutation("missing_candidate_metadata_%02d"%(i+1),
        lambda s,w,slug=slug:s["snapshots"][1]["article_files"].pop(slug+".meta.json"))

if __name__=="__main__":unittest.main()
