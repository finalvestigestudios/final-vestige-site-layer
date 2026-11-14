#!/usr/bin/env python3
"""R355 Preparedness sensitive-form claims & print/runtime custody; REVIEW ONLY.

Never certify a browser's privacy, child-card completeness, or publication safety from
static source inspection. Original drafts and QA are unchanged; this is read-only.
"""
from __future__ import annotations
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re

SCHEMA = 'fv-preparedness-r355-form-privacy-claim-provenance-v1'
HOLD = dict(may_merge=False, may_publish=False, qualified_qd_pass=False,
            customer_private_data_verified=False, child_card_safe=False,
            browser_network_safety_verified=False, print_accessibility_verified=False,
            verified_paid_orders=False)
EXPECTED_BODY_BLOB = 'be8698ac5d020476ff649d85813810e2000c6f98'
EXPECTED_META_BLOB = '47da1e7e20e39f0ea85e26d54a8d58301f6e0a15'
EXPECTED_TAXONOMY_BLOB = '15c547bb3018ac182b12a51036389cfa39a59168'
IDENT = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
CITE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
INCLUDE = re.compile(r'\{\{inline-js:([a-zA-Z0-9_-]+\.js)\}\}')
ABSOLUTES = {
    'no_storage': re.compile(r'\b(?:nothing|no\s+data|information|your\s+data)\s+(?:is\s+)?(?:never\s+)?stored\b|\bnot\s+saved\b|\bis\s+not\s+(?:sent\s+or\s+)?saved\b', re.I),
    'no_transmission': re.compile(r'\b(?:not|never)\s+sent\b|\bstays?\s+(?:on|in)\s+(?:this\s+page|your\s+(?:browser|device))\b', re.I),
    'closing_clears': re.compile(r'\bclosing\s+(?:the|this)\s+tab\s+clears\b|\bcleared\s+(?:on|when)\s+tab\s+close\b', re.I),
    'local_guarantee': re.compile(r'\blocal[- ]only\b|\bruns?\s+locally\b|\bkeeps?\s+(?:your\s+)?(?:information|data)\s+on\s+(?:your|the)\s+device\b', re.I),
}


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def sha256(value: str) -> str:
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


class FieldInventory(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.form_depth = 0
        self.forms = 0
        self.fields = []
        self.scripts = 0
        self.has_inline_handlers = False
        self.external_scripts = []
        self.malformed = False

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if any(k.startswith('on') for k, _ in attrs):
            self.has_inline_handlers = True
        if tag == 'form':
            self.forms += 1
            self.form_depth += 1
        if tag == 'script':
            self.scripts += 1
            if d.get('src'):
                self.external_scripts.append(d['src'])
        if tag in ('input', 'select', 'textarea') and self.form_depth:
            self.fields.append({'kind': tag, 'name': d.get('name') or d.get('id') or '',
                                'type': d.get('type', 'text'), 'autocomplete': d.get('autocomplete')})

    def handle_endtag(self, tag):
        if tag == 'form':
            self.form_depth -= 1
            if self.form_depth < 0:
                self.malformed = True


def review(documents: dict, taxonomy: dict, *, baseline: dict | None = None) -> dict:
    """Fail closed; return a private structural finding docket, not a safety verdict."""
    errors, dockets = [], []
    if not isinstance(documents, dict) or not isinstance(taxonomy, dict):
        return {'schema': SCHEMA, 'status': 'INVALID_HARD_HOLD', 'errors': ['INPUT_INVALID'], **HOLD}
    if len(documents) != 41:
        errors.append('ORIGINAL_41_DOCUMENT_INVENTORY_INCOMPLETE')
    slugs = set()
    for slug, doc in sorted(documents.items(), key=lambda pair: str(pair[0])):
        if not isinstance(slug, str) or not IDENT.fullmatch(slug) or not isinstance(doc, dict):
            errors.append('INVALID_DOCUMENT_IDENTITY'); continue
        body, meta = doc.get('body'), doc.get('meta')
        if not isinstance(body, str) or not isinstance(meta, dict):
            errors.append('BODY_OR_META_MISSING:' + slug); continue
        if slug in slugs or meta.get('slug') != slug:
            errors.append('SLUG_IDENTITY_DRIFT:' + slug)
        slugs.add(slug)
        if not body.strip() or not isinstance(meta.get('source_use'), dict):
            errors.append('BODY_EMPTY_OR_SOURCE_USE_MISSING:' + slug)
        if not isinstance(meta.get('status'), dict) or meta['status'].get('publish') != 'draft':
            errors.append('PUBLICATION_STATE_NOT_DRAFT:' + slug)
        if not isinstance(meta.get('safety_review'), dict) or meta['safety_review'].get('state') not in ('pending', 'not-required'):
            errors.append('SAFETY_REVIEW_STATE_UNACCEPTABLE:' + slug)
        source_use = meta.get('source_use') if isinstance(meta.get('source_use'), dict) else {}
        unmatched = sorted(set(CITE.findall(body)) - set(source_use))
        if unmatched:
            errors.append('UNDECLARED_BODY_SOURCE:' + slug)
        inv = FieldInventory()
        try:
            inv.feed(body)
            inv.close()
        except (ValueError, TypeError):
            errors.append('FORM_HTML_UNPARSABLE:' + slug); continue
        if inv.malformed or inv.form_depth:
            errors.append('FORM_MARKUP_UNBALANCED:' + slug)
        if inv.forms and inv.fields:
            promises = []
            for where, value in (('body', body), ('description', meta.get('description', '')),
                                 ('dek', meta.get('dek', '')), ('tags', ' '.join(meta.get('tags', []) if isinstance(meta.get('tags'), list) else []))):
                if not isinstance(value, str):
                    errors.append('INVALID_PRIVACY_COPY:' + slug); continue
                for label, regex in ABSOLUTES.items():
                    if regex.search(value):
                        promises.append({'field': where, 'claim': label, 'source_sha256': sha256(value)})
            dockets.append({'slug': slug, 'input_count': len(inv.fields),
                            'privacy_claims': sorted(promises, key=lambda x:(x['field'], x['claim'])),
                            'inline_js_dependencies': sorted(set(INCLUDE.findall(body))),
                            'external_script_count': len(inv.external_scripts),
                            'inline_handlers_present': inv.has_inline_handlers,
                            'requires_human_runtime_review': True,
                            'source_body_sha256': sha256(body)})
    planned = taxonomy.get('tools')
    if not isinstance(planned, list) or len(planned) != 9:
        errors.append('NINE_TOOL_PLAN_MISSING')
    else:
        planned_slugs = [row.get('slug') for row in planned if isinstance(row, dict)]
        if len(planned_slugs) != 9 or not all(isinstance(x, str) and IDENT.fullmatch(x) for x in planned_slugs) or len(set(planned_slugs)) != 9:
            errors.append('DUPLICATE_OR_INVALID_TOOL_PLAN')
        authored = set(x for x in planned_slugs if isinstance(x, str)) & slugs
        if len(authored) != 6:
            errors.append('SIX_AUTHORED_TOOLS_NOT_ACCOUNTED')
    for row in taxonomy.get('sections', []) if isinstance(taxonomy.get('sections'), list) else []:
        if not isinstance(row, dict):
            errors.append('INVALID_SECTION'); continue
        if row.get('slug') == 'field-tools':
            text = row.get('blurb', '')
            if not isinstance(text, str):
                errors.append('INVALID_FIELD_TOOL_DESCRIPTION')
            elif any(p.search(text) for p in ABSOLUTES.values()):
                dockets.append({'slug': 'taxonomy/field-tools', 'privacy_claims':
                    [{'field': 'blurb', 'claim': label, 'source_sha256': sha256(text)} for label,p in ABSOLUTES.items() if p.search(text)],
                    'requires_human_runtime_review': True})
    if baseline is not None:
        if not isinstance(baseline, dict):
            errors.append('INVALID_BASELINE')
        else:
            for slug, want in baseline.items():
                d = documents.get(slug)
                if not isinstance(d, dict) or not isinstance(want, dict):
                    errors.append('PINNED_SOURCE_MISSING:' + str(slug)); continue
                if sha256(d.get('body', '') if isinstance(d.get('body'), str) else '') != want.get('body_sha256'):
                    errors.append('SOURCE_BODY_EDIT_REQUIRES_ADJUDICATION:' + str(slug))
                if sha256(json.dumps(d.get('meta'), sort_keys=True, ensure_ascii=False)) != want.get('meta_sha256'):
                    errors.append('SOURCE_META_EDIT_REQUIRES_ADJUDICATION:' + str(slug))
    tool104 = next((r for r in dockets if r['slug'] == 'family-reunification-card'), None)
    if not tool104:
        errors.append('TOOL104_FORM_NOT_FOUND')
    else:
        required = {('body', 'no_storage'), ('body', 'no_transmission'), ('body', 'closing_clears')}
        if not required <= {(p['field'],p['claim']) for p in tool104['privacy_claims']}:
            errors.append('TOOL104_ORIGINAL_PROMISE_FINGERPRINT_CHANGED_REVIEW_REQUIRED')
        if not {'shelter_common.js','reunion_card.js'} <= set(tool104['inline_js_dependencies']):
            errors.append('TOOL104_INLINE_DEPENDENCY_CHANGED_REVIEW_REQUIRED')
        if tool104['input_count'] < 10:
            errors.append('TOOL104_FORM_FIELDS_CHANGED_REVIEW_REQUIRED')
    return {'schema': SCHEMA, 'status': 'INVALID_HARD_HOLD' if errors else 'PRIVACY_PROVENANCE_REVIEW_REQUIRED_HARD_HOLD',
            'errors': sorted(set(errors)), 'inspected_documents': len(slugs),
            'input_form_dockets': sorted(dockets, key=lambda d:d['slug']), **HOLD}


def native_review(repo: Path) -> dict:
    """Read only the original 41-document private source corpus; no CMS access."""
    try:
        root = Path(repo).resolve(strict=True)
        if not (root/'.git').exists():
            raise ValueError('GIT_CHECKOUT_REQUIRED')
        prep = root/'preparedness'
        def read(p: Path) -> str:
            if p.is_symlink() or not p.is_file():
                raise ValueError('NONREGULAR_FILE')
            return p.read_text(encoding='utf-8')
        taxonomy_path = prep/'taxonomy.json'
        if git_blob(taxonomy_path.read_bytes()) != EXPECTED_TAXONOMY_BLOB:
            raise ValueError('TAXONOMY_PIN_CHANGED')
        documents = {}
        for part in ('articles','tools'):
            directory = prep/'content'/part
            for meta_file in sorted(directory.glob('*.meta.json')):
                slug = meta_file.name.removesuffix('.meta.json')
                body_file = directory/(slug+'.body.html')
                if slug in documents:
                    raise ValueError('DUPLICATE_SLUG')
                documents[slug] = {'body': read(body_file), 'meta': json.loads(read(meta_file))}
        tool_root = prep/'content'/'tools'
        if git_blob((tool_root/'family-reunification-card.body.html').read_bytes()) != EXPECTED_BODY_BLOB:
            raise ValueError('TOOL104_BODY_PIN_CHANGED')
        if git_blob((tool_root/'family-reunification-card.meta.json').read_bytes()) != EXPECTED_META_BLOB:
            raise ValueError('TOOL104_META_PIN_CHANGED')
        return review(documents, json.loads(read(taxonomy_path)))
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError, UnicodeError) as exc:
        return {'schema': SCHEMA, 'status': 'INVALID_HARD_HOLD',
                'errors': ['NATIVE_SOURCE_CUSTODY_UNAVAILABLE:' + type(exc).__name__], **HOLD}

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[2])
    print(json.dumps(native_review(ap.parse_args().repo_root), indent=2, sort_keys=True))
    raise SystemExit(2)  # Deliberately never a publication-safe exit.
