"""R132: author-scoped URL-alias regression tests. No external calls or source writes.

Run only in a trusted checkout: python -I -m unittest discover -s preparedness/tests -v
All tests are structural; no medical, food-safety or publishing approval.
"""
import copy
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build
import validate

JERKY = "https://nchfp.uga.edu/how/dry/recipes/jerky"


class AliasScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = build.Library()

    def test_35_draft_slate(self):
        self.assertEqual(len(self.lib.taxonomy["slate"]), 35)
        self.assertEqual(len(set(a["slug"] for a in self.lib.taxonomy["slate"])), 35)
        self.assertTrue(all(a["status"]["publish"] == "draft"
                            for a in self.lib.articles.values()))

    def test_source_rows_untouched(self):
        self.assertEqual(self.lib.crosswalk["raw_source_rows"], 244)
        self.assertEqual(self.lib.crosswalk["unique_source_urls"], 202)
        self.assertEqual(self.lib.crosswalk["duplicate_url_groups"], 32)

    def test_group_has_three_distinct_author_records(self):
        groups = [g for g in self.lib.crosswalk["groups"] if g["url"] == JERKY]
        self.assertEqual(len(groups), 1)
        g = groups[0]
        self.assertEqual({(x["origin"],x["source"]["id"]) for x in g["variants"]},
                         {("base","nchfp-jerky"),("food","nchfp-jerky"),
                          ("hist-food","hist-food-nchfp-jerky")})
        self.assertEqual(len(g["identities"]), 3)

    def test_author_scope_and_url_stay_independent(self):
        base = self.lib.source_variants["nchfp-jerky"][0]
        historic = self.lib.source_variants["hist-food-nchfp-jerky"][0]
        self.assertEqual(base["url"], JERKY)
        self.assertEqual(historic["url"], JERKY + "/")
        self.assertNotEqual(base.get("notes"), historic.get("notes"))
        self.assertNotEqual(base["id"], historic["id"])

    def test_conservative_alias_does_not_rewrite_literal_url(self):
        self.assertEqual(build.review_alias_key(JERKY),
                         build.review_alias_key(JERKY + "/"))
        self.assertNotEqual(JERKY, JERKY + "/")
        self.assertEqual(build.review_alias_key(JERKY + "/?x=1"),
                         JERKY + "?x=1")

    def test_alias_preserves_query(self):
        self.assertNotEqual(build.review_alias_key(JERKY + "/?x=1"),
                            build.review_alias_key(JERKY + "?x=2"))

    def test_alias_preserves_case(self):
        self.assertNotEqual(build.review_alias_key(JERKY.replace("jerky","JERKY")),
                            build.review_alias_key(JERKY))

    def test_each_author_has_unreviewed_group(self):
        g = next(x for x in self.lib.crosswalk["groups"] if x["url"] == JERKY)
        self.assertEqual(g["review_status"],
                         "pending-human-source-and-reading-scope-review")
        self.assertIsNone(g["reviewer"])
        self.assertIsNone(g["reviewed_on"])
        for origin, sid, url in (("base","nchfp-jerky",JERKY),
                                 ("food","nchfp-jerky",JERKY),
                                 ("hist-food","hist-food-nchfp-jerky",JERKY+"/")):
            self.assertIs(self.lib.crosswalk_member_groups[(origin,sid,url)],g)

    def test_historical_article_reading_scope(self):
        meta = self.lib.articles["pemmican-and-dried-meats"]
        source = self.lib.source_for(meta, "hist-food-nchfp-jerky")
        self.assertEqual(source["_origin"], "hist-food")
        self.assertEqual(source["url"], JERKY + "/")
        self.assertIn("full page", source["notes"])

    def test_historic_draft_source_block_warns(self):
        meta = self.lib.articles["pemmican-and-dried-meats"]
        block = build.sources_block(self.lib, ["hist-food-nchfp-jerky"], meta)
        self.assertIn("Shared-source reading scope: independent review pending", block)
        self.assertIn(JERKY + "/", block)

    def test_food_draft_source_block_warns(self):
        meta = self.lib.articles["safe-jerky-dehydration"]
        block = build.sources_block(self.lib, ["nchfp-jerky"], meta)
        self.assertIn("Shared-source reading scope: independent review pending", block)
        self.assertIn(JERKY, block)

    def test_draft_validate_has_no_crosswalk_mismatch(self):
        errors, _ = validate.validate(self.lib)
        self.assertFalse([s for s in errors if "source crosswalk mismatch" in s
                          or "duplicate url without source crosswalk" in s], errors)

    def test_approved_metadata_forgery_fails_publication(self):
        lib = build.Library()
        meta = lib.articles["pemmican-and-dried-meats"]
        meta["status"]["publish"] = "published"
        errors, _ = validate.validate(lib)
        self.assertTrue(any("CANNOT be published" in s for s in errors), errors)

    def test_distinct_historical_jerky_citation_is_not_retarged(self):
        meta = self.lib.articles["pemmican-and-dried-meats"]
        self.assertIn("{{cite:hist-food-nchfp-jerky}}", meta["_body"])
        self.assertNotIn("{{cite:nchfp-jerky}}", meta["_body"])


if __name__ == "__main__":
    unittest.main()
