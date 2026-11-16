#!/usr/bin/env python3
"""R401: source-custody + visibility admission for the R400 read-only staging runner.

This additive QA layer restores R392/R393/R394 source/chronology/visibility
checks omitted by R400. It does not modify R400, WordPress, analytics or media.
A fixture run with non-identical local legacy dependency is explicitly labelled.
Staging runs require exact Git blobs from the reviewed parent commits.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from pathlib import Path

EXPERIENCE2 = Path(__file__).resolve().parents[2]
EXPECTED = {
    "apollo-r377/custody.json": "dd04d446d480f519f85a7ebd065e257dfdd84957",
    "apollo-r392/qa/semantic_custody.py": "de2aaf8040dca54c6ace355b344fa572a5c8f01b",
    "apollo-r393/qa/topology.py": "6efac8f5663b00c1773b5400a643e3248bb6d707",
    "apollo-r394/qa/visibility_custody.py": "86cf2be0243cab9d07ab338c91f2f15ac84fd585",
    "apollo-r400/qa/staging_browser_gate.py": "e06d61a2ef2ad627f40eeed05dd79a6621dbb9c2",
}


def git_blob(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(payload)).encode("ascii") + b"\x00" + payload).hexdigest()


def dependencies(staging: bool) -> dict:
    """No implicit parent-tree drift. Fixture tests may disclose R392 shadow drift."""
    result = {}
    for path, expected in EXPECTED.items():
        target = EXPERIENCE2 / path
        actual = git_blob(target) if target.is_file() else "MISSING"
        result[path] = {"expected_git_blob": expected, "actual_git_blob": actual, "match": actual == expected}
    missing = [k for k,v in result.items() if not v["match"]]
    # Fixture reproduction from archived local artifacts may use a logically
    # equivalent source inspector; never certify that as the remote exact head.
    if missing and (staging or set(missing) != {"apollo-r392/qa/semantic_custody.py", "apollo-r400/qa/staging_browser_gate.py"}):
        raise RuntimeError("HOLD: unreviewed or missing upstream Git blobs: " + ", ".join(missing))
    return result


def modules():
    # Import reviewed files from known absolute paths, not caller CWD.
    for path in (EXPERIENCE2/"apollo-r400"/"qa", EXPERIENCE2/"apollo-r394"/"qa"):
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))
    import staging_browser_gate as base
    import visibility_custody as visual
    return base, visual


def strengthened_inspector(base, visual):
    name = 'inspect' if hasattr(base, 'inspect') else 'inspect_gallery'
    original = getattr(base, name)
    def inspect(page):
        fields = original(page)
        passed, defects = visual.verify_page(page)
        if not passed:
            # Print only stable failure codes, never user/page-text data.
            raise AssertionError("NASA source/chronology/proof custody: " + ", ".join(defects[:32]))
        fields["exact_source_custody"] = "PASS"
        fields["chronology_proof_visibility"] = "PASS"
        fields["source_controlled_validator"] = "R392 + R393 + R394"
        return fields
    return inspect


def inspect_page(page):
    base, visual = modules()
    return strengthened_inspector(base, visual)(page)


def run(args):
    staging=bool(args.url)
    deps=dependencies(staging=staging)
    base, visual=modules()
    name = "inspect" if hasattr(base, "inspect") else "inspect_gallery"
    original=getattr(base, name)
    setattr(base, name, strengthened_inspector(base, visual))
    # R400 local archived runner has alternate argument labels. This compatibility
    # is only for fixture shadow tests; exact GitHub source remains required for staging.
    args.output=args.out
    args.allow_host=args.host
    args.axe_file=args.axe
    try:
        report=base.run(args)
    finally:
        setattr(base,name,original)
    report["source_custody_layer"]="R401"
    contexts = report.get("screens", report.get("contexts", []))
    blockers = report.get("blockers", [])
    report["upstream_git_blobs"]=deps
    report["exact_remote_upstream"] = all(v["match"] for v in deps.values())
    if not staging and not report["exact_remote_upstream"] and not blockers:
        report["status"]="PASS_LOCAL_FIXTURE_SHADOW_DEPENDENCY_ONLY"
        report["result"]="PASS_LOCAL_FIXTURE_SHADOW_DEPENDENCY_ONLY"
    report["screens"] = contexts
    report["status"] = report.get("status",report.get("result", "HOLD"))
    report["release_allowed"]=False
    Path(args.out).mkdir(parents=True,exist_ok=True)
    (Path(args.out)/"report.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return report


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    opts=p.add_mutually_exclusive_group(required=True)
    opts.add_argument('--fixture'); opts.add_argument('--url')
    p.add_argument('--host'); p.add_argument('--axe'); p.add_argument('--axe-sha256')
    p.add_argument('--out',default=str(EXPERIENCE2/'apollo-r401'/'QA'))
    p.add_argument('--chromium',default='/usr/bin/chromium')
    args=p.parse_args()
    try:
        output=run(args)
        print(json.dumps({"status":output["status"],"screens":len(output["screens"]),"blockers":output["blockers"],"exact_remote_upstream":output["exact_remote_upstream"]}))
        sys.exit(2 if output["blockers"] else 0)
    except Exception as exc:
        print("HARD HOLD: " + type(exc).__name__ + ": " + str(exc), file=sys.stderr)
        sys.exit(2)
