"""Deterministic synthetic adversarial tests; do not qualify safety or publications."""
import copy
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "tools" / "r398_adjudication_review_gate.py"
spec = importlib.util.spec_from_file_location("r398_gate", SOURCE)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


def sha(x):
    return hashlib.sha1(str(x).encode()).hexdigest()


def fixture():
    branches = sorted(g.FORK_BRANCHES | {f"claude/prep-sample-{i}" for i in range(6)})
    pins = [{"branch": b, "sha": sha(b)} for b in branches]
    ids = sorted(g.SOURCE_IDS) + [f"src-{i:03d}" for i in range(198)]
    items = []
    for i, sid in enumerate(ids):
        vs = [{"branch": branches[i % 9], "source_blob": sha((i, 0)), "url": f"https://example.org/doc/{i}"}]
        if i < 77:
            b = branches[(i+1) % 9]
            vs.append({"branch": b, "source_blob": sha((i, 1)), "url": f"https://example.org/doc/{i}"})
        items.append({"source_id": sid, "variants": vs})
    aliases = []
    for i in range(17):
        left, right = items[5 + 2*i], items[6 + 2*i]
        url = f"https://example.org/shared/{i}"
        for x in (left, right):
            for v in x["variants"]:
                v["url"] = url
        aliases.append({"url": url, "ids": [left["source_id"], right["source_id"]], "review_required": True})
    disputes = []
    for i, sid in enumerate(sorted(g.SOURCE_IDS)):
        vset = items[i]["variants"]
        cases = []
        for j, v in enumerate(vset):
            cases.append({**v, "verified_on": "2026-11-15", "human_link_check": False,
                "publisher": "Test publisher", "fragment": "preparedness/sources/fragments/food.json",
                "supports_exact": f"Test original scoped claim {sid} variant {j}",
                "reading_scope_notes_exact": f"Original reading scope notes {sid} variant {j}"})
        disputes.append({"source_id": sid, "decision": "HUMAN_REVIEW_REQUIRED", "selected_record": None, "variants": cases})
    article_slugs = ["family-communication-plan", "home-fire-escape-plan", "outage-heat-cold-generators", "shelter-or-evacuate"] + [f"article-{i:02d}" for i in range(31)]
    articles = [{"slug": s, "body_candidate_git_blobs": [sha((s, k)) for k in range(3)]} for s in article_slugs]
    forks = []
    for slug in article_slugs[:4]:
        for extension in ("body.html", "meta.json"):
            v = []
            for i, branch in enumerate(sorted(g.FORK_BRANCHES)):
                h = sha((slug, i)) if extension == "body.html" else sha((slug, "meta", i))
                v.append({"branch": branch, "git_blob_sha": h, "byte_length": 200 + i})
            forks.append({"path": f"preparedness/content/articles/{slug}.{extension}",
                          "decision": "HUMAN_REVIEW_REQUIRED", "selected_sha": None,
                          "requires_reading_depth_review": True, "requires_source_citation_review": True, "variants": v})
    forks.append({"path": "preparedness/sources/fragments/shelter.json", "decision": "HUMAN_REVIEW_REQUIRED",
                  "selected_sha": None, "requires_reading_depth_review": True, "requires_source_citation_review": True,
                  "variants": [{"branch": b, "git_blob_sha": sha((b,"source")), "byte_length": 222}
                               for b in sorted(g.FORK_BRANCHES)]})
    return {"schema": 1, "repo": "finalvestigestudios/final-vestige-site-layer", "issue": 136,
        "parent_conversion_issue": 820, "provenance": "ORIGINAL_UNSELECTED_GIT_SOURCE_INVENTORY",
        "original_git_blob_pins": copy.deepcopy(g.PINNED_BLOBS),
        "expected": copy.deepcopy(g.COUNTS), "observed": copy.deepcopy(g.COUNTS),
        "release_state": "DRAFT_HARD_HOLD", "publication_approved": False,
        "qualified_safety_approved": False, "merchant_offer_verified": False,
        "automatic_variant_selection": False, "qualified_review_backlog": sorted(g.REQUIRED_BACKLOG),
        "branch_pins": pins, "all_original_source_id_crosswalk": items,
        "source_evidence_disputes": disputes, "original_articles": articles,
        "original_fork_disputes": forks, "shared_exact_url_review_groups": aliases}


class R398ReviewGateTests(unittest.TestCase):
    def test_valid_synthetic_inventory_still_hard_hold(self):
        outcome = g.audit(fixture())
        self.assertEqual(outcome["errors"], [])
        self.assertEqual(outcome["integrity"], "PASS")
        self.assertEqual(outcome["release"], "HARD_HOLD")
        self.assertEqual(len(outcome["cases"]), 14)

    def test_read_only(self):
        d = fixture()
        before = json.dumps(d, sort_keys=True)
        g.audit(d)
        self.assertEqual(before, json.dumps(d, sort_keys=True))

    def test_template_remains_unselected(self):
        d = fixture()
        t = g.proposal_template(d)
        self.assertEqual(len(t["cases"]), 14)
        self.assertFalse(t["release_approval"])
        self.assertTrue(t["review_only"])
        self.assertEqual(g.check_proposals(d,t), [])

    def test_valid_proposal_is_never_release(self):
        d = fixture()
        t = g.proposal_template(d)
        t["cases"][0].update({"status": "PROPOSED_FOR_QD_ONLY",
                              "proposed_git_blob": t["cases"][0]["candidate_blobs"][0],
                              "reviewer_evidence_url": "https://example.org/review/1",
                              "scope_note": "Source text and original historical context cross-read."})
        self.assertEqual(g.check_proposals(d, t), [])
        self.assertEqual(g.audit(d)["release"], "HARD_HOLD")

    def test_invalid_input_fails_closed(self):
        self.assertEqual(g.audit([])["release"], "HARD_HOLD")
        self.assertEqual(g.audit(None)["integrity"], "FAIL")

    def test_git_hash_algorithm(self):
        b=b"hello\n"
        self.assertEqual(g.git_blob_sha(b), hashlib.sha1(b"blob 6\x00hello\n").hexdigest())

    def test_cli_missing_input_hard_hold(self):
        with tempfile.TemporaryDirectory() as temp:
            self.assertEqual(g.main(["--docket", str(Path(temp)/"absent.json")]), 2)

    def test_cli_docket_byte_mismatch_hard_hold(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/"docket.json"
            p.write_text(json.dumps(fixture()))
            self.assertEqual(g.main(["--docket", str(p)]), 2)


# Each mutation is a distinct unittest method, not just one parametrized subtest.
MUTATIONS = [
 ("schema_changed", lambda d: d.update(schema=2)),
 ("repo_changed", lambda d: d.update(repo="other/repo")),
 ("issue_changed", lambda d: d.update(issue=820)),
 ("parent_issue_changed", lambda d: d.update(parent_conversion_issue=136)),
 ("provenance_changed", lambda d: d.update(provenance="AUTHOR_APPROVED")),
 ("manifest_blob_tampered", lambda d: d["original_git_blob_pins"].update(manifest=sha("bad"))),
 ("source_blob_tampered", lambda d: d["original_git_blob_pins"].update(source_fragment_crosswalk=sha("bad"))),
 ("base_blob_tampered", lambda d: d["original_git_blob_pins"].update(base_source_register=sha("bad"))),
 ("expected_articles_forged", lambda d: d["expected"].update(original_article_count=34)),
 ("observed_sources_forged", lambda d: d["observed"].update(original_distinct_source_ids=200)),
 ("publication_approved", lambda d: d.update(publication_approved=True)),
 ("safety_approved", lambda d: d.update(qualified_safety_approved=True)),
 ("merchant_approved", lambda d: d.update(merchant_offer_verified=True)),
 ("automatic_selection", lambda d: d.update(automatic_variant_selection=True)),
 ("release_state_changed", lambda d: d.update(release_state="PASS")),
 ("missing_qd_backlog", lambda d: d["qualified_review_backlog"].remove("TOOL_104_CHILD_PRIVACY")),
 ("duplicate_branch_pin", lambda d: d["branch_pins"].append(copy.deepcopy(d["branch_pins"][0]))),
 ("branch_sha_malformed", lambda d: d["branch_pins"][0].update(sha="x")),
 ("shelter_branch_missing", lambda d: d["branch_pins"][0].update(branch="claude/prep-random")),
 ("source_crosswalk_removed", lambda d: d["all_original_source_id_crosswalk"].pop()),
 ("source_crosswalk_duplicate_id", lambda d: d["all_original_source_id_crosswalk"][0].update(source_id=d["all_original_source_id_crosswalk"][1]["source_id"])),
 ("source_crosswalk_bad_url", lambda d: d["all_original_source_id_crosswalk"][42]["variants"][0].update(url="file:///etc/passwd")),
 ("source_crosswalk_bad_sha", lambda d: d["all_original_source_id_crosswalk"][42]["variants"][0].update(source_blob="0")),
 ("source_occurrence_missing", lambda d: d["all_original_source_id_crosswalk"][42]["variants"].pop()),
 ("source_occurrence_duplicate", lambda d: d["all_original_source_id_crosswalk"][42]["variants"].append(copy.deepcopy(d["all_original_source_id_crosswalk"][42]["variants"][0]))),
 ("dispute_case_removed", lambda d: d["source_evidence_disputes"].pop()),
 ("dispute_id_changed", lambda d: d["source_evidence_disputes"][0].update(source_id="bogus")),
 ("dispute_automatically_selected", lambda d: d["source_evidence_disputes"][0].update(selected_record=0)),
 ("dispute_marked_approved", lambda d: d["source_evidence_disputes"][0].update(decision="APPROVED")),
 ("dispute_scope_erased", lambda d: d["source_evidence_disputes"][0]["variants"][0].update(reading_scope_notes_exact="")),
 ("dispute_claim_erased", lambda d: d["source_evidence_disputes"][0]["variants"][0].update(supports_exact="")),
 ("dispute_crosswalk_broken", lambda d: d["source_evidence_disputes"][0]["variants"][0].update(url="https://example.org/wrong")),
 ("dispute_link_check_untyped", lambda d: d["source_evidence_disputes"][0]["variants"][0].update(human_link_check="pass")),
 ("dispute_duplicate_branch", lambda d: d["source_evidence_disputes"][0]["variants"][1].update(branch=d["source_evidence_disputes"][0]["variants"][0]["branch"])),
 ("article_missing", lambda d: d["original_articles"].pop()),
 ("article_duplicate_slug", lambda d: d["original_articles"][1].update(slug=d["original_articles"][0]["slug"])),
 ("article_body_digest_missing", lambda d: d["original_articles"][2].update(body_candidate_git_blobs=[])),
 ("article_body_digest_malformed", lambda d: d["original_articles"][2].update(body_candidate_git_blobs=["0"])),
 ("fork_missing", lambda d: d["original_fork_disputes"].pop()),
 ("fork_path_traversal", lambda d: d["original_fork_disputes"][0].update(path="preparedness/../evil.json")),
 ("fork_path_duplicate", lambda d: d["original_fork_disputes"][1].update(path=d["original_fork_disputes"][0]["path"])),
 ("fork_selected", lambda d: d["original_fork_disputes"][0].update(selected_sha=sha("selected"))),
 ("fork_decision_pass", lambda d: d["original_fork_disputes"][0].update(decision="APPROVED")),
 ("fork_reading_scope_false", lambda d: d["original_fork_disputes"][0].update(requires_reading_depth_review=False)),
 ("fork_citation_scope_false", lambda d: d["original_fork_disputes"][0].update(requires_source_citation_review=False)),
 ("fork_branch_missing", lambda d: d["original_fork_disputes"][0]["variants"].pop()),
 ("fork_digest_corrupted", lambda d: d["original_fork_disputes"][0]["variants"][0].update(git_blob_sha="x")),
 ("fork_size_negative", lambda d: d["original_fork_disputes"][0]["variants"][0].update(byte_length=-1)),
 ("fork_article_mismatch", lambda d: d["original_fork_disputes"][0]["variants"][0].update(git_blob_sha=sha("orphan"))),
 ("alias_group_missing", lambda d: d["shared_exact_url_review_groups"].pop()),
 ("alias_review_waived", lambda d: d["shared_exact_url_review_groups"][0].update(review_required=False)),
 ("alias_unknown_id", lambda d: d["shared_exact_url_review_groups"][0]["ids"].append("unknown")),
 ("alias_nonmatching_url", lambda d: d["shared_exact_url_review_groups"][0].update(url="https://example.org/other")),
 ("alias_same_id_twice", lambda d: d["shared_exact_url_review_groups"][0]["ids"].append(d["shared_exact_url_review_groups"][0]["ids"][0])),
 ("alias_url_duplicate", lambda d: d["shared_exact_url_review_groups"][0].update(url=d["shared_exact_url_review_groups"][1]["url"])),
]

for name, mutate in MUTATIONS:
    def test(self, mutate=mutate, name=name):
        d=fixture()
        mutate(d)
        got=g.audit(d)
        self.assertEqual(got["release"],"HARD_HOLD")
        self.assertEqual(got["integrity"],"FAIL",name)
        self.assertTrue(got["errors"],name)
    setattr(R398ReviewGateTests, "test_reject_"+name, test)

PROPOSAL_MUTATIONS = [
 ("wrong_schema", lambda t: t.update(schema=2)),
 ("approval_bit", lambda t: t.update(release_approval=True)),
 ("review_only_false", lambda t: t.update(review_only=False)),
 ("duplicate_case", lambda t: t["cases"].append(copy.deepcopy(t["cases"][0]))),
 ("unknown_case", lambda t: t["cases"][0].update(id="not-real")),
 ("invalid_status", lambda t: t["cases"][0].update(status="APPROVED")),
 ("prohibited_selection", lambda t: t["cases"][0].update(selected=True)),
 ("prohibited_qd_pass", lambda t: t["cases"][0].update(qd_pass=True)),
 ("invalid_proposed_sha", lambda t: t["cases"][0].update(status="PROPOSED_FOR_QD_ONLY",proposed_git_blob=sha("forged"),reviewer_evidence_url="https://example.org/review",scope_note="A full original reading scope note about documentation")),
 ("proposal_missing_url", lambda t: t["cases"][0].update(status="PROPOSED_FOR_QD_ONLY",proposed_git_blob=t["cases"][0]["candidate_blobs"][0],scope_note="A full original reading scope note about documentation")),
 ("proposal_scope_too_short", lambda t: t["cases"][0].update(status="PROPOSED_FOR_QD_ONLY",proposed_git_blob=t["cases"][0]["candidate_blobs"][0],reviewer_evidence_url="https://example.org/review",scope_note="too short")),
]
for name, mutate in PROPOSAL_MUTATIONS:
    def test(self, mutate=mutate, name=name):
        d=fixture();t=g.proposal_template(d);mutate(t)
        self.assertTrue(g.check_proposals(d,t),name)
    setattr(R398ReviewGateTests,"test_proposal_reject_"+name,test)

if __name__=="__main__":
    unittest.main()
