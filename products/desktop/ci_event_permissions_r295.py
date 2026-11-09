"""Fail closed on unexpected desktop CI events and token permissions.

This intentionally narrow source preflight certifies only the approved local
workflow preamble. It is not a YAML interpreter, runner attestation, or release
authorization. Jobs, actions, and uploads are guarded separately.
"""
from __future__ import annotations


class EventPermissionsError(ValueError):
    """Workflow trigger or access policy differs from reviewed configuration."""


# Exact mapping lines are intentional: aliases, quoted keys, path wildcards,
# duplicate keys, or a broader GitHub token scope require independent review.
_APPROVED_PREAMBLE = (
    "name: Desktop suite build (internal)",
    "on:",
    "  pull_request:",
    "    paths:",
    "      - 'products/desktop/**'",
    "      - '.github/workflows/desktop-build.yml'",
    "  workflow_dispatch:",
    "permissions:",
    "  contents: read",
)


def verify_event_permissions(source: str) -> None:
    """Require only reviewed PR/manual triggers and read-only GITHUB_TOKEN.

    Look only before the jobs mapping; the existing source-contract root-key
    verifier separately rejects unreviewed keys after jobs. Whitespace-only
    and whole-line comments do not grant extra YAML settings.
    """
    if type(source) is not str or "\x00" in source or "\t" in source:
        raise EventPermissionsError("Untrusted workflow trigger configuration")
    lines = source.splitlines()
    if lines.count("jobs:") != 1:
        raise EventPermissionsError("Ambiguous desktop jobs boundary")
    preamble = lines[:lines.index("jobs:")]
    meaningful = tuple(
        line for line in preamble
        if line.strip() and not line.lstrip().startswith("#")
    )
    if meaningful != _APPROVED_PREAMBLE:
        raise EventPermissionsError("Unreviewed desktop triggers or token permissions")
