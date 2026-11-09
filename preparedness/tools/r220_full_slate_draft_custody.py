#!/usr/bin/env python3
"""R220: immutable 35-article -> 41-draft WordPress custody; read-only, HOLD-only.

Checks two distinct source identities: R200 contributor originals and the R219
integration head. A changed integrated body is NOT an approval or an error if its
exact SHA is on the explicit review docket. Native build and independent human
review remain separate mandatory gates.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import types
from pathlib import Path

SCHEMA = 'fv-preparedness-r220-full-slate-draft-custody-v1'
HOLD = 'DRAFT_HARD_HOLD'
INVALID = 'INVALID_HARD_HOLD'
MANIFEST_PATH = 'audits/r200_seven_cluster_35_article_frozen_custody.json'
MANIFEST_BLOB = '5822f9dfde21d1f3bdfc26658769d852c639438c'
# R221 authenticated module: 35 frozen routes + 6 tools + 2026-11-08 taxonomy.
R221_AUTHORITY_PATH = 'tools/r221_frozen_route_tool_authority.py'
R221_AUTHORITY_BLOB = '88a8d37955957b4e1cba7a73e73ed4ee1e2fe0d1'
# R222 pins the renderer, source registers/fragments, CSS and nine inline scripts.
R222_BUNDLE_PATH = 'tools/r222_producer_source_bundle_gate.py'
R222_BUNDLE_BLOB = 'bd57ef0caba7ad68381fa6a22af64aff4d486c84'
# R226 all-41-export browser-semantics and visible citation/review HOLD gate.
R226_DOM_PATH = 'tools/r226_export_browser_custody.py'
R226_DOM_BLOB = 'f261e785c47af9556c3fe3864bbbccb46c3890bc'
# R227 catches markup inert to HTML reading or conditional on JS/open state.
R227_INERT_PATH = 'tools/r227_inert_context_citation_hold.py'
R227_INERT_BLOB = '8e7a4b8334f7166630d8f362da94b9d56afdbc85'
# R230 independently rejects unsupported HTML tokenizer-mode changes.
R230_TOKENIZER_PATH = 'tools/r230_html_tokenizer_state_hold.py'
R230_TOKENIZER_BLOB = '94e0eb8d790df732f5ae79d8aa2fc8c41d9b3f8e'
# R231 byte-for-byte replay against independently pinned WordPress producer.
R231_REPLAY_PATH = 'tools/r231_exact_export_replay_hold.py'
R231_REPLAY_BLOB = 'baf540008487ce0bad02e3b0336f1af7c045f1b4'
# R232 validates the generated landing + hub shells and exact output inventory.
R232_AUXILIARY_PATH = 'tools/r232_auxiliary_export_custody_hold.py'
R232_AUXILIARY_BLOB = 'd723f888dba57d8e280ac24003239e93e30cae65'
# R233 freezes the optional content/hubs source bytes and directory membership.
R233_HUB_INPUT_PATH = 'tools/r233_hub_input_custody_hold.py'
R233_HUB_INPUT_BLOB = '668c74c1672d86e4defad5e14a95ab1924ca6aa2'
# R234 independently checks draft card routes/badges and auxiliary outbound links.
R234_EXPOSURE_PATH = 'tools/r234_auxiliary_draft_exposure_hold.py'
R234_EXPOSURE_BLOB = '316e5463cd41a067b6503fe7de115e1a1110d345'
# R235 independently reconciles 244 source rows and all 32 crosswalk groups.
R235_DOCKET_PATH = 'tools/r235_crosswalk_receipt_hold.py'
R235_DOCKET_BLOB = 'cb5a45a6373d531a639fdce43ae29fc43aded171'
# These are independently observed R219 integration Git blobs, not certified text.
# Missing entries MUST match the older R200 original exactly.
INTEGRATED_DIFFS = {
     1: 'f81cd43516e8295104230412f18776919148f905',
     2: '933f38ff3cd55a241cf9b392014fc52d4961e84f',
    12: '2cd3e30b3a7e3dfdb3fd30cfd2b832355f58dfe2',
    13: '0412484304a3bcf08f0bb1b170110f617e3c2869',
    14: 'de3cb805041904cf22d4f216296bd4c8ddec17c1',
    15: '8ac8bd7dba3be15d477c15737e54d83364d72527',
    16: 'e5910015fc6e33ad015bc5dc0605b86622b701be',
    20: '68344cf6c4022285fffb2a01f42027bf6f9ee95d',
    24: '058c90b763d8cd6dec0731a7b0a9cee4dd5a57c7',
    25: '0b3319cc85ea2bc6d069b46d13a40e12ddbd5bc5',
    27: '2ff8d029769aa9a97de6b1e388d937899f3af38c',
    32: '3c02e58c30d1d608224944142f31fbead44a1252',
    33: 'd56df76647d2598f35cfd4609f91649cef063f12',
    34: 'ad158ee898f76d05bcb65c845b1e4a0e8103c660',
}
INTEGRATED_META_DIFFS = {
     2: '1c69d5f1636a3a41631a5d93f11254d85cbe1b59',
     6: '827d861eb3beebfd010ee98fcca764b23a2de90e',
     7: '91c730bd1c7a61fa3140a86245c9bc0c88160c29',
    12: 'be37b602d0b82593d438083dfc8a1e5ef595dd44',
    13: 'ff1246dcbfb0dd0bc864977f815badb9ad4e7ed8',
    14: 'cb559141d1e4a39debad16cf5cb796b746a01f19',
    15: 'dcad79faa8e0e6f1aef6db03e9e6e9451e19d8d3',
    20: 'ba840917f34634ccd634c488eeca4a8a6b3a8fe2',
    21: '1c4c5396da703f3724b584c67e49e2128ab1f4c6',
    24: '7191acba55d63dc405ad9c2003d66193276da89f',
    25: '03d3824e07fe51931671d0ddc7aa8c85eda58435',
    34: '4d2dc4958736e3c5257c65dda8ed016a473ac6be',
}
EXPECTED_EXCEPTIONS = {(7, 'cdc-find-clean-water'): 2,
                       (20, 'start-ready-plan'): 1}
CITE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
LINK = re.compile(r'\{\{link:([a-z0-9-]+)\|([^}]+)\}\}')
TOKEN = re.compile(r'\{\{[^}]*\}\}')
SAFE_SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def strict_object(data: bytes) -> dict:
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('duplicate JSON key: ' + key)
            result[key] = value
        return result
    def reject_constant(x):
        raise ValueError('nonfinite JSON literal: ' + x)
    result = json.loads(data.decode('utf-8', 'strict'), object_pairs_hook=unique,
                        parse_constant=reject_constant)
    if type(result) is not dict:
        raise ValueError('expected JSON object')
    return result


def safe_read(root: Path, relative: str) -> bytes:
    """Reject symlink ancestors, missing paths and escapes, including checkout root."""
    if not relative or relative.startswith('/') or '\\' in relative:
        raise ValueError('unsafe relative path: ' + relative)
    parts = Path(relative).parts
    if any(p in ('', '.', '..') for p in parts):
        raise ValueError('path traversal: ' + relative)
    current = root
    for segment in parts:
        if current.is_symlink():
            raise ValueError('symlink ancestor: ' + str(current))
        current = current / segment
    if current.is_symlink() or not current.is_file():
        raise ValueError('missing or symlinked input: ' + relative)
    return current.read_bytes()


def verify_roster(doc: dict) -> list[dict]:
    if (doc.get('schema') != 'fv-preparedness-r200-seven-cluster-35-article-frozen-custody-v1'
            or doc.get('state') != HOLD or doc.get('issue') != 136
            or doc.get('conversion_issue') != 820
            or doc.get('artifact_count') != 35
            or doc.get('export_target_count_with_six_tools') != 41):
        raise ValueError('R200 governance / count mismatch')
    for flag in ('publication_authorized', 'independent_qd_pass',
                 'human_source_approved', 'medical_safety_verified',
                 'merchant_offer_verified'):
        if doc.get(flag) is not False:
            raise ValueError('false release flag missing: ' + flag)
    heads = doc.get('branch_heads')
    if type(heads) is not dict or set(heads) != {
        'start', 'shelter', 'food', 'health', 'hist-field', 'hist-food', 'hist-home'
    } or any(not re.fullmatch('[0-9a-f]{40}', x) for x in heads.values()):
        raise ValueError('seven original contributor identities required')
    articles = doc.get('articles')
    if type(articles) is not list or len(articles) != 35:
        raise ValueError('exactly 35 frozen articles required')
    routes = set()
    for n, a in enumerate(articles, 1):
        if (type(a) is not dict or type(a.get('n')) is not int or a['n'] != n
                or a.get('source_cluster') not in heads
                or a.get('branch_sha') != heads[a['source_cluster']]):
            raise ValueError('frozen contributor mapping drift at #' + str(n))
        slug = a.get('slug'); section = a.get('section'); route = a.get('route')
        if (not isinstance(slug, str) or SAFE_SLUG.fullmatch(slug) is None
                or not isinstance(section, str) or SAFE_SLUG.fullmatch(section) is None
                or route != f'/preparedness/{section}/{slug}/'
                or route in routes):
            raise ValueError('duplicate/invalid canonical route at #' + str(n))
        routes.add(route)
        for key in ('body_oid', 'meta_oid'):
            if not re.fullmatch('[0-9a-f]{40}', str(a.get(key, ''))):
                raise ValueError('frozen object ID missing: ' + key)
    if not set(INTEGRATED_DIFFS) <= set(range(1, 36)):
        raise ValueError('integration docket has unknown article')
    return articles


def verify_originals(root: Path, articles: list[dict]) -> tuple[list[dict], dict]:
    status = []; exceptions = {}
    for a in articles:
        n = a['n']; slug = a['slug']
        raw = safe_read(root, f'content/articles/{slug}.body.html')
        actual = git_blob(raw)
        expected = INTEGRATED_DIFFS.get(n, a['body_oid'])
        if actual != expected:
            raise ValueError(f'#{n} changed without reviewed custody receipt: {actual}')
        meta_raw = safe_read(root, f'content/articles/{slug}.meta.json')
        expected_meta = INTEGRATED_META_DIFFS.get(n, a['meta_oid'])
        if git_blob(meta_raw) != expected_meta:
            raise ValueError(f'#{n} metadata changed without custody receipt')
        meta = strict_object(meta_raw)
        if (meta.get('n') != n or meta.get('slug') != slug
                or meta.get('section') != a['section']
                or meta.get('track') != a['track']
                or meta.get('status', {}).get('publish') != 'draft'
                or not isinstance(meta.get('source_use'), dict)):
            raise ValueError(f'#{n} metadata/slug/status contradiction')
        # A historically authored safety label is NOT an independent QD PASS.
        safety = meta.get('safety_review', {})
        if not isinstance(safety, dict) or safety.get('state') not in (
                'pending', 'approved', 'not-required'):
            raise ValueError(f'#{n} missing/invalid legacy safety label')
        body = raw.decode('utf-8', 'strict')
        tokens = [m.group(0) for m in TOKEN.finditer(body)]
        cited = [m.group(1) for m in CITE.finditer(body)]
        linked = [m.group(1) for m in LINK.finditer(body)]
        allowed = {m.group(0) for m in CITE.finditer(body)} | {
            m.group(0) for m in LINK.finditer(body)}
        allowed |= {m.group(0) for m in re.finditer(r'\{\{inline-js:[a-z_]+\.js\}\}', body)}
        if any(t not in allowed for t in tokens):
            raise ValueError(f'#{n} unknown template opcode')
        slugs = {x['slug'] for x in articles}
        if any(x not in slugs for x in linked):
            raise ValueError(f'#{n} internal link outside frozen roster')
        missing = {}
        for sid in cited:
            if sid not in meta['source_use']:
                missing[sid] = missing.get(sid, 0) + 1
        for sid, times in missing.items():
            exceptions[(n, sid)] = times
        status.append({'n': n, 'slug': slug, 'source_cluster': a['source_cluster'],
                       'original_blob': a['body_oid'], 'integrated_blob': actual,
                       'changed_since_original': actual != a['body_oid'],
                       'citations': len(cited), 'sources': len(set(cited)),
                       'links': len(linked), 'meta_blob': git_blob(meta_raw),
                       'route': a['route'], 'legacy_safety_label': safety['state']})
    if exceptions != EXPECTED_EXCEPTIONS:
        raise ValueError('source-use explanations changed; independently adjudicate: ' + str(exceptions))
    return status, {f'{n}:{sid}': count for (n, sid), count in exceptions.items()}


def verify_render(root: Path, articles: list[dict], report: dict, library, builder, dom_guard, inert_guard, tokenizer_guard, replay_guard) -> dict:
    actual = report.get('articles')
    if type(actual) is not list or len(actual) != 41:
        raise ValueError('expected 41 individual article/tool build-report entries')
    by_slug = {}
    for row in actual:
        if type(row) is not dict or not isinstance(row.get('slug'), str):
            raise ValueError('invalid build-report article entry')
        if row['slug'] in by_slug:
            raise ValueError('duplicate WordPress export slug: ' + row['slug'])
        by_slug[row['slug']] = row
    frozen_slugs = {a['slug'] for a in articles}
    if not frozen_slugs <= set(by_slug) or set(by_slug) != set(library.articles):
        raise ValueError('frozen articles or six tools missing / extra exports')
    if set(library.articles) - frozen_slugs != {
        p.name.removesuffix('.meta.json') for p in (root / 'content' / 'tools').glob('*.meta.json')
    } or len(set(library.articles) - frozen_slugs) != 6:
        raise ValueError('exact six existing tools required')
    seen_routes = set()
    for slug, meta in library.articles.items():
        route = library.url_path(slug)
        if route in seen_routes:
            raise ValueError('colliding route: ' + route)
        seen_routes.add(route)
        expected, order = builder.resolve_tokens(library, meta)
        row = by_slug[slug]
        if (row.get('canonical') != 'https://finalvestige.com' + route
                or row.get('sources') != order
                or row.get('words') != builder.word_count(expected)):
            raise ValueError('build-report source/canonical/reading-depth drift: ' + slug)
        wrapper = '<div class="pa-body" id="pa-main">' + expected + '</div>'
        for mode in ('wp', 'preview'):
            raw = safe_read(root, f'build/{mode}/{slug}.html')
            page = raw.decode('utf-8', 'strict')
            if page.count(wrapper) != 1:
                raise ValueError('body lost, truncated, duplicated or hidden in ' + mode + ':' + slug)
            if page.count('class="pa-body" id="pa-main"') != 1:
                raise ValueError('unexpected duplicate article body in ' + mode + ':' + slug)
            if meta['status']['publish'] != 'draft':
                raise ValueError('published article disallowed')
            if 'Independent safety/source and QD verification pending' not in page:
                raise ValueError('mandatory warning absent in ' + mode + ':' + slug)
            # HTML string parity alone cannot prove sources remain navigable/visible.
            # Enforce actual fragment identities, article-origin URLs, review visibility
            # and duplicate-id/attribute rejection in BOTH export formats.
            # Reject browser tokenizer-mode divergence BEFORE interpreting citations.
            tokenizer_result = tokenizer_guard.verify_tokenizer_states(page)
            if (tokenizer_result.get('state') != HOLD or
                    tokenizer_result.get('release_authorized') is not False):
                raise ValueError('unexpected tokenizer safety state: ' + slug)
            dom_result = dom_guard.verify_export(page, order, meta, library, expected)
            if dom_result.get('state') != HOLD:
                raise ValueError('unexpected browser-semantics safety state: ' + slug)
            # R226 does not identify inert <template>/<noscript>, closed <details>,
            # closed <dialog>, or browser parser recovery that can conceal a source.
            # Enforce an independent exact-byte read-only companion for all 82 files.
            inert_result = inert_guard.verify_inert_contexts(page, order)
            if inert_result.get('state') != HOLD or inert_result.get('release_authorized') is not False:
                raise ValueError('unexpected conditional-visibility safety state: ' + slug)
            # R231 catches exact-byte export mutations missed by parser-only gates:
            # extra CSS, scripts, link rewrites, warnings and build-report drift.
            # The pinned builder is replayed IN MEMORY; no file or CMS writes.
            replay_result = replay_guard.verify_exact_export(page, mode, slug, meta, library, builder, row)
            if (replay_result.get('state') != HOLD or
                    replay_result.get('release_authorized') is not False or
                    replay_result.get('exact_export_bytes') is not True):
                raise ValueError('unexpected exact-replay safety state: ' + slug)
    if report.get('release_evidence', {}).get('wordpress_publication_performed') is not False:
        raise ValueError('WordPress publication flag must remain false')
    if report.get('release_evidence', {}).get('independent_qa_verified') is not False:
        raise ValueError('independent QA flag must remain false')
    return {'exports_verified': len(by_slug), 'draft_channels': 2,
            'channel_files_verified': 2 * len(by_slug), 'canonical_routes': len(seen_routes)}


def load_frozen_gate(root: Path, relative: str, pin: str, module_name: str, required: tuple[str, ...]):
    """Execute authenticated gate bytes, never an independently re-opened path.

    Importlib loaders can read the file a *second* time after SHA inspection.
    This binds the functions used for later validation to the bytes actually
    checked and rejects any replacement during module execution.
    """
    if type(pin) is not str or re.fullmatch(r'[0-9a-f]{40}', pin) is None:
        raise ValueError('malformed pinned gate identity: ' + relative)
    raw = safe_read(root, relative)
    if git_blob(raw) != pin:
        raise ValueError('pinned gate changed before execution: ' + relative)
    filename = str(root / relative)
    module = types.ModuleType(module_name)
    module.__file__ = filename
    module.__package__ = None
    try:
        exec(compile(raw, filename, 'exec', dont_inherit=True), module.__dict__)
    except (SyntaxError, UnicodeError) as exc:
        raise ValueError('pinned gate cannot be compiled: ' + relative) from exc
    if git_blob(safe_read(root, relative)) != pin:
        raise ValueError('pinned gate changed during execution: ' + relative)
    for api in required:
        if not callable(getattr(module, api, None)):
            raise ValueError('pinned gate missing required API: ' + api)
    return module


def load_r221_authority(root: Path):
    return load_frozen_gate(root, R221_AUTHORITY_PATH, R221_AUTHORITY_BLOB,
                            'fv_preparedness_r221_frozen_authority',
                            ('verify_authorities', 'verify_routes'))


def load_r222_bundle(root: Path):
    return load_frozen_gate(root, R222_BUNDLE_PATH, R222_BUNDLE_BLOB,
                            'fv_preparedness_r222_source_bundle',
                            ('check_bundle',))


def load_frozen_builder(root: Path, bundle):
    """Bind the executable producer to the verified R222 Git blob, not sys.modules.

    The preflight bundle scan is necessary but not sufficient: ``import build``
    can reuse an unrelated module already cached in sys.modules. Compile the
    original bytes re-read after preflight into a private namespace instead.
    Re-check the file once the module is initialized to detect any replacement
    during loading. This grants no publishing, safety or source approval.
    """
    relative = 'tools/build.py'
    pin = bundle.PINNED.get(relative)
    if type(pin) is not str or re.fullmatch(r'[0-9a-f]{40}', pin) is None:
        raise ValueError('untrusted producer receipt')
    raw = safe_read(root, relative)
    if git_blob(raw) != pin:
        raise ValueError('producer changed between preflight and execution')
    filename = str(root / relative)
    producer = types.ModuleType('fv_preparedness_custody_bound_build')
    producer.__file__ = filename
    producer.__package__ = None
    try:
        exec(compile(raw, filename, 'exec', dont_inherit=True), producer.__dict__)
    except (SyntaxError, UnicodeError) as exc:
        raise ValueError('frozen producer cannot be compiled') from exc
    if git_blob(safe_read(root, relative)) != pin:
        raise ValueError('producer changed during module binding')
    for name in ('Library', 'resolve_tokens', 'word_count', 'build_article', 'wp_wrap', 'preview_wrap'):
        if not callable(getattr(producer, name, None)):
            raise ValueError('frozen producer lacks required API: ' + name)
    return producer


def audit(root: Path, *, verify_exports: bool = True) -> dict:
    result = {'schema': SCHEMA, 'state': INVALID, 'issue': 136, 'conversion_issue': 820,
              'publication_authorized': False, 'independent_qd_pass': False,
              'human_claim_verified': False, 'medical_safety_verified': False,
              'merchant_offer_verified': False, 'errors': [], 'articles': [],
              'reconciliation': None, 'source_exceptions': None}
    try:
        original = safe_read(root, MANIFEST_PATH)
        if git_blob(original) != MANIFEST_BLOB:
            raise ValueError('frozen manifest identity changed')
        roster = verify_roster(strict_object(original))
        authority = load_r221_authority(root)
        result['authorities'] = authority.verify_authorities(root, roster, safe_read)
        # Fail before importing or executing the mutable WordPress producer.
        bundle = load_r222_bundle(root)
        result['producer_sources'] = bundle.check_bundle(root, safe_read)
        # Docket is mechanical evidence ONLY: neither source equivalence nor
        # independent QD/medical safety approval can be inferred from it.
        docket_guard = load_frozen_gate(root, R235_DOCKET_PATH, R235_DOCKET_BLOB,
                                        'fv_preparedness_r235_source_docket_gate',
                                        ('audit_crosswalk',))
        docket = docket_guard.audit_crosswalk(root, safe_read)
        if (docket.get('state') != HOLD or docket.get('release_authorized') is not False
                or docket.get('independent_qd_pass') is not False
                or docket.get('source_or_medical_safety_approved') is not False
                or docket.get('merchant_approved') is not False
                or docket.get('raw_source_rows') != 244
                or docket.get('shared_url_groups') != 32
                or docket.get('pending_human_groups') != 32):
            raise ValueError('R235 crosswalk source-scope review is not approved')
        result['source_scope_docket'] = docket
        status, exceptions = verify_originals(root, roster)
        result['articles'] = status
        result['source_exceptions'] = exceptions
        if verify_exports:
            # Only imports the repository's own build code from its trusted tools path.
            tools_path = root / 'tools'
            if tools_path.is_symlink() or not tools_path.is_dir():
                raise ValueError('untrusted tools directory')
            build = load_frozen_builder(root, bundle)
            dom_guard = load_frozen_gate(root, R226_DOM_PATH, R226_DOM_BLOB,
                                         'fv_preparedness_r226_browser_gate',
                                         ('verify_export',))
            inert_guard = load_frozen_gate(root, R227_INERT_PATH, R227_INERT_BLOB,
                                           'fv_preparedness_r227_inert_gate',
                                           ('verify_inert_contexts',))
            tokenizer_guard = load_frozen_gate(root, R230_TOKENIZER_PATH, R230_TOKENIZER_BLOB,
                                               'fv_preparedness_r230_tokenizer_gate',
                                               ('verify_tokenizer_states',))
            replay_guard = load_frozen_gate(root, R231_REPLAY_PATH, R231_REPLAY_BLOB,
                                            'fv_preparedness_r231_exact_replay_gate',
                                            ('verify_exact_export',))
            auxiliary_guard = load_frozen_gate(root, R232_AUXILIARY_PATH, R232_AUXILIARY_BLOB,
                                                'fv_preparedness_r232_auxiliary_gate',
                                                ('audit_auxiliary_exports',))
            hub_input_guard = load_frozen_gate(root, R233_HUB_INPUT_PATH, R233_HUB_INPUT_BLOB,
                                               'fv_preparedness_r233_hub_input_guard',
                                               ('verify_hub_inputs',))
            exposure_guard = load_frozen_gate(root, R234_EXPOSURE_PATH, R234_EXPOSURE_BLOB,
                                               'fv_preparedness_r234_auxiliary_exposure_gate',
                                               ('verify_auxiliary_drafts',))
            library = build.Library(root=root)
            authority.verify_routes(roster, library)
            report = strict_object(safe_read(root, 'build/build-report.json'))
            result['render'] = verify_render(root, roster, report, library, build, dom_guard, inert_guard, tokenizer_guard, replay_guard)
            # R233 freezes ALL optional editorial hub inputs BEFORE R232 invokes
            # the authenticated builder, so matching regenerated exports cannot
            # launder an altered or newly added hub into a replay PASS.
            hubs_before = hub_input_guard.verify_hub_inputs(root)
            if (hubs_before.get('state') != HOLD or hubs_before.get('release_authorized') is not False
                    or hubs_before.get('independent_qd_pass') is not False
                    or hubs_before.get('source_or_medical_safety_approved') is not False):
                raise ValueError('unexpected frozen editorial hub input state')
            result['hub_input_custody'] = hubs_before
            # R231 protects 41 × 2 article/tool files. R232 independently
            # audits landing, editorial hubs, all output filenames and
            # their build-report rows, including both delivery formats.
            auxiliary = auxiliary_guard.audit_auxiliary_exports(root, report, library, build, safe_read)
            hubs_after = hub_input_guard.verify_hub_inputs(root)
            if hubs_after != hubs_before:
                raise ValueError('editorial hub source identity changed during replay')
            result['hub_input_custody_postrender'] = hubs_after
            if (auxiliary.get('state') != HOLD or auxiliary.get('release_authorized') is not False
                    or auxiliary.get('independent_qd_pass') is not False
                    or auxiliary.get('source_or_medical_safety_approved') is not False):
                raise ValueError('unexpected auxiliary export custody state')
            result['auxiliary_render'] = auxiliary
            # R232 byte replay protects output integrity, not independently
            # interpreted exposure: drafts must still be visibly marked DRAFT,
            # card links must be exactly the frozen 41 routes, and auxiliary
            # pages must not acquire unreviewed merchant/outbound anchors.
            exposure = exposure_guard.verify_auxiliary_drafts(root, library, tokenizer_guard, safe_read)
            if (exposure.get('state') != HOLD or exposure.get('release_authorized') is not False
                    or exposure.get('independent_qd_pass') is not False
                    or exposure.get('source_or_medical_safety_approved') is not False
                    or exposure.get('commercial_approval') is not False
                    or exposure.get('distinct_frozen_routes') != 41):
                raise ValueError('unexpected auxiliary exposure safety state')
            result['auxiliary_exposure'] = exposure
            # Repeat source custody after building the rendered-corpus view.
            # A file replaced after preflight cannot silently inherit its pin.
            bundle.check_bundle(root, safe_read)
            authority.verify_authorities(root, roster, safe_read)
            verify_originals(root, roster)
            if git_blob(safe_read(root, R230_TOKENIZER_PATH)) != R230_TOKENIZER_BLOB:
                raise ValueError('tokenizer guard mutated after render')
            if git_blob(safe_read(root, R231_REPLAY_PATH)) != R231_REPLAY_BLOB:
                raise ValueError('exact-replay guard mutated after render')
            if git_blob(safe_read(root, R232_AUXILIARY_PATH)) != R232_AUXILIARY_BLOB:
                raise ValueError('auxiliary-export guard mutated after render')
            if git_blob(safe_read(root, R233_HUB_INPUT_PATH)) != R233_HUB_INPUT_BLOB:
                raise ValueError('hub-input guard mutated after render')
            if git_blob(safe_read(root, R234_EXPOSURE_PATH)) != R234_EXPOSURE_BLOB:
                raise ValueError('auxiliary exposure guard mutated after render')
            result['postrender_custody_recheck'] = 'DRAFT_HARD_HOLD'
        if git_blob(safe_read(root, R235_DOCKET_PATH)) != R235_DOCKET_BLOB:
            raise ValueError('R235 source-scope docket guard mutated during audit')
        result['reconciliation'] = {'frozen_articles': 35,
                                    'integrated_changes_held_for_review': sum(
                                        x['changed_since_original'] for x in status),
                                    'unchanged_originals': sum(not x['changed_since_original'] for x in status),
                                    'word_level_review': 'REQUIRED',
                                    'source_url_adjudication': 'REQUIRED'}
        result['state'] = HOLD
    except (ValueError, KeyError, OSError, ImportError, TypeError, UnicodeError) as exc:
        result['errors'].append(str(exc))
    return result


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', required=True, type=Path, help='path to preparedness directory')
    ap.add_argument('--originals-only', action='store_true',
                    help='skip build outputs; still never grant any release PASS')
    args = ap.parse_args(argv)
    result = audit(args.root, verify_exports=not args.originals_only)
    print(json.dumps(result, sort_keys=True, indent=2))
    return 2 if result['state'] == HOLD else 3


if __name__ == '__main__':
    sys.exit(main())
