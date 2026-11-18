"""Isolated adversarial tests. NO actual release, WordPress or user data."""
from __future__ import annotations
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "tools" / "r459_full_draft_surface_custody.py"
SPEC = importlib.util.spec_from_file_location("r459_gate", SOURCE)
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class FakeLibrary:
    def __init__(self, root):
        self.root = root
        self.articles = {}
        for i in range(35):
            slug = f"guide-{i:02d}"
            self.articles[slug] = {"slug": slug, "h1": f"How to plan guide {i}",
                                   "description": f"Official sources for guide {i}",
                                   "section": "start" if i % 2 else "food",
                                   "status": {"publish": "draft"}}
        self.taxonomy = {"sections": [{"slug": "food"}, {"slug": "start"}]}

    def url_path(self, slug):
        return "/preparedness/" + self.articles[slug]["section"] + "/" + slug + "/"


class FakeBuilder:
    @staticmethod
    def build_article(lib, slug):
        return {"slug": slug, "meta": lib.articles[slug],
                "inner": f'<div class="pa pa-article" data-slug="{slug}"><h1>{slug}</h1>'
                         '<div class="pa-body">Emergency caveat. Consult current official guidance.</div>'
                         '<section class="pa-sources">Source: Official organization</section>'
                         '<aside class="pa-review">Draft; independent QD pending</aside></div>',
                "words": 14, "minutes": 2, "sources": ["official-src"],
                "canonical": "https://finalvestige.com" + lib.url_path(slug)}

    @staticmethod
    def build_hub(lib, section, include_drafts=True):
        assert include_drafts
        count = sum(a["section"] == section for a in lib.articles.values())
        return {"slug": "hub-" + section, "count": count, "title": "Hub " + section,
                "description": "Free verified guides awaiting review", "inner": "<div>Hub " + section + "</div>"}

    @staticmethod
    def build_landing(lib, include_drafts=True):
        assert include_drafts
        return {"slug": "landing", "article_cards": len(lib.articles),
                "populated_sections": ["food", "start"],
                "inner": "<div>Free public agency resources; draft human review pending</div>"}

    @staticmethod
    def wp_wrap(lib, inner):
        return "<!-- wp:html -->\n<style>.pa{display:block}</style>\n" + inner + "\n<!-- /wp:html -->\n"

    @staticmethod
    def preview_wrap(lib, inner, title, description):
        return '<!doctype html><html><head><meta name="robots" content="noindex,nofollow"><title>' + title + \
               '</title><meta name="description" content="' + description + '"></head><body>' + \
               inner + '</body></html>'


class R459Test(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "preparedness"
        (self.root / "build" / "wp").mkdir(parents=True)
        (self.root / "build" / "preview").mkdir(parents=True)
        self.lib = FakeLibrary(self.root)
        self.build = FakeBuilder()
        self.prior = {"release_state": mod.STATE, "qualified_qd_pass": False,
                      "entries": [{"slug": s} for s in self.lib.articles]}
        art_rows = []
        for slug, meta in self.lib.articles.items():
            build = self.build.build_article(self.lib, slug)
            art_rows.append({k: build[k] for k in ("slug", "words", "minutes", "sources", "canonical")})
            for folder, rendered in (("wp", self.build.wp_wrap(self.lib, build["inner"])),
                                     ("preview", self.build.preview_wrap(self.lib, build["inner"],
                                          meta["h1"] + " | The Preparedness Archive", meta["description"]))):
                (self.root / "build" / folder / (slug + ".html")).write_bytes(rendered.encode())
        hubs = []
        for section in ("food", "start"):
            h = self.build.build_hub(self.lib, section)
            hubs.append({"section": section, "guides": h["count"]})
            self.put(h["slug"], h["inner"], h["title"], h["description"])
        l = self.build.build_landing(self.lib)
        self.put("landing", l["inner"], "The Preparedness Archive | Final Vestige",
                 "Evidence-based household preparedness and a historical record of how earlier generations managed without modern infrastructure.")
        self.report = {"articles": art_rows, "hubs": hubs,
                       "landing": {"populated_sections": l["populated_sections"], "article_cards": l["article_cards"]},
                       "release_evidence": {"state": "HOLD", "independent_qa_verified": False,
                                            "wordpress_publication_performed": False}}
        self.save_report()

    def put(self, slug, inner, title, description):
        (self.root / "build" / "wp" / (slug + ".html")).write_bytes(self.build.wp_wrap(self.lib, inner).encode())
        (self.root / "build" / "preview" / (slug + ".html")).write_bytes(
            self.build.preview_wrap(self.lib, inner, title, description).encode())

    def save_report(self):
        (self.root / "build" / "build-report.json").write_text(json.dumps(self.report), encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def run_gate(self):
        return mod.audit_surfaces(self.root, self.lib, self.build, prior=self.prior)

    def assert_hold(self):
        with self.assertRaises(mod.SurfaceHold):
            self.run_gate()

    def test_positive_exact_full_slate(self):
        receipt = self.run_gate()
        self.assertEqual(receipt["draft_export_count"], 76)
        self.assertEqual(receipt["article_and_tool_count"], 35)
        self.assertEqual(receipt["hub_count"], 2)
        self.assertFalse(receipt["qualified_qd_pass"])
        self.assertFalse(receipt["wordpress_publication_performed"])
        self.assertFalse(receipt["source_claim_support_verified"])
        self.assertEqual(len({(e["slug"], e["surface"]) for e in receipt["entries"]}), 76)

    def test_git_blob_uses_canonical_git_algorithm(self):
        self.assertEqual(mod.git_blob(b"hello\n"), hashlib.sha1(b"blob 6\0hello\n").hexdigest())

    def test_missing_checkout_does_not_pass(self):
        with self.assertRaises(mod.SurfaceHold):
            mod.verify_native(self.root)

    def test_unreviewed_builder_blob_rejected(self):
        p = self.root / "build" / "random.py"
        p.write_text("pass", encoding="utf-8")
        with self.assertRaises(mod.SurfaceHold):
            mod.pinned_asset(p, mod.BUILDER_BLOB, "builder")

    def test_invalid_previous_receipt_variants(self):
        for alteration in [None, {}, {"release_state": "PASS", "qualified_qd_pass": False},
                           {"release_state": mod.STATE, "qualified_qd_pass": True}]:
            with self.subTest(alteration=alteration):
                current = self.prior
                self.prior = alteration
                self.assert_hold()
                self.prior = current

    def test_report_flags_fail_closed(self):
        for key, value in [("state", "APPROVED"), ("state", "REQUIRES_INDEPENDENT_QA"),
                           ("independent_qa_verified", True), ("independent_qa_verified", None),
                           ("wordpress_publication_performed", True)]:
            with self.subTest(key=key, value=value):
                self.report["release_evidence"][key] = value
                self.save_report()
                self.assert_hold()
                self.report["release_evidence"][key] = "HOLD" if key == "state" else False
                self.save_report()

    def test_duplicate_missing_extra_report_rows(self):
        old = copy.deepcopy(self.report["articles"])
        mutations = [old[:-1], old + [old[0]], old[:-1] + [old[0]],
                     [{**r, "sources": ["retargeted"]} if i == 0 else r for i, r in enumerate(old)],
                     [{**r, "canonical": "https://bad.test/offer"} if i == 0 else r for i, r in enumerate(old)],
                     [{**r, "words": 1} if i == 0 else r for i, r in enumerate(old)],
                     [{**r, "minutes": 0} if i == 0 else r for i, r in enumerate(old)]]
        for rows in mutations:
            with self.subTest(rows=len(rows), first=rows[0]):
                self.report["articles"] = rows
                self.save_report()
                self.assert_hold()
        self.report["articles"] = old
        self.save_report()

    def test_altered_hub_landing_fails(self):
        old_h = copy.deepcopy(self.report["hubs"])
        old_l = copy.deepcopy(self.report["landing"])
        for bad in [[{"section": "food", "guides": 10}], old_h[::-1], old_h + old_h[:1]]:
            self.report["hubs"] = bad
            self.save_report()
            self.assert_hold()
        self.report["hubs"] = old_h
        self.report["landing"]["article_cards"] = 0
        self.save_report()
        self.assert_hold()
        self.report["landing"] = old_l
        self.save_report()

    def test_invalid_status_or_identity_fails(self):
        slug = "guide-00"
        for status in ("published", "approved", None):
            self.lib.articles[slug]["status"]["publish"] = status
            self.assert_hold()
        self.lib.articles[slug]["status"]["publish"] = "draft"
        self.prior["entries"][0]["slug"] = "guide-01"
        self.assert_hold()

    def test_stale_artifact_in_wp_or_preview_fails(self):
        for surface in ("wp", "preview"):
            p = self.root / "build" / surface / "stale-previous-release.html"
            p.write_text("<a href='https://payhip.com/b/unapproved'>PAY</a>")
            self.assert_hold()
            p.unlink()

    def test_missing_export_any_surface_fails(self):
        for surface in ("wp", "preview"):
            p = self.root / "build" / surface / "guide-07.html"
            original = p.read_bytes()
            p.unlink()
            self.assert_hold()
            p.write_bytes(original)

    def test_export_symlink_rejected(self):
        p = self.root / "build" / "wp" / "guide-00.html"
        payload = p.read_bytes()
        p.unlink()
        p.symlink_to(self.root / "build" / "preview" / "guide-00.html")
        self.assert_hold()
        p.unlink()
        p.write_bytes(payload)

    def test_changed_publisher_metadata_does_not_pass(self):
        meta = self.lib.articles["guide-01"]
        meta["description"] = "Unverified new medical safety promise"
        self.assert_hold()

    def test_unsafe_artifact_name_rejected(self):
        for x in ("../foo", "Foo", "foo.html", "foo_bar", "", "pay/checkout"):
            with self.subTest(x=x):
                with self.assertRaises(mod.SurfaceHold):
                    mod.checked_name(x)

    def _mutate_one_export(self, name, surface):
        path = self.root / "build" / surface / (name + ".html")
        original = path.read_bytes()
        path.write_bytes(original + b'<aside class="offer">Buy our unverified emergency kit</aside>')
        self.assert_hold()
        path.write_bytes(original)

    def test_mutate_each_article_and_index_surface(self):
        # 35 original articles + hub(s) + landing; independent WP and preview alterations
        for name in [*self.lib.articles, "hub-food", "hub-start", "landing"]:
            for surface in ("wp", "preview"):
                with self.subTest(slug=name, surface=surface):
                    self._mutate_one_export(name, surface)

    def test_targeted_deceptive_render_mutations(self):
        # Attacks deliberately occur outside the authored body (R458's primary scope).
        needle_pairs = [
            (b'Draft; independent QD pending', b'Independently safety approved!'),
            (b'Source: Official organization', b'Source: AI has verified all advice'),
            (b'Skip to the guide', b'Join and pay to get emergency guidance'),
            (b'Sources', b'Paid product'),
            (b'Emergency caveat.', b'All medications are safe.'),
            (b'<style>.pa{display:block}</style>', b'<style>.pa-sources{display:none}</style>'),
            (b'<!-- /wp:html -->', b'<!-- /wp:html --><script src="https://bad.test/tracker.js"></script>'),
        ]
        p = self.root / "build" / "wp" / "guide-00.html"
        original = p.read_bytes()
        for old, new in needle_pairs:
            if old in original:
                p.write_bytes(original.replace(old, new, 1))
                self.assert_hold()
                p.write_bytes(original)

    def test_no_unapproved_legacy_freebie_or_paid_label(self):
        # A paywall/CTA inserted outside the article body is not invisible to R459.
        for payload in ("<a href='/old-water-guide/'>Retired freebie</a>",
                        "<div>Buy now for urgent household safety advice</div>",
                        "<form action='https://merchant.test/pay'>Checkout</form>",
                        "<meta name='robots' content='index,follow'>"):
            p = self.root / "build" / "preview" / "landing.html"
            old = p.read_bytes()
            p.write_bytes(old.replace(b'</head>', payload.encode() + b'</head>'))
            self.assert_hold()
            p.write_bytes(old)

    def test_preview_robots_disclosure_mutation(self):
        p = self.root / "build" / "preview" / "guide-11.html"
        original = p.read_bytes()
        self.assertIn(b'noindex,nofollow', original)
        p.write_bytes(original.replace(b'noindex,nofollow', b'index,follow'))
        self.assert_hold()
        p.write_bytes(original)


# Each export mutation has its own named, independently counted adversarial test.
# The 35 original article IDs are simulated; authentic source checks are separate.
for _surface in ("wp", "preview"):
    for _i in range(35):
        _slug = f"guide-{_i:02d}"
        def _factory(slug=_slug, surface=_surface):
            def _test(self):
                self._mutate_one_export(slug, surface)
            return _test
        setattr(R459Test, f"test_individual_tamper_{_surface}_{_i:02d}", _factory())

if __name__ == "__main__":
    unittest.main()
