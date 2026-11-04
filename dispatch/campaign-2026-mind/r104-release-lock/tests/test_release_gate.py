"""R104 offline mutation tests. Run with unittest; no network, no sending."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import release_gate as gate

class TestReleaseLock(unittest.TestCase):
    def setUp(self):
        self.lock = gate.read_json(gate.LEDGER)
        self.manifest = gate.read_json(gate.ROOT / "manifest.json")

    def mutated(self, adjust):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/"issues").mkdir()
            (root/"manifest.json").write_bytes((gate.ROOT/"manifest.json").read_bytes())
            for item in self.lock["inherited"]["issues"]:
                original = gate.ROOT / "issues" / item["file"]
                (root/"issues"/item["file"]).write_bytes(original.read_bytes())
            ledger=copy.deepcopy(self.lock)
            adjust(root,ledger)
            lp=root/"ledger.json"
            lp.write_text(json.dumps(ledger),encoding="utf-8")
            return gate.audit(root,lp)

    def assert_problem(self, adjust):
        result=self.mutated(adjust)
        self.assertEqual(result["status"],"HOLD_UNSENT")
        self.assertFalse(result["source_audit_passed"])
        self.assertFalse(result["permission_to_send"])

    def test_unmodified_current_snapshot(self):
        report=gate.audit()
        self.assertEqual(report["problems"],[])
        self.assertTrue(report["source_audit_passed"])
        self.assertFalse(report["permission_to_send"])

    def test_complete_six_issue_manifest(self):
        self.assertEqual(len(self.manifest["issues"]),6)

    def test_four_to_two_mix(self):
        self.assertEqual([i["number"] for i in self.manifest["issues"] if i["kind"]=="commercial-review-pending"],[3,5])

    def test_all_original_versions_differ(self):
        self.assertNotEqual(self.lock["original"]["manifest_sha"],self.lock["inherited"]["manifest_sha"])
        self.assertTrue(all(a["sha"]!=b["sha"] for a,b in zip(self.lock["original"]["issues"],self.lock["inherited"]["issues"])))

    def test_all_ten_approvals_false(self):
        self.assertEqual(len(self.lock["required_evidence"]),10)
        self.assertTrue(all(v is False for v in self.lock["required_evidence"].values()))

    def test_no_fabricated_metrics(self):
        self.assertTrue(all(v is None for v in self.lock["metrics"].values()))

    def test_reject_founder_approval(self):
        self.assert_problem(lambda r,l:l.update(founder_send_approval=True))

    def test_reject_version_selection(self):
        self.assert_problem(lambda r,l:l.update(founder_version_selection="PR175"))

    def test_reject_merchant_permission(self):
        for k in ("affiliate_zen12_email_permission","affiliate_total_focus_email_permission"):
            with self.subTest(k=k):
                self.assert_problem(lambda r,l:l["required_evidence"].update({k:True}))

    def test_reject_live_guide_claim(self):
        for k in ("live_zen12_warmup_guide","live_total_focus_warmup_guide"):
            with self.subTest(k=k):
                self.assert_problem(lambda r,l:l["required_evidence"].update({k:True}))

    def test_reject_fake_address(self):
        self.assert_problem(lambda r,l:l["required_evidence"].update(valid_final_vestige_postal_address=True))

    def test_reject_fake_mime(self):
        self.assert_problem(lambda r,l:l["required_evidence"].update(received_real_jetpack_mime=True))

    def test_reject_fake_unsubscribe(self):
        self.assert_problem(lambda r,l:l["required_evidence"].update(working_unsubscribe=True))

    def test_reject_fake_recipient_count(self):
        self.assert_problem(lambda r,l:l["current_jetpack"].update(verified_email_eligible=2))

    def test_reject_made_up_clicks(self):
        self.assert_problem(lambda r,l:l["metrics"].update(clicks=17))

    def test_reject_false_welcome_receipt(self):
        self.assert_problem(lambda r,l:l["current_jetpack"].update(welcome_received=True))

    def test_reject_full_text_assumption(self):
        self.assert_problem(lambda r,l:l["current_jetpack"].update(mode="full"))

    def test_reject_auto_send_enabled(self):
        self.assert_problem(lambda r,l:l["current_jetpack"].update(auto_send=True))

    def test_reject_manifest_byte_change(self):
        self.assert_problem(lambda r,l:(r/"manifest.json").write_bytes((r/"manifest.json").read_bytes()+b" "))

    def test_reject_issue_blob_change(self):
        def tamper(r,l):
            p=r/"issues"/l["inherited"]["issues"][1]["file"]
            p.write_bytes(p.read_bytes()+b" changed")
        self.assert_problem(tamper)

    def test_reject_mutated_blob_lock(self):
        self.assert_problem(lambda r,l:l["inherited"]["issues"][2].update(sha="0"*40))

    def test_reject_identical_manifest_provenance(self):
        self.assert_problem(lambda r,l:l["original"].update(manifest_sha=l["inherited"]["manifest_sha"]))

    def test_reject_changed_4235_allocation(self):
        self.assert_problem(lambda r,l:l.update(commerce_slots=[1,5]))

    def test_reject_changed_release_state(self):
        self.assert_problem(lambda r,l:l.update(status="READY_TO_SEND"))

if __name__=="__main__":
    unittest.main()
