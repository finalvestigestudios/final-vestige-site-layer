"""R391: read-only, inode-stable evidence snapshot around ALL rendered audits.

The export bundle may change between R386, R387 and R390 passes. This gate
records each original/private export's SHA-256, identity and metadata before
and after the complete independent audit callback, rejects races or replaced
files, and binds R390's per-file checksums to exactly that snapshot. It cannot
clear QD, medical, child privacy, emergency, merchant or publication review.
"""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import re
import stat

SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\.html\Z')
DIGEST = re.compile(r'[a-f0-9]{64}\Z')
SIZE_MAX = 3_000_000


def _snapshot(path: Path):
    """No-follow, fd-relative bounded immutable-by-observation inventory."""
    flags = os.O_RDONLY | getattr(os, 'O_DIRECTORY', 0) | getattr(os, 'O_NOFOLLOW', 0)
    fd = os.open(path, flags)
    try:
        ds = os.fstat(fd)
        if not stat.S_ISDIR(ds.st_mode):
            raise ValueError('NOT_DIRECTORY')
        files = {}
        names = sorted(os.listdir(fd))
        for name in names:
            if not SLUG.fullmatch(name):
                raise ValueError('UNSAFE_FILENAME_OR_UNEXPECTED_ENTRY')
            filefd = os.open(name, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) |
                             getattr(os, 'O_NONBLOCK', 0), dir_fd=fd)
            try:
                before = os.fstat(filefd)
                if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or not 0 < before.st_size <= SIZE_MAX:
                    raise ValueError('INVALID_OR_HARDLINKED_FILE')
                h = sha256()
                total = 0
                while True:
                    chunk = os.read(filefd, min(64 * 1024, SIZE_MAX + 1 - total))
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > SIZE_MAX:
                        raise ValueError('GROWING_OR_OVERSIZED_FILE')
                    h.update(chunk)
                after = os.fstat(filefd)
                named = os.stat(name, dir_fd=fd, follow_symlinks=False)
                ident = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns, s.st_nlink)
                if ident(before) != ident(after) or ident(after) != ident(named) or total != after.st_size:
                    raise ValueError('FILE_MUTATED_DURING_READ')
                files[name[:-5]] = {'sha256': h.hexdigest(), 'size': total,
                                     'identity': list(ident(after))}
            finally:
                os.close(filefd)
        current = os.fstat(fd)
        if (ds.st_dev, ds.st_ino, ds.st_mtime_ns, ds.st_ctime_ns) != (
                current.st_dev, current.st_ino, current.st_mtime_ns, current.st_ctime_ns):
            raise ValueError('DIRECTORY_MUTATED_DURING_SCAN')
        return {'directory_identity': [ds.st_dev, ds.st_ino], 'files': files}
    finally:
        os.close(fd)


def audit_frozen(wp_dir: Path, preview_dir: Path, original_slugs, audit_callback) -> dict:
    """Callback must perform R386 + R387 + R390 on the SAME snapshot window."""
    errors = []
    reports = {}
    before = {}
    after = {}
    try:
        original = list(original_slugs)
        if (len(original) != 35 or len(set(original)) != 35 or
                any(not isinstance(s, str) or not SLUG.fullmatch(s + '.html') for s in original)):
            raise ValueError('NOT_AUTHENTIC_35_SLUG_SET')
        before = {'wp': _snapshot(Path(wp_dir)), 'preview': _snapshot(Path(preview_dir))}
        first_wp, first_pv = before['wp']['files'], before['preview']['files']
        if set(first_wp) != set(first_pv) or len(first_wp) < 50 or not set(original).issubset(first_wp):
            errors.append('INCOMPLETE_OR_NONPAIR_EXPORT_SET')
        else:
            reports = audit_callback()
        after = {'wp': _snapshot(Path(wp_dir)), 'preview': _snapshot(Path(preview_dir))}
        if before != after:
            errors.append('EXPORT_MUTATION_DURING_VALIDATION')
        wp = before['wp']['files']; preview = before['preview']['files']
        if set(wp) != set(preview) or len(wp) < 50 or not set(original).issubset(wp):
            errors.append('INCOMPLETE_OR_NONPAIR_EXPORT_SET')
        if not isinstance(reports, dict) or set(reports) != {'render', 'anchor', 'full'}:
            errors.append('MISSING_INDEPENDENT_AUDITS')
        else:
            full = reports['full']
            if not isinstance(full, dict) or full.get('status') != 'ALL_EXPORT_BYTES_REVIEW_HARD_HOLD' or full.get('errors'):
                errors.append('R390_AUDIT_FAILED')
            else:
                rows = full.get('exports')
                if not isinstance(rows, list) or len(rows) != len(wp):
                    errors.append('R390_EXPORT_ROWS_UNBOUND')
                else:
                    seen = set()
                    for row in rows:
                        slug = row.get('slug') if isinstance(row, dict) else None
                        if slug in seen or slug not in wp or slug not in preview:
                            errors.append('R390_EXPORT_ROWS_UNBOUND')
                            continue
                        seen.add(slug)
                        if (row.get('wp_sha256') != wp[slug]['sha256'] or
                                row.get('preview_sha256') != preview[slug]['sha256'] or
                                row.get('wp_bytes') != wp[slug]['size'] or
                                row.get('preview_bytes') != preview[slug]['size'] or
                                row.get('errors') or row.get('release_allowed') is not False or
                                row.get('qualified_review_required') is not True):
                            errors.append('R390_HASH_OR_REVIEW_DRIFT:' + slug)
                    if seen != set(wp):
                        errors.append('R390_EXPORT_ROWS_UNBOUND')
            for name, status in [('render', 'RENDER_PARITY_REVIEW_HARD_HOLD'),
                                 ('anchor', 'CLAIM_POSITION_REVIEW_HARD_HOLD')]:
                r = reports[name]
                if (not isinstance(r, dict) or r.get('status') != status or r.get('errors') or
                        r.get('publication_approved') is not False or
                        r.get('qualified_safety_approved') is not False):
                    errors.append('DEPENDENT_AUDIT_NOT_CLEAR:' + name)
    except Exception as exc:
        errors.append('SNAPSHOT_UNAVAILABLE:' + type(exc).__name__)
    inventory = {kind: {k: v['sha256'] for k, v in sorted(data.get('files', {}).items())}
                 for kind, data in sorted(before.items())}
    manifest_digest = sha256(json.dumps(inventory, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    return {'schema': 1, 'status': 'INVALID_HARD_HOLD' if errors else 'FROZEN_EXPORT_REVIEW_HARD_HOLD',
            'release_state': 'DRAFT_HARD_HOLD', 'publication_approved': False,
            'qualified_safety_approved': False, 'merchant_offer_verified': False,
            'live_release_allowed': False, 'errors': sorted(set(errors)),
            'matched_snapshot_pairs': len(before.get('wp', {}).get('files', {})),
            'snapshot_sha256': manifest_digest, 'reports': reports,
            'release_blockers': ['FIVE_SOURCE_GROUPS_UNADJUDICATED',
                                 'NINE_SHELTER_FORKS_UNSELECTED',
                                 'QUALIFIED_SAFETY_QD_AND_MERCHANT_APPROVAL_MISSING']}


def main(argv=None) -> int:
    print(json.dumps({'status': 'INVALID_HARD_HOLD', 'release_state': 'DRAFT_HARD_HOLD',
                      'publication_approved': False,
                      'errors': ['CALL_FROM_AUTHENTIC_NATIVE_R389_OBJECT_CUSTODY_REQUIRED']}, sort_keys=True))
    return 2


if __name__ == '__main__':
    raise SystemExit(main())