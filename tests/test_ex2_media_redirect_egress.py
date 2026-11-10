"""Real localhost HTTP redirect egress regression for FV archival media checks.

All network calls target 127.0.0.1 only; no production server, subscriber data,
or archival CDN request. Negative control demonstrates the pre-fix egress.
"""
import importlib.util
from pathlib import Path
import unittest

p=Path(__file__).resolve().parents[1]/'tools'/'experience-2'/'verify_ex2_media_bytes.py'
spec=importlib.util.spec_from_file_location('ex2bytes',p)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class TestRealRedirectEgress(unittest.TestCase):
    """Local HTTP servers prove no second network request is made.

    The fixture uses only 127.0.0.1 and never contacts WordPress or offsite hosts.
    """

    def test_redirect_destination_never_requested(self):
        from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
        from threading import Thread
        from urllib.request import Request, urlopen
        hits = []
        code = [302]
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                hits.append(self.path)
                if self.path == '/origin':
                    self.send_response(code[0])
                    self.send_header('Location', '/unapproved-second-request')
                    self.end_headers()
                else:
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b'not-an-archival-image')
            def log_message(self,*args):
                pass
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        thread=Thread(target=server.serve_forever,daemon=True)
        thread.start()
        try:
            origin=f'http://127.0.0.1:{server.server_port}/origin'
            # Reproduced old behavior: urllib default follows Location, making
            # a second request before inspect() would inspect geturl().
            with urlopen(origin,timeout=3) as response:
                self.assertEqual(response.read(),b'not-an-archival-image')
            self.assertEqual(hits,['/origin','/unapproved-second-request'])
            for status in (301,302,303,307,308):
                with self.subTest(status=status):
                    hits.clear()
                    code[0]=status
                    with self.assertRaises(m.GateFailure):
                        m.first_party_open(Request(origin),timeout=3)
                    self.assertEqual(hits,['/origin'])
        finally:
            server.shutdown()
            server.server_close()

    def test_default_inspect_uses_no_follow_opener(self):
        from unittest.mock import patch
        row=m.MEDIA[0]
        # This confirms the default path is the guarded opener, not urllib.urlopen.
        with patch.object(m,'first_party_open',side_effect=m.GateFailure('stopped before redirect')) as protected:
            with self.assertRaises(m.GateFailure):
                m.inspect(row)
            self.assertEqual(protected.call_count,1)

if __name__=='__main__':unittest.main()
