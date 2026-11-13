#!/usr/bin/env python3
"""R349: bind EVERY authored citation occurrence to frozen registered source identities.

Private, read-only audit. A URL, token, verification date, or source-use declaration
is NOT claim support, a human link check, qualified safety review, QD pass, or a sale.
Never writes to WordPress, social platforms, analytics or source files.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec
import json
import re

def _load_sibling(name):
    path = Path(__file__).resolve().with_name(name + '.py')
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


registry = _load_sibling('r344_source_url_identity_citation_hold')
cited = _load_sibling('r348_citation_occurrence_crosswalk_hold')

SCHEMA = 'fv-preparedness-r349-41-document-citation-registry-join-v1'
R348_BLOB = '98d083b7ec202a2e467863419398e5814747b714'
R344_BLOB = '4d9b562c72c13c8a1fd71fd1f2129571b8d35dbf'
HOLD = {'may_publish': False, 'may_merge': False, 'qualified_qd_pass': False,
        'independent_claim_support_verified': False,
        'human_link_check_verified': False, 'safety_review_approved': False,
        'commerce_offer_verified': False, 'realized_net_revenue_verified': False,
        'native_export_verified': False}


def hexhash(value: str) -> str:
    return sha256(value.encode('utf-8')).hexdigest()


def join_documents(documents: list[dict], catalog: dict, *, complete: bool = True) -> dict:
    """Pure deterministic audit. Inputs can be synthetic, output never contains claim text."""
    errors = list(catalog.get('errors', [])) if isinstance(catalog, dict) else ['INVALID_CATALOG']
    rows = catalog.get('rows', {}) if isinstance(catalog, dict) else {}
    if not isinstance(rows, dict):
        rows = {}
        errors.append('INVALID_SOURCE_REGISTRY_ROWS')
    if not isinstance(documents, list):
        documents = []
        errors.append('INVALID_DOCUMENTS')
    if complete and (sum(d.get('kind') == 'articles' for d in documents if isinstance(d, dict)) != 35 or
                     sum(d.get('kind') == 'tools' for d in documents if isinstance(d, dict)) != 6):
        errors.append('NOT_EXACTLY_35_ARTICLES_AND_6_TOOLS')
    seen, seen_slugs, out, declarations, ids = set(), set(), [], [], Counter()
    for d in sorted(documents, key=lambda a: (str(a.get('kind','')), str(a.get('slug',''))) if isinstance(a, dict) else ('','')):
        if not isinstance(d, dict):
            errors.append('INVALID_DOCUMENT_ENTRY')
            continue
        kind, slug = d.get('kind'), d.get('slug')
        if kind not in ('articles', 'tools') or not isinstance(slug, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug):
            errors.append('INVALID_DOCUMENT_ID')
            continue
        key = kind + '/' + slug
        if key in seen:
            errors.append('DUPLICATE_CANONICAL_DOCUMENT_ID:' + key)
        seen.add(key)
        if slug in seen_slugs:
            errors.append('CROSS_TYPE_SLUG_COLLISION:' + slug)
        seen_slugs.add(slug)
        record = cited.inspect_record(slug, d.get('body'), d.get('meta'), kind)
        errors.extend(key + ':' + e for e in record.get('errors', []))
        meta = d.get('meta') if isinstance(d.get('meta'), dict) else {}
        uses = meta.get('source_use') if isinstance(meta.get('source_use'), dict) else {}
        for sid in sorted(uses):
            if not isinstance(sid, str):
                errors.append(key + ':INVALID_SOURCE_USE_ID')
                continue
            if sid not in rows:
                errors.append(key + ':DECLARED_SOURCE_NOT_REGISTERED:' + sid)
            if sid not in {c['source_id'] for c in record['citations']}:
                declarations.append({'document': key, 'source_id': sid, 'status': 'DECLARED_NOT_CITED_DOES_NOT_ESTABLISH_CLAIM_SUPPORT'})
        for occurrence in record['citations']:
            sid = occurrence['source_id']
            ids[sid] += 1
            src = rows.get(sid)
            if not isinstance(src, dict):
                errors.append(key + ':CITED_SOURCE_NOT_REGISTERED:' + sid)
            else:
                if src.get('verified_on') is None:
                    errors.append(key + ':SOURCE_RESEARCH_UNVERIFIED:' + sid)
                if src.get('human_link_check') is True:
                    errors.append(key + ':UNATTESTED_HUMAN_LINK_CHECK_FLAG:' + sid)
            out.append({'document': key, 'source_id': sid,
                        'ordinal': occurrence['ordinal'],
                        'region_tag': occurrence['region_tag'],
                        'region_sha256': occurrence['region_sha256'],
                        'occurrence_sha256': occurrence['occurrence_sha256'],
                        'source_identity_sha256': src.get('source_identity_sha256') if isinstance(src, dict) else None,
                        'url_sha256': hexhash(src['canonical_source_url']) if isinstance(src, dict) and isinstance(src.get('canonical_source_url'), str) else None,
                        'metadata_source_use_sha256': hexhash(uses[sid]) if isinstance(uses.get(sid), str) else None,
                        'review_required': True})
    disputed = [r for r in out if r['source_id'] in cited.CONFLICTS]
    counts = {sid: ids[sid] for sid in sorted(ids)}
    return {'schema': SCHEMA, 'status': 'INVALID_HARD_HOLD' if errors else 'DRAFT_CROSSWALK_ONLY_HARD_HOLD',
            'errors': sorted(set(errors)), 'documents_inspected': len(seen),
            'all_citations': out, 'occurrences_count': len(out),
            'registered_sources_used': len(counts), 'per_source_counts': counts,
            'declared_only_source_uses': declarations,
            'disputed_occurrences': len(disputed),
            'disputed_occurrence_fingerprints': [r['occurrence_sha256'] for r in disputed],
            'disputed_source_ids': sorted(set(r['source_id'] for r in disputed)),
            'private_claim_text_exported': False,
            'research_fetch_is_not_human_claim_verification': True, **HOLD}


def read_documents(prep: Path) -> tuple[list[dict], list[str]]:
    docs, errors = [], []
    content = prep / 'content'
    for kind, count in (('articles', 35), ('tools', 6)):
        folder = content / kind
        if folder.is_symlink() or not folder.is_dir():
            errors.append('UNSAFE_OR_MISSING_CONTENT_DIRECTORY:' + kind)
            continue
        bodies = sorted(folder.glob('*.body.html'))
        metas = sorted(folder.glob('*.meta.json'))
        if len(bodies) != count or len(metas) != count:
            errors.append('INCOMPLETE_CONTENT_SLATE:' + kind)
        if {p.name[:-10] for p in bodies} != {p.name[:-10] for p in metas}:
            errors.append('BODY_METADATA_IDENTITY_MISMATCH:' + kind)
        for body_path in bodies:
            slug = body_path.name.removesuffix('.body.html')
            meta_path = folder / (slug + '.meta.json')
            if body_path.is_symlink() or meta_path.is_symlink() or not meta_path.is_file():
                errors.append('UNSAFE_CANONICAL_SOURCE_PAIR:' + kind + '/' + slug)
                continue
            try:
                raw = body_path.read_text(encoding='utf8')
                data = json.loads(meta_path.read_text(encoding='utf8'))
            except (ValueError, UnicodeError, OSError):
                errors.append('UNREADABLE_CANONICAL_PAIR:' + kind + '/' + slug)
                continue
            docs.append({'kind': kind, 'slug': slug, 'body': raw, 'meta': data})
    return docs, errors


def audit_native(root: Path) -> dict:
    prep = root / 'preparedness' if (root / 'preparedness').is_dir() else root
    docs, errors = read_documents(prep)
    try:
        r344_path = prep / 'tools' / 'r344_source_url_identity_citation_hold.py'
        if r344_path.is_symlink() or not r344_path.is_file() or cited.git_blob(r344_path.read_bytes()) != R344_BLOB:
            errors.append('R344_PREDECESSOR_COMMITTED_GIT_BLOB_MISMATCH')
        r348_path = prep / 'tools' / 'r348_citation_occurrence_crosswalk_hold.py'
        if r348_path.is_symlink() or not r348_path.is_file() or cited.git_blob(r348_path.read_bytes()) != R348_BLOB:
            errors.append('R348_PREDECESSOR_COMMITTED_GIT_BLOB_MISMATCH')
        prior = cited.native_audit(root)
        if prior.get('errors') or prior.get('documents_checked') != 41 or prior.get('may_publish') is not False:
            errors.append('R348_NATIVE_41_SOURCE_CUSTODY_FAILED')
        catalog = registry.read_frozen_catalog(prep)
        result = join_documents(docs, catalog)
        if prior.get('citation_occurrences') != result['occurrences_count']:
            errors.append('CROSSWALK_OCCURRENCE_COUNT_DISAGREES_WITH_R348')
        if len(prior.get('disputed_source_occurrences', [])) != result['disputed_occurrences']:
            errors.append('DISPUTED_OCCURRENCE_COUNT_DISAGREES_WITH_R348')
    except (ImportError, OSError, ValueError, TypeError, KeyError, AttributeError) as e:
        result = join_documents(docs, {'rows': {}, 'errors': []})
        errors.append('NATIVE_SOURCE_CUSTODY_UNAVAILABLE:' + type(e).__name__)
    result['errors'] = sorted(set(result['errors'] + errors))
    result['status'] = 'INVALID_HARD_HOLD' if result['errors'] else 'DRAFT_CROSSWALK_ONLY_HARD_HOLD'
    return result


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description='R349 41-document citation registry join; always HARD HOLD')
    ap.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[2])
    args = ap.parse_args()
    print(json.dumps(audit_native(args.repo_root), indent=2, sort_keys=True))
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
