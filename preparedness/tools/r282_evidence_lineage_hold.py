#!/usr/bin/env python3
"""R282: three-way historical evidence custody. DRAFT/HARD HOLD, never approval.

Compares authenticated R200 originals, R276 integrated inventory and the older
article-evidence lock, which is a *different historical snapshot*. Both source
origins and manuscript blob lineages must remain visible to human reviewers.
"""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path

HOLD = 'DRAFT_HARD_HOLD'
INVALID = 'INVALID_HARD_HOLD'
PINS = {
 'audits/r200_seven_cluster_35_article_frozen_custody.json': '5822f9dfde21d1f3bdfc26658769d852c639438c',
 'audits/r276_all_slate_identity_UNAPPROVED.json': 'b8c7c6df0dca62b04b01abc5671b7083ad9cb61e',
 'sources/article-evidence-lock.json': '2dc41fccad6f1272f0a9d9585b6c10c760dcb08c',
 'audits/r282_three_way_evidence_lineage_UNAPPROVED.json': '410226ffc7dcbcc65ad356055a81d9bef4e91eb2',
}
HOLD_FLAGS = ('publication_authorized','may_merge','independent_qd_pass','medical_safety_verified','privacy_approved','commercial_offer_approved')
SHA = re.compile(r'^[0-9a-f]{40}$')

def require(ok, reason):
    if not ok: raise ValueError(reason)

def blob(raw):
    return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()

def strict_json(raw):
    def unique(pairs):
        d={}
        for k,v in pairs:
            if k in d: raise ValueError('duplicate JSON key: '+k)
            d[k]=v
        return d
    return json.loads(raw.decode('utf-8'),object_pairs_hook=unique,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite JSON')))

def read_pinned(root, rel, sha):
    root=Path(root)
    require(root.is_dir() and not root.is_symlink(),'unsafe root')
    p=root
    for segment in rel.split('/'):
        require(segment not in ('','.','..'),'unsafe path')
        p=p/segment
        require(not p.is_symlink(),'symlinked custody input: '+rel)
    require(p.is_file(),'missing custody input: '+rel)
    raw=p.read_bytes()
    require(blob(raw)==sha,'Git identity mismatch: '+rel)
    return strict_json(raw)

def lineage(original, integrated, historical):
    if original==integrated==historical: return 'all_equal'
    if original==integrated: return 'original_integrated_equal'
    if original==historical: return 'original_lock_equal'
    if integrated==historical: return 'integrated_lock_equal'
    return 'all_distinct'

def derive(o,i,l):
    require(o.get('artifact_count')==35 and i.get('schema')=='fv-r276-all-slate-identity-v1','35-article baseline lost')
    require(o.get('state')==i.get('state')==HOLD,'source hold drift')
    require(i.get('source_review')=={'shared_url_groups':32,'duplicate_id_groups':15,'held_occurrences':3},'citation hold drift')
    arts=o.get('articles'); records=l.get('records'); inventory=i.get('entries')
    require(type(arts) is list and len(arts)==35 and type(records) is list and len(records)==36 and type(inventory) is list and len(inventory)==96,'census mismatch')
    require(l.get('longform_article_count')==35 and l.get('local_tool_count')==1,'historical lock counts')
    known={x['path']:x for x in inventory}
    require(len(known)==96,'duplicate integrated path')
    lock_articles=[x for x in records if x['body']['path'].startswith('preparedness/content/articles/')]
    lock_tools=[x for x in records if x['body']['path'].startswith('preparedness/content/tools/')]
    require(len(lock_articles)==35 and len(lock_tools)==1 and lock_tools[0]['slug']=='water-planner','historical lock tool/roster')
    locks={x['slug']:x for x in lock_articles}
    require(len(locks)==35 and {x['slug'] for x in arts}==set(locks),'historical lock slugs')
    require(len({x['slug'] for x in arts})==len({x['route'] for x in arts})==35,'duplicate article URL')
    require({x['n'] for x in arts}==set(range(1,36)),'article numbers missing')
    rows=[]
    for a in arts:
        slug=a['slug']; lock=locks[slug]
        require(a['route']==f'/preparedness/{slug}/','canonical route mismatch')
        b=known[f'content/articles/{slug}.body.html']; m=known[f'content/articles/{slug}.meta.json']
        require(b['role']=='article_body' and m['role']=='article_meta','wrong integrated role')
        require(lock['body']['path']==f'preparedness/content/articles/{slug}.body.html' and lock['metadata']['path']==f'preparedness/content/articles/{slug}.meta.json','historical lock path mismatch')
        def part(oid,size,current,historic):
            ids=(oid,current['sha'],historic['git_blob_sha'])
            require(all(type(x) is str and SHA.fullmatch(x) for x in ids),'invalid source object ID')
            require(all(type(x) is int and x>0 for x in (size,current['size'],historic['bytes'])),'source byte length invalid')
            relation=lineage(*ids)
            return dict(r200_blob=oid,r200_bytes=size,integrated_blob=current['sha'],integrated_bytes=current['size'],evidence_lock_blob=historic['git_blob_sha'],evidence_lock_bytes=historic['bytes'],lineage=relation,review_required=relation!='all_equal')
        body=part(a['body_oid'],a['body_bytes'],b,lock['body'])
        meta=part(a['meta_oid'],a['meta_bytes'],m,lock['metadata'])
        different=a['source_cluster']!=lock['origin']
        rows.append(dict(n=a['n'],slug=slug,original_cluster=a['source_cluster'],evidence_lock_origin=lock['origin'],origin_differs=different,route=a['route'],body=body,metadata=meta,human_review_required=body['review_required'] or meta['review_required'] or different))
    rows.sort(key=lambda x:x['n'])
    count=lambda fn:sum(bool(fn(x)) for x in rows)
    stats={'articles':35,'integrated_articles':35,'original_lock_tool_count':1,
      'source_origin_differences':count(lambda x:x['origin_differs']),
      'r200_integrated_article_differences':count(lambda x:x['body']['r200_blob']!=x['body']['integrated_blob'] or x['metadata']['r200_blob']!=x['metadata']['integrated_blob']),
      'r200_lock_article_differences':count(lambda x:x['body']['r200_blob']!=x['body']['evidence_lock_blob'] or x['metadata']['r200_blob']!=x['metadata']['evidence_lock_blob']),
      'lock_integrated_article_differences':count(lambda x:x['body']['integrated_blob']!=x['body']['evidence_lock_blob'] or x['metadata']['integrated_blob']!=x['metadata']['evidence_lock_blob']),
      'r200_integrated_body_changes':count(lambda x:x['body']['r200_blob']!=x['body']['integrated_blob']),
      'r200_integrated_metadata_changes':count(lambda x:x['metadata']['r200_blob']!=x['metadata']['integrated_blob']),
      'r200_lock_body_changes':count(lambda x:x['body']['r200_blob']!=x['body']['evidence_lock_blob']),
      'r200_lock_meta_changes':count(lambda x:x['metadata']['r200_blob']!=x['metadata']['evidence_lock_blob']),
      'review_required_articles':count(lambda x:x['human_review_required'])}
    for part in ('body','metadata'):
        frequencies={}
        for row in rows:
            key=row[part]['lineage'];frequencies[key]=frequencies.get(key,0)+1
        stats[part+'_lineage']=frequencies
    require((stats['source_origin_differences'],stats['r200_integrated_article_differences'],stats['r200_integrated_body_changes'],stats['r200_integrated_metadata_changes'])==(6,17,14,12),'unreviewed historical difference census')
    return {'schema':'fv-preparedness-r282-three-way-historical-evidence-lineage-unapproved-v1','state':HOLD,'issue':136,'conversion_issue':820,
      'original_pin':PINS['audits/r200_seven_cluster_35_article_frozen_custody.json'],
      'integrated_pin':PINS['audits/r276_all_slate_identity_UNAPPROVED.json'],
      'historical_lock_pin':PINS['sources/article-evidence-lock.json'],
      'authority':'MECHANICAL_GIT_OBJECT_COMPARISON_NOT_HUMAN_SOURCE_ADJUDICATION',
      **{f:False for f in HOLD_FLAGS},
      'source_review':{'shared_url_groups':32,'duplicate_id_groups':15,'held_occurrences':3},
      'unresolved_editorial':{'changed_article_substantive_review_required':17,'shorter_body_article_numbers':[24,25,27,32,33,34],
        'article_7_contamination_review_required':True,'article_15_tool_104_privacy_review_required':True},
      'aggregates':stats,
      'historical_lock_extra_tool':{'slug':lock_tools[0]['slug'],'origin':lock_tools[0]['origin'],'body':lock_tools[0]['body'],'metadata':lock_tools[0]['metadata'],'not_an_authorized_offer':True},
      'articles':rows}

def audit(root):
    try:
        data=[read_pinned(root,path,sha) for path,sha in PINS.items()]
        expected=derive(*data[:3]);require(expected==data[3],'three-way review docket differs from authentic source objects')
        require(all(data[3].get(k) is False for k in HOLD_FLAGS),'approval state mutated')
        return {'state':HOLD,'three_way_review_mechanical_only':True,'articles':35,'requires_human_review':True,
                'publication_authorized':False,'independent_qd_pass':False,'review_required_articles':expected['aggregates']['review_required_articles']}
    except (OSError,KeyError,IndexError,TypeError,ValueError,UnicodeError,AttributeError) as exc:
        return {'state':INVALID,'three_way_review_mechanical_only':False,'publication_authorized':False,
                'independent_qd_pass':False,'errors':[str(exc)]}

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',required=True,type=Path)
    print(json.dumps(audit(p.parse_args().root),indent=2,sort_keys=True))
    raise SystemExit(2)  # Even mechanically authentic sources are NOT release-approved.
