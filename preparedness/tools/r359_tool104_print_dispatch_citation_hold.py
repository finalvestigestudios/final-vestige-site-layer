#!/usr/bin/env python3
"""R359: read-only custody of Tool #104 print, dispatch, privacy and citations.

A matching source fingerprint is *evidence of identity*, not a medical/privacy/
emergency approval. Synthetic inputs may test implementation only. Every result holds.
"""
from __future__ import annotations
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import sys

SCHEMA = 'fv-preparedness-r359-tool104-claim-placement-v1'
BASE_REF = 'fa6957edab05bacd3ca18d1efb4a9c622562a695'
TOOL_PATH = 'preparedness/content/tools/family-reunification-card.body.html'
META_PATH = 'preparedness/content/tools/family-reunification-card.meta.json'
ARTICLE_PATH = 'preparedness/content/articles/family-communication-plan.body.html'
PINS = {'tool': 'be8698ac5d020476ff649d85813810e2000c6f98',
        'metadata': '47da1e7e20e39f0ea85e26d54a8d58301f6e0a15',
        'article': '8ac8bd7dba3be15d477c15737e54d83364d72527'}
HOLD = dict(may_merge=False, may_publish=False, qd_pass=False,
            safety_review_complete=False, privacy_review_complete=False,
            verified_sale=False, native_export_verified=False)
CITE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
LINK = re.compile(r'\{\{link:([a-z0-9-]+)\|[^{}]*\}\}')
SCRIPT = re.compile(r'\{\{inline-js:([a-zA-Z0-9_.-]+)\}\}')


def git_blob(text):
    data = text.encode('utf-8')
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()


class NoticeParser(HTMLParser):
    """Collect exact ancestor tag/classes for printed notice, not browser layout."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.notices = []
        self.cards = []
    def handle_starttag(self, tag, attrs):
        fields = dict(attrs)
        self.stack.append((tag, set(fields.get('class', '').split())))
        if tag == 'div' and 'pa-card-mainhide' in self.stack[-1][1]:
            self.cards.append(len(self.stack))
    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break
    def handle_data(self, data):
        if 'A printed card can be lost' in data:
            self.notices.append((data.strip(),
                 any('pa-card-mainhide' in css for _, css in self.stack)))


def inspect(tool: str, metadata: str, article: str, *, authenticate=False) -> dict:
    errors, docket, facts = [], [], {}
    try:
        if any(not isinstance(t, str) or len(t) > 250000 for t in (tool,metadata,article)):
            raise ValueError('INVALID_INPUT')
        sources = dict(tool=tool, metadata=metadata, article=article)
        facts['git_blobs'] = {key: git_blob(value) for key,value in sources.items()}
        if authenticate and any(facts['git_blobs'][key] != sha for key,sha in PINS.items()):
            errors.append('ORIGINAL_GIT_IDENTITY_DRIFT')
        meta = json.loads(metadata)
        if not isinstance(meta, dict):
            raise ValueError('INVALID_METADATA_OBJECT')
        if meta.get('slug') != 'family-reunification-card' or meta.get('kind') != 'tool':
            errors.append('TOOL_IDENTITY_INVALID')
        state = meta.get('status')
        safety = meta.get('safety_review')
        if not isinstance(state,dict) or not isinstance(safety,dict) or state.get('publish') != 'draft' or safety.get('state') != 'pending':
            errors.append('UNAUTHORIZED_PUBLICATION_OR_SAFETY_STATE')
        source_use = meta.get('source_use')
        if not isinstance(source_use,dict) or not source_use or any(not re.fullmatch(r'[a-z0-9-]+', k) for k in source_use):
            errors.append('SOURCE_USE_INVALID')
            source_use = {}
        cites = CITE.findall(tool)
        fact_links = LINK.findall(tool)
        article_cites = CITE.findall(article)
        facts.update(tool_citation_occurrences=len(cites), tool_citation_unique=len(set(cites)),
                     tool_citation_ids=sorted(set(cites)), source_use_ids=sorted(source_use),
                     article_citation_occurrences=len(article_cites),
                     related_link_ids=sorted(set(fact_links)),
                     script_dependencies=sorted(set(SCRIPT.findall(tool))))
        if not cites or not article_cites:
            errors.append('SOURCE_CITATIONS_MISSING')
        if set(cites)-set(source_use):
            errors.append('UNDECLARED_CITATION:'+','.join(sorted(set(cites)-set(source_use))))
        if set(source_use)-set(cites):
            docket.append('UNUSED_SOURCE_DECLARATION_REVIEW:'+','.join(sorted(set(source_use)-set(cites))))
        if not fact_links:
            errors.append('RELATED_GUIDE_LINKS_MISSING')
        if not facts['script_dependencies']:
            errors.append('INTERACTIVE_SCRIPT_PROVENANCE_MISSING')
        parser = NoticeParser()
        parser.feed(tool)
        facts['printed_loss_notice_source_count'] = len(parser.notices)
        facts['loss_notice_under_mainhide'] = bool(parser.notices) and all(n[1] for n in parser.notices)
        print_rules = re.findall(r'@media\s+print\s*\{(.+?)(?=\n\s*\}\s*\n\s*</style>|\Z)', tool, flags=re.S|re.I)
        facts['print_css_hides_mainhide'] = any(re.search(r'\.pa-card-mainhide\s*\{\s*display\s*:\s*none\s*!important', block, re.I) for block in print_rules)
        facts['loss_notice_at_risk_of_print_omission'] = facts['loss_notice_under_mainhide'] and facts['print_css_hides_mainhide']
        if not parser.notices:
            errors.append('CARRIED_CARD_WARNING_SOURCE_MISSING')
        if facts['loss_notice_at_risk_of_print_omission']:
            docket.append('PRINT_WARNING_HIDDEN_IN_AUTHORED_PRINT_CSS_REQUIRES_REVIEW')
        facts['life_threat_only_911'] = bool(re.search(r'call\s+911\s+for\s+anything\s+life-threatening',tool,re.I))
        facts['absolute_privacy_promise'] = ('It is not sent or saved' in tool and 'Closing the tab clears it' in tool)
        facts['excludes_child_full_name'] = bool(re.search(r'Do not put a child\'s full name',tool,re.I))
        facts['small_print_7_5pt'] = bool(re.search(r'font-size\s*:\s*7\.5pt',tool,re.I))
        for key,flag in [('EMERGENCY_DISPATCH_NARROWING',facts['life_threat_only_911']),
                         ('UNVERIFIED_ABSOLUTE_PRIVACY_PROMISE',facts['absolute_privacy_promise']),
                         ('CHILD_CARD_COMPLETENESS_REVIEW',facts['excludes_child_full_name']),
                         ('PRINT_LEGIBILITY_REVIEW',facts['small_print_7_5pt'])]:
            if flag: docket.append(key)
        if not {'family-communication-plan','shelter-or-evacuate'}.issubset(set(fact_links)):
            errors.append('CROSS_REFERENCE_LOST')
    except (ValueError, TypeError, KeyError, UnicodeError, json.JSONDecodeError) as exc:
        errors.append('INVALID_SOURCE:'+str(exc)[:100])
    return dict(schema=SCHEMA,status='INVALID_HARD_HOLD' if errors else 'QUALIFIED_REVIEW_REQUIRED_HARD_HOLD',
                input_mode='GIT_PINNED' if authenticate else 'SYNTHETIC_UNVERIFIED',
                errors=sorted(set(errors)), review_docket=sorted(set(docket)), facts=facts, **HOLD)


def native_review(repo: Path) -> dict:
    try:
        repo = Path(repo).resolve(strict=True)
        if not (repo/'.git').exists(): raise ValueError('MISSING_AUTHENTIC_CHECKOUT')
        cmd = ['git','-C',str(repo),'rev-parse','--show-toplevel']
        p = subprocess.run(cmd,capture_output=True,check=True,timeout=15)
        if Path(p.stdout.decode().strip()).resolve()!=repo: raise ValueError('REPO_ROOT_MISMATCH')
        inputs=[]
        for path in (TOOL_PATH,META_PATH,ARTICLE_PATH):
            p=subprocess.run(['git','-C',str(repo),'show',BASE_REF+':'+path],
                             capture_output=True,check=True,timeout=15)
            inputs.append(p.stdout.decode('utf-8','strict'))
        return inspect(*inputs,authenticate=True)
    except (OSError,ValueError,UnicodeError,subprocess.SubprocessError) as exc:
        return dict(schema=SCHEMA,status='INVALID_HARD_HOLD',errors=['NATIVE_SOURCE_UNAVAILABLE:'+type(exc).__name__],**HOLD)


if __name__ == '__main__':
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[2])
    print(json.dumps(native_review(ap.parse_args().repo_root),sort_keys=True,indent=2))
    sys.exit(2)  # Tests never constitute emergency, privacy, QD or publish approval.
