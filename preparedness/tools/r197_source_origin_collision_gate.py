#!/usr/bin/env python3
"""R197 read-only source-origin collision custody; NOT safety or release approval."""
from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib
import json
import re
import subprocess

SCHEMA = 'fv-preparedness-r197-origin-collision-custody-v1'
HOLD, INVALID = 'DRAFT_HARD_HOLD', 'INVALID_HARD_HOLD'
DOCKET = '05d393013a952d9d2c92a6e1d9759ca53579ae8b'
# base stays unchanged; historic clusters preserve both old and observed objects.
PINS = {
 'base': ('b25cd02b9beaadaf5a2db0c52e0ae66d20b1ac77', 'b25cd02b9beaadaf5a2db0c52e0ae66d20b1ac77', 34, 34),
 'hist-field': ('4f369122cc0e230ee39654c215f18ffc79b5cc85', '6b65e0aaa777b4c5ebc57fbeade0386b4ab6c32f', 26, 28),
 'hist-food': ('d10628342fea5f177a8d1be00dd906d0c9c7850e', 'c1856c998c6c728f0de72221e5654a238df994a9', 28, 28),
 'hist-home': ('6460d4b0734991675c889f28be2f73a19e3c42c0', '8d85fd868508c5caba14a839d119d55f31f14f72', 27, 29),
}
# The R194 7-article metadata positions, NOT inferred from a mutable request.
ARTICLES = (
 ('hist-field','navigation-before-gps','40c83419760bc7bd0c4c574304e65b773b4a8423','40c83419760bc7bd0c4c574304e65b773b4a8423'),
 ('hist-field','pioneer-supply-chains-failed','fcb42c440e3b7aad5eeecfd4e0c974a5d04a9cec','8789c77dcc2be717f09ce0fbd340a04319aaf223'),
 ('hist-food','pemmican-and-dried-meats','03d3824e07fe51931671d0ddc7aa8c85eda58435','c19f68f2ac0988a8d0959e2d05b8ace8f9511348'),
 ('hist-food','pioneer-travel-rations','7191acba55d63dc405ad9c2003d66193276da89f','521e56a3f18d8b211920529a88a3c3b86eb332d7'),
 ('hist-home','pickling-fermentation-old-recipes','4b955811459017df83a28704aaf1e69ddb036c29','da97f42fcabbd05dc513d26c6af289bbeb8816f3'),
 ('hist-home','root-cellars-cool-storage','705e1157f9394b615ecb74ffd25be8500453e18a','c3b7425711c3953c2d6cac9eb2aabe21a6717285'),
 ('hist-home','sanitation-before-germ-theory','0dad1731adc3c88aac65baceaa9aa09112e5eb5b','3294cd9fcf59496c9ece9342e67b0d57d2ed5523'),
)
EXPECTED = {
 'frozen': {'nchfp-home','nps-lewis-clark-salt','nps-salt-works','loc-pioneer-diaries','loc-prairie-traveler','nchfp-historical-origins'},
 'observed': {'nchfp-home','nchfp-jerky','nps-lewis-clark-salt','nps-salt-works','loc-pioneer-diaries','loc-prairie-traveler','nchfp-historical-origins'},
}
ID = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
class AdmissionError(ValueError): pass

def require(ok, why):
    if not ok: raise AdmissionError(why)

def oid(raw):
    return hashlib.sha1(b'blob '+str(len(raw)).encode('ascii')+b'\0'+raw).hexdigest()

def strict_json(raw):
    require(type(raw) is bytes and len(raw)<200_000, 'missing/oversized Git blob')
    def unique(pairs):
        d={}
        for k,v in pairs:
            require(k not in d,'duplicate JSON field')
            d[k]=v
        return d
    def nonstandard(v): raise AdmissionError('nonstandard JSON constant')
    return json.loads(raw.decode('utf-8'), object_pairs_hook=unique, parse_constant=nonstandard)

def read_oid(read_blob, sha):
    raw=read_blob(sha)
    require(type(raw) is bytes and oid(raw)==sha, 'substituted/missing Git object '+sha)
    return strict_json(raw)

def audit(read_blob, *, docket_oid=DOCKET, pins=PINS, articles=ARTICLES, expected=EXPECTED,
          check_real_census=True):
    result={'schema':SCHEMA,'issue':136,'coordination_issue':820,'state':INVALID,
      'publication_authorized':False,'independent_qd_pass':False,
      'human_source_approved':False,'medical_safety_verified':False,
      'merchant_offer_verified':False,'verified_paid_orders':None,'realized_net_revenue':None,
      'objects_checked':0,'versioned_source_rows':{},'same_id_conflicts':[],
      'article_origin_workorders':[],'errors':[]}
    try:
        docket=read_oid(read_blob,docket_oid);result['objects_checked']+=1
        require(docket.get('schema')=='fv-preparedness-r194-seven-delta-citation-custody-v1'
                and docket.get('state')==HOLD and docket.get('issue')==136,
                'docket schema/hold changed')
        for k in ('publication_authorized','independent_qd_pass','medical_safety_verified',
                  'source_claims_human_approved','merchant_offer_verified'):
            require(docket.get(k) is False,'forged docket approval '+k)
        require(type(docket.get('source_fragments')) is dict,
                'missing source roster')
        require(len(docket.get('articles',[]))==len(articles), 'article inventory changed')
        for group,sl,old,new in articles:
            rows=[r for r in docket['articles'] if r.get('cluster')==group and r.get('slug')==sl]
            require(len(rows)==1 and rows[0].get('human_source_review')=='PENDING'
                    and rows[0].get('qualified_safety_review')=='PENDING'
                    and rows[0].get('frozen',{}).get('meta_blob')==old
                    and rows[0].get('observed',{}).get('meta_blob')==new,
                    'missing/changed pinned article provenance '+sl)
        require(set(pins)=={'base','hist-field','hist-food','hist-home'},'origin roster drift')
        for origin in sorted(set(pins)-{'base'}):
            require(docket['source_fragments'].get(origin)==dict(zip(('frozen','observed'),pins[origin][:2])),
                    'changed historical fragment pin '+origin)
        versions={}
        for version,ix in (('frozen',0),('observed',1)):
            groups={};index=defaultdict(list);row_total=0
            for origin in sorted(pins):
                sha=pins[origin][ix];count=pins[origin][ix+2]
                obj=read_oid(read_blob,sha);result['objects_checked']+=1
                require(type(obj) is dict and type(obj.get('sources')) is list
                        and len(obj['sources'])==count,'source census changed '+origin)
                m={}
                for src in obj['sources']:
                    require(type(src) is dict and type(src.get('id')) is str
                            and ID.fullmatch(src['id']) and src['id'] not in m,
                            'duplicate/bad source ID in '+origin)
                    require(type(src.get('url')) is str and src['url'].startswith('https://')
                            and src.get('human_link_check') is False,
                            'unsafe or falsely approved source record '+src['id'])
                    require(all(type(src.get(k)) is str and src[k].strip() for k in ('title','publisher','supports')),
                            'missing title/publisher/claim support '+src['id'])
                    m[src['id']]=src
                    index[src['id']].append((origin,src))
                groups[origin]=m;row_total+=len(m)
            conflicts={sid:rows for sid,rows in index.items() if len(rows)>1}
            require(set(conflicts)==expected[version], 'shared-origin collision roster changed')
            result['versioned_source_rows'][version]=row_total
            for sid,rows in sorted(conflicts.items()):
                result['same_id_conflicts'].append({'version':version,'source_id':sid,
                 'provenance':[{'origin':origin,'record_sha256':hashlib.sha256(json.dumps(src,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),
                 'human_link_check':False} for origin,src in rows],
                 'differing_fields':sorted(k for k in set().union(*(r.keys() for _,r in rows))
                  if len({json.dumps(r.get(k),sort_keys=True) for _,r in rows})>1),
                 'automatic_collapse_allowed':False,'human_review':'PENDING'})
            versions[version]=(groups,index)
        if check_real_census:
            require(result['versioned_source_rows']=={'frozen':115,'observed':119},
                    'total base + historical fragment census changed')
        for group,slug,old,new in articles:
            for ver,sha in (('frozen',old),('observed',new)):
                meta=read_oid(read_blob,sha);result['objects_checked']+=1
                require(meta.get('slug')==slug and type(meta.get('source_use')) is dict
                        and meta.get('status',{}).get('publish')=='draft',
                        'article source_use/draft status drift '+slug)
                index=versions[ver][1]
                work=[]
                for sid,explanation in sorted(meta['source_use'].items()):
                    require(type(explanation) is str and explanation.strip() and sid in index,
                            'missing source provenance: '+slug+'/'+sid)
                    # Name every source origin. Never silently select a winner.
                    candidates=index[sid]
                    work.append({'source_id':sid,'source_origins':sorted(x[0] for x in candidates),
                       'ambiguous':len(candidates)>1,'human_review':'PENDING'})
                result['article_origin_workorders'].append({'cluster':group,'slug':slug,
                    'version':ver,'meta_blob':sha,'source_use_count':len(work),
                    'origins':work,'human_review':'PENDING'})
        result['state']=HOLD
    except (AdmissionError,KeyError,ValueError,TypeError,UnicodeError,OSError,
            subprocess.CalledProcessError,subprocess.TimeoutExpired) as exc:
        result['errors'].append(str(exc)[:400])
    return result

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo',default='.')
    p.add_argument('--report')
    args=p.parse_args(argv)
    def read(sha):
        return subprocess.run(['git','cat-file','blob',sha],cwd=args.repo,check=True,
            timeout=15,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout
    result=audit(read)
    output=json.dumps(result,sort_keys=True,indent=2,ensure_ascii=False)+'\n'
    if args.report:
        with open(args.report,'w',encoding='utf-8') as f:f.write(output)
    else:print(output,end='')
    return 2 if result['state']==HOLD else 3

if __name__=='__main__':raise SystemExit(main())
