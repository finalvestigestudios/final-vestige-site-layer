#!/usr/bin/env python3
"""R121: fail-closed, read-only Git-blob/article-scoped citation custody audit.

Runs over the R117 frozen 35-article nine-head snapshot and both R120 context
parts. The actual bytes are fetched from local *immutable Git blobs*, never
working-tree content, WordPress, a production site or the network. R120's
manifest validates its own algebra; this gate independently recomputes the
citation occurrences from both historical bodies, reconciles each article's
source_use justifications, and guards unpublished safety-review state.

A clean structural audit is STILL NOT a qualified safety review or QD PASS.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
import re
import subprocess
import sys

OID = re.compile(r"[a-f0-9]{40}\Z")
CITE = re.compile(r"\{\{cite:([a-z0-9]+(?:-[a-z0-9]+)*)\}\}")
CITE_LIKE = re.compile(r"\{\{cite:[^}]*\}\}")

class Hold(ValueError):
    """Cannot establish evidence identity, provenance, safety state or scope."""

def require(ok: bool, message: str) -> None:
    if not ok:
        raise Hold(message)

def strict_json(text: str):
    def unique(pairs):
        value = {}
        for key, item in pairs:
            require(key not in value, 'DUPLICATE_JSON_KEY:' + key)
            value[key] = item
        return value
    return json.loads(text, object_pairs_hook=unique)

def load(path: Path):
    return strict_json(Path(path).read_text(encoding='utf-8'))

def oid_bytes(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()

def git_reader(repo: Path):
    """Read immutable blobs from a checkout; no writes, remote access or shell."""
    repo = Path(repo)
    def read(oid):
        require(type(oid) is str and OID.fullmatch(oid) is not None, 'INVALID_BLOB_OID')
        proc = subprocess.run(['git', '-C', str(repo), 'cat-file', 'blob', oid],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              timeout=15, check=False)
        require(proc.returncode == 0, 'GIT_BLOB_UNAVAILABLE:' + oid)
        return proc.stdout
    return read

class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hidden = 0
        self.tokens = []
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'template'):
            self.hidden += 1
    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'template') and self.hidden:
            self.hidden -= 1
    def handle_data(self, data):
        if not self.hidden:
            self.tokens.append(data)

def visible_words(body: str) -> int:
    p = VisibleText()
    p.feed(CITE.sub('', body))
    return len(re.findall(r"\b[\w]+(?:['’][\w]+)?\b", ' '.join(p.tokens)))

def body_cites(body: str, slug: str):
    legitimate = CITE.findall(body)
    require(len(legitimate) == len(CITE_LIKE.findall(body)), 'MALFORMED_CITATION:' + slug)
    return legitimate

def audit(snapshot: dict, parts: list, get_blob, *, depth_floor=0.85) -> dict:
    """Return a reviewer-only HOLD report. Raise on forged or incomplete data.

    get_blob must return exact raw bytes for an immutable Git SHA1 object.
    Structural issues in citation/source_use/safety are collected as blockers.
    """
    require(0.0 < depth_floor <= 1.0, 'INVALID_DEPTH_FLOOR')
    require(snapshot.get('schema') == 'fv-preparedness-r117-nine-snapshot-article-source-git-custody-HOLD-v1', 'INVALID_SNAPSHOT_SCHEMA')
    require(snapshot.get('issue') == 136 and snapshot.get('business_issue') == 820, 'ISSUE_MISMATCH')
    gov = snapshot.get('governance', {})
    require(gov.get('release_state') == 'HOLD', 'MISSING_RELEASE_HOLD')
    for k in ('independent_QD_PASS', 'medical_safety_verified', 'merchant_offer_verified', 'may_merge', 'may_publish'):
        require(gov.get(k) is False, 'ILLEGAL_RELEASE_UPGRADE:' + k)
    heads = snapshot.get('snapshots')
    require(type(heads) is list and len(heads) == 9, 'NINE_HEADS_REQUIRED')
    baseline, candidate, *contributors = heads
    require([h.get('role') for h in heads] == ['baseline', 'candidate'] + ['contributor']*7, 'HEAD_ROLES_MISMATCH')
    require(len({h.get('cluster') for h in contributors}) == 7, 'SEVEN_CLUSTERS_REQUIRED')
    for h in heads:
        require(type(h.get('sha')) is str and OID.fullmatch(h['sha']) is not None, 'BAD_HEAD_SHA')
    before, after = baseline.get('article_files'), candidate.get('article_files')
    require(type(before) is dict and type(after) is dict and set(before) == set(after), 'ROSTER_CHANGED')
    bodies = sorted(k for k in before if k.endswith('.body.html'))
    slugs = [s[:-len('.body.html')] for s in bodies]
    require(len(slugs) == len(set(slugs)) == 35 and
            set(before) == {s+e for s in slugs for e in ('.body.html','.meta.json')},
            'NOT_35_ARTICLE_METADATA_PAIRS')
    require(type(parts) is list and len(parts) == 2, 'TWO_PARTS_REQUIRED')
    part_rows = {}
    for part in parts:
        require(part.get('schema') == 'r120-partial-citation-context-HOLD-v1', 'BAD_CONTEXT_SCHEMA')
        require(part.get('issue') == 136 and part.get('base_sha') == baseline['sha'] and
                part.get('candidate_sha') == candidate['sha'], 'STALE_CONTEXT_HEAD')
        require(type(part.get('rows')) is list and part['rows'], 'EMPTY_CONTEXT_PART')
        for row in part['rows']:
            slug = row.get('slug')
            require(type(slug) is str and slug not in part_rows and slug in slugs, 'DUPLICATE_OR_UNKNOWN_CONTEXT_SLUG')
            require(row.get('approval') == 'UNREVIEWED', 'ILLEGAL_HUMAN_APPROVAL:' + slug)
            part_rows[slug] = row
    changed = {s for s in slugs if before[s+'.body.html'] != after[s+'.body.html']}
    require(set(part_rows) == changed, 'MISSING_CHANGED_BODY_CONTEXT')

    cache = {}
    def fetch(oid):
        require(type(oid) is str and OID.fullmatch(oid) is not None, 'INVALID_BLOB_OID')
        if oid not in cache:
            raw = get_blob(oid)
            require(type(raw) is bytes and oid_bytes(raw) == oid, 'GIT_BLOB_IDENTITY_MISMATCH:' + oid)
            try:
                cache[oid] = raw.decode('utf-8')
            except UnicodeError as exc:
                raise Hold('NON_UTF8_GIT_OBJECT:' + oid) from exc
        return cache[oid]

    blockers = []
    review_rows = []
    original_total = candidate_total = 0
    for slug in slugs:
        cites = {}
        meta = {}
        words = {}
        for version, tree in (('before', before), ('after', after)):
            body = fetch(tree[slug+'.body.html'])
            metadata = strict_json(fetch(tree[slug+'.meta.json']))
            require(type(metadata) is dict and metadata.get('slug') == slug, 'META_SLUG_MISMATCH:' + slug)
            require(type(metadata.get('source_use')) is dict, 'SOURCE_USE_NOT_OBJECT:' + slug)
            require(type(metadata.get('status')) is dict and metadata['status'].get('publish') == 'draft', 'UNAUTHORIZED_PUBLISH_STATE:' + slug)
            safety = metadata.get('safety_review')
            require(type(safety) is dict and type(safety.get('state')) is str, 'MISSING_SAFETY_STATE:' + slug)
            cited = body_cites(body, slug)
            source_use = metadata['source_use']
            for key in sorted(set(cited)):
                if key not in source_use or type(source_use.get(key)) is not str or not source_use[key].strip():
                    blockers.append({'slug': slug, 'version': version, 'code': 'MISSING_AUTHOR_SCOPED_SOURCE_USE', 'source_id': key})
            cites[version] = cited
            meta[version] = metadata
            words[version] = visible_words(body)
            if version == 'before': original_total += len(cited)
            else: candidate_total += len(cited)
        if meta['before']['safety_review']['state'] != meta['after']['safety_review']['state']:
            blockers.append({'slug':slug,'code':'SAFETY_REVIEW_STATE_CHANGED',
                             'before':meta['before']['safety_review']['state'],
                             'after':meta['after']['safety_review']['state']})
        if words['after'] < depth_floor * max(1, words['before']):
            blockers.append({'slug':slug,'code':'READING_DEPTH_REDUCTION',
                             'before':words['before'],'after':words['after']})
        if slug in changed:
            row=part_rows[slug]
            require(row.get('before_git_blob') == before[slug+'.body.html'] and
                    row.get('after_git_blob') == after[slug+'.body.html'], 'CONTEXT_BLOB_MISMATCH:' + slug)
            require(row.get('before_citation_count') == len(cites['before']) and
                    row.get('after_citation_count') == len(cites['after']), 'CITATION_COUNT_DRIFT:' + slug)
            for k in ('before_word_count','after_word_count'):
                require(type(row.get(k)) is int and row[k] > 0, 'BAD_MANIFEST_READING_DEPTH:' + slug)
            require(row['after_word_count'] >= depth_floor * row['before_word_count'], 'MANIFEST_DEPTH_LOSS:' + slug)
            old, new = Counter(cites['before']), Counter(cites['after'])
            actual = [{'source_id':k,'before':old[k],'after':new[k]}
                      for k in sorted(set(old)|set(new)) if old[k] != new[k]]
            require(actual == row.get('occurrence_changes'), 'SOURCE_OCCURRENCE_CROSSWALK_DRIFT:' + slug)
            require((cites['before'] != cites['after']) is row.get('citation_sequence_changed'),
                    'CITATION_SEQUENCE_DRIFT:' + slug)
            for ex in row.get('context_examples', []):
                key=ex.get('citation','')
                require(type(key) is str and re.fullmatch(r'[a-z0-9-]+#[1-9][0-9]*',key) is not None,
                        'INVALID_EXAMPLE_CITATION_KEY:' + slug)
                sid, ix = key.rsplit('#',1)
                if old[sid] < int(ix) or new[sid] < int(ix):
                    blockers.append({'slug':slug,'code':'EXAMPLE_KEY_OUT_OF_RANGE','citation':key})
        review_rows.append({'slug':slug,'changed_body':slug in changed,
                            'before_git_blob':before[slug+'.body.html'],
                            'after_git_blob':after[slug+'.body.html'],
                            'before_citations':len(cites['before']),
                            'after_citations':len(cites['after']),
                            'before_visible_words':words['before'],
                            'after_visible_words':words['after'],
                            'review_state':'UNREVIEWED' if slug in changed else 'NOT_IN_THIS_DELTA'})
    return {'state':'HOLD','issue':136,'business_issue':820,
            'release_authorized':False,'QD_PASS':False,'medical_safety_verified':False,
            'article_count':len(slugs),'changed_body_count':len(changed),
            'source_occurrences_original':original_total,
            'source_occurrences_candidate':candidate_total,
            'source_occurrence_delta':candidate_total-original_total,
            'distinct_git_objects_read':len(cache),
            'blockers':sorted(blockers,key=lambda x:(x['slug'],x['code'],x.get('source_id',''))),
            'review_rows':review_rows,
            'note':'Git-object and author-scoped citation structure only; no human factual or medical approval.'}

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo',type=Path,required=True)
    p.add_argument('--snapshots',type=Path,required=True)
    p.add_argument('--part-a',type=Path,required=True)
    p.add_argument('--part-b',type=Path,required=True)
    a=p.parse_args(argv)
    try:
        report=audit(load(a.snapshots),[load(a.part_a),load(a.part_b)],git_reader(a.repo))
        print(json.dumps(report,indent=2,sort_keys=True))
        return 2 if report['blockers'] else 0  # Still HOLD even on exit 0.
    except (OSError,ValueError,KeyError,TypeError,subprocess.TimeoutExpired) as exc:
        print('HOLD: '+str(exc),file=sys.stderr)
        return 2

if __name__=='__main__':
    sys.exit(main())
