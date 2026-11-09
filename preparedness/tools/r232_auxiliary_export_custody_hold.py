#!/usr/bin/env python3
"""R232: strict auxiliary draft-output inventory and exact renderer replay.

Read-only. Protects the landing/hub drafts which R220/R231's 41-article
loop does not inspect. A PASS from this gate remains DRAFT_HARD_HOLD, *never*
source/medical/independent-QD/publication approval. Inputs must already be
subject to R220/R221/R222 custody; builder code MUST be authenticated.
"""
from __future__ import annotations

import re
from pathlib import Path

HOLD = 'DRAFT_HARD_HOLD'
LANDING_TITLE = 'The Preparedness Archive | Final Vestige'
LANDING_DESCRIPTION = ('Evidence-based household preparedness and a historical '
                       'record of how earlier generations managed without modern infrastructure.')
SAFE = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')


def _directory_inventory(root: Path, mode: str, names: set[str]) -> None:
    """Fail closed on stale/extra files, symlinks, subdirs and wrong channels."""
    node = root / 'build' / mode
    if (root / 'build').is_symlink() or node.is_symlink() or not node.is_dir():
        raise ValueError('R232 missing/symlinked output directory: ' + mode)
    found = set()
    for p in node.iterdir():
        if p.is_symlink() or not p.is_file() or p.name in found:
            raise ValueError('R232 unsafe generated export member: ' + p.name)
        found.add(p.name)
    if found != names:
        raise ValueError('R232 output inventory drift: ' + mode
                         + ' missing=' + repr(sorted(names - found))
                         + ' extra=' + repr(sorted(found - names)))


def _exact_page(root: Path, mode: str, name: str, expected: str, safe_read) -> None:
    if type(expected) is not str:
        raise ValueError('R232 renderer output is not text: ' + name)
    actual = safe_read(root, f'build/{mode}/{name}.html')
    if actual != expected.encode('utf-8', 'strict'):
        raise ValueError('R232 auxiliary export-byte drift: ' + mode + ':' + name)


def audit_auxiliary_exports(root: Path, report: dict, library, builder, safe_read) -> dict:
    """Verify ALL generated output filenames, landing, hubs, and report rows.

    Does not approve the source quality of manually written editorial hub text.
    Report fields are compared with *replayed* pinned producer outputs, not
    trusted as statements from the writable build report.
    """
    if type(report) is not dict or type(report.get('articles')) is not list:
        raise ValueError('R232 missing build report articles')
    if type(getattr(library, 'articles', None)) is not dict or len(library.articles) != 41:
        raise ValueError('R232 exact 35 article + 6 tool identities required')
    slugs = set(library.articles)
    if any(type(s) is not str or SAFE.fullmatch(s) is None for s in slugs):
        raise ValueError('R232 invalid article/tool slug')
    sections = library.taxonomy.get('sections')
    if type(sections) is not list or not sections:
        raise ValueError('R232 missing frozen section definitions')
    hub_rows = []
    hub_outputs = []
    section_ids = set()
    for sec in sections:
        if type(sec) is not dict:
            raise ValueError('R232 invalid section metadata')
        sid = sec.get('slug')
        if type(sid) is not str or SAFE.fullmatch(sid) is None or sid in section_ids:
            raise ValueError('R232 duplicate/unsafe section identity')
        section_ids.add(sid)
        hub = builder.build_hub(library, sid, include_drafts=True)
        if hub is None:
            continue
        if (type(hub) is not dict or hub.get('slug') != 'hub-' + sid
                or type(hub.get('inner')) is not str
                or type(hub.get('title')) is not str
                or type(hub.get('description')) is not str
                or type(hub.get('count')) is not int or hub['count'] < 1):
            raise ValueError('R232 malformed hub producer result: ' + sid)
        hub_rows.append({'section': sid, 'guides': hub['count']})
        hub_outputs.append(hub)
    if report.get('hubs') != hub_rows:
        raise ValueError('R232 hub-report parity failed')
    landing = builder.build_landing(library, include_drafts=True)
    if (type(landing) is not dict or landing.get('slug') != 'landing'
            or type(landing.get('inner')) is not str
            or type(landing.get('populated_sections')) is not list
            or type(landing.get('article_cards')) is not int):
        raise ValueError('R232 malformed landing producer result')
    if report.get('landing') != {k: landing[k] for k in ('populated_sections', 'article_cards')}:
        raise ValueError('R232 landing-report parity failed')
    names = {s + '.html' for s in slugs} | {h['slug'] + '.html' for h in hub_outputs} | {'landing.html'}
    if len(names) != len(slugs) + len(hub_outputs) + 1:
        raise ValueError('R232 duplicate landing/hub/article output filename')
    for mode in ('wp', 'preview'):
        _directory_inventory(root, mode, names)
        for hub in hub_outputs:
            if mode == 'wp':
                page = builder.wp_wrap(library, hub['inner'])
            else:
                page = builder.preview_wrap(library, hub['inner'], hub['title'], hub['description'])
            _exact_page(root, mode, hub['slug'], page, safe_read)
        if mode == 'wp':
            page = builder.wp_wrap(library, landing['inner'])
        else:
            page = builder.preview_wrap(library, landing['inner'], LANDING_TITLE, LANDING_DESCRIPTION)
        _exact_page(root, mode, 'landing', page, safe_read)
    return {'state': HOLD, 'release_authorized': False,
            'article_tool_names': len(slugs), 'hubs': len(hub_outputs),
            'auxiliary_files_verified': 2 * (len(hub_outputs) + 1),
            'total_expected_html_files': len(names) * 2,
            'commercial_approval': False, 'independent_qd_pass': False,
            'source_or_medical_safety_approved': False}
