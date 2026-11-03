"""Narrow, fail-closed lexical guard for action-bearing YAML keys in desktop CI.

A six-SHA inventory alone can miss YAML-equivalent spellings of uses, such
as 'uses :', quoted keys, or inline mapping syntax. This independent syntactic
guard rejects those shapes before the immutable-commit verifier runs.
It is NOT a general YAML parser, and it cannot certify workflow run scripts,
runner integrity, independent QD approval, or executable releases.
"""
from __future__ import annotations

import re

MAX_WORKFLOW_BYTES = 128 * 1024
# Approved workflow has four step-list '- uses' entries and two nested
# 'uses' entries after a step 'name'. Other shapes require human review.
CANONICAL = re.compile(r"^(?: {6}- | {8})uses: [^\r\n]+$")
KEY_HINT = re.compile(r"""(?<![a-zA-Z0-9_-])(?:uses|"uses"|'uses')\s*:""")
ESCAPED_KEY = re.compile(
    r'(?<![a-zA-Z0-9_-])"[^"\r\n]*\\(?:u[0-9a-fA-F]{4}|U[0-9a-fA-F]{8}|x[0-9a-fA-F]{2})[^"\r\n]*"\s*:'
)
MERGE_KEY = re.compile(r"^\s*(?:-\s*)?<<\s*:")
EXPLICIT_KEY = re.compile(r"^\s*\?\s*(?:uses|[\"']uses[\"'])\s*$")


class ActionKeyError(ValueError):
    """Ambiguous YAML mapping could conceal an executable action step."""


def verify_action_key_shape(source: str) -> int:
    """Check six conventional action keys; reject alternate YAML spellings.

    This validator deliberately fails closed on ambiguous uses occurrences,
    even in an apparent shell string: code review can resolve false positives.
    """
    if (type(source) is not str or "\x00" in source or "\t" in source
            or len(source.encode("utf-8")) > MAX_WORKFLOW_BYTES):
        raise ActionKeyError("Invalid desktop workflow")
    count = 0
    for line in source.splitlines():
        if line.lstrip().startswith("#"):
            continue
        if (MERGE_KEY.search(line) or EXPLICIT_KEY.search(line)
                or ESCAPED_KEY.search(line)):
            raise ActionKeyError("Ambiguous YAML action mapping")
        if KEY_HINT.search(line):
            if CANONICAL.fullmatch(line) is None:
                raise ActionKeyError("Noncanonical YAML action source key")
            count += 1
    if count != 6:
        raise ActionKeyError("Expected six explicit YAML action source keys")
    return count
