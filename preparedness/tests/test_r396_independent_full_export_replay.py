"""R396 synthetic-only, read-only adversarial tests. No QD or commerce PASS."""
from __future__ import annotations

import copy
from hashlib import sha256
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import Mock

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
# Available local archives omit the R390 and exact R395 production source.
# This test uses explicit injected auditors and production R391 no-follow snapshot.
# Tests do NOT claim native R390/R395 execution.
_isolated_stubs = []
for name in ("r390_all_export_custody", "r395_authentic_render_replay"):
    try:
        __import__(name)  # Actual repository takes precedence in native tests.
    except ModuleNotFoundError as error:
        if error.name != name:
            raise  # A broken dependency is not a reason to fabricate a stub.
        module = types.ModuleType(name)
        module.audit = lambda *_: None
        module.replay_native = lambda *_: None
        sys.modules[name] = module
        _isolated_stubs.append(name)
import r396_independent_full_export_replay as gate
for _name in _isolated_stubs:
    del sys.modules[_name]  # Never contaminate other collected tests.
import r391_frozen_export_attestation as frozen_gate


def held(status, **extra):
    return {"status": status, "release_state": "DRAFT_HARD_HOLD",
            "publication_approved": False, "qualified_safety_approved": False,
            "live_release_allowed": False, "merchant_offer_verified": False,
            "automatic_variant_selection": False, "errors": [], **extra}


def fixture(root):
    wp, pv = root / "wp", root / "preview"
    wp.mkdir(); pv.mkdir()
    for i in range(50):
        slug = f"guide-{i:02d}" if i < 35 else f"tool-{i:02d}"
        (wp / (slug + ".html")).write_text(f'<div class="pa-page" data-slug="{slug}">DRAFT REVIEW content {i}</div>', encoding="utf-8")
        (pv / (slug + ".html")).write_text(f'<html><div class="pa-page" data-slug="{slug}">DRAFT REVIEW content {i}</div></html>', encoding="utf-8")
    originals = [f"guide-{i:02d}" for i in range(35)]
    snapshots = {name: frozen_gate._snapshot(path) for name, path in (("wp", wp), ("preview", pv))}
    rows = []
    for slug in sorted(snapshots["wp"]["files"]):
        a, b = snapshots["wp"]["files"][slug], snapshots["preview"]["files"][slug]
        rows.append({"slug": slug, "kind": "original_article" if slug in originals else "unreviewed_supplemental",
                     "wp_sha256": a["sha256"], "preview_sha256": b["sha256"],
                     "wp_bytes": a["size"], "preview_bytes": b["size"],
                     "errors": [], "release_allowed": False, "qualified_review_required": True})
    full = held("ALL_EXPORT_BYTES_REVIEW_HARD_HOLD", exports=rows)
    inventory = {k: {s: v["sha256"] for s, v in sorted(d["files"].items())}
                 for k, d in sorted(snapshots.items())}
    data = {
        "repo": root,
        "wp": wp, "preview": pv,
        "original": held("REVIEW_PACKET_HARD_HOLD", articles=[{"slug": s} for s in originals],
                         unselected_conflicts=[{"i": i} for i in range(9)]),
        "integrated": held("INTEGRATED_REVIEW_HARD_HOLD"),
        "frozen": held("FROZEN_EXPORT_REVIEW_HARD_HOLD",
                       reports={"full": copy.deepcopy(full)}, matched_snapshot_pairs=50,
                       snapshot_sha256=sha256(gate._canonical(inventory)).hexdigest()),
        "witness": held("CROSS_GATE_WITNESS_REVIEW_HARD_HOLD"),
        "r395": held("AUTHENTIC_RENDER_REPLAY_REVIEW_HARD_HOLD", replay_sha256="a" * 64),
        "full": full,
    }
    return data


def call(d, *, full=None, replay=None, snapshot=None):
    if full is None:
        full = lambda wp, preview, original: copy.deepcopy(d["full"])
    if replay is None:
        replay = lambda *args: copy.deepcopy(d["r395"])
    return gate.audit(d["repo"], d["original"], d["integrated"], d["frozen"],
                      d["witness"], d["r395"], d["wp"], d["preview"],
                      full_auditor=full, native_replayer=replay, snapshotter=snapshot)


class R396Synthetic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="r396-hold-")
        cls.d = fixture(Path(cls.tmp.name))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_valid_synthetic_still_unpublishable(self):
        v = call(self.d)
        self.assertEqual(v["status"], "INDEPENDENT_FULL_EXPORT_REPLAY_HARD_HOLD", v)
        self.assertEqual(v["counts"]["original_articles"], 35)
        self.assertEqual(v["counts"]["private_pairs"], 50)
        self.assertFalse(v["qualified_safety_approved"])
        self.assertFalse(v["merchant_offer_verified"])
        self.assertEqual(len(v["independent_replay_sha256"]), 64)

    def test_deterministic_digest(self):
        self.assertEqual(call(self.d), call(copy.deepcopy(self.d)))

    def test_forged_claimed_full_even_with_same_snapshot_rejected(self):
        d = copy.deepcopy(self.d)
        d["frozen"]["reports"]["full"]["exports"][0]["kind"] = "verified_article"
        self.assertEqual(call(d)["status"], "INVALID_HARD_HOLD")

    def test_r395_replay_mutation_detected(self):
        d = copy.deepcopy(self.d)
        bad = copy.deepcopy(d["r395"])
        bad["replay_sha256"] = "f" * 64
        result = call(d, replay=lambda *args: bad)
        self.assertEqual(result["status"], "INVALID_HARD_HOLD")
        self.assertIn("R395_REPLAY_REPORT_NOT_REPRODUCED", result["errors"])

    def test_replay_not_invoked_when_full_report_is_different(self):
        d = copy.deepcopy(self.d)
        bad = copy.deepcopy(d["full"])
        bad["exports"][0]["wp_sha256"] = "a" * 64
        spy = Mock()
        out = call(d, full=lambda *_: bad, replay=spy)
        spy.assert_not_called()
        self.assertEqual(out["status"], "INVALID_HARD_HOLD")

    def test_mid_audit_mutation_detected(self):
        d = self.d
        orig = d["wp"] / "tool-49.html"
        old = orig.read_bytes()
        def mutate(*args):
            orig.write_bytes(old + b"<p>tamper</p>")
            return copy.deepcopy(d["full"])
        try:
            self.assertEqual(call(d, full=mutate)["status"], "INVALID_HARD_HOLD")
        finally:
            orig.write_bytes(old)

    def test_audit_failure_is_hard_hold(self):
        def explode(*args):
            raise PermissionError("fixture permission denied")
        v = call(self.d, full=explode)
        self.assertEqual(v["status"], "INVALID_HARD_HOLD")

    def test_missing_git_objects_is_hard_hold(self):
        def missing(*args):
            raise RuntimeError("not a complete repository")
        v = call(self.d, replay=missing)
        self.assertEqual(v["status"], "INVALID_HARD_HOLD")

    def test_cli_missing_json_never_returns_zero(self):
        from contextlib import redirect_stdout
        from io import StringIO
        f = StringIO()
        with redirect_stdout(f):
            code = gate.main(["--repo", "/missing", "--original", "/missing",
                "--integrated", "/missing", "--frozen", "/missing",
                "--witness", "/missing", "--r395", "/missing",
                "--wp", "/missing", "--preview", "/missing"])
        self.assertEqual(code, 2)
        self.assertIn("INVALID_HARD_HOLD", f.getvalue())


# 60 independent mutations of data, claimed receipts and full-export rows.
def modifications():
    m = []
    for name in ("original", "integrated", "frozen", "witness", "r395", "full"):
        for field, value in (("status", "PASS"), ("publication_approved", True),
                             ("qualified_safety_approved", True), ("errors", ["not clear"])):
            m.append((name + ":" + field, lambda d, n=name, f=field, v=value:
                      d[n].__setitem__(f, v)))
    m.extend([
        ("original-less-article", lambda d: d["original"]["articles"].pop()),
        ("duplicate-slug", lambda d: d["original"]["articles"][0].update(slug="guide-01")),
        ("invalid-slug", lambda d: d["original"]["articles"][0].update(slug="../bad")),
        ("empty-slug", lambda d: d["original"]["articles"][0].update(slug="")),
        ("extra-fork", lambda d: d["original"]["unselected_conflicts"].append({"x": 1})),
        ("lost-fork", lambda d: d["original"]["unselected_conflicts"].pop()),
        ("lost-export", lambda d: d["full"]["exports"].pop()),
        ("duplicate-export", lambda d: d["full"]["exports"][0].update(slug="guide-01")),
        ("wrong-export-slug", lambda d: d["full"]["exports"][0].update(slug="other")),
        ("wrong-hash", lambda d: d["full"]["exports"][0].update(wp_sha256="a" * 64)),
        ("wrong-preview-hash", lambda d: d["full"]["exports"][0].update(preview_sha256="b" * 64)),
        ("wrong-byte-size", lambda d: d["full"]["exports"][0].update(wp_bytes=10)),
        ("wrong-preview-size", lambda d: d["full"]["exports"][0].update(preview_bytes=10)),
        ("false-review-clearance", lambda d: d["full"]["exports"][0].update(qualified_review_required=False)),
        ("false-publication", lambda d: d["full"]["exports"][0].update(release_allowed=True)),
        ("wrong-kind", lambda d: d["full"]["exports"][0].update(kind="unreviewed_supplemental")),
        ("wrong-supplemental-kind", lambda d: d["full"]["exports"][-1].update(kind="original_article")),
        ("row-errors", lambda d: d["full"]["exports"][0].update(errors=["bad"])),
        ("bad-snapshot-hash", lambda d: d["frozen"].update(snapshot_sha256="a" * 64)),
        ("bad-snapshot-count", lambda d: d["frozen"].update(matched_snapshot_pairs=51)),
        ("bad-replay-digest", lambda d: d["r395"].update(replay_sha256=None)),
        ("missing-full-evidence", lambda d: d["frozen"]["reports"].pop("full")),
    ])
    return m


def _case(idx):
    def case(self):
        d = copy.deepcopy(self.d)
        name, alter = modifications()[idx]
        alter(d)
        got = call(d)
        self.assertEqual(got["status"], "INVALID_HARD_HOLD", (name, got))
        self.assertIsNone(got["independent_replay_sha256"])
        self.assertFalse(got["publication_approved"])
    return case


for i, (name, fn) in enumerate(modifications()):
    setattr(R396Synthetic, f"test_mutation_{i:02d}_{name.replace(':','_').replace('-', '_')}", _case(i))

if __name__ == "__main__":
    unittest.main()