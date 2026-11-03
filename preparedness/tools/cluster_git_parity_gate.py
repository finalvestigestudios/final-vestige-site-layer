#!/usr/bin/env python3
"""R15: verify seven author-cluster Git-blob custody against immutable Git objects.

The R14 parity JSON is an *assertion*. This tool tests its 72 path claims
against actual contributor and integrated commit trees, rejects ref drift, and
retains any content discrepancy as an unresolved human-review item. It grants
NO article publication, source verification or qualified safety approval.

Read only: Git object database + R14 JSON. No network, CMS or public writes.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

SCHEMA = 1
R13_SHA = 'f7b73e0235f95c3b6a86dd4660a21c9d8f184bf0'
R14_SHA = 'd5c14e58e309d2a831fe77fd7f7a1d94594ba332'
EXPECTED = {'start': 4, 'shelter': 4, 'food': 4, 'health': 3,
            'hist-food': 6, 'hist-home': 5, 'hist-field': 3}
BRANCHES = {
    'start': 'claude/prep-start-bbfeb8',
    'shelter': 'claude/prep-shelter-5e1e0e',
    'food': 'claude/prep-food-ccdc55',
    'health': 'claude/prep-health-837444',
    'hist-food': 'claude/prep-hist-food-b81f19',
    'hist-home': 'claude/prep-hist-home-0e0e38',
    'hist-field': 'claude/prep-hist-field-9db767',
}
# R14 recorded ONE article-specific source-use explanation not present at
# the original start-cluster commit. Preserve it; do not auto-approve it.
EXCEPTION_PATH = 'preparedness/content/articles/preparedness-real-households.meta.json'
EXCEPTION_BRANCH = 'start'
EXCEPTION_OLD = 'a0c3a09143a825560b5a5ed79d857b7402bfa295'
EXCEPTION_NEW = 'ba840917f34634ccd634c488eeca4a8a6b3a8fe2'
# Stage 4 of the custody repair (2026-11-03). A cluster may be re-pinned to a newly reviewed
# contributor head only by naming an integrated reference commit from this code-pinned
# allowlist (never a commit chosen by the manifest). The integrated blobs must also equal
# the blobs at the current head, exactly as for the original R13 reference.
REPIN_REFERENCES = {
    '6739a8376b430ebf9ce69200e57249ce0ab0217f':
        'integration repair stage 3b head (integration/preparedness-custody-repair-20261103)',
}
# A contributor blob that stores CRLF against preparedness/.gitattributes (text eol=lf) may
# differ from the integrated blob ONLY by line endings. The gate proves this from the blob
# contents; a manifest assertion alone is never enough.
EOL_ONLY_STATE = 'EOL_ONLY_LF_NORMALIZED'
SHA1 = re.compile(r'[0-9a-f]{40}\Z')
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
MAX_BYTES = 2_000_000


class ParityFailure(ValueError):
    """Historical provenance cannot be substantiated from exact Git objects."""


def require(value, message):
    if not value:
        raise ParityFailure(message)


def is_sha1(s):
    return isinstance(s, str) and SHA1.fullmatch(s) is not None


def _git(root: Path, *args: str) -> bytes:
    """Never use a shell or mutate the checkout. Runner must provide all refs."""
    try:
        p = subprocess.run(['git', '-C', str(root), *args],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           timeout=8, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ParityFailure(f'git unavailable or timed out: {exc}') from exc
    if p.returncode != 0:
        raise ParityFailure(f'git object/ref unavailable: {args[0]} ({p.returncode})')
    if len(p.stdout) > 4096:
        raise ParityFailure('unexpectedly oversized git response')
    return p.stdout


def git_blob(root: Path, commit: str, path: str) -> str:
    require(is_sha1(commit), 'untrusted commit SHA')
    require(_approved_path(path), 'untrusted repository path')
    result = _git(root, 'ls-tree', '-z', commit, '--', path)
    items = [x for x in result.split(b'\0') if x]
    require(len(items) == 1, f'missing or ambiguous Git blob: {path}')
    try:
        prefix, listed_path = items[0].split(b'\t', 1)
        mode, objtype, digest = prefix.decode('ascii').split(' ')
        require(listed_path.decode('utf-8') == path, 'Git returned a different path')
        require(mode == '100644' and objtype == 'blob' and is_sha1(digest),
                f'nonregular Git blob at {path}')
    except ParityFailure:
        raise
    except (ValueError, UnicodeError) as exc:
        raise ParityFailure('malformed Git tree object') from exc
    return digest


def git_content(root: Path, digest: str) -> bytes:
    """Bounded, read-only blob bytes by object id (no shell, no checkout change)."""
    require(is_sha1(digest), 'untrusted blob id')
    try:
        p = subprocess.run(['git', '-C', str(root), 'cat-file', 'blob', digest],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           timeout=15, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ParityFailure(f'git unavailable or timed out: {exc}') from exc
    require(p.returncode == 0, 'git blob unavailable')
    require(0 < len(p.stdout) <= MAX_BYTES, 'blob size outside the allowed range')
    return p.stdout


def git_ref(root: Path, branch: str, *, remote='origin') -> str:
    require(branch in BRANCHES.values(), 'unknown contributor branch')
    require(re.fullmatch(r'[a-zA-Z0-9_-]+', remote) is not None,
            'invalid Git remote name')
    raw = _git(root, 'rev-parse', '--verify', f'refs/remotes/{remote}/{branch}^{{commit}}')
    digest = raw.decode('ascii').strip()
    require(is_sha1(digest), 'invalid contributor ref SHA')
    return digest


def check_checkout(root: Path, claimed_sha: str) -> str:
    """Reject a stale CLI --current-integrated-sha or modified source tree."""
    require(is_sha1(claimed_sha), 'invalid claimed checkout SHA')
    head = _git(root, 'rev-parse', '--verify', 'HEAD^{commit}').decode('ascii').strip()
    require(head == claimed_sha, 'actual checkout HEAD does not match --current-integrated-sha')
    source_paths = ['preparedness/content/articles', 'preparedness/sources/fragments',
                    'preparedness/docs/R14-SEVEN-CLUSTER-GIT-BLOB-PARITY.json',
                    'preparedness/docs/R14R-SEVEN-CLUSTER-REPIN-20261103.json']
    source_paths.extend(f'preparedness/docs/CLUSTER-{name}.md' for name in EXPECTED)
    dirty = _git(root, 'status', '--porcelain', '--untracked-files=all', '--', *source_paths)
    require(not dirty.strip(), 'uncommitted or untracked contributor evidence content; audit cancelled')
    return head


def _approved_path(path):
    if not isinstance(path, str) or '\\' in path or '..' in path or '//' in path:
        return False
    if re.fullmatch(r'preparedness/content/articles/[a-z0-9-]+\.(?:body\.html|meta\.json)', path):
        return True
    if re.fullmatch(r'preparedness/docs/CLUSTER-[a-z-]+\.md', path):
        return True
    if re.fullmatch(r'preparedness/sources/fragments/[a-z-]+\.json', path):
        return True
    return False


def check_manifest(manifest: dict, blob_lookup, ref_lookup, *, integrated_head=R14_SHA,
                   content_lookup=None):
    """Return a HOLD receipt or raise; blob_lookup(commit,path), ref_lookup(branch).

    Every input is treated as untrusted until rederived from the actual Git
    object database. This does not cover six integration-authored articles,
    the unpublished water planner, or source-claim accuracy.
    """
    require(isinstance(manifest, dict), 'manifest must be an object')
    require(manifest.get('schema_version') == SCHEMA, 'unknown parity schema')
    require(manifest.get('issue') == 136, 'wrong tracking issue')
    require(manifest.get('authority') == 'GIT_BLOB_PARITY_ONLY_NOT_FACT_OR_SAFETY_APPROVAL',
            'manifest asserts wrong trust authority')
    require(manifest.get('release_state') == 'HOLD' and manifest.get('may_publish') is False,
            'publication state must be HOLD')
    require(manifest.get('human_source_review_complete') is False and
            manifest.get('independent_human_source_checks_verified') == 0 and
            manifest.get('qualified_emergency_safety_clearance') is False,
            'source or medical review cannot be inferred from SHA parity')
    require(manifest.get('reference_integrated_commit_sha') == R13_SHA,
            'integrated reference changed; manifest must be independently regenerated')
    require(is_sha1(integrated_head), 'invalid current integration SHA')
    require(isinstance(manifest.get('branches'), list) and
            len(manifest['branches']) == len(EXPECTED), 'all seven branches required')
    require(isinstance(manifest.get('exceptions'), list), 'missing discrepancy register')

    seen_branches, seen_paths, seen_articles = set(), set(), set()
    mismatches, actual_counts, checks, digests = [], Counter(), 0, []
    repinned: set[str] = set()
    for branch in manifest['branches']:
        require(isinstance(branch, dict), 'malformed contributor record')
        name = branch.get('name')
        require(name in EXPECTED and name not in seen_branches, 'missing/unknown/duplicate contributor')
        seen_branches.add(name)
        commit = branch.get('contributor_commit_sha')
        require(is_sha1(commit), f'{name}: invalid contributor SHA')
        require(ref_lookup(BRANCHES[name]) == commit,
                f'{name}: live contributor branch moved; re-review before integration')
        reference = branch.get('integrated_reference_sha', R13_SHA)
        require(reference == R13_SHA or reference in REPIN_REFERENCES,
                f'{name}: integrated reference commit is not an allowlisted re-pin point')
        if reference != R13_SHA:
            repinned.add(name)
        files = branch.get('files')
        require(isinstance(files, list) and len(files) == 2*EXPECTED[name]+2,
                f'{name}: file inventory changed')
        require(branch.get('scoped_paths') == len(files) and
                branch.get('article_count') == EXPECTED[name], f'{name}: incorrect recorded file totals')
        by_slug: dict[str, set[str]] = {}
        docs, fragments, n_identical = 0, 0, 0
        for item in files:
            require(isinstance(item, dict), 'malformed file record')
            path = item.get('path')
            require(_approved_path(path) and path not in seen_paths,
                    f'{name}: unexpected, unsafe or duplicate file path')
            seen_paths.add(path)
            if path.startswith('preparedness/content/articles/'):
                entry = path.rsplit('/', 1)[-1]
                slug, ending = entry.split('.', 1)
                require(SLUG.fullmatch(slug) is not None, 'invalid article slug')
                require(slug not in seen_articles, 'article assigned to multiple contributors') if slug not in by_slug else None
                by_slug.setdefault(slug, set()).add(ending)
            elif path.startswith('preparedness/docs/'):
                require(path == f'preparedness/docs/CLUSTER-{name}.md', 'foreign cluster documentation')
                docs += 1
            else:
                require(path == f'preparedness/sources/fragments/{name}.json', 'foreign source fragment')
                fragments += 1
            old, new = item.get('contributor_blob_sha'), item.get('integrated_blob_sha')
            require(is_sha1(old) and is_sha1(new), f'{path}: invalid Git object digest')
            require(blob_lookup(commit, path) == old, f'{path}: contributor Git blob mismatch')
            require(blob_lookup(reference, path) == new, f'{path}: R13 frozen Git blob mismatch')
            require(blob_lookup(integrated_head, path) == new,
                    f'{path}: current integration Git blob drift')
            require(item.get('identical') is (old == new), f'{path}: false equality flag')
            checks += 3
            n_identical += int(old == new)
            digests.append(f'{name}|{path}|{old}|{new}')
            if old != new:
                mismatches.append((name, path, old, new))
        require(docs == 1 and fragments == 1, f'{name}: missing source provenance inventory')
        require(len(by_slug) == EXPECTED[name], f'{name}: incomplete articles')
        for slug, kinds in by_slug.items():
            require(kinds == {'body.html', 'meta.json'}, f'{slug}: article body or metadata missing')
            seen_articles.add(slug)
        require(branch.get('exact_matches') == n_identical and
                branch.get('nonidentical_paths') == len(files)-n_identical,
                f'{name}: wrong equality summary')
        actual_counts[name] = len(by_slug)
    require(seen_branches == set(EXPECTED), 'seven cluster names must match exactly')
    require(len(seen_paths) == 72 and len(seen_articles) == 29,
            'lost cluster source file or article')
    exceptions = manifest['exceptions']
    eol_entries = [e for e in exceptions if isinstance(e, dict) and e.get('state') == EOL_ONLY_STATE]
    review_entries = [e for e in exceptions
                      if not (isinstance(e, dict) and e.get('state') == EOL_ONLY_STATE)]
    eol_tuples = []
    for e in eol_entries:
        require(e.get('branch') in repinned and e.get('identical') is False and
                is_sha1(e.get('contributor_blob_sha')) and is_sha1(e.get('integrated_blob_sha')) and
                _approved_path(e.get('path')),
                'EOL-only exception is only allowed on a re-pinned cluster with exact blob ids')
        require(content_lookup is not None,
                'EOL-only exception cannot be proven without blob contents')
        raw_old = content_lookup(e['contributor_blob_sha'])
        raw_new = content_lookup(e['integrated_blob_sha'])
        require(isinstance(raw_old, bytes) and isinstance(raw_new, bytes) and raw_old != raw_new and
                b'\r' not in raw_new and raw_old.replace(b'\r\n', b'\n') == raw_new,
                f"{e.get('path')}: difference is not line endings only")
        eol_tuples.append((e['branch'], e['path'], e['contributor_blob_sha'], e['integrated_blob_sha']))
    require(len(set(eol_tuples)) == len(eol_tuples), 'duplicate EOL-only exception')
    require(sorted(mismatches) ==
            sorted([(EXCEPTION_BRANCH, EXCEPTION_PATH, EXCEPTION_OLD, EXCEPTION_NEW)] + eol_tuples),
            'new or missing Git-blob discrepancy; do not auto-accept article edits')
    require(len(review_entries) == 1,
            'exception register must retain one unresolved discrepancy')
    exception = review_entries[0]
    require(isinstance(exception, dict) and exception.get('branch') == EXCEPTION_BRANCH and
            exception.get('path') == EXCEPTION_PATH and exception.get('state') == 'NEEDS_HUMAN_DIFF_REVIEW' and
            exception.get('contributor_blob_sha') == EXCEPTION_OLD and
            exception.get('integrated_blob_sha') == EXCEPTION_NEW and
            exception.get('identical') is False,
            'source explanation discrepancy must remain human-review pending')
    expected_totals = {'contributor_branches': 7, 'cluster_authored_articles': 29,
                       'scoped_blob_paths': 72, 'exact_matches': 72 - len(mismatches),
                       'nonidentical_paths': len(mismatches)}
    require(manifest.get('totals') == expected_totals, 'manifest totals are not canonical')
    return {'schema_version': 1, 'authority': 'GIT_OBJECT_PARITY_ONLY',
            'release_state': 'HOLD', 'may_publish': False,
            'contributor_branches': 7, 'cluster_articles': 29, 'inspected_paths': 72,
            'git_blob_checks': checks, 'identical_paths': 72 - len(mismatches),
            'unresolved_contributor_metadata_differences': 1,
            'exception_state': 'NEEDS_HUMAN_DIFF_REVIEW',
            'other_integration_articles_outside_scope': 6,
            'unpublished_water_planner_outside_scope': 1,
            'source_links_independently_verified': False,
            'qualified_safety_review_complete': False,
            'full_native_validator_and_QD_still_required': True,
            'frozen_reference_sha': R13_SHA, 'audited_integration_sha': integrated_head,
            'verified_rows_digest_sha256': hashlib.sha256('\n'.join(sorted(digests)).encode()).hexdigest(),
            **({'repinned_clusters_to_allowlisted_reference': sorted(repinned),
                'eol_only_paths_proven_from_blob_contents': len(eol_tuples)}
               if repinned or eol_tuples else {})}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--current-integrated-sha', required=True)
    parser.add_argument('--remote', default='origin')
    parser.add_argument('--receipt', type=Path,
                        help='Optional LOCAL report file; never CMS/public')
    args = parser.parse_args(argv)
    try:
        require(args.manifest.is_file() and not args.manifest.is_symlink(),
                'manifest must be an ordinary file')
        require(args.manifest.stat().st_size <= MAX_BYTES, 'manifest too large')
        check_checkout(args.repo_root, args.current_integrated_sha)
        manifest = json.loads(args.manifest.read_text(encoding='utf-8'))
        # Recheck frozen objects and the branch's current content, irrespective
        # of working-tree status; the native build and QD are separate gates.
        report = check_manifest(manifest,
                                lambda sha, path: git_blob(args.repo_root, sha, path),
                                lambda branch: git_ref(args.repo_root, branch, remote=args.remote),
                                integrated_head=args.current_integrated_sha,
                                content_lookup=lambda digest: git_content(args.repo_root, digest))
        if args.receipt:
            require(not args.receipt.is_symlink(), 'symlinked report destination forbidden')
            args.receipt.write_text(json.dumps(report, indent=2, sort_keys=True)+'\n', encoding='utf-8')
        print(json.dumps(report, sort_keys=True))
        return 0
    except (ParityFailure, OSError, ValueError, UnicodeError) as exc:
        print(json.dumps({'release_state': 'HOLD', 'may_publish': False,
                          'gate': 'CLOSED', 'error': str(exc)}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
