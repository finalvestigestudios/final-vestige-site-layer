"""R354 synthetic safety-regression tests; not native build or qualified QD."""
import unittest
import tempfile
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
import r354_exact_claim_render_custody_hold as gate

SLUGS=[f"guide-{i:02d}" for i in range(35)]+[f"tool-{i:02d}" for i in range(6)]
BODY=('<p>Source A <sup class="pa-cite"><a href="#src-1" aria-label="Source 1: Agency A">[1]</a></sup>'
      ' and B <sup class="pa-cite"><a href="#src-2" aria-label="Source 2: Agency B">[2]</a></sup>.</p>')
SRC=('<section class="pa-sources"><li id="src-1"><a href="https://agency-a.gov/">Agency A</a> Human source-link check pending</li>'
     '<li id="src-2"><a href="https://agency-b.gov/">Agency B</a> Human source-link check pending</li></section>')
def fixture():
    entries=[];artifacts={};reports=[]
    for i,s in enumerate(SLUGS):
        entries.append({"slug":s,"kind":"articles" if i<35 else "tools","publish":"draft","safety":"pending",
          "original":"<p>Source A {{cite:agency-a}} and B {{cite:agency-b}}.</p>",
          "resolved":BODY,"sources_html":SRC,"source_ids":["agency-a","agency-b"]})
        reports.append({"slug":s,"sources":["agency-a","agency-b"]})
        inner='<div class="pa"><div class="pa-body" id="pa-main">'+BODY+'</div></div>'+SRC+'</div>'
        artifacts["wp/"+s+".html"]='<!-- wp:html -->\n<style>.pa{}</style>\n'+inner+'\n<!-- /wp:html -->\n'
        artifacts["preview/"+s+".html"]='<!doctype html><html><head><meta name="robots" content="noindex,nofollow"></head><body><main>'+inner+'</main></body></html>'
    report={"articles":reports,"release_evidence":{"state":"HOLD","independent_qa_verified":False,
             "wordpress_publication_performed":False,"article_published":0}}
    return entries,artifacts,report

class TestR354(unittest.TestCase):
    def setUp(self):self.rows,self.art,self.report=fixture()
    def reject(self,marker):
        out=gate.audit(self.rows,self.art,self.report)
        self.assertEqual(out["status"],"INVALID_HARD_HOLD",out["errors"])
        self.assertTrue(any(marker in error for error in out["errors"]),out["errors"])
        for k in gate.HOLD:self.assertFalse(out[k])
    def test_synthetic_baseline_still_hard_hold(self):
        o=gate.audit(self.rows,self.art,self.report)
        self.assertEqual(o["status"],"RESEARCH_ONLY_EXACT_RENDER_HARD_HOLD",o["errors"])
        self.assertEqual(o["paired_private_documents"],41)
        self.assertFalse(o["may_publish"])
    def test_missing_checkout(self):
        with tempfile.TemporaryDirectory() as p:o=gate.native_audit(p)
        self.assertEqual(o["status"],"INVALID_HARD_HOLD")
    def test_missing_article(self):
        self.rows.pop(0);self.reject("CORPUS_35_ARTICLES_6_TOOLS_REQUIRED")
    def test_duplicate_slug(self):
        self.rows[0]["slug"]=self.rows[1]["slug"];self.reject("DUPLICATE_SOURCE_SLUG")
    def test_published_state(self):
        self.rows[0]["publish"]="published";self.reject("PRIVATE_SOURCE_STATE_DRIFT")
    def test_fake_safety_approval(self):
        self.rows[0]["safety"]="approved";self.reject("PRIVATE_SOURCE_STATE_DRIFT")
    def test_false_report_sources(self):
        self.report["articles"][0]["sources"]=["agency-b","agency-a"];self.reject("REPORT_CITATION_SOURCE_DRIFT")
    def test_false_qd(self):
        self.report["release_evidence"]["qualified_qd_pass"]=True;self.reject("RELEASE_HOLD_MISSING_OR_FALSE")
    def test_false_paid_orders(self):
        self.report["release_evidence"]["verified_paid_orders"]=5;self.reject("RELEASE_HOLD_MISSING_OR_FALSE")
    def test_not_a_hold(self):
        self.report["release_evidence"]["state"]="PASS";self.reject("RELEASE_HOLD_MISSING_OR_FALSE")
    def test_reassigned_source_order(self):
        self.rows[0]["source_ids"]=["agency-b","agency-a"];self.reject("SOURCE_ID_ORDER_UNBOUND")
    def test_no_sources(self):
        self.rows[0]["source_ids"]=[];self.reject("SOURCE_ID_ORDER_UNBOUND")
    def test_disclosure_claim_upgrade(self):
        for kind in ("wp","preview"):
            k=kind+"/guide-00.html";self.art[k]=self.art[k].replace("check pending","check complete")
        self.reject("EXACT_SOURCE_DISCLOSURE_DRIFT")
    def test_equal_word_count_changed_claim(self):
        for kind in ("wp","preview"):
            k=kind+"/guide-00.html";self.art[k]=self.art[k].replace("Source A","Source Z")
        self.reject("EXACT_CLAIM_RENDER_DRIFT")
    def test_citation_retargeted_same_count(self):
        for kind in ("wp","preview"):
            k=kind+"/guide-00.html";self.art[k]=self.art[k].replace('href="#src-2"','href="#src-1"')
        self.reject("CLAIM_CITATION_POSITION_DRIFT")
    def test_source_url_substituted_same_count(self):
        for kind in ("wp","preview"):
            k=kind+"/guide-00.html";self.art[k]=self.art[k].replace("agency-b.gov","untrusted.invalid")
        self.reject("EXACT_SOURCE_DISCLOSURE_DRIFT")
    def test_unresolved_citation(self):
        for kind in ("wp","preview"):
            k=kind+"/guide-00.html";self.art[k]=self.art[k].replace("Source A","{{cite:agency-a}} Source A")
        self.reject("UNRESOLVED_CITATION")

def make_missing(i):
    def test(self):
        slug=SLUGS[i];del self.art["preview/"+slug+".html"]
        self.reject("INVALID_OR_MISSING_PRIVATE_EXPORT")
    return test
def make_body(i):
    def test(self):
        slug=SLUGS[i]
        for kind in ("wp","preview"):
            k=kind+"/"+slug+".html";self.art[k]=self.art[k].replace("Source A","Source X")
        self.reject("EXACT_CLAIM_RENDER_DRIFT")
    return test
def make_disclosure(i):
    def test(self):
        slug=SLUGS[i]
        for kind in ("wp","preview"):
            k=kind+"/"+slug+".html";self.art[k]=self.art[k].replace("agency-a.gov","example.invalid")
        self.reject("EXACT_SOURCE_DISCLOSURE_DRIFT")
    return test

for i,slug in enumerate(SLUGS):
    setattr(TestR354,"test_missing_"+slug.replace("-","_"),make_missing(i))
    setattr(TestR354,"test_claim_"+slug.replace("-","_"),make_body(i))
    setattr(TestR354,"test_source_"+slug.replace("-","_"),make_disclosure(i))
if __name__=="__main__":unittest.main()
