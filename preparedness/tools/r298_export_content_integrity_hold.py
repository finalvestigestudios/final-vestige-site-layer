#!/usr/bin/env python3
"""Review-only, fail-closed article export/citation/read-depth inventory guard.

Reads local WordPress DRAFT outputs, *never* writes to the website. It cannot
approve source meaning, medical advice, privacy, a sale, publishing, or QD.
Requires custody receipt, complete local build and separate six-tool receipt.
"""
from __future__ import annotations
import argparse
import hashlib
from html.parser import HTMLParser
import json
import re
import unicodedata
from pathlib import Path

CUSTODY = 'preparedness/audits/r200_seven_cluster_35_article_frozen_custody.json'
CUSTODY_OID = '5822f9dfde21d1f3bdfc26658769d852c639438c'
SITE = 'https://finalvestige.com'
PATTERN = re.compile(r'\{\{(?:cite|link|inline-js):[^}]+\}\}')
TOKEN = re.compile(r"[a-z0-9]+(?:['’][a-z0-9]+)?", re.I)


def blob_oid(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


class Narrative(HTMLParser):
    def __init__(self, target=False):
        super().__init__(convert_charrefs=True)
        self.target, self.depth, self.suppressed = target, 0, []
        self.parts = []

    def handle_starttag(self, tag, attrs):
        void = tag in ('area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr')
        if self.depth and not void:
            self.depth += 1
        elif self.target and tag == 'div' and ('class', 'pa-body') in attrs:
            self.depth = 1
        if tag in ('style', 'script', 'noscript') or (tag=='sup' and ('class','pa-cite') in attrs):
            self.suppressed.append(tag)

    def handle_endtag(self, tag):
        if self.depth:
            self.depth -= 1
        if tag in self.suppressed:
            self.suppressed.remove(tag)

    def handle_data(self, data):
        if not self.suppressed and (not self.target or self.depth):
            self.parts.append(data)


def words(html: str, *, target=False) -> list[str]:
    parser = Narrative(target=target)
    parser.feed(PATTERN.sub(' ', html))
    return TOKEN.findall(unicodedata.normalize('NFKC', ' '.join(parser.parts)).casefold())


def window_coverage(source: list[str], rendered: list[str], *, width=9) -> float:
    """Count exact source word windows preserved in output; not a semantic check."""
    if not source:
        return 0.0
    width = min(width, len(source))
    originals = [tuple(source[i:i+width]) for i in range(len(source)-width+1)]
    observed = set(tuple(rendered[i:i+width]) for i in range(max(0, len(rendered)-width+1)))
    return sum(w in observed for w in originals) / len(originals)


def inspect(custody: dict, report: dict, originals: dict[str, bytes],
            wp: dict[str, bytes], tool_receipt: dict | None) -> dict:
    errors, detail = [], []
    def fail(code):
        errors.append(code)
    articles = custody.get('articles', [])
    if custody.get('state') != 'DRAFT_HARD_HOLD' or any(custody.get(k) is not False for k in
         ('publication_authorized','independent_qd_pass','human_source_approved','medical_safety_verified')):
        fail('CUSTODY_RELEASE_STATE_INVALID')
    if (custody.get('artifact_count'),custody.get('export_target_count_with_six_tools')) != (35,41):
        fail('CUSTODY_COUNT_INVALID')
    if len(articles) != 35 or sorted(a.get('n') for a in articles) != list(range(1,36)):
        fail('CUSTODY_ARTICLE_INVENTORY_INVALID')
    slugs = [a.get('slug') for a in articles]
    routes = [a.get('route') for a in articles]
    if len(set(slugs)) != 35 or len(set(routes)) != 35:
        fail('DUPLICATE_CUSTODY_SLUG_OR_URL')
    built = report.get('articles', [])
    if len(built) != 41 or len({a.get('slug') for a in built}) != 41:
        fail('BUILD_REPORT_INVENTORY_INVALID')
    by_slug = {a.get('slug'):a for a in built if isinstance(a,dict)}
    if not set(slugs).issubset(by_slug) or len(set(by_slug)-set(slugs)) != 6:
        fail('BUILD_REPORT_SLUG_SET_DRIFT')
    tool_slugs = set(by_slug)-set(slugs)
    ev = report.get('release_evidence', {})
    if ev.get('independent_qa_verified') is not False or ev.get('wordpress_publication_performed') is not False:
        fail('BUILD_REPORT_RELEASE_STATE_INVALID')
    if ev.get('state') not in ('HOLD','REQUIRES_INDEPENDENT_QA'):
        fail('BUILD_REPORT_RELEASE_STATE_UNKNOWN')
    for a in articles:
        slug,section = a.get('slug'),a.get('section')
        if not isinstance(slug,str) or not re.fullmatch('[a-z0-9-]+',slug):
            fail('INVALID_SLUG:'+str(slug)); continue
        want = '/preparedness/'+str(section)+'/'+slug+'/'
        if a.get('route') != want:
            fail('CUSTODY_ROUTE_DRIFT:'+slug)
        entry = by_slug.get(slug)
        if not entry:
            fail('MISSING_BUILD_ENTRY:'+slug);continue
        if entry.get('canonical') != SITE+want:
            fail('CANONICAL_DRIFT:'+slug)
        body_path = 'preparedness/content/articles/'+slug+'.body.html'
        html_path = 'preparedness/build/wp/'+slug+'.html'
        raw, output = originals.get(body_path),wp.get(html_path)
        if raw is None or output is None:
            fail('MISSING_SOURCE_OR_WP_DRAFT:'+slug);continue
        if not isinstance(raw,bytes) or not isinstance(output,bytes):
            fail('INVALID_SOURCE_OR_DRAFT_TYPE:'+slug);continue
        if blob_oid(raw) != a.get('body_oid'):
            fail('CHANGED_ORIGINAL_BODY:'+slug)
        if len(raw) < int(a.get('body_bytes') or 0):
            fail('ORIGINAL_BODY_TRUNCATED:'+slug)
        try:
            src,doc=raw.decode('utf-8'),output.decode('utf-8')
        except UnicodeError:
            fail('INVALID_UTF8:'+slug);continue
        if not doc.startswith('<!-- wp:html -->\n') or not doc.rstrip().endswith('<!-- /wp:html -->'):
            fail('WORDPRESS_DRAFT_WRAPPER:'+slug)
        if f'data-slug="{slug}"' not in doc:
            fail('DRAFT_WRONG_ARTICLE:'+slug)
        if 'Independent safety/source and QD verification pending' not in doc:
            fail('DRAFT_REVIEW_WARNING_MISSING:'+slug)
        srcw,docw=words(src),words(doc,target=True)
        coverage=window_coverage(srcw,docw)
        # Boundary anchors catch short introduction/conclusion deletions that a
        # global 94%-coverage score can otherwise conceal.
        windows = set(tuple(docw[i:i+16]) for i in range(max(0,len(docw)-15)))
        edges = len(srcw)>=16 and tuple(srcw[:16]) in windows and tuple(srcw[-16:]) in windows
        if len(srcw)<120 or len(docw)<120 or coverage < 0.94 or not edges:
            fail('READING_DEPTH_OR_PASSAGE_LOSS:'+slug)
        detail.append({'slug':slug,'source_words':len(srcw),'draft_body_words':len(docw),
                       'unchanged_word_window_fraction':round(coverage,5),
                       'original_oid_matches':blob_oid(raw)==a.get('body_oid')})
    # The native builder registers both content/articles and content/tools in
    # lib.articles and exports BOTH through build_article(): 35 + 6 = 41.
    # A tool receipt must attest actual bytes, not just assert a file hash exists.
    if not isinstance(tool_receipt, dict):
        fail('SIX_TOOL_EXPORT_RECEIPT_MISSING')
    else:
        tools = tool_receipt.get('tools', [])
        tool_ids = [t.get('slug') for t in tools if isinstance(t, dict)]
        if len(tools) != 6 or len(set(tool_ids)) != 6 or set(tool_ids) != tool_slugs:
            fail('SIX_TOOL_INVENTORY_INVALID')
        for t in tools:
            if not isinstance(t, dict):
                fail('SIX_TOOL_RELEASE_WITNESS_INVALID'); continue
            slug=t.get('slug')
            if not isinstance(slug,str) or not re.fullmatch('[a-z0-9-]+',slug):
                fail('SIX_TOOL_SLUG_INVALID'); continue
            srcpath=f'preparedness/content/tools/{slug}.body.html'
            metapath=f'preparedness/content/tools/{slug}.meta.json'
            wppath=f'preparedness/build/wp/{slug}.html'
            raw, metaraw, output=originals.get(srcpath),originals.get(metapath),wp.get(wppath)
            if not all(isinstance(x,bytes) for x in (raw,metaraw,output)):
                fail('SIX_TOOL_SOURCE_OR_EXPORT_MISSING:'+slug);continue
            if blob_oid(raw) != t.get('body_oid') or blob_oid(metaraw) != t.get('meta_oid'):
                fail('SIX_TOOL_SOURCE_CUSTODY_MISMATCH:'+slug)
            if hashlib.sha256(output).hexdigest() != t.get('file_sha256'):
                fail('SIX_TOOL_EXPORT_HASH_MISMATCH:'+slug)
            if t.get('status')!='draft' or t.get('review_only') is not True:
                fail('SIX_TOOL_RELEASE_WITNESS_INVALID:'+slug)
            try:
                meta=json.loads(metaraw)
                body=raw.decode('utf-8')
                doc=output.decode('utf-8')
            except (ValueError,UnicodeError):
                fail('SIX_TOOL_PARSE_ERROR:'+slug);continue
            if meta.get('slug')!=slug or meta.get('status',{}).get('publish')!='draft' or meta.get('kind') not in ('tool',None):
                fail('SIX_TOOL_META_IDENTITY_OR_RELEASE_DRIFT:'+slug)
            route=SITE+'/preparedness/'+str(meta.get('section'))+'/'+slug+'/'
            if by_slug.get(slug,{}).get('canonical')!=route or route in (SITE+r for r in routes):
                fail('SIX_TOOL_CANONICAL_COLLISION:'+slug)
            if not doc.startswith('<!-- wp:html -->\n') or not doc.rstrip().endswith('<!-- /wp:html -->'):
                fail('SIX_TOOL_WORDPRESS_WRAPPER:'+slug)
            if f'data-slug="{slug}"' not in doc or 'Independent safety/source and QD verification pending' not in doc:
                fail('SIX_TOOL_REVIEW_LABEL_MISSING:'+slug)
            srcw,docw=words(body),words(doc,target=True)
            if len(srcw)<25 or window_coverage(srcw,docw)<.90:
                fail('SIX_TOOL_READING_DEPTH_LOSS:'+slug)
    return {'schema':'fv-preparedness-r298-export-content-integrity-v1',
            'state':'INVALID_HARD_HOLD' if errors else 'DRAFT_HARD_HOLD',
            'errors':sorted(set(errors)),'article_entries_reviewed':len(detail),
            'article_evidence':detail,
            'all_41_exports_verified':False,'publication_authorized':False,
            'independent_qd_pass':False,'medical_safety_verified':False,
            'merchant_approved':False,'net_revenue_verified':False}


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[2])
    ap.add_argument('--tool-receipt',type=Path)
    ns=ap.parse_args(argv)
    root=ns.repo_root
    custody_raw=(root/CUSTODY).read_bytes() if (root/CUSTODY).is_file() else b''
    if blob_oid(custody_raw)!=CUSTODY_OID:
        print(json.dumps({'state':'INVALID_HARD_HOLD','errors':['R200_CUSTODY_BLOB_INVALID']}))
        return 1
    try:
        custody=json.loads(custody_raw)
        report=json.loads((root/'preparedness/build/build-report.json').read_text())
        tools=json.loads(ns.tool_receipt.read_text()) if ns.tool_receipt else None
        originals={};wp={}
        for a in custody['articles']:
            slug=a['slug']
            for dest,p in ((originals,f'preparedness/content/articles/{slug}.body.html'),
                           (wp,f'preparedness/build/wp/{slug}.html')):
                if (root/p).is_file(): dest[p]=(root/p).read_bytes()
        if tools:
            for t in tools.get('tools',[]):
                slug=t.get('slug','')
                if not re.fullmatch('[a-z0-9-]+',slug): continue
                for dest,p in ((originals,f'preparedness/content/tools/{slug}.body.html'),
                               (originals,f'preparedness/content/tools/{slug}.meta.json'),
                               (wp,f'preparedness/build/wp/{slug}.html')):
                    if (root/p).is_file(): dest[p]=(root/p).read_bytes()
        result=inspect(custody,report,originals,wp,tools)
    except (OSError,ValueError,KeyError,TypeError) as e:
        result={'state':'INVALID_HARD_HOLD','errors':['MISSING_OR_INVALID_INPUT:'+type(e).__name__]}
    print(json.dumps(result,sort_keys=True,indent=2))
    return 2 if result['state']=='DRAFT_HARD_HOLD' else 1

if __name__=='__main__':raise SystemExit(main())
