#!/usr/bin/env python3
"""Read-only R150 tool source-origin migration impact gate for Issue #136.

Every citation occurrence is accounted for. This DOES NOT apply crosswalk changes,
verify URLs, approve medical/safety guidance, build public pages or grant QD PASS.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re

SCHEMA = 'FV-PREP-R150-ORIGIN-SHADOW-1'
R149_SCHEMA = 'FV-PREP-R149-TOOL-CLAIM-CUSTODY-1'
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
BASELINE = {'missing': 58, 'scope_change': 4, 'unchanged': 5,
            'occ_missing': 142, 'occ_scope_change': 15, 'occ_unchanged': 16,
            'source_rows': 67, 'citations': 173}
CHANGED_PAIRS = {('home-fire-escape-worksheet', 'usfa-fire-escape'),
                 ('kit-builder', 'ready-are-you-ready'),
                 ('power-outage-planner', 'fsis-power-failure'),
                 ('reunification-plan', 'ready-are-you-ready')}
ORIGIN_FILES = {'base': 'sources/register.json',
                'start': 'sources/fragments/start.json',
                'shelter': 'sources/fragments/shelter.json'}

class Hold(ValueError):
    """Non-publishable source evidence mismatch or an unadjudicated source risk."""

def check(ok, message):
    if not ok:
        raise Hold(message)

def fingerprint(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False,
                                     separators=(',', ':')).encode('utf-8')).hexdigest()

def git_blob(raw):
    return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\x00'+raw).hexdigest()

def load_custodied(root: Path, path: str, expected_sha: str):
    check(isinstance(path,str) and not path.startswith('/') and '..' not in Path(path).parts,
          'invalid relative custody path')
    p=root/path
    check(p.is_file() and not p.is_symlink(), 'missing or linked evidence '+path)
    raw=p.read_bytes()
    check(git_blob(raw)==expected_sha, 'evidence blob drift: '+path)
    return json.loads(raw.decode('utf-8'))

def index_sources(source_registers):
    indexed={}
    for origin, data in source_registers.items():
        check(origin in ORIGIN_FILES and isinstance(data.get('sources'),list), 'unknown origin/register')
        rows={}
        for rec in data['sources']:
            sid=rec.get('id') if isinstance(rec,dict) else None
            check(isinstance(sid,str) and SLUG.fullmatch(sid) and sid not in rows,
                  'invalid/duplicate source identity in '+origin)
            check(isinstance(rec.get('url'),str) and rec['url'].startswith('https://'),
                  'missing HTTPS source URL')
            rows[sid]=rec
        indexed[origin]=rows
    check(set(indexed)==set(ORIGIN_FILES), 'missing original source register')
    return indexed

def lookup(index, origin, sid):
    check(origin in index, 'unknown origin '+str(origin))
    if sid in index[origin]:
        return origin,index[origin][sid]
    if sid in index['base']:
        return 'base',index['base'][sid]
    return None,None

def analyze(docket, source_registers, *, strict_baseline=True):
    check(docket.get('schema')==R149_SCHEMA and
          docket.get('status')=='CANDIDATE_ONLY_HUMAN_SOURCE_REVIEW_REQUIRED' and
          docket.get('publication_allowed') is False and
          docket.get('source_scope_human_review')=='PENDING' and
          docket.get('independent_qd')=='NOT_APPROVED', 'R149 review is not in pending HOLD state')
    candidate=docket.get('candidate_tool_origins')
    check(isinstance(candidate,dict) and len(candidate)==6 and
          set(candidate.values())<=set(ORIGIN_FILES), 'candidate origins malformed')
    summaries=docket.get('tool_summaries')
    check(isinstance(summaries,list) and len(summaries)==6 and
          {s.get('tool') for s in summaries}==set(candidate), 'tool inventory drift')
    summary={s['tool']:s for s in summaries}
    index=index_sources(source_registers)
    rows=docket.get('source_use_rows')
    check(isinstance(rows,list) and rows and len(rows)==docket.get('source_use_row_count'),
          'missing author-specific source rows')
    result=[]; seen=set(); totals={k:0 for k in BASELINE}
    scopes=set()
    for row in rows:
        tool,sid=row.get('tool'),row.get('source_id')
        check(isinstance(tool,str) and tool in candidate and isinstance(sid,str) and
              SLUG.fullmatch(sid) and (tool,sid) not in seen, 'invalid/duplicated tool claim')
        seen.add((tool,sid))
        s=summary[tool]
        check(row.get('current_origin')==s['current_origin'] and
              row.get('candidate_origin')==candidate[tool]==s['candidate_origin'],
              'tool origin does not match pinned author reading')
        check(row.get('review_decision')=='PENDING' and row.get('reviewer') is None and
              row.get('human_source_scope_adjudicated') is False and
              row.get('medical_safety_approved') is False, 'source reviewer approval must not be forged')
        occurs=row.get('citation_occurrences')
        check(type(occurs) is int and occurs>0, 'invalid source citation count')
        old_origin,old=lookup(index,row['current_origin'],sid)
        new_origin,new=lookup(index,candidate[tool],sid)
        check(new is not None, f'unresolved candidate citation {tool}/{sid}')
        check(row.get('currently_resolvable')==(old is not None), 'R149 original resolution mismatch')
        check(row.get('effective_source_origin')==new_origin and
              row.get('literal_url')==new.get('url') and
              row.get('source_supports')==new.get('supports') and
              row.get('publisher')==new.get('publisher'), 'source identity/support drift')
        check(isinstance(row.get('author_specific_use'),str) and row['author_specific_use'].strip(),
              'author interpretation missing')
        check(new['url'].startswith('https://') and row.get('human_link_check_recorded') is False,
              'source link review state changed without adjudication')
        if old is None:
            state='missing'; delta=['NOT_RESOLVABLE_BEFORE']
        else:
            check(old['url']==new['url'], f'URL changed under same citation ID {tool}/{sid}')
            delta=sorted(k for k in set(old)|set(new) if old.get(k)!=new.get(k))
            state='scope_change' if delta else 'unchanged'
        totals[state]+=1; totals['occ_'+state]+=occurs
        if state=='scope_change':scopes.add((tool,sid))
        result.append({'tool':tool,'source_id':sid,'citation_occurrences':occurs,
                       'impact':state,'before_origin':old_origin,'after_origin':new_origin,
                       'before_source_sha256':fingerprint(old) if old else None,
                       'after_source_sha256':fingerprint(new),'changed_source_fields':delta,
                       'url':new['url'], 'requires_human_source_scope_review': True})
    for tool,s in summary.items():
        tool_rows=[r for r in result if r['tool']==tool]
        check(len(tool_rows)==s['unique_cited_sources'] and
              sum(r['citation_occurrences'] for r in tool_rows)==s['citation_occurrences'] and
              {r['source_id'] for r in tool_rows if r['impact']=='missing'}==
              set(s['currently_unresolved_source_ids']), 'per-tool occurrence inventory drift')
    totals['source_rows']=len(result)
    totals['citations']=sum(r['citation_occurrences'] for r in result)
    if strict_baseline:
        check(totals==BASELINE, f'new source impact requires adjudication: {totals}')
        check(scopes==CHANGED_PAIRS, 'unexpected changed source reading scope')
    return {'schema':SCHEMA,'state':'DRAFT_HOLD_UNREVIEWED',
            'source_migration_proposed_only':True,'source_crosswalk_modified':False,
            'totals':totals,'source_scope_changes':[{'tool':a,'source_id':b}
                for a,b in sorted(scopes)], 'rows':result,
            'human_source_scope_review':'PENDING','independent_qd':'NOT_APPROVED',
            'medical_safety_approved':False,'publish_allowed':False,
            'commercial_offer_verified':False,'paid_orders_verified':False}

def run(root:Path,docket_path:Path):
    doc=json.loads(docket_path.read_text(encoding='utf-8'))
    check(doc.get('schema')==R149_SCHEMA, 'wrong R149 docket')
    pinned=doc.get('immutable_git_blob_sha1')
    check(isinstance(pinned,dict) and len(pinned)==16, 'missing 16-file R149 custody inventory')
    for path,sha in pinned.items():
        load_custodied(root,path,sha)
    sources={origin:load_custodied(root,path,pinned[path])
             for origin,path in ORIGIN_FILES.items()}
    return analyze(doc,sources)

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--preparedness',default='preparedness')
    p.add_argument('--docket',default='preparedness/docs/r149/tool-source-use-review-docket.json')
    p.add_argument('--report',help='optional offline reviewer report file; never writes CMS or source crosswalk')
    args=p.parse_args(argv)
    try:
        result=run(Path(args.preparedness),Path(args.docket))
        if args.report:
            dest=Path(args.report)
            check('preparedness/sources' not in str(dest).replace('\\','/'), 'cannot write over source register')
            check(dest.suffix=='.json' and not dest.is_symlink(), 'unsafe report destination')
            dest.parent.mkdir(parents=True,exist_ok=True)
            dest.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
        else:
            # Short fail-closed machine summary; full 67-row report is opt-in.
            result={k:v for k,v in result.items() if k!='rows'}
        print(json.dumps(result,indent=2,sort_keys=True))
    except (Hold,KeyError,TypeError,ValueError,OSError,UnicodeError,json.JSONDecodeError) as exc:
        print(json.dumps({'schema':SCHEMA,'state':'HOLD','error':str(exc),
                          'publish_allowed':False,'independent_qd':'NOT_APPROVED'},sort_keys=True))
    return 2  # never grant release, even when the evidence and expected impact are identical

if __name__=='__main__':
    raise SystemExit(main())
