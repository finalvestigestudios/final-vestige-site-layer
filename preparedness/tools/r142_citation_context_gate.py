#!/usr/bin/env python3
"""R142: fail-closed, read-only citation-to-passage drift review.

Given *both exact* R140 candidate and contributor article sets, compare the textual
contexts in which each literal author-scoped citation appears. Equal cite counts
are not evidence that source support is unchanged. A result is NEVER safety/QD or
publication approval; missing inputs are a HOLD, not a partial pass.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import re
import sys
import unicodedata

CITE = re.compile(r"\{\{cite:([a-z0-9]+(?:-[a-z0-9]+)*)\}\}")
ANY_CITE = re.compile(r"\{\{cite:([^}]+)\}\}")
LINK = re.compile(r"\{\{link:[^}]+\}\}")
BLOCKS = frozenset(('p','li','h1','h2','h3','h4','h5','h6','blockquote','td','th','dd','dt','figcaption','caption'))
RELEASE = 'DRAFT_HOLD_QUALIFIED_SOURCE_SAFETY_AND_QD_REVIEW_REQUIRED'


def canon(raw: str) -> str:
    without_cites = ANY_CITE.sub('', raw)
    without_links = LINK.sub('[internal link]', without_cites)
    return ' '.join(unicodedata.normalize('NFKC', without_links).casefold().split())


class PassageParser(HTMLParser):
    """Capture each citation with its immediate rendered text block, not page totals."""
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[dict] = []
        self.rows: list[dict] = []
        self.unscoped: list[str] = []
        self.blocks_seen = 0

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag in BLOCKS:
            self.stack.append({'tag':tag, 'parts':[], 'index':self.blocks_seen})
            self.blocks_seen += 1

    def handle_startendtag(self, tag: str, attrs: list) -> None:
        # Self-closing tags have no visible textual citation content.
        pass

    def handle_data(self, data: str) -> None:
        if self.stack:
            self.stack[-1]['parts'].append(data)
        elif ANY_CITE.search(data):
            self.unscoped.extend(ANY_CITE.findall(data))

    def handle_endtag(self, tag: str) -> None:
        if tag not in BLOCKS:
            return
        if not self.stack or self.stack[-1]['tag'] != tag:
            raise ValueError('unbalanced or overlapping citation-bearing HTML blocks')
        frame = self.stack.pop()
        raw = ''.join(frame['parts'])
        ids = ANY_CITE.findall(raw)
        if not ids:
            return
        text = canon(raw)
        if not text:
            raise ValueError('citation has no visible accompanying passage')
        digest = hashlib.sha256(text.encode('utf-8')).hexdigest()
        for sid in ids:
            if not CITE.fullmatch('{{cite:' + sid + '}}'):
                raise ValueError('malformed source citation identity')
            self.rows.append({'id':sid, 'context_sha256':digest,
                              'block_index':frame['index'], 'excerpt':text[:220]})


def contexts(raw: bytes) -> list[dict]:
    html = raw.decode('utf-8', 'strict')
    parser = PassageParser()
    parser.feed(html)
    parser.close()
    if parser.stack or parser.unscoped:
        raise ValueError('unclosed blocks or citation outside recognized reader-visible block')
    literal = Counter(ANY_CITE.findall(html))
    extracted = Counter(row['id'] for row in parser.rows)
    if extracted != literal:
        raise ValueError('citation token not captured in reader-visible blocks')
    return parser.rows


def compare_contexts(before: list[dict], after: list[dict]) -> dict:
    def index(rows: list[dict]):
        counts = Counter((r['id'], r['context_sha256']) for r in rows)
        examples = {(r['id'], r['context_sha256']):r for r in rows}
        return counts, examples
    a, a_examples = index(before)
    b, b_examples = index(after)
    lost = a - b
    added = b - a
    def serialize(delta, examples):
        return [{'source_id':sid, 'occurrences':count, 'context_sha256':hash_id,
                 'block_index':examples[(sid,hash_id)]['block_index'],
                 'excerpt':examples[(sid,hash_id)]['excerpt']}
                for (sid,hash_id),count in sorted(delta.items())]
    losses, gains = serialize(lost,a_examples),serialize(added,b_examples)
    return {'old_citation_occurrences':len(before), 'new_citation_occurrences':len(after),
            'lost_context_occurrences':sum(x['occurrences'] for x in losses),
            'added_context_occurrences':sum(x['occurrences'] for x in gains),
            'changed_source_ids':sorted({x['source_id'] for x in losses+gains}),
            'old_only':losses, 'new_only':gains, 'human_review':'UNREVIEWED_REQUIRED'}


def _load_parent(tool: Path):
    if not tool.is_file() or tool.is_symlink():
        raise ValueError('R141 custody tool absent or untrusted')
    spec = importlib.util.spec_from_file_location('r141_for_r142', tool)
    if not spec or not spec.loader:
        raise ValueError('cannot load R141 custody gate')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def run(manifest_path: Path, docket_path: Path, rc_root: Path,
        contributor_root: Path, *, parent_tool: Path) -> dict:
    parent = _load_parent(parent_tool)
    manifest_raw = manifest_path.read_bytes()
    manifest = json.loads(manifest_raw)
    docket = json.loads(docket_path.read_bytes())
    parent.validate_docket(manifest, manifest_raw, docket)
    rows = docket['article_deltas']
    # Both sides must be present and byte-for-byte match frozen Git content.
    parent.verify_files(rc_root, rows, version='rc')
    parent.verify_occurrences(rc_root, docket, manifest, version='rc')
    parent.verify_files(contributor_root, rows, version='contributor')
    parent.verify_occurrences(contributor_root, docket, manifest, version='contributor')
    results=[]
    for row in sorted(rows,key=lambda x:x['slug']):
        relative = Path('preparedness/content/articles')/(row['slug']+'.body.html')
        old = contexts((rc_root/relative).read_bytes())
        new = contexts((contributor_root/relative).read_bytes())
        item = compare_contexts(old,new)
        item.update({'slug':row['slug'],'cluster':row['cluster'],
                     'rc_blob':row['rc_blob'],'contributor_blob':row['contributor_blob']})
        results.append(item)
    return {'schema':'R142-CITATION-PASSAGE-DIFF-1',
            'release':RELEASE, 'qd':'NOT_APPROVED','safety':'UNREVIEWED_HUMAN_REQUIRED',
            'verified_exact_pairs':len(results),
            'lost_context_occurrences':sum(x['lost_context_occurrences'] for x in results),
            'added_context_occurrences':sum(x['added_context_occurrences'] for x in results),
            'articles':results}


def main(argv: list[str] | None=None) -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--manifest',type=Path,required=True)
    ap.add_argument('--docket',type=Path,required=True)
    ap.add_argument('--rc-root',type=Path,required=True)
    ap.add_argument('--contributor-root',type=Path,required=True)
    ap.add_argument('--r141-tool',type=Path,default=Path(__file__).with_name('r141_citation_delta_gate.py'))
    ap.add_argument('--report',type=Path,help='Optional local review JSON output, never approval or CMS write')
    args=ap.parse_args(argv)
    try:
        output=run(args.manifest,args.docket,args.rc_root,args.contributor_root,
                   parent_tool=args.r141_tool)
        code=0
    except (ValueError, TypeError, UnicodeError, OSError, KeyError, json.JSONDecodeError) as e:
        output={'schema':'R142-CITATION-PASSAGE-DIFF-1','release':RELEASE,
                'qd':'NOT_APPROVED','safety':'UNREVIEWED_HUMAN_REQUIRED',
                'verified_exact_pairs':0,'error':str(e)}
        code=2
    payload=json.dumps(output,ensure_ascii=False,indent=2,sort_keys=True)+'\n'
    if args.report:
        args.report.write_text(payload,encoding='utf-8')
    else:
        print(payload)
    return code


if __name__=='__main__':
    raise SystemExit(main())
