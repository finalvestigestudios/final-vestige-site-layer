#!/usr/bin/env python3
"""Fail-closed runtime gate for the unpublished WordPress Playground CI.

Only local Node/npm versions are inspected. No WordPress.com endpoint, secret,
user database, filesystem export, or production CMS write is involved.
"""
from __future__ import annotations
import re
import subprocess
import sys

CLI_SPEC = '@wp-playground/cli@3.1.61'
MIN_NODE = (24, 18, 0)
MIN_NPM = (11, 16, 0)


def parse_version(value: str, label: str) -> tuple[int, int, int]:
    if not isinstance(value, str):
        raise ValueError(f'{label} VERSION_UNREADABLE')
    match = re.fullmatch(r'v?(\d+)\.(\d+)\.(\d+)', value.strip())
    if not match:
        raise ValueError(f'{label} VERSION_UNREADABLE')
    return tuple(int(part) for part in match.groups())


def verify_versions(node_version: str, npm_version: str) -> None:
    node = parse_version(node_version, 'NODE')
    npm = parse_version(npm_version, 'NPM')
    if node < MIN_NODE or npm < MIN_NPM:
        raise ValueError('PLAYGROUND_UNSUPPORTED_NODE_NPM_ENGINE')


def verify_cli_argv(argv: object) -> None:
    if not isinstance(argv, list) or argv[:3] != ['npx', CLI_SPEC, 'server']:
        raise ValueError('PLAYGROUND_UNPINNED_OR_UNEXPECTED_CLI')


def main() -> int:
    try:
        node = subprocess.check_output(['node', '--version'], text=True, timeout=10).strip()
        npm = subprocess.check_output(['npm', '--version'], text=True, timeout=10).strip()
        verify_versions(node, npm)
        print(f'PLAYGROUND_ENGINE_SUPPORTED node={node} npm={npm} cli={CLI_SPEC}')
        return 0
    except (OSError, ValueError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        print('PLAYGROUND_ENGINE_UNSUPPORTED_OR_UNAVAILABLE; no staging executed', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
