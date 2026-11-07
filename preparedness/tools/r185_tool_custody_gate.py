#!/usr/bin/env python3
"""R185: six unpublished Preparedness tools; source decisions, privacy and draft exports.

A structural/source-custody preflight only. No source claim is medically/safety
approved by this script. No CMS, analytics, network, checkout or publishing writes.
The command always exits 2, even for perfectly preserved draft inputs.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

TOOL_COUNT = 6
ROW_COUNT = 67
UNRESOLVED_COUNT = 58
TOOL_CITATIONS = {
    'family-reunification-card': 16, 'home-fire-escape-worksheet': 11,
    'kit-builder': 106, 'power-outage-planner': 26,
    'reunification-plan': 7, 'water-planner': 7,
}
EXPECTED_CITATIONS = sum(TOOL_CITATIONS.values())  # 173 original tool occurrences
BASE = 'https://finalvestige.com/preparedness/'
TOKEN = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
# The family-card handles names/phones/children's details. Inspect the actual
# generated artifact, not solely the source templates. This denylist is one
# static backstop; it does not substitute for browser/network/privacy QA.
PRIVATE_SINKS = (
    r'\bfetch\s*\(', r'\bXMLHttpRequest\b', r'\bsendBeacon\s*\(',
    r'\bWebSocket\s*\(', r'\bEventSource\s*\(',
    r'\blocalStorage\b', r'\bsessionStorage\b', r'\bindexedDB\b',
    r'<\s*(?:iframe|script)\b[^>]+\bsrc\s*=',
    r'<\s*form\b[^>]*\b(?:action|method)\s*=',
)


def trusted(path: Path) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f'missing/symlinked file {path}')
    return path.read_bytes()


def load(path: Path) -> dict:
    return json.loads(trusted(path).decode('utf-8'))


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()


def check(repo: Path) -> tuple[list[str], dict]:
    errors: list[str] = []
    summary = {'state': 'INVALID_HARD_HOLD', 'tool_count': 0, 'source_rows': 0,
               'citation_occurrences': 0, 'independent_qd_verified': False,
               'merchant_offer_verified': False, 'wordpress_published': False}

    def require(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    try:
        prep = repo / 'preparedness'
        docket = load(prep / 'docs/r149/tool-source-use-review-docket.json')
        taxonomy = load(prep / 'taxonomy.json')
        report = load(prep / 'build/build-report.json')
        origins = docket['candidate_tool_origins']
        names = set(origins)
        require(len(names) == TOOL_COUNT, 'six-tool custody roster')
        require(docket.get('schema') == 'FV-PREP-R149-TOOL-CLAIM-CUSTODY-1', 'unknown docket schema')
        require(docket.get('status') == 'CANDIDATE_ONLY_HUMAN_SOURCE_REVIEW_REQUIRED', 'unreviewed docket misrepresented')
        require(docket.get('source_use_row_count') == ROW_COUNT, 'source row total altered')
        require(docket.get('currently_unresolved_source_ids') == UNRESOLVED_COUNT, 'unresolved source count altered')
        require(docket.get('human_link_checked_rows') == 0, 'human source link approval invented')
        require(docket.get('source_scope_human_review') == 'PENDING', 'source review represented as resolved')
        require(docket.get('independent_qd') == 'NOT_APPROVED', 'independent QD claimed')
        for field in ('publication_allowed', 'payment_offer_verified', 'customer_conversion_verified'):
            require(docket.get(field) is False, f'false clearance: {field}')
        listed = taxonomy.get('tools', [])
        taxonomy_slugs = [x['slug'] if isinstance(x, dict) else x for x in listed]
        require(set(taxonomy_slugs) == names and len(taxonomy_slugs) == TOOL_COUNT,
                'taxonomy six-tool roster mismatch')
        paths = sorted((prep / 'content/tools').glob('*.meta.json'))
        require({p.name.removesuffix('.meta.json') for p in paths} == names and len(paths) == TOOL_COUNT,
                'original tool pair inventory mismatch')
        rows = docket['source_use_rows']
        summaries = docket['tool_summaries']
        summary_index = {r['tool']: r for r in summaries}
        require(len(summary_index) == TOOL_COUNT and len(summaries) == TOOL_COUNT and set(summary_index) == names,
                'tool summary roster drift')
        require(len(rows) == ROW_COUNT, 'actual source-use row count differs')
        require(sum(not r.get('currently_resolvable', True) for r in rows) == UNRESOLVED_COUNT,
                'currently unresolved source-use rows drifted')
        key_counts = Counter((r['tool'], r['source_id']) for r in rows)
        require(len(key_counts) == ROW_COUNT and all(v == 1 for v in key_counts.values()),
                'duplicate/omitted authored tool-source relationship')
        report_index = {r['slug']: r for r in report['articles']}
        require(len(report_index) == len(report['articles']), 'duplicate report slug')
        require(report['release_evidence']['state'] == 'HOLD', 'native report release hold absent')
        require(report['release_evidence']['independent_qa_verified'] is False,
                'native report falsely marks independent QD')
        require(report['release_evidence']['wordpress_publication_performed'] is False,
                'native report falsely marks publication')
        require(report['release_evidence'].get('article_published') == 0,
                'native report includes published guide or tool')
        files_pinned = docket['immutable_git_blob_sha1']
        # Pin the original tool bodies and their metadata, plus the author-scope
        # source registries. Never accept silent edits as a review resolution.
        required_pins = {f'content/tools/{name}.{kind}' for name in names
                         for kind in ('body.html', 'meta.json')}
        required_pins |= {'sources/crosswalk.json', 'sources/fragments/shelter.json',
                          'sources/fragments/start.json', 'sources/register.json'}
        require(set(files_pinned) == required_pins, 'source custody pin coverage mismatch')
        for rel in sorted(required_pins):
            observed = git_blob(trusted(prep / rel))
            require(observed == files_pinned[rel], f'original Git blob identity drift: {rel}')
        for name in sorted(names):
            meta = load(prep / f'content/tools/{name}.meta.json')
            body = trusted(prep / f'content/tools/{name}.body.html').decode('utf-8')
            require(meta.get('slug') == name and meta.get('kind') == 'tool', f'{name}: wrong tool identity')
            require(meta.get('section') == 'field-tools' and meta.get('track') == 'modern',
                    f'{name}: section/track drift')
            require(meta.get('status', {}).get('publish') == 'draft', f'{name}: public source state')
            require(meta.get('safety_review', {}).get('state') == 'pending', f'{name}: safety approval asserted')
            source_counts = Counter(TOKEN.findall(body))
            author_sources = set(meta.get('source_use', {}))
            own_rows = {r['source_id']: r for r in rows if r['tool'] == name}
            require(set(own_rows) == author_sources == set(source_counts),
                    f'{name}: missing/extra author source relationship')
            require(all(source_counts[k] == r['citation_occurrences'] for k, r in own_rows.items()),
                    f'{name}: claim occurrence / source register mismatch')
            ss = summary_index[name]
            require(ss['tool'] == name and ss['current_origin'] == 'base'
                    and ss['candidate_origin'] == origins[name], f'{name}: origin/candidate scope drift')
            require(ss.get('unique_cited_sources') == len(own_rows)
                    and ss.get('citation_occurrences') == sum(source_counts.values()),
                    f'{name}: summary citation/relationship mismatch')
            require(sum(source_counts.values()) == TOOL_CITATIONS[name],
                    f'{name}: original citation occurrence baseline drift')
            require(set(ss.get('currently_unresolved_source_ids', [])) ==
                    {sid for sid, r in own_rows.items() if not r.get('currently_resolvable')},
                    f'{name}: unresolved source decision roster drift')
            require(ss.get('publication_allowed') is False, f'{name}: summary false publication clearance')
            for sid, row in own_rows.items():
                require(row.get('review_decision') == 'PENDING' and row.get('reviewer') is None,
                        f'{name}/{sid}: unsupported human reviewer decision')
                require(row.get('human_link_check_recorded') is False
                        and row.get('human_source_scope_adjudicated') is False
                        and row.get('medical_safety_approved') is False,
                        f'{name}/{sid}: source/medical clearance invented')
                require(row.get('current_origin') == 'base'
                        and row.get('candidate_origin') == origins[name],
                        f'{name}/{sid}: author scope reinterpreted')
                require(bool(row.get('literal_url')) and row['literal_url'].startswith('https://'),
                        f'{name}/{sid}: missing literal source URL')
                require(bool(row.get('author_specific_use')) and bool(row.get('source_supports')),
                        f'{name}/{sid}: source-use provenance missing')
            target = prep / f'build/wp/{name}.html'
            markup = trusted(target).decode('utf-8')
            rendered = report_index.get(name, {})
            require(rendered.get('canonical') == BASE + 'field-tools/' + name + '/',
                    f'{name}: canonical mismatch/merchant redirect')
            require(rendered.get('sources') == list(dict.fromkeys(TOKEN.findall(body))),
                    f'{name}: rendered report source order changed')
            require(markup.startswith('<!-- wp:html -->') and
                    markup.rstrip().endswith('<!-- /wp:html -->'), f'{name}: WordPress draft wrapper')
            require(markup.count('data-slug="' + name + '"') == 1, f'{name}: rendered tool slug')
            require(markup.count('class="pa-cite"') == sum(source_counts.values()),
                    f'{name}: exported citation count mismatch')
            require('class="pa-sources"' in markup and 'class="pa-review"' in markup,
                    f'{name}: source/review evidence missing in export')
            require('Draft: not public' in markup and
                    'Independent safety/source and QD verification pending' in markup,
                    f'{name}: draft/source/QD warning absent')
            require('data-verify="reviewed"' not in markup and 'safety-approved-draft' not in markup,
                    f'{name}: unsafe approval badge')
            if name == 'family-reunification-card':
                # Avoid matching ordinary external *source bibliography* links.
                for pattern in PRIVATE_SINKS:
                    require(re.search(pattern, markup, re.I) is None,
                            f'family-card privacy sink injected: {pattern}')
                require('id="rc-minimal"' in markup and 'id="rc-reset"' in markup,
                        'family-card privacy controls removed')
                require('A printed card can be lost' in markup,
                        'family-card found-card privacy warning removed')
                require('rcModel(fields(), minimal)' in markup,
                        'family-card minimal model bypassed')
            summary['tool_count'] += 1
            summary['citation_occurrences'] += sum(source_counts.values())
        summary['source_rows'] = len(rows)
        require(summary['tool_count'] == TOOL_COUNT, 'all tools not admitted')
        require(summary['citation_occurrences'] == EXPECTED_CITATIONS,
                '173-citation companion-tool corpus baseline altered')
    except (OSError, ValueError, TypeError, KeyError, AttributeError, UnicodeError) as e:
        errors.append(f'incomplete/untrusted Preparedness tool checkout: {e}')
    summary['errors'] = errors
    summary['state'] = 'DRAFT_HARD_HOLD' if not errors else 'INVALID_HARD_HOLD'
    return errors, summary


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args(argv)
    _errors, receipt = check(args.repo)
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
