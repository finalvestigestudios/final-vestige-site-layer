"""R409 deterministic synthetic graph tamper tests. NOT real-source/QD approval."""
from __future__ import annotations
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

FILE = Path(__file__).resolve().parents[1] / "tools" / "r409_source_equivalence_gate.py"
spec=importlib.util.spec_from_file_location("r409_gate",FILE)
g=importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)
COUNT={**g.COUNTS,"original_distinct_source_ids":34,"source_record_occurrences":36}

def fixture():
    pins=[{"branch":f"claude/prep-{i}","sha":f"{i+1:040x}"} for i in range(9)]
    a=[{"slug":f"item-{i}","body_candidate_git_blobs":[f"{i+30:040x}"]} for i in range(35)]
    ids=[]; groups=[]
    for i in range(17):
        url=f"https://www.ready.gov/test-{i}"
        names=[f"evidence-{i}-a",f"evidence-{i}-b"]
        groups.append({"url":url,"ids":names,"review_required":True})
        for j,n in enumerate(names):
            vs=[{"branch":"claude/prep-0","source_blob":f"{i*2+j+100:040x}","url":url}]
            if i==0:vs.append({"branch":"claude/prep-1","source_blob":f"{j+201:040x}","url":url})
            ids.append({"source_id":n,"variants":vs})
    disputes=[{"source_id":f"scope-{i}","decision":"HUMAN_REVIEW_REQUIRED","selected_record":None,"variants":[{"branch":"one"},{"branch":"two"}]} for i in range(5)]
    forks=[{"path":f"preparedness/content/{i}.html","decision":"HUMAN_REVIEW_REQUIRED","selected_sha":None,"variants":[{"branch":"one"},{"branch":"two"}],"requires_reading_depth_review":True,"requires_source_citation_review":True} for i in range(9)]
    return {"schema":1,"provenance":"ORIGINAL_UNSELECTED_GIT_SOURCE_INVENTORY","issue":136,
            "release_state":"DRAFT_HARD_HOLD","publication_approved":False,"qualified_safety_approved":False,
            "merchant_offer_verified":False,"automatic_variant_selection":False,
            "expected":dict(COUNT),"observed":dict(COUNT),"original_articles":a,
            "all_original_source_id_crosswalk":ids,"shared_exact_url_review_groups":groups,
            "source_evidence_disputes":disputes,"original_fork_disputes":forks,"branch_pins":pins}

def check(d):return g.audit(d,counts=COUNT,require_pin=False)

class Baseline(unittest.TestCase):
    def test_control_fixture_integrity_only(self):
        r=check(fixture()); self.assertTrue(r["integrity_ok"],r["errors"])
        self.assertFalse(r["eligible"])
        self.assertFalse(r["publication_approved"])
        self.assertEqual(r["release_state"],"DRAFT_HARD_HOLD")
        self.assertEqual(r["counts"]["exact_url_review_groups"],17)
        self.assertEqual(len([x for x in r["risks"] if x["kind"]=="EXACT_URL_DISTINCT_SOURCE_IDS"]),17)
    def test_git_blob_hash(self):self.assertEqual(g.blob(b"test\n"),"9daeafb9864cf43055ae93beb0afd6c7d144bfa4")
    def test_source_pin_refused_without_original(self):self.assertIn("original R397 Git blob mismatch/missing",g.audit(fixture(),counts=COUNT)["errors"])
    def test_data_not_dict(self):self.assertFalse(g.audit([],counts=COUNT)["eligible"])
    def test_non_https_rejected(self):
        for raw in ["http://ready.gov/","ftp://ready.gov/","//ready.gov/","https://a:44/x","https://user@ready.gov/","https://ready.gov/has space","https://ready.gov/\n"]:
            with self.subTest(url=raw),self.assertRaises(ValueError):g.checked_url(raw)
    def test_normalization_does_not_discard_query(self):self.assertNotEqual(g.checked_url("https://ready.gov/a?k=1"),g.checked_url("https://ready.gov/a?k=2"))
    def test_fragment_only_ignored_in_warning_normalization(self):self.assertEqual(g.checked_url("https://ready.gov/a#one"),g.checked_url("https://ready.gov/a#two"))
    def test_regular_file_read(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"d.json"; p.write_bytes(b"abc")
            self.assertEqual(g.read_original(p),b"abc")
    def test_symlink_not_read(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"real"; p.write_bytes(b"x"); q=Path(t)/"link"; q.symlink_to(p)
            with self.assertRaises(ValueError):g.read_original(q)
    def test_oversize_not_read(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"big"; p.write_bytes(b"x"*11)
            with self.assertRaises(ValueError):g.read_original(p,max_bytes=10)
    def test_hardlink_not_read(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"a"; p.write_bytes(b"x"); q=Path(t)/"b"; q.hardlink_to(p)
            with self.assertRaises(ValueError):g.read_original(q)
    def test_duplicate_json_keys_not_accepted(self):
        with self.assertRaises(ValueError):json.loads('{"x":1,"x":2}',object_pairs_hook=g.unique_pairs)
    def test_missing_cli_is_hard_hold_exit2(self):
        r=subprocess.run([sys.executable,str(FILE),"/definitely/missing/r397.json"],capture_output=True,text=True)
        self.assertEqual(r.returncode,2)
        self.assertFalse(json.loads(r.stdout)["eligible"])

# Every attack runs as its own distinct unittest; no global graph state mutation.
ATTACKS=[]
for k,v in [("schema",2),("provenance","OTHER"),("issue",820),("release_state","PASS"),
            ("publication_approved",True),("qualified_safety_approved",True),
            ("merchant_offer_verified",True),("automatic_variant_selection",True)]:
    ATTACKS.append((f"root_{k}",lambda d,k=k,v=v:d.__setitem__(k,v)))
for section in ("expected","observed"):
    for k in COUNT:
        ATTACKS.append((f"count_{section}_{k}",lambda d,section=section,k=k:d[section].__setitem__(k,d[section][k]+1)))
ATTACKS += [
 ("lost_article",lambda d:d["original_articles"].pop()),
 ("duplicate_article",lambda d:d["original_articles"][1].__setitem__("slug",d["original_articles"][0]["slug"])),
 ("illegal_article_slug",lambda d:d["original_articles"][0].__setitem__("slug","Foo Bar")),
 ("lost_id",lambda d:d["all_original_source_id_crosswalk"].pop()),
 ("duplicate_id",lambda d:d["all_original_source_id_crosswalk"][1].__setitem__("source_id",d["all_original_source_id_crosswalk"][0]["source_id"])),
 ("invalid_id",lambda d:d["all_original_source_id_crosswalk"][0].__setitem__("source_id","Source One")),
 ("lost_variant",lambda d:d["all_original_source_id_crosswalk"][0]["variants"].pop()),
 ("bad_source_git_blob",lambda d:d["all_original_source_id_crosswalk"][0]["variants"][0].__setitem__("source_blob","abc")),
 ("unknown_contributor",lambda d:d["all_original_source_id_crosswalk"][0]["variants"][0].__setitem__("branch","ghost/branch")),
 ("source_http",lambda d:d["all_original_source_id_crosswalk"][0]["variants"][0].__setitem__("url","http://unsafe.invalid")),
 ("source_url_rewrite",lambda d:d["all_original_source_id_crosswalk"][0]["variants"][0].__setitem__("url","https://ready.gov/different")),
 ("lost_shared_url_group",lambda d:d["shared_exact_url_review_groups"].pop()),
 ("wrong_shared_group_id",lambda d:d["shared_exact_url_review_groups"][0]["ids"].__setitem__(0,"wrong")),
 ("duplicate_shared_url_group",lambda d:d["shared_exact_url_review_groups"][1].__setitem__("url",d["shared_exact_url_review_groups"][0]["url"])),
 ("group_review_false",lambda d:d["shared_exact_url_review_groups"][0].__setitem__("review_required",False)),
 ("group_reorder",lambda d:d["shared_exact_url_review_groups"][0]["ids"].reverse()),
 ("lost_dispute",lambda d:d["source_evidence_disputes"].pop()),
 ("source_auto_select",lambda d:d["source_evidence_disputes"][0].__setitem__("selected_record",{"id":"unsafe"})),
 ("source_decision_pass",lambda d:d["source_evidence_disputes"][0].__setitem__("decision","PASS")),
 ("source_variant_lost",lambda d:d["source_evidence_disputes"][0]["variants"].pop()),
 ("lost_fork",lambda d:d["original_fork_disputes"].pop()),
 ("fork_auto_select",lambda d:d["original_fork_disputes"][0].__setitem__("selected_sha","abc")),
 ("fork_decision_pass",lambda d:d["original_fork_disputes"][0].__setitem__("decision","PASS")),
 ("fork_depth_false",lambda d:d["original_fork_disputes"][0].__setitem__("requires_reading_depth_review",False)),
 ("fork_source_false",lambda d:d["original_fork_disputes"][0].__setitem__("requires_source_citation_review",False)),
 ("fork_variant_lost",lambda d:d["original_fork_disputes"][0]["variants"].pop()),
 ("branch_lost",lambda d:d["branch_pins"].pop()),
 ("branch_duplicate",lambda d:d["branch_pins"][1].__setitem__("branch",d["branch_pins"][0]["branch"])),
 ("branch_bad_sha",lambda d:d["branch_pins"][0].__setitem__("sha","some-sha")),
]

def make_attack(name,edit):
    def test(self):
        d=fixture();edit(d);r=check(d)
        self.assertFalse(r["integrity_ok"],f"{name}: {r}")
        self.assertFalse(r["eligible"])
    test.__name__="test_attack_"+name
    return test

class Attacks(unittest.TestCase):pass
for name, fn in ATTACKS:setattr(Attacks,"test_attack_"+name,make_attack(name,fn))
