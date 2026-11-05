"""R133 synthetic, fully isolated, 35-article integrity adversarial tests.

No repository/shared-path writes, external network, medical approval or publication.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

MODULE = Path(__file__).with_name("r133_exact_ledger_gate.py")
SPEC = importlib.util.spec_from_file_location("r133_gate", MODULE)
G = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(G)


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def create_fixture(root):
    root = Path(root)
    p = root / "preparedness"
    d = p / "docs" / "r133"
    origins = ["base", "start", "shelter", "food", "health", "hist-food", "hist-home", "hist-field"]
    unique = [{"id": f"source-{i:03d}", "url": f"https://e.example/{i}",
               "supports": f"Distinct test source {i}", "notes": f"synthetic scope {i}"}
              for i in range(202)]
    rows = [(origins[i % 8], source) for i, source in enumerate(unique)]
    extra = 0
    for i in range(32):
        for _ in range(2 if i < 10 else 1):
            duplicate = dict(unique[i])
            if extra >= 19:
                duplicate["id"] = f"extra-source-{extra:02d}"
            rows.append((origins[(i + extra + 1) % 8], duplicate))
            extra += 1
    assert len(rows) == 244
    by_origin = {o: [] for o in origins}
    for origin, s in rows:
        by_origin[origin].append(s)
    files, by_source_id, by_url = [], {}, {}
    for origin in origins:
        path = ("register.json" if origin == "base" else "fragments/" + origin + ".json")
        file_path = p / "sources" / path
        write_json(file_path, {"sources": by_origin[origin]})
        sha = G.blob_sha(file_path.read_bytes())
        files.append({"origin": origin, "path": "preparedness/sources/" + path,
                      "sha": sha, "count": len(by_origin[origin])})
        for i, s in enumerate(by_origin[origin]):
            by_source_id.setdefault(s["id"], []).append({"origin": origin, "row_index": i, "url": s["url"]})
            by_url.setdefault(G.alias(s["url"]), []).append((origin, i, s))
    assert len(by_source_id) == 225 and len(by_url) == 202
    source_index = {"schema_version": 1, "candidate_ref": G.CANDIDATE,
                    "state": "HOLD_UNREVIEWED", "source_files": files,
                    "raw_source_rows": 244, "unique_source_ids": 225,
                    "literal_urls": 202, "by_source_id": by_source_id}
    write_json(d / "SOURCE_ID_ORIGIN_LOOKUP.json", source_index)
    groups = []
    for url, group in by_url.items():
        if len(group) < 2:
            continue
        groups.append({"url": url, "review_status": G.PENDING,
                       "reviewer": None, "reviewed_on": None,
                       "variants": [{"origin": o, "row_index": i, "source": s}
                                    for o, i, s in group]})
    assert len(groups) == 32
    slugs = [f"article-{i:02d}" for i in range(35)]
    tools = ["family-card", "power-planner"]
    slate = [{"slug": slug, "section": "start-here", "track": "modern", "gate": True}
             for slug in slugs]
    write_json(p / "taxonomy.json", {"slate": slate, "tools": [{"slug": s} for s in tools]})
    cross = {"groups": groups, "article_origins": {s: "base" for s in slugs}}
    write_json(p / "sources" / "crosswalk.json", cross)
    first_id = unique[0]["id"]
    old_records, entries = [], []
    for n, slug in enumerate(slugs):
        count = 58 if n < 5 else 57
        body = ("<section>" + ("A safe synthetic example.{{cite:" + first_id + "}}") * count
                + "{{link:family-card|free card}}</section>")
        meta = {"slug": slug, "status": {"publish": "draft"},
                "safety_review": {"state": "pending" if n < 29 else
                                   "approved" if n < 31 else "not-required"},
                "source_use": {first_id: "Synthetic first-party explanatory record."}}
        bp = p / "content" / "articles" / (slug + ".body.html")
        mp = p / "content" / "articles" / (slug + ".meta.json")
        bp.parent.mkdir(parents=True, exist_ok=True)
        bp.write_text(body, encoding="utf-8")
        write_json(mp, meta)
        bh, mh = G.blob_sha(bp.read_bytes()), G.blob_sha(mp.read_bytes())
        old_records.append({"slug": slug, "body": {"git_blob_sha": bh},
                            "metadata": {"git_blob_sha": mh}})
        entries.append({"slug": slug, "origin": "base", "section": "start-here",
                        "track": "modern", "body_sha": bh, "metadata_sha": mh,
                        "citation_occurrences": count, "lexically_visible_citations": count,
                        "unique_citation_ids": [first_id],
                        "author_explanation_ids": [first_id],
                        "estimated_text_words": count * 4, "status": "draft",
                        "safety_review": meta["safety_review"]["state"],
                        "compared_prior_body_sha": bh, "compared_prior_metadata_sha": mh,
                        "prior_body_same": True, "prior_meta_same": True,
                        "missing_source_ids": [], "missing_explanations": [],
                        "unused_explanations": [], "unresolved_scope_ids": [],
                        "broken_article_links": [], "invisible_token_count": 0})
    write_json(p / "sources" / "article-evidence-lock.json", {"records": old_records})
    t_sha = G.blob_sha((p / "taxonomy.json").read_bytes())
    x_sha = G.blob_sha((p / "sources" / "crosswalk.json").read_bytes())
    l_sha = G.blob_sha((p / "sources" / "article-evidence-lock.json").read_bytes())
    for offset in G.PARTS:
        write_json(d / f"CITATION_LEDGER_{offset:02d}.json",
                   {"schema_version": 1, "candidate_ref": G.CANDIDATE,
                    "release": "DRAFT_HOLD", "offset": offset,
                    "taxonomy_sha": t_sha, "crosswalk_sha": x_sha,
                    "prior_article_lock_sha": l_sha,
                    "entries": entries[offset:offset + 5]})
    return p


class TestSyntheticExactLedger(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="r133-isolated-")
        cls.root = Path(cls.temp.name)
        create_fixture(cls.root)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="r133-case-")
        self.case = Path(self.tmp.name)
        shutil.copytree(self.root / "preparedness", self.case / "preparedness")

    def tearDown(self):
        self.tmp.cleanup()

    def jsonpath(self, sub):
        return self.case / "preparedness" / sub

    def mutate_json(self, relpath, callback):
        fp = self.jsonpath(relpath)
        obj = G.load(fp)
        callback(obj)
        write_json(fp, obj)

    def test_valid_fixture_is_still_hold_not_qd(self):
        result = G.audit(self.case)
        self.assertEqual(result["state"], "HOLD")
        self.assertFalse(result["may_publish"])
        self.assertFalse(result["independent_QD_PASS"])
        self.assertEqual(result["raw_citations"], 2000)
        self.assertEqual(result["shared_source_groups_unreviewed"], 32)

    def test_blob_sha_distinguishes_bytes_and_git_header(self):
        self.assertNotEqual(G.blob_sha(b"hello"), hashlib.sha1(b"hello").hexdigest())
        self.assertNotEqual(G.blob_sha(b"hello"), G.blob_sha(b"hello\n"))

    def test_citation_parser_does_not_reinterpret_link(self):
        self.assertEqual(G.citations("{{link:x|y}} {{cite:src}}"), ["src"])
        self.assertEqual(G.link_targets("{{link:family-card|free card}}"), ["family-card"])

    def test_invisible_comment_citation_not_counted_as_lexically_visible(self):
        s = "visible {{cite:x}} <!-- {{cite:hidden}} -->"
        self.assertEqual(G.visible_lexical_citations(s), ["x"])

    def test_source_alias_preserves_query(self):
        self.assertNotEqual(G.alias("https://a.test/x/?a=1"), G.alias("https://a.test/x/?a=2"))
        self.assertEqual(G.alias("https://a.test/x/"), G.alias("https://a.test/x"))

    def test_duplicate_json_key_is_fail_closed(self):
        file = self.jsonpath("docs/r133/SOURCE_ID_ORIGIN_LOOKUP.json")
        file.write_text('{"candidate_ref":"A","candidate_ref":"B"}', encoding="utf-8")
        with self.assertRaisesRegex(G.IntegrityHold, "DUPLICATE_JSON_KEY"):
            G.audit(self.case)

    def test_source_record_edit_rejected(self):
        path = self.jsonpath("sources/register.json")
        obj = G.load(path)
        obj["sources"][0]["supports"] = "tampered reading-scope claim"
        write_json(path, obj)
        with self.assertRaisesRegex(G.IntegrityHold, "SOURCE_BLOB_DRIFT"):
            G.audit(self.case)

    def test_source_origin_index_edit_rejected(self):
        self.mutate_json("docs/r133/SOURCE_ID_ORIGIN_LOOKUP.json",
                         lambda obj: obj["by_source_id"]["source-000"][0].update(url="https://fake.example"))
        with self.assertRaisesRegex(G.IntegrityHold, "SOURCE_ORIGIN_LOOKUP_DRIFT"):
            G.audit(self.case)

    def test_crosswalk_approval_is_rejected(self):
        self.mutate_json("sources/crosswalk.json",
                         lambda obj: obj["groups"][0].update(review_status="approved"))
        with self.assertRaisesRegex(G.IntegrityHold, "UNAUTHORIZED_SOURCE_APPROVAL"):
            G.audit(self.case)

    def test_taxonomy_route_duplicate_rejected(self):
        self.mutate_json("taxonomy.json", lambda obj: obj["tools"].append({"slug":"article-00"}))
        with self.assertRaisesRegex(G.IntegrityHold, "DUPLICATE_ARTICLE_TOOL_ROUTE"):
            G.audit(self.case)

    def test_missing_source_variant_rejected(self):
        self.mutate_json("sources/crosswalk.json",lambda obj: obj["groups"][0]["variants"].pop())
        with self.assertRaisesRegex(G.IntegrityHold,"CROSSWALK_SOURCE_VARIANT_DRIFT"):
            G.audit(self.case)

    def test_missing_manifest_rejected(self):
        self.jsonpath("docs/r133/CITATION_LEDGER_15.json").unlink()
        with self.assertRaises(FileNotFoundError):
            G.audit(self.case)

    def test_illicit_release_flag_rejected(self):
        self.mutate_json("docs/r133/CITATION_LEDGER_00.json",
                         lambda obj: obj.update(release="APPROVED"))
        with self.assertRaisesRegex(G.IntegrityHold, "LEDGER_RELEASE_OR_ORDER_DRIFT"):
            G.audit(self.case)

    def test_unknown_source_citation_rejected(self):
        path = self.jsonpath("content/articles/article-00.body.html")
        path.write_text(path.read_text().replace("source-000", "unknown-id"), encoding="utf-8")
        with self.assertRaisesRegex(G.IntegrityHold, "ARTICLE_BLOB_DRIFT"):
            G.audit(self.case)

    def test_changed_safety_review_rejected(self):
        self.mutate_json("content/articles/article-00.meta.json",
                         lambda obj: obj["safety_review"].update(state="approved"))
        with self.assertRaisesRegex(G.IntegrityHold, "ARTICLE_BLOB_DRIFT"):
            G.audit(self.case)

    def test_missing_article_body_rejected(self):
        self.jsonpath("content/articles/article-00.body.html").unlink()
        with self.assertRaises(FileNotFoundError):
            G.audit(self.case)


# Each article file has an independent immutable Git-blob gate (35 actual tests).
# These are deliberate, reproducible one-byte mutations in an isolated copy.
for i in range(35):
    def generate(n):
        def test(self):
            slug = f"article-{n:02d}"
            path = self.jsonpath(f"content/articles/{slug}.body.html")
            path.write_bytes(path.read_bytes() + b"x")
            with self.assertRaisesRegex(G.IntegrityHold, "ARTICLE_BLOB_DRIFT:" + slug):
                G.audit(self.case)
        return test
    setattr(TestSyntheticExactLedger, f"test_{i:02d}_article_blob_mutation_rejected", generate(i))

if __name__ == "__main__":
    unittest.main()
