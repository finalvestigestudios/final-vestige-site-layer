"""R293 offline synthetic regression tests; no network, CMS, commerce, or source writes."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location("prep_r293",ROOT/"tools/r293_branch_head_drift_hold.py")
g=importlib.util.module_from_spec(s);s.loader.exec_module(g)
def fixture():
 return json.loads((ROOT/"audits/r293_live_contributor_branch_crosswalk_UNAPPROVED.json").read_text())
class Tests(unittest.TestCase):
 def test_current_snapshot_holds(self):
  r=g.evaluate(fixture());self.assertEqual(r["state"],g.HOLD)
  self.assertEqual(r["drifted_clusters"],["food","health","hist-field","hist-food","hist-home"])
  self.assertEqual(r["changed_file_count"],23)
  self.assertEqual(len(r["affected_article_slugs"]),7)
 def test_does_not_authorize(self):
  r=g.evaluate(fixture())
  for k in ("publication_authorized","independent_qd_pass","medical_safety_verified",
            "privacy_approved","github_currentness_verified","full_native_build_verified"):
   self.assertIs(r[k],False)
 def test_missing_repo_fails_closed(self):
  with tempfile.TemporaryDirectory() as t:self.assertEqual(g.audit(t)["state"],g.INVALID)
 def test_unchanged_branches_still_hold(self):
  x=fixture()
  for r in x["clusters"].values():
   r.update(head=r["frozen"],status="identical",ahead=0,behind=0,paths=[])
  self.assertEqual(g.evaluate(x)["state"],g.HOLD)
  self.assertFalse(g.evaluate(x)["publication_authorized"])
 def test_invalid_json_duplicate_key(self):
  with self.assertRaises(ValueError):g.load('{"a":1,"a":2}')
 def test_nonfinite_json(self):
  with self.assertRaises(ValueError):g.load('{"a":NaN}')
 def test_source_readonly(self):
  before=(ROOT/"audits/r293_live_contributor_branch_crosswalk_UNAPPROVED.json").read_bytes()
  g.evaluate(fixture())
  self.assertEqual(before,(ROOT/"audits/r293_live_contributor_branch_crosswalk_UNAPPROVED.json").read_bytes())
def invalid(label,edit):
 def test(self):
  x=fixture();edit(x)
  with self.assertRaises((ValueError,KeyError,TypeError),msg=label):g.evaluate(x)
 test.__name__="test_adversarial_"+label
 return test
M={
 "schema":lambda x:x.update(schema="unrecognized"),
 "repo":lambda x:x.update(repository="unknown/repo"),
 "timestamp":lambda x:x.update(captured_on_utc="yesterday"),
 "missing_cluster":lambda x:x["clusters"].pop("start"),
 "added_cluster":lambda x:x["clusters"].update(rogue={}),
 "clusters_list":lambda x:x.update(clusters=[]),
 "root_approval_flag":lambda x:x.update(publication_authorized=True),
 "false_frozen":lambda x:x["clusters"]["food"].update(frozen="0"*40),
 "wrong_branch":lambda x:x["clusters"]["food"].update(branch="other/branch"),
 "short_head":lambda x:x["clusters"]["food"].update(head="abc"),
 "nonhex_head":lambda x:x["clusters"]["food"].update(head="g"*40),
 "negative_ahead":lambda x:x["clusters"]["food"].update(ahead=-1),
 "negative_behind":lambda x:x["clusters"]["food"].update(behind=-1),
 "bool_ahead":lambda x:x["clusters"]["food"].update(ahead=True),
 "float_ahead":lambda x:x["clusters"]["food"].update(ahead=1.0),
 "excessive_ahead":lambda x:x["clusters"]["food"].update(ahead=101),
 "unknown_status":lambda x:x["clusters"]["food"].update(status="published"),
 "false_identical":lambda x:x["clusters"]["food"].update(status="identical"),
 "false_behind":lambda x:x["clusters"]["food"].update(status="behind"),
 "false_ahead":lambda x:x["clusters"]["food"].update(status="ahead"),
 "false_diverged":lambda x:x["clusters"]["health"].update(status="diverged"),
 "identical_with_delta":lambda x:x["clusters"]["start"].update(paths=["preparedness/docs/changed.md"]),
 "identical_with_sha_drift":lambda x:x["clusters"]["start"].update(head="0"*40),
 "drift_without_paths":lambda x:x["clusters"]["food"].update(paths=[]),
 "duplicate_path":lambda x:x["clusters"]["food"]["paths"].append(x["clusters"]["food"]["paths"][0]),
 "escape_path":lambda x:x["clusters"]["food"]["paths"].__setitem__(0,"preparedness/../secret/bad"),
 "outside_repo":lambda x:x["clusters"]["food"]["paths"].__setitem__(0,"other/secret/data"),
 "path_percent":lambda x:x["clusters"]["food"]["paths"].__setitem__(0,"preparedness/%2e%2e/data"),
 "path_backslash":lambda x:x["clusters"]["food"]["paths"].__setitem__(0,"preparedness\\foo\\bar"),
 "path_short":lambda x:x["clusters"]["food"]["paths"].__setitem__(0,"preparedness/file"),
 "path_long":lambda x:x["clusters"]["food"]["paths"].__setitem__(0,"preparedness/docs/"+"x"*260),
 "path_number":lambda x:x["clusters"]["food"]["paths"].__setitem__(0,42),
 "path_none":lambda x:x["clusters"]["food"]["paths"].__setitem__(0,None),
 "paths_not_list":lambda x:x["clusters"]["food"].update(paths=None),
 "extra_cluster_key":lambda x:x["clusters"]["food"].update(review_approved=True),
 "missing_cluster_key":lambda x:x["clusters"]["food"].pop("frozen"),
 "extra_root_key":lambda x:x.update(merchant_ready=True),
 "missing_root_key":lambda x:x.pop("repository"),
 "bool_behind":lambda x:x["clusters"]["food"].update(behind=True),
 "zero_ahead":lambda x:x["clusters"]["food"].update(ahead=0),
 "zero_behind":lambda x:x["clusters"]["food"].update(behind=0),
}
for name,edit in M.items():setattr(Tests,"test_adversarial_"+name,invalid(name,edit))
if __name__=="__main__":unittest.main()
