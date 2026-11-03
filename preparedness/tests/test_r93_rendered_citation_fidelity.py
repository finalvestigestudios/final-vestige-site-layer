"""Isolated R93 synthetic mutations and native corpus citation-output fidelity tests."""
from __future__ import annotations

import html
from pathlib import Path
import sys
import unittest
import re

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import r93_rendered_citation_fidelity as target  # noqa: E402


class FakeLib:
    def __init__(self, count=7):
        self.data = {f"s{i}": {
            "id": f"s{i}", "url": f"https://example.org/source-{i}",
            "title": f"Independent reading {i}", "_origin": f"cluster-{i}",
            "human_link_check": False
        } for i in range(1, count + 1)}
        self.crosswalk_groups = {}
        body = "".join(f"<p>Full independent statement {i} {{{{cite:s{i}}}}}</p>"
                       for i in range(1, count + 1))
        self.meta = {
            "slug": "test-guide", "title": "Test guide",
            "description": "Testing only", "section": "water",
            "_body": body, "status": {"publish": "draft", "editorial": "drafted"},
            "safety_review": {"state": "pending"},
            "source_use": {f"s{i}": f"Original unabridged reading scope {i}"
                           for i in range(1, count + 1)}
        }
        self.articles = {"test-guide": self.meta}
        self.taxonomy = {"slate": [{"slug": f"article-{i}"}
                                    for i in range(1, 36)],
                         "tools": [{"slug": "test-guide"}, *[
                             {"slug": f"planned-tool-{i}"} for i in range(5)]]}

    def source_for(self, meta, sid):
        return self.data[sid]

    def url_path(self, slug):
        return "/preparedness/water/" + slug + "/"


def synthetic_html(lib, order=None, meta=None):
    m = meta or lib.meta
    ids = order or [f"s{i}" for i in range(1, len(lib.data) + 1)]
    number = {x: i for i, x in enumerate(dict.fromkeys(ids), 1)}
    cites = "".join(
        f'<p>Full independent statement {j} <sup class="pa-cite">'
        f'<a href="#src-{number[sid]}" aria-label="Source {number[sid]}: '
        f'{html.escape(lib.data[sid]["title"], quote=True)}">'
        f'[{number[sid]}]</a></sup></p>'
        for j, sid in enumerate(ids, 1))
    sources = "".join(
        f'<li id="src-{number[sid]}"><a href="{lib.data[sid]["url"]}">'
        f'{html.escape(lib.data[sid]["title"])}</a>'
        f'<span class="pa-src-meta">Human source-link check pending</span>'
        f'<span class="pa-src-use">Used for: '
        f'{html.escape(m["source_use"][sid])}</span></li>'
        for sid in dict.fromkeys(ids))
    return (
        '<div class="pa pa-article" data-slug="test-guide">'
        '<header>Draft: not public Safety review pending</header>'
        f'<div class="pa-body" id="pa-main">{cites}</div>'
        '<section class="pa-sources"><ol>' + sources + '</ol></section>'
        '<section class="pa-review">'
        'A human safety review is required before this page can be published.'
        '</section></div>'
    )


class SyntheticAuditTests(unittest.TestCase):
    def setUp(self):
        self.lib = FakeLib()
        self.html = synthetic_html(self.lib)

    def check(self, markup=None):
        return target.audit_document(self.lib, self.lib.meta,
                                     self.html if markup is None else markup)

    def test_control_exact_seven(self):
        rows = self.check()
        self.assertEqual(len(rows), 7)
        self.assertEqual([x["literal_source_ID"] for x in rows],
                         [f"s{i}" for i in range(1, 8)])
        self.assertTrue(all(x["may_publish"] is False and
                            x["human_claim_review"] == "NOT_REVIEWED"
                            for x in rows))

    def test_repeated_one_id_has_two_distinct_review_rows(self):
        lib = FakeLib(1)
        lib.meta["_body"] += " <p>Repeated {{cite:s1}}</p>"
        markup = synthetic_html(lib).replace("</div><section class=\"pa-sources\">",
                 '<p>Repeated <sup class="pa-cite">'
                 '<a href="#src-1" aria-label="Source 1: Independent reading 1">'
                 '[1]</a></sup></p></div><section class="pa-sources">')
        rows = target.audit_document(lib, lib.meta, markup)
        self.assertEqual(len(rows), 2)
        self.assertEqual([r["citation_ordinal"] for r in rows], [1, 2])
        self.assertEqual({r["literal_source_ID"] for r in rows}, {"s1"})

    def test_reordered_original_sources_are_rejected(self):
        self.lib.meta["_body"] = self.lib.meta["_body"].replace(
            "{{cite:s1}}", "{{cite:s7}}", 1)
        with self.assertRaises(target.Gate):
            self.check()

    def test_duplicate_source_footnote_rejected(self):
        with self.assertRaises(target.Gate):
            self.check(self.html.replace('id="src-2"', 'id="src-1"'))

    def test_rendered_citation_added_rejected(self):
        mutated = self.html.replace("</div><section class=\"pa-sources\">",
            '<sup class="pa-cite"><a href="#src-1" '
            'aria-label="Source 1: Independent reading 1">[1]</a></sup>'
            '</div><section class="pa-sources">')
        with self.assertRaises(target.Gate):
            self.check(mutated)

    def test_missing_original_citation_rejected(self):
        self.lib.meta["_body"] += " New citation {{cite:s1}}"
        with self.assertRaises(target.Gate):
            self.check()

    def test_duplicate_source_scope_not_equivalent(self):
        # Two contributor records may have exactly the same URL.
        self.lib.data["s2"]["url"] = self.lib.data["s1"]["url"]
        unchanged = self.html.replace("https://example.org/source-2",
                                      "https://example.org/source-1")
        with self.assertRaises(target.Gate):
            self.check(unchanged)
        self.lib.crosswalk_groups[self.lib.data["s1"]["url"]] = {
            "review_status": "pending"}
        with self.assertRaises(target.Gate):
            self.check(unchanged)
        repaired = unchanged.replace(
            '<span class="pa-src-meta">Human source-link check pending</span>',
            '<span class="pa-src-meta">Human source-link check pending</span>'
            '<span>Shared-source reading scope: independent review pending</span>', 2)
        self.assertEqual(len(self.check(repaired)), 7)

    def test_raw_body_must_be_literal(self):
        self.lib.meta["_body"] = None
        with self.assertRaises(target.Gate):
            self.check()

    def test_missing_draft_badge_rejected(self):
        with self.assertRaises(target.Gate):
            self.check(self.html.replace("Draft: not public", "Approved for release"))

    def test_published_status_rejected(self):
        self.lib.meta["status"]["publish"] = "published"
        with self.assertRaises(target.Gate):
            self.check()

    def test_pending_review_disclaimer_must_survive(self):
        with self.assertRaises(target.Gate):
            self.check(self.html.replace("A human safety review is required before"
                                         " this page can be published.", ""))

    def test_human_source_check_is_not_assumed(self):
        self.lib.data["s1"]["human_link_check"] = True
        with self.assertRaises(target.Gate):
            self.check()
        changed = self.html.replace("Human source-link check pending",
                                    "Human source-link check complete", 1)
        self.assertEqual(len(self.check(changed)), 7)

    def test_article_identity_cannot_shift(self):
        with self.assertRaises(target.Gate):
            self.check(self.html.replace('data-slug="test-guide"',
                                         'data-slug="another-guide"'))

    def test_missing_author_scoped_source_use_rejected(self):
        del self.lib.meta["source_use"]["s4"]
        with self.assertRaises(target.Gate):
            self.check()

    def test_unchecked_extra_source_use_rejected(self):
        self.lib.meta["source_use"]["unread-source"] = "x"
        with self.assertRaises(target.Gate):
            self.check()

    def test_http_source_is_rejected(self):
        self.lib.data["s1"]["url"] = "http://example.org/insecure"
        with self.assertRaises(target.Gate):
            self.check()

    def test_author_origin_cannot_be_removed(self):
        del self.lib.data["s4"]["_origin"]
        with self.assertRaises(target.Gate):
            self.check()

    def test_html_outside_source_list_cannot_fake_a_source(self):
        markup = self.html.replace('<section class="pa-sources">',
              '<footer><a href="https://example.org/source-99">Fake source</a></footer>'
              '<section class="pa-sources">')
        self.assertEqual(len(self.check(markup)), 7)

    def test_unapproved_source_scope_not_hidden(self):
        self.lib.meta["source_use"]["s1"] = "Only first paragraph was checked"
        with self.assertRaises(target.Gate):
            self.check()

    def test_bogus_safety_state_rejected(self):
        self.lib.meta["safety_review"]["state"] = "clinically-safe"
        with self.assertRaises(target.Gate):
            self.check()

    def test_seal_stable_for_identical_payloads(self):
        obj = {"z": [1, 2, 3], "a": "full scope"}
        self.assertEqual(target.seal(obj), target.seal(dict(reversed(list(obj.items())))))


def _mutant(case, ordinal):
    lib = FakeLib()
    markup = synthetic_html(lib)
    sid = "s" + str(ordinal)
    title = lib.data[sid]["title"]
    srcurl = lib.data[sid]["url"]
    scope = lib.meta["source_use"][sid]
    number = str(ordinal)
    if case == "inline_href":
        before, after = (f'href="#src-{number}"',
                         f'href="#src-{ordinal+100}"')
    elif case == "inline_label":
        before, after = (f'aria-label="Source {number}: {title}"',
                         f'aria-label="Source {number}: Untested reference"')
    elif case == "inline_number":
        before, after = (f'[{number}]</a></sup>', f'[{ordinal+100}]</a></sup>')
    elif case == "source_url":
        before, after = (f'href="{srcurl}"',
                         f'href="https://unverified.example.org/{ordinal}"')
    elif case == "source_id":
        before, after = (f'id="src-{number}"',
                         f'id="src-{ordinal+100}"')
    elif case == "source_title":
        before, after = (f'>{title}</a>',
                         f'>Misattributed reading {ordinal}</a>')
    elif case == "source_scope":
        before, after = (f'Used for: {scope}',
                         f'Used for: unverified alternative {ordinal}')
    else:
        raise AssertionError("unknown adversarial case")
    assert before in markup
    markup = markup.replace(before, after, 1)
    return lib, markup


# Seven separate source positions x seven independent corruption dimensions:
# 49 discoverable unittest tests, rather than one loop disguised as a test.
for _case in ("inline_href", "inline_label", "inline_number", "source_url",
              "source_id", "source_title", "source_scope"):
    for _ordinal in range(1, 8):
        def _test(self, case=_case, ordinal=_ordinal):
            lib, page = _mutant(case, ordinal)
            with self.assertRaises(target.Gate,
                                   msg=f"{case} source {ordinal} was accepted"):
                target.audit_document(lib, lib.meta, page)
        setattr(SyntheticAuditTests, f"test_mutation_{_case}_{_ordinal}", _test)


class NativeCorpusTests(unittest.TestCase):
    def test_actual_wordpress_drafts_not_historical_packet_claims(self):
        # Read only; all data stays in memory. This is a transport integrity
        # regression, not a QD PASS, human review or permission to publish.
        import build
        lib = build.Library()
        report = target.audit_library(lib, build.build_article, build.wp_wrap,
                                      build.preview_wrap)
        self.assertEqual(report["release_state"], "HOLD")
        self.assertFalse(report["may_publish"])
        self.assertEqual(report["full_slate_article_count"], 35)
        self.assertEqual(report["planned_tools"], 6)
        self.assertEqual(report["actual_article_drafts"], 35)
        self.assertEqual(len(report["missing_tool_drafts_NOT_WORDPRESS_READY"]),
                         6 - report["actual_tool_drafts"])
        self.assertEqual(report["actual_distinct_draft_routes"],
                         report["actual_article_drafts"] + report["actual_tool_drafts"])
        self.assertTrue(all(x["may_publish"] is False for x in
            report["unabridged_rendered_source_workorders_NOT_APPROVED"]))
        copy = dict(report)
        checksum = copy.pop("sha256_seal")
        self.assertEqual(target.seal(copy), checksum)


if __name__ == "__main__":
    unittest.main()
