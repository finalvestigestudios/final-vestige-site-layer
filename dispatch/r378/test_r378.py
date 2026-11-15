"""R378: offline-only six original-issue safety tests. No network, email or CMS calls.
Run: python -m unittest discover -s dispatch/r378 -p 'test_r378.py' -v
"""
import unittest, json, re, subprocess
from pathlib import Path
from html.parser import HTMLParser

HERE=Path(__file__).resolve().parent
MASTER=HERE.parent/"campaign-2026-mind"/"issues"

class Tags(HTMLParser):
    def __init__(self):
        super().__init__(); self.tags=[]; self.links=[]; self.h1=0; self.lang=[]; self.bad=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs); self.tags.append(tag)
        if tag=="a": self.links.append(d.get("href",""))
        if tag=="h1": self.h1+=1
        if tag=="html": self.lang.append(d.get("lang"))
        if tag in ("script","form","img","iframe","object","video","audio"): self.bad.append(tag)

class R378Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest=json.loads((HERE/"ORIGINAL_SIX_RELEASE_STATE.json").read_text())
        cls.rows=cls.manifest["issues"]
    def test_01_six(self):
        self.assertEqual([r["issue"] for r in self.rows],["01","02","03","04","05","06"])
    def test_02_four_two(self):
        self.assertEqual([r["issue"] for r in self.rows if r["kind"]!="editorial"],["03","05"])
    def test_03_all_hold(self):
        self.assertEqual(self.manifest["release_state"],"HOLD_UNSENT")
        self.assertTrue(all(r["status"].startswith("HOLD") for r in self.rows))
    def test_04_live_gates_false(self):
        self.assertFalse(any(self.manifest["pending"].values()))
        self.assertIsNone(self.manifest["wordpress"]["actual_unique_eligible_email_inboxes"])
    def test_05_original_blob_ids(self):
        for r in self.rows:
            f=MASTER/Path(r["source_path"]).name
            self.assertTrue(f.is_file())
            sha=subprocess.check_output(["git","hash-object",str(f)],text=True).strip()
            self.assertEqual(sha,r["source_git_blob_sha"])
    def test_06_subject_from_original(self):
        for r in self.rows:
            src=(MASTER/Path(r["source_path"]).name).read_text()
            self.assertIn("**Subject:** "+r["subject"],src)
    def test_07_markup_accessibility(self):
        for r in self.rows:
            data=(HERE/r["html"]).read_text()
            t=Tags();t.feed(data)
            self.assertEqual(t.lang,["en"])
            self.assertEqual(t.h1,1)
            self.assertEqual(t.bad,[])
            self.assertGreaterEqual(t.tags.count("table"),2)
            self.assertTrue(all(u.startswith("https://") for u in t.links))
            self.assertIn("COMPLIANCE HARD STOP",data)
            self.assertIn("OFFLINE SPECIMEN",data)
            self.assertIn("table-layout:fixed",data)
            self.assertIn("word-break:break-word",data)
    def test_08_merchant_links_not_live(self):
        for r in self.rows:
            t=Tags();t.feed((HERE/r["html"]).read_text())
            self.assertFalse(any(re.search(r"(zen12|hypnosislive|inspire3)\.com",u,re.I) for u in t.links))
    def test_09_plaintext_safety(self):
        for r in self.rows:
            s=(HERE/r["plaintext"]).read_text()
            self.assertIn("COMPLIANCE HARD STOP",s)
            self.assertIn("NOT VERIFIED JETPACK FIELD",s)
            self.assertNotIn("<script",s)
    def test_10_guide_cta_inert(self):
        for n in ("03","05"):
            h=(HERE/(n+".html")).read_text()
            self.assertIn("GUIDE NOT APPROVED",h)
            self.assertNotIn('href="[[',h)
            self.assertIn("Commercial disclosure",h)
    def test_11_apollo_copy_hold(self):
        r=next(r for r in self.rows if r["issue"]=="04")
        self.assertEqual(r["status"],"HOLD_COPY")
        self.assertIn("Fourteen seconds",r["subject"])
    def test_12_no_fake_rendering(self):
        for r in self.rows:
            self.assertFalse(r["native_jetpack_preheader_verified"])
            self.assertFalse(r["native_jetpack_preview_verified"])
            self.assertFalse(r["publisher_postal_verified"])
            self.assertFalse(r["actual_unsubscribe_verified"])
    def test_13_all_board_links_present(self):
        board=(HERE/"REVIEW_BOARD.html").read_text()
        for r in self.rows:
            self.assertIn(r["html"],board)
            self.assertIn(r["plaintext"],board)
    def test_14_no_send_implementation(self):
        self.assertFalse(any(p.suffix in (".php",".sh") for p in HERE.iterdir()))

if __name__=="__main__": unittest.main()
