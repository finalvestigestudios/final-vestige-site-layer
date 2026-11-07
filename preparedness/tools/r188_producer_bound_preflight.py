#!/usr/bin/env python3
"""R188 recommended entrypoint: source-code custody BEFORE R186 native execution.

This is a trusted-code diagnostic, not a hostile-code sandbox or safety approval.
It cannot authorize public release, WordPress writes, merchant links or QD PASS.
No new executable is run if a pinned producer differs from its Git identity.
"""
from __future__ import annotations

import argparse
from importlib import util
import json
from pathlib import Path

SCHEMA = 'fv-preparedness-r188-producer-bound-preflight-v1'
HOLD = 'DRAFT_HARD_HOLD'
INVALID = 'INVALID_HARD_HOLD'


def _load(path: Path, name: str):
    if not path.is_file() or path.is_symlink():
        raise ValueError('missing/unsafe trusted local module: ' + name)
    spec = util.spec_from_file_location('_fv_r188_' + name, path)
    if spec is None or spec.loader is None:
        raise ValueError('cannot import local module: ' + name)
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def preflight(repo: Path, timeout: int = 300, *, synthetic_pins=None) -> dict:
    """Fail-closed wrapper; `synthetic_pins` is for offline tests only.

    The command-line path deliberately NEVER accepts mutable pins or manifests.
    """
    packet = {'schema': SCHEMA, 'state': INVALID,
              'publication_authorized': False, 'independent_qd_pass': False,
              'merchant_offer_verified': False, 'native_structural_checks_complete': False,
              'checks': [], 'source_pin_baseline':
                  'c881583358c485dcc02ca69e6cc275cd395a287a'}
    try:
        if (type(timeout) is not int or not (10 <= timeout <= 1200) or
            not repo.is_dir() or repo.is_symlink()):
            raise ValueError('invalid trusted checkout or timeout')
        tool_dir = repo / 'preparedness' / 'tools'
        pinned = _load(tool_dir / 'r188_producer_code_custody_gate.py', 'r188_code')
        proof = pinned.verify(repo / 'preparedness', synthetic_pins)
        if (proof.get('state') != HOLD or proof.get('publication_authorized') is not False or
            proof.get('independent_qd_pass') is not False or
            proof.get('native_build_executed') is not False):
            raise ValueError('R188 producer custody returned false clearance')
        packet['producer_code'] = proof
        native = _load(tool_dir / 'r186_whole_archive_preflight.py', 'r186_native')
        result = native.preflight(repo, timeout)
        if not isinstance(result, dict) or result.get('state') not in (HOLD, INVALID):
            raise ValueError('R186 native pipeline emitted an unsupported state')
        if result.get('publication_authorized') is not False or result.get('independent_qd_pass') is not False:
            raise ValueError('R186 native pipeline falsely cleared publication/QD')
        packet['native'] = result
        packet['state'] = result['state']
        packet['checks'] = result.get('checks', [])
        if packet['state'] == INVALID:
            packet['blocker'] = 'R186 native build/validation/safety custody incomplete'
        else:
            packet['native_structural_checks_complete'] = True  # structural executions ONLY, not safety approval.
    except (OSError, ValueError, TypeError, KeyError, ImportError, AttributeError) as exc:
        packet['blocker'] = str(exc)[:300]
    return packet


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path('.'))
    parser.add_argument('--timeout', type=int, default=300)
    args = parser.parse_args(argv)
    print(json.dumps(preflight(args.repo, args.timeout), sort_keys=True))
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
