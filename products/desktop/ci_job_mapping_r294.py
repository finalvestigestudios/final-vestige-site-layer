"""Strict, lexical job-mapping custody for the reviewed desktop CI workflow.

Only the explicitly reviewed source-test and Windows-build job shapes are
accepted. This guards against YAML duplicate/alternate job keys that could
shadow validated steps. It is not a general YAML parser or release approval.
"""
from __future__ import annotations


class JobMappingError(ValueError):
    """An unreviewed job-level YAML key could change executable CI behavior."""


# The historic R57 contract fixture uses the two-field forms. The deployed
# workflow also pins the runner timeout and source-only PYTHONPATH environment.
REVIEWED_SHAPES = {
    "source-tests": (
        ("    runs-on: ubuntu-24.04", "    steps:"),
        ("    runs-on: ubuntu-24.04", "    timeout-minutes: 20",
         "    env:", "    steps:"),
    ),
    "windows-build": (
        ("    runs-on: windows-latest", "    steps:"),
        ("    runs-on: windows-latest", "    timeout-minutes: 45",
         "    steps:"),
    ),
}


def verify_job_mapping(name: str, lines: list[str]) -> None:
    """Reject unexpected job-level mappings, including duplicate YAML keys.

    ``lines`` includes the two-space job heading followed by its body. A
    four-space, non-comment token is a direct child mapping key; exact source
    lines, cardinality and order must match a reviewed shape. Contents nested
    six or more spaces are independently checked by the existing CI guards.
    """
    if type(name) is not str or type(lines) is not list or name not in REVIEWED_SHAPES:
        raise JobMappingError("Unreviewed desktop CI job")
    if not lines or lines[0] != f"  {name}:":
        raise JobMappingError("Unreviewed desktop CI job heading")
    observed: list[str] = []
    for line in lines[1:]:
        if type(line) is not str:
            raise JobMappingError("Unreviewed desktop CI job entry")
        # A four-space YAML mapping key is distinct from a nested step (6+).
        # Unquoted/quoted/space-before-colon/alias/merge-key forms are all
        # rejected because they are not members of an exact reviewed shape.
        if line.startswith("    ") and len(line) > 4 and line[4] not in " \t":
            if line[4] != "#":
                observed.append(line)
    if tuple(observed) not in REVIEWED_SHAPES[name]:
        raise JobMappingError("Unreviewed or duplicate desktop CI job keys")
