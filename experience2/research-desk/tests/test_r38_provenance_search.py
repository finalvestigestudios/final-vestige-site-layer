"""R38 actual-source evidence and search custody tests. No WordPress or network writes.
Run from complete repository checkout:
  python -m unittest experience2/research-desk/tests/test_r38_provenance_search.py -v
"""
import hashlib
import json
import pathlib
import re
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
EXPECTED={
    "templates/ledger.html":"4842afb84b4c993cfc4861ce7f5a7a4d7b451871",
    "assets/source-ledger.css":"7b0972fc3a920ded08f9783fddcfc9c609c7ff06",
    "assets/source-ledger.js":"57f4a639d4c37fc4355b10fe7dec085bf87c6eb7",
}

def git_blob(data):
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\\0"+data).hexdigest()

def records(html):
    return re.findall(r'<article\\b[^>]*data-fvx-record\\b[^>]*>[\\s\\S]*?</article>', html)

class ProvenanceSearch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html=(ROOT/"templates/ledger.html").read_text(encoding="utf-8")
        cls.js=(ROOT/"assets/source-ledger.js").read_text(encoding="utf-8")
        cls.css=(ROOT/"assets/source-ledger.css").read_text(encoding="utf-8")
        cls.data=json.loads((ROOT/"sources/R37_PHOTO_CUSTODY_CROSSWALK.json").read_text())
    def test_exact_reviewed_blobs(self):
        for rel,expected in EXPECTED.items():
            with self.subTest(path=rel):
                self.assertEqual(git_blob((ROOT/rel).read_bytes()),expected)
    def test_six_sources_and_rights_hold(self):
        self.assertEqual(len(records(self.html)),6)
        self.assertEqual(self.html.count("data-fvx-photo-record="),6)
        self.assertEqual(self.html.count("data-fvx-chrono-link"),6)
        self.assertEqual(self.html.count("Image reuse has not been individually reviewed or cleared"),6)
        self.assertEqual(self.data["release"],"STAGING_HOLD")
        self.assertEqual(len(self.data["records"]),6)
        self.assertTrue(all(x["media_rights"]=="INDIVIDUAL_REVIEW_REQUIRED" for x in self.data["records"]))
    def test_provenance_search_indexes_real_visible_text(self):
        hits=[i+1 for i,c in enumerate(records(self.html)) if "kim shiflett" in c.casefold()]
        self.assertEqual(hits,[4,6])
        self.assertIn("card.textContent",self.js)
        self.assertIn("getAttribute('data-fvx-search')",self.js)
    def test_keyboard_touch_clear_is_nojs_safe(self):
        self.assertEqual(self.html.count("data-fvx-clear"),1)
        self.assertIn("data-fvx-clear hidden",self.html)
        for token in ("event.key==='Escape'","clear.addEventListener('click',clearSearch)",
                      "clear.removeEventListener('click',clearSearch)",
                      "search.focus()","clear.hidden=!needle",
                      "cards.forEach(card=>{card.hidden=false;})"):
            self.assertIn(token,self.js)
        for token in (".fv-ex2-ledger__clear","min-height:44px","[hidden]{display:none!important}"):
            self.assertIn(token,self.css)
    def test_no_geo_media_or_external_injection(self):
        self.assertNotRegex(self.html,r'data-(?:lat|lng|fvx-geo)\\b|mapbox|leaflet')
        self.assertNotRegex(self.html,r'<(?:img|iframe|script|canvas)\\b')
        self.assertNotIn("innerHTML=",self.js)
        self.assertNotIn("fetch(",self.js)
    def test_negative_mutations_rejected(self):
        self.assertNotEqual(records(self.html.replace("data-fvx-record","broken-record",1)),records(self.html))
        self.assertNotEqual(self.html.replace("data-fvx-clear hidden","data-fvx-clear",1),self.html)
        self.assertNotEqual(self.js.replace("card.textContent","''",1),self.js)

if __name__=="__main__":unittest.main()
