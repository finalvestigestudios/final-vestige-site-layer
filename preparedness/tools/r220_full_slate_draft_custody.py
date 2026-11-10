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
# R236 distinguishes PRESENT author source-use explanations from three HELD claims.
R236_PARITY_PATH = 'tools/r236_citation_source_parity_hold.py'
R236_PARITY_BLOB = '78936188bcb636d638346348d51c5f44daf8e5e2'
# R237 binds every citation occurrence to a deterministic review-only claim context.
R237_CLAIM_DOCKET_PATH = 'tools/r237_citation_claim_context_hold.py'
R237_CLAIM_DOCKET_BLOB = '30379a441948ed264871a4b2280a154b5a5167e0'
# R238 catches cite markers buried in quoted HTML attributes and nonreader markup.
R238_VISIBILITY_PATH = 'tools/r238_source_lexer_hold.py'
R238_VISIBILITY_BLOB = '694bbb23bcadb16169d783a0352b790f3629e4f6'
# R239 rejects deceptive HTML non-void '/>' while allowing real SVG shapes.
R239_SOLIDUS_PATH = 'tools/r239_foreign_solidus_custody_hold.py'
R239_SOLIDUS_BLOB = '04b5f6e1ea20cf1039e129a155713ddac1033f82'
# R245 repairs R242's false rejection of separated valueless attributes,
# retaining strict adjacency, C0, encoded visibility and value-parity holds.
R240_ENTITY_ATTR_PATH = 'tools/r240_html_attribute_entity_custody_hold.py'
R240_ENTITY_ATTR_BLOB = '156f475b88c1e374e4626119ec1e9965474ec329'
# R243 independently rejects authored executable HTML, event handlers,
# unreviewed interactive forms, URL-scheme tricks and covert third-party loads.
R243_ACTIVE_SOURCE_PATH = 'tools/r243_active_source_markup_custody_hold.py'
R243_ACTIVE_SOURCE_BLOB = 'fd44288b0009811f1812ede1d618f2290308ed7e'
# R246 pins the original Article 15 / Tool 104 privacy and minimal-mode claim
# witness docket. Observed mismatches remain HUMAN REVIEW REQUIRED, not PASS.
R246_FAMILY_CARD_PATH = 'tools/r246_family_card_claim_custody_hold.py'
R246_FAMILY_CARD_BLOB = '7c27ad9e9c6d5d0dd5917e57733285db48973812'
# R247 preserves observed JavaScript-off form/blank fallback contradiction.
# Parser checks source witnesses; DOM behavior and privacy remain unverified.
R247_NOJS_CARD_PATH = 'tools/r247_nojs_card_semantics_custody_hold.py'
R247_NOJS_CARD_BLOB = '60e073a5b3e6b0d4eaffc65b8010d3b2af7454b9'
# R248 reconciles actual print-field disclosure with the authored minimal-only
# and storage/no-JS copy, without changing the held source or declaring privacy.
R248_FIELD_CROSSWALK_PATH = 'tools/r248_family_card_field_crosswalk_hold.py'
R248_FIELD_CROSSWALK_BLOB = 'cd53368378bf89d365aba3d2175af78a0db08845'
# R249 separately authenticates an UNAPPROVED plain-language preview:
# no scripts, merchant links, forms, or misleading minimal-card claims.
R249_READER_COPY_PATH = 'tools/r249_reader_disclosure_preview_hold.py'
R249_READER_COPY_BLOB = '7952b897d26e2496b371d9f4fab517cef1c7011d'
R249_UNPUBLISHED_PREVIEW_PATH = 'audits/r249_family_card_reader_disclosure_draft.html'
R249_UNPUBLISHED_PREVIEW_BLOB = 'ce5c363786deb0296f78598818af1fd7abefae65'
# R250 checks R248's authenticated original print-field model against R249's
# unapproved, visible reader copy. Source parity is NOT human/medical/QD approval.
R250_SOURCE_READER_PATH = 'tools/r250_family_card_reader_source_alignment_hold.py'
R250_SOURCE_READER_BLOB = 'c8149e31b44b6b37ce930dfc8a140560270f1f73'
# R251 independently verifies that all R249 notices remain visible prose,
# not HTML popovers, foreign wrappers, hidden attributes or conditional UI.
# The underlying Article 15/Tool 104 is still unreviewed and unchanged.
R251_READER_CONTEXT_PATH = 'tools/r251_reader_visible_context_hold.py'
R251_READER_CONTEXT_BLOB = '677285daafbd53ab3bd2b5ea71e4a84a211bb30a'
# R252 binds the three original disputed claim occurrences to exact author
# bodies and a frozen human-review-only CDC/Ready.gov source-scope docket.
# Presence of a citation NEVER conveys claim or safety approval.
R252_DISPUTED_CLAIMS_PATH = 'tools/r252_three_disputed_claims_hold.py'
R252_DISPUTED_CLAIMS_BLOB = '3f2667e088729ec4353c08f8c1f5ef49f4ba6027'
R252_REVIEW_DOCKET_PATH = 'audits/r252_three_disputed_claims_hard_hold.json'
R252_REVIEW_DOCKET_BLOB = 'e3aca0a67d0cbbddb9a2bd84c591687d868d7392'
# R253 joins the frozen 32 shared-source review groups to the 2,000
# authentic R237 citation contexts across all 35 original articles.
# Risk-term priority is a human review queue, NEVER safety or QD approval.
R253_SOURCE_CONTEXT_PATH = 'tools/r253_full_slate_shared_source_priority_hold.py'
R253_SOURCE_CONTEXT_BLOB = '4456a15606a3787b348cc4d540a2ea40299a0ee5'
# R254 exposes the original author-owned claim context to human reviewers while
# enforcing the independently observed 562 shared-source occurrences/56 IDs.
# Its output remains review-only; every release, medical and QD HOLD persists.
R254_READABLE_WORKORDERS_PATH = 'tools/r254_readable_claim_workorders_hold.py'
R254_READABLE_WORKORDERS_BLOB = '5af564610f10fb3fe35512348cad2ed30844dfea'
# R255 authenticates the R254 source workorders and builds a self-contained,
# HTML-escaped OFFLINE HUMAN REVIEW surface in memory; no source URL clicks,
# CMS exports, source approval, merchant links or WordPress publication.
R255_REVIEW_SURFACE_PATH = 'tools/r255_offline_source_review_surface_hold.py'
R255_REVIEW_SURFACE_BLOB = '86e8b8e3cb29efbac738fd8574b487c4d633b1af'
# R257 additionally accounts for ALL 1,438 original citations not represented
# in the 562 shared-source workorders, retaining source contexts and all holds.
R257_PARTITION_PATH = 'tools/r257_complete_citation_partition_hold.py'
R257_PARTITION_BLOB = 'df74968de5ee609fa16287a7339cd8262616603c'
# R260 pins a source-only, reviewer-held witness: Tool #104's visible
# privacy alert is hidden by original @media print CSS; printed JS/no-JS
# paths lack an equivalent privacy warning in the checked source. It is
# not a computed-style/browser/privacy/QD approval.
R260_PRINT_DISCLOSURE_PATH = 'tools/r260_family_card_print_disclosure_witness_hold.py'
R260_PRINT_DISCLOSURE_BLOB = '3a5c51f2e49c0b92de0730d558af18b29b6c206b'
# R261 proposes only an in-memory, source-bound print privacy draft;
# original source, citations and review holds remain untouched.
R261_PRINT_DRAFT_PATH = 'tools/r261_family_card_print_remediation_draft_hold.py'
R261_PRINT_DRAFT_BLOB = '7132840d9f35bd60af5c7e4152053270f347da58'
# R262 supersedes R261's inaccurate feature description in an OFFLINE
# source-bound candidate. Original HTML and all release holds remain intact.
R262_NOJS_TRUTH_PATH = 'tools/r262_family_card_truthful_nojs_gate_hold.py'
R262_NOJS_TRUTH_BLOB = 'e8eae0980bbd30cc27a714a0b6b5a4d711c3224b'
# R263 witnesses the separate cut-out-card warning gap; it is intentionally
# a NEGATIVE privacy finding, not a printable-card repair or release approval.
R263_WALLET_PRIVACY_PATH = 'tools/r263_wallet_cutout_privacy_witness_hold.py'
R263_WALLET_PRIVACY_BLOB = 'd07b2e504c0c5cf0c4d1e900e81d79740bb587ea'
# R258 binds the complete R254/R257 original source-claim partition to a
# deterministic, entirely escaped, no-clickable-links offline reviewer view.
R258_COMPLETE_REVIEW_PATH = 'tools/r258_complete_offline_claim_review_hold.py'
R258_COMPLETE_REVIEW_BLOB = 'ade65322cf347c34bd9f731bbb490ff2bc9fc9f0'
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
# Authentic R235 HEAD: 35/35 integrated metadata files contain notes for every
# cited ID. The historical three occurrences are still UNREVIEWED (R236), but
# they are NOT *missing* source_use notes. Treating them as exceptions made the
# originals-only audit fail incorrectly before the native build could run.
EXPECTED_EXCEPTIONS = {}
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
        parity_guard = load_frozen_gate(root, R236_PARITY_PATH, R236_PARITY_BLOB,
                                        'fv_preparedness_r236_source_use_parity_gate',
                                        ('audit_parity',))
        parity = parity_guard.audit_parity(root, roster, safe_read)
        if (parity.get('state') != HOLD or parity.get('article_count') != 35
                or parity.get('unreviewed_original_occurrences') != 3
                or parity.get('unreviewed_original_groups') != 2
                or parity.get('source_use_missing_occurrences') != 0
                or parity.get('release_authorized') is not False
                or parity.get('independent_qd_pass') is not False
                or parity.get('source_review_approved') is not False
                or parity.get('medical_safety_verified') is not False):
            raise ValueError('R236 source-use parity or editorial review HOLD changed')
        result['citation_source_use_parity'] = parity
        # Every source citation receives its own anchored reading-context receipt.
        # These snippets are review leads, NOT claim-support or safety approval.
        claim_guard = load_frozen_gate(root, R237_CLAIM_DOCKET_PATH, R237_CLAIM_DOCKET_BLOB,
                                       'fv_preparedness_r237_claim_context_gate',
                                       ('audit_claim_contexts',))
        claims = claim_guard.audit_claim_contexts(root, roster, safe_read)
        if (claims.get('state') != HOLD or claims.get('article_count') != 35
                or claims.get('citation_count') != 2000
                or claims.get('original_hold_occurrences') != 3
                or claims.get('human_review_required') is not True
                or claims.get('release_authorized') is not False
                or claims.get('independent_qd_pass') is not False
                or claims.get('source_review_approved') is not False
                or claims.get('medical_safety_verified') is not False
                or claims.get('claim_evidence_adjudicated') is not False):
            raise ValueError('R237 per-occurrence claim/source review HOLD changed')
        result['claim_context_review_docket'] = claims
        r253 = load_frozen_gate(root, R253_SOURCE_CONTEXT_PATH,
                                R253_SOURCE_CONTEXT_BLOB,
                                'fv_preparedness_r253_source_claim_join',
                                ('audit_join',))
        joined = r253.audit_join(docket, claims, roster)
        totals = joined.get('totals') or {}
        if (joined.get('state') != HOLD
                or joined.get('article_count') != 35
                or joined.get('citation_count') != 2000
                or joined.get('contributor_cluster_count') != 7
                or totals.get('groups') != 32
                or totals.get('matched_occurrences', -1) + totals.get('unmatched_occurrences', -1) != 2000
                or totals.get('original_disputed_occurrences') != 3
                or any(joined.get(key) is not False for key in (
                    'human_source_scope_approved', 'independent_claim_reviewed',
                    'independent_qd_pass', 'medical_safety_verified',
                    'merchant_approved', 'publication_authorized'))):
            raise ValueError('R253 35-article source/claim join HARD HOLD drift')
        result['shared_source_context_review_queue'] = joined
        r254 = load_frozen_gate(root, R254_READABLE_WORKORDERS_PATH,
                                R254_READABLE_WORKORDERS_BLOB,
                                'fv_preparedness_r254_readable_review_workorders',
                                ('audit_readable_workorders',))
        workorders = r254.audit_readable_workorders(joined, claims)
        if (workorders.get('state') != HOLD
                or workorders.get('article_count') != 35
                or workorders.get('citation_count') != 2000
                or workorders.get('source_review_groups') != 32
                or workorders.get('shared_source_ids') != 56
                or workorders.get('human_readable_workorders') != 562
                or workorders.get('other_citation_occurrences_still_unreviewed') != 1438
                or workorders.get('disputed_original_claims') != 3
                or workorders.get('shared_disputed_claims') != 1
                or workorders.get('outside_shared_disputed_claims') != 2
                or len(workorders.get('outside_shared_disputed_workorders') or []) != 2
                or any(workorders.get(key) is not False for key in (
                    'independent_claim_source_verified', 'independent_qd_pass',
                    'medical_safety_verified', 'merchant_approved',
                    'publication_authorized'))):
            raise ValueError('R254 human-readable 562-citation review docket HARD HOLD drift')
        result['shared_source_readable_claim_workorders'] = workorders
        r255 = load_frozen_gate(root, R255_REVIEW_SURFACE_PATH,
                                R255_REVIEW_SURFACE_BLOB,
                                'fv_preparedness_r255_offline_review_surface',
                                ('audit_offline_review', 'render_offline_review'))
        offline_review = r255.audit_offline_review(workorders)
        if (offline_review.get('schema') != r255.SCHEMA
                or offline_review.get('state') != HOLD
                or offline_review.get('source_review_groups') != 32
                or offline_review.get('review_workorders') != 562
                or offline_review.get('unmatched_citations_unreviewed') != 1438
                or offline_review.get('original_disputes_visible') != 3
                or offline_review.get('shared_disputes_visible') != 1
                or offline_review.get('outside_shared_disputes_visible') != 2
                or type(offline_review.get('source_url_triage_labels')) is not dict
                or type(offline_review.get('potential_url_alias_pairs_to_review')) is not int
                or not re.fullmatch('[0-9a-f]{64}', offline_review.get('offline_review_sha256', ''))
                or offline_review.get('offline_review_utf8_bytes', 0) <= 10000
                or any(offline_review.get(k) is not False for k in (
                    'source_support_verified', 'independent_qd_pass',
                    'medical_safety_verified', 'merchant_approved',
                    'publication_authorized'))):
            raise ValueError('R255 offline source-review surface HARD HOLD drift')
        result['unpublished_offline_source_review_surface'] = offline_review
        r257 = load_frozen_gate(root, R257_PARTITION_PATH,
                                R257_PARTITION_BLOB,
                                'fv_preparedness_r257_full_citation_partition',
                                ('audit_full_partition',))
        partition = r257.audit_full_partition(claims, workorders)
        if (partition.get('schema') != r257.SCHEMA
                or partition.get('state') != HOLD
                or partition.get('article_count') != 35
                or partition.get('citation_count') != 2000
                or partition.get('shared_workorders') != 562
                or partition.get('nonshared_workorders') != 1438
                or partition.get('total_unapproved_citation_occurrences') != 2000
                or partition.get('shared_disputes') != 1
                or partition.get('nonshared_disputes') != 2
                or len(partition.get('unreviewed_nonshared_queue') or []) != 1438
                or any(partition.get(k) is not False for k in (
                    'independent_claim_source_verified', 'independent_qd_pass',
                    'medical_safety_verified', 'merchant_approved',
                    'publication_authorized'))):
            raise ValueError('R257 full 2000-citation partition HARD HOLD drift')
        result['complete_unreviewed_citation_partition'] = partition
        # R255's HTML only renders 562 shared + two CDC exception contexts.
        # R258 requires ALL 2,000 original citation excerpts in ONE offline,
        # unapproved human-readable review. Never write to CMS or emit HTML
        # into the audit JSON (the reviewer can render from authenticated inputs).
        r258 = load_frozen_gate(root, R258_COMPLETE_REVIEW_PATH,
                                R258_COMPLETE_REVIEW_BLOB,
                                'fv_preparedness_r258_full_offline_review',
                                ('prepare', 'render_full_review'))
        full_review = r258.render_full_review(workorders, partition)
        if (full_review.get('schema') != r258.SCHEMA
                or full_review.get('state') != HOLD
                or full_review.get('article_count') != 35
                or full_review.get('citation_occurrences') != 2000
                or full_review.get('shared') != 562
                or full_review.get('other') != 1438
                or full_review.get('held_disputes') != 3
                or full_review.get('source_groups') != 32
                or full_review.get('shared_source_ids') != 56
                or full_review.get('review_approval') is not False
                or any(full_review.get(k) is not False for k in (
                    'independent_claim_source_verified', 'independent_qd_pass',
                    'medical_safety_verified', 'merchant_approved',
                    'publication_authorized'))
                or not re.fullmatch('[0-9a-f]{64}', full_review.get('offline_review_sha256', ''))
                or full_review.get('offline_review_utf8_bytes', 0) < 150000):
            raise ValueError('R258 2000-citation offline source-review HOLD drift')
        full_review.pop('offline_review_html')  # audit JSON: only the checksum and counts
        result['full_2000_citation_offline_human_review'] = full_review
        # R237's simple tag/attribute regex can mistake '>' inside a quoted
        # attribute or HTML comment for the end of markup. Verify source-level
        # visibility separately with an independently pinned quote-aware lexer.
        visible_guard = load_frozen_gate(root, R238_VISIBILITY_PATH, R238_VISIBILITY_BLOB,
                                         'fv_preparedness_r238_visible_source_gate',
                                         ('audit_source_visibility',))
        visibility = visible_guard.audit_source_visibility(root, roster, safe_read)
        if (visibility.get('state') != HOLD or visibility.get('article_count') != 35
                or visibility.get('citation_count') != 2000
                or visibility.get('human_review_required') is not True
                or visibility.get('release_authorized') is not False
                or visibility.get('independent_qd_pass') is not False
                or visibility.get('source_approved') is not False
                or visibility.get('medical_safety_verified') is not False):
            raise ValueError('R238 source citation visibility/source safety HOLD drift')
        result['source_citation_visibility_custody'] = visibility
        # R238 must not mistake <div hidden/> for a closed div; browsers
        # keep non-void HTML elements open despite the trailing solidus.
        # Preserve genuine diagram SVG <rect/>/<path/> foreign syntax.
        solidus_guard = load_frozen_gate(root, R239_SOLIDUS_PATH, R239_SOLIDUS_BLOB,
                                         'fv_preparedness_r239_nonvoid_html_guard',
                                         ('audit_solidus_custody',))
        solidus = solidus_guard.audit_solidus_custody(root, roster, safe_read)
        if (solidus.get('state') != HOLD or solidus.get('article_count') != 35
                or solidus.get('citation_count') != 2000
                or solidus.get('human_review_required') is not True
                or solidus.get('release_authorized') is not False
                or solidus.get('independent_qd_pass') is not False
                or solidus.get('source_review_approved') is not False
                or solidus.get('medical_safety_verified') is not False):
            raise ValueError('R239 browser nonvoid solidus/source safety HOLD drift')
        result['browser_solidus_original_custody'] = solidus
        # Browsers decode character references inside HTML attribute values.
        # R242 additionally rejects missing separators and parser-value drift.
        # R238's raw hidden-state regex alone misses aria-hidden="tr&#117;e"
        # and style="display:&#110;one"; never treat the citation as visible.
        entity_guard = load_frozen_gate(root, R240_ENTITY_ATTR_PATH, R240_ENTITY_ATTR_BLOB,
                                        'fv_preparedness_r240_attribute_entity_guard',
                                        ('audit_attribute_entity_custody',))
        entities = entity_guard.audit_attribute_entity_custody(root, roster, safe_read)
        if (entities.get('state') != HOLD or entities.get('article_count') != 35
                or entities.get('citation_count') != 2000
                or entities.get('human_review_required') is not True
                or entities.get('release_authorized') is not False
                or entities.get('independent_qd_pass') is not False
                or entities.get('source_review_approved') is not False
                or entities.get('medical_safety_verified') is not False):
            raise ValueError('R240 encoded HTML attribute/source citation HOLD drift')
        result['decoded_html_attribute_custody'] = entities
        # Raw authored markup can bypass the frozen citation-link resolver or
        # introduce active remote loads even when citation tokens are visible.
        # Inspect every original body BEFORE executing the WordPress producer.
        active_guard = load_frozen_gate(root, R243_ACTIVE_SOURCE_PATH, R243_ACTIVE_SOURCE_BLOB,
                                        'fv_preparedness_r243_authored_active_source_guard',
                                        ('audit_active_markup_custody',))
        active = active_guard.audit_active_markup_custody(root, roster, safe_read)
        if (active.get('state') != HOLD or active.get('article_count') != 35
                or active.get('citation_count') != 2000
                or active.get('human_review_required') is not True
                or active.get('release_authorized') is not False
                or active.get('source_review_approved') is not False
                or active.get('independent_qd_pass') is not False
                or active.get('medical_safety_verified') is not False
                or active.get('merchant_approved') is not False):
            raise ValueError('R243 authored active-markup/source URL safety HOLD drift')
        result['authored_active_markup_custody'] = active
        # Editorial E244/E245 established exact source-to-output discrepancies:
        # the optional minimal printable still includes Household and Phone, and
        # several cross-linked original pages make absolute privacy promises.
        # This is an immutable review docket, NOT adjudication or live privacy QA.
        family_claim_guard = load_frozen_gate(root, R246_FAMILY_CARD_PATH, R246_FAMILY_CARD_BLOB,
                                              'fv_preparedness_r246_family_card_claim_guard',
                                              ('audit_family_card_claims',))
        family_claims = family_claim_guard.audit_family_card_claims(root, safe_read)
        if (family_claims.get('state') != HOLD or family_claims.get('source_count') != 5
                or family_claims.get('held_claim_count') != 7
                or family_claims.get('human_review_required') is not True
                or family_claims.get('claim_truth_evaluated') is not False
                or family_claims.get('runtime_privacy_certified') is not False
                or family_claims.get('release_authorized') is not False
                or family_claims.get('independent_qd_pass') is not False
                or family_claims.get('source_review_approved') is not False
                or family_claims.get('medical_safety_verified') is not False
                or family_claims.get('merchant_approved') is not False):
            raise ValueError('R246 Article 15 / Tool 104 source-to-claim review HOLD changed')
        result['family_card_claim_review_docket'] = family_claims
        # Independent Article 15 / Tool 104 JS-off source-to-interface claim check.
        # Its fixed no-JS/print witnesses are unresolved editorial work, not QA PASS.
        nojs_guard = load_frozen_gate(root, R247_NOJS_CARD_PATH, R247_NOJS_CARD_BLOB,
                                      'fv_preparedness_r247_nojs_card_guard', ('audit',))
        nojs = nojs_guard.audit(root, safe_read)
        if (nojs.get('state') != HOLD or nojs.get('source_count') != 4
                or nojs.get('nojs_block_count') != 3 or nojs.get('blank_fallback_field_count') != 13
                or nojs.get('held_witness_count') != 5
                or nojs.get('nojs_copy_conflicts_with_hidden_form') is not True
                or nojs.get('minimal_identifier_disclosure_requires_review') is not True
                or nojs.get('human_review_required') is not True
                or any(nojs.get(k) is not False for k in (
                    'nojs_browser_print_verified', 'privacy_certified', 'claims_adjudicated',
                    'source_review_approved', 'independent_qd_pass', 'release_authorized',
                    'merchant_approved'))):
            raise ValueError('R247 no-JS family card source-to-claim HOLD drift')
        result['nojs_family_card_claim_review_docket'] = nojs
        # Field-by-field, reader-facing print disclosure is an independent
        # unresolved claim scope; a hash match never means readers consented.
        matrix_guard = load_frozen_gate(root, R248_FIELD_CROSSWALK_PATH,
                                        R248_FIELD_CROSSWALK_BLOB,
                                        'fv_preparedness_r248_field_crosswalk', ('audit',))
        field_matrix = matrix_guard.audit(root, safe_read)
        if (field_matrix.get('state') != HOLD or field_matrix.get('source_count') != 5
                or field_matrix.get('full_field_count') != 13
                or field_matrix.get('minimal_field_count') != 6
                or field_matrix.get('minimal_excluded_field_count') != 7
                or len(field_matrix.get('field_matrix', [])) != 13
                or field_matrix.get('claimed_only_list_is_incomplete') is not True
                or field_matrix.get('nojs_form_claim_is_contradicted') is not True
                or field_matrix.get('privacy_claim_scope_requires_browser_review') is not True
                or field_matrix.get('human_review_required') is not True
                or any(field_matrix.get(key) is not False for key in (
                    'reader_disclosure_approved', 'privacy_certified',
                    'claims_adjudicated', 'medical_safety_verified',
                    'source_review_approved', 'independent_qd_pass',
                    'merchant_approved', 'release_authorized'))):
            raise ValueError('R248 family-card field-disclosure HOLD drift')
        result['family_card_field_disclosure_review_matrix'] = field_matrix
        # R260 preserves a critical unresolved print/privacy finding. The
        # source witness remains held and no approval may be inferred from it.
        print_guard = load_frozen_gate(root, R260_PRINT_DISCLOSURE_PATH,
                                       R260_PRINT_DISCLOSURE_BLOB,
                                       'fv_preparedness_r260_print_privacy_witness', ('audit',))
        print_witness = print_guard.audit(root, safe_read)
        if (print_witness.get('state') != HOLD
                or print_witness.get('source_git_blob') != 'be8698ac5d020476ff649d85813810e2000c6f98'
                or print_witness.get('print_css_hides_original_privacy_alert') is not True
                or print_witness.get('javascript_print_note_lacks_privacy_warning') is not True
                or print_witness.get('nojs_print_fallback_field_count') != 13
                or print_witness.get('nojs_print_fallback_lacks_privacy_warning') is not True
                or print_witness.get('human_editorial_and_privacy_review_required') is not True
                or any(print_witness.get(key) is not False for key in (
                    'browser_print_verified', 'privacy_certified', 'medical_safety_verified',
                    'source_review_approved', 'independent_qd_pass', 'merchant_approved',
                    'release_authorized'))):
            raise ValueError('R260 printed family-card privacy witness HARD HOLD changed')
        result['family_card_print_privacy_review_witness'] = print_witness
        # An offline candidate is not a corrected original or a privacy PASS.
        r261 = load_frozen_gate(root, R261_PRINT_DRAFT_PATH,
                                R261_PRINT_DRAFT_BLOB,
                                'fv_preparedness_r261_print_privacy_draft', ('audit',))
        candidate_receipt = r261.audit(root, safe_read)
        if (candidate_receipt.get('state') != HOLD
                or candidate_receipt.get('original_git_blob') != print_witness['source_git_blob']
                or candidate_receipt.get('changed_anchor_count') != 3
                or candidate_receipt.get('draft_notice_occurrences') != 2
                or candidate_receipt.get('javascript_print_note_contains_notice') is not True
                or candidate_receipt.get('nojs_print_sheet_contains_notice') is not True
                or candidate_receipt.get('nojs_functionality_claim_corrected_in_draft') is not True
                or candidate_receipt.get('original_source_unchanged') is not True
                or candidate_receipt.get('real_browser_and_print_tests_required') is not True
                or any(candidate_receipt.get(key) is not False for key in (
                    'privacy_certified', 'medical_safety_verified', 'independent_qd_pass',
                    'source_review_approved', 'merchant_approved',
                    'release_authorized', 'public_published'))):
            raise ValueError('R261 offline print privacy candidate HOLD drift')
        result['family_card_unpublished_print_remediation_receipt'] = candidate_receipt
        # R261's draft still describes automatic reminders/text download which
        # the actual original Tool #104 does not implement. Preserve R261 as an
        # historical witness but use ONLY the held R262 truthfully worded option.
        r262 = load_frozen_gate(root, R262_NOJS_TRUTH_PATH, R262_NOJS_TRUTH_BLOB,
                                'fv_preparedness_r262_nojs_feature_truth', ('audit', 'propose'))
        truth = r262.audit(root, safe_read, r261)
        if (truth.get('state') != HOLD
                or truth.get('original_git_blob') != print_witness['source_git_blob']
                or truth.get('r261_candidate_blob') != candidate_receipt['draft_git_blob']
                or truth.get('unsupported_feature_promises_removed') != 2
                or truth.get('review_only_claim_replacements') != 1
                or truth.get('required_static_affordances') != 9
                or truth.get('static_affordance_checks_pass') is not True
                or truth.get('two_print_privacy_notices_retained') is not True
                or truth.get('citations_and_links_unchanged') is not True
                or truth.get('original_source_unchanged') is not True
                or truth.get('independent_editorial_review_required') is not True
                or truth.get('real_browser_and_print_tests_required') is not True
                or any(truth.get(key) is not False for key in (
                    'privacy_certified', 'medical_safety_verified', 'independent_qd_pass',
                    'source_review_approved', 'merchant_approved',
                    'release_authorized', 'public_published'))):
            raise ValueError('R262 truthful no-JS draft candidate HARD HOLD changed')
        result['family_card_unpublished_truthful_nojs_candidate'] = truth
        # Even the R262 held candidate places privacy cautions above, NOT inside,
        # either wallet-size cut-out. Preserve this as explicit non-PASS evidence.
        r263 = load_frozen_gate(root, R263_WALLET_PRIVACY_PATH,
                                R263_WALLET_PRIVACY_BLOB,
                                'fv_preparedness_r263_wallet_cutout_privacy_witness',
                                ('audit', 'inspect'))
        cutout = r263.audit(root, safe_read, r261, r262)
        if (cutout.get('state') != HOLD
                or cutout.get('original_git_blob') != truth['original_git_blob']
                or cutout.get('r262_candidate_blob') != truth['r262_candidate_blob']
                or cutout.get('nojs_source_field_count') != 13
                or cutout.get('nojs_cutout_faces') != 2
                or cutout.get('print_css_face_overflow_hidden') is not True
                or cutout.get('javascript_warning_on_print_page_only') is not True
                or cutout.get('nojs_warning_on_print_page_only') is not True
                or cutout.get('wallet_cutout_has_privacy_warning') is not False
                or cutout.get('printed_card_privacy_resolved') is not False
                or cutout.get('actual_browser_and_physical_cutout_qa_completed') is not False
                or cutout.get('qualified_child_privacy_review_completed') is not False
                or cutout.get('requires_editorial_resolution_before_publication') is not True
                or cutout.get('original_source_unchanged') is not True
                or any(cutout.get(key) is not False for key in (
                    'privacy_certified', 'medical_safety_verified',
                    'independent_qd_pass', 'source_review_approved',
                    'merchant_approved', 'release_authorized', 'public_published'))):
            raise ValueError('R263 wallet privacy NON-PASS evidence/HARD HOLD drift')
        result['family_card_wallet_cutout_privacy_witness'] = cutout
        # An editorial option is NOT a source correction or approval. Authenticate
        # its exact preview bytes, then separately inspect its visible copy.
        if git_blob(safe_read(root, R249_UNPUBLISHED_PREVIEW_PATH)) != R249_UNPUBLISHED_PREVIEW_BLOB:
            raise ValueError('R249 unpublished reader-preview identity changed')
        preview_guard = load_frozen_gate(root, R249_READER_COPY_PATH,
                                        R249_READER_COPY_BLOB,
                                        'fv_preparedness_r249_reader_copy', ('audit',))
        preview = preview_guard.audit(root, safe_read)
        if (preview.get('state') != HOLD or preview.get('printed_full_fields') != 13
                or preview.get('printed_shorter_fields') != 6
                or preview.get('excluded_shorter_fields') != 7
                or preview.get('visible_free_destinations') != ['/preparedness/']
                or preview.get('human_review_required') is not True
                or any(preview.get(k) is not False for k in (
                    'source_and_medical_safety_approved', 'browser_print_verified',
                    'privacy_certified', 'independent_qd_pass',
                    'commerce_approved', 'release_authorized'))):
            raise ValueError('R249 reader-preview citation/commerce HARD HOLD drift')
        result['unapproved_reader_copy_preview'] = preview
        alignment_guard = load_frozen_gate(root, R250_SOURCE_READER_PATH,
                                           R250_SOURCE_READER_BLOB,
                                           'fv_preparedness_r250_source_reader', ('inspect',))
        alignment = alignment_guard.inspect(
            field_matrix, preview, safe_read(root, R249_UNPUBLISHED_PREVIEW_PATH).decode('utf-8', 'strict'))
        if (alignment.get('state') != HOLD
                or alignment.get('source_to_reader_six_field_parity') != 'OBSERVED_NOT_APPROVED'
                or alignment.get('printed_shorter_fields') != 6
                or alignment.get('human_review_required') is not True
                or any(alignment.get(k) is not False for k in (
                    'independent_qd_pass', 'source_review_approved',
                    'privacy_certified', 'medical_safety_verified',
                    'merchant_approved', 'release_authorized'))):
            raise ValueError('R250 source-to-reader evidence HARD HOLD drift')
        result['unapproved_reader_source_alignment'] = alignment
        context_guard = load_frozen_gate(root, R251_READER_CONTEXT_PATH,
                                         R251_READER_CONTEXT_BLOB,
                                         'fv_preparedness_r251_reader_visible', ('inspect',))
        visible = context_guard.inspect(
            safe_read(root, R249_UNPUBLISHED_PREVIEW_PATH).decode('utf-8', 'strict'),
            preview)
        if (visible.get('state') != HOLD
                or visible.get('scope') != 'UNAPPROVED_OFFLINE_READER_COPY_ONLY'
                or visible.get('visible_paragraph_count') != 7
                or visible.get('unique_free_destinations') != ['/preparedness/']
                or visible.get('human_review_required') is not True
                or any(visible.get(k) is not False for k in (
                    'source_review_approved', 'medical_safety_verified',
                    'privacy_certified', 'independent_qd_pass',
                    'merchant_approved', 'release_authorized'))):
            raise ValueError('R251 conditional reader-disclosure context HARD HOLD drift')
        result['unapproved_reader_visible_context'] = visible
        # Three frozen source citations remain independent HUMAN REVIEW,
        # even where an agency page can be retrieved successfully.
        r252 = load_frozen_gate(root, R252_DISPUTED_CLAIMS_PATH,
                                R252_DISPUTED_CLAIMS_BLOB,
                                'fv_preparedness_r252_claim_review',
                                ('audit_bytes', 'strict_json', 'git_blob'))
        review_docket_raw = safe_read(root, R252_REVIEW_DOCKET_PATH)
        if git_blob(review_docket_raw) != R252_REVIEW_DOCKET_BLOB:
            raise ValueError('R252 citation review docket Git identity drift')
        claim_hold = r252.audit_bytes(
            {
                'homemade-water-filters': safe_read(
                    root, 'content/articles/homemade-water-filters.body.html'),
                'preparedness-real-households': safe_read(
                    root, 'content/articles/preparedness-real-households.body.html'),
            }, r252.strict_json(review_docket_raw))
        if (claim_hold.get('state') != HOLD
                or claim_hold.get('observed_count') != 3
                or claim_hold.get('shared_source_groups_still_unreviewed') != 32
                or claim_hold.get('ready_gov_page_verified') is not False
                or any(claim_hold.get(k) is not False for k in (
                    'human_claim_approved', 'human_source_approved',
                    'medical_safety_verified', 'independent_qd_pass',
                    'commerce_approved', 'publication_authorized'))):
            raise ValueError('R252 three citation-claim occurrences HARD HOLD drift')
        result['unadjudicated_citation_claims'] = claim_hold
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
        if git_blob(safe_read(root, R236_PARITY_PATH)) != R236_PARITY_BLOB:
            raise ValueError('R236 citation-parity gate mutated during audit')
        if git_blob(safe_read(root, R238_VISIBILITY_PATH)) != R238_VISIBILITY_BLOB:
            raise ValueError('R238 source citation visibility gate mutated during audit')
        if git_blob(safe_read(root, R239_SOLIDUS_PATH)) != R239_SOLIDUS_BLOB:
            raise ValueError('R239 browser solidus gate mutated during audit')
        if git_blob(safe_read(root, R240_ENTITY_ATTR_PATH)) != R240_ENTITY_ATTR_BLOB:
            raise ValueError('R240 encoded visibility attribute gate mutated during audit')
        if git_blob(safe_read(root, R243_ACTIVE_SOURCE_PATH)) != R243_ACTIVE_SOURCE_BLOB:
            raise ValueError('R243 authored active-markup/source guard mutated during audit')
        if git_blob(safe_read(root, R246_FAMILY_CARD_PATH)) != R246_FAMILY_CARD_BLOB:
            raise ValueError('R246 Article 15 / Tool 104 source-claim guard mutated during audit')
        if git_blob(safe_read(root, R247_NOJS_CARD_PATH)) != R247_NOJS_CARD_BLOB:
            raise ValueError('R247 no-JS card source-to-claim guard mutated during audit')
        if git_blob(safe_read(root, R248_FIELD_CROSSWALK_PATH)) != R248_FIELD_CROSSWALK_BLOB:
            raise ValueError('R248 family-card field crosswalk mutated during audit')
        if git_blob(safe_read(root, R249_READER_COPY_PATH)) != R249_READER_COPY_BLOB:
            raise ValueError('R249 reader-preview guard changed during audit')
        if git_blob(safe_read(root, R249_UNPUBLISHED_PREVIEW_PATH)) != R249_UNPUBLISHED_PREVIEW_BLOB:
            raise ValueError('R249 reader-preview HTML changed during audit')
        if git_blob(safe_read(root, R250_SOURCE_READER_PATH)) != R250_SOURCE_READER_BLOB:
            raise ValueError('R250 source-to-reader guard changed during audit')
        if git_blob(safe_read(root, R251_READER_CONTEXT_PATH)) != R251_READER_CONTEXT_BLOB:
            raise ValueError('R251 reader-disclosure context guard changed during audit')
        if git_blob(safe_read(root, R252_DISPUTED_CLAIMS_PATH)) != R252_DISPUTED_CLAIMS_BLOB:
            raise ValueError('R252 citation-claim gate changed during audit')
        if git_blob(safe_read(root, R252_REVIEW_DOCKET_PATH)) != R252_REVIEW_DOCKET_BLOB:
            raise ValueError('R252 source-scope review docket changed during audit')
        if git_blob(safe_read(root, R253_SOURCE_CONTEXT_PATH)) != R253_SOURCE_CONTEXT_BLOB:
            raise ValueError('R253 source-context join gate changed during audit')
        if git_blob(safe_read(root, R254_READABLE_WORKORDERS_PATH)) != R254_READABLE_WORKORDERS_BLOB:
            raise ValueError('R254 readable claim review gate changed during audit')
        if git_blob(safe_read(root, R255_REVIEW_SURFACE_PATH)) != R255_REVIEW_SURFACE_BLOB:
            raise ValueError('R255 offline reviewer surface guard changed during audit')
        if git_blob(safe_read(root, R257_PARTITION_PATH)) != R257_PARTITION_BLOB:
            raise ValueError('R257 complete citation partition gate changed during audit')
        if git_blob(safe_read(root, R260_PRINT_DISCLOSURE_PATH)) != R260_PRINT_DISCLOSURE_BLOB:
            raise ValueError('R260 print/privacy disclosure witness changed during audit')
        if git_blob(safe_read(root, R261_PRINT_DRAFT_PATH)) != R261_PRINT_DRAFT_BLOB:
            raise ValueError('R261 offline print privacy draft gate changed during audit')
        if git_blob(safe_read(root, R262_NOJS_TRUTH_PATH)) != R262_NOJS_TRUTH_BLOB:
            raise ValueError('R262 truthful no-JS draft gate changed during audit')
        if git_blob(safe_read(root, R263_WALLET_PRIVACY_PATH)) != R263_WALLET_PRIVACY_BLOB:
            raise ValueError('R263 wallet privacy witness gate changed during audit')
        if git_blob(safe_read(root, R258_COMPLETE_REVIEW_PATH)) != R258_COMPLETE_REVIEW_BLOB:
            raise ValueError('R258 2000-citation offline reviewer gate changed during audit')
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
