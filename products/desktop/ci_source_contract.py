"""Require complete normal/-OO source provenance before six-app CI packaging.

This is a deliberately narrow validator for the two known GitHub Actions jobs.
It does not parse arbitrary YAML, validate binaries, or grant QD release approval.
Unknown job shapes and fail-open conditional execution must be reviewed first.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

from ci_gate_step_contract import GateStepError, verify_gate_step
from ci_action_pin_guard import ActionPinError, verify_action_pins

MAX_WORKFLOW_BYTES = 128 * 1024
SOURCE_CMD = 'python products/desktop/scripts/offline_source_gate.py --report "$RUNNER_TEMP/fvs-source/offline-source-suite.json"'
WINDOWS_CMD = 'python products/desktop/scripts/offline_source_gate.py'
POLICY_CMD = 'python products/desktop/ci_source_contract.py .github/workflows/desktop-build.yml'
JOBS = ('source-tests', 'windows-build')
JOB_START = re.compile(r'^  ([a-z][a-z0-9-]*):\s*$')
STEP_START = re.compile(r'^      - (?:name|uses):\s*')
YAML_CONDITION = re.compile(r'^\s*(?:if|continue-on-error):\s*', re.MULTILINE)


class SourceContractError(ValueError):
    """Cannot certify mandatory, nonconditional two-mode source checks."""


def _jobs(source: str) -> dict[str, str]:
    lines = source.splitlines()
    if lines.count('jobs:') != 1:
        raise SourceContractError('Missing or ambiguous jobs tree')
    position = lines.index('jobs:') + 1
    blocks: dict[str, list[str]] = {}
    current: str | None = None
    for line in lines[position:]:
        if line and not line.startswith((' ', '#')):
            break
        match = JOB_START.match(line)
        if match:
            current = match.group(1)
            if current in blocks:
                raise SourceContractError('Duplicate CI job')
            blocks[current] = [line]
        elif current is not None:
            blocks[current].append(line)
        elif line.strip() and not line.lstrip().startswith('#'):
            raise SourceContractError('Unrecognized CI job syntax')
    if set(blocks) != set(JOBS):
        raise SourceContractError('Unexpected desktop CI job configuration')
    return {name: '\n'.join(lines) for name, lines in blocks.items()}


def _steps(job: str) -> list[str]:
    lines = job.splitlines()
    chunks: list[list[str]] = []
    for line in lines:
        if STEP_START.match(line):
            chunks.append([line])
        elif chunks:
            chunks[-1].append(line)
    if not chunks:
        raise SourceContractError('Job has no steps')
    return ['\n'.join(chunk) for chunk in chunks]


def _command_steps(steps: list[str], literal: str) -> list[int]:
    return [i for i, block in enumerate(steps) if any(
        line in ('          ' + literal, '        run: ' + literal)
        for line in block.splitlines())]


def verify_workflow(source: str) -> int:
    if (type(source) is not str or '\x00' in source or '\t' in source or
            len(source.encode('utf-8')) > MAX_WORKFLOW_BYTES):
        raise SourceContractError('Untrusted workflow contents')
    try:
        verify_action_pins(source)
    except ActionPinError as exc:
        raise SourceContractError('Untrusted mutable or missing GitHub Action') from exc
    jobs = _jobs(source)
    for name, runner in (('source-tests', 'ubuntu-24.04'),
                         ('windows-build', 'windows-latest')):
        job = jobs[name]
        if YAML_CONDITION.search(job) or '|| true' in job or '|| $true' in job:
            raise SourceContractError('CI source verification may not be conditional or ignored')
        if len(re.findall(r'^    runs-on: ' + re.escape(runner) + r'$', job, re.M)) != 1:
            raise SourceContractError('Unrecognized CI runner assignment')
        steps = _steps(job)
        policy_steps = _command_steps(steps, POLICY_CMD)
        if len(policy_steps) != 1:
            raise SourceContractError('Required CI source contract preflight missing')
        if name == 'source-tests':
            provenance = _command_steps(steps, SOURCE_CMD)
            if len(provenance) != 1 or policy_steps[0] >= provenance[0]:
                raise SourceContractError('Full Linux source evidence gate missing')
            evidence_step = steps[provenance[0]]
            try:
                verify_gate_step(evidence_step, 'linux')
            except GateStepError as exc:
                raise SourceContractError('Untrusted Linux source-gate commands') from exc
            if ('mkdir -p "$RUNNER_TEMP/fvs-source"' not in evidence_step or
                    'run: |' not in evidence_step):
                raise SourceContractError('Private Linux evidence directory not established')
            if not any('uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02' in step for step in steps[provenance[0] + 1:]):
                raise SourceContractError('Linux provenance evidence is not retained')
        else:
            provenance = _command_steps(steps, WINDOWS_CMD)
            if len(provenance) != 1 or policy_steps[0] >= provenance[0]:
                raise SourceContractError('Full Windows source evidence gate missing')
            command_step = steps[provenance[0]]
            try:
                verify_gate_step(command_step, 'windows')
            except GateStepError as exc:
                raise SourceContractError('Untrusted Windows source-gate commands') from exc
            if ('shell: pwsh' not in command_step or
                    'if ($LASTEXITCODE -ne 0) { throw ' not in command_step):
                raise SourceContractError('Windows source gate may ignore failure')
            build_steps = [i for i, step in enumerate(steps)
                           if 'name: Build six standalone Windows executables' in step]
            if len(build_steps) != 1 or provenance[0] >= build_steps[0]:
                raise SourceContractError('Windows packaging precedes source verification')
    return len(jobs)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('workflow', type=Path)
    args = parser.parse_args(argv)
    try:
        if args.workflow.stat().st_size > MAX_WORKFLOW_BYTES:
            raise SourceContractError('Oversized workflow')
        validated = verify_workflow(args.workflow.read_text(encoding='utf-8'))
    except (OSError, UnicodeError, SourceContractError):
        print('REJECTED: mandatory desktop source provenance gate unavailable', file=sys.stderr)
        return 1
    print(f'PASS: {validated} mandatory normal/-OO source CI jobs; NOT Windows EXE/QD/release approval')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
