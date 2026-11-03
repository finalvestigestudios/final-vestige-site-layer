"""R97 private JSON-LD, canonical destination and generated-navigation regression.

All mutations are in memory. No fixtures are written to the shared working
tree, no URL contacted, and no WordPress or public-site action is permitted.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402
import r97_structured_data_route_custody as gate  # noqa: E402

LIB = build.Library()
META = LIB.articles["household-emergency-plan"]
BASE = build.build_article(LIB, META["slug"])


def mutated_page(html):
    page = dict(BASE)
    page["inner"] = html
    return page


def replace_html(old, new):
    html = BASE["inner"]
    assert old in html, ("test mutation target disappeared", old)
    return mutated_page(html.replace(old, new, 1))


def set_nested(obj, path, value):
    target = obj
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value


def altered_ld(change):
    page = copy.deepcopy(BASE)
    found = re.search(r'<script type="application/ld\+json">(.*?)</script>',
                      page["inner"], re.S)
    assert found, "builder JSON-LD script missing"
    doc = json.loads(found.group(1))
    change(doc)
    page["inner"] = (page["inner"][:found.start(1)] +
                     json.dumps(doc, ensure_ascii=False) +
                     page["inner"][found.end(1):])
    return page


def page_with_raw_ld(raw):
    page = dict(BASE)
    found = re.search(r'<script type="application/ld\+json">(.*?)</script>',
                      page["inner"], re.S)
    assert found
    page["inner"] = page["inner"][:found.start(1)] + raw + page["inner"][found.end(1):]
    return page


class GoodPrivateContracts(unittest.TestCase):
    def test_actual_draft_identity_is_explicitly_hold(self):
        row = gate.audit_page(META, BASE, LIB)
        self.assertEqual(row["slug"], META["slug"])
        self.assertEqual(row["release_state"], "HOLD")
        self.assertIs(row["may_publish"], False)
        self.assertEqual(row["qualified_safety_review"], "NOT_REVIEWED")

    def test_same_page_is_deterministic(self):
        self.assertEqual(gate.audit_page(META, BASE, LIB),
                         gate.audit_page(META, BASE, LIB))

    def test_canonical_is_exact(self):
        self.assertEqual(gate.audit_page(META, BASE, LIB)["canonical"],
                         "https://finalvestige.com/preparedness/start-here/household-emergency-plan/")

    def test_declared_safety_approval_is_not_independent_qd_pass(self):
        # Only an in-memory metadata fixture is modified; no review granted.
        meta = {**META, "safety_review": {"state": "approved"}}
        result = gate.audit_page(meta, BASE, LIB)
        self.assertIs(result["may_publish"], False)
        self.assertEqual(result["independent_QD"], "NOT_REVIEWED")

    def test_semantic_jsonld_key_order_is_immaterial(self):
        page = altered_ld(lambda d: d.update(list(reversed(list(d.items())))))
        self.assertEqual(gate.audit_page(META, page, LIB)["release_state"], "HOLD")

    def test_duplicate_jsonld_key_fails_closed(self):
        source = re.search(r'<script type="application/ld\+json">(.*?)</script>',
                           BASE["inner"], re.S).group(1)
        malformed = source.replace('{"@context":',
                                   '{"@context":"https://schema.org","@context":', 1)
        with self.assertRaises(gate.Gate):
            gate.audit_page(META, page_with_raw_ld(malformed), LIB)

    def test_duplicate_citation_policy_remains_upstream(self):
        # This R97 gate must never claim to replace the R93-R96 custody gates.
        self.assertEqual(gate.SCHEMA, "r97-private-structured-data-route-custody-hold-v1")

    def test_base_route_rejects_non_preparedness(self):
        taxonomy = dict(LIB.taxonomy)
        taxonomy["base_path"] = "/external/"
        shadow = copy.copy(LIB)
        shadow.taxonomy = taxonomy
        with self.assertRaises(gate.Gate):
            gate.audit_page(META, BASE, shadow)

    def test_page_dict_missing(self):
        with self.assertRaises(gate.Gate):
            gate.audit_page(META, {"slug": META["slug"]}, LIB)

    def test_page_canonical_altered(self):
        page = dict(BASE, canonical="https://evil.example/preparedness/")
        with self.assertRaises(gate.Gate):
            gate.audit_page(META, page, LIB)

    def test_page_slug_altered(self):
        with self.assertRaises(gate.Gate):
            gate.audit_page(META, dict(BASE, slug="other-guide"), LIB)

    def test_source_publish_status_gated(self):
        meta = copy.deepcopy(META)
        meta["status"]["publish"] = "published"
        with self.assertRaises(gate.Gate):
            gate.audit_page(meta, BASE, LIB)

    def test_no_meta_slug_traversal(self):
        meta = dict(META, slug="../other")
        with self.assertRaises(gate.Gate):
            gate.audit_page(meta, BASE, LIB)

    def test_no_meta_section_traversal(self):
        meta = dict(META, section="../other")
        with self.assertRaises(gate.Gate):
            gate.audit_page(meta, BASE, LIB)

    def test_invalid_track_is_closed(self):
        meta = dict(META, track="unreviewed-track")
        with self.assertRaises(gate.Gate):
            gate.audit_page(meta, BASE, LIB)


# Literal in-HTML attacks on the generated (not authored) page shell. Every
# entry becomes its own unittest method; no shared-tree mutation is necessary.
SHELL_ATTACKS = {
    "root_duplicate_data_slug": ('data-slug="household-emergency-plan"',
                                'data-slug="household-emergency-plan" data-slug="other"'),
    "root_wrong_section": ('data-section="start-here"', 'data-section="food"'),
    "root_wrong_track": ('data-track="modern"', 'data-track="lost-ways"'),
    "root_unknown_attr": ('data-track="modern"', 'data-track="modern" data-cert="approved"'),
    "root_hidden": ('data-track="modern"', 'data-track="modern" hidden'),
    "root_role_none": ('data-track="modern"', 'data-track="modern" role="none"'),
    "skip_destination": ('class="pa-skip" href="#pa-main"',
                         'class="pa-skip" href="#private-nowhere"'),
    "skip_open_redirect": ('class="pa-skip" href="#pa-main"',
                           'class="pa-skip" href="https://example.net/"'),
    "skip_fake_label": ('Skip to the guide', 'This has been medically approved'),
    "skip_duplicate": ('class="pa-skip" href="#pa-main"',
                       'class="pa-skip" href="#pa-main" data-extra="1"'),
    "breadcrumb_role": ('class="pa-crumbs" aria-label="Breadcrumb"',
                        'class="pa-crumbs" aria-label="Certified Advice"'),
    "breadcrumb_hidden": ('class="pa-crumbs" aria-label="Breadcrumb"',
                          'class="pa-crumbs" aria-label="Breadcrumb" hidden'),
    "breadcrumb_wrong_home": ('<a href="/">Final Vestige</a>',
                              '<a href="https://example.com/">Final Vestige</a>'),
    "breadcrumb_fake_home": ('<a href="/">Final Vestige</a>',
                             '<a href="/">Official Government Agency</a>'),
    "breadcrumb_extra_link": ('<a href="/">Final Vestige</a>',
                              '<a href="/">Final Vestige</a><a href="/approved/">Approved</a>'),
    "breadcrumb_current_removed": ('<span aria-current="page">',
                                   '<span class="not-current">'),
    "breadcrumb_current_changed": ('<span aria-current="page">',
                                   '<span aria-current="false">'),
    "breadcrumb_duplicate": ('class="pa-crumbs" aria-label="Breadcrumb"',
                             'class="pa-crumbs pa-crumbs" aria-label="Breadcrumb"'),
    "header_h1_falsified": ('<h1>' + META["h1"] + '</h1>',
                            '<h1>Officially verified survival guidance</h1>'),
    "extra_root_instructions": ('<a class="pa-skip"',
                                '<p>Confirmed medically safe to follow.</p><a class="pa-skip"'),
    "extra_root_source_link": ('<a class="pa-skip"',
                               '<a href="https://example.com/misleading">Medical approval</a><a class="pa-skip"'),
    "extra_shell_banner": ('<div class="pa-shell">',
                           '<div class="pa-shell"><aside>Ignore emergency warnings</aside>'),
    "extra_shell_script": ('<div class="pa-shell">',
                           '<div class="pa-shell"><script>alert(1)</script>'),
    "extra_shell_style": ('<div class="pa-shell">',
                          '<div class="pa-shell"><style>.pa-review{display:none}</style>'),
    "jsonld_type_changed": ('type="application/ld+json"',
                            'type="application/javascript"'),
    "jsonld_script_async": ('type="application/ld+json"',
                            'type="application/ld+json" async'),
    "jsonld_script_hidden": ('type="application/ld+json"',
                             'type="application/ld+json" hidden'),
    "jsonld_script_duplicate_attr": ('type="application/ld+json"',
                                     'type="application/ld+json" type="text/javascript"'),
    "jsonld_script_removed": ('<script type="application/ld+json">',
                              '<span class="metadata">'),
}


def make_shell_test(old, new):
    def test(self):
        page = replace_html(old, new)
        with self.assertRaises(gate.Gate):
            gate.audit_page(META, page, LIB)
    return test


for name, (old, new) in SHELL_ATTACKS.items():
    setattr(GoodPrivateContracts, "test_adversarial_shell_" + name,
            make_shell_test(old, new))


# Every distinct forged field in the JSON-LD object is an independent
# negative test. Source and claim accuracy cannot be invented by metadata.
LD_ATTACKS = {
    "context_wrong": (("@context",), "https://example.org"),
    "graph_wrong_type": (("@graph",), []),
    "article_type_changed": (("@graph", 0, "@type"), "MedicalWebPage"),
    "article_id_retargeted": (("@graph", 0, "@id"), "https://attacker.invalid/article"),
    "article_headline_changed": (("@graph", 0, "headline"), "Doctor-certified advice"),
    "article_description_changed": (("@graph", 0, "description"), "Approved safe"),
    "article_canonical_retargeted": (("@graph", 0, "mainEntityOfPage"), "https://attacker.invalid"),
    "article_date_advanced": (("@graph", 0, "dateModified"), "2099-01-01"),
    "article_lang_changed": (("@graph", 0, "inLanguage"), "xx-YY"),
    "article_author_person": (("@graph", 0, "author"), {"@type": "Person", "name": "Unknown doctor"}),
    "article_publisher_wrong": (("@graph", 0, "publisher", "name"), "Emergency Ministry"),
    "article_publisher_url": (("@graph", 0, "publisher", "url"), "https://attacker.invalid/"),
    "article_access_false": (("@graph", 0, "isAccessibleForFree"), False),
    "breadcrumb_type_changed": (("@graph", 1, "@type"), "MedicalWebPage"),
    "breadcrumb_position": (("@graph", 1, "itemListElement", 1, "position"), 8),
    "breadcrumb_home_retargeted": (("@graph", 1, "itemListElement", 0, "item"),
                                  "https://attacker.invalid/"),
    "breadcrumb_title_changed": (("@graph", 1, "itemListElement", 3, "name"),
                                 "Verified medical survival instructions"),
    "breadcrumb_crumb_type": (("@graph", 1, "itemListElement", 0, "@type"), "HowToStep"),
}


def make_ld_test(path, value):
    def test(self):
        def attack(doc):
            set_nested(doc, path, value)
        with self.assertRaises(gate.Gate):
            gate.audit_page(META, altered_ld(attack), LIB)
    return test


for name, (path, value) in LD_ATTACKS.items():
    setattr(GoodPrivateContracts, "test_adversarial_jsonld_" + name,
            make_ld_test(path, value))


EXTRA_LD = {
    "published_date": ("datePublished", "2026-11-03"),
    "reviewed_claim": ("reviewedBy", {"@type": "Person", "name": "Medical Review Board"}),
    "implied_safety": ("medicalSpecialty", "EmergencyMedicine"),
    "implied_rating": ("aggregateRating", {"@type": "AggregateRating",
                                          "ratingValue": 5, "ratingCount": 500}),
    "certified_by": ("recognizedBy", {"@type": "Organization", "name": "CDC"}),
    "false_safety_award": ("award", "Clinically safe"),
    "medical_audience": ("audience", {"@type": "MedicalAudience", "name": "Patients"}),
    "date_fake": ("dateCreated", "2000-01-01"),
    "speakable_fake": ("speakable", {"@type": "SpeakableSpecification", "cssSelector": ".pa-sources"}),
    "external_sameas": ("sameAs", "https://attacker.invalid/"),
    "malicious_image": ("image", "https://attacker.invalid/pixel.gif"),
}


def make_extra_test(field, value):
    def test(self):
        def attack(doc):
            doc["@graph"][0][field] = value
        with self.assertRaises(gate.Gate):
            gate.audit_page(META, altered_ld(attack), LIB)
    return test


for name, (field, value) in EXTRA_LD.items():
    setattr(GoodPrivateContracts, "test_adversarial_jsonld_injected_" + name,
            make_extra_test(field, value))


class WholeSlate(unittest.TestCase):
    def test_all_actual_private_drafts_preserve_route_and_jsonld(self):
        self.assertEqual(len(LIB.articles), 36)
        rows = [gate.audit_page(meta, build.build_article(LIB, slug), LIB)
                for slug, meta in sorted(LIB.articles.items())]
        self.assertEqual(len(set(row["canonical"] for row in rows)), 36)
        self.assertTrue(all(row["may_publish"] is False for row in rows))

    def test_unchanged_all_draft_routes_are_deterministic(self):
        first = [gate.audit_page(meta, build.build_article(LIB, slug), LIB)
                 for slug, meta in sorted(LIB.articles.items())]
        second = [gate.audit_page(meta, build.build_article(LIB, slug), LIB)
                  for slug, meta in sorted(LIB.articles.items())]
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
