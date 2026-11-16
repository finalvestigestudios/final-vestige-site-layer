#!/usr/bin/env python3
"""Fail-closed dependency and loopback server tests independent of browser."""
from pathlib import Path
import tempfile
import unittest
from http_server import git_blob, verified_source, LocalFixture, GIT_SHAS
from urllib.request import urlopen
from urllib.error import HTTPError

class SourceGuard(unittest.TestCase):
 def test_git_blob_vectors(self):
  self.assertEqual(git_blob(b'hello\n'),'ce013625030ba8dba906f756967f9e9ca394464a')
 def test_exact_immutable_r411_dependencies(self):
  html,css=verified_source()
  self.assertIn(b'data-fv-r411-sources',html)
  self.assertIn(b'/assets/source-drawer.css',html)
  self.assertIn(b'.fv-r411{',css)
  self.assertEqual(len(GIT_SHAS),3)
 def test_real_loopback_http_headers_and_denial(self):
  with LocalFixture() as srv:
   with urlopen(srv.base_url+'/apollo-r411/') as r:
    self.assertEqual(r.status,200)
    self.assertIn("script-src 'none'",r.headers.get('Content-Security-Policy',''))
   with urlopen(srv.base_url+'/assets/source-drawer.css') as r:
    self.assertEqual(r.status,200)
    self.assertIn('text/css',r.headers.get('Content-Type',''))
   with self.assertRaises(HTTPError) as err: urlopen(srv.base_url+'/qa/http_server.py')
   self.assertEqual(err.exception.code,404)
if __name__=='__main__':unittest.main(verbosity=2)
