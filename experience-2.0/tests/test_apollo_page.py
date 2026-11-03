"""The plugin-free Apollo 1 page block: static checks only (no browser, no network)."""
from __future__ import annotations

import hashlib
import json
import re
import unittest
from html.parser import HTMLParser

import support  # noqa: F401  (sets sys.path)
import fvx_lib as lib
import render_apollo_page as page

BLOCKS_DIR = lib.EX2 / "page-blocks"
MANIFEST = lib.EX2 / "page-blocks" / "manifest.json"
ATLAS = lib.EX2 / "atlas" / "data" / "atlas.json"


def _entry() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))["apollo1-investigation"]


def _block() -> str:
    """The whole page content, as stored: every committed block file in manifest order."""
    return page.NL.join((BLOCKS_DIR / b["file"]).read_text(encoding="utf-8") for b in _entry()["blocks"])


class _Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags, self.hrefs, self.srcs, self.ids, self.h = [], [], [], [], []
        self._in = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.tags.append(tag)
        if tag == "a" and "href" in a:
            self.hrefs.append(a["href"])
        if tag == "img":
            self.srcs.append(a.get("src"))
            self.srcs += [p.strip().split(" ")[0] for p in (a.get("srcset") or "").split(",") if p.strip()]
        if "id" in a:
            self.ids.append(a["id"])
        if tag in ("h1", "h2", "h3"):
            self.h.append(tag)


class Block(unittest.TestCase):
    def test_committed_block_is_current_and_deterministic(self):
        fresh = page.render_block()
        self.assertEqual(fresh, _block(), "page-blocks is stale: run tools/build_all.py")
        self.assertEqual(fresh, page.render_block())

    def test_manifest_matches_the_file_bytes(self):
        entry = _entry()
        for b in entry["blocks"]:
            raw = (BLOCKS_DIR / b["file"]).read_bytes()
            self.assertEqual({k: b[k] for k in ("bytes", "sha1", "sha256")},
                             {"bytes": len(raw), "sha1": hashlib.sha1(raw).hexdigest(), "sha256": hashlib.sha256(raw).hexdigest()}, b["file"])
            self.assertNotIn(bytes([13]), raw, "CR bytes would change the hash on a CRLF checkout")
        whole = _block().encode()
        self.assertEqual(entry["page_content"]["sha1"], hashlib.sha1(whole).hexdigest())
        self.assertEqual(entry["page_content"]["sha256"], hashlib.sha256(whole).hexdigest())

    def test_every_block_is_one_top_level_core_html_block(self):
        entry = _entry()
        self.assertEqual([b["order"] for b in entry["blocks"]], list(range(len(entry["blocks"]))))
        for b in entry["blocks"]:
            text = (BLOCKS_DIR / b["file"]).read_text(encoding="utf-8")
            self.assertTrue(text.startswith("<!-- wp:html -->\n") and text.endswith("\n<!-- /wp:html -->\n"), b["file"])
            self.assertEqual(text.count("<!--"), 2, f"{b['file']}: no other HTML comments")
            self.assertEqual(text.count("<!-- wp:html -->"), 1)
            self.assertLess(len(text.encode()), 40_000, f"{b['file']} should stay small enough to write and verify on its own")

    def test_no_plugin_and_no_unreviewed_runtime_dependencies(self):
        text = _block()
        for banned in ("innerHTML", "outerHTML", "insertAdjacentHTML", "document.write", "eval(", "new Function", "fetch(", "XMLHttpRequest",
                       "localStorage", "sessionStorage", "indexedDB", "navigator.sendBeacon", "import(", "[fv_ex2", "[fvx"):
            self.assertNotIn(banned, text, banned)
        self.assertEqual(len(re.findall(r"<script\b", text)), 1)
        self.assertNotRegex(text, r"<script[^>]+src=")
        self.assertNotRegex(text, r"<link\b")
        self.assertNotRegex(text, r"@import|url\(")
        self.assertNotIn("</script", text.split("<script>", 1)[1].rsplit("</script>", 1)[0].lower())
        self.assertNotIn("data-fvx-drawer", re.search(r"<style>(.*?)</style>", text, re.S).group(1))
        self.assertNotIn("[data-fvx-drawer]", re.search(r"<style>(.*?)</style>", text, re.S).group(1), "unused drawer CSS should not ship")

    def test_css_is_namespaced(self):
        css = re.search(r"<style>(.*?)</style>", _block(), re.S).group(1)
        css = re.sub(r"@keyframes [^{]+\{(?:[^{}]*\{[^{}]*\})+\}", "", css)
        css = re.sub(r"@media[^{]*\{", "", css)
        for selector_group in re.findall(r"(?:^|\})([^{}@]+)\{", css):
            for sel in selector_group.split(","):
                self.assertTrue(sel.strip().startswith((".fv-ex2", ":where(.fv-ex2", "html.fv-ex2-")), sel)
        self.assertNotRegex(css, r"(?<![-\w])--(?!fvx-)[a-z]")

    def test_structure(self):
        t = _Tags()
        t.feed(_block())
        self.assertEqual(t.h.count("h1"), 1)
        self.assertNotIn("main", t.tags, "the theme owns <main>")
        self.assertNotIn("dialog", t.tags)
        self.assertEqual(len(t.ids), len(set(t.ids)), "duplicate ids")
        for href in t.hrefs:
            if href.startswith("#"):
                self.assertIn(href[1:], t.ids, href)
            else:
                lib.safe_https(href)
        for src in t.srcs:
            lib.safe_https(src, lib.IMAGE_HOSTS)

    def test_no_hero_photograph_and_no_staging_language(self):
        text = _block()
        self.assertNotIn('class="fv-ex2-hero__media"', text, "the hero photograph was the measured mobile LCP element")
        for phrase in ("Integration candidate", "Not published", "not published", "FVSL-QD-PASS", "approved by"):
            self.assertNotIn(phrase, text, phrase)

    def test_every_image_is_a_record_image_with_its_rights_row(self):
        data = lib.load_apollo1()
        text = _block()
        for rec in data["records"]:
            img = rec["image"]
            self.assertIn(img["src"], text)
            self.assertIn(f'id="rights-{rec["id"]}"', text)
            self.assertIn(img["record_url"], text)
            self.assertIn(img["credit"], text)
        self.assertIn(data["rights_policy"]["restriction"], text)

    def test_classification_matches_the_atlas_relationships(self):
        atlas = json.loads(ATLAS.read_text(encoding="utf-8"))
        rels = [r for r in atlas["relationships"] if r["object"] == "evt-apollo1-fire"]
        text = _block()
        body = text.split("</style>", 1)[1]
        documented = sum(1 for r in rels if r["basis"] == "documented")
        # legend + the one documented photograph's plate + the classification list (the Board report has no plate)
        self.assertEqual(body.count('data-status="documented"'), 1 + 1 + documented)
        for r in rels:
            self.assertIn(r["justification"].replace("'", "&#x27;"), text)
        self.assertEqual(sum(1 for r in rels if r["basis"] == "documented"), 2)

    def test_related_posts_are_atlas_investigations_sharing_a_theme(self):
        atlas = json.loads(ATLAS.read_text(encoding="utf-8"))
        mine = next(i for i in atlas["investigations"] if i["wordpress_post_id"] == 434)
        t = _Tags()
        t.feed(_block())
        for other in atlas["investigations"]:
            shared = set(other["themes"]) & set(mine["themes"])
            linked = other["url"] in t.hrefs
            if other is mine:
                continue
            self.assertEqual(linked, bool(shared), other["title"])

    def test_the_page_does_not_overstate_review(self):
        text = _block()
        self.assertIn("Not yet reviewed", text)
        self.assertIn("human rights review pending", text)
        self.assertNotIn("independent review", text.lower())

    def test_size_budget(self):
        self.assertLess(len(_block().encode()), 110_000)

    def test_rejects_an_unsafe_dataset(self):
        data = json.loads((lib.DATA / "apollo1.json").read_text(encoding="utf-8"))
        data["records"][0]["image"]["src"] = "https://evil.example/a.jpg"
        with self.assertRaises(lib.BadRecord):
            page.render_block(data)


if __name__ == "__main__":
    unittest.main()
