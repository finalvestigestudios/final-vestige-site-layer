#!/usr/bin/env python3
"""Offline exact-SHA source-to-staging evidence guard for Experience 2.0.

Reads a saved GitHub compare JSON. No network, WordPress, CI reruns, or writes.
A previously green staging artifact is NEVER inherited by a later HEAD.
Usage: python qualification_freshness.py compare.json --qualified-sha SHA --candidate-sha SHA
"""
import argparse
import json
from pathlib import Path
import re
import sys
import unittest

SHA = re.compile(r"^[0-9a-f]{40}$")

def verdict(payload, qualified_sha, candidate_sha):
    if not (SHA.fullmatch(qualified_sha) and SHA.fullmatch(candidate_sha)):
        return {"status":"HOLD","reason":"missing or malformed immutable commit SHA"}
    data = payload.get("result", payload)
    base = data.get("base_commit") or {}
    if base.get("sha") != qualified_sha:
        return {"status":"HOLD","reason":"comparison is not anchored at qualified SHA"}
    status = data.get("status")
    ahead = data.get("ahead_by")
    behind = data.get("behind_by")
    if status == "identical" and ahead == 0 and behind == 0 and qualified_sha == candidate_sha:
        return {"status":"EXACT_SHA_MATCH_ONLY","reason":"same source SHA; CI/QD/rights/manual gates still independent"}
    if status in ("ahead","behind","diverged") and isinstance(ahead,int) and isinstance(behind,int):
        return {"status":"HOLD","reason":"last qualified isolated WordPress evidence does not certify candidate HEAD",
                "ahead":ahead,"behind":behind,
                "changed_file_count":len(data.get("files") or [])}
    return {"status":"HOLD","reason":"missing, incompatible or untrusted compare data"}

class UnitTests(unittest.TestCase):
    q = "f9f9fc243ceed7df09a1674f533a9cf12c7a7c53"
    h = "a0f403de362a8418bb77d5cf226ba5cc2daf5aec"
    def sample(self, status, ahead, behind, base=None):
        return {"result":{"base_commit":{"sha":base or self.q},
            "status":status,"ahead_by":ahead,"behind_by":behind,
            "files":[{"filename":"experience2/home-flagship/index.html"}]}}
    def test_real_lineage_is_hold(self):
        v=verdict(self.sample("ahead",379,0),self.q,self.h)
        self.assertEqual((v["status"],v["ahead"],v["changed_file_count"]),("HOLD",379,1))
    def test_identical_exact_sha_is_only_source_match(self):
        self.assertEqual(verdict(self.sample("identical",0,0),self.q,self.q)["status"],"EXACT_SHA_MATCH_ONLY")
    def test_changed_head_even_identical_metadata_holds(self):
        self.assertEqual(verdict(self.sample("identical",0,0),self.q,self.h)["status"],"HOLD")
    def test_behind_holds(self):
        self.assertEqual(verdict(self.sample("behind",0,1),self.q,self.h)["status"],"HOLD")
    def test_diverged_holds(self):
        self.assertEqual(verdict(self.sample("diverged",5,3),self.q,self.h)["status"],"HOLD")
    def test_wrong_base_holds(self):
        self.assertEqual(verdict(self.sample("identical",0,0,base=self.h),self.q,self.q)["status"],"HOLD")
    def test_unknown_response_holds(self):
        self.assertEqual(verdict({"result":{"status":"ahead"}},self.q,self.h)["status"],"HOLD")
    def test_partial_sha_holds(self):
        self.assertEqual(verdict(self.sample("identical",0,0),"deadbeef",self.h)["status"],"HOLD")
    def test_empty_file_list_does_not_create_pass(self):
        x=self.sample("ahead",1,0);x["result"]["files"]=[]
        self.assertEqual(verdict(x,self.q,self.h)["status"],"HOLD")

if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("compare_json",nargs="?")
    p.add_argument("--qualified-sha")
    p.add_argument("--candidate-sha")
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    if args.self_test:
        suite=unittest.defaultTestLoader.loadTestsFromTestCase(UnitTests)
        if not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful():sys.exit(1)
    elif args.compare_json:
        if not args.qualified_sha or not args.candidate_sha:p.error("Both immutable SHAs required")
        v=verdict(json.loads(Path(args.compare_json).read_text()),args.qualified_sha,args.candidate_sha)
        print(json.dumps(v,indent=2))
        if v["status"]!="EXACT_SHA_MATCH_ONLY":sys.exit(1)
    else:p.error("supply --self-test or compare_json and both SHAs")
