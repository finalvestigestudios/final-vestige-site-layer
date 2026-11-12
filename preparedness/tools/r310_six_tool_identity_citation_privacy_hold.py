#!/usr/bin/env python3
"""Read-only R310: six-tool identity, citation, privacy-claim and fallback gate.

Issue #136 / #820. Distinguishes original contributor-local tool numbers from
unique public identities; refuses to silently conflate #102/#103 source tools.
Static tests do NOT certify safety, accessibility, actual privacy or publication.
"""
from __future__ import annotations
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re

SCHEMA = 'fv-preparedness-r310-six-tool-identity-citation-privacy-v1'
PREDECESSOR = 'preparedness/tools/r309_tool_identity_hold.py'
PREDECESSOR_OID = '748e814f47984164993c5871865be95465e1b8c1'
TAXONOMY = 'preparedness/taxonomy.json'
TAXONOMY_OID = '15c547bb3018ac182b12a51036389cfa39a59168'
SLUGS = ('family-reunification-card', 'home-fire-escape-worksheet',
         'kit-builder', 'power-outage-planner', 'reunification-plan',
         'water-planner')
# Exact GitHub blob IDs of authentic integrated R309 sources. The identities
# are source custody witnesses, not content/safety certification.
BLOBS = {
 'family-reunification-card': ('be8698ac5d020476ff649d85813810e2000c6f98','47da1e7e20e39f0ea85e26d54a8d58301f6e0a15'),
 'home-fire-escape-worksheet': ('01161948b6de6ffbd1b053c9b83a420758e707e4','397c7d3072fb237b490a5a316c93fc863c101be9'),
 'kit-builder': ('2cb531174d6828fa5185c47bd2b742a0befa8353','e9be8a497df737b36d7d399fccc4a00000ce8eac'),
 'power-outage-planner': ('aa8f866aaaaab9253f41c4363d31919029c69234','8796bba2b323cce096639997002c402bd853e50f'),
 'reunification-plan': ('3305578369183edb1d427c8f8f8002eaacee420f','10cd57dc8d39e366aaef8fd76cc3f8969b8c5348'),
 'water-planner': ('a738d1f7824437911064d425868ed3d709326027','7ea188a06b614940a226328c0166c2a2b20ff84e'),
}
CITE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
LINK = re.compile(r'\{\{link:([a-z0-9-]+)(?:\|[^}]*)?\}\}')
BLOCKED_JS = (
 ('NETWORK_FETCH', r'\bfetch\s*\('),
 ('NETWORK_XHR', r'\bXMLHttpRequest\b'),
 ('NETWORK_BEACON', r'\bsendBeacon\s*\('),
 ('NETWORK_SOCKET', r'\b(?:WebSocket|EventSource)\s*\('),
 ('LOCAL_STORAGE', r'\b(?:localStorage|sessionStorage|indexedDB)\b'),
 ('COOKIE_ACCESS', r'\bdocument\s*\.\s*cookie\b'),
 ('FORM_NETWORK_SUBMIT', r'\b(?:navigator\s*\.\s*sendBeacon|window\s*\.\s*open)\b'),
)


def oid(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()


def file_bytes(root: Path, relative: str) -> bytes | None:
    """Refuse path escape, missing paths, symlinks and unreadable files."""
    if not isinstance(relative, str) or '..' in Path(relative).parts or Path(relative).is_absolute():
        return None
    base = root.absolute()
    p = base
    try:
        if p.is_symlink(): return None
        for part in Path(relative).parts:
            p = p / part
            if p.is_symlink(): return None
        if not p.is_file(): return None
        return p.read_bytes()
    except (OSError, ValueError, RuntimeError):
        return None


class _ElementAudit(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.script_stack = 0
        self.script_text = []
        self.scripts = 0
        self.noscripts = 0
        self.form_action = False
        self.remote_script = False
        self.inline_event = []
        self.duplicate_attributes = []
        self.nodes = 0

    def handle_starttag(self, tag, attrs):
        self.nodes += 1
        keys = [x[0].lower() for x in attrs]
        if len(keys) != len(set(keys)):
            self.duplicate_attributes.append(tag)
        d = dict(attrs)
        if tag == 'script':
            self.scripts += 1
            self.script_stack += 1
            if d.get('src') is not None: self.remote_script = True
        if tag == 'noscript': self.noscripts += 1
        if tag == 'form' and (d.get('action') is not None or d.get('method') is not None):
            self.form_action = True
        for k, v in attrs:
            if k.lower().startswith('on') and k.lower() not in ('onclick', 'onsubmit', 'onchange', 'oninput'):
                self.inline_event.append(k)
            if k.lower().startswith('on') and v and re.search(r'\b(?:fetch|sendBeacon|XMLHttpRequest|localStorage|sessionStorage)\b',v):
                self.inline_event.append(k + ':network_or_storage')

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag == 'script': self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag == 'script' and self.script_stack: self.script_stack -= 1

    def handle_data(self, text):
        if self.script_stack: self.script_text.append(text)


def inspect_tool(body: str, meta: dict, slug: str, known_links: set[str]) -> tuple[list[str], dict]:
    errors = []
    if not isinstance(meta, dict): return ['INVALID_METADATA:' + slug], {}
    if meta.get('slug') != slug or meta.get('kind') != 'tool' or meta.get('section') != 'field-tools':
        errors.append('TOOL_IDENTITY_DRIFT:' + slug)
    if meta.get('track') != 'modern': errors.append('TOOL_TRACK_CHANGED:' + slug)
    if not isinstance(meta.get('n'), int) or isinstance(meta.get('n'), bool) or meta['n'] <= 0:
        errors.append('TOOL_NUMBER_INVALID:' + slug)
    if meta.get('status') != {'editorial': 'drafted', 'publish': 'draft'}:
        errors.append('TOOL_PUBLICATION_OR_EDITORIAL_STATUS_CHANGED:' + slug)
    if meta.get('safety_review') != {'state': 'pending', 'reviewer': None, 'date': None}:
        errors.append('TOOL_UNAPPROVED_SAFETY_CHANGE:' + slug)
    use = meta.get('source_use')
    if not isinstance(use, dict) or not use or not all(isinstance(k, str) and isinstance(v, str) and v.strip() for k,v in use.items()):
        errors.append('SOURCE_USE_MISSING_OR_INVALID:' + slug)
        use = {}
    cited = set(CITE.findall(body))
    if cited != set(use): errors.append('CITATION_SOURCE_USE_PARITY:' + slug)
    links = set(LINK.findall(body))
    unknown = sorted(links - known_links)
    if unknown: errors.append('UNKNOWN_ARTICLE_OR_TOOL_DESTINATION:' + slug + ':' + ','.join(unknown))
    parser = _ElementAudit()
    try: parser.feed(body); parser.close()
    except (ValueError, TypeError): errors.append('MALFORMED_TOOL_MARKUP:' + slug)
    if parser.duplicate_attributes: errors.append('DUPLICATE_INLINE_ATTRIBUTES:' + slug)
    if parser.remote_script: errors.append('EXTERNAL_SCRIPT_IN_TOOL:' + slug)
    if parser.form_action: errors.append('NETWORK_FORM_ACTION:' + slug)
    if parser.inline_event: errors.append('UNREVIEWED_EVENT_HANDLER:' + slug)
    js = '\n'.join(parser.script_text)
    for code, pattern in BLOCKED_JS:
        if re.search(pattern, js, re.I): errors.append(code + ':' + slug)
    if parser.scripts and parser.noscripts == 0:
        errors.append('NO_NOSCRIPT_FALLBACK_WITNESS:' + slug)
    return errors, {'number':meta.get('n'),'cited':len(cited),'declared':len(use),
                    'link_targets':sorted(links),'script_tags':parser.scripts,
                    'noscript_tags':parser.noscripts,'static_network_storage_tokens':sum(
                        bool(re.search(pattern, js, re.I)) for _,pattern in BLOCKED_JS)}


def audit(root: Path, *, pins: dict = BLOBS, predecessor_oid: str = PREDECESSOR_OID,
          taxonomy_oid: str = TAXONOMY_OID, enforce_custody: bool = True) -> dict:
    """Deterministic; no writes or network. Synthetic tests can supply fixture pins."""
    errors = []; observed = {}; numbers: dict[int,list[str]] = {}
    if set(pins) != set(SLUGS): errors.append('SIX_TOOL_MANIFEST_INCOMPLETE_OR_EXTRA')
    if enforce_custody:
        data = file_bytes(root, PREDECESSOR)
        if data is None or oid(data) != predecessor_oid: errors.append('R309_PREDECESSOR_NOT_AUTHENTIC')
    tbytes = file_bytes(root, TAXONOMY)
    if tbytes is None or (enforce_custody and oid(tbytes)!=taxonomy_oid):
        errors.append('TAXONOMY_MISSING_OR_CHANGED');taxonomy={}
    else:
        try: taxonomy=json.loads(tbytes)
        except (UnicodeError,json.JSONDecodeError):
            errors.append('INVALID_TAXONOMY');taxonomy={}
    entries = taxonomy.get('tools',[]) if isinstance(taxonomy,dict) else []
    slate = taxonomy.get('slate',[]) if isinstance(taxonomy,dict) else []
    if not isinstance(entries,list) or not isinstance(slate,list):
        errors.append('INVALID_TAXONOMY_LAYOUT');entries=[];slate=[]
    toolrows = {x.get('slug'):x for x in entries if isinstance(x,dict) and isinstance(x.get('slug'),str)}
    known = {x.get('slug') for x in entries+slate if isinstance(x,dict) and isinstance(x.get('slug'),str)}
    if len(toolrows) != len([x for x in entries if isinstance(x,dict)]):
        errors.append('DUPLICATE_TAXONOMY_TOOL_SLUG')
    actual_files = {f.name for f in (root/'preparedness/content/tools').glob('*.body.html')}
    actual_meta = {f.name for f in (root/'preparedness/content/tools').glob('*.meta.json')}
    expected_bodies = {s+'.body.html' for s in SLUGS}
    expected_meta = {s+'.meta.json' for s in SLUGS}
    if actual_files != expected_bodies or actual_meta != expected_meta:
        errors.append('TOOL_SOURCE_SET_CHANGED')
    verified = 0
    for slug in SLUGS:
        row = toolrows.get(slug)
        if not isinstance(row,dict) or row.get('gate') is not True or row.get('status')!='drafted-pending-safety-review':
            errors.append('TAXONOMY_SAFETY_GATE_OR_ROUTE_MISSING:'+slug)
        paths=[f'preparedness/content/tools/{slug}.body.html',f'preparedness/content/tools/{slug}.meta.json']
        expected = pins.get(slug)
        if not isinstance(expected,(tuple,list)) or len(expected)!=2:
            errors.append('TOOL_BLOB_PAIR_MISSING:'+slug);continue
        raws=[]
        for path, hash_expected in zip(paths,expected):
            raw=file_bytes(root,path)
            if raw is None: errors.append('SOURCE_MISSING_OR_SYMLINK:'+path)
            elif oid(raw)!=hash_expected: errors.append('SOURCE_BLOB_CHANGED:'+path)
            else: verified+=1
            raws.append(raw)
        if not all(raw is not None for raw in raws): continue
        try:
            btext=raws[0].decode('utf-8')
            meta=json.loads(raws[1].decode('utf-8'))
        except (UnicodeError,json.JSONDecodeError):
            errors.append('SOURCE_PARSE_FAILURE:'+slug);continue
        es, observations=inspect_tool(btext,meta,slug,known)
        errors.extend(es);observed[slug]=observations
        number=observations.get('number')
        if isinstance(number,int) and not isinstance(number,bool): numbers.setdefault(number,[]).append(slug)
    collisions={str(n):sorted(slugs) for n,slugs in sorted(numbers.items()) if len(slugs)>1}
    for n,slugs in collisions.items(): errors.append('DUPLICATE_TOOL_NUMBER:'+n+':'+','.join(slugs))
    return {'schema':SCHEMA,'state':'DRAFT_HARD_HOLD' if not errors else 'INVALID_HARD_HOLD',
            'errors':sorted(set(errors)),'tool_count':len(observed),
            'source_blobs_verified':verified,'number_collisions':collisions,'tools':observed,
            'publication_authorized':False,'independent_qd_pass':False,
            'privacy_verified':False,'medical_safety_verified':False,
            'actual_41_wordpress_drafts_verified':False,'paid_offer_approved':False,
            'verified_paid_orders':None,'net_revenue_per_1000_qualified_sessions':None}


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2])
    args=ap.parse_args()
    result=audit(args.root)
    print(json.dumps(result,indent=2,sort_keys=True))
    return 1 if result['errors'] else 0


if __name__=='__main__':
    raise SystemExit(main())
