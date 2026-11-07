#!/usr/bin/env python3
"""R195 read-only, pinned, two-version claim/citation impact preflight.

Never merges source versions, aliases identifiers, certifies safety, authorizes
publication, or infers sales. A structural pass is DRAFT_HARD_HOLD (exit 2).
"""
from __future__ import annotations
import argparse
from collections import Counter
import difflib
import hashlib
import html
import json
from pathlib import Path
import re
import subprocess

SCHEMA = 'fv-preparedness-r195-claim-impact-review-v1'
R194_SCHEMA = 'fv-preparedness-r194-seven-delta-citation-custody-v1'
PINNED_DOCKET_BLOB = '05d393013a952d9d2c92a6e1d9759ca53579ae8b'
HOLD = 'DRAFT_HARD_HOLD'
INVALID = 'INVALID_HARD_HOLD'
CITE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
WORDS = re.compile(r"[A-Za-z0-9][A-Za-z0-9'’\-]*")
# Literal, reviewed custody pins from R194: old and new are NOT interchangeable.
# Each entry: cluster, slug, old_body, old_meta, old_count, new_body, new_meta, new_count.
PINS = (
 ('hist-field','navigation-before-gps','64c6b2c7004bc5549eea5a47d9095183e7436750','40c83419760bc7bd0c4c574304e65b773b4a8423',47,'49beb68339a6b85b07d686c0cfb9fe1d88b8de4f','40c83419760bc7bd0c4c574304e65b773b4a8423',47),
 ('hist-field','pioneer-supply-chains-failed','1332df3540a903fdecdb3527fb22347d57968fb0','fcb42c440e3b7aad5eeecfd4e0c974a5d04a9cec',57,'3643c50b43ca7ba6c1d9bc439e7c78730503b80f','8789c77dcc2be717f09ce0fbd340a04319aaf223',63),
 ('hist-food','pemmican-and-dried-meats','0b3319cc85ea2bc6d069b46d13a40e12ddbd5bc5','03d3824e07fe51931671d0ddc7aa8c85eda58435',46,'1febc8929f8b90c81a3fcef1e46a2811778b7e06','c19f68f2ac0988a8d0959e2d05b8ace8f9511348',46),
 ('hist-food','pioneer-travel-rations','058c90b763d8cd6dec0731a7b0a9cee4dd5a57c7','7191acba55d63dc405ad9c2003d66193276da89f',39,'a658481d828dc4c5ba85f296adbfbee0514f0611','521e56a3f18d8b211920529a88a3c3b86eb332d7',39),
 ('hist-home','pickling-fermentation-old-recipes','17f5da8a998e6b9b38695a2ef6716c6f336f31c4','4b955811459017df83a28704aaf1e69ddb036c29',42,'1869e37626b7463da45763d60202bd5ac0bd7700','da97f42fcabbd05dc513d26c6af289bbeb8816f3',49),
 ('hist-home','root-cellars-cool-storage','e28548b4e5014f36ffd12becb9261ae696480efa','705e1157f9394b615ecb74ffd25be8500453e18a',37,'7f375c32d74f2828b4912f5692abc44483e4629a','c3b7425711c3953c2d6cac9eb2aabe21a6717285',42),
 ('hist-home','sanitation-before-germ-theory','15852c158708270d72d5f9723d90e5cb6083a766','0dad1731adc3c88aac65baceaa9aa09112e5eb5b',47,'02090fc1b773fd79f08a7ba754b6125844c37eab','3294cd9fcf59496c9ece9342e67b0d57d2ed5523',48),
)

class CustodyError(ValueError):
    pass

def require(condition, reason):
    if not condition:
        raise CustodyError(reason)

def git_oid(raw):
    return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()

def strict_json(raw):
    def unique(pairs):
        data = {}
        for k,v in pairs:
            require(k not in data, 'duplicate JSON key')
            data[k]=v
        return data
    def bad_constant(_):
        raise CustodyError('nonstandard JSON constant')
    return json.loads(raw.decode('utf-8'),object_pairs_hook=unique,parse_constant=bad_constant)

def read_citations(body):
    text=body.decode('utf-8')
    ids=CITE.findall(text)
    require(text.count('{{cite:') == len(ids), 'malformed citation token')
    return ids

def excerpt(body, identifier, index):
    text=body.decode('utf-8')
    hits=list(CITE.finditer(text))
    match=hits[index]
    require(match.group(1)==identifier,'citation position drift')
    section=text[max(0,match.start()-150):min(len(text),match.end()+150)]
    clean=' '.join(html.unescape(re.sub(r'<[^>]+>',' ',section)).split())
    return {'index_1_based':index+1,'source_id':identifier,
            'excerpt':clean[:310], 'excerpt_sha256':hashlib.sha256(clean.encode()).hexdigest()}

def text_words(body):
    t=body.decode('utf-8')
    t=re.sub(r'<(?:style|script)\b[^>]*>[\s\S]*?</(?:style|script)>',' ',t,flags=re.I)
    t=html.unescape(re.sub(r'<[^>]+>',' ',t))
    return len(WORDS.findall(t))

def evaluate(docket_bytes, read_blob, *, trusted_docket_oid=PINNED_DOCKET_BLOB,
             trusted_pins=PINS):
    """Unit tests may inject fixture custody pins; CLI NEVER accepts overrides."""
    report={'schema':SCHEMA,'state':INVALID,'publication_authorized':False,
            'independent_qd_pass':False,'source_claims_human_approved':False,
            'medical_safety_verified':False,'merchant_offer_verified':False,
            'verified_paid_orders':None,'realized_net_revenue':None,
            'articles_checked':0,'frozen_citations':0,'observed_citations':0,
            'source_aliases_approved':0,'workorders':[],'errors':[]}
    try:
        require(type(docket_bytes) is bytes and git_oid(docket_bytes)==trusted_docket_oid,
                'R194 evidence docket object changed; explicit human re-baseline required')
        docket=strict_json(docket_bytes)
        require(type(docket) is dict and docket.get('schema')==R194_SCHEMA
                and docket.get('state')==HOLD and docket.get('issue')==136,
                'wrong docket schema or authority')
        for k in ('publication_authorized','independent_qd_pass','medical_safety_verified',
                  'merchant_offer_verified','source_claims_human_approved'):
            require(docket.get(k) is False,'unapproved state: '+k)
        rows=docket.get('articles')
        require(type(rows) is list and len(rows)==len(trusted_pins)==7,'original roster lost')
        found=set()
        for row in rows:
            require(type(row) is dict,'invalid article row')
            key=(row.get('cluster'),row.get('slug'))
            pin=next((p for p in trusted_pins if p[:2]==key),None)
            require(pin is not None and key not in found,'duplicate or unexpected article route')
            found.add(key)
            require(row.get('human_source_review')=='PENDING' and
                    row.get('qualified_safety_review')=='PENDING','false human approval')
            rec={'cluster':key[0],'slug':key[1],'manual_source_claim_review':'PENDING',
                 'unapproved_source_aliases':[],'source_use_scope_changes':[],
                 'citation_sequence_edits':[],'human_review_required':True}
            pairs=[]
            for ver, offset in (('frozen',2),('observed',5)):
                item=row.get(ver)
                require(type(item) is dict,'version missing: '+ver)
                bo,mo,count=pin[offset:offset+3]
                require(item.get('body_blob')==bo and item.get('meta_blob')==mo
                        and type(item.get('citations')) is int and item['citations']==count,
                        'historical or observed object/count pin changed: '+ver)
                body=read_blob(bo);meta=read_blob(mo)
                require(type(body) is bytes and type(meta) is bytes and
                        git_oid(body)==bo and git_oid(meta)==mo,'missing or substituted Git object')
                ids=read_citations(body);m=strict_json(meta)
                require(len(ids)==count and type(m) is dict and m.get('slug')==key[1]
                        and type(m.get('source_use')) is dict and
                        type(m.get('status')) is dict and m['status'].get('publish')=='draft',
                        'citation, route, source-use or draft state changed')
                for sid in ids:
                    use=m['source_use'].get(sid)
                    require(type(use) is str and use.strip(),'missing/non-explanatory source use '+sid)
                wc=text_words(body)
                rec[ver+'_words']=wc
                rec[ver+'_blob_sha1']=bo
                pairs.append((body,ids,m))
                report[ver+'_citations'] = report.get(ver+'_citations',0)+len(ids)
            (old_body,old_ids,old_meta),(new_body,new_ids,new_meta)=pairs
            require(old_meta.get('safety_review')==new_meta.get('safety_review'),
                    'historical safety status changed')
            require(rec['observed_words']>=0.90*rec['frozen_words'],
                    'reading-depth loss (>10%)')
            oldc,newc=Counter(old_ids),Counter(new_ids)
            rec['unapproved_source_aliases']=sorted(set(old_ids)^set(new_ids))
            rec['source_occurrence_changes']={k:[oldc[k],newc[k]]
                for k in sorted(set(oldc)|set(newc)) if oldc[k]!=newc[k]}
            for sid in sorted(set(old_meta['source_use'])|set(new_meta['source_use'])):
                a=old_meta['source_use'].get(sid);b=new_meta['source_use'].get(sid)
                if a!=b:
                    rec['source_use_scope_changes'].append({'source_id':sid,
                         'frozen_source_use':a,'observed_source_use':b,'human_review':'PENDING'})
            for tag,oi,oj,ni,nj in difflib.SequenceMatcher(a=old_ids,b=new_ids,
                                                             autojunk=False).get_opcodes():
                if tag=='equal':continue
                rec['citation_sequence_edits'].append({
                  'edit':tag,'frozen': [excerpt(old_body,old_ids[i],i)
                                         for i in range(oi,oj)],
                  'observed':[excerpt(new_body,new_ids[i],i) for i in range(ni,nj)],
                  'human_review':'PENDING'})
            rec['body_changed_even_if_citations_equal']=old_body!=new_body
            rec['citation_sequence_identical_not_safety_approval']=old_ids==new_ids
            report['workorders'].append(rec)
            report['articles_checked']+=1
        require(found==set(p[:2] for p in trusted_pins),'roster mismatch')
        require(report['frozen_citations']==315 and report['observed_citations']==334,
                'original 315→334 citation evidence census drift')
        report['workorders'].sort(key=lambda r:(r['cluster'],r['slug']))
        report['state']=HOLD
    except (CustodyError,KeyError,UnicodeError,TypeError,ValueError,OSError,
            subprocess.CalledProcessError,subprocess.TimeoutExpired) as exc:
        report['errors'].append(str(exc)[:350])
    return report

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo',type=Path,default=Path('.'))
    p.add_argument('--docket',type=Path,required=True)
    p.add_argument('--report',type=Path)
    args=p.parse_args(argv)
    def gitread(oid):
        return subprocess.run(['git','cat-file','blob',oid],cwd=args.repo,check=True,
            timeout=15,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout
    try:
        result=evaluate(args.docket.read_bytes(),gitread)
    except (OSError,ValueError,TypeError) as exc:
        result={'schema':SCHEMA,'state':INVALID,'errors':[str(exc)[:350]],
                'publication_authorized':False,'independent_qd_pass':False}
    output=json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n'
    if args.report:
        args.report.write_bytes(output.encode('utf-8'))
    else:
        print(output,end='')
    return 2 if result['state']==HOLD else 3

if __name__=='__main__':
    raise SystemExit(main())
