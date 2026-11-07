"""Local mock-host negative controls for the EX2 WordPress launch admission.

HTTP fakes exercise preflight only. They never constitute WordPress acceptance.
"""
import importlib.util
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import socket
import threading
from unittest import TestCase, main
from unittest.mock import Mock

SPEC = importlib.util.spec_from_file_location('runner', Path(__file__).with_name('run_local_wordpress_acceptance.py'))
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


class Fixture(BaseHTTPRequestHandler):
    rest_payload = None
    home_html = '<html><div class="wp-site-blocks" data-fv-home-flagship>fixture</div></html>'
    paths = []
    rest_type = 'application/json; charset=UTF-8'
    rest_code = 200

    def do_GET(self):
        type(self).paths.append(self.path)
        if self.path == '/':
            body = type(self).home_html.encode()
            self.send_response(200)
            self.send_header('Content-Type','text/html; charset=UTF-8')
        elif self.path == '/wp-json/':
            if type(self).rest_code == 302:
                self.send_response(302)
                self.send_header('Location','https://finalvestige.com/')
                self.end_headers()
                return
            body = type(self).rest_payload
            body = json.dumps(body).encode() if not isinstance(body, bytes) else body
            self.send_response(type(self).rest_code)
            self.send_header('Content-Type',type(self).rest_type)
        else:
            self.send_response(404)
            self.end_headers()
            return
        self.send_header('Content-Length',str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self,*args):
        pass


class Server:
    def __enter__(self):
        self.http = ThreadingHTTPServer(('127.0.0.1',0),Fixture)
        self.thread = threading.Thread(target=self.http.serve_forever,daemon=True)
        self.thread.start()
        self.url = f'http://127.0.0.1:{self.http.server_port}/'
        Fixture.rest_payload = {'name':'FV Fixture','url':self.url.rstrip('/'), 'namespaces':['wp/v2','oembed/1.0']}
        Fixture.home_html = '<html><div class="wp-site-blocks" data-fv-home-flagship>fixture</div></html>'
        Fixture.rest_code = 200
        Fixture.rest_type = 'application/json; charset=UTF-8'
        Fixture.paths = []
        return self

    def __exit__(self,*args):
        self.http.shutdown()
        self.http.server_close()
        self.thread.join(timeout=2)


class NativeIdentityGate(TestCase):
    def assertNotReady(self, server):
        with self.assertRaises(TimeoutError):
            runner.ready(server.url,0.15,Mock(poll=lambda:None))

    def test_no_other_listener_allowed(self):
        with Server() as s:
            with self.assertRaisesRegex(RuntimeError,'REVIEW_PORT_ALREADY_IN_USE'):
                runner.refuse_occupied_port(s.http.server_port)

    def test_vacant_port_allowed(self):
        with socket.socket() as sock:
            sock.bind(('127.0.0.1',0))
            port=sock.getsockname()[1]
        runner.refuse_occupied_port(port)

    def test_fake_html_alone_fails(self):
        with Server() as s:
            Fixture.rest_payload={'not':'wordpress'}
            self.assertNotReady(s)
            self.assertEqual(Fixture.paths[:2],['/','/wp-json/'])

    def test_rest_wrong_site_url_fails(self):
        with Server() as s:
            Fixture.rest_payload['url']='https://finalvestige.com'
            self.assertNotReady(s)

    def test_rest_missing_namespace_fails(self):
        with Server() as s:
            Fixture.rest_payload['namespaces']=['oembed/1.0']
            self.assertNotReady(s)

    def test_rest_redirect_to_production_fails_closed(self):
        with Server() as s:
            Fixture.rest_code=302
            self.assertNotReady(s)
            self.assertNotIn('/wp-admin/', Fixture.paths)

    def test_rest_wrong_mime_fails(self):
        with Server() as s:
            Fixture.rest_type='text/html'
            self.assertNotReady(s)

    def test_rest_invalid_json_fails(self):
        with Server() as s:
            Fixture.rest_payload=b'not json'
            self.assertNotReady(s)

    def test_nonstring_rest_url_fails_gracefully(self):
        with Server() as s:
            Fixture.rest_payload['url']=None
            self.assertNotReady(s)

    def test_missing_source_root_fails(self):
        with Server() as s:
            Fixture.home_html='<main>WordPress mock (no flagship)</main>'
            self.assertNotReady(s)
            self.assertEqual(Fixture.paths,['/'])

    def test_well_formed_fixture_returns_but_not_wp_certification(self):
        with Server() as s:
            result=runner.ready(s.url,1,Mock(poll=lambda:None))
            self.assertTrue(result['wordpress_rest_api'])
            self.assertTrue(result['local_site_url_matched'])
            self.assertTrue(result['flagship_root_detected'])
            # This proves only the guard's behavior with a synthetic HTTP fixture.
            self.assertEqual(Fixture.paths,['/','/wp-json/'])

    def test_nonloopback_rejected_without_http(self):
        for url in ['https://finalvestige.com/','http://localho.st/','http://127.0.0.1:9400/other']:
            with self.assertRaises(ValueError):
                runner.ready(url,1,Mock(poll=lambda:None))


if __name__ == '__main__':
    main(verbosity=2)
