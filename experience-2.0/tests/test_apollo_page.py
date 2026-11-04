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

    def test_no_photograph_without_a_named_editor_signoff(self):
        """Founder rule: an image with no sign-off is omitted and the text-and-document page stands without it."""
        data = lib.load_apollo1()
        approved = page.approved_images(data)
        timeline_approved = page.approved_timeline_images(data)
        text = _block()
        for rec in data["records"]:
            img = rec["image"]
            shown = img["nasa_id"] in approved
            self.assertEqual(img["src"] in text, shown, img["nasa_id"])
            self.assertIn(f'id="rights-{rec["id"]}"', text)
            self.assertIn(img["record_url"], text)
        if not approved and not timeline_approved:
            self.assertNotIn("<img", text)
            self.assertIn("Photographs not shown in this release", text)
        self.assertIn(data["rights_policy"]["restriction"], text)

    def test_chronology_archival_views_are_approved_and_context_only(self):
        data = lib.load_apollo1()
        ids = page.approved_timeline_images(data)
        self.assertEqual(ids, {"S66-58038", "S67-15717", "KSC-20170124-PH_KLS01_0129"})
        markup = _block()
        self.assertEqual(markup.count('data-fvx-chrono-photo='), 3)
        self.assertEqual(markup.count('class="fvx-chrono-gallery__image"'), 3)
        self.assertIn("The photographs below show separate historical contexts", markup)
        self.assertIn("These photographs do not depict the marked seconds", markup)
        self.assertIn("Image provenance and editorial use", markup)

    def test_signoff_rules(self):
        import tempfile, pathlib
        data = lib.load_apollo1()
        nid = data["records"][1]["image"]["nasa_id"]
        def run(items):
            with tempfile.TemporaryDirectory() as d:
                p = pathlib.Path(d) / "s.json"
                p.write_text(json.dumps({"approved": items}), encoding="utf-8")
                return page.approved_images(data, p)
        self.assertEqual(run([]), set())
        self.assertEqual(run([{"nasa_id": nid}]), set(), "no editor, date or use: not approved")
        self.assertEqual(run([{"nasa_id": nid, "editor": "A. Editor", "date": "2026-11-03", "contextual_use": " "}]), set())
        self.assertEqual(run([{"nasa_id": "NOT-A-RECORD", "editor": "A", "date": "d", "contextual_use": "u"}]), set())
        self.assertEqual(run([{"nasa_id": nid, "editor": "A. Editor", "date": "2026-11-03", "contextual_use": "Context plate, chapter 2"}]), {nid})

    def test_an_approved_photograph_renders_its_plate_and_rights_row(self):
        import tempfile, pathlib
        data = lib.load_apollo1()
        atlas = json.loads(ATLAS.read_text(encoding="utf-8"))
        nid = data["records"][4]["image"]["nasa_id"]
        orig = page.SIGNOFFS
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "s.json"
            p.write_text(json.dumps({"approved": [{"nasa_id": nid, "editor": "A. Editor", "date": "2026-11-03", "contextual_use": "Plate 5"}]}), encoding="utf-8")
            page.SIGNOFFS = p
            try:
                import fvx_lib
                original = page.approved_images
                page.approved_images = lambda data, path=p: original(data, path)
                blocks = dict(page.render_blocks(data, atlas))
            finally:
                page.approved_images = original
                page.SIGNOFFS = orig
        self.assertIn(data["records"][4]["image"]["src"], blocks["01-investigation"])
        self.assertEqual(blocks["01-investigation"].count("<img"), 1)
        self.assertIn("Documented", blocks["02-classification"])
        self.assertIn("S67-21294 is documented", blocks["02-classification"].replace("photograph, S67-21294,", "S67-21294"))

    def test_no_internal_notes_reach_visitors(self):
        text = _block()
        for phrase in ("Sprint 5", "not re-checked", "Not re-checked", "confirm before publication", "Confirm before publication", "confirm wording",
                       "Confirm wording", "candidate", "human rights review pending", "integration candidate", "Fourteen seconds", "fourteen seconds",
                       "prototype", "was not found through the NASA Image API"):
            self.assertNotIn(phrase, text, phrase)
        self.assertIn("About fifteen seconds changed the system.", text)
        self.assertIn("approximately 15 seconds after the verbal report", text)

    def test_every_claim_names_its_nasa_source(self):
        data = lib.load_apollo1()
        ids = {s["id"] for s in data.get("claim_sources", [])} | {"src-nasa-board-report"}
        for rec in data["records"]:
            for row in rec["crosswalk"]:
                self.assertEqual(row["status"], "verified", f'{rec["id"]}: {row["claim"]}: ship only claims matched to a NASA source, or remove them')
                self.assertTrue(row.get("url", "").startswith("https://www.nasa.gov/"), row["claim"])
                self.assertTrue(row.get("source_ids") and set(row["source_ids"]) <= ids, row["claim"])

    def test_classification_matches_the_atlas_relationships(self):
        atlas = json.loads(ATLAS.read_text(encoding="utf-8"))
        rels = [r for r in atlas["relationships"] if r["object"] == "evt-apollo1-fire"]
        docs = {d["id"]: d for d in atlas["documents"]}
        approved = page.approved_images(lib.load_apollo1())
        listed = [r for r in rels if docs[r["subject"]]["document_type"] != "photograph" or docs[r["subject"]]["archive_id"] in approved]
        body = _block().split("</style>", 1)[1]
        for r in listed:
            self.assertIn(r["justification"].replace("'", "&#x27;"), body)
        for r in rels:
            if r not in listed:
                self.assertNotIn(r["justification"].replace("'", "&#x27;"), body, "a photograph that is not shown must not be classified on the page")

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
        self.assertNotIn("independent review", text.lower())

    def test_unverified_claims_would_be_flagged_in_their_chapter(self):
        """If a non-verified crosswalk row ever returns, the renderer must flag it in its chapter (legend and callout)."""
        import copy
        data = copy.deepcopy(lib.load_apollo1())
        data["records"][3]["crosswalk"].append({"claim": "A test claim.", "status": "article-only", "source": "Our article."})
        atlas = json.loads(ATLAS.read_text(encoding="utf-8"))
        blocks = dict(page.render_blocks(data, atlas))
        self.assertIn("Open question", blocks["01-investigation"])
        self.assertIn("A test claim.", blocks["01-investigation"])

    def test_no_character_that_wordpress_rewrites(self):
        """WordPress's content filters turn a bare ampersand into &#038;. In an inline script that breaks the syntax (`&&` became `&#038;&#038;`
        on draft 2017), so no block may contain one outside a valid entity, and the script must still compile after a conversion pass."""
        entity = re.compile(r"&(?:#[0-9]+|#x[0-9a-fA-F]+|[a-zA-Z][a-zA-Z0-9]{1,31});")
        for b in _entry()["blocks"]:
            text = (BLOCKS_DIR / b["file"]).read_text(encoding="utf-8")
            self.assertNotIn("&", entity.sub("", text), f'{b["file"]}: bare ampersand')
        script = _block().split("<script>", 1)[1].rsplit("</script>", 1)[0]
        self.assertNotIn("&&", script)

    def test_inline_script_compiles_before_and_after_a_wordpress_style_conversion(self):
        import pathlib, shutil, subprocess, tempfile
        node = shutil.which("node")
        self.assertTrue(node, "node is required to compile the inline script; this check cannot be skipped")
        script = _block().split("<script>", 1)[1].rsplit("</script>", 1)[0]
        converted = script
        for _ in range(2):
            converted = re.sub(r"&([^#])(?![a-zA-Z1-4]{1,8};)", r"&#038;\1", converted)
        self.assertEqual(converted, script, "a conversion pass must change nothing")
        with tempfile.TemporaryDirectory() as d:
            f = pathlib.Path(d) / "inline.js"
            f.write_text(converted, encoding="utf-8")
            proc = subprocess.run([node, "--check", str(f)], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_size_budget(self):
        self.assertLess(len(_block().encode()), 110_000)

    def test_rejects_an_unsafe_dataset(self):
        data = json.loads((lib.DATA / "apollo1.json").read_text(encoding="utf-8"))
        data["records"][0]["image"]["src"] = "https://evil.example/a.jpg"
        with self.assertRaises(lib.BadRecord):
            page.render_block(data)


if __name__ == "__main__":
    unittest.main()
