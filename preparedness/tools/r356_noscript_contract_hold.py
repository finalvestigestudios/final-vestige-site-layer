#!/usr/bin/env python3
"""R356: original Tool #104 no-JS/print promises. Source-only, read-only HARD HOLD."""
from __future__ import annotations
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import r355_sensitive_form_privacy_provenance_hold as prior

SCHEMA = 'fv-preparedness-r356-noscript-contract-v1'
HOLD = dict(prior.HOLD, no_js_function_verified=False, no_js_download_verified=False,
            paper_print_verified=False, may_activate_paid_cta=False)
NS = re.compile(r'<noscript\b[^>]*>(.*?)</noscript\s*>', re.I | re.S)
CSS = re.compile(r'([^{}]+)\{([^{}]*)\}', re.S)
STYLE = re.compile(r'<style\b[^>]*>(.*?)</style\s*>', re.I | re.S)
FORM = re.compile(r'<form\b[^>]*\bid\s*=\s*["\']rc["\'][^>]*>', re.I | re.S)


class Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
    def handle_data(self, text):
        self.parts.append(text)


def visible_text(markup):
    parser = Text()
    parser.feed(STYLE.sub('', markup))
    parser.close()
    return ' '.join(' '.join(parser.parts).split())


def hides_form(blocks, tag):
    classes = re.search(r'\bclass\s*=\s*["\']([^"\']+)["\']', tag, re.I)
    accepted = {'#rc', 'form#rc'} | ({'.'+x for x in classes.group(1).split()} if classes else set())
    for block in blocks:
        for css in STYLE.findall(block):
            for selectors, declarations in CSS.findall(css):
                if not re.search(r'(?:^|;)\s*display\s*:\s*none\s*(?:!important)?\s*(?:;|$)', declarations, re.I):
                    continue
                if any(selector.strip() in accepted for selector in selectors.split(',')):
                    return True
    return False


def review(body, metadata):
    if not isinstance(body, str) or not isinstance(metadata, dict):
        return {'schema': SCHEMA, 'status': 'INVALID_HARD_HOLD', 'issues': ['INVALID_INPUT'], **HOLD}
    issues=[]
    if metadata.get('slug')!='family-reunification-card' or metadata.get('kind')!='tool':
        issues.append('TOOL104_IDENTITY_DRIFT')
    if not isinstance(metadata.get('status'),dict) or metadata['status'].get('publish')!='draft':
        issues.append('PUBLICATION_STATE_DRIFT')
    if not isinstance(metadata.get('safety_review'),dict) or metadata['safety_review'].get('state')!='pending':
        issues.append('PENDING_SAFETY_GATE_DRIFT')
    source_use = metadata.get('source_use')
    if not isinstance(source_use,dict) or set(prior.CITE.findall(body))-set(source_use):
        issues.append('CITATION_DECLARATIONS_INCOMPLETE')
    if not {'shelter_common.js','reunion_card.js'} <= set(prior.INCLUDE.findall(body)):
        issues.append('EMBEDDED_JS_DEPENDENCIES_DRIFT')
    form=FORM.search(body)
    if not form:
        issues.append('FORM_ID_MISSING')
    ns=NS.findall(body)
    if not ns:
        issues.append('NOSCRIPT_FALLBACK_MISSING')
    copy=' '.join(visible_text(n) for n in ns)
    hidden=hides_form(ns, form.group()) if form else False
    form_claim=bool(re.search(r'form\s+below\s+still\s+works',copy,re.I))
    download_claim=bool(re.search(r'text\s+download',copy,re.I))
    blank=any('pa-printsheet' in b and 'pa-foldcard' in b for b in ns)
    if form_claim:
        issues.append('NOSCRIPT_FORM_HIDDEN_CONTRADICTS_COPY' if hidden else 'NOSCRIPT_FORM_BEHAVIOR_UNVERIFIED')
    if download_claim:
        ui=bool(re.search(r'<(?:button|a)\b[^>]*(?:\bdownload\b|\bid=["\'][^"\']*(?:download|export))',body,re.I|re.S))
        issues.append('TEXT_DOWNLOAD_RUNTIME_UNVERIFIED' if ui else 'TEXT_DOWNLOAD_UI_NOT_EVIDENCED')
    if not blank:
        issues.append('BLANK_PRINT_CARD_NOT_EVIDENCED')
    if re.search(r'\.pa-foldcard\s+\.pa-face\s*\{[^}]*font-size\s*:\s*7\.5pt',body,re.I|re.S):
        issues.append('ORIGINAL_7_5PT_PRINT_REQUIRES_HUMAN_LEGIBILITY_TEST')
    if re.search(r'closing\s+(?:the|this)\s+tab\s+clears',body,re.I):
        issues.append('TAB_CLOSE_PRIVACY_PROMISE_UNVERIFIED')
    if re.search(r'not\s+sent\s+or\s+saved',body,re.I):
        issues.append('NO_SEND_NO_SAVE_PRIVACY_PROMISE_UNVERIFIED')
    invalid={'TOOL104_IDENTITY_DRIFT','PUBLICATION_STATE_DRIFT','PENDING_SAFETY_GATE_DRIFT',
             'CITATION_DECLARATIONS_INCOMPLETE','EMBEDDED_JS_DEPENDENCIES_DRIFT','FORM_ID_MISSING',
             'NOSCRIPT_FALLBACK_MISSING'}
    return {'schema': SCHEMA, 'status':'INVALID_HARD_HOLD' if invalid.intersection(issues) else 'REVIEW_REQUIRED_HARD_HOLD',
            'issues':sorted(set(issues)), 'form_hidden_by_noscript_css':hidden,
            'form_function_claim':form_claim,'text_download_claim':download_claim,
            'blank_print_card_present_in_source':blank, 'noscript_block_count':len(ns),
            'body_sha256':prior.sha256(body),'metadata_sha256':prior.sha256(json.dumps(metadata,sort_keys=True,ensure_ascii=False)),
            'private_form_values_exported':False, **HOLD}


def native_review(repo):
    try:
        root=Path(repo).resolve(strict=True)
        if not (root/'.git').exists():
            raise ValueError('GIT_CHECKOUT_REQUIRED')
        base=root/'preparedness'
        relative=['content/tools/family-reunification-card.body.html',
                  'content/tools/family-reunification-card.meta.json','taxonomy.json']
        originals=[]
        for path in relative:
            p=base/path
            if p.is_symlink() or not p.is_file() or not p.resolve().is_relative_to(base.resolve()):
                raise ValueError('NONREGULAR_SOURCE')
            originals.append(p.read_bytes())
        if [prior.git_blob(b) for b in originals]!=[prior.EXPECTED_BODY_BLOB,prior.EXPECTED_META_BLOB,prior.EXPECTED_TAXONOMY_BLOB]:
            raise ValueError('ORIGINAL_SOURCE_HASH_DRIFT')
        return review(originals[0].decode('utf-8'),json.loads(originals[1].decode('utf-8')))
    except (OSError,ValueError,TypeError,UnicodeError,json.JSONDecodeError) as exc:
        return {'schema':SCHEMA,'status':'INVALID_HARD_HOLD',
                'issues':['NATIVE_CUSTODY_UNAVAILABLE:'+type(exc).__name__],**HOLD}

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[2])
    print(json.dumps(native_review(parser.parse_args().repo_root),sort_keys=True,indent=2))
    raise SystemExit(2) # No publication-qualified success path.
