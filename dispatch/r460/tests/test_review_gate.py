"""Portable local tests. They test failure modes with fixtures, not actual email delivery."""
import unittest
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from review_gate import inspect, PDF, SOURCE_URLS

class GateChecks(unittest.TestCase):
    def setUp(self):
        self.md = "# THE DISPATCH\nNot approved to replace PR #175\n" + PDF + "\n" + "\n".join(SOURCE_URLS)
        self.txt = "Subject: The map was not the whole argument\nPreheader (review intent only; native Jetpack transport not verified): John Snow's 1854 investigation, and the limits of a seven-day log.\nHOLD UNSENT\n" + PDF + "\n" + "\n".join(SOURCE_URLS)
        self.html = '<html lang="en"><table role="presentation"><h1 >The map was not the whole argument</h1>' + ''.join(f'<a href="{u}">Source reference</a>' for u in SOURCE_URLS) + f'<a href="{PDF}">Read the Focus Fieldbook PDF</a>HOLD UNSENT</table></html>'
        for k in ("[[VALID_POSTAL_ADDRESS_REQUIRED]]","[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]"):
            self.md += k
            self.txt += k
            self.html += k
        self.ledger = {"status":"HOLD_UNSENT","claims":[{"commercial_rights_verified":False} for _ in range(6)]}
    def check(self): return inspect(self.md,self.txt,self.html,self.ledger)
    def test_good_fixture(self): self.assertEqual(self.check(),[])
    def test_duplicate_cta(self):
        self.html += f'<a href="{PDF}">Again</a>'
        self.assertTrue(self.check())
    def test_mail_missing_address(self):
        self.html=self.html.replace("[[VALID_POSTAL_ADDRESS_REQUIRED]]","")
        self.assertTrue(self.check())
    def test_misleading_approval(self):
        self.ledger["claims"][0]["commercial_rights_verified"]=True
        self.assertTrue(self.check())
    def test_merchant_link(self):
        self.html += '<a href="https://zen12.com/secret/">Buy now</a>'
        self.assertTrue(self.check())
    def test_tracking(self):
        self.html += "?utm_campaign=test"
        self.assertTrue(self.check())
    def test_script(self):
        self.html += '<script>alert(1)</script>'
        self.assertTrue(self.check())
    def test_missing_sources(self):
        self.txt=self.txt.replace(SOURCE_URLS[0],"")
        self.assertTrue(self.check())
    def test_email_subject(self):
        self.txt=self.txt.replace("Subject: The map was not the whole argument","Subject: MIRACLE")
        self.assertTrue(self.check())
    def test_no_release_hold(self):
        self.ledger["status"]="READY"
        self.assertTrue(self.check())
    def test_empty_anchor(self):
        self.html += '<a href="#">  </a>'
        self.assertTrue(self.check())

if __name__ == "__main__":
    unittest.main()
