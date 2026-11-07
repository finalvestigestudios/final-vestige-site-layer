#!/usr/bin/env python3
"""R184: fail-closed custody of *unpublished* Preparedness build-report + WordPress drafts.

Structural tests only. Nothing here asserts safety approval, source truth or a right
 to publish. A clean inventory deliberately returns DRAFT_HARD_HOLD, exit 2.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re

EXPECTED = 35
BASE = 'https://finalvestige.com/preparedness/'
PENDING = 'drafted-pending-safety-review'
BANNED = ('safety-approved-draft', 'data-verify="reviewed"')


def load(path: Path) -> dict:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f'missing or symlinked file: {path}')
    return json.loads(path.read_text(encoding='utf-8'))


def check(root: Path) -> tuple[list[str], dict]:
    errors: list[str] = []
    summary: dict = {'state': 'INVALID_HARD_HOLD', 'articles_checked': 0,
                     'citation_occurrences_checked': 0, 'independent_qa_verified': False,
                     'wordpress_publication_performed': False}

    def require(ok: bool, msg: str) -> None:
        if not ok:
            errors.append(msg)

    prep = root / 'preparedness'
    folder = prep / 'content' / 'articles'
    try:
        taxonomy = load(prep / 'taxonomy.json')
        report = load(prep / 'build' / 'build-report.json')
        paths = sorted(folder.glob('*.meta.json'))
        require(len(paths) == EXPECTED, f'expected 35 original metadata files, got {len(paths)}')
        slate = taxonomy['slate']
        require(len(slate) == EXPECTED, 'slate is not 35 entries')
        roster = {row['slug']: row for row in slate}
        require(len(roster) == EXPECTED, 'duplicate slate slugs')
        require(taxonomy.get('base_path') == '/preparedness/', 'unexpected archive base path')
        rows = report['articles']
        reported = {row['slug']: row for row in rows}
        require(len(reported) == len(rows), 'duplicate report article slug')
        require(len(rows) >= EXPECTED, 'report omits original articles')
        ev = report['release_evidence']
        require(ev.get('state') == 'HOLD', 'report must remain HOLD')
        require(ev.get('independent_qa_verified') is False, 'report claims independent QD approval')
        require(ev.get('wordpress_publication_performed') is False, 'report claims WordPress publication')
        require(ev.get('article_published') == 0, 'report indicates published articles')
        require(ev.get('article_drafts') == len(rows), 'report draft count inconsistent')
        statuses = report['slate_status']
        require(statuses == {PENDING: EXPECTED}, 'report implies historical safety clearance or incorrect slate states')
        for forbidden in BANNED:
            require(forbidden not in json.dumps(report), f'forbidden approval wording in report: {forbidden}')
        for path in paths:
            meta = load(path)
            slug = meta['slug']
            require(slug == path.name.removesuffix('.meta.json'), f'{slug}: mismatched metadata filename')
            require(slug in roster, f'{slug}: absent from 35-item slate')
            require(meta.get('status', {}).get('publish') == 'draft', f'{slug}: original is not draft')
            require(meta.get('safety_review', {}).get('state') in {'pending', 'not-required', 'approved'},
                    f'{slug}: unknown historical label')
            require(slug in reported, f'{slug}: missing from build report')
            body = path.with_name(slug + '.body.html')
            if body.is_symlink() or not body.is_file():
                errors.append(f'{slug}: body missing or symlinked')
                continue
            original = body.read_text(encoding='utf-8')
            count = len(re.findall(r'\{\{cite:[a-z0-9-]+\}\}', original))
            summary['citation_occurrences_checked'] += count
            target = prep / 'build' / 'wp' / (slug + '.html')
            if target.is_symlink() or not target.is_file():
                errors.append(f'{slug}: WordPress export missing or symlinked')
                continue
            html = target.read_text(encoding='utf-8')
            row = reported.get(slug, {})
            section = meta.get('section', '')
            canonical = BASE + section + '/' + slug + '/'
            require(row.get('canonical') == canonical, f'{slug}: report canonical mismatch')
            require(row.get('words', 0) >= 1800, f'{slug}: original guide depth below cornerstone floor')
            require(html.startswith('<!-- wp:html -->') and html.rstrip().endswith('<!-- /wp:html -->'),
                    f'{slug}: invalid WordPress draft wrapper')
            require(html.count('data-slug="' + slug + '"') == 1, f'{slug}: rendered slug identity mismatch')
            require('Draft: not public' in html and 'Independent safety/source and QD verification pending' in html,
                    f'{slug}: publication/review disclaimer absent')
            require('class="pa-review"' in html and 'class="pa-sources"' in html,
                    f'{slug}: rendered review/source record absent')
            require(len(re.findall(r'class="pa-cite"', html)) == count,
                    f'{slug}: citation occurrence lost in WordPress render')
            require(not any(text in html for text in BANNED), f'{slug}: false review clearance markup')
            state = meta['safety_review']['state']
            if state == 'approved':
                require('Historical label recorded as approved' in html and 'not been independently verified' in html,
                        f'{slug}: historical approved label misrepresented')
            if state == 'not-required':
                require('Historically marked not required' in html and 'independent QD' in html,
                        f'{slug}: historical not-required label misrepresented')
            summary['articles_checked'] += 1
        landing = prep / 'build' / 'wp' / 'landing.html'
        if landing.is_symlink() or not landing.is_file():
            errors.append('draft landing export missing or symlinked')
        else:
            land = landing.read_text(encoding='utf-8')
            cards = re.findall(r'class="pa-card"[^>]+data-verify="([^"]+)"', land)
            require(len(cards) == report['landing']['article_cards'], 'landing card count mismatch')
            require(bool(cards) and set(cards) == {'pending'}, 'landing contains false reviewed card')
        require(summary['articles_checked'] == EXPECTED, 'not all article exports inspected')
        require(summary['citation_occurrences_checked'] == 2000,
                'original 35-article citation count drifted from 2,000 custody baseline')
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        errors.append(f'incomplete/untrusted native checkout: {exc}')
    summary['errors'] = errors
    summary['state'] = 'DRAFT_HARD_HOLD' if not errors else 'INVALID_HARD_HOLD'
    return errors, summary


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[2])
    args = ap.parse_args(argv)
    _errors, summary = check(args.repo)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 2  # ALWAYS nonzero, including structurally clean drafts: never QD PASS.


if __name__ == '__main__':
    raise SystemExit(main())
