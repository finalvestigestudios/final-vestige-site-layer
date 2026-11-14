"""R355 adversarial synthetic tests. Never substitute for native/QD verification."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import r355_tool104_claim_custody_hold as gate

BODY = '''<p>Call 911 for anything life-threatening, and use text messages
rather than calls for everything else when networks are busy.
{{cite:shelter-ready-tech}} What you type stays on this page.
It is not sent or saved. Closing the tab clears it.</p>
<style>.pa-face {font-size:7.5pt}</style>
<p>Do not put a child's full name or a medical diagnosis on the card.
First names or nicknames and phone numbers are usually enough.</p>
<p>The CDC suggests giving children emergency contact cards for their
school bags. {{cite:shelter-cdc-reunification}}</p>
<p>Government agency information is not saved, stored or shared by any
government agency. {{cite:shelter-ready-plan-form}}</p>
<noscript>Print a blank card and fill it by hand.</noscript>
<script>{{inline-js:reunion_card.js}}</script><form onsubmit="return false"></form>'''
META = {"kind":"tool","slug":"family-reunification-card","n":104,
        "status":{"publish":"draft"},"safety_review":{"state":"pending"},
        "title":"Family contact card","dek":"Free, local-only",
        "description":"Nothing is stored","tags":["Runs locally"],
        "source_use":{"shelter-ready-tech":"SMS","shelter-cdc-reunification":"CDC",
                      "shelter-ready-plan-form":"Official form"}}

class TestR355(unittest.TestCase):
    def call(self, body=BODY, meta=None, **kwargs):
        return gate.inspect(body, copy.deepcopy(META if meta is None else meta), **kwargs)
    def must(self, flag, body=BODY, meta=None, **kwargs):
        report=self.call(body,meta,**kwargs)
        self.assertEqual(report["status"],"INVALID_HARD_HOLD",report)
        self.assertIn(flag,report["errors"])
        self.assertTrue(all(report[k] is False for k in gate.HOLD))
    def test_docket(self):
        report=self.call()
        self.assertEqual(len(report["obligations"]),8)
        self.assertEqual(report["citation_ids"],
                         ["shelter-ready-tech","shelter-cdc-reunification",
                          "shelter-ready-plan-form"])
    def test_original_pins(self):
        self.assertEqual(gate.BODY_GIT_BLOB,"be8698ac5d020476ff649d85813810e2000c6f98")
        self.assertEqual(gate.META_GIT_BLOB,"47da1e7e20e39f0ea85e26d54a8d58301f6e0a15")
    def test_python_probe_holds_without_checkout(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(gate.native_probe(Path(directory))["status"],
                             "INVALID_HARD_HOLD")
    def test_python_probe_holds_on_mutated_original(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/".git").mkdir()
            f=root/"preparedness/content/tools"
            f.mkdir(parents=True)
            (f/"family-reunification-card.body.html").write_text(BODY)
            (f/"family-reunification-card.meta.json").write_text(json.dumps(META))
            result=gate.native_probe(root)
            self.assertFalse(result["native_body_blob_verified"])
            self.assertFalse(result["native_meta_blob_verified"])
    def test_source_id_no_register(self):
        meta=copy.deepcopy(META); meta["source_use"]={}
        self.must("SOURCE_USE_REGISTER_MISSING_OR_INVALID",meta=meta)
    def test_source_id_added(self):
        self.must("INLINE_SOURCE_IDS_NOT_DECLARED",body=BODY+"{{cite:fake-new-source}}")
    def test_cites_missing(self):
        self.must("INLINE_CITATION_EVIDENCE_MISSING",body="<p>uncited text</p>")
    def test_reordered_metadata_digest(self):
        alt={k:META[k] for k in reversed(list(META))}
        self.assertEqual(self.call()["metadata_semantic_sha256"],
                         self.call(meta=alt)["metadata_semantic_sha256"])
    def test_changed_body_digest(self):
        self.assertNotEqual(self.call()["body_sha256"],
                            self.call(body=BODY+" difference")["body_sha256"])
    def test_html_parser_hides_script_prose(self):
        body="<script>what you type stays on this page</script><noscript>Blank</noscript>{{cite:shelter-ready-tech}}"
        self.assertNotIn("ABSOLUTE_PRIVACY_PROMISE_REQUIRES_RUNTIME_PROOF",
                         self.call(body)["errors"])
    def test_missing_private_surfaces(self):
        self.must("PRIVATE_RENDER_SURFACES_NOT_PROVIDED")
    def test_no_js_fallback_missing(self):
        self.must("NO_JS_ALTERNATIVE_NOT_EVIDENCED",
                  body=BODY.replace("<noscript>Print a blank card and fill it by hand.</noscript>",""))
    def test_private_wrapper_fake_identical(self):
        self.must("IDENTICAL_RENDER_WRAPPERS_ARE_NOT_AUTHENTIC_PARITY",
                  render_surfaces={"wp":"pending review","preview":"pending review"})
    def test_private_metadata_fake_release(self):
        self.must("PRIVATE_RENDER_PUBLICATION_SIGNAL:preview",
                  render_surfaces={"wp":"pending review",
                                   "preview":'pending review "datePublished":"2026"'})
    def test_private_missing_notice(self):
        self.must("PRIVATE_RENDER_HOLD_DISCLOSURE_NOT_ESTABLISHED:wp",
                  render_surfaces={"wp":"no notice","preview":"pending review"})
    def test_private_absolute_copy(self):
        self.must("PRIVATE_RENDER_ABSOLUTE_PRIVACY_COPY:wp",
                  render_surfaces={"wp":"pending review nothing is stored",
                                   "preview":"pending review"})
    def test_invalid_body(self):
        self.must("INVALID_INPUT",body=None)
    def test_invalid_metadata(self):
        out=gate.inspect(BODY,None)
        self.assertIn("INVALID_INPUT",out["errors"])
    def test_invalid_surfaces(self):
        self.must("INVALID_RENDER_SURFACES",render_surfaces="not a map")
    def test_unverified_meta_claim(self):
        meta=copy.deepcopy(META);meta["qd_pass"]=True
        self.must("UNSUPPORTED_CLEARANCE_OR_COMMERCE_FIELD",meta=meta)
    def test_unreviewed_merchant_claim(self):
        meta=copy.deepcopy(META);meta["verified_paid_orders"]=1
        self.must("UNSUPPORTED_CLEARANCE_OR_COMMERCE_FIELD",meta=meta)
    def test_pin_rewrites_fail(self):
        self.must("ORIGINAL_BODY_GIT_BLOB_DRIFT",pin_original=True)

# Each independently named variant is a real unittest case.
CLAIM_CASES = [
 ("privacy_page","what you type stays on this page","ABSOLUTE_PRIVACY_PROMISE_REQUIRES_RUNTIME_PROOF"),
 ("privacy_sent","it is not sent or saved","ABSOLUTE_PRIVACY_PROMISE_REQUIRES_RUNTIME_PROOF"),
 ("privacy_close","closing the tab clears it","ABSOLUTE_PRIVACY_PROMISE_REQUIRES_RUNTIME_PROOF"),
 ("privacy_nothing","nothing is stored","ABSOLUTE_PRIVACY_PROMISE_REQUIRES_RUNTIME_PROOF"),
 ("emergency_911","call 911 for anything life-threatening","BLANKET_EMERGENCY_AND_SMS_ADVICE_UNREVIEWED"),
 ("emergency_text","text messages rather than calls for everything else","BLANKET_EMERGENCY_AND_SMS_ADVICE_UNREVIEWED"),
 ("child_full","do not put a child's full name","CHILD_CARRIED_CARD_SCOPE_REQUIRES_QUALIFIED_REVIEW"),
 ("child_diagnosis","do not put a medical diagnosis","CHILD_CARRIED_CARD_SCOPE_REQUIRES_QUALIFIED_REVIEW"),
 ("child_nicknames","first names or nicknames and phone numbers are usually enough","CHILD_CARRIED_CARD_SCOPE_REQUIRES_QUALIFIED_REVIEW"),
 ("cdc_contact","CDC suggests giving contact cards to children","CDC_CARD_COMPLETENESS_AND_CONTEXT_NOT_CERTIFIED"),
 ("cdc_school","CDC suggests giving children emergency contact cards for their school bags","CDC_CARD_COMPLETENESS_AND_CONTEXT_NOT_CERTIFIED"),
 ("smallprint7","<style>a{font-size:7pt}</style>","SMALL_PRINT_REQUIRES_ACCESSIBILITY_REVIEW"),
 ("smallprint75","<style>a{font-size:7.5pt}</style>","SMALL_PRINT_REQUIRES_ACCESSIBILITY_REVIEW"),
 ("smallprint8","<style>a{font-size:8pt}</style>","SMALL_PRINT_REQUIRES_ACCESSIBILITY_REVIEW"),
 ("client_script","<script>console.log('fixture')</script>","CLIENT_SCRIPT_PRIVACY_NO_JS_NOT_VERIFIED"),
 ("inline_js","{{inline-js:reunion_card.js}}","CLIENT_SCRIPT_PRIVACY_NO_JS_NOT_VERIFIED"),
 ("form_submit","<form onsubmit='return false'></form>","CLIENT_SCRIPT_PRIVACY_NO_JS_NOT_VERIFIED"),
 ("form_change","<input onchange='x'>","CLIENT_SCRIPT_PRIVACY_NO_JS_NOT_VERIFIED"),
 ("gov_transfer","not saved, stored or shared by any government agency. what you type stays on this page","GOVERNMENT_FORM_PRIVACY_NOT_TRANSFERABLE_TO_FV"),
]
def claim_case(fragment, flag):
    def run(self):
        body="<noscript>Blank</noscript>{{cite:shelter-ready-tech}}<p>"+fragment+"</p>"
        self.must(flag,body=body)
    return run
for name, fragment, flag in CLAIM_CASES:
    setattr(TestR355,"test_claim_"+name,claim_case(fragment,flag))

META_CASES=[
 ("slug","slug","fake-slug","TOOL_104_IDENTITY_DRIFT"),
 ("number","n",102,"TOOL_104_IDENTITY_DRIFT"),
 ("kind","kind","article","TOOL_104_IDENTITY_DRIFT"),
 ("publish","status",{"publish":"public"},"UNAUTHORIZED_PUBLISH_STATE"),
 ("status_bad","status","published","UNAUTHORIZED_PUBLISH_STATE"),
 ("approve","safety_review",{"state":"approved"},"SAFETY_REVIEW_STATE_MUST_STAY_PENDING"),
 ("review_absent","safety_review",None,"SAFETY_REVIEW_STATE_MUST_STAY_PENDING"),
 ("source_absent","source_use",{},"SOURCE_USE_REGISTER_MISSING_OR_INVALID"),
 ("source_fake","source_use",{"made-up":"yes"},"INLINE_SOURCE_IDS_NOT_DECLARED"),
 ("source_wrongtype","source_use",["source"],"SOURCE_USE_REGISTER_MISSING_OR_INVALID"),
 ("qd","qd_pass",True,"UNSUPPORTED_CLEARANCE_OR_COMMERCE_FIELD"),
 ("merchant","verified_paid_orders",4,"UNSUPPORTED_CLEARANCE_OR_COMMERCE_FIELD"),
 ("permission","may_publish",True,"UNSUPPORTED_CLEARANCE_OR_COMMERCE_FIELD"),
 ("approval","independent_approval","yes","UNSUPPORTED_CLEARANCE_OR_COMMERCE_FIELD"),
 ("local","description","local-only","META_PRIVACY_PROMISE_NOT_RUNTIME_VERIFIED"),
 ("runs","description","runs locally","META_PRIVACY_PROMISE_NOT_RUNTIME_VERIFIED"),
 ("nothing","description","nothing is stored","META_PRIVACY_PROMISE_NOT_RUNTIME_VERIFIED"),
 ("no_data","description","no data is stored","META_PRIVACY_PROMISE_NOT_RUNTIME_VERIFIED"),
 ("never","description","never stored","META_PRIVACY_PROMISE_NOT_RUNTIME_VERIFIED"),
]
def meta_case(k,v,flag):
    def run(self):
        meta=copy.deepcopy(META);meta[k]=v
        self.must(flag,meta=meta)
    return run
for name,k,v,flag in META_CASES:
    setattr(TestR355,"test_meta_"+name,meta_case(k,v,flag))

if __name__=="__main__":
    unittest.main()
