from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_PATH = ROOT / "tests" / "verify_case_pin_r1.py"
spec = importlib.util.spec_from_file_location("case_pin_r1_base", BASE_PATH)
if spec is None or spec.loader is None:
    raise SystemExit("FAIL: unable to load Case Pin R1 base verifier")
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
original_fixture = base.fixture


def fixture_with_preinteraction_baseline(payload: str, mode: str) -> tuple[str, str]:
    html, fragment = original_fixture(payload, mode)
    needle = """     const beforeTab=target.getAttribute('tabindex');\n     const beforeClass=target.getAttribute('class');\n     const beforeHasClass=target.hasAttribute('class');"""
    replacement = """     const beforeTab=mode==='incoming-owned-zero'?'0':mode==='incoming-owned-neg'?'-7':null;\n     const beforeClass=mode==='incoming-owned-zero'?'publisher-owned fvcp-target':mode==='incoming-owned-neg'?'publisher-owned':null;\n     const beforeHasClass=mode==='incoming-owned-zero'||mode==='incoming-owned-neg';"""
    if mode in {"incoming-absent", "incoming-owned-zero", "incoming-owned-neg", "shifted"}:
        if needle not in html:
            raise SystemExit(f"FAIL: expected baseline fixture marker missing for {mode}")
        html = html.replace(needle, replacement, 1)
    return html, fragment


base.fixture = fixture_with_preinteraction_baseline
base.main()
