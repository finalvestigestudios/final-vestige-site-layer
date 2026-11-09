import unittest
from destination_audit import review_url, commercial_hold, PUBLISHED, EDITORIAL_CTA

SOCIAL = 'https://finalvestige.com/focus/?utm_source=youtube&utm_medium=organic_social&utm_campaign=perception_pilot&utm_content=asset_realshape001'
def email(i, path):
    return 'https://finalvestige.com'+path+f'?utm_source=dispatch&utm_medium=email&utm_campaign=pilot_2026&utm_content=issue_{i:02d}'

class TestDestinationAudit(unittest.TestCase):
    def test_observed_six_published_route_ids(self):
        self.assertEqual(len(PUBLISHED), 6)
        self.assertEqual(PUBLISHED['/focus/'], 1579)
    def test_accept_social_public_focus(self):
        result=review_url(SOCIAL,'grok')
        self.assertTrue(result['syntactically_allowed'])
        self.assertFalse(result['send_authorized'])
        self.assertIsNone(result['actual_paid_order'])
        self.assertFalse(result['actual_asset_authenticated'])
    def test_accept_each_editorial_issue(self):
        for i,path in EDITORIAL_CTA.items():
            with self.subTest(issue=i):
                self.assertEqual(review_url(email(i,path),'dispatch',i)['path'],path)
    def test_unpublished_guides_must_not_pass(self):
        for issue, path in ((3,'/mind/zen12-guide/'),(5,'/mind/hypnosis-live-guide/')):
            with self.subTest(issue=issue),self.assertRaises(ValueError):
                review_url(email(issue,path),'dispatch',issue)
    def test_fake_valid_live_route_cannot_bypass_commercial_hold(self):
        for i in (3,5):
            with self.subTest(issue=i),self.assertRaises(ValueError):
                review_url(email(i,'/focus/'),'dispatch',i)
    def test_commercial_hold_never_authorizes(self):
        for i in (3,5):
            h=commercial_hold(i)
            self.assertFalse(h['newsletter_send_authorized'])
            self.assertIsNone(h['paid_revenue'])
            self.assertFalse(h['affiliate_email_permission_verified'])
    def test_email_subject_issue_must_match_cta(self):
        with self.assertRaises(ValueError):
            review_url(email(1,'/focus/'),'dispatch',1)
        with self.assertRaises(ValueError):
            review_url(email(1,EDITORIAL_CTA[1]).replace('issue_01','issue_02'),'dispatch',1)
    def test_path_traversal_and_encoded(self):
        for path in ('/wp-admin/','/wp-login.php','/mind/zen12-guide/','/../focus/','/%2Ffocus/','/dispa%74ch/','/foo//bar/','/./focus/'):
            with self.subTest(path=path),self.assertRaises(ValueError):
                review_url(SOCIAL.replace('/focus/',path),'grok')
    def test_no_forgeries_in_queries(self):
        for u in (SOCIAL+'&utm_source=tiktok', SOCIAL.replace('asset_realshape001','user@example.com'), SOCIAL.replace('utm_source=youtube','utm_source=dispatch'), SOCIAL.replace('perception_pilot',''), SOCIAL.replace('asset_realshape001','item')):
            with self.subTest(url=u),self.assertRaises(ValueError):review_url(u,'grok')
    def test_domain_and_url_variants(self):
        for u in (SOCIAL.replace('https://','http://'),SOCIAL.replace('finalvestige.com','finalvestige.com.evil.net'),SOCIAL.replace('/focus/','/focus/#frag'),SOCIAL.replace('finalvestige.com','finalvestige.com:443')):
            with self.subTest(url=u),self.assertRaises(ValueError):review_url(u,'grok')
    def test_email_grok_not_interchangeable(self):
        with self.assertRaises(ValueError):review_url(SOCIAL,'dispatch',1)
        with self.assertRaises(ValueError):review_url(email(1,EDITORIAL_CTA[1]),'grok')
    def test_bool_issue_not_int(self):
        with self.assertRaises(ValueError):review_url(email(1,EDITORIAL_CTA[1]),'dispatch',True)
    def test_no_tracking_customers(self):
        for u in (SOCIAL+'&email=test@a.com',SOCIAL.replace('utm_content','email'),SOCIAL.replace('asset_realshape001','asset_test%40a.com')):
            with self.subTest(url=u),self.assertRaises(ValueError):review_url(u,'grok')
    def test_invalid_commercial_hold_argument(self):
        for i in (0,1,6,True):
            with self.subTest(issue=i),self.assertRaises(ValueError):commercial_hold(i)

if __name__=='__main__':unittest.main()
