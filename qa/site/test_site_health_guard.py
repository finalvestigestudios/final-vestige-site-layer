"""Regression coverage for the offline WordPress site-health guard."""
from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from site_health_guard import check, main, nav_links, route


def link(label: str, target: str) -> str:
    return '<!-- wp:navigation-link ' + json.dumps({"label": label, "url": target},
                                                   separators=(",", ":")) + ' /-->'


def fixture() -> dict:
    return {
        "hostname": "finalvestige.com",
        "expected_brand": "Final Vestige Studios",
        "settings": {
            "site_info": {"is_private": False},
            "reading": {"blog_public": 1},
            "general": {"blogname": "Final Vestige Studios"},
            "identity": {"site_icon": 42, "site_logo": 42}
        },
        "content": [
            {"id": 6, "status": "publish", "published_url": "https://finalvestige.com/"},
            {"id": 1579, "status": "publish", "published_url": "https://finalvestige.com/focus/"},
            {"id": 523, "status": "publish", "published_url": "https://finalvestige.com/dispatch/"},
            {"id": 77, "status": "publish", "published_url": "https://finalvestige.com/free-resources/"},
            {"id": 85, "status": "draft", "intended_url": "https://finalvestige.com/collection/water-resilience-field-manual/"}
        ],
        "navigation_markup": "\n".join([
            link("Home", "https://finalvestige.com/"),
            link("Focus", "https://finalvestige.com/focus/"),
            link("Dispatch", "https://finalvestige.com/dispatch/"),
        ]),
        "plugins": [
            {"name": "Final Vestige Site Layer", "status": "active", "update_available": False}
        ],
        "dynamic_prefixes": ["/portal"],
        "review_plugin_names": []
    }


class SiteHealthGuardTests(unittest.TestCase):
    def test_healthy_baseline(self):
        result = check(fixture())
        self.assertEqual(result["findings"], [])
        self.assertEqual(result["active_plugins"], 1)

    def test_draft_navigation_link_is_p1(self):
        s = fixture()
        s["navigation_markup"] += "\n" + link("Old guide", "/collection/water-resilience-field-manual/")
        self.assertIn("navigation-unpublished", [x["code"] for x in check(s)["findings"]])

    def test_internal_unknown_is_unverified_not_broken(self):
        s = fixture()
        s["navigation_markup"] += "\n" + link("Mystery", "/path-not-in-wp/")
        f = check(s)["findings"]
        self.assertEqual(len(f), 1)
        self.assertEqual(f[0]["severity"], "REVIEW")
        self.assertEqual(f[0]["code"], "navigation-not-in-inventory")

    def test_dynamic_routes_not_false_positive(self):
        s = fixture()
        s["navigation_markup"] += "\n" + link("Portal", "/portal/discover/spaces")
        self.assertEqual(check(s)["findings"], [])

    def test_critical_focus_route_p1(self):
        s = fixture()
        s["content"][1]["status"] = "draft"
        self.assertIn("critical-route-not-published-in-snapshot",
                      [x["code"] for x in check(s)["findings"]])

    def test_missing_focus_nav_p1(self):
        s = fixture()
        s["navigation_markup"] = link("Home", "/")
        self.assertIn("focus-navigation-missing", [x["code"] for x in check(s)["findings"]])

    def test_pending_plugin_update_review_only(self):
        s = fixture()
        s["plugins"].append({"name": "Site Kit", "status": "active",
                             "version": "1.1", "new_version": "1.2", "update_available": True})
        issues = check(s)["findings"]
        self.assertEqual(issues[0]["code"], "plugin-update-available")
        self.assertEqual(issues[0]["severity"], "REVIEW")

    def test_inactive_plugin_ignored(self):
        s = fixture()
        s["plugins"].append({"name": "Temporary Probe", "status": "inactive",
                             "update_available": True})
        self.assertEqual(check(s)["findings"], [])

    def test_one_shot_plugin_needs_review_not_shutdown(self):
        s = fixture()
        s["plugins"].append({"name": "History Lab LIVEPASS One-Shot Controller",
                             "status": "active", "update_available": False})
        self.assertIn("temporary-sounding-active-plugin",
                      [x["code"] for x in check(s)["findings"]])

    def test_private_site_p0(self):
        s = fixture()
        s["settings"]["reading"]["blog_public"] = 0
        self.assertIn("search-visibility-private", [x["code"] for x in check(s)["findings"]])

    def test_branding_warnings_not_release_failure(self):
        s = fixture()
        s["settings"]["identity"] = {"site_logo": 0, "site_icon": 0}
        s["settings"]["general"]["blogname"] = "FINAL VESTIGE"
        result = check(s)
        self.assertEqual(set(x["code"] for x in result["findings"]),
                         {"site-icon-unset", "site-logo-unset", "site-name-brand-mismatch"})
        self.assertTrue(all(x["severity"] == "REVIEW" for x in result["findings"]))

    def test_same_site_normalization(self):
        self.assertEqual(route("https://www.finalvestige.com/focus/?subscribe=1#foo"), "/focus")
        self.assertIsNone(route("https://elsewhere.com/focus/"))
        self.assertIsNone(route("mailto:hello@example.com"))
        self.assertEqual(route("/"), "/")

    def test_valid_navigation_parser(self):
        self.assertEqual(len(nav_links(link("Focus", "/focus/"))), 1)
        self.assertEqual(nav_links("<!-- wp:navigation-link {broken} /-->"), [])

    def test_cli_does_not_write_snapshot(self):
        s = fixture()
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "snapshot.json"
            initial = json.dumps(s)
            path.write_text(initial, encoding="utf-8")
            self.assertEqual(main([str(path), "--strict"]), 0)
            self.assertEqual(path.read_text(encoding="utf-8"), initial)

    def test_strict_blocks_only_actual_priority(self):
        s = fixture()
        s["plugins"].append({"name": "Some Probe", "status": "active"})
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "snapshot.json"
            path.write_text(json.dumps(s), encoding="utf-8")
            self.assertEqual(main([str(path), "--strict"]), 0)
            s["navigation_markup"] = link("Home", "/")
            path.write_text(json.dumps(s), encoding="utf-8")
            self.assertEqual(main([str(path), "--strict"]), 1)


if __name__ == "__main__":
    unittest.main()
