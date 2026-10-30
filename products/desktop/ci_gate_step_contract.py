"""Fail closed when a desktop CI source-gate step can silently skip execution.

R58 pins executed shell statements, not just the presence of a command string.
A command present after exit 0 or inside a here-document is not evidence
of a source test. This is a deliberately small contract for the two existing
workflow steps, not an arbitrary YAML parser or Windows release approval.
"""
from __future__ import annotations

import re

LINUX_COMMANDS = (
    '          mkdir -p "$RUNNER_TEMP/fvs-source"',
    '          python products/desktop/scripts/offline_source_gate.py --report "$RUNNER_TEMP/fvs-source/offline-source-suite.json"',
)
WINDOWS_PREFIX = (
    '          $env:PYTHONPATH = "products/desktop"',
    '          python products/desktop/scripts/offline_source_gate.py',
)
WINDOWS_EXIT_GUARD = re.compile(
    r'          if \(\$LASTEXITCODE -ne 0\) \{ throw "[A-Za-z0-9 .,!?():-]{1,120}" \}'
)
MAX_STEP_BYTES = 2048


class GateStepError(ValueError):
    """The required source suite is not an unconditional, exact shell step."""


def verify_gate_step(step: str, platform: str) -> None:
    """Require one short, known-good source-gate shell body with no extra code.

    This rejects prepended/embedded exit 0, shell pipelines, conditionals,
    here-documents, command substitution, duplicate YAML keys, and appended
    steps able to mask the source verifier. New CI semantics require review.
    """
    if (type(step) is not str or platform not in ('linux', 'windows')
            or '\x00' in step or '\t' in step or '\r' in step
            or len(step.encode('utf-8')) > MAX_STEP_BYTES):
        raise GateStepError('Unrecognized source gate step')
    lines = step.splitlines()
    if (not lines or not lines[0].startswith('      - name: ')
            or not 0 < len(lines[0].split(': ', 1)[1]) <= 120):
        raise GateStepError('Source gate step missing an explicit name')
    if platform == 'linux':
        if lines[1:] != ['        run: |', *LINUX_COMMANDS]:
            raise GateStepError('Linux source-gate shell body differs from reviewed commands')
    else:
        if (len(lines) != 6
                or lines[1:3] != ['        shell: pwsh', '        run: |']
                or tuple(lines[3:5]) != WINDOWS_PREFIX
                or not WINDOWS_EXIT_GUARD.fullmatch(lines[5])):
            raise GateStepError('Windows source-gate shell body differs from reviewed commands')
