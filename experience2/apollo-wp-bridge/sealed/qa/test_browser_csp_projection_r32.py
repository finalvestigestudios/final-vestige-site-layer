"""Fail-closed adversarial controls for the R32 header-to-Chromium projection."""
import unittest
from browser_csp_projection_r32 import project_policy, projected_html

NONCE='aBcDeFgHiJkLmNoPqRsTuVwX'
CSP=("default-src 'none'; script-src 'nonce-"+NONCE+"'; style-src 'nonce-"+NONCE+
     "'; img-src 'none'; font-src 'none'; connect-src 'none'; object-src 'none'; "
     "base-uri 'none'; form-action 'none'; frame-ancestors 'self'")
HTML=('<!doctype html><html><head><style nonce="'+NONCE+'">a{color:red}</style></head>'
      '<body><script nonce="'+NONCE+'">window.ok=true</script></body></html>').encode()
class ProjectionTests(unittest.TestCase):
    def test_strict_projection(self):
        p=project_policy(CSP,NONCE)
        self.assertNotIn('frame-ancestors',p)
        self.assertIn("default-src 'none'",p)
        rendered=projected_html(HTML,p,NONCE,probes=True)
        self.assertIn('http-equiv="Content-Security-Policy"',rendered)
        self.assertIn('window.__r32_blocked=true',rendered)
    def test_csp_duplication_rejected(self):
        with self.assertRaises(AssertionError):project_policy(CSP+"; script-src 'self'",NONCE)
    def test_remote_execution_rejected(self):
        with self.assertRaises(AssertionError):project_policy(CSP.replace("'nonce-"+NONCE+"'", "'self'",1),NONCE)
    def test_insecure_inline_rejected(self):
        with self.assertRaises(AssertionError):project_policy(CSP.replace("script-src 'nonce-"+NONCE+"'","script-src 'unsafe-inline'"),NONCE)
    def test_missing_form_action_rejected(self):
        with self.assertRaises(AssertionError):project_policy(CSP.replace("form-action 'none'; ",""),NONCE)
    def test_weakened_frame_policy_rejected(self):
        with self.assertRaises(AssertionError):project_policy(CSP.replace("frame-ancestors 'self'","frame-ancestors *"),NONCE)
    def test_unknown_directive_rejected(self):
        with self.assertRaises(AssertionError):project_policy(CSP+"; navigate-to *",NONCE)
    def test_duplicate_nonce_tag_rejected(self):
        with self.assertRaises(AssertionError):projected_html(HTML.replace(b'</body>',('<script nonce="'+NONCE+'"></script></body>').encode()),'abc',NONCE,probes=True)
    def test_missing_head_rejected(self):
        with self.assertRaises(AssertionError):projected_html(HTML.replace(b'<head>',b''),'abc',NONCE,probes=True)
    def test_existing_csp_meta_rejected(self):
        with self.assertRaises(AssertionError):projected_html(HTML.replace(b'<head>',b'<head><meta http-equiv="Content-Security-Policy" content="default-src *">'),'abc',NONCE,probes=True)
    def test_invalid_nonce_rejected(self):
        with self.assertRaises(AssertionError):project_policy(CSP,'x')
if __name__=='__main__':unittest.main()
