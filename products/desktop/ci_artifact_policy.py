"""Fail-closed policy check for CI artifact *upload selections* (not a release gate).

GitHub Actions artifacts in a private repository are accessible to authorized
repository users, not product customers. Keep every six-app EXE, especially the
two premium EXEs, out of automatically downloadable workflow artifacts.

This deliberately accepts a *small* subset of the known upload-artifact YAML.
Unknown syntax fails closed instead of guessing its upload scope. It does not
prove that unrelated CI steps cannot transfer files by other mechanisms.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

MAX_WORKFLOW_BYTES = 128 * 1024
ALLOWED = {
    "final-vestige-desktop-source-only": (
        "${{ runner.temp }}/fvs-source/offline-source-suite.json",
    ),
    "final-vestige-desktop-windows-internal": (
        "dist/SHA256SUMS.txt", "build/offline-candidate-evidence.json",
    ),
}
STEP_RE = re.compile(r"^(\s*)- (?:name|uses):")
UPLOAD_RE = re.compile(r"^\s*uses:\s*actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02\s*(?:#.*)?$")
USE_RE = re.compile(r"^\s*uses:\s*(.+?)\s*$")
FIELD_RE = re.compile(r"^(\s*)([a-zA-Z_-]+):(?:\s*(.*))?$")


class ArtifactPolicyError(ValueError):
    """A CI export may contain unapproved content; do not run/upload it."""


def _fields(step: list[str]) -> tuple[str, tuple[str, ...]]:
    """Extract *only* literal name/path fields from a single upload action."""
    action_lines = [line for line in step if USE_RE.match(line)]
    if len(action_lines) != 1 or not UPLOAD_RE.match(action_lines[0]):
        raise ArtifactPolicyError("Upload action must use approved version and syntax")
    with_lines = [(i, line) for i, line in enumerate(step)
                  if FIELD_RE.match(line) and FIELD_RE.match(line).group(2) == "with"]
    if len(with_lines) != 1:
        raise ArtifactPolicyError("Upload action must have one literal with block")
    start, raw_with = with_lines[0]
    with_indent = len(raw_with) - len(raw_with.lstrip())
    name = None
    paths = None
    options: dict[str, str] = {}
    offset = start + 1
    while offset < len(step):
        raw = step[offset]
        if not raw.strip() or raw.lstrip().startswith("#"):
            offset += 1
            continue
        indent = len(raw) - len(raw.lstrip())
        if indent <= with_indent:
            break
        match = FIELD_RE.match(raw)
        if not match or len(match.group(1)) != with_indent + 2:
            raise ArtifactPolicyError("Unsupported upload action field syntax")
        key, value = match.group(2), (match.group(3) or "").strip()
        if key == "name":
            if name is not None or not re.fullmatch(r"[a-z0-9-]+", value):
                raise ArtifactPolicyError("Upload name must be a unique literal")
            name = value
        elif key == "path":
            if paths is not None:
                raise ArtifactPolicyError("Duplicate upload path field")
            if value == "|":
                paths_list = []
                while offset + 1 < len(step):
                    line = step[offset + 1]
                    if not line.strip():
                        offset += 1
                        continue
                    space = len(line) - len(line.lstrip())
                    if space <= indent:
                        break
                    if space != indent + 2 or line.lstrip().startswith("#"):
                        raise ArtifactPolicyError("Unapproved multiline artifact selection")
                    paths_list.append(line.strip())
                    offset += 1
                paths = tuple(paths_list)
            elif value and not any(c in value for c in "'\"#"):
                paths = (value,)
            else:
                raise ArtifactPolicyError("Upload path must be a literal allowlist")
        elif key in {"if-no-files-found", "retention-days"}:
            if key in options:
                raise ArtifactPolicyError("Duplicate artifact security option")
            options[key] = value
        else:
            raise ArtifactPolicyError("Unknown upload-artifact option")
        offset += 1
    if options != {"if-no-files-found": "error", "retention-days": "7"}:
        raise ArtifactPolicyError("Artifact failure/retention settings are not approved")
    if name is None or paths is None:
        raise ArtifactPolicyError("Upload name and paths are required")
    return name, paths


def verify_upload_policy(workflow_source: str) -> int:
    """Reject any extra or broadened GitHub upload-artifact action."""
    if "\x00" in workflow_source or len(workflow_source.encode("utf-8")) > MAX_WORKFLOW_BYTES:
        raise ArtifactPolicyError("Workflow is unsafe or too large")
    lines = workflow_source.splitlines()
    steps: list[list[str]] = []
    current: list[str] = []
    current_indent: int | None = None
    for line in lines:
        match = STEP_RE.match(line)
        if match and (current_indent is None or len(match.group(1)) <= current_indent):
            if current:
                steps.append(current)
            current = [line]
            current_indent = len(match.group(1))
        elif current:
            current.append(line)
    if current:
        steps.append(current)
    seen: dict[str, tuple[str, ...]] = {}
    found = 0
    for step in steps:
        if not any("upload-artifact@" in line for line in step):
            continue
        found += 1
        name, paths = _fields(step)
        if name in seen:
            raise ArtifactPolicyError("Duplicate upload artifact name")
        seen[name] = paths
    if found != len(ALLOWED) or set(seen) != set(ALLOWED):
        raise ArtifactPolicyError("Upload artifact actions differ from approved set")
    if any(seen[name] != expected for name, expected in ALLOWED.items()):
        raise ArtifactPolicyError("Unapproved artifact payload selection")
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workflow", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.workflow.stat().st_size > MAX_WORKFLOW_BYTES:
            raise ArtifactPolicyError("Workflow is too large")
        checked = verify_upload_policy(args.workflow.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ArtifactPolicyError):
        print("REJECTED: CI artifact upload scope is not approved", file=sys.stderr)
        return 1
    print(f"PASS: {checked} evidence-only CI uploads; no executables allowed. NOT release approval.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
