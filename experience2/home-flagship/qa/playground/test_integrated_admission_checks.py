#!/usr/bin/env python3
"""Adversarial, network-free admission regressions. Run with python -m unittest."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from integrated_admission_checks import (
    AdmissionClosed, MEDIA, read_trusted_media_manifest, validate_stage_url,
    verify_integrated_dom, verify_media_payload)

class IntegratedAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.good=dict(main=1,h1=1,links=7,panels=3,flagship_roots=1,legacy_hero=0,
                       dev_controls=0,margins=72,focus_links=2,
                       body_classes=['home','page','wp-theme-assembler'],sw=390,cw=390)

    def test_local_and_playground_allowlist(self):
        for u in ['http://127.0.0.1:8080/','http://localhost:8080/',
                  'http://[::1]:8080/','http://wp.localhost/',
                  'https://playground.wordpress.net/']:
            self.assertTrue(validate_stage_url(u))

    def test_public_production_credentials_and_non_http_closed(self):
        for u in ['https://finalvestige.com/','https://www.finalvestige.com/',
                  'https://finalvestige.com.evil.example/','http://example.com/',
                  'https://google.com/','ftp://localhost/','http://admin:pw@localhost/',
                  'http://localhost/?preview=1','http://localhost/#s']:
            with self.subTest(url=u), self.assertRaises(AdmissionClosed):
                validate_stage_url(u)

    def test_named_host_requires_exact_https(self):
        self.assertEqual(validate_stage_url('https://stage.review.example/','stage.review.example'),
                         'stage.review.example')
        for u in ['http://stage.review.example/','https://other.review.example/']:
            with self.assertRaises(AdmissionClosed):
                validate_stage_url(u,'stage.review.example')

    def test_integrated_wordpress_dom_positive(self):
        self.assertTrue(verify_integrated_dom(self.good))

    def test_legacy_72_focus_and_dev_controls_negative(self):
        for k,v in [('margins',71),('focus_links',1),('legacy_hero',1),
                    ('flagship_roots',2),('dev_controls',1)]:
            with self.subTest(field=k), self.assertRaises(AdmissionClosed):
                verify_integrated_dom({**self.good,k:v})

    def test_non_wordpress_landmarks_and_overflow_negative(self):
        for variant in [{'body_classes':['home','page']},{'h1':2},{'main':2},
                        {'panels':2},{'links':6},{'sw':400}]:
            with self.subTest(changed=variant), self.assertRaises(AdmissionClosed):
                verify_integrated_dom({**self.good,**variant})

    def _manifest(self,folder,mutate=None):
        images={name:{'source_url':rec['source_url'],'bytes':rec['bytes'],
                      'sha256':'a'*64} for name,rec in MEDIA.items()}
        if mutate: mutate(images)
        f=folder/'trusted.json'
        f.write_text(json.dumps({'purpose':'isolated-staging-media-review','images':images}))
        return f

    def test_manifest_original_3_hash_schema(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertEqual(set(read_trusted_media_manifest(self._manifest(Path(t)))),set(MEDIA))

    def test_missing_altered_or_extra_media_manifest_closed(self):
        with tempfile.TemporaryDirectory() as t:
            d=Path(t)
            with self.assertRaises(AdmissionClosed):
                read_trusted_media_manifest(d/'absent.json')
            for change in [lambda m:m.pop('nypl.jpg'),
                           lambda m:m['apollo.webp'].update(bytes=0),
                           lambda m:m['franklin.jpg'].update(sha256='INVALID'),
                           lambda m:m['nypl.jpg'].update(source_url='https://wrong.test/image.jpg'),
                           lambda m:m.update(extra={})]:
                with self.assertRaises(AdmissionClosed):
                    read_trusted_media_manifest(self._manifest(d,change))

    def test_same_length_altered_bytes_closed(self):
        a=b'A'*MEDIA['apollo.webp']['bytes']; fake=b'B'+a[1:]
        sha=hashlib.sha256(a).hexdigest()
        self.assertEqual(verify_media_payload('apollo.webp',a,[1041,810],sha)['sha256'],sha)
        with self.assertRaises(AdmissionClosed):
            verify_media_payload('apollo.webp',fake,[1041,810],sha)

    def test_bad_size_dimensions_media_name_or_sha_closed(self):
        a=b'A'*MEDIA['apollo.webp']['bytes'];sha=hashlib.sha256(a).hexdigest()
        for args in [('apollo.webp',a[:-1],[1041,810],sha),
                     ('apollo.webp',a,[1041,811],sha),
                     ('forgery.jpg',a,[1041,810],sha),
                     ('apollo.webp',a,[1041,810],None)]:
            with self.assertRaises(AdmissionClosed):verify_media_payload(*args)

if __name__ == '__main__':
    unittest.main(verbosity=2)
