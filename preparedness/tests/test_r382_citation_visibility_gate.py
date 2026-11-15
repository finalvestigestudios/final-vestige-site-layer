"""R382 synthetic citation visibility tests. Never edit original source or article files."""
import importlib.util, unittest
from pathlib import Path

PATH=Path(__file__).resolve().parents[1]/"tools"/"r382_citation_visibility_gate.py"
SPEC=importlib.util.spec_from_file_location("r382_gate",PATH)
G=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(G)
TEXT="A full original claim with substantial reader-facing context and safety caveats."
GOOD="<p>"+TEXT+"{{cite:src-a}}</p>"
META={"slug":"synthetic","status":{"publish":"draft"},
      "safety_review":{"state":"pending"},
      "source_use":{"src-a":"This claim is supported in a particular source section."}}

def run_case(html,expected=None,meta=None):
    r=G.examine(html.encode("utf-8"),META if meta is None else meta,{"src-a"})
    assert r["publication_approved"] is False
    assert r["qualified_safety_approved"] is False
    assert r["verified_human_source"] is False
    if expected is None: assert r["errors"]==[],r
    else: assert expected in r["errors"],(expected,r)
    return r

class Invariants(unittest.TestCase):
    def test_clean_static_still_hard_holds(self):
        self.assertEqual(run_case(GOOD)["status"],"STATIC_REVIEW_HARD_HOLD")
    def test_historic_founder_approved_not_independent_qd(self):
        m={**META,"safety_review":{"state":"approved","reviewer":"Founder"}}
        self.assertIn("FOUNDER_LABEL_NOT_INDEPENDENT_QD",run_case(GOOD,meta=m)["warnings"])
    def test_historic_not_required_not_qd(self):
        m={**META,"safety_review":{"state":"not-required"}}
        self.assertFalse(run_case(GOOD,meta=m)["qualified_safety_approved"])
    def test_published_rejected(self):
        m={**META,"status":{"publish":"published"}}
        run_case(GOOD,"NOT_PRIVATE_DRAFT",m)
    def test_non_dict_status_rejected(self):
        m={**META,"status":None}
        run_case(GOOD,"NOT_PRIVATE_DRAFT",m)
    def test_invalid_safety_review_rejected(self):
        m={**META,"safety_review":{"state":"QD PASS"}}
        run_case(GOOD,"INVALID_HISTORICAL_SAFETY_STATE",m)
    def test_missing_safety_review_rejected(self):
        m={**META,"safety_review":None}
        run_case(GOOD,"INVALID_HISTORICAL_SAFETY_STATE",m)
    def test_missing_source_use_map_rejected(self):
        m={**META,"source_use":None}
        run_case(GOOD,"SOURCE_USE_NOT_OBJECT",m)
    def test_empty_source_reading_scope_rejected(self):
        m={**META,"source_use":{"src-a":"  "}}
        run_case(GOOD,"MISSING_READING_SCOPE:src-a",m)
    def test_missing_source_reading_scope_rejected(self):
        m={**META,"source_use":{}}
        run_case(GOOD,"MISSING_READING_SCOPE:src-a",m)
    def test_unrecognized_id_not_substituted(self):
        run_case("<p>"+TEXT+"{{cite:unrecognized}}</p>","UNRESOLVED_ID:unrecognized")
    def test_malformed_input_fails_closed(self):
        r=G.examine(b"\xff",None,set())
        self.assertIn("NON_UTF8_BODY",r["errors"])
    def test_repeated_citation_preserved(self):
        r=run_case("<p>"+TEXT+"{{cite:src-a}} Additional advice.{{cite:src-a}}</p>")
        self.assertEqual(r["raw"],2)
        self.assertTrue(any("REPEATED_SOURCE_SAME_BLOCK" in s for s in r["warnings"]))
    def test_css_screenreader_uncertainty_visible(self):
        self.assertIn("CSS_BROWSER_PRINT_SCREENREADER_UNVERIFIED",run_case(GOOD)["warnings"])
    def test_bad_manifest_rejected(self):
        self.assertEqual(G.audit_originals({},{"sources":[]},lambda _:b"")["status"],"INVALID_HARD_HOLD")
    def test_nonobject_manifest_rejected(self):
        self.assertIn("UNTRUSTED_INPUT",G.audit_originals(None,{},lambda _:b"")["errors"])

class Matrix(unittest.TestCase): pass

def add(name,body,error=None):
    def test(self):
        r=run_case(body,error)
        if error: self.assertEqual(r["status"],"INVALID_HARD_HOLD")
        else: self.assertEqual(r["status"],"STATIC_REVIEW_HARD_HOLD")
    setattr(Matrix,"test_"+name,test)

for name,body in {
    "paragraph":GOOD,
    "list_item":"<li>"+TEXT+"{{cite:src-a}}</li>",
    "table_cell":"<td>"+TEXT+"{{cite:src-a}}</td>",
    "table_header":"<th>"+TEXT+"{{cite:src-a}}</th>",
    "heading":"<h2>"+TEXT+"{{cite:src-a}}</h2>",
    "blockquote":"<blockquote>"+TEXT+"{{cite:src-a}}</blockquote>",
    "figcaption":"<figcaption>"+TEXT+"{{cite:src-a}}</figcaption>",
    "term":"<dt>"+TEXT+"{{cite:src-a}}</dt>",
    "definition":"<dd>"+TEXT+"{{cite:src-a}}</dd>",
    "nested_em":"<p><em>"+TEXT+"</em>{{cite:src-a}}</p>",
    "nested_strong":"<p><strong>"+TEXT+"</strong>{{cite:src-a}}</p>",
    "nested_span":"<p><span>"+TEXT+"</span>{{cite:src-a}}</p>",
    "br":"<p>"+TEXT+"<br>{{cite:src-a}}</p>",
    "safe_comment":"<!-- editorial note --><p>"+TEXT+"{{cite:src-a}}</p>",
    "safe_hidden_unrelated":"<p hidden>Different text</p><p>"+TEXT+"{{cite:src-a}}</p>",
    "safe_script_unrelated":"<script>const x=1;</script><p>"+TEXT+"{{cite:src-a}}</p>",
}.items():add("visible_"+name,body)

for name,body in {
    "hidden_attribute":"<p hidden>"+TEXT+"{{cite:src-a}}</p>",
    "aria_hidden":"<p aria-hidden='true'>"+TEXT+"{{cite:src-a}}</p>",
    "aria_hidden_capital":"<p aria-hidden='TRUE'>"+TEXT+"{{cite:src-a}}</p>",
    "inert":"<section inert><p>"+TEXT+"{{cite:src-a}}</p></section>",
    "display_none":"<p style='display: none'>"+TEXT+"{{cite:src-a}}</p>",
    "visibility_hidden":"<p style='visibility:hidden'>"+TEXT+"{{cite:src-a}}</p>",
    "script":"<script>"+TEXT+"{{cite:src-a}}</script>",
    "style":"<style>"+TEXT+"{{cite:src-a}}</style>",
    "head":"<head>"+TEXT+"{{cite:src-a}}</head>",
    "template":"<template>"+TEXT+"{{cite:src-a}}</template>",
    "svg":"<svg>"+TEXT+"{{cite:src-a}}</svg>",
    "iframe":"<iframe>"+TEXT+"{{cite:src-a}}</iframe>",
    "object":"<object>"+TEXT+"{{cite:src-a}}</object>",
    "canvas":"<canvas>"+TEXT+"{{cite:src-a}}</canvas>",
    "nested_hidden":"<section hidden><p>"+TEXT+"{{cite:src-a}}</p></section>",
}.items():add("invisible_"+name,body,"INVISIBLE_CITATION")

for name,body in {
    "comment":"<!-- {{cite:src-a}} -->",
    "attribute":"<p data-src='{{cite:src-a}}'>Claim</p>",
    "href":"<a href='{{cite:src-a}}'>Link</a>",
    "declaration":"<!DOCTYPE html {{cite:src-a}}>",
}.items():add("nontext_"+name,body,"NON_TEXT_CITATION")

for name,body in {
    "empty":"{{cite:}}",
    "uppercase":"{{cite:SRC-A}}",
    "missing_brace":"{{cite:src-a}",
    "spaces":"{{cite: src-a}}",
    "split":"{{cite:<span>src-a}}</span>",
    "underscore":"{{cite:src_a}}",
}.items():add("malformed_"+name,body,"MALFORMED_CITATION_TOKEN")

if __name__=="__main__":unittest.main()
