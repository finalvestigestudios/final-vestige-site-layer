#!/usr/bin/env python3
"""R122: read-only HOLD gate for reader-visible citation evidence in 35 articles.

An accurate Git blob, a matching token count and author-scoped source_use do not
prove the citation is actually visible to a reader. Count independently in HTML
text nodes and reject tokens in comments, attributes, scripts or hidden regions.
Does not replace R121, human source checks, qualified safety review or QD.
"""
from __future__ import annotations
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import sys

SCHEMA = 'fv-preparedness-r117-nine-snapshot-article-source-git-custody-HOLD-v1'
OID = re.compile(r'[0-9a-f]{40}\Z')
CITE = re.compile(r'\{\{cite:([a-z0-9]+(?:-[a-z0-9]+)*)\}\}')
INVISIBLE = {'script','style','template','noscript','iframe','svg','canvas'}
VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
CLASS_HIDDEN = {'sr-only','screen-reader-text','visually-hidden','u-screen-reader-text'}

class Hold(ValueError):
    """Missing or invalid source custody: never approve publication."""

def need(cond, code):
    if not cond:
        raise Hold(code)

def oid_bytes(value):
    return hashlib.sha1(b'blob ' + str(len(value)).encode('ascii') + b'\0' + value).hexdigest()

def no_duplicate_json(data):
    def unique(pairs):
        value = {}
        for k, v in pairs:
            need(k not in value, 'DUPLICATE_JSON_KEY')
            value[k] = v
        return value
    return json.loads(data, object_pairs_hook=unique)

class VisibleCitationParser(HTMLParser):
    """Conservatively identify citations that can appear as normal visible text."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.visible = []
    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        sty = re.sub(r'\s+', '', (values.get('style') or '').lower())
        classes = set((values.get('class') or '').lower().split())
        hidden = (tag in INVISIBLE or 'hidden' in values or
                  (values.get('aria-hidden') or '').strip().lower() == 'true' or
                  'display:none' in sty or 'visibility:hidden' in sty or
                  bool(classes & CLASS_HIDDEN))
        if tag not in VOID:
            self.stack.append((tag, hidden))
    def handle_startendtag(self, tag, attrs):
        pass
    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                return
    def handle_data(self, data):
        if not any(hidden for _, hidden in self.stack):
            self.visible.extend(CITE.findall(data))

def check_body(body, slug):
    raw = CITE.findall(body)
    need(body.count('{{cite:') == len(raw), 'MALFORMED_CITATION:' + slug)
    parser = VisibleCitationParser()
    parser.feed(body)
    parser.close()
    return {'raw':raw, 'visible':parser.visible,
            'concealed':raw != parser.visible}

def audit(snapshot, fetch_bytes):
    need(type(snapshot) is dict and snapshot.get('schema') == SCHEMA, 'INVALID_SNAPSHOT')
    need(snapshot.get('issue') == 136 and snapshot.get('business_issue') == 820, 'WRONG_ISSUE')
    g = snapshot.get('governance', {})
    need(g.get('release_state') == 'HOLD', 'NOT_HOLD')
    for flag in ('may_publish','may_merge','independent_QD_PASS','medical_safety_verified','merchant_offer_verified'):
        need(g.get(flag) is False, 'UNAUTHORIZED_GOVERNANCE_UPGRADE:' + flag)
    heads = snapshot.get('snapshots')
    need(type(heads) is list and len(heads) == 9, 'NINE_HEADS_REQUIRED')
    before, after, *contributors = heads
    need([s.get('role') for s in heads] == ['baseline','candidate'] + ['contributor'] * 7,
         'INVALID_HEAD_ROLES')
    need(len({h.get('cluster') for h in contributors}) == 7, 'INVALID_CLUSTER_ROSTER')
    for h in heads:
        need(type(h.get('sha')) is str and OID.fullmatch(h['sha']) is not None, 'BAD_HEAD_SHA')
    b, a = before.get('article_files'), after.get('article_files')
    need(type(b) is dict and type(a) is dict and set(a) == set(b), 'ARTICLE_ROSTER_CHANGED')
    slugs = sorted(path[:-10] for path in b if path.endswith('.body.html'))
    need(len(slugs) == len(set(slugs)) == 35 and
         set(b) == {slug + ext for slug in slugs for ext in ('.body.html','.meta.json')},
         'NOT_35_PAIRED_ARTICLES')
    cache = {}
    rows = []
    for slug in slugs:
        status = {}
        for version, head in (('original', b), ('candidate', a)):
            oid = head[slug + '.body.html']
            need(type(oid) is str and OID.fullmatch(oid) is not None, 'INVALID_OBJECT_ID')
            if oid not in cache:
                raw = fetch_bytes(oid)
                need(type(raw) is bytes and oid_bytes(raw) == oid, 'GIT_OBJECT_MISMATCH:' + slug)
                try:
                    cache[oid] = raw.decode('utf-8')
                except UnicodeDecodeError as ex:
                    raise Hold('NON_UTF8_BLOB:' + slug) from ex
            status[version] = check_body(cache[oid], slug)
        if status['original']['concealed'] or status['candidate']['concealed']:
            rows.append({'slug':slug,'original_raw':len(status['original']['raw']),
                         'original_visible':len(status['original']['visible']),
                         'candidate_raw':len(status['candidate']['raw']),
                         'candidate_visible':len(status['candidate']['visible']),
                         'code':'CITATION_NOT_VISIBLE_TO_READER','review':'UNREVIEWED'})
    return {'state':'HOLD','release_authorized':False,'QD_PASS':False,
            'medical_safety_verified':False, 'issue':136,'business_issue':820,
            'articles_checked':len(slugs),'distinct_git_body_objects_read':len(cache),
            'citation_visibility_blockers':rows,
            'note':'Static citation visibility only. Print CSS, actual browser, source accuracy, and safety remain unverified.'}

def git_fetch(repo):
    def read(oid):
        need(type(oid) is str and OID.fullmatch(oid) is not None, 'INVALID_OBJECT_ID')
        p = subprocess.run(['git','-C',str(repo),'cat-file','blob',oid],
                           stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                           timeout=20,check=False)
        need(p.returncode == 0, 'GIT_BLOB_UNAVAILABLE:' + oid)
        return p.stdout
    return read

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo',required=True,type=Path)
    p.add_argument('--snapshots',required=True,type=Path)
    x=p.parse_args(argv)
    try:
        snap=no_duplicate_json(x.snapshots.read_text(encoding='utf-8'))
        result=audit(snap,git_fetch(x.repo))
        print(json.dumps(result,sort_keys=True,indent=2))
        return 2 if result['citation_visibility_blockers'] else 0
    except (Hold, OSError, ValueError, subprocess.SubprocessError) as exc:
        print('HOLD: '+str(exc),file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
