"""R221: independent taxonomy, tool-input and canonical-route custody; HOLD-only.

Preserves R220's 35 frozen contributor articles and prevents a mutable taxonomy
or six substituted tool inputs from making forged but internally consistent
WordPress drafts look valid. This is structural custody, NOT editorial/QD approval.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

TAXONOMY_OID = '15c547bb3018ac182b12a51036389cfa39a59168'
# Immutable observations of the six tool inputs at R220 head deb4ab4c.
# body Git blob SHA, metadata Git blob SHA; not independent safety approvals.
FROZEN_TOOLS = {
    'family-reunification-card': ('be8698ac5d020476ff649d85813810e2000c6f98', '47da1e7e20e39f0ea85e26d54a8d58301f6e0a15'),
    'home-fire-escape-worksheet': ('01161948b6de6ffbd1b053c9b83a420758e707e4', '397c7d3072fb237b490a5a316c93fc863c101be9'),
    'kit-builder': ('2cb531174d6828fa5185c47bd2b742a0befa8353', 'e9be8a497df737b36d7d399fccc4a00000ce8eac'),
    'power-outage-planner': ('aa8f866aaaaab9253f41c4363d31919029c69234', '8796bba2b323cce096639997002c402bd853e50f'),
    'reunification-plan': ('3305578369183edb1d427c8f8f8002eaacee420f', '10cd57dc8d39e366aaef8fd76cc3f8969b8c5348'),
    'water-planner': ('a738d1f7824437911064d425868ed3d709326027', '7ea188a06b614940a226328c0166c2a2b20ff84e'),
}


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def strict_dict(raw: bytes) -> dict:
    def unique(pairs):
        obj = {}
        for key, value in pairs:
            if key in obj:
                raise ValueError('duplicate JSON key: ' + key)
            obj[key] = value
        return obj
    obj = json.loads(raw.decode('utf-8', 'strict'), object_pairs_hook=unique,
                     parse_constant=lambda x: (_ for _ in ()).throw(ValueError('nonfinite JSON')))
    if type(obj) is not dict:
        raise ValueError('expected JSON object')
    return obj


def verify_authorities(root: Path, roster: list[dict], safe_read) -> dict:
    """Validate exact 2026-11-08 taxonomy and tool input bytes before build.

    Inject existing R220 safe_read, whose symlink and traversal guards apply to
    every pinned input. Never trust a generated build report as a source authority.
    """
    raw = safe_read(root, 'taxonomy.json')
    if git_blob(raw) != TAXONOMY_OID:
        raise ValueError('taxonomy authority modified: canonical routes cannot be trusted')
    taxonomy = strict_dict(raw)
    if taxonomy.get('base_path') != '/preparedness/':
        raise ValueError('unexpected canonical base path')
    slate = taxonomy.get('slate')
    if type(slate) is not list or len(slate) != 35:
        raise ValueError('missing taxonomy article authority')
    for row, frozen in zip(slate, roster):
        if any(row.get(k) != frozen[k] for k in ('n', 'slug', 'section', 'track')):
            raise ValueError('taxonomy/frozen roster conflict: ' + frozen['slug'])
    folder = root / 'content' / 'tools'
    if folder.is_symlink() or not folder.is_dir():
        raise ValueError('missing or symlinked tool directory')
    expected = {f'{name}.{ext}' for name in FROZEN_TOOLS
                for ext in ('body.html', 'meta.json')}
    actual = {p.name for p in folder.iterdir()
              if p.name.endswith(('.body.html', '.meta.json'))}
    if actual != expected:
        raise ValueError('tool inputs missing, substituted or duplicated')
    for slug, (body_oid, meta_oid) in FROZEN_TOOLS.items():
        body = safe_read(root, f'content/tools/{slug}.body.html')
        meta_raw = safe_read(root, f'content/tools/{slug}.meta.json')
        if git_blob(body) != body_oid or git_blob(meta_raw) != meta_oid:
            raise ValueError('tool body/metadata provenance mismatch: ' + slug)
        meta = strict_dict(meta_raw)
        if (meta.get('slug') != slug or meta.get('section') != 'field-tools'
                or meta.get('kind') != 'tool' or meta.get('track') != 'modern'
                or not isinstance(meta.get('status'), dict)
                or meta['status'].get('publish') != 'draft'):
            raise ValueError('tool route or unpublished status conflict: ' + slug)
    return {'taxonomy_oid': TAXONOMY_OID, 'tool_inputs_pinned': len(FROZEN_TOOLS) * 2,
            'tool_routes_pinned': len(FROZEN_TOOLS)}


def verify_routes(roster: list[dict], library) -> None:
    """Compare against immutable routes, NOT mutable Library.url_path alone."""
    frozen = {a['slug']: a['route'] for a in roster}
    frozen.update({slug: f'/preparedness/field-tools/{slug}/' for slug in FROZEN_TOOLS})
    if set(library.articles) != set(frozen):
        raise ValueError('41 exact source identities required for route verification')
    seen = set()
    for slug, route in frozen.items():
        candidate = library.url_path(slug)
        if candidate != route or candidate in seen:
            raise ValueError('canonical route authority mismatch: ' + slug)
        seen.add(candidate)
