"""R395 synthetic adversarial tests. Never an actual CMS or safety/QD approval."""
from __future__ import annotations

import copy
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tests"))
import r395_authentic_render_replay as r395
from test_r394_authenticated_export_receipt import make_inputs, run as r394_run, mutations


def inputs(d):
    return {
        "original": copy.deepcopy(d["orig"]),
        "integrated": copy.deepcopy(d["integrated"]),
        "frozen": copy.deepcopy(d["frozen"]),
        "witness": copy.deepcopy(d["witness"]),
        "rebuilt": copy.deepcopy(d["orig"]),
        "render": copy.deepcopy(d["frozen"]["reports"]["render"]),
        "anchor": copy.deepcopy(d["frozen"]["reports"]["anchor"]),
        "reintegrated": copy.deepcopy(d["integrated"]),
        "refrozen": copy.deepcopy(d["frozen"]),
        "custody": r394_run(d),
    }


def run(d):
    return r395.check_replay(d["original"], d["integrated"], d["frozen"],
                             d["witness"], d["rebuilt"], d["render"], d["anchor"],
                             d["reintegrated"], d["refrozen"], d["custody"])


def extra_mutations():
    return [
        lambda d:d["rebuilt"].update(status="PASS"),
        lambda d:d["rebuilt"].update(publication_approved=True),
        lambda d:d["rebuilt"].update(qualified_safety_approved=True),
        lambda d:d["rebuilt"]["articles"].pop(),
        lambda d:d["rebuilt"]["articles"][0].update(slug="other"),
        lambda d:d["rebuilt"]["articles"][0]["variants"][0].update(body_sha="f"*40),
        lambda d:d["rebuilt"]["unselected_conflicts"].pop(),
        lambda d:d["render"].update(status="PASS"),
        lambda d:d["render"].update(publication_approved=True),
        lambda d:d["render"].update(qualified_safety_approved=True),
        lambda d:d["render"]["articles"].pop(),
        lambda d:d["render"]["articles"][0].update(slug="other"),
        lambda d:d["render"]["articles"][0]["matching_variant_candidates"][0].update(body_sha="f"*40),
        lambda d:d["anchor"].update(status="PASS"),
        lambda d:d["anchor"].update(publication_approved=True),
        lambda d:d["anchor"].update(qualified_safety_approved=True),
        lambda d:d["anchor"]["articles"].pop(),
        lambda d:d["anchor"]["articles"][0].update(slug="other"),
        lambda d:d["anchor"]["articles"][0]["matching_original_candidates"][0].update(body_sha="f"*40),
        lambda d:d["reintegrated"].update(status="PASS"),
        lambda d:d["reintegrated"].update(publication_approved=True),
        lambda d:d["reintegrated"].update(qualified_safety_approved=True),
        lambda d:d["reintegrated"].update(merchant_offer_verified=True),
        lambda d:d["reintegrated"]["counts"].update(unselected_source_collisions=4),
        lambda d:d["reintegrated"]["candidate_intersections"].pop(),
        lambda d:d["reintegrated"]["candidate_intersections"][0].update(slug="other"),
        lambda d:d["refrozen"].update(status="PASS"),
        lambda d:d["refrozen"].update(publication_approved=True),
        lambda d:d["refrozen"].update(qualified_safety_approved=True),
        lambda d:d["refrozen"].update(snapshot_sha256="f"*64),
        lambda d:d["refrozen"]["reports"]["full"]["exports"].pop(),
        lambda d:d["refrozen"]["reports"]["full"]["exports"][0].update(wp_sha256="f"*64),
        lambda d:d["custody"].update(status="PASS"),
        lambda d:d["custody"].update(publication_approved=True),
        lambda d:d["custody"].update(qualified_safety_approved=True),
        lambda d:d["custody"].update(custody_sha256=None),
        lambda d:d["custody"].update(errors=["read failed"]),
    ]


class R395Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="r395-audit-")
        cls.d = make_inputs(Path(cls.tmp.name))
        cls.base = inputs(cls.d)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_matching_synthetic_still_never_publishable(self):
        report = run(copy.deepcopy(self.base))
        self.assertEqual(report["status"], "AUTHENTIC_RENDER_REPLAY_REVIEW_HARD_HOLD", report)
        self.assertFalse(report["publication_approved"])
        self.assertFalse(report["qualified_safety_approved"])
        self.assertFalse(report["merchant_offer_verified"])
        self.assertEqual(report["counts"]["articles"], 35)
        self.assertEqual(report["counts"]["export_pairs"], 50)
        self.assertEqual(report["counts"]["shelter_conflicts"], 9)

    def test_digest_determinism(self):
        self.assertEqual(run(self.base), run(copy.deepcopy(self.base)))

    def test_fake_recomputed_witness_cannot_hide_render_substitution(self):
        d = copy.deepcopy(self.base)
        d["frozen"]["reports"]["render"]["articles"][0]["matching_variant_candidates"][0]["body_sha"] = "f"*40
        d["witness"] = r395.cross_gate.check(d["original"], d["integrated"], d["frozen"])
        self.assertEqual(run(d)["status"], "INVALID_HARD_HOLD")

    def test_native_with_missing_authentic_git_objects_fails(self):
        with self.assertRaises((OSError, ValueError, subprocess.SubprocessError)):
            r395.replay_native(Path("/missing-native-repository"), self.base["original"],
                               self.base["integrated"], self.base["frozen"], self.base["witness"],
                               Path("/no/wp"), Path("/no/preview"))

    def test_isolated_python_cli_returns_invalid_hold_not_import_error(self):
        command = [sys.executable, "-I", str(ROOT / "tools" / "r395_authentic_render_replay.py"),
                   "--repo", "/missing", "--original", "/missing", "--integrated", "/missing",
                   "--frozen", "/missing", "--witness", "/missing",
                   "--wp", "/missing", "--preview", "/missing"]
        result = subprocess.run(command, text=True, capture_output=True, check=False, timeout=20)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn('"status": "INVALID_HARD_HOLD"', result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_cli_never_returns_zero(self):
        capture = StringIO()
        with redirect_stdout(capture):
            self.assertEqual(r395.main_r395([
                "--repo", "/missing", "--original", "/missing", "--integrated", "/missing",
                "--frozen", "/missing", "--witness", "/missing",
                "--wp", "/missing", "--preview", "/missing"]), 2)
        self.assertIn("INVALID_HARD_HOLD", capture.getvalue())


def _make_r394_mutation(idx):
    def case(self):
        d = copy.deepcopy(self.base)
        mutation = mutations()[idx]
        # R394 first 36 mutations alter report evidence; no shared filesystem edits.
        aliases = {"orig": "original", "integrated": "integrated",
                   "frozen": "frozen", "witness": "witness"}
        view = {k: d[v] for k,v in aliases.items()}
        mutation(view)
        report = run(d)
        self.assertEqual(report["status"], "INVALID_HARD_HOLD", f"r394 mutation {idx}: {report}")
        self.assertIsNone(report["replay_sha256"])
    return case


def _make_replay_mutation(idx):
    def case(self):
        d = copy.deepcopy(self.base)
        extra_mutations()[idx](d)
        report = run(d)
        self.assertEqual(report["status"], "INVALID_HARD_HOLD", f"replay mutation {idx}: {report}")
        self.assertFalse(report["publication_approved"])
        self.assertIsNone(report["replay_sha256"])
    return case


for _index in range(36):
    setattr(R395Tests, f"test_r394_parent_mutation_{_index:02d}", _make_r394_mutation(_index))
for _index in range(len(extra_mutations())):
    setattr(R395Tests, f"test_native_replay_mutation_{_index:02d}", _make_replay_mutation(_index))

if __name__ == "__main__":
    unittest.main()
