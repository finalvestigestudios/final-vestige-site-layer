#!/usr/bin/env python3
"""Deterministic adversarial tests: canonical URL is NOT proof of publication."""
from copy import deepcopy
from pathlib import Path
import importlib.util
import json
import unittest

P=Path(__file__).resolve().parent/'authenticity_guard.py'
spec=importlib.util.spec_from_file_location('fva',P);a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
TEMPLATE=Path(__file__).resolve().parents[2]/'apollo-r452/proof-template.json'
YT='https://www.youtube.com/watch?v=AaBbCcDd_12'
SHORT='https://www.youtube.com/shorts/AaBbCcDd_12'
TIKTOK='https://www.tiktok.com/@finalvestige/video/7312345678901234567'

class Gate(unittest.TestCase):
    def test_r452_pinned(self): self.assertEqual(a.verified_r452_guard().__name__,'apollo_r452_guard_verified')
    def test_baseline_hold(self):
        d=json.loads(TEMPLATE.read_text())
        self.assertEqual(a.assess(d)['status'],'HARD_HOLD')
        self.assertIsNone(a.assess(d)['realized_net_revenue_per_1000_qualified_sessions'])
    def test_allowed_youtube_url_shapes(self):
        for x in (YT,SHORT,'https://youtu.be/AaBbCcDd_12','https://youtube.com/live/AaBbCcDd_12'):
            with self.subTest(url=x):self.assertTrue(a.creator_video_url(x,'youtube'))
    def test_allowed_tiktok_shape(self):self.assertTrue(a.creator_video_url(TIKTOK,'tiktok'))
    def test_url_attacks(self):
        attacks=[
          ('https://www.youtube.com.evil.org/watch?v=AaBbCcDd_12','youtube'),
          ('https://www.youtube.com@evil.org/watch?v=AaBbCcDd_12','youtube'),
          ('http://www.youtube.com/watch?v=AaBbCcDd_12','youtube'),
          ('https://www.youtube.com:8443/watch?v=AaBbCcDd_12','youtube'),
          ('https://www.youtube.com/watch?v=AaBbCcDd_12&redirect=https://evil.org','youtube'),
          ('https://www.youtube.com/watch?v=AaBbCcDd_12&v=AaBbCcDd_12','youtube'),
          ('https://www.youtube.com/watch?v=AaBbCcDd_12#fragment','youtube'),
          ('https://www.youtube.com/watch?v=too_short','youtube'),
          ('https://www.youtube.com/watch?v=AaBbCcDd_12','tiktok'),
          ('https://youtu.be/AaBbCcDd_12/extra','youtube'),
          ('https://www.youtube.com/@account','youtube'),
          ('https://www.tiktok.com/@name/video/abc','tiktok'),
          ('https://www.tiktok.com/@name/video/7312345678901234567?x=1','tiktok'),
          ('https://www.tiktok.com/@name/video/7312345678901234567','youtube'),
          ('https://www.youtube.com/watch?v=AaBbCcDd_12%0a','youtube'),
          ('https://www.youtube.com/watch?v=AaBbCcDd_12\','youtube'),
          ('javascript:alert(1)','youtube'),
          ('https://www.youtube.com./watch?v=AaBbCcDd_12','youtube'),
          ('https://www.youtube.com/watch?url=https://evil.org','youtube'),
          ('https://m.youtube.com/shorts/AaBbCcDd_12?utm_source=unknown','youtube'),
        ]
        for url,platform in attacks:
            with self.subTest(url=url):self.assertFalse(a.creator_video_url(url,platform))
    def test_invalid_post_claim_rejected(self):
        d=json.loads(TEMPLATE.read_text())
        d['campaign'].update(publication_proof_status='INDEPENDENTLY_CONFIRMED',platform_post_url='https://evil.example/watch?v=AaBbCcDd_12',praxxis_review_ref='review-sample-00001',approved_landing_url=a.LANDING)
        with self.assertRaises(a.Hold):a.assess(d)
    def test_valid_post_shape_not_verified_as_published(self):
        d=json.loads(TEMPLATE.read_text())
        d['campaign'].update(publication_proof_status='INDEPENDENTLY_CONFIRMED',platform_post_url=YT,praxxis_review_ref='synthetic-ref-does-not-confirm',approved_landing_url=a.LANDING)
        r=a.assess(d)
        self.assertEqual(r['creator_url_shape'],'CANONICAL_SHAPE_ONLY_NOT_PUBLICATION_PROOF')
        self.assertFalse(r['publication_independently_verified_by_this_tool'])
        self.assertIsNone(r['realized_net_revenue_per_1000_qualified_sessions'])
    def test_commerce_cta_forbidden(self):
        d=json.loads(TEMPLATE.read_text());d['commercial_cta_enabled']=True
        with self.assertRaises(a.Hold):a.assess(d)
    def test_pii_forbidden_by_inherited_guard(self):
        d=json.loads(TEMPLATE.read_text());d['campaign']['customer_email']='x@example.com'
        with self.assertRaises(a.Hold):a.assess(d)
    def test_immutable_asset_id_mismatch_rejected(self):
        d=json.loads(TEMPLATE.read_text());d['campaign']['utm_content']='different999'
        with self.assertRaises(a.Hold):a.assess(d)
    def test_nonmatching_landing_rejected(self):
        d=json.loads(TEMPLATE.read_text());d['landing_url']='https://evil.org/'
        with self.assertRaises(a.Hold):a.assess(d)
    def test_creator_approval_cannot_enable_revenue(self):
        d=json.loads(TEMPLATE.read_text());d['campaign'].update(publication_proof_status='INDEPENDENTLY_CONFIRMED',platform_post_url=YT,praxxis_review_ref='synthetic-claim-only',approved_landing_url=a.LANDING)
        d['cohorts']=[]
        self.assertIsNone(a.assess(d)['realized_net_revenue_per_1000_qualified_sessions'])

if __name__=='__main__':unittest.main(verbosity=2)
