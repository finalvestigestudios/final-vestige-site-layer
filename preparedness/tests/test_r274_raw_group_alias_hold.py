"""R274 synthetic no-release regression: compare raw source labels via review-only aliases."""
import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("r274_source", ROOT / "tools/r272_crosswalk_snapshot_hold.py")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
BASE = "https://example.org/report"


def fixture(urls, label):
    names = ("base", "food", "hist-food")[:len(urls)]
    sources = {name: [{"id": "duplicate", "url": url, "supports": name, "human_link_check": False}]
               for name, url in zip(names, urls)}
    sources["base"].append({"id": "solo", "url": "https://example.org/other", "supports": "separate"})
    paths = {name: "preparedness/sources/fragments/" + name + ".json" for name in names}
    group = {"url": label, "canonical_url": label,
             "review_status": "pending-human-source-and-reading-scope-review",
             "reviewer": None, "reviewed_on": None,
             "variants": [{"origin": name, "source_file": paths[name], "row_index": 0,
                           "source": copy.deepcopy(sources[name][0])} for name in names],
             "identities": [{"origin": name, "row_index": 0, "id": "duplicate"} for name in names]}
    x = {"schema_version": 1,
         "status": "DRAFT_CROSSWALK_ALL_SHARED_SOURCE_GROUPS_UNRESOLVED",
         "warning": "UNREVIEWED: not approved",
         "source_files": [{"origin": name, "path": paths[name], "count": len(sources[name]),
                           "git_blob_sha": "a"*40} for name in names],
         "source_head_commits": {name: "b"*40 for name in names},
         "article_origins": {"article-" + name: name for name in names},
         "groups": [group],
         "candidate_reconciliation_20261104": {"status": "DRAFT_UNREVIEWED_HOLD",
                                                **{flag: False for flag in gate.FLAGS}},
         "raw_source_rows": len(urls)+1, "unique_source_urls": len(set(urls))+1,
         "duplicate_url_groups": 1, "duplicate_id_groups": 1}
    census = {"rows": len(urls)+1, "exact_urls": len(set(urls))+1,
              "alias_urls": 2, "shared_groups": 1, "duplicate_id_groups": 1,
              "alias_variants": sum(u != label for u in urls),
              "article_origins": len(names)}
    return x, sources, census


GOOD = {
    "all_slash": ([BASE+"/", BASE+"/"], BASE+"/"),
    "all_no_slash": ([BASE, BASE], BASE),
    "root_slash": (["https://nchfp.uga.edu/"]*2, "https://nchfp.uga.edu/"),
    "url_with_query": ([BASE+"/?st=list"]*2, BASE+"/?st=list"),
    "url_with_fragment": ([BASE+"/#ref"]*2, BASE+"/#ref"),
    "majority_slash": ([BASE+"/", BASE+"/", BASE], BASE+"/"),
    "majority_no_slash": ([BASE, BASE, BASE+"/"], BASE),
    "tied_urls": ([BASE, BASE+"/"], BASE),
}
BAD = {
    "change_slash_label": "url_slashless",
    "change_no_slash_label": "url_slash",
    "forged_canonical": "canonical",
    "false_reviewer": "reviewer",
    "false_group_approval": "status",
    "alter_claim": "claim",
    "alter_source_url": "source_url",
    "alter_variant_origin": "variant_origin",
    "alter_variant_path": "variant_path",
    "omit_variant": "omit_variant",
    "false_independent_qd": "qd",
    "false_publish": "publish",
    "replace_query": "query",
    "replace_fragment": "fragment",
    "wrong_subpath": "subpath",
    "wrong_host": "host",
}

class AliasLabelTests(unittest.TestCase):
    def test_query_not_discarded(self):
        self.assertNotEqual(gate.alias(BASE+"?a=1"), gate.alias(BASE+"?a=2"))

    def test_fragment_not_discarded(self):
        self.assertNotEqual(gate.alias(BASE+"#a"), gate.alias(BASE+"#b"))

    def test_terminal_slash_only_equivalence(self):
        self.assertEqual(gate.alias(BASE), gate.alias(BASE+"/"))
        self.assertNotEqual(gate.alias(BASE), gate.alias(BASE+"/child"))

    def test_pin_r273_matches_exact_gate(self):
        from importlib.util import spec_from_file_location
        source = (ROOT / "tools/r272_crosswalk_snapshot_hold.py").read_bytes()
        r273 = (ROOT / "tools/r273_source_review_docket_hold.py").read_text()
        self.assertIn('SOURCE_GATE_BLOB = "' + gate.blob(source) + '"', r273)

    def test_audit_cannot_upgrade_invalid_custody_to_pass(self):
        result = gate.audit(Path("."), lambda root, rel: b"not the frozen crosswalk")
        self.assertEqual(result["state"], gate.INVALID)
        self.assertFalse(result["publication_authorized"])


for title, (urls, label) in GOOD.items():
    def allowed(self, urls=urls, label=label):
        x, sources, counts = fixture(urls, label)
        before = copy.deepcopy((x, sources))
        result = gate.inspect(x, sources, census=counts)
        self.assertEqual(result["state"], gate.HOLD)
        self.assertEqual(result["counts"], counts)
        self.assertFalse(result["independent_qd_pass"])
        self.assertFalse(result["publication_authorized"])
        self.assertEqual((x, sources), before, "gate must not rewrite source evidence")
    setattr(AliasLabelTests, "test_accept_historical_" + title, allowed)


for title, mutation in BAD.items():
    def rejected(self, mutation=mutation):
        urls = [BASE, BASE+"/"] if mutation == "url_slash" else [BASE+"/", BASE+"/"]
        label = BASE if mutation == "url_slash" else BASE+"/"
        if mutation == "url_slash":
            urls, label = [BASE, BASE+"/"], BASE
        x, sources, counts = fixture(urls, label)
        group = x["groups"][0]
        if mutation == "url_slashless": group["url"] = BASE
        elif mutation == "url_slash": group["url"] = BASE+"/"
        elif mutation == "canonical": group["canonical_url"] = BASE
        elif mutation == "reviewer": group["reviewer"] = "unapproved"
        elif mutation == "status": group["review_status"] = "approved"
        elif mutation == "claim": group["variants"][0]["source"]["supports"] = "rewritten"
        elif mutation == "source_url": sources["food"][0]["url"] = BASE
        elif mutation == "variant_origin": group["variants"][0]["origin"] = "food"
        elif mutation == "variant_path": group["variants"][0]["source_file"] = "wrong"
        elif mutation == "omit_variant": group["variants"].pop()
        elif mutation == "qd": x["candidate_reconciliation_20261104"]["independent_QD_PASS"] = True
        elif mutation == "publish": x["candidate_reconciliation_20261104"]["may_publish"] = True
        elif mutation == "query": group["url"] = BASE+"/?different=true"
        elif mutation == "fragment": group["url"] = BASE+"/#other"
        elif mutation == "subpath": group["url"] = BASE+"/child"
        elif mutation == "host": group["url"] = "https://other.org/report/"
        with self.assertRaises((ValueError, KeyError, TypeError, AttributeError)):
            gate.inspect(x, sources, census=counts)
    setattr(AliasLabelTests, "test_reject_" + title, rejected)


if __name__ == "__main__":
    unittest.main()
