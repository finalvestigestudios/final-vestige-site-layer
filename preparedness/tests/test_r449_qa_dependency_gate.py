"""R449 synthetic regression suite. Never asserts QD, medical safety or commerce PASS."""
from __future__ import annotations
import copy
import importlib.util
from pathlib import Path
import unittest

P=Path(__file__).resolve().parents[1]/"tools"/"r449_qa_dependency_gate.py"
S=importlib.util.spec_from_file_location("r449_qa_dependency_gate",P)
g=importlib.util.module_from_spec(S)
S.loader.exec_module(g)

PINS=[{"branch":f"claude/prep-{i}", "sha":f"{i+80:040x}"} for i in range(9)]
def fixtures():
    prs=[]
    for n in g.EXPECTED:
        if n in g.ALLOWED:
            files=sorted(g.ALLOWED[n])
        elif n==2939:
            files=["preparedness/reviews/r449-test-only.md"]
        else:
            files=[g.PREFIXES[n]+"r449-test-only.md"]
        prs.append({"number":n,"head_sha":f"{n+80:040x}",
                    "base_sha":f"{n+5000:040x}",
                    "base":g.BASES[n],"state":"open","draft":True,
                    "filenames":files,"changed_files":len(files)})
    next(x for x in prs if x["number"]==2205)["base_sha"]=next(
        x for x in prs if x["number"]==169)["head_sha"]
    lock={"repo":"finalvestigestudios/final-vestige-site-layer",
          "source_issue":136,"business_issue":820,
          "release_state":g.HOLD,"publishable":False,"qd_approved":False,
          "paid_offer_verified":False,"paid_conversion_verified":False,
          "review_disputes":{"source":5,"forks":9,"shared_url_groups":17},
          "merge_decision":"NOT_APPROVED","branch_pins":copy.deepcopy(PINS),
          "pull_requests":prs}
    observed={"observed_at_utc":"2026-11-18T02:45:00Z",
              "observed_branch_heads":{p["branch"]:p["sha"] for p in PINS},
              "pull_requests":copy.deepcopy(prs)}
    ledger={"counts":copy.deepcopy(g.COUNTS),"branch_pins":copy.deepcopy(PINS),
            "release_state":g.HOLD,"publishable":False,
            "articles":[{"slug":f"article-{n}","publication_state":"HARD_HOLD",
                         "qualified_safety_state":"NOT_APPROVED",
                         "source_occurrences_bound_to_this_article":
                         "NOT_AUTHENTICATED_FROM_ORIGINAL_DOCKET"}
                        for n in range(35)]}
    return lock,observed,ledger

class TestR449(unittest.TestCase):
    def test_structural_pass_is_always_hard_hold(self):
        r=g.audit(*fixtures())
        self.assertEqual(r["errors"],[])
        self.assertTrue(r["structural_preflight_pass"])
        self.assertEqual(r["release_state"],g.HOLD)
        self.assertFalse(r["qd_pass"])
        self.assertFalse(r["publishable"])
        self.assertFalse(r["verified_fv_preparedness_offer"])
        self.assertIsNone(r["net_revenue_per_1000_qualified_sessions"])
    def test_detect_real_three_way_QA_overlap(self):
        r=g.audit(*fixtures())
        self.assertEqual(r["overlapping_files"],{g.OVERLAP:[157,169,2205]})
        self.assertTrue(r["required_manual_qa_merge_resolution"])
    def test_independent_readback_missing(self):
        l,o,s=fixtures()
        self.assertIn("NO_INDEPENDENT_FRESH_GITHUB_READBACK",g.audit(l,None,s)["errors"])
    def test_original_ledger_missing(self):
        l,o,s=fixtures()
        self.assertIn("NO_AUTHENTIC_ORIGINAL_LEDGER",g.audit(l,o,None)["errors"])
    def test_duplicate_json_keys_rejected(self):
        with self.assertRaises(ValueError):
            g.unique_object([("a",1),("a",2)])
    def test_valid_unique_json_keys(self):
        self.assertEqual(g.unique_object([("a",1),("b",2)]),{"a":1,"b":2})
    def test_source_count_mutation_blocks(self):
        l,o,s=fixtures();s["counts"]["source_ids"]=202
        self.assertIn("ORIGINAL_ARTICLE_SOURCE_CUSTODY_DRIFT",g.audit(l,o,s)["errors"])
    def test_original_branch_mutation_blocks(self):
        l,o,s=fixtures();o["observed_branch_heads"][PINS[0]["branch"]]="a"*40
        self.assertIn("FRESH_ORIGINAL_BRANCH_DRIFT",g.audit(l,o,s)["errors"])
    def test_dependent_parent_sha_mutation_blocks(self):
        l,o,s=fixtures()
        next(x for x in l["pull_requests"] if x["number"]==2205)["base_sha"]="a"*40
        self.assertIn("DEPENDENT_QA_PARENT_SHA_DRIFT",g.audit(l,o,s)["errors"])
    def test_unsafe_file_path_detected(self):
        l,o,s=fixtures()
        next(x for x in l["pull_requests"] if x["number"]==169)["filenames"].append("../escape")
        self.assertIn("PATH_INVALID:169",g.audit(l,o,s)["errors"])
    def test_test_file_conflicts_never_implicitly_resolved(self):
        l,o,s=fixtures();l["merge_decision"]="APPROVED"
        self.assertIn("MERGE_APPROVAL_INVENTED",g.audit(l,o,s)["errors"])
    def test_forced_original_article_release_detected(self):
        l,o,s=fixtures();s["articles"][0]["publication_state"]="PUBLISHED"
        self.assertIn("ORIGINAL_ARTICLE_SAFETY_OR_PLACEMENTS_UNPROVEN",g.audit(l,o,s)["errors"])

# 35 adversarial article-placement mutations and 6 exact PR HEAD drift tests.
for i in range(35):
    def mk_article(n):
        def test(self):
            l,o,s=fixtures()
            s["articles"][n]["qualified_safety_state"]="APPROVED"
            self.assertIn("ORIGINAL_ARTICLE_SAFETY_OR_PLACEMENTS_UNPROVEN",g.audit(l,o,s)["errors"])
        return test
    setattr(TestR449,f"test_article_{i:02d}_cannot_be_approved_by_metadata",mk_article(i))

for i in g.EXPECTED:
    def mk_pr(n):
        def test(self):
            l,o,s=fixtures()
            next(p for p in o["pull_requests"] if p["number"]==n)["head_sha"]="f"*40
            self.assertIn(f"FRESH_PR_DRIFT:{n}:head_sha",g.audit(l,o,s)["errors"])
        return test
    setattr(TestR449,f"test_pr_{i}_exact_head_sha_drift",mk_pr(i))

for i in g.EXPECTED:
    def mk_scope(n):
        def test(self):
            l,o,s=fixtures()
            row=next(p for p in l["pull_requests"] if p["number"]==n)
            row["filenames"].append("wp-content/live-merchant.php")
            row["changed_files"]+=1
            result=g.audit(l,o,s)["errors"]
            self.assertTrue(any(k.endswith(":"+str(n)) and (
                "SCOPE_DRIFT" in k or "FOREIGN_WORKSTREAM_CHANGE" in k or
                "INTEGRATION_MANUSCRIPT_TOUCH" in k) for k in result),result)
        return test
    setattr(TestR449,f"test_pr_{i}_cannot_write_foreign_scope",mk_scope(i))

for name,field,value,expected in [
    ("repo","repo","not-fv/repo","REPO_DRIFT"),
    ("source_issue","source_issue",999,"ISSUE_DRIFT"),
    ("business_issue","business_issue",999,"ISSUE_DRIFT"),
    ("publish","publishable",True,"FALSE_APPROVAL"),
    ("qd","qd_approved",True,"FALSE_APPROVAL"),
    ("sales","paid_conversion_verified",True,"FALSE_APPROVAL"),
    ("offer","paid_offer_verified",True,"FALSE_APPROVAL"),
    ("merge","merge_decision","READY","MERGE_APPROVAL_INVENTED"),
    ("disputes","review_disputes",{},"REVIEW_DISPUTES_LOST"),
]:
    def mk_state(f,v,e):
        def test(self):
            l,o,s=fixtures()
            l[f]=v
            self.assertIn(e,g.audit(l,o,s)["errors"])
        return test
    setattr(TestR449,"test_custody_mutation_"+name,mk_state(field,value,expected))

if __name__=="__main__":
    unittest.main()
