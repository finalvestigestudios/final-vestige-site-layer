"""R353 adversarial synthetic parity fixtures; never a native build or QD PASS."""
import json
import unittest
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
import r353_private_wp_preview_parity_hold as gate

SECTIONS=["start-here","water","food","shelter-power",
          "health-sanitation","family-communication","lost-ways","field-tools"]
SLUGS=[f"guide-{i:02d}" for i in range(35)]+[f"tool-{i:02d}" for i in range(6)]

def wp(inner):
    return "<!-- wp:html -->\n<style>.pa{color:#fff}</style>\n"+inner+"\n<!-- /wp:html -->\n"

def pv(inner):
    return '<!doctype html><html><head><meta name="robots" content="noindex,nofollow"></head><body><main>'+inner+"</main></body></html>"

def fixture():
    taxonomy={"base_path":"/preparedness/","sections":[{"slug":s} for s in SECTIONS]}
    docs=[]; artifacts={}; article_rows=[]
    for i,slug in enumerate(SLUGS):
        kind="articles" if i<35 else "tools"
        sec=SECTIONS[i%8] if i<35 else "field-tools"
        text="<p>"+" ".join(["Careful source-aware family preparation."]*24)+"</p> {{cite:official}}"
        meta={"slug":slug,"section":sec,"status":{"publish":"draft"},
              "safety_review":{"state":"pending"}}
        docs.append({"kind":kind,"meta":meta,"body":text})
        route="https://finalvestige.com/preparedness/"+sec+"/"+slug+"/"
        article_rows.append({"slug":slug,"canonical":route,"words":gate._words(text),"sources":["official"]})
        content="<p>"+" ".join(["Careful source-aware family preparation."]*24)+"</p>"
        content+='<sup class="pa-cite">[1]</sup>'
        graph={"@graph":[{"@type":"Article","mainEntityOfPage":route}]}
        inner='<div class="pa pa-article"><p>Draft: not public</p>'
        inner+='<p>Independent safety/source and QD verification pending</p>'
        inner+='<div class="pa-shell"><div class="pa-body" id="pa-main">'+content+'</div></div>'
        inner+='<section class="pa-sources"><ol><li id="src-1">Official</li></ol></section>'
        inner+='<script type="application/ld+json">'+json.dumps(graph)+'</script></div>'
        artifacts["wp/"+slug+".html"]=wp(inner)
        artifacts["preview/"+slug+".html"]=pv(inner)
    for sec in SECTIONS:
        slug="hub-"+sec
        graph={"@graph":[{"@type":"CollectionPage",
                          "url":"https://finalvestige.com/preparedness/"+sec+"/"}]}
        inner='<div class="pa pa-hub"><script type="application/ld+json">'+json.dumps(graph)+'</script></div>'
        artifacts["wp/"+slug+".html"]=wp(inner)
        artifacts["preview/"+slug+".html"]=pv(inner)
    land={"@type":"CollectionPage","url":"https://finalvestige.com/preparedness/"}
    inner='<div class="pa pa-landing"><script type="application/ld+json">'+json.dumps(land)+'</script></div>'
    artifacts["wp/landing.html"]=wp(inner)
    artifacts["preview/landing.html"]=pv(inner)
    report={"articles":article_rows,
            "hubs":[{"section":s,"guides":5} for s in SECTIONS],
            "landing":{"article_cards":41,"populated_sections":SECTIONS[:]},
            "release_evidence":{"state":"HOLD","independent_qa_verified":False,
                                "wordpress_publication_performed":False,
                                "article_drafts":41,"article_published":0}}
    return taxonomy,docs,artifacts,report

class TestPrivateParity(unittest.TestCase):
    def setUp(self):
        self.tax,self.docs,self.art,self.report=fixture()
    def reject(self,reason):
        x=gate.audit(self.tax,self.docs,self.art,self.report)
        self.assertEqual(x["status"],"INVALID_HARD_HOLD",x["errors"])
        self.assertTrue(any(reason in e for e in x["errors"]),x["errors"])
        self.assertFalse(x["may_publish"])
        self.assertFalse(x["qualified_qd_pass"])
    def test_synthetic_fixture_never_approves_release(self):
        x=gate.audit(self.tax,self.docs,self.art,self.report)
        self.assertEqual(x["status"],"PRIVATE_PARITY_ONLY_HARD_HOLD",x["errors"])
        self.assertEqual(x["pairs_compared"],50)
        self.assertFalse(x["qualified_qd_pass"])
    def test_missing_full_checkout_fails_closed(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as path:
            x=gate.native_audit(path)
        self.assertEqual(x["status"],"INVALID_HARD_HOLD")
    def test_published_draft_claim_rejected(self):
        self.docs[0]["meta"]["status"]["publish"]="published"
        self.reject("NONPRIVATE_OR_UNSAFE_STATE")
    def test_fabricated_qd_pass_rejected(self):
        self.report["release_evidence"]["qualified_qd_pass"]=True
        self.reject("FALSE_OR_MISSING_RELEASE_HOLD")
    def test_fabricated_sale_rejected(self):
        self.report["release_evidence"]["verified_paid_orders"]=1
        self.reject("FALSE_OR_MISSING_RELEASE_HOLD")
    def test_source_citation_loss_rejected(self):
        self.report["articles"][0]["sources"]=[]
        self.reject("SOURCE_CITATION_OR_CANONICAL_DRIFT")
    def test_false_revenue_or_safety_not_returned(self):
        x=gate.audit(self.tax,self.docs,self.art,self.report)
        self.assertFalse(x["paid_offer_verified"])
        self.assertFalse(x["independent_claim_support_verified"])
    def test_missing_release_hard_hold(self):
        del self.report["release_evidence"]
        self.reject("FALSE_OR_MISSING_RELEASE_HOLD")
    def test_missing_guide_body_rejected(self):
        self.docs.pop()
        self.reject("CORPUS_NOT_35_ARTICLES_6_TOOLS")
    def test_duplicate_article_slug(self):
        self.docs[0]["meta"]["slug"]=self.docs[1]["meta"]["slug"]
        self.reject("DUPLICATE_ORIGINAL_SLUG")
    def test_duplicate_report_row(self):
        self.report["articles"][0]["slug"]=self.report["articles"][1]["slug"]
        self.reject("DUPLICATE_REPORT_ID")
    def test_internal_retired_url_rejected(self):
        for key in ("wp/guide-00.html","preview/guide-00.html"):
            self.art[key]=self.art[key].replace("Draft: not public",
                '<a href="/preparedness/retired-water-product/">No</a>Draft: not public')
        self.reject("UNBUILT_INTERNAL_LINK")
    def test_unsecured_scheme_rejected(self):
        for key in ("wp/guide-00.html","preview/guide-00.html"):
            self.art[key]=self.art[key].replace("Draft: not public",
                '<a href="HTTP://example.org">No</a>Draft: not public')
        self.reject("UNSAFE_EXPORT_LINK")
    def test_false_article_publish_date_rejected(self):
        for key in ("wp/guide-00.html","preview/guide-00.html"):
            self.art[key]=self.art[key].replace('"@type": "Article"',
                '"@type": "Article", "datePublished":"2026-11-13"')
        self.reject("ARTICLE_STRUCTURED_DATA_DRIFT")
    def test_header_warning_removed_rejected(self):
        for key in ("wp/guide-00.html","preview/guide-00.html"):
            self.art[key]=self.art[key].replace("Draft: not public","Ready to publish")
        self.reject("DRAFT_HOLD_MARKER_MISSING")
    def test_report_reading_depth_reduction(self):
        self.report["articles"][0]["words"]=1
        self.reject("READING_REPORT_REDUCTION")
    def test_tampered_landing_canonical(self):
        for key in ("wp/landing.html","preview/landing.html"):
            self.art[key]=self.art[key].replace("https://finalvestige.com/preparedness/",
                "https://example.org/unauthorized/")
        self.reject("HUB_OR_LANDING_CANONICAL_DRIFT")

def _missing(slug):
    def test(self):
        del self.art["preview/"+slug+".html"]
        self.reject("PRIVATE_EXPORT_SET_NOT_EXACT_100")
    return test

def _drift(slug):
    def test(self):
        self.art["preview/"+slug+".html"]=self.art["preview/"+slug+".html"].replace("<main>","<main>UNAPPROVED COPY")
        self.reject("WORDPRESS_PREVIEW_PARITY_FAIL")
    return test

for _slug in SLUGS+["hub-"+s for s in SECTIONS]+["landing"]:
    setattr(TestPrivateParity,"test_missing_preview_"+_slug.replace("-","_"),_missing(_slug))
    setattr(TestPrivateParity,"test_divergence_"+_slug.replace("-","_"),_drift(_slug))

if __name__=="__main__":
    unittest.main()
