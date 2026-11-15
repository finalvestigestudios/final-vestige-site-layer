"""R386 | Preparedness original-manuscript -> WordPress/preview citation parity.

REVIEW-ONLY. This checks complete pairs of draft artifacts against *every*
original variant in an immutable R384 review packet. Matching a variant is
NOT choosing it, NOT validating the advice, and NOT a release/commerce gate.
The CLI obtains the packet from original SHA-checked git objects, never from a
user-provided JSON file or an untrusted source register. It is read-only.

Do not use this as medical/safety verification or as a WordPress publishing step.
"""
from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
ORIGINAL_MANIFEST_BLOB = '5e7d9a8972872c82b4bc46ac13aab18883d8149a'
SHA40 = re.compile(r'[a-f0-9]{40}\Z')
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
CITE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
CITE_SUP = re.compile(r'<sup\b[^>]*\bclass\s*=\s*["\'][^"\']*\bpa-cite\b[^"\']*["\'][^>]*>.*?</sup\s*>', re.I | re.S)
DISGUISED = re.compile(r'(?:display\s*:\s*none|visibility\s*:\s*hidden|opacity\s*:\s*0(?:\D|$)|font-size\s*:\s*0(?:\D|$)|clip-path\s*:\s*inset\s*\(\s*100%|left\s*:\s*-\d{3,}px)', re.I)
ALLOWED_EXTRA = re.compile(r'(?:landing|hub-[a-z0-9-]+|[a-z0-9-]+-tool)\Z')


def _load_r384():
    spec = importlib.util.spec_from_file_location('r384_for_render_parity', ROOT / 'r384_variant_review_packet.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def digest(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()


def attrs_dict(attrs):
    return dict(attrs)


def classes(attrs):
    return set((attrs_dict(attrs).get('class') or '').split())


class Subtree(HTMLParser):
    """Extract exactly one HTML subtree by tag+class without regex-div truncation."""
    VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
    def __init__(self, tag, class_name):
        super().__init__(convert_charrefs=False)
        self.tag, self.class_name = tag, class_name
        self.depth = 0
        self.found = 0
        self.parts = []
        self.root_attrs = None
        self.errors = []
    def handle_starttag(self, tag, attrs):
        if self.depth == 0 and tag == self.tag and self.class_name in classes(attrs):
            self.found += 1
            if self.found > 1: self.errors.append('DUPLICATE_SUBTREE')
            self.depth = 1
            self.root_attrs = attrs_dict(attrs)
            self.parts.append(self.get_starttag_text())
        elif self.depth:
            self.parts.append(self.get_starttag_text())
            if tag not in self.VOID: self.depth += 1
    def handle_startendtag(self, tag, attrs):
        if self.depth: self.parts.append(self.get_starttag_text())
    def handle_endtag(self, tag):
        if self.depth:
            self.parts.append(f'</{tag}>')
            self.depth -= 1
    def handle_data(self, data):
        if self.depth: self.parts.append(data)
    def handle_entityref(self, name):
        if self.depth: self.parts.append('&'+name+';')
    def handle_charref(self, name):
        if self.depth: self.parts.append('&#'+name+';')
    def handle_comment(self, data):
        if self.depth: self.parts.append('<!--'+data+'-->')
    def take(self, raw):
        self.feed(raw); self.close()
        if self.depth: self.errors.append('UNCLOSED_SUBTREE')
        if self.found != 1: self.errors.append('SUBTREE_COUNT_'+str(self.found))
        return ''.join(self.parts)


class Footnotes(HTMLParser):
    """Treat rendered citations and source anchors as visible DOM, not text hits."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.refs = []
        self.sources = {}
        self.errors = []
        self.capture_source = None
        self.suppress = False
    def handle_starttag(self, tag, attrs):
        a=attrs_dict(attrs); cs=classes(attrs)
        blocked=bool(a.get('hidden') is not None or a.get('aria-hidden') == 'true' or DISGUISED.search(a.get('style') or ''))
        blocked = blocked or (self.stack[-1][2] if self.stack else False)
        if tag in {'script','style','template','noscript'}: blocked=True
        self.stack.append((tag, a, blocked))
        if tag == 'sup' and 'pa-cite' in cs:
            self.refs.append({'n':None, 'blocked':blocked, 'anchors':0, 'text': '', 'href':None})
        if tag == 'li' and re.fullmatch(r'src-\d+', a.get('id','')):
            n = int(a['id'][4:])
            if n in self.sources: self.errors.append('DUPLICATE_SOURCE_ANCHOR:'+str(n))
            self.sources[n] = {'hrefs':[], 'blocked':blocked, 'text':''}
            self.capture_source = n
        if tag == 'a' and self.capture_source is not None:
            self.sources[self.capture_source]['hrefs'].append({'href':a.get('href'), 'rel':a.get('rel',''), 'blocked':blocked})
        if tag == 'a' and self.refs and any(t == 'sup' and 'pa-cite' in classes(tuple(d.items())) for t,d,_ in self.stack[:-1]):
            r=self.refs[-1];r['anchors']+=1;r['href']=a.get('href');r['blocked'] |= blocked
            r['aria']=a.get('aria-label','')
    def handle_endtag(self, tag):
        if self.stack:
            # malformed HTML yields a failed audit rather than an exception
            if self.stack[-1][0] != tag:
                self.errors.append('MALFORMED_HTML_CLOSE:'+tag)
                for pos in range(len(self.stack)-1,-1,-1):
                    if self.stack[pos][0] == tag:
                        self.stack=self.stack[:pos];break
            else: self.stack.pop()
        if tag == 'li': self.capture_source=None
    def handle_data(self, value):
        if self.capture_source is not None:
            self.sources[self.capture_source]['text']+=value
        if self.refs and any(tag == 'sup' and 'pa-cite' in (d.get('class') or '').split() for tag,d,_ in self.stack):
            self.refs[-1]['text']+=value
    def validate(self, unique_order: list[str], occurrence_order: list[str], expected_urls: dict[str,str] | None = None):
        numbers={sid:i+1 for i,sid in enumerate(unique_order)}
        expect=[numbers[sid] for sid in occurrence_order]
        seen=[]
        for i,ref in enumerate(self.refs):
            href=ref['href']
            num=int(href[5:]) if isinstance(href,str) and re.fullmatch(r'#src-[1-9]\d*',href) else None
            seen.append(num)
            if ref['anchors'] != 1 or num is None: self.errors.append('MALFORMED_CITATION:'+str(i+1))
            if ref['blocked']: self.errors.append('HIDDEN_CITATION:'+str(i+1))
            if ref['text'].strip() != f'[{num}]' or not re.fullmatch(r'Source '+re.escape(str(num))+r': \S.*', ref.get('aria','')):
                self.errors.append('CITATION_LABEL_MISMATCH:'+str(i+1))
        if seen != expect: self.errors.append('CITATION_OCCURRENCE_ORDER_MISMATCH')
        if set(self.sources) != set(range(1,len(unique_order)+1)):
            self.errors.append('SOURCE_ANCHOR_SET_MISMATCH')
        for n,row in sorted(self.sources.items()):
            anchors=row['hrefs']
            if row['blocked'] or not row['text'].strip(): self.errors.append('HIDDEN_OR_EMPTY_SOURCE:'+str(n))
            if len(anchors) != 1: self.errors.append('SOURCE_OUTBOUND_COUNT:'+str(n))
            else:
                u=anchors[0]['href'] or ''
                try: parts=urlsplit(u)
                except ValueError: parts=None
                if (not parts or parts.scheme!='https' or not parts.netloc or parts.username or parts.password or
                    u.lower().startswith(('javascript:', 'data:')) or anchors[0]['blocked']):
                    self.errors.append('UNSAFE_SOURCE_HREF:'+str(n))
                if 'noopener' not in anchors[0]['rel'].split():
                    self.errors.append('SOURCE_REL_MISSING:'+str(n))
                if expected_urls is None or n > len(unique_order) or expected_urls.get(unique_order[n-1]) != u:
                    self.errors.append('SOURCE_URL_NOT_ORIGINAL_ORIGIN:'+str(n))
        return sorted(set(self.errors))


def paragraph_hashes(raw_body):
    """Source words survive cite token rendering: strip only genuine footnote superscripts."""
    r384 = _load_r384()
    cleaned=CITE_SUP.sub('',raw_body)
    return [(p['tag'],p['prose_sha256'],p['words']) for p in r384.paragraphs(cleaned.encode('utf-8'))]


def variant_signature(variant):
    b=variant.get('blocks',[])
    return [(x['tag'],x['prose_sha256'],x['words']) for x in b]


def candidate_checks(variant, wp_article, wp_body, source_urls):
    expected = [sid for block in variant['blocks'] for sid in block['citations']]
    unique=list(dict.fromkeys(expected))
    out=[]
    actual=paragraph_hashes(wp_body)
    if actual != variant_signature(variant): out.append('ORIGINAL_PROSE_BLOCK_MISMATCH')
    notes=Footnotes();notes.feed(wp_article);notes.close()
    branch=variant.get('branch')
    expected_urls={}
    for sid in unique:
        url=(source_urls or {}).get(branch,{}).get(sid) or (source_urls or {}).get('BASE',{}).get(sid)
        if not url:out.append('SOURCE_ORIGIN_UNRESOLVED:'+sid)
        else:expected_urls[sid]=url
    out.extend(notes.validate(unique,expected,expected_urls))
    if variant.get('missing_reading_scopes'):
        out.append('ORIGINAL_READING_SCOPE_MISSING')
    return sorted(set(out))


def audit(packet:dict, wp_dir:Path, preview_dir:Path, *, source_urls:dict|None=None, original_enforcement=True) ->dict:
    """Never writes to either input directory; never returns publication approval."""
    problems=[]; rows=[]; canonical_seen={}
    if (not isinstance(packet,dict) or packet.get('status')!='REVIEW_PACKET_HARD_HOLD' or
        packet.get('publication_approved') is not False or packet.get('qualified_safety_approved') is not False):
        return {'status':'INVALID_HARD_HOLD','errors':['UNAUTHENTIC_OR_APPROVED_PACKET'], 'publication_approved':False}
    arts=packet.get('articles',[])
    if source_urls is None or not isinstance(source_urls,dict):problems.append('SOURCE_ORIGIN_REGISTRY_UNAVAILABLE')
    if not isinstance(arts,list) or (original_enforcement and len(arts)!=35) or (original_enforcement and len(packet.get('unselected_conflicts',[]))!=9):
        problems.append('ORIGINAL_ARTICLE_OR_FORK_INVENTORY_INVALID')
    names=[a.get('slug') for a in arts if isinstance(a,dict)]
    if len(names)!=len(set(names)) or any(not isinstance(x,str) or not SLUG.fullmatch(x) for x in names):
        problems.append('DUPLICATE_OR_INVALID_ORIGINAL_SLUG')
    wp_files={x.stem for x in wp_dir.glob('*.html')} if wp_dir.is_dir() else set()
    prev_files={x.stem for x in preview_dir.glob('*.html')} if preview_dir.is_dir() else set()
    if wp_files != prev_files: problems.append('WP_PREVIEW_FILE_SET_MISMATCH')
    if not set(names).issubset(wp_files & prev_files): problems.append('MISSING_ORIGINAL_ARTICLE_EXPORTS')
    if any(not ALLOWED_EXTRA.fullmatch(x) for x in (wp_files|prev_files)-set(names)):
        problems.append('UNRECOGNIZED_EXTRA_EXPORT')
    for article in arts:
        if not isinstance(article,dict):continue
        slug=article.get('slug')
        if not isinstance(slug,str) or not SLUG.fullmatch(slug) or slug not in wp_files or slug not in prev_files:continue
        try:
            wp_path,pr_path=wp_dir/(slug+'.html'),preview_dir/(slug+'.html')
            if wp_path.is_symlink() or pr_path.is_symlink():raise ValueError('SYMLINK_EXPORT')
            wp=wp_path.read_text(encoding='utf-8');pr=pr_path.read_text(encoding='utf-8')
            if len(wp)>3_000_000 or len(pr)>3_000_000:raise ValueError('OVERSIZED_EXPORT')
            w=Subtree('div','pa-article');w_article=w.take(wp)
            p=Subtree('div','pa-article');p_article=p.take(pr)
            b=Subtree('div','pa-body');wp_body=b.take(w_article)
            pb=Subtree('div','pa-body');pr_body=pb.take(p_article)
            issues=w.errors+p.errors+b.errors+pb.errors
            if w_article!=p_article or wp_body!=pr_body:issues.append('WP_PREVIEW_ARTICLE_BYTES_MISMATCH')
            if not wp.lstrip().startswith('<!-- wp:html -->') or not pr.lstrip().lower().startswith('<!doctype html>'):
                issues.append('EXPORT_WRAPPER_INVALID')
            if not re.search(r'<meta\s+name="robots"\s+content="noindex,nofollow"',pr,re.I):
                issues.append('PRIVATE_PREVIEW_ROBOTS_MISSING')
            if w.root_attrs.get('data-slug')!=slug or p.root_attrs.get('data-slug')!=slug:
                issues.append('ARTICLE_DATA_SLUG_MISMATCH')
            if 'Draft: not public' not in w_article or 'Independent safety/source and QD verification pending' not in w_article:
                issues.append('DRAFT_WARNING_ABSENT')
            if 'Human source/safety review and independent QD are still required before publication.' not in w_article and 'Human source/safety review and independent QD are required before publication.' not in w_article and 'Editorial source review and independent QD are still required before publication.' not in w_article:
                issues.append('INDEPENDENT_REVIEW_WARNING_ABSENT')
            if '{{cite:' in w_article or '{{link:' in w_article:issues.append('UNRESOLVED_BODY_TOKENS')
            # Source URL in JSON-LD carries the public target, but the FILE is still private.
            urls=re.findall(r'"mainEntityOfPage"\s*:\s*"([^"\\]+)"',w_article)
            if (len(urls)!=1 or not urls[0].startswith('https://finalvestige.com/preparedness/') or
                not urls[0].endswith('/'+slug+'/')):
                issues.append('CANONICAL_URL_INVALID')
            else:
                if urls[0] in canonical_seen:issues.append('DUPLICATE_CANONICAL_URL:'+canonical_seen[urls[0]])
                canonical_seen[urls[0]]=slug
            matching=[]; unsuccessful={}
            for v in article.get('variants',[]):
                if not isinstance(v,dict) or not SHA40.fullmatch(str(v.get('body_sha'))) or v.get('safety_state') not in {'pending','approved','not-required'}:
                    issues.append('INVALID_ORIGINAL_VARIANT');continue
                checks=candidate_checks(v,w_article,wp_body,source_urls)
                if not checks: matching.append({'branch':v['branch'],'body_sha':v['body_sha'],'meta_sha':v['meta_sha']})
                else: unsuccessful[v['branch']]=checks
            if not matching:
                issues.append('NO_MATCHING_ORIGINAL_VARIANT')
                for reason_list in unsuccessful.values(): issues.extend(reason_list)
            rows.append({'slug':slug,'wp_sha256':hashlib.sha256(wp.encode()).hexdigest(),
                         'preview_sha256':hashlib.sha256(pr.encode()).hexdigest(),
                         'matching_variant_candidates':sorted(matching,key=lambda x:x['branch']),
                         'candidate_mismatches':unsuccessful,'errors':sorted(set(issues))})
            problems.extend(f'{slug}:{e}' for e in sorted(set(issues)))
        except (OSError,UnicodeError,ValueError,TypeError,KeyError) as exc:
            problems.append(slug+':EXPORT_READ_OR_PARSE_ERROR:'+type(exc).__name__)
    return {'schema':1,'status':'INVALID_HARD_HOLD' if problems else 'RENDER_PARITY_REVIEW_HARD_HOLD',
            'release_state':'DRAFT_HARD_HOLD','publication_approved':False,'qualified_safety_approved':False,
            'merchant_offer_verified':False,'live_release_allowed':False,
            'counts':{'original_articles':len(arts),'matched_exports':len(rows),'candidate_matches':sum(len(r['matching_variant_candidates']) for r in rows),
                      'nonarticle_exports_needing_independent_review':len((wp_files|prev_files)-set(names)),
                      'unselected_original_forks':len(packet.get('unselected_conflicts',[]))},
            'errors':sorted(set(problems)),'articles':rows, 'report_sha256':digest(rows)}


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo',default='.')
    ap.add_argument('--wp',default='preparedness/build/wp')
    ap.add_argument('--preview',default='preparedness/build/preview')
    args=ap.parse_args(argv)
    try:
        r384=_load_r384()
        def reader(sha):
            p=subprocess.run(['git','-C',args.repo,'cat-file','blob',sha],capture_output=True,check=True,timeout=20)
            if r384.blob_sha(p.stdout)!=sha:raise ValueError('OBJECT_HASH_MISMATCH')
            return p.stdout
        original=json.loads(reader(ORIGINAL_MANIFEST_BLOB))
        sources=json.loads(reader('24b49f0a423119c2f612455f021669709a3f22b5'))
        base=json.loads(reader('b25cd02b9beaadaf5a2db0c52e0ae66d20b1ac77'))
        r375_spec=importlib.util.spec_from_file_location('r375_for_render_parity',ROOT/'r375_source_collision_integrity_gate.py')
        r375=importlib.util.module_from_spec(r375_spec);r375_spec.loader.exec_module(r375)
        check=r375.check_crosswalk(original,sources)
        if check['status']!='SOURCE_REVIEW_HARD_HOLD':raise ValueError('ORIGINAL_SOURCE_CROSSWALK_CUSTODY_FAILED')
        packet=r384.build_packet(original,reader)
        by_origin={}
        for record in base['sources']:
            sid,url=record['id'],record['url']
            if sid in by_origin.setdefault('BASE',{}):raise ValueError('DUPLICATE_BASE_SOURCE')
            by_origin['BASE'][sid]=url
        for group in sources['source_id_variants']:
            for v in group['variants']:
                branch,sid,url=v['branch'],v['id'],v['url']
                if sid in by_origin.setdefault(branch,{}):raise ValueError('DUPLICATE_BRANCH_SOURCE')
                by_origin[branch][sid]=url
        result=audit(packet,Path(args.wp),Path(args.preview),source_urls=by_origin)
    except (OSError,ValueError,UnicodeError,TypeError,subprocess.SubprocessError,json.JSONDecodeError) as exc:
        result={'status':'INVALID_HARD_HOLD','release_state':'DRAFT_HARD_HOLD',
                'publication_approved':False,'qualified_safety_approved':False,
                'errors':['AUTHENTIC_INPUT_UNAVAILABLE:'+type(exc).__name__]}
    print(json.dumps(result,indent=2,sort_keys=True))
    return 2  # even a complete, matched private pair is not QD approval


if __name__=='__main__':raise SystemExit(main())