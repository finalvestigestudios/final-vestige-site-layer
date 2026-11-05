#!/usr/bin/env python3
"""R148: detect Preparedness tool author-origin gaps without changing source records.

This is a fail-closed review diagnostic. It NEVER changes crosswalk.json,
grants source/safety/QD approval, builds drafts, or authorizes publication.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re

CITE = re.compile(r"\{\{cite:([a-z0-9]+(?:-[a-z0-9]+)*)\}\}")

class Hold(ValueError):
    pass

def need(ok, msg):
    if not ok: raise Hold(msg)

def readj(p):
    need(p.is_file() and not p.is_symlink(), f"source missing/linked: {p}")
    obj = json.loads(p.read_text(encoding='utf-8', errors='strict'))
    need(isinstance(obj, dict), f"expected JSON object: {p}")
    return obj

def collect(root):
    """Keep origin/id/URL triples rather than merging same-URL source scopes."""
    files = [("base", root / "sources/register.json")]
    files += [(f.stem, f) for f in sorted((root / "sources/fragments").glob('*.json'))]
    need(len(files) >= 2, "no source fragments available")
    variants = {}
    for origin, f in files:
        rows = readj(f).get("sources")
        need(isinstance(rows, list), f"missing source rows: {origin}")
        for row in rows:
            need(isinstance(row, dict), "invalid source row")
            sid, url = row.get('id'), row.get('url')
            need(isinstance(sid, str) and sid and isinstance(url, str) and url,
                 f"invalid source identity: {origin}")
            key = (origin, sid)
            need(key not in variants, f"duplicate origin/id: {origin}/{sid}")
            variants[key] = url
    # The active renderer requires one literal URL for every repeated source ID.
    # The author-specific reading scope still remains separate by origin.
    urls = {}
    for (origin, sid), url in variants.items():
        urls.setdefault(sid, set()).add(url)
    need(all(len(s) == 1 for s in urls.values()),
         "conflicting literal URL per source ID: manual adjudication required")
    return variants

def possible_origins(ids, variants):
    choices = sorted({origin for origin, _ in variants})
    return [origin for origin in choices if all((origin, sid) in variants or ('base',sid) in variants for sid in ids)]

def diagnose_tool(slug, cites, source_use, configured_origin, variants):
    need(isinstance(source_use, dict) and source_use and all(isinstance(v,str) and v.strip() for v in source_use.values()),
         f"{slug}: absent author-specific source-use interpretation")
    need(cites and set(cites) == set(source_use), f"{slug}: body citation/source_use key mismatch")
    ids = sorted(set(cites))
    unresolved = [sid for sid in ids if (configured_origin, sid) not in variants and ('base',sid) not in variants]
    options = possible_origins(ids, variants)
    safe_suggestion = options[0] if len(options) == 1 else None
    return {"slug":slug, "configured_origin":configured_origin, "unresolved_source_ids":unresolved,
            "candidate_origins":options, "unique_candidate":safe_suggestion,
            "requires_human_review":bool(unresolved), "article_or_source_mutation_performed":False,
            "publication_allowed":False}

def inspect(root, *, tool_count=6, article_count=35):
    root = Path(root).resolve(strict=True)
    crosswalk = readj(root / 'sources/crosswalk.json')
    origins = crosswalk.get('article_origins')
    need(isinstance(origins,dict), "missing author-origin crosswalk")
    variants = collect(root)
    article_meta = sorted((root/'content/articles').glob('*.meta.json'))
    tool_meta = sorted((root/'content/tools').glob('*.meta.json'))
    need(len(article_meta)==article_count and len(tool_meta)==tool_count,
         "original article/tool inventory changed")
    report = []
    for p in tool_meta:
        meta = readj(p)
        slug = p.name.removesuffix('.meta.json')
        need(meta.get('slug')==slug and meta.get('status',{}).get('publish')=='draft',
             f"{slug}: slug/publication state drift")
        body = p.with_name(slug+'.body.html')
        need(body.is_file() and not body.is_symlink(), f"{slug}: missing body")
        html = body.read_text(encoding='utf-8',errors='strict')
        cites = CITE.findall(html)
        need(html.count('{{cite:')==len(cites), f"{slug}: malformed citations")
        entry = diagnose_tool(slug, cites, meta.get('source_use'), origins.get(slug,'base'), variants)
        report.append(entry)
    blockers = [r for r in report if r['unresolved_source_ids']]
    ambiguity = [r for r in blockers if r['unique_candidate'] is None]
    return {"schema":"FV-PREP-R148-TOOL-ORIGIN-1", "status":"DRAFT_HOLD_SOURCE_ORIGIN_DIAGNOSTIC",
            "tool_count":len(report), "unresolved_tool_count":len(blockers),
            "unresolved_source_use_identifiers":sum(len(r['unresolved_source_ids']) for r in blockers),
            "ambiguous_tool_count":len(ambiguity), "tools":report,
            "source_crosswalk_modified":False, "article_corpus_modified":False,
            "publication_allowed":False, "independent_qd":"NOT_APPROVED",
            "medical_safety_verified":False, "merchant_offer_verified":False}

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--preparedness',type=Path,default=Path('preparedness'))
    args=p.parse_args(argv)
    out={'schema':'FV-PREP-R148-TOOL-ORIGIN-1','status':'HOLD',
         'publication_allowed':False,'independent_qd':'NOT_APPROVED'}
    try:
        out.update(inspect(args.preparedness))
        # A correct diagnostic that finds currently broken render paths should
        # NOT return 0, so CI cannot mistake a report for build readiness.
        code = 2 if out['unresolved_tool_count'] else 0
    except (Hold,ValueError,TypeError,OSError,UnicodeError) as e:
        out['error'],code=str(e),2
    print(json.dumps(out,indent=2,sort_keys=True))
    return code

if __name__=='__main__':
    raise SystemExit(main())
