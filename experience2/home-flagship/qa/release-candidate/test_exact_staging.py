"""Offline admission tests. No claim of a real WordPress staging site."""
import hashlib
from pathlib import Path
import subprocess
import tempfile
import unittest
import verify_exact_staging as gate

class GateTests(unittest.TestCase):
    def test_production_is_denied_even_if_allowlisted(self):
        for domain in ('finalvestige.com','www.finalvestige.com'):
            with self.assertRaisesRegex(ValueError,'never production'):
                gate.check_url('https://'+domain+'/',domain)
    def test_unauthorized_host_is_denied(self):
        with self.assertRaises(ValueError):
            gate.check_url('https://unexpected.example/', 'staging.example')
    def test_nonlocal_http_is_denied(self):
        with self.assertRaisesRegex(ValueError,'HTTPS'):
            gate.check_url('http://staging.example/','staging.example')
    def test_credentials_and_nonces_are_denied(self):
        for url in ('https://staging.example/?_wpnonce=secret',
                    'https://user:pass@staging.example/private/',
                    'https://staging.example/#token'):
            with self.assertRaisesRegex(ValueError,'credentials'):
                gate.check_url(url,'staging.example')
    def test_explicit_staging_host(self):
        self.assertEqual(gate.check_url('https://private.wpcomstaging.com/preview/','private.wpcomstaging.com'),
                         'private.wpcomstaging.com')
        self.assertEqual(gate.check_url('http://127.0.0.1:8044/preview/','127.0.0.1'), '127.0.0.1')
    def test_local_wordpress_query_permalink_is_allowed_only_for_review_page(self):
        for host in ('127.0.0.1','localhost'):
            url='http://'+host+':9400/?pagename=fv-ex2-playground-review'
            self.assertEqual(gate.check_url(url,host),host)
        for url,allow in (
            ('https://staging.example/?pagename=fv-ex2-playground-review','staging.example'),
            ('http://127.0.0.1:9400/?pagename=home','127.0.0.1'),
            ('http://127.0.0.1:9400/?pagename=fv-ex2-playground-review&_wpnonce=evil','127.0.0.1'),
            ('http://127.0.0.1:9400/?pagename=fv-ex2-playground-review#token','127.0.0.1'),
            ('http://127.0.0.1:9400/other?pagename=fv-ex2-playground-review','127.0.0.1'),
        ):
            with self.subTest(url=url),self.assertRaises(ValueError):
                gate.check_url(url,allow)
    def test_margins_preservation_positive(self):
        src=''.join(f'<span class="fv-margin-strip__item" style="--i:{i}">note</span>' for i in range(72))
        src += '<a href="/focus/">Seven Day Focus Fieldbook</a><!-- wp:jetpack/subscriptions /-->'
        self.assertTrue(all([v for k,v in gate.margins_contract(src).items() if k in ('present','focus_fieldbook','jetpack_signup')]))
    def test_margins_deletion_fails(self):
        src=''.join(f'<span class="fv-margin-strip__item" style="--i:{i}">note</span>' for i in range(71))
        self.assertFalse(gate.margins_contract(src)['present'])
    def test_duplicate_margin_fails(self):
        src=''.join(f'<span class="fv-margin-strip__item" style="--i:{i%71}">note</span>' for i in range(72))
        self.assertFalse(gate.margins_contract(src)['present'])
    def test_sha_measures_bytes(self):
        self.assertEqual(gate.sha(b'abc'),hashlib.sha256(b'abc').hexdigest())
    def test_missing_or_modified_checkout_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            repo=Path(td)
            def run(*args):
                r=subprocess.run(['git','-C',td,*args],capture_output=True,text=True)
                self.assertEqual(r.returncode,0,r.stderr)
                return r.stdout.strip()
            run('init','-q');run('config','user.email','qa@example.invalid');run('config','user.name','QA')
            d=repo/gate.HOME;d.mkdir(parents=True)
            for name in ('index.html',)+gate.STYLES+gate.SCRIPTS:
                (d/name).write_text('original '+name)
            # The current exact-stage gate also attests its OWN QA source files.
            q=d/'qa'/'release-candidate';q.mkdir(parents=True)
            for name in ('verify_exact_staging.py','media_transfer_admission.py',
                         'test_media_transfer_admission.py','test_exact_staging.py'):
                (q/name).write_text('committed QA fixture '+name)
            run('add','.');run('commit','-qm','fixture')
            head=run('rev-parse','HEAD')
            _,assets=gate.checkout(repo,head)
            self.assertEqual(len(assets),11)
            with self.assertRaisesRegex(ValueError,'does not equal'):
                gate.checkout(repo,'0'*40)
            (d/'flagship.css').write_text('uncommitted')
            with self.assertRaisesRegex(ValueError,'uncommitted'):
                gate.checkout(repo,head)
            (d/'flagship.css').write_text('original flagship.css')
            (q/'media_transfer_admission.py').write_text('modified verifier')
            with self.assertRaisesRegex(ValueError,'modified staging QA code'):
                gate.checkout(repo,head)
    def test_no_staging_means_fail_closed_receipt(self):
        with self.assertRaises(ValueError):
            gate.check_url('https://finalvestige.com/','finalvestige.com')

if __name__=='__main__':unittest.main()
