"""R76 native Python aggregate attribution regression and privacy tests."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
R76=ROOT/"r76-attribution-integrity"
spec=importlib.util.spec_from_file_location("r76metrics",R76/"metrics_contract.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class R76AttributionTests(unittest.TestCase):
 def setUp(self):self.d=json.loads((R76/"source_snapshot.json").read_text(encoding="utf-8"))
 def test_exact_authentic_traffic(self):
  self.assertEqual([x["views"] for x in self.d["periods"]],[287,795,32])
  self.assertEqual([x["visitors"] for x in self.d["periods"]],[18,17,6])
 def test_absolute_sitewide_change(self):
  r=m.assess(self.d);self.assertEqual(r["sitewide_view_change"],508);self.assertEqual(r["sitewide_visitor_change"],-1)
 def test_no_attribution_from_web_traffic(self):
  r=m.assess(self.d);self.assertTrue(all(v is None for v in r["newsletter_attribution"].values()))
 def test_partial_day_cannot_be_full_week(self):
  self.assertTrue(m.assess(self.d)["today_is_partial"])
 def test_no_fake_send_authorization(self):
  r=m.assess(self.d);self.assertFalse(r["send_allowed"]);self.assertEqual(r["state"],"HOLD_UNSENT")
 def test_commercial_holds_are_isolated(self):
  self.assertEqual(m.assess(self.d)["commercial_issues"],{"03":"HOLD_MERCHANT","05":"HOLD_MERCHANT"})
 def test_counters_are_not_four_people(self):
  r=m.assess(self.d);self.assertEqual(list(r["nonadditive_subscriber_counters"].values()),[2,2,2]);self.assertIsNone(r["email_eligible"])
 def test_zero_recent_sends_is_not_zero_opens(self):
  r=m.assess(self.d);self.assertEqual(r["recent_send_count"],0);self.assertIsNone(r["newsletter_attribution"]["email_opens"])
 def test_reject_email_input(self):
  self.d["subscriber_email"]="private@example.invalid"
  with self.assertRaises(m.InvalidEvidence):m.assess(self.d)
 def test_reject_bool_as_integer(self):
  self.d["periods"][0]["views"]=True
  with self.assertRaises(m.InvalidEvidence):m.assess(self.d)
 def test_reject_negative(self):
  self.d["newsletter"]["confirmed"]=-3
  with self.assertRaises(m.InvalidEvidence):m.assess(self.d)
 def test_reject_bad_dates(self):
  self.d["periods"][1]["start"]="2026-10-27"
  with self.assertRaises(m.InvalidEvidence):m.assess(self.d)
 def test_reject_partial_labeled_complete(self):
  self.d["periods"][2]["complete"]=True
  with self.assertRaises(m.InvalidEvidence):m.assess(self.d)
 def test_reject_other_merchant_slot(self):
  self.d["merchants"]["06"]=True
  with self.assertRaises(m.InvalidEvidence):m.assess(self.d)
 def test_html_is_noninteractive_and_accessible(self):
  h=m.html_report(m.assess(self.d)).lower()
  for x in ('lang="en"','<caption>','scope="col"','scope="row"','name="viewport"'):self.assertIn(x,h)
  for x in ("<script","<form","<iframe","href=","<img"):self.assertNotIn(x,h)
 def test_cli_outputs_are_redacted_and_hold(self):
  with tempfile.TemporaryDirectory() as folder:
   f=Path(folder)/"source.json";f.write_text(json.dumps(self.d),encoding="utf-8")
   target=Path(folder)/"reports"
   out=subprocess.run([sys.executable,str(R76/"metrics_contract.py"),"--input",str(f),"--output-dir",str(target)],capture_output=True,text=True,timeout=15)
   self.assertEqual(out.returncode,0,out.stderr);self.assertEqual(sorted(p.name for p in target.iterdir()),["report.html","report.json","report.txt"])
   self.assertFalse(json.loads((target/"report.json").read_text())["send_allowed"])
 def test_bad_input_does_not_echo_private_address(self):
  self.d["email"]="test@example.invalid"
  with tempfile.TemporaryDirectory() as folder:
   f=Path(folder)/"bad.json";f.write_text(json.dumps(self.d),encoding="utf-8")
   out=subprocess.run([sys.executable,str(R76/"metrics_contract.py"),"--input",str(f),"--output-dir",str(Path(folder)/"out")],capture_output=True,text=True,timeout=15)
   self.assertEqual(out.returncode,2);self.assertNotIn("example.invalid",out.stdout+out.stderr)
if __name__=="__main__":unittest.main()
