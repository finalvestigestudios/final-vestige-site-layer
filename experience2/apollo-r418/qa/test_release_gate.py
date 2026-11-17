import unittest
from release_gate import evaluate

class ReleaseHardHold(unittest.TestCase):
    def test_empty_evidence(self):
        result=evaluate({})
        self.assertEqual(result['decision'],'HOLD')
        self.assertFalse(result['release_permitted'])
        self.assertGreater(len(result['blockers']),5)

    def test_self_reported_pass_is_never_real_approval(self):
        forged={
            'installed_wordpress_staging_url':'https://staging.example/',
            'navigated_playwright':True,'axe_core_violations':0,'lcp_ms':890,'cls':0.01,
            'keyboard_screenreader_review':True,'independent_qd_approval':True,
            'exact_head_ci_green':True,'founder_release_authorization':True,
        }
        result=evaluate(forged)
        self.assertEqual(result['decision'],'HOLD')
        self.assertIn('offline acceptance cannot authenticate founder, QD or exact-head CI status', result['blockers'])

    def test_wrong_metrics_hold(self):
        for data in ({'lcp_ms':3000,'cls':0.5,'axe_core_violations':5},
                     {'lcp_ms':'500','cls':'0.01','axe_core_violations':False}):
            result=evaluate(data)
            self.assertEqual(result['decision'],'HOLD')
            self.assertFalse(result['release_permitted'])

if __name__=='__main__':unittest.main(verbosity=2)
