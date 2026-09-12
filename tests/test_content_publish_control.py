import copy
import tempfile
import unittest
from pathlib import Path

from ops.content_publish_control import (
    ContentPublishControl,
    CriticalRollbackFailure,
    JsonLedger,
    MemoryLedger,
    PolicyError,
    PreconditionError,
    ReplayConflict,
    ValidationError,
    VerificationError,
    make_envelope,
    snapshot_hash,
)


BASE = {
    "title": "Original title",
    "content": "<p>Original</p>",
    "excerpt": "Original excerpt",
    "featured_media": 12,
    "slug": "original-slug",
    "status": "draft",
    "seo": {"title": "Original SEO", "description": "Original description"},
    "indexing": {"robots": "noindex,nofollow"},
}


class FakeAdapter:
    def __init__(self, state=None):
        self.state = copy.deepcopy(state or BASE)
        self.write_calls = 0
        self.restore_calls = 0
        self.apply_then_raise = False
        self.corrupt_after_write = False
        self.restore_raises = False
        self.restore_corrupts = False

    def read(self, kind, resource_id):
        return copy.deepcopy(self.state)

    def write(self, kind, resource_id, patch):
        self.write_calls += 1
        self.state.update(copy.deepcopy(patch))
        if self.corrupt_after_write:
            self.state["slug"] = "unexpected-drift"
        if self.apply_then_raise:
            raise RuntimeError("simulated post-write transport failure")

    def restore(self, kind, resource_id, snapshot):
        self.restore_calls += 1
        if self.restore_raises:
            raise RuntimeError("rollback unavailable")
        self.state = copy.deepcopy(snapshot)
        if self.restore_corrupts:
            self.state["status"] = "publish"


class FailingLedger(MemoryLedger):
    def put(self, package_id, record):
        raise OSError("disk full")


def manifest(mutation=None, authorized=None, *, package_id="FVD6.TEST.0001", before=None):
    mutation = mutation or {"content": "<p>Revised</p>"}
    authorized = authorized or list(mutation)
    return {
        "spec": "fvs-content-publish/v1",
        "package_id": package_id,
        "qd_artifact_id": "QD-FVD6-R1-EXACT",
        "qd_decision_id": "DQ-FVD6-R1-EXACT",
        "target": {"kind": "post", "id": 123},
        "expected_before_sha256": snapshot_hash(before or BASE),
        "authorized_fields": authorized,
        "mutation": mutation,
    }


class ContentPublishControlTests(unittest.TestCase):
    def control(self, adapter=None, ledger=None, allowlist=None):
        return ContentPublishControl(
            adapter=adapter or FakeAdapter(),
            ledger=ledger or MemoryLedger(),
            allowed_targets=allowlist or {("post", 123)},
        )

    def test_happy_path_preserves_non_authorized_sensitive_fields(self):
        adapter = FakeAdapter()
        receipt = self.control(adapter=adapter).execute(make_envelope(manifest()))
        self.assertEqual(receipt.status, "implemented_verified")
        self.assertTrue(receipt.verified)
        self.assertEqual(adapter.state["content"], "<p>Revised</p>")
        self.assertEqual(adapter.state["status"], "draft")
        self.assertEqual(adapter.state["slug"], "original-slug")
        self.assertEqual(adapter.state["seo"], BASE["seo"])
        self.assertEqual(adapter.state["indexing"], BASE["indexing"])

    def test_external_allowlist_is_not_self_authorized_by_package(self):
        adapter = FakeAdapter()
        with self.assertRaises(PolicyError):
            self.control(adapter=adapter, allowlist={("page", 999)}).execute(
                make_envelope(manifest())
            )
        self.assertEqual(adapter.write_calls, 0)

    def test_exact_manifest_and_mutation_scope_rejects_extra_global_key(self):
        m = manifest()
        m["mutation"]["plugins"] = {"activate": "evil"}
        m["authorized_fields"].append("plugins")
        env = make_envelope(m)
        with self.assertRaises(ValidationError):
            self.control().execute(env)

    def test_authorized_fields_must_equal_mutation_keys(self):
        env = make_envelope(manifest(authorized=["content", "status"]))
        with self.assertRaises(ValidationError):
            self.control().execute(env)

    def test_destructive_status_is_rejected(self):
        env = make_envelope(manifest({"status": "trash"}))
        with self.assertRaises(PolicyError):
            self.control().execute(env)

    def test_package_hash_tamper_is_rejected_before_read_or_write(self):
        adapter = FakeAdapter()
        env = make_envelope(manifest())
        env["manifest"]["mutation"]["content"] = "<p>Tampered</p>"
        with self.assertRaises(ValidationError):
            self.control(adapter=adapter).execute(env)
        self.assertEqual(adapter.write_calls, 0)

    def test_before_fingerprint_mismatch_rejects_without_mutation(self):
        adapter = FakeAdapter()
        changed = copy.deepcopy(BASE)
        changed["status"] = "publish"
        env = make_envelope(manifest(before=changed))
        with self.assertRaises(PreconditionError):
            self.control(adapter=adapter).execute(env)
        self.assertEqual(adapter.write_calls, 0)

    def test_readback_mismatch_rolls_back_exact_snapshot(self):
        adapter = FakeAdapter()
        adapter.corrupt_after_write = True
        with self.assertRaises(VerificationError):
            self.control(adapter=adapter).execute(make_envelope(manifest()))
        self.assertEqual(adapter.restore_calls, 1)
        self.assertEqual(adapter.state, BASE)

    def test_post_write_exception_rolls_back(self):
        adapter = FakeAdapter()
        adapter.apply_then_raise = True
        with self.assertRaises(VerificationError):
            self.control(adapter=adapter).execute(make_envelope(manifest()))
        self.assertEqual(adapter.restore_calls, 1)
        self.assertEqual(adapter.state, BASE)

    def test_rollback_exception_escalates_unknown_state(self):
        adapter = FakeAdapter()
        adapter.apply_then_raise = True
        adapter.restore_raises = True
        with self.assertRaises(CriticalRollbackFailure):
            self.control(adapter=adapter).execute(make_envelope(manifest()))

    def test_rollback_readback_mismatch_escalates_unknown_state(self):
        adapter = FakeAdapter()
        adapter.corrupt_after_write = True
        adapter.restore_corrupts = True
        with self.assertRaises(CriticalRollbackFailure):
            self.control(adapter=adapter).execute(make_envelope(manifest()))

    def test_ledger_failure_restores_destination(self):
        adapter = FakeAdapter()
        with self.assertRaises(ReplayConflict):
            self.control(adapter=adapter, ledger=FailingLedger()).execute(
                make_envelope(manifest())
            )
        self.assertEqual(adapter.state, BASE)
        self.assertEqual(adapter.restore_calls, 1)

    def test_same_exact_package_replay_is_noop_after_destination_verification(self):
        adapter = FakeAdapter()
        ledger = MemoryLedger()
        ctl = self.control(adapter=adapter, ledger=ledger)
        env = make_envelope(manifest())
        first = ctl.execute(env)
        writes_after_first = adapter.write_calls
        second = ctl.execute(env)
        self.assertEqual(first.status, "implemented_verified")
        self.assertEqual(second.status, "already_verified")
        self.assertEqual(adapter.write_calls, writes_after_first)

    def test_same_package_id_different_bytes_is_replay_conflict(self):
        adapter = FakeAdapter()
        ledger = MemoryLedger()
        ctl = self.control(adapter=adapter, ledger=ledger)
        ctl.execute(make_envelope(manifest()))
        changed_manifest = manifest(
            {"content": "<p>Different</p>"},
            package_id="FVD6.TEST.0001",
            before=adapter.state,
        )
        with self.assertRaises(ReplayConflict):
            ctl.execute(make_envelope(changed_manifest))

    def test_verified_replay_fails_closed_if_destination_drifted(self):
        adapter = FakeAdapter()
        ledger = MemoryLedger()
        ctl = self.control(adapter=adapter, ledger=ledger)
        env = make_envelope(manifest())
        ctl.execute(env)
        adapter.state["title"] = "Out-of-band change"
        with self.assertRaises(ReplayConflict):
            ctl.execute(env)

    def test_json_ledger_persists_exact_record_atomically(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "ledger.json"
            adapter = FakeAdapter()
            ctl = self.control(adapter=adapter, ledger=JsonLedger(path))
            env = make_envelope(manifest())
            receipt = ctl.execute(env)
            self.assertTrue(path.exists())
            self.assertEqual(receipt.status, "implemented_verified")
            second = self.control(adapter=adapter, ledger=JsonLedger(path)).execute(env)
            self.assertEqual(second.status, "already_verified")

    def test_unknown_envelope_key_rejected(self):
        env = make_envelope(manifest())
        env["activate"] = True
        with self.assertRaises(ValidationError):
            self.control().execute(env)

    def test_empty_allowlist_is_rejected(self):
        with self.assertRaises(PolicyError):
            ContentPublishControl(adapter=FakeAdapter(), ledger=MemoryLedger(), allowed_targets=set())


if __name__ == "__main__":
    unittest.main()
