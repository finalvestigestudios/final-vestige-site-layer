"""Offline adversarial tests: synthetic responses; NO live source or rights claim."""
import hashlib
from io import BytesIO
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

import acquire_private_stage_inputs as m


def theme_bytes():
    buf = BytesIO()
    with zipfile.ZipFile(buf, 'w') as z:
        z.writestr('assembler/style.css', '/*\nTheme Name: Assembler\n*/')
        z.writestr('assembler/theme.json', '{}')
        z.writestr('assembler/templates/index.html', '<!-- wp:post-content /-->')
    return buf.getvalue()


class FakeResponse:
    def __init__(self, url, data, mime, *, status=200, destination=None, length=True):
        self.status = status
        self.url = destination or url
        self.body = BytesIO(data)
        self.headers = {'Content-Type': mime}
        if length:
            self.headers['Content-Length'] = str(len(data))
    def geturl(self): return self.url
    def read(self, n): return self.body.read(n)
    def __enter__(self): return self
    def __exit__(self, *args): self.body.close()


class FakeOpener:
    def __init__(self, alterations=None):
        self.alterations = alterations or {}
        self.urls = []
    def open(self, req, timeout):
        u = req.full_url
        self.urls.append(u)
        name = next((k for k, (v, _) in m.MEDIA_SOURCES.items() if v == u), 'theme')
        if name == 'theme':
            raw, mime = theme_bytes(), 'application/zip'
        elif name.endswith('.webp'):
            raw, mime = b'RIFF' + b'\0'*4 + b'WEBP' + b'\0'*(m.MEDIA_SOURCES[name][1]-12), 'image/webp'
        else:
            raw, mime = b'\xff\xd8\xff' + b'\0'*(m.MEDIA_SOURCES[name][1]-3), 'image/jpeg'
        changes = self.alterations.get(name, {})
        return FakeResponse(u, changes.get('data', raw), changes.get('mime', mime),
                            status=changes.get('status', 200),
                            destination=changes.get('destination'), length=changes.get('length', True))


class SourceCustodyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.root.chmod(0o700)
    def tearDown(self): self.tmp.cleanup()

    def test_fully_quarantines_only_four_known_sources(self):
        opener = FakeOpener()
        receipt = m.stage_candidates(self.root, opener=opener)
        self.assertEqual(receipt['status'], 'UNREVIEWED_CANDIDATES_NOT_RELEASE_ADMITTED')
        self.assertEqual(opener.urls, [m.THEME_URL] + [v[0] for v in m.MEDIA_SOURCES.values()])
        target = self.root/'fv-source-quarantine'
        data = json.loads((target/'UNREVIEWED_SOURCE_CANDIDATES.json').read_text())
        self.assertFalse(data['rights_cleared'])
        self.assertFalse(data['sha_independently_approved'])
        self.assertEqual(set(data['images']), set(m.MEDIA_SOURCES))
        for name, x in data['images'].items():
            self.assertEqual(hashlib.sha256((target/'media'/name).read_bytes()).hexdigest(), x['sha256'])
            self.assertEqual((target/'media'/name).stat().st_mode & 0o077, 0)
        with self.assertRaisesRegex(Exception, 'overwrite'):
            m.stage_candidates(self.root, opener=FakeOpener())

    def test_refuses_short_image_and_no_output(self):
        with self.assertRaisesRegex(Exception, 'byte-length mismatch'):
            m.stage_candidates(self.root, opener=FakeOpener({'apollo.webp':{'data':b'RIFF1234WEBP'}}))
        self.assertFalse((self.root/'fv-source-quarantine').exists())

    def test_refuses_wrong_media_mime(self):
        with self.assertRaisesRegex(Exception, 'unexpected WebP'):
            m.stage_candidates(self.root, opener=FakeOpener({'apollo.webp':{'mime':'image/jpeg'}}))

    def test_refuses_redirect(self):
        with self.assertRaisesRegex(Exception, 'redirect'):
            m.stage_candidates(self.root, opener=FakeOpener({'theme':{'destination':'https://evil.example/theme.zip'}}))

    def test_refuses_html_error(self):
        with self.assertRaisesRegex(Exception, 'MIME'):
            m.stage_candidates(self.root, opener=FakeOpener({'theme':{'mime':'text/html'}}))

    def test_refuses_non_200(self):
        with self.assertRaisesRegex(Exception, 'non-200'):
            m.stage_candidates(self.root, opener=FakeOpener({'theme':{'status':403}}))

    def test_refuses_unapproved_scheme_host(self):
        for url in ['http://finalvestige.com/p.jpg','https://evil.example/p.jpg',
                    'https://user:password@finalvestige.com/p.jpg']:
            with self.assertRaisesRegex(Exception, 'unapproved'):
                m.fetch_binary(url, 200, opener=FakeOpener())

    def test_refuses_oversized_theme(self):
        with self.assertRaisesRegex(Exception, 'transfer size'):
            m.stage_candidates(self.root, opener=FakeOpener({'theme':{'data':b'\0'*(m.MAX_THEME_BYTES+1)}}))

    def test_refuses_world_readable_workspace(self):
        self.root.chmod(0o755)
        with self.assertRaisesRegex(Exception, 'chmod 700'):
            m.stage_candidates(self.root, opener=FakeOpener())

    def test_refuses_corrupt_theme_zip(self):
        with self.assertRaises(Exception):
            m.stage_candidates(self.root, opener=FakeOpener({'theme':{'data':b'not zip'}}))

    def test_no_network_after_fetch_error(self):
        fake=FakeOpener({'franklin.jpg':{'mime':'text/html'}})
        with self.assertRaises(Exception):m.stage_candidates(self.root, opener=fake)
        self.assertEqual(len(fake.urls), 3)
        self.assertFalse((self.root/'fv-source-quarantine').exists())


if __name__=='__main__': unittest.main()
