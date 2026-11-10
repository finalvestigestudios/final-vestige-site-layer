"""R264 source-level synthetic regression suite: NOT real-browser or safety approval."""
import importlib.util
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"tools/r264_minimal_wallet_cutout_candidate_hold.py"
spec=importlib.util.spec_from_file_location("r264",P)
gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)
HTML=(ROOT/"audits/r264_minimal_wallet_card_REVIEW_ONLY.html").read_bytes()
ORIGINAL=b"synthetic source only, NOT actual Tool 104"
PIN=gate.git_blob(ORIGINAL)

def held():
    return {"state":gate.HOLD,"original_git_blob":PIN,
        "wallet_cutout_has_privacy_warning":False,
        "printed_card_privacy_resolved":False,
        "requires_editorial_resolution_before_publication":True,
        **{k:False for k in gate.REQUIRED_FALSE}}

def check(html=HTML,original=ORIGINAL,witness=None,pin=PIN):
    return gate.inspect(original,html,held() if witness is None else witness,
                        expected_original_blob=pin)

class Positive(unittest.TestCase):
    def test_structurally_inside_both_faces(self):self.assertIs(check()["cautions_structurally_inside_both_faces"],True)
    def test_two_faces(self):self.assertEqual(check()["cutout_faces"],2)
    def test_hard_hold(self):self.assertEqual(check()["state"],gate.HOLD)
    def test_no_browser_proof(self):self.assertIs(check()["real_browser_and_cutout_qa_completed"],False)
    def test_no_child_privacy_approval(self):self.assertIs(check()["qualified_child_privacy_review_completed"],False)
    def test_not_safe_to_carry_approval(self):self.assertIs(check()["safe_to_carry_certified"],False)
    def test_no_wordpress_approval(self):self.assertIs(check()["ready_for_wordpress"],False)
    def test_original_preserved(self):self.assertTrue(check()["original_source_unchanged"])
    def test_draft_hash(self):self.assertEqual(check()["candidate_git_blob"],gate.git_blob(HTML))
    def test_release_flags(self):
        for k in gate.REQUIRED_FALSE:self.assertIs(check()[k],False)
    def test_nonbytes(self):
        with self.assertRaises(ValueError):check(html="not bytes")
    def test_bad_original_blob(self):
        with self.assertRaises(ValueError):check(original=ORIGINAL+b"X")
    def test_bad_pin(self):
        with self.assertRaises(ValueError):check(pin="no")
    def test_missing_witness(self):
        with self.assertRaises(ValueError):check(witness={})
    def test_false_qd(self):
        w=held();w["independent_qd_pass"]=True
        with self.assertRaises(ValueError):check(witness=w)
    def test_prior_cutout_false_flip(self):
        w=held();w["wallet_cutout_has_privacy_warning"]=True
        with self.assertRaises(ValueError):check(witness=w)

# Every case is a source-changing negative mutation of the exact draft fixture.
MUTATIONS=[
("card_renamed",'class="pa-foldcard"','class="pa-other"'),
("card_duplicated",'class="pa-foldcard"','class="pa-foldcard pa-foldcard"'),
("front_face",'aria-label="Front"','aria-label="Other"'),
("back_face",'aria-label="Back"','aria-label="Other"'),
("front_notice",'lost or photographed','lost'),
("child_names",'child names','names'),
("school_details",'school details','school'),
("home_addresses",'home addresses','locations'),
("passwords",'passwords','codes'),
("medical",'medical information','health'),
("access",'access codes','access'),
("back_notice",'A finder can read this card','People can see it'),
("non_sensitive",'non-sensitive','sensitive'),
("first_privacy_class",'class="pa-privacy"','class="pa-text"'),
("second_privacy_text",'review before sharing','share freely'),
("field_one",'Out-of-area contact:','Child name:'),
("field_two",'Telephone:','Home address:'),
("field_three",'Backup contact:','Guardian info:'),
("field_four",'Backup telephone:','Access PIN:'),
("field_five",'Plan reviewed:','Date of birth:'),
("field_filled",'__________________','Jane Smith'),
("additional_field",'<h2>Emergency contact</h2>','<h2>Emergency contact</h2><p class="pa-write">School: _________________</p>'),
("print_removed",'@media print','@media screen'),
("width",'width:7in','width:8in'),
("height",'min-height:2.125in','min-height:3.125in'),
("clip",'min-width:0;','min-width:0; overflow:hidden;'),
("hide",'font-weight:bold;','font-weight:bold; display:none;'),
("fade",'font-weight:bold;','font-weight:bold; opacity:0;'),
("remote_css",'<style>','<style>@import "https://example.com/a";'),
("url_css",'<style>','<style>h2{background:url(//example.com/t)}'),
("css_content",'<style>','<style>h2:before{content:"x"}'),
("css_position",'<style>','<style>h2{position:absolute}'),
("script",'<h2>Emergency contact</h2>','<script>alert(1)</script><h2>Emergency contact</h2>'),
("form",'<h2>Emergency contact</h2>','<form></form><h2>Emergency contact</h2>'),
("iframe",'<h2>Emergency contact</h2>','<iframe></iframe><h2>Emergency contact</h2>'),
("img",'<h2>Emergency contact</h2>','<img src="x"><h2>Emergency contact</h2>'),
("onclick",'class="pa-write"','class="pa-write" onclick="alert(1)"'),
("href",'class="pa-write"','class="pa-write" href="/checkout/"'),
("src",'class="pa-write"','class="pa-write" src="x"'),
("style_attr",'class="pa-write"','class="pa-write" style="color:red"'),
("duplicate_attr",'class="pa-write"','class="pa-write" class="pa-write"'),
("data_attr",'class="pa-write"','class="pa-write" data-id="track"'),
("cite",'<h2>Emergency contact</h2>','{{cite:unverified}}<h2>Emergency contact</h2>'),
("link",'<h2>Emergency contact</h2>','{{link:merchant|pay}}<h2>Emergency contact</h2>'),
("http",'<h2>Emergency contact</h2>','http://example.com<h2>Emergency contact</h2>'),
("https",'<h2>Emergency contact</h2>','https://example.com<h2>Emergency contact</h2>'),
("utm",'<h2>Emergency contact</h2>','utm_campaign=x<h2>Emergency contact</h2>'),
("no_unapproved",'UNAPPROVED REVIEW CONCEPT','APPROVED FOR PUBLICATION'),
("no_distribute",'Do not distribute','Distribute freely'),
("extra_editor_note",'class="pa-editor-note"','class="pa-editor-note pa-editor-note"'),
("self_closing",'<h2>Emergency contact</h2>','<h2/>Emergency contact'),
("svg",'<h2>Emergency contact</h2>','<svg></svg><h2>Emergency contact</h2>'),
("noscript",'<h2>Emergency contact</h2>','<noscript></noscript><h2>Emergency contact</h2>'),
("meta",'<h2>Emergency contact</h2>','<meta http-equiv="refresh"><h2>Emergency contact</h2>'),
]
class Negative(unittest.TestCase):pass
for name,old,new in MUTATIONS:
    def make(old=old,new=new,name=name):
        def test(self):
            self.assertIn(old.encode(),HTML,name)
            variant=HTML.replace(old.encode(),new.encode(),1)
            self.assertNotEqual(variant,HTML)
            with self.assertRaises(ValueError,msg=name):check(html=variant)
        return test
    setattr(Negative,"test_mutation_"+name,make())

# R265 regression cases: a global ordered notice list is NOT face ownership.
# Tests repin the MUTATED synthetic HTML to force semantic rejection rather
# than relying only on R220's fixed candidate hash.
FRONT_WARN='<p class="pa-privacy">'+gate.NOTICES[0]+'</p>'
BACK_WARN='<p class="pa-privacy">'+gate.NOTICES[1]+'</p>'
HTML_TEXT=HTML.decode("utf-8")
FACE_BACK='<section class="pa-face" aria-label="Back">'
FACE_FRONT='<section class="pa-face" aria-label="Front">'
FRONT_END='<p class="pa-write">Telephone: __________________</p>\n</section>'
BACK_END='<p class="pa-write">Plan reviewed: __________________</p>\n</section>'

def _new_case(title, transform):
    def test(self):
        changed=transform(HTML_TEXT)
        self.assertNotEqual(changed,HTML_TEXT,title)
        with self.assertRaises(ValueError,msg=title):
            check(html=changed.encode("utf-8"))
    return test

def _both_front(s):
    self_check=BACK_WARN+"\n"
    assert self_check in s
    return s.replace(self_check,"",1).replace(FRONT_WARN,FRONT_WARN+"\n"+BACK_WARN,1)

def _both_back(s):
    assert FRONT_WARN+"\n" in s
    return s.replace(FRONT_WARN+"\n","",1).replace(
        '<h2>Backup contact</h2>','<h2>Backup contact</h2>\n'+FRONT_WARN,1)

def _nested_faces(s):
    assert FRONT_END+"\n"+FACE_BACK in s
    assert BACK_END in s
    return s.replace(FRONT_END+"\n"+FACE_BACK,
                     '<p class="pa-write">Telephone: __________________</p>\n'+FACE_BACK,1).replace(
        BACK_END,BACK_END+"\n</section>",1)

def _wrapped_back(s):
    assert FACE_BACK in s and BACK_END in s
    return s.replace(FACE_BACK,"<div>"+FACE_BACK,1).replace(BACK_END,BACK_END+"\n</div>",1)

def _wrapped_front(s):
    assert FACE_FRONT in s and FRONT_END in s
    return s.replace(FACE_FRONT,"<div>"+FACE_FRONT,1).replace(FRONT_END,FRONT_END+"\n</div>",1)

def _warning_outside(s):
    assert BACK_WARN+"\n" in s and "</div>\n<p class=\"pa-editor-note\">" in s
    return s.replace(BACK_WARN+"\n","",1).replace(
        '</div>\n<p class="pa-editor-note">',
        '</div>\n'+BACK_WARN+'\n<p class="pa-editor-note">',1)

for _name,_transform in (
    ("both_notices_on_front",_both_front),
    ("both_notices_on_back",_both_back),
    ("nested_sibling_faces",_nested_faces),
    ("back_face_wrapped",_wrapped_back),
    ("front_face_wrapped",_wrapped_front),
    ("warning_outside_cutout",_warning_outside),
):
    setattr(Negative,"test_r265_"+_name,_new_case(_name,_transform))

if __name__=="__main__":unittest.main()
