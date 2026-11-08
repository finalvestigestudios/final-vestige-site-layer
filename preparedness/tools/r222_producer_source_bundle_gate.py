"""R222: immutable producer and source-input custody for Preparedness drafts.

Read-only. This is NOT an independent source-reading, safety, QD, or release
approval. It prevents a valid-looking 41-export report from being produced from
substituted code or bibliography after the original article bodies were frozen.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

# Git blob identifiers were read from the exact R221 head on 2026-11-08.
# They are archival observations, not endorsements of the material.
PINNED = {
    'tools/build.py': '349173d1e1d735eade218d95c7a0a2649c8cccd9',
    'assets/preparedness.css': 'e354395cdb7985eb2fe16b99ca9fd66c9885557e',
    'sources/register.json': 'b25cd02b9beaadaf5a2db0c52e0ae66d20b1ac77',
    'sources/crosswalk.json': 'd62e493a67dedd23e04cfdf3cce762ef933c6bf9',
    'sources/fragments/food.json': 'a1f73c8170932d6b3192e9cd506686d516d23d30',
    'sources/fragments/health.json': 'cc29c439372b9d49debf78e63020ffe4d62baeb8',
    'sources/fragments/hist-field.json': '3dafa9425f3829c0be2e6fea00889aff95124031',
    'sources/fragments/hist-food.json': 'd10628342fea5f177a8d1be00dd906d0c9c7850e',
    'sources/fragments/hist-home.json': '8d85fd868508c5caba14a839d119d55f31f14f72',
    'sources/fragments/shelter.json': '2a3f1a7ddeab2782add875be1e0e378513504aa1',
    'sources/fragments/start.json': '96140d6d1872588e5d20d9052445c9157e88934d',
    'tools/fire_worksheet.js': '7bfd283205c68ec1cbd9666cb63051c332ba23ac',
    'tools/kit_planner.js': '3bf8ea8e64a7b8e70815f1c6d8ee8df15bf7822f',
    'tools/kit_planner_ui.js': 'd2ff08d8ba5585fe69b557a73db55de42aac9d92',
    'tools/outage_items.js': '3bd519402202c40a49e9e1bde9fc9ba0f54d3fff',
    'tools/plan_builder.js': '311aa78ec1abca6f7c1113f2620a459dad92748d',
    'tools/plan_builder_ui.js': '2cc9a1196a6b433d861d91dafa6c5a85161990fb',
    'tools/reunion_card.js': 'b1a09b1eda1ae26f081de65b400a37bc19538035',
    'tools/shelter_common.js': 'efe1c7910d99437e3687621dabab8ce55dc24fd4',
    'tools/water_planner.js': '9cd2944e7b5c5061ae041669c327069d488c2062',
}


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()


def check_bundle(root: Path, safe_read) -> dict:
    """Check source/producer files *before* importing mutable build.py.

    ``safe_read`` is the R220 no-symlink/no-traversal reader. All mutations
    require a fresh frozen manifest and qualified independent review, not a
    rewritten hash in a generated build report. A successful check is HOLD.
    """
    # Reject malformed receipts before any synthetic mutation or filesystem read.
    # Passing synthetic fixtures alone is never proof that these hard-coded
    # receipts match the authentic archive; the real-checkout test proves that.
    if len(PINNED) != 20 or any(
            type(value) is not str or re.fullmatch(r'[0-9a-f]{40}', value) is None
            for value in PINNED.values()):
        raise ValueError('producer/source pin list must contain 20 valid 40-hex Git OIDs')
    required = {
        'sources/fragments': {Path(p).name for p in PINNED if p.startswith('sources/fragments/')},
        'tools': {Path(p).name for p in PINNED if p.startswith('tools/') and p.endswith('.js')},
    }
    for folder, expected in required.items():
        node = root / folder
        if node.is_symlink() or not node.is_dir():
            raise ValueError('missing or symlinked source bundle directory: ' + folder)
        suffix = '.json' if folder == 'sources/fragments' else '.js'
        discovered = {p.name for p in node.iterdir() if p.name.endswith(suffix)}
        if discovered != expected:
            raise ValueError('source bundle directory membership drift: ' + folder)
        for path in node.iterdir():
            if path.name.endswith(suffix) and (path.is_symlink() or not path.is_file()):
                raise ValueError('unsafe source bundle member: ' + path.name)
    for path, expected_oid in PINNED.items():
        raw = safe_read(root, path)
        if git_blob(raw) != expected_oid:
            raise ValueError('producer/source Git identity changed without adjudication: ' + path)
    return {
        'status': 'DRAFT_HARD_HOLD',
        'files_verified': len(PINNED),
        'source_register_and_crosswalk_pinned': True,
        'seven_source_fragments_pinned': True,
        'renderer_and_stylesheet_pinned': True,
        'inline_scripts_pinned': len(required['tools']),
        'source_reading_approved': False,
        'independent_qd_pass': False,
        'publication_authorized': False,
    }
