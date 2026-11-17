"""R446 deterministic synthetic negative tests; never constitute safety or QD approval."""
from __future__ import annotations
import copy
import importlib.util
import json
from pathlib import Path
import unittest

module=Path(__file__).resolve().parents[1]/"tools"/"r446_original_review_packet_integrity.py"
spec=importlib.util.spec_from_file_location("r446_integrity",module)
gate=importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
NAMES=("fsis-power-failure","loc-pioneer-diaries","loc-prairie-traveler","nchfp-home","nchfp-jerky")


def fixture():
    pins=[{"branch":f"claude/prep-{i}","sha":f"{i:040x}"} for i in range(1,10)]
    ids=[f"source-{i:03d}" for i in range(203)]
    ids[:5]=NAMES
    url={}
    pos=0
    for k in range(17):
        size=3 if k<5 else 2
        for sid in ids[pos:pos+size]: url[sid]=f"https://example.test/shared/{k}"
        pos+=size
    for j,sid in enumerate(ids[pos:]): url[sid]=f"https://example.test/unique/{j}"
    rows=[]
    for i,sid in enumerate(ids):
        variants=[{"branch":pins[0]["branch"],"source_blob":f"{100+i:040x}","url":url[sid]}]
        if i<77: variants.append({"branch":pins[1]["branch"],"source_blob":f"{1000+i:040x}","url":url[sid]})
        rows.append({"source_id":sid,"variants":variants})
    groups=[{"url":f"https://example.test/shared/{k}","ids":[s for s in ids if url[s]==f"https://example.test/shared/{k}"],"review_required":True} for k in range(17)]
    disputes=[{"source_id":ids[i],"decision":"HUMAN_REVIEW_REQUIRED","selected_record":None,
      "variants":[dict(v,supports_exact=f"Evidence claim {j}",reading_scope_notes_exact=f"Exact pages read {j}")
        for j,v in enumerate(rows[i]["variants"])]} for i in range(5)]
    forks=[{"path":f"preparedness/content/articles/fork-{i}.body.html","decision":"HUMAN_REVIEW_REQUIRED",
      "selected_sha":None,"requires_reading_depth_review":True,"requires_source_citation_review":True,
      "variants":[{"branch":pins[j]["branch"],"source_blob":f"{700+i*3+j:040x}"} for j in range(3)]} for i in range(9)]
    articles=[{"slug":f"article-{i}","body_candidate_git_blobs":[f"{i+300:040x}"]} for i in range(35)]
    original={"schema":1,"issue":136,"parent_conversion_issue":820,"release_state":gate.RELEASE,
      "publication_approved":False,"qualified_safety_approved":False,"automatic_variant_selection":False,
      "merchant_offer_verified":False,"branch_pins":pins,"original_articles":articles,
      "all_original_source_id_crosswalk":rows,"shared_exact_url_review_groups":groups,
      "source_evidence_disputes":disputes,"original_fork_disputes":forks}
    packet={"schema":"R446_ORIGINAL_ADJUDICATION_REVIEW_ONLY_v1","release_state":gate.RELEASE,
      "qualified_review_approved":False,"publishable":False,"safety_approved":False,"merchant_offer_verified":False,
      "original_docket":{"git_blob":None},"branch_pins":copy.deepcopy(pins),
      "article_identities":[{"slug":a["slug"],"body_candidate_git_blobs":a["body_candidate_git_blobs"]} for a in articles],
      "source_scope_review":[{"source_id":s["source_id"],"source_variants":copy.deepcopy(s["variants"]),
        "original_decision":s["decision"],"proposed_selection":None,"reviewer":None,
        "review_evidence":None,"qualified_safety_approved":False} for s in disputes],
      "manuscript_fork_review":[{"path":f["path"],"original_variants":copy.deepcopy(f["variants"]),
        "original_decision":f["decision"],"reading_depth_review_required":True,
        "source_citation_review_required":True,"proposed_selection":None,"reviewer":None,
        "review_evidence":None,"qualified_safety_approved":False} for f in forks],
      "duplicate_exact_url_review":[{"url":g["url"],"source_ids":sorted(g["ids"]),
        "review_required":True,"decision":"UNSELECTED","merge_authorized":False,"reviewer":None} for g in groups],
      "preservation_counts":dict(gate.COUNTS)}
    heads={p["branch"]:p["sha"] for p in pins}
    return original,packet,heads


def evaluate(original,packet,heads):
    raw=json.dumps(original,sort_keys=True).encode()
    before=gate.ORIGINAL_BLOB
    try:
        # Synthetic-only monkeypatch: installed module retains immutable real R397 pin.
        gate.ORIGINAL_BLOB=gate.git_blob(raw)
        packet["original_docket"]["git_blob"]=gate.ORIGINAL_BLOB
        return gate.check(original,packet,raw,heads)
    finally:
        gate.ORIGINAL_BLOB=before


class TestR446PacketIntegrity(unittest.TestCase):
    def setUp(self):
        self.o,self.p,self.heads=fixture()

    def test_complete_synthetic_counts_only(self):
        q=evaluate(self.o,self.p,self.heads)
        self.assertEqual(q["errors"],[],q["errors"])
        self.assertTrue(q["structural_evidence_pass"])
        self.assertEqual(q["counts"],gate.COUNTS)
        self.assertFalse(q["qd_pass"])
        self.assertFalse(q["publishable"])
        self.assertFalse(q["verified_paid_offer"])

    def test_real_git_pin_does_not_accept_synthetic(self):
        raw=json.dumps(self.o,sort_keys=True).encode()
        q=gate.check(self.o,self.p,raw,self.heads)
        self.assertIn("EXTERNAL_ORIGINAL_BLOB_PROOF_MISSING",q["errors"])

    def test_no_current_heads(self):
        self.assertIn("CURRENT_CONTRIBUTOR_SHA_NOT_PROVEN",evaluate(self.o,self.p,{})["errors"])

    def test_duplicate_json_key_error(self):
        with self.assertRaises(ValueError):
            json.loads('{"a":1,"a":2}',object_pairs_hook=gate.unique_pairs)

    def test_missing_original_byte_proof(self):
        q=gate.check(self.o,self.p,None,self.heads)
        self.assertFalse(q["structural_evidence_pass"])
        self.assertEqual(q["release_state"],gate.RELEASE)

    def test_original_to_packet_scope_literal_preserved(self):
        self.assertEqual(self.o["source_evidence_disputes"][0]["variants"],
                         self.p["source_scope_review"][0]["source_variants"])

    def test_all_17_urls_remain_separate(self):
        self.assertEqual(len(self.p["duplicate_exact_url_review"]),17)
        self.assertTrue(all(x["merge_authorized"] is False for x in self.p["duplicate_exact_url_review"]))

    def test_all_nine_forks_unselected(self):
        self.assertEqual(len(self.p["manuscript_fork_review"]),9)
        self.assertTrue(all(x["proposed_selection"] is None for x in self.p["manuscript_fork_review"]))


def mutation_test(i):
    def exercise(self):
        if i<5:
            self.p["source_scope_review"][i]["source_variants"][0]["reading_scope_notes_exact"]="silently altered"
            marker="CLAIM_OR_READING_SCOPE_VARIANT_DRIFT"
        elif i<10:
            self.p["source_scope_review"][i-5]["source_variants"][0]["supports_exact"]="different safety claim"
            marker="CLAIM_OR_READING_SCOPE_VARIANT_DRIFT"
        elif i<19:
            self.p["manuscript_fork_review"][i-10]["proposed_selection"]="f"*40
            marker="PREMATURE_MANUSCRIPT_APPROVAL"
        elif i<36:
            self.p["duplicate_exact_url_review"][i-19]["source_ids"][0]="source-200"
            marker="EXACT_URL_TO_IDS_DRIFT"
        elif i<45:
            self.heads[f"claude/prep-{i-35}"]="f"*40
            marker="CURRENT_CONTRIBUTOR_SHA_NOT_PROVEN"
        elif i<49:
            self.p[("qualified_review_approved","publishable","safety_approved","merchant_offer_verified")[i-45]]=True
            marker="FALSE_PACKET_APPROVAL"
        elif i<54:
            self.p["source_scope_review"][i-49]["reviewer"]="unapproved-reviewer"
            marker="PREMATURE_SOURCE_APPROVAL"
        else:
            self.p["article_identities"][i-54]["slug"]="lost-original-id"
            marker="ARTICLE_CANDIDATE_CUSTODY_DRIFT"
        result=evaluate(self.o,self.p,self.heads)
        self.assertIn(marker,result["errors"],(i,result["errors"]))
        self.assertEqual(result["release_state"],gate.RELEASE)
        self.assertFalse(result["publishable"])
    return exercise


for n in range(59):
    setattr(TestR446PacketIntegrity,f"test_negative_{n:02d}",mutation_test(n))

if __name__=="__main__":
    unittest.main()
