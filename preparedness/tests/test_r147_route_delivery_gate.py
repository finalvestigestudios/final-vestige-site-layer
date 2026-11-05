"""R147 adversarial synthetic fixtures only; no authentic native suite claim."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

source = Path(__file__).resolve().parents[1] / "tools/r147_route_delivery_gate.py"
spec = importlib.util.spec_from_file_location("r147", source)
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


class RouteGate(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.sections = ["start-here", "water", "food", "shelter-power", "health-sanitation",
                         "family-communication", "lost-ways", "field-tools"]
        self.slugs = [f"guide-{i:02d}" for i in range(35)]
        self.paths = {}
        tax = {"base_path": "/preparedness/", "sections": [{"slug": x} for x in self.sections],
               "slate": [{"slug": x, "section": self.sections[i % 7]}
                         for i, x in enumerate(self.slugs)],
               "tools": [{"slug": "contact-card"}]}
        self.save(self.root / "taxonomy.json", tax)
        for i, slug in enumerate(self.slugs):
            self.article("articles", slug, self.sections[i % 7])
        self.article("tools", "contact-card", "field-tools")
        built = []
        for (kind, slug), path in self.paths.items():
            meta = json.loads(path.read_text())
            built.append({"slug": slug, "canonical":
                          f"https://finalvestige.com/preparedness/{meta['section']}/{slug}/"})
        self.report = {"articles": built,
                       "hubs": [{"section": x} for x in self.sections],
                       "release_evidence": {"state": "HOLD", "article_drafts": 36,
                                            "article_published": 0,
                                            "wordpress_publication_performed": False,
                                            "independent_qa_verified": False}}
        self.save(self.root / "build/build-report.json", self.report)
        for name in ["landing"] + self.sections + self.slugs + ["contact-card"]:
            for dest in ["wp", "preview"]:
                p = self.root / "build" / dest / (name + ".html")
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text("<p>Local-only draft</p>")

    @staticmethod
    def save(path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value))

    def article(self, kind, slug, section):
        p = self.root / "content" / kind / (slug + ".meta.json")
        self.save(p, {"slug": slug, "section": section, "status": {"publish": "draft"},
                      "safety_review": {"state": "pending"},
                      "source_use": {"source-a": "Original author scope retained"}})
        p.with_name(slug + ".body.html").write_text("<p>{{cite:source-a}}</p>")
        self.paths[(kind, slug)] = p

    def inspect(self, **kwargs):
        return r.inspect(self.root, **({"expected_citations": 35, "expected_tools": 1} | kwargs))

    def hold(self, message, **kwargs):
        with self.assertRaises(r.Hold) as caught:
            self.inspect(**kwargs)
        self.assertIn(message, str(caught.exception))

    def test_baseline(self):
        result = self.inspect()
        self.assertEqual(result["unique_draft_routes"], 45)
        self.assertEqual(result["article_citation_occurrences"], 35)
        self.assertFalse(result["publication_allowed"])
        self.assertEqual(result["independent_qd"], "NOT_APPROVED")

    def test_no_build_is_explicit(self):
        self.assertEqual(self.inspect(require_build=False)["build"], "NOT_EXECUTED")

    def test_citation_baseline_hold(self):
        self.hold("citation baseline mismatch", expected_citations=2000)

    def test_missing_build_report(self):
        (self.root / "build/build-report.json").unlink()
        self.hold("missing/linked")

    def test_missing_draft_artifact(self):
        (self.root / "build/wp/landing.html").unlink()
        self.hold("missing/linked")

    def test_build_canonical_drift(self):
        self.report["articles"][0]["canonical"] = "https://finalvestige.com/preparedness/water/other/"
        self.save(self.root / "build/build-report.json", self.report)
        self.hold("canonical differs")

    def test_build_forged_approval(self):
        self.report["release_evidence"]["independent_qa_verified"] = True
        self.save(self.root / "build/build-report.json", self.report)
        self.hold("approval contradiction")

    def test_build_duplicate_slug(self):
        self.report["articles"][1]["slug"] = self.report["articles"][0]["slug"]
        self.save(self.root / "build/build-report.json", self.report)
        self.hold("duplicate build")

    def test_wordpress_existing_url_collision(self):
        p = self.root / "wp.json"
        self.save(p, {"urls": ["/preparedness/start-here/guide-00/"]})
        self.hold("route collision requires", wp_inventory=p)

    def test_clean_external_snapshot_cannot_grant_approval(self):
        p = self.root / "wp.json"
        self.save(p, {"urls": ["/preparedness/unrelated/"]})
        outcome = self.inspect(wp_inventory=p)
        self.assertIn("UNVERIFIED_SNAPSHOT", outcome["external_wp"])
        self.assertFalse(outcome["publication_allowed"])

    def test_existing_url_case_alias(self):
        p = self.root / "wp.json"
        self.save(p, {"urls": ["/PREPAREDNESS/START-HERE/GUIDE-00"]})
        self.hold("route collision requires", wp_inventory=p)

    def test_missing_source_scope(self):
        path = self.paths[("articles", self.slugs[0])]
        obj = json.loads(path.read_text()); obj["source_use"] = {}
        self.save(path, obj)
        self.hold("author-specific citation")

    def test_missing_original_tool(self):
        self.paths[("tools", "contact-card")].unlink()
        self.hold("expected 1 metadata")

    def test_invalid_route(self):
        for url in ("/focus/", "/preparedness/%252e%252e/", "/preparedness/a/?x=1",
                    "http://finalvestige.com/preparedness/a/", "https://evil.example/preparedness/a/",
                    "/preparedness//a/", "/preparedness/a/b/c/", "/preparedness/a\\b/"):
            with self.subTest(url=url), self.assertRaises(r.Hold):
                r.route_key(url)


# Distinct mutation for each of the 35 authentic article slots; failures must be local.
def add_loss(slot, field):
    def check(self):
        slug = self.slugs[slot]
        if field == "cite":
            (self.root / "content/articles" / (slug + ".body.html")).write_text("<p>lost reference</p>")
            self.hold("author-specific citation")
        else:
            path = self.paths[("articles", slug)]
            data = json.loads(path.read_text())
            data["status"]["publish"] = "published"
            self.save(path, data)
            self.hold("publication state")
    return check


for i in range(35):
    setattr(RouteGate, f"test_slot_{i:02d}_citation_removed", add_loss(i, "cite"))
    setattr(RouteGate, f"test_slot_{i:02d}_unauthorized_publication", add_loss(i, "publish"))

if __name__ == "__main__":
    unittest.main()
