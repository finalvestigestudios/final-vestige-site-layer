"""Pin six-app Python/build inputs before packaging; reject observed changes.

A process-bound source-custody check, not a signature, build reproducibility
proof, native Windows smoke, malware clearance, QD approval or release permit.
No financial/customer files or local absolute paths are serialized.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path, PurePosixPath
import stat
import sys

DESKTOP = Path(__file__).resolve().parents[1]
ROOT = DESKTOP.parents[1]
for folder in (str(DESKTOP), str(DESKTOP / 'scripts')):
    if folder not in sys.path:
        sys.path.insert(0, folder)

import source_smoke_gate as source_gate
from report_evidence import prepare_report_path, publish_report

SCHEMA = 'fvs-build-input-custody-v1'
EXTRA_BUILD_FILES = (
    'products/desktop/scripts/verify-windows-candidate.ps1',
    '.github/workflows/desktop-build.yml',
)
MAX_MANIFEST_BYTES = 256 * 1024
MAX_INPUT_FILES = source_gate.MAX_SOURCE_FILES + len(EXTRA_BUILD_FILES)
SAFE_ERROR = 'REJECTED: desktop build-input custody could not be verified'


def _stat_identity(path: Path) -> list[int]:
    try:
        info = path.lstat()
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise ValueError('unsafe build input')
        return list(source_gate._identity(info))
    except (OSError, RuntimeError):
        raise ValueError('unsafe build input') from None


def _same_path_descriptor_identity(path_identity: list[int],
                                   descriptor_identity: list[int],
                                   *, windows: bool | None = None) -> bool:
    """Keep complete per-view custody despite Windows lstat/fstat ctime drift."""
    if windows is None:
        windows = os.name == 'nt'
    return (path_identity[:-1] == descriptor_identity[:-1] if windows
            else path_identity == descriptor_identity)


def snapshot(root: Path) -> dict:
    """Capture complete Python source inventory plus two build-control files."""
    root = Path(root).resolve(strict=True)
    python_inputs = source_gate.source_inventory(root)
    identities = source_gate._source_metadata(root, python_inputs)
    entries = [
        {'path': item['path'], 'sha256': item['sha256'],
         'identity': list(identity)}
        for item, identity in zip(python_inputs, identities, strict=True)
    ]
    for relative in EXTRA_BUILD_FILES:
        path = root / relative
        source_gate._checked_directory(path.parent, root)
        before = _stat_identity(path)
        digest = source_gate._fingerprint(path, root)
        if _stat_identity(path) != before:
            raise ValueError('build control changed during fingerprint')
        entries.append({'path': relative, 'sha256': digest, 'identity': before})
    entries.sort(key=lambda item: item['path'])
    if (not 2 < len(entries) <= MAX_INPUT_FILES or
            len({entry['path'] for entry in entries}) != len(entries)):
        raise ValueError('incomplete build input inventory')
    return {
        'schema': SCHEMA,
        'scope': 'PYTHON_AND_EXPLICIT_BUILD_CONTROLS_ONLY_NOT_BINARY_VERIFICATION',
        'released': False,
        'qd_approved': False,
        'premium_download_authorized': False,
        'windows_executables_verified': False,
        'inputs': entries,
    }


def _manifest_path(path: Path, root: Path) -> Path:
    """Only outside-checkout, preexisting parent; never follow final symlinks."""
    root = Path(root).resolve(strict=True)
    parent = path.parent.resolve(strict=True)
    if not parent.is_dir() or parent == root or root in parent.parents:
        raise ValueError('unsafe custody manifest location')
    return parent / path.name


def capture(root: Path, destination: Path) -> None:
    root = Path(root).resolve(strict=True)
    target = prepare_report_path(destination, root)
    state = snapshot(root)
    if snapshot(root) != state:
        raise ValueError('source changed during capture')
    publish_report(target, state)  # exclusive, atomic, no overwrite
    # No success evidence if the source changed as the report was published.
    if snapshot(root) != state:
        raise ValueError('source changed after capture')


def _read_manifest(path: Path, root: Path) -> dict:
    path = _manifest_path(Path(path), root)
    fd = None
    try:
        before = _stat_identity(path)
        if before[4] > MAX_MANIFEST_BYTES:
            raise ValueError('oversized custody manifest')
        flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_BINARY', 0)
        fd = os.open(path, flags)
        opened = list(source_gate._identity(os.fstat(fd)))
        if not _same_path_descriptor_identity(before, opened):
            raise ValueError('custody manifest replaced')
        payload = bytearray()
        while len(payload) <= MAX_MANIFEST_BYTES:
            chunk = os.read(fd, min(65536, MAX_MANIFEST_BYTES + 1 - len(payload)))
            if not chunk:
                break
            payload.extend(chunk)
        if (len(payload) != before[4] or len(payload) > MAX_MANIFEST_BYTES or
                list(source_gate._identity(os.fstat(fd))) != opened or
                _stat_identity(path) != before):
            raise ValueError('custody manifest changed')
        def no_duplicate_keys(pairs):
            data = {}
            for key, val in pairs:
                if key in data:
                    raise ValueError('duplicate custody manifest key')
                data[key] = val
            return data
        manifest = json.loads(payload.decode('utf-8'), object_pairs_hook=no_duplicate_keys)
        if type(manifest) is not dict or set(manifest) != {
            'schema', 'scope', 'released', 'qd_approved',
            'premium_download_authorized', 'windows_executables_verified', 'inputs'
        } or manifest['schema'] != SCHEMA or any(
            manifest[name] is not False for name in (
                'released', 'qd_approved', 'premium_download_authorized',
                'windows_executables_verified')
        ) or manifest['scope'] != snapshot_scope():
            raise ValueError('invalid custody manifest schema')
        inputs = manifest['inputs']
        if type(inputs) is not list or not 2 < len(inputs) <= MAX_INPUT_FILES:
            raise ValueError('invalid custody manifest inventory')
        previous = ''
        for item in inputs:
            if type(item) is not dict or set(item) != {'path', 'sha256', 'identity'}:
                raise ValueError('invalid custody manifest entry')
            name, digest, identity = item['path'], item['sha256'], item['identity']
            if (type(name) is not str or not previous < name or
                    PurePosixPath(name).is_absolute() or
                    any(part in ('', '.', '..') for part in name.split('/')) or
                    type(digest) is not str or len(digest) != 64 or
                    any(ch not in '0123456789abcdef' for ch in digest) or
                    type(identity) is not list or len(identity) != 7 or
                    any(type(n) is not int or n < 0 for n in identity)):
                raise ValueError('invalid custody manifest entry values')
            previous = name
        return manifest
    except (OSError, UnicodeError, json.JSONDecodeError):
        raise ValueError('invalid or unsafe custody manifest') from None
    finally:
        if fd is not None:
            os.close(fd)


def snapshot_scope() -> str:
    return 'PYTHON_AND_EXPLICIT_BUILD_CONTROLS_ONLY_NOT_BINARY_VERIFICATION'


def check(root: Path, manifest_path: Path) -> None:
    root = Path(root).resolve(strict=True)
    expected = _read_manifest(manifest_path, root)
    if snapshot(root) != expected:
        raise ValueError('packaging source or controls changed')


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('capture', 'check'))
    parser.add_argument('manifest', type=Path, help='private JSON outside the source checkout')
    parser.add_argument('--root', type=Path, default=ROOT,
                        help='trusted source root (testing only)')
    args = parser.parse_args(argv)
    try:
        if args.action == 'capture':
            capture(args.root, args.manifest)
        else:
            check(args.root, args.manifest)
    except (OSError, RuntimeError, ValueError, TypeError):
        print(SAFE_ERROR, file=sys.stderr)
        return 1
    print('PASS: desktop build inputs unchanged; NOT EXE/QD/distribution approval')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
