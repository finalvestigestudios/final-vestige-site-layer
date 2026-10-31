"""R18 synthetic/adversarial tests of the private preflight *orchestrator*.

No test accesses live GitHub, WordPress, public websites, or clinical sources.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import private_release_preflight as p

SHA = "a" * 40


def proc(out=b"", err=b"", code=0):
    return SimpleNamespace(stdout=out, stderr=err, returncode=code)


class FakeProcess:
    def __init__(self):
        self.calls = []
        self.head = SHA
        self.status = ""
        self.code = {}
        self.output = {}
        self.failure = None
        self.test_count = 49
        self.build_exists = True

    def __call__(self, cmd, **kwargs):
        self.calls.append((tuple(cmd), kwargs))
        if cmd[0] == "git":
            if "rev-parse" in cmd:
                return proc((self.head + "\n").encode())
            if "status" in cmd:
                return proc(self.status.encode())
            raise AssertionError(cmd)
        stage = Path(cmd[3]).name if len(cmd) > 3 and cmd[3].endswith(".py") else "<unittest>"
        if self.failure and stage == self.failure:
            raise subprocess.TimeoutExpired(cmd, timeout=1)
        if stage == "<unittest>":
            return proc(err=f"Ran {self.test_count} tests in 0.123s\n\nOK\n".encode(),
                        code=self.code.get(stage, 0))
        default = json.dumps({"release_state": "HOLD", "may_publish": False}).encode()
        return proc(self.output.get(stage, default), code=self.code.get(stage, 0))


class Fixture(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory(prefix="fv-r18-test-")
        self.addCleanup(t.cleanup)
        self.root = Path(t.name) / "repo"
        self.root.mkdir()
        (self.root / ".git").mkdir()
        base = self.root / "preparedness"
        for d in ("tools", "tests", "docs", "build"):
            (base / d).mkdir(parents=True)
        for _, script, kind in p.STEPS:
            if kind != "tests":
                (base / "tools" / script).write_text("# fixture\n", encoding="utf-8")
        (self.root / p.MANIFEST).write_text("{}\n", encoding="utf-8")
        self.fake = FakeProcess()

    def execute(self):
        return p.execute(self.root, SHA, run=self.fake)

    def assert_closed(self, thunk, match=None):
        with self.assertRaises(p.PreflightHold) as caught:
            thunk()
        if match:
            self.assertIn(match, str(caught.exception))

    def test_01_exact_twelve_steps(self):
        self.assertEqual(len(p.STEPS), 12)
        self.assertEqual(len(set(x[0] for x in p.STEPS)), 12)

    def test_02_success_is_still_release_hold(self):
        r = self.execute()
        self.assertEqual(r["release_state"], "HOLD")
        self.assertIs(r["may_publish"], False)

    def test_03_no_implicit_public_wordpress_writes(self):
        self.execute()
        self.assertTrue(all("wordpress" not in str(c[0]).lower() for c in self.fake.calls))

    def test_04_no_cmd_uses_shell_true(self):
        self.execute()
        self.assertTrue(all(c[1].get("shell") is not True for c in self.fake.calls))

    def test_05_python_isolation_for_every_gate(self):
        self.execute()
        self.assertTrue(all(c[0][1:3] == ("-I", "-B")
                            for c in self.fake.calls if c[0][0] == sys.executable))

    def test_06_all_steps_are_recorded(self):
        self.assertEqual([x["gate"] for x in self.execute()["steps"]],
                         [x[0] for x in p.STEPS])

    def test_07_native_tests_count_carried_forward(self):
        self.assertEqual(next(x for x in self.execute()["steps"]
                              if x["gate"] == "native_unit_suite")["native_test_count"],49)

    def test_08_machine_completion_does_not_imply_QD(self):
        r=self.execute()
        self.assertIs(r["independent_QD_approval"], False)
        self.assertIs(r["qualified_medical_or_emergency_safety_review"], False)

    def test_09_deterministic_receipt(self):
        self.assertEqual(self.execute(),self.execute())

    def test_10_receipt_cryptographic_hash(self):
        r=self.execute()
        c={k:v for k,v in r.items() if k!="fingerprint_sha256"}
        self.assertEqual(r["fingerprint_sha256"],p.sha256(p.canonical_json(c)))

    def test_11_source_checkout_not_modified(self):
        before=(self.root/p.MANIFEST).read_bytes()
        self.execute()
        self.assertEqual(before,(self.root/p.MANIFEST).read_bytes())

    def test_12_native_execution_occurs_in_checkout(self):
        self.execute()
        for cmd, kw in self.fake.calls:
            if cmd[0] == sys.executable:
                self.assertEqual(kw["cwd"],str(self.root))

    def test_13_pinned_branch_commit_supplied_to_parity(self):
        self.execute()
        call=[c for c,_ in self.fake.calls if "cluster_git_parity_gate.py" in str(c)]
        self.assertEqual(len(call),1)
        self.assertIn(SHA,call[0])

    def test_14_expected_manifest_path_supplied(self):
        self.execute()
        call=[c for c,_ in self.fake.calls if "cluster_git_parity_gate.py" in str(c)][0]
        self.assertIn(str(self.root/p.MANIFEST),call)

    def test_15_native_tests_use_unittest_discover(self):
        call=next(x for x in p.commands(self.root,SHA) if x.kind=="tests")
        self.assertIn("discover",call.command)
        self.assertIn("preparedness/tests",call.command)

    def test_16_refuse_dirty_preparedness_tree(self):
        self.fake.status="?? preparedness/content/articles/unsafe.body.html\n"
        self.assert_closed(self.execute,"dirty")

    def test_17_refuse_modified_source_file(self):
        self.fake.status=" M preparedness/sources/crosswalk.json\n"
        self.assert_closed(self.execute,"dirty")

    def test_18_refuse_wrong_checkout_sha(self):
        self.fake.head="b"*40
        self.assert_closed(self.execute,"HEAD drifted")

    def test_19_refuse_no_git_checkout(self):
        (self.root/".git").rmdir()
        self.assert_closed(self.execute,"trusted Git")

    def test_20_refuse_missing_manifest(self):
        (self.root/p.MANIFEST).unlink()
        self.assert_closed(self.execute,"manifest")

    def test_21_refuse_symlink_manifest(self):
        f=self.root/p.MANIFEST
        f.unlink()
        f.symlink_to(self.root/".git")
        self.assert_closed(self.execute,"manifest")

    def test_22_refuse_missing_test_directory(self):
        (self.root/"preparedness/tests").rmdir()
        self.assert_closed(self.execute,"native gate")

    def test_23_refuse_missing_gate_script(self):
        (self.root/"preparedness/tools/outbound_link_custody.py").unlink()
        self.assert_closed(self.execute,"outbound")

    def test_24_refuse_symlink_gate_script(self):
        f=self.root/"preparedness/tools/validate.py"
        f.unlink()
        f.symlink_to(self.root/".git")
        self.assert_closed(self.execute,"native gate")

    def test_25_refuse_symlinked_build_directory(self):
        (self.root/"preparedness/build").rmdir()
        (self.root/"preparedness/build").symlink_to(self.root/".git")
        self.assert_closed(self.execute,"symbolic link")

    def test_26_refuse_empty_head(self):
        self.assert_closed(lambda:p.commands(self.root,""),"40-hex")

    def test_27_refuse_short_head(self):
        self.assert_closed(lambda:p.commands(self.root,"b"*39),"40-hex")

    def test_28_refuse_sha_with_newline(self):
        self.assert_closed(lambda:p.commands(self.root,SHA+"\n"),"40-hex")

    def test_29_refuse_shell_injection_head(self):
        self.assert_closed(lambda:p.commands(self.root,"x;rm -rf /"),"40-hex")

    def test_30_refuse_nonnumeric_timeout(self):
        self.assert_closed(lambda:p.execute(self.root,SHA,run=self.fake,timeout="180"),"timeout")

    def test_31_refuse_unbounded_timeout(self):
        self.assert_closed(lambda:p.execute(self.root,SHA,run=self.fake,timeout=1201),"timeout")

    def test_32_refuse_zero_timeout(self):
        self.assert_closed(lambda:p.execute(self.root,SHA,run=self.fake,timeout=0),"timeout")

    def test_33_refuse_failed_validation(self):
        self.fake.code["validate.py"]=1
        self.assert_closed(self.execute,"native_validation")

    def test_34_refuse_failed_draft_build(self):
        self.fake.code["build.py"]=2
        self.assert_closed(self.execute,"private_draft_build")

    def test_35_refuse_failed_unit_suite(self):
        self.fake.code["<unittest>"]=3
        self.assert_closed(self.execute,"native_unit_suite")

    def test_36_refuse_test_suite_below_minimum(self):
        self.fake.test_count=35
        self.assert_closed(self.execute,"fewer than 36")

    def test_37_accept_36_tests_minimum(self):
        self.fake.test_count=36
        self.assertEqual(self.execute()["steps"][2]["native_test_count"],36)

    def test_38_refuse_missing_test_summary(self):
        self.assert_closed(lambda:p.verify_tests(b"",b"OK\n"),"count missing")

    def test_39_refuse_test_failure_with_reported_count(self):
        self.assert_closed(lambda:p.verify_tests(b"",b"Ran 50 tests in 0.1s\nFAILED\n"),"successful")

    def test_40_refuse_duplicate_test_summaries(self):
        self.assert_closed(lambda:p.verify_tests(b"",b"Ran 50 tests in 0.1s\nRan 50 tests in 0.1s\nOK\n"),"ambiguous")

    def test_41_refuse_nonjson_custody_gate(self):
        self.fake.output["source_crosswalk_truth_gate.py"]=b"not json"
        self.assert_closed(self.execute,"single valid JSON")

    def test_42_refuse_extra_json_after_hold(self):
        self.fake.output["source_crosswalk_truth_gate.py"]=b'{"release_state":"HOLD","may_publish":false}\n{}'
        self.assert_closed(self.execute,"single valid JSON")

    def test_43_refuse_approval_in_custody_gate(self):
        self.fake.output["source_crosswalk_truth_gate.py"]=b'{"release_state":"HOLD","may_publish":true}'
        self.assert_closed(self.execute,"non-HOLD")

    def test_44_refuse_wrong_release_state(self):
        self.fake.output["source_crosswalk_truth_gate.py"]=b'{"release_state":"PASS","may_publish":false}'
        self.assert_closed(self.execute,"non-HOLD")

    def test_45_refuse_missing_release_field(self):
        self.fake.output["source_crosswalk_truth_gate.py"]=b'{"may_publish":false}'
        self.assert_closed(self.execute,"non-HOLD")

    def test_46_refuse_misleading_independent_QD_bool(self):
        self.assert_closed(lambda:p.verify_hold_json(b'{"release_state":"HOLD","may_publish":false,"qualified_safety_clearance":true}'),"falsely asserted")

    def test_47_refuse_claim_accuracy_assertion(self):
        self.assert_closed(lambda:p.verify_hold_json(b'{"release_state":"HOLD","may_publish":false,"article_claim_accuracy_verified":true}'),"falsely asserted")

    def test_48_refuse_human_source_assertion(self):
        self.assert_closed(lambda:p.verify_hold_json(b'{"release_state":"HOLD","may_publish":false,"human_source_review_complete":true}'),"falsely asserted")

    def test_49_refuse_nan_in_json(self):
        self.assert_closed(lambda:p.verify_hold_json(b'{"release_state":"HOLD","may_publish":false,"value":NaN}'),"single valid JSON")

    def test_50_refuse_bom_or_invalid_utf8(self):
        self.assert_closed(lambda:p.verify_hold_json(b'\xff\xff'),"invalid UTF-8")

    def test_51_refuse_oversized_json(self):
        self.assert_closed(lambda:p.verify_hold_json(b"x"*4_000_001),"safe cap")

    def test_52_stop_without_further_steps_after_failure(self):
        self.fake.code["claim_corpus_release_gate.py"]=7
        self.assert_closed(self.execute,"canonical_claim_corpus")
        self.assertFalse(any("outbound_link_custody.py" in str(x[0]) for x in self.fake.calls))

    def test_53_refuse_timed_out_stage(self):
        self.fake.failure="draft_export_custody.py"
        self.assert_closed(self.execute,"timed out")

    def test_54_exact_stdout_digest(self):
        r=self.execute()
        self.assertEqual(r["steps"][0]["stdout_sha256"],
                         p.sha256(b'{"release_state": "HOLD", "may_publish": false}'))

    def test_55_no_private_receipt_outside_build(self):
        self.assert_closed(lambda:p.private_receipt(self.root/"out.json",self.root,{}),"receipt must")

    def test_56_private_receipt_is_write_once(self):
        path=self.root/"preparedness/build/R18-PREFLIGHT-SYNTHETIC.json"
        p.private_receipt(path,self.root,{"release_state":"HOLD","may_publish":False})
        self.assert_closed(lambda:p.private_receipt(path,self.root,{}),"already exists")

    def test_57_no_reused_unmarked_receipt(self):
        path=self.root/"preparedness/build/unapproved.json"
        self.assert_closed(lambda:p.private_receipt(path,self.root,{}),"receipt must")

    def test_58_receipt_json_is_hold(self):
        path=self.root/"preparedness/build/R18-PREFLIGHT-SYNTHETIC.json"
        p.private_receipt(path,self.root,self.execute())
        r=json.loads(path.read_text())
        self.assertEqual(r["release_state"],"HOLD")
        self.assertIs(r["may_publish"],False)

    def test_59_escaped_path_not_accepted(self):
        path=self.root/"preparedness/build/.."/"other.json"
        self.assert_closed(lambda:p.private_receipt(path,self.root,{}),"receipt must")

    def test_60_wrong_gate_order_is_not_executed(self):
        names=[x[0] for x in p.STEPS]
        self.assertLess(names.index("private_draft_build"),names.index("draft_export_custody"))
        self.assertLess(names.index("native_unit_suite"),names.index("source_crosswalk_truth"))


if __name__ == "__main__":
    unittest.main()
