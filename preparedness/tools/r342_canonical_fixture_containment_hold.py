#!/usr/bin/env python3
"""R342: fail-closed audit fence for source-mutation during QA fixtures.

This standalone test-only runner is intentionally NOT a publication, QD, or
citation-support gate. It protects the 35-article + six-tool source checkout
against transient file writes by tests; final hash equality alone would miss
write-then-restore races. It has no WordPress/network operations.

Run from a complete native checkout (read only until --execute-suite):
  python -I preparedness/tools/r342_canonical_fixture_containment_hold.py
  python -I preparedness/tools/r342_canonical_fixture_containment_hold.py --execute-suite

CAVEAT: Python audit hooks do not sandbox native code, external child processes,
or preexisting file descriptors. They complement, not replace, source custody,
permission isolation, full build validation or human claim review.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import unittest

SCHEMA = 'fv-preparedness-r342-canonical-fixture-containment-v1'
PROTECTED_DIRS = ('content', 'sources', 'templates', 'assets')
PROTECTED_FILES = ('taxonomy.json',)
REQUIRED_SOURCE_DIRS = ('content/articles', 'content/tools', 'sources')
REQUIRED_FILES = ('taxonomy.json', 'sources/register.json')
FINAL_HOLD_FIELDS = {
    'may_merge': False, 'may_publish': False,
    'qualified_qd_pass': False, 'source_claim_support_verified': False,
    'native_100_export_build_verified': False, 'paid_sku_verified': False,
    'paid_orders_verified': False, 'net_revenue_verified': False,
}


def _within(candidate: Path, parent: Path) -> bool:
    return candidate == parent or parent in candidate.parents


def _absolute_variants(path: str | bytes | os.PathLike | int, cwd: Path) -> tuple[Path, ...]:
    """Both lexical and resolved paths: stop symlink-in and symlink-out escapes."""
    if isinstance(path, int) or not isinstance(path, (str, bytes, os.PathLike)):
        return ()
    try:
        p = Path(os.fsdecode(path))
        if not p.is_absolute():
            p = cwd / p
        lexical = Path(os.path.abspath(p))
        resolved = lexical.resolve(strict=False)
        return (lexical, resolved)
    except (OSError, ValueError, RuntimeError):
        # Fail closed when the file path cannot be reliably interpreted.
        raise PermissionError('UNRESOLVED_AUDIT_TARGET')


def protected_target(path: str | bytes | os.PathLike | int, prep_root: Path, cwd: Path | None = None) -> bool:
    """Only mutable source inputs (not build outputs, tests or audits) are fenced."""
    root = prep_root.resolve(strict=False)
    working = cwd or Path.cwd()
    for candidate in _absolute_variants(path, working):
        if any(_within(candidate, root / d) for d in PROTECTED_DIRS):
            return True
        if candidate in (root / p for p in PROTECTED_FILES):
            return True
    return False


def _write_open_mode(mode: object, flags: object) -> bool:
    if isinstance(mode, str) and set(mode).intersection('wax+'):
        return True
    if isinstance(flags, int):
        mask = os.O_WRONLY | os.O_RDWR | os.O_APPEND | os.O_CREAT | os.O_TRUNC | os.O_EXCL
        return bool(flags & mask)
    # Unknown modes/flags must not be counted as proof that a write is safe.
    return mode not in (None, 'r', 'rb', 'rt') and not isinstance(mode, str)


class SourceMutationGuard:
    """Audit-hook callback; install BEFORE importing/starting QA tests."""

    def __init__(self, prep_root: Path):
        self.prep_root = prep_root.resolve(strict=False)
        self.blocked: list[str] = []
        self.observed_events = 0

    def _deny(self, event: str, path: object) -> None:
        if protected_target(path, self.prep_root):
            target = os.fsdecode(path) if isinstance(path, (str, bytes, os.PathLike)) else '<fd>'
            self.blocked.append(event + ':' + target)
            raise PermissionError('CANONICAL_PREPAREDNESS_SOURCE_WRITE_BLOCKED')

    def inspect(self, event: str, args: tuple) -> None:
        self.observed_events += 1
        if event == 'open':
            if len(args) >= 3 and _write_open_mode(args[1], args[2]):
                self._deny(event, args[0])
        elif event in ('os.remove', 'os.unlink', 'os.rmdir', 'os.mkdir',
                       'os.chmod', 'os.chown', 'os.utime', 'os.truncate'):
            if args:
                self._deny(event, args[0])
        elif event in ('os.rename', 'os.replace', 'os.link', 'os.symlink'):
            # Both source and destination: prohibits a temporary escape followed by restore.
            if len(args) >= 2:
                self._deny(event + '.src', args[0])
                self._deny(event + '.dst', args[1])
        elif event == 'os.chdir' and args:
            # Do not allow test to change into protected sources to evade relative-path audits.
            self._deny(event, args[0])


def inventory(prep_root: Path) -> dict[str, str]:
    """Digest every original source input; reject symlinks and missing source roots."""
    p = prep_root.resolve(strict=False)
    if not p.is_dir():
        raise ValueError('NATIVE_PREPAREDNESS_ROOT_MISSING')
    for rel in REQUIRED_SOURCE_DIRS:
        target = p / rel
        if target.is_symlink() or not target.is_dir():
            raise ValueError('REQUIRED_NATIVE_SOURCE_DIRECTORY_MISSING:' + rel)
    for rel in REQUIRED_FILES:
        target = p / rel
        if target.is_symlink() or not target.is_file():
            raise ValueError('REQUIRED_NATIVE_SOURCE_FILE_MISSING:' + rel)
    expected = {'articles': 35, 'tools': 6}
    for kind, count in expected.items():
        bodies = list((p / 'content' / kind).glob('*.body.html'))
        metas = list((p / 'content' / kind).glob('*.meta.json'))
        body_slugs = {q.name[:-10] for q in bodies}
        meta_slugs = {q.name[:-10] for q in metas}
        if len(bodies) != count or len(metas) != count or body_slugs != meta_slugs:
            raise ValueError('NATIVE_35_ARTICLE_6_TOOL_BODY_METADATA_COVERAGE_MISMATCH:' + kind)
        if len(body_slugs) != count or not all(re.fullmatch(r'[a-z0-9-]+', s) for s in body_slugs):
            raise ValueError('NATIVE_ARTICLE_TOOL_SLUG_DUPLICATION_OR_PATH_INVALID:' + kind)
    files: dict[str, str] = {}
    for rel in list(PROTECTED_DIRS) + list(PROTECTED_FILES):
        target = p / rel
        if not target.exists():
            continue
        candidates = target.rglob('*') if target.is_dir() else [target]
        for item in candidates:
            if item.is_symlink():
                raise ValueError('SYMLINK_SOURCE_MUTATION_BYPASS:' + item.relative_to(p).as_posix())
            if not item.is_file():
                continue
            key = item.relative_to(p).as_posix()
            if key in files:
                raise ValueError('DUPLICATE_SOURCE_PATH:' + key)
            files[key] = hashlib.sha256(item.read_bytes()).hexdigest()
    if not files:
        raise ValueError('EMPTY_NATIVE_SOURCE_INVENTORY')
    return dict(sorted(files.items()))


def report(errors: list[str], before: dict[str, str] | None = None,
           after: dict[str, str] | None = None, tests: dict | None = None,
           blocked: list[str] | None = None) -> dict:
    return {
        'schema': SCHEMA, 'state': 'INVALID_HARD_HOLD' if errors else 'DRAFT_HARD_HOLD',
        'errors': sorted(set(errors)), 'protected_source_count': len(before or {}),
        'source_sha256_manifest': before or {},
        'source_unchanged_after_tests': before is not None and after is not None and before == after,
        'transient_source_write_attempts_blocked': len(blocked or []),
        'attempted_write_events': blocked or [], 'tests': tests or {},
        'scope': 'READ_ONLY_SOURCE_CUSTODY_PLUS_TEST_AUDIT_HOOK_NOT_QD_OR_PUBLISH_APPROVAL',
        'known_gaps': ['native-code and subprocess write bypass not prevented by Python audit hook',
                       'Python-level audit is not a filesystem permission sandbox',
                       'passing test integrity does not verify citation-to-claim support',
                       'native WordPress export build/approval is a separate gate'],
        'legacy_editorial_conflicts_unresolved': 15,
        'original_article15_tool104_claims_unresolved': 17,
        **FINAL_HOLD_FIELDS,
    }


def run(root: Path, execute_suite: bool = False, pattern: str = 'test*.py',
        require_native_witness: bool = True) -> dict:
    """Run tests in this process with audit installed; no CMS, network, or deployment."""
    prep = (root / 'preparedness').resolve(strict=False)
    try:
        before = inventory(prep)
    except (OSError, ValueError) as exc:
        return report(['AUTHENTIC_NATIVE_SOURCE_INVENTORY_REQUIRED:' + str(exc)])
    # Isolated Python excludes both CWD and script dir; make only the authenticated
    # checkout roots importable before witness/test discovery, never test fixture paths.
    for module_root in (str(root.resolve()), str(prep / 'tools')):
        if module_root not in sys.path:
            sys.path.insert(0, module_root)
    if require_native_witness:
        try:
            from r341_nine_branch_conflict_review_hold import audit_native
            custody = audit_native(root)
            if custody['state'] != 'DRAFT_HARD_HOLD':
                return report(['R341_FROZEN_9_HEAD_SOURCE_WITNESS_FAILED'] + custody.get('errors', []), before)
        except (ImportError, OSError, ValueError, KeyError, TypeError) as exc:
            return report(['R341_FROZEN_9_HEAD_SOURCE_WITNESS_UNAVAILABLE:' + type(exc).__name__], before)
    if not execute_suite:
        return report([], before, before, {'executed': False, 'passed': None})
    tests_dir = prep / 'tests'
    if not tests_dir.is_dir() or not re.fullmatch(r'test[a-zA-Z0-9_*.]*\.py', pattern):
        return report(['NATIVE_TEST_DIRECTORY_OR_PATTERN_INVALID'], before)
    guard = SourceMutationGuard(prep)
    # Python auditing is process-global. Never install after test discovery.
    sys.addaudithook(guard.inspect)
    sys.path.insert(0, str(prep / 'tools'))
    try:
        suite = unittest.defaultTestLoader.discover(start_dir=str(tests_dir), pattern=pattern)
        count = suite.countTestCases()
        result = unittest.TextTestRunner(verbosity=1, stream=sys.stderr).run(suite)
        tests = {'executed': True, 'count': count, 'run': result.testsRun,
                 'failures': len(result.failures), 'errors': len(result.errors),
                 'skipped': len(result.skipped), 'successful': result.wasSuccessful()}
        errors = [] if result.wasSuccessful() and count >= 36 else ['NATIVE_SUITE_FAILED_OR_UNDER_36_TESTS']
    except BaseException as exc:  # report even when suite loader itself faults
        errors = ['NATIVE_TEST_RUNNER_EXCEPTION:' + type(exc).__name__]
        tests = {'executed': True, 'successful': False}
    try:
        after = inventory(prep)
        if after != before:
            errors.append('NATIVE_CANONICAL_SOURCE_CHANGED_DURING_SUITE')
    except (OSError, ValueError) as exc:
        after = None
        errors.append('NATIVE_POSTTEST_SOURCE_INVENTORY_INVALID:' + str(exc))
    if guard.blocked:
        errors.append('TRANSIENT_CANONICAL_SOURCE_MUTATION_ATTEMPT_DETECTED')
    return report(errors, before, after, tests, guard.blocked)


def main() -> int:
    p = argparse.ArgumentParser(description='R342 canonical fixture containment test fence; NEVER a release PASS')
    p.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[2])
    p.add_argument('--execute-suite', action='store_true')
    p.add_argument('--pattern', default='test*.py')
    args = p.parse_args()
    out = run(args.repo_root, args.execute_suite, args.pattern)
    # Do not print a huge manifest in routine CLI summary; full manifest is available in Python API.
    out.pop('source_sha256_manifest', None)
    print(json.dumps(out, indent=2, sort_keys=True))
    return 1 if out['state'] == 'INVALID_HARD_HOLD' else 2


if __name__ == '__main__':
    raise SystemExit(main())
