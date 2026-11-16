from unittest import TestCase
from release_gate import audit
class ReleaseGateTests(TestCase):
 def test_absence_of_metrics_and_axe_must_hard_hold(self):
  r=audit({'chromium_http_navigation':{'status':'BLOCKED_BY_RUNTIME_POLICY'},'metrics':[],'axe_core':{'status':'BLOCKED_NOT_INSTALLED_OR_VERIFIED'},'installed_wordpress':False})
  self.assertEqual(r['release'],'HOLD');self.assertGreaterEqual(len(r['blockers']),5)
 def test_local_metrics_alone_must_never_promote(self):
  r=audit({'chromium_http_navigation':{'status':'AVAILABLE'},'metrics':[{'lcp_ms':200.1,'cls':0}], 'axe_core':{'status':'EXECUTED','violations':[]},'installed_wordpress':False,'real_production_cwv':False})
  self.assertEqual(r['release'],'HOLD');self.assertIn('Installed WordPress/Assembler staging untested',r['blockers'])
