#!/usr/bin/env python3
"""R62 PRIVATE HOLD: contributor citation-context/source drift review docket.

Consumes ONLY R61's unreviewed, two-version Git-custody evidence. Never pairs
claims automatically, promotes source checks, rebases research, or publishes.
R61 must independently regenerate the input from trusted Git objects first.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys

SCHEMA = 'r62-contributor-claim-context-review-v1'
PARENT = 'r61-private-contributor-two-version-lineage-v1'
HOLD_FIELDS = ('may_publish', 'independent_QD_approval',
               'qualified_safety_clearance', 'human_source_links_verified')
CITE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
SHA256 = re.compile(r'[0-9a-f]{64}\Z')
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
REVIEW_COLUMNS = ('work_order_sha256', 'cluster', 'slug', 'version',
                  'citation_ordinal', 'source_id', 'body_sha256',
                  'context_sha256', 'risk_flags_NOT_VERDICT',
                  'context_PREVIEW_ONLY', 'untrusted_reviewer_note')
INVALID_NOTE = frozenset('\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069')
MAX_PACKET = 24_000_000

class ReviewHold(ValueError):
    """Exact source/citation custody or untrusted review intake failed closed."""

def need(condition, why):
    if not condition:
        raise ReviewHold(why)

def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode('utf-8')

def digest(data):
    return hashlib.sha256(canonical(data)).hexdigest()

def text_sha(data):
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def audit_citations(text):
    need(type(text) is str and text.count('{{cite:') == len(CITE.findall(text)),
         'malformed embedded citation in modified article')
    return [{'source_id': match.group(1), 'offset_codepoints': match.start(),
             'unabridged_local_context': text[max(0, match.start()-180):
                                              min(len(text), match.end()+240)]}
            for match in CITE.finditer(text)]

def validate_parent(doc):
    """Reject mutated/incomplete R61 packets. Not a substitute for Git recheck."""
    need(type(doc) is dict and doc.get('schema') == PARENT and
         doc.get('issue') == 136 and doc.get('release_state') == 'HOLD' and
         doc.get('machine_only') is True and
         doc.get('existing_R14_exception_remains_open') is True and
         all(doc.get(k) is False for k in HOLD_FIELDS),
         'R61 prerequisite missing or claims safety/publication approval')
    old = doc.get('fingerprint_sha256')
    need(type(old) is str and SHA256.fullmatch(old) and
         digest({k:v for k,v in doc.items() if k != 'fingerprint_sha256'}) == old,
         'R61 complete evidence fingerprint mismatch')
    counts = doc.get('counts')
    need(type(counts) is dict and counts.get('clusters') == 7 and
         counts.get('original_contributor_articles') == 29 and
         counts.get('frozen_evidence_paths') == 72,
         'original seven-cluster/29-article/72-file census changed')
    groups = doc.get('source_inventories_BOTH_VERSIONS_UNREVIEWED')
    articles = doc.get('per_article_citation_and_context_lineage_NOT_REVIEWED')
    changes = doc.get('unreviewed_git_file_change_docket')
    need(type(groups) is list and len(groups) == 7 and
         type(articles) is list and len(articles) == 29 and
         type(changes) is list and len(changes) == counts.get('changed_preparedness_files'),
         'unreviewed original evidence inventory incomplete')
    registry = {'frozen': defaultdict(list), 'observed': defaultdict(list)}
    source_by_cluster = {}
    names = set()
    for group in groups:
        cluster = group.get('cluster')
        need(type(cluster) is str and cluster not in names and
             group.get('review_state') == 'NOT_REVIEWED', 'duplicate/approved source cluster')
        names.add(cluster)
        source_by_cluster[cluster] = {}
        for version, key in (('frozen','all_original_reading_records_UNABRIDGED'),
                             ('observed','all_observed_reading_records_UNABRIDGED_UNVERIFIED')):
            rows = group.get(key)
            need(type(rows) is list and group.get(
                'original_source_record_count' if version == 'frozen' else
                'observed_source_record_count') == len(rows),
                'contributor reading census changed')
            mapping = {}
            for entry in rows:
                need(type(entry) is dict and type(entry.get('id')) is str and
                     SLUG.fullmatch(entry['id']) and entry['id'] not in mapping and
                     type(entry.get('url')) is str,
                     'contributor source ID/URL invalid or repeated')
                mapping[entry['id']] = entry
                registry[version][entry['id']].append({
                    'cluster':cluster, 'source_record_sha256':digest(entry)})
            source_by_cluster[cluster][version] = mapping
        a, b = source_by_cluster[cluster]['frozen'], source_by_cluster[cluster]['observed']
        need(group.get('added_source_ids_NOT_APPROVED') == sorted(b.keys()-a.keys())
             and group.get('removed_source_ids_NOT_ALIASED') == sorted(a.keys()-b.keys())
             and group.get('modified_same_id_source_records_NOT_APPROVED') ==
             sorted(k for k in a.keys() & b.keys() if a[k] != b[k]),
             'source additions/removals/modifications cannot be hidden')
    need(names == {'start','shelter','food','health','hist-food','hist-home','hist-field'},
         'original named contributor set changed')
    seen, census = set(), {'frozen':0,'observed':0}
    for item in articles:
        need(type(item) is dict and item.get('cluster') in names and
             type(item.get('slug')) is str and SLUG.fullmatch(item['slug']) and
             (item['cluster'],item['slug']) not in seen and
             item.get('review_state') == 'NOT_REVIEWED',
             'duplicated, unsafe or approved article identity')
        seen.add((item['cluster'], item['slug']))
        versions = item.get('versions')
        need(type(versions) is dict and set(versions) == {'frozen','observed'},
             'article must retain both complete versions')
        for version in ('frozen','observed'):
            v = versions[version]
            citations = v.get('citation_occurrences_in_original_order')
            need(type(citations) is list and type(v.get('full_source_use_mapping_UNABRIDGED')) is dict
                 and type(v.get('body_sha256')) is str and
                 SHA256.fullmatch(v['body_sha256']),
                 'article version or source-use evidence missing')
            raw = v.get('full_article_html_WHEN_MODIFIED')
            if item.get('changed_body_requires_claim_context_review'):
                need(type(raw) is str and text_sha(raw) == v['body_sha256'] and
                     audit_citations(raw) == [
                         {'source_id':x.get('source_id'),
                          'offset_codepoints':x.get('offset_codepoints'),
                          'unabridged_local_context':x.get('unabridged_local_context')}
                         for x in citations],
                     'modified full article text/citation offset/context differs')
            need(item.get('citation_tokens_before' if version=='frozen' else
                          'citation_tokens_after') == len(citations),
                 'citation occurrence census changed')
            census[version] += len(citations)
            for citation in citations:
                sid = citation.get('source_id')
                need(type(sid) is str and SLUG.fullmatch(sid) and
                     type(citation.get('offset_codepoints')) is int and
                     citation['offset_codepoints'] >= 0 and
                     type(citation.get('unabridged_local_context')) is str and
                     citation.get('human_claim_support_state') == 'NOT_REVIEWED',
                     'citation location/context or human review state modified')
                need(citation.get('candidate_contributor_readings_NOT_CLAIM_SUPPORT') ==
                     registry[version].get(sid,[]) and
                     citation.get('outside_seven_clusters_must_check_full_R58') is
                     (not bool(registry[version].get(sid,[]))),
                     'contributor citation/source identity crosswalk altered')
        x, y = versions['frozen'], versions['observed']
        need(item.get('changed_body_requires_claim_context_review') is
             (x['body_sha256'] != y['body_sha256']) and
             item.get('changed_metadata_requires_provenance_review') is
             (x.get('metadata_sha256') != y.get('metadata_sha256')) and
             item.get('citation_sequence_exactly_equal_NOT_CLAIM_APPROVAL') is
             ([t['source_id'] for t in x['citation_occurrences_in_original_order']] ==
              [t['source_id'] for t in y['citation_occurrences_in_original_order']]),
             'article body/metadata/citation change flags incorrect')
    need(census['frozen'] == counts.get('old_citation_occurrences') and
         census['observed'] == counts.get('observed_citation_occurrences_UNVERIFIED') and
         len(seen) == 29,
         'citations or original contributor articles disappeared')
    return registry, source_by_cluster

def make_report(lineage):
    registry, sources = validate_parent(lineage)
    articles = lineage['per_article_citation_and_context_lineage_NOT_REVIEWED']
    version_urls = {'frozen':defaultdict(list), 'observed':defaultdict(list)}
    id_conflicts = {'frozen':[], 'observed':[]}
    for version in ('frozen','observed'):
        for cluster in sorted(sources):
            for sid, row in sorted(sources[cluster][version].items()):
                version_urls[version][row['url']].append({
                    'cluster':cluster,'source_id':sid,
                    'source_record_sha256':digest(row)})
        for sid, rows in sorted(registry[version].items()):
            if len(rows) > 1:
                id_conflicts[version].append({
                    'source_id':sid, 'contributor_readings_NOT_ALIASES':rows})
    url_collisions = {v:[{'url_EXACT_NOT_CANONICAL':url, 'distinct_readings':rows}
                         for url,rows in sorted(version_urls[v].items()) if len(rows)>1]
                      for v in ('frozen','observed')}
    impacted, work = [], []
    for article in sorted(articles,key=lambda x:(x['cluster'],x['slug'])):
        group, slug = article['cluster'], article['slug']
        versions = article['versions']
        before = versions['frozen']['citation_occurrences_in_original_order']
        after = versions['observed']['citation_occurrences_in_original_order']
        old_ids = [x['source_id'] for x in before]
        new_ids = [x['source_id'] for x in after]
        flags = []
        if article['changed_body_requires_claim_context_review']:
            flags.append('FULL_BODY_CHANGED_CLAIM_REVIEW_REQUIRED')
        if article['changed_metadata_requires_provenance_review']:
            flags.append('METADATA_OR_SOURCE_USE_CHANGED')
        if (versions['frozen'].get('safety_review_as_recorded_NOT_CLEARED') !=
                versions['observed'].get('safety_review_as_recorded_NOT_CLEARED')):
            flags.append('SAFETY_REVIEW_METADATA_CHANGED_NOT_APPROVED')
        if (versions['frozen'].get('status_as_recorded_NOT_REVIEWED') !=
                versions['observed'].get('status_as_recorded_NOT_REVIEWED')):
            flags.append('PUBLICATION_STATUS_METADATA_CHANGED_NOT_APPROVED')
        for vv in versions.values():
            if (vv.get('status_as_recorded_NOT_REVIEWED',{}).get('publish') != 'draft' or
                vv.get('safety_review_as_recorded_NOT_CLEARED',{}).get('state') != 'pending'):
                flags.append('NON_DRAFT_OR_NON_PENDING_METADATA_HOLD')
        if old_ids != new_ids:
            flags.append('CITATION_SEQUENCE_CHANGED_NO_AUTO_PAIRING')
        elif article['changed_body_requires_claim_context_review'] and any(
            a['unabridged_local_context'] != b['unabridged_local_context']
            for a,b in zip(before,after)):
            flags.append('SAME_CITATION_SEQUENCE_BUT_CONTEXT_CHANGED')
        elif article['changed_body_requires_claim_context_review']:
            flags.append('SAME_CITATION_CONTEXT_BUT_OTHER_PROSE_CHANGED')
        for version in ('frozen','observed'):
            v = versions[version]
            cited = {x['source_id'] for x in v['citation_occurrences_in_original_order']}
            cited.update(v['full_source_use_mapping_UNABRIDGED'])
            for sid in sorted(cited):
                candidates = registry[version].get(sid,[])
                if len(candidates)>1:
                    flags.append('SHARED_SOURCE_ID_MULTIPLE_CONTRIBUTOR_READINGS')
                for c in candidates:
                    cluster = c['cluster']
                    old_row = sources[cluster]['frozen'].get(sid)
                    new_row = sources[cluster]['observed'].get(sid)
                    if old_row != new_row:
                        flags.append('CITED_OR_MAPPED_SOURCE_READING_CHANGED')
                        if old_row is not None and new_row is not None and old_row.get('url') != new_row.get('url'):
                            flags.append('CITED_SOURCE_URL_CHANGED_NOT_REVIEWED')
                    url = sources[cluster][version][sid]['url']
                    if len(version_urls[version][url])>1:
                        flags.append('SHARED_EXACT_URL_DISTINCT_SOURCE_IDENTITIES')
                if not candidates:
                    flags.append('CITATION_OR_MAPPING_OUTSIDE_SEVEN_CLUSTERS_CHECK_R58')
        flags = sorted(set(flags))
        if not flags:
            continue
        impacted.append({'cluster':group,'slug':slug,'risk_flags_NOT_VERDICT':flags,
            'frozen_body_sha256':versions['frozen']['body_sha256'],
            'observed_body_sha256_UNVERIFIED':versions['observed']['body_sha256'],
            'original_citation_count':len(before),'observed_citation_count_UNVERIFIED':len(after),
            'same_sequence_NOT_SAME_CLAIM':old_ids==new_ids,
            'human_claim_support_review':'NOT_REVIEWED',
            'qualified_safety_review':'NOT_REVIEWED'})
        for version in ('frozen','observed'):
            v = versions[version]
            for ordinal,t in enumerate(v['citation_occurrences_in_original_order'],1):
                identity = {'cluster':group,'slug':slug,'version':version,'ordinal':ordinal,
                            'body_sha256':v['body_sha256'],'source_id':t['source_id'],
                            'offset_codepoints':t['offset_codepoints'],
                            'context_sha256':text_sha(t['unabridged_local_context'])}
                work.append({
                    'work_order_sha256':digest(identity),
                    **identity,'unabridged_local_context':t['unabridged_local_context'],
                    'candidate_contributor_readings_NOT_CLAIM_SUPPORT':
                        t['candidate_contributor_readings_NOT_CLAIM_SUPPORT'],
                    'risk_flags_NOT_VERDICT':flags,
                    'human_claim_support_review':'NOT_REVIEWED',
                    'qualified_safety_review':'NOT_REVIEWED'})
    keys = [t['work_order_sha256'] for t in work]
    need(len(keys)==len(set(keys)),'duplicate claim-context work orders')
    result = {'schema':SCHEMA,'issue':136,'release_state':'HOLD','machine_only':True,
        'parent_R61_fingerprint_sha256':lineage['fingerprint_sha256'],
        'original_contributor_articles':29,
        'impacted_articles_NOT_CLEARED':impacted,
        'unreviewed_citation_context_work_orders':work,
        'source_id_collisions_NO_ALIAS':id_conflicts,
        'exact_url_shared_identity_groups_NO_DEDUP':url_collisions,
        'counts':{'impacted_articles':len(impacted), 'citation_work_orders':len(work),
                  'frozen_original_citation_occurrences':lineage['counts']['old_citation_occurrences'],
                  'new_proposed_citation_occurrences_NOT_INTEGRATED':lineage['counts']['observed_citation_occurrences_UNVERIFIED']},
        'R58_full_corpus_35_articles_1959_citations_NOT_REVALIDATED_HERE':True,
        'limitations':('Every work order is machine-only, not evidence that a citation supports a '
                       'specific claim. Stable citation order does not imply unchanged advice. '
                       'Same URL/ID does not merge distinct contributor readings. '
                       'No new contributor version integrated, original R14 provenance HOLD open. '
                       'Qualified emergency/medical safety, human source checks, QD, WordPress '
                       'browser QA and publication remain unapproved.'),
        **{f:False for f in HOLD_FIELDS}}
    result['fingerprint_sha256'] = digest(result)
    return result

def verify_report(report, lineage):
    need(type(report) is dict and report == make_report(lineage),
         'risk docket does not match independently regenerated lineage')
    return True

def display(s, limit=220):
    need(type(s) is str,'invalid preview')
    s = ''.join(c if ord(c)>=32 and ord(c)!=127 and c not in INVALID_NOTE else ' '
                for c in s.replace('\n',' ').replace('\r',' ').replace('\t',' '))
    if len(s)>limit: s=s[:limit]+' [PREVIEW; SEE UNABRIDGED R61 EVIDENCE]'
    if s.lstrip().startswith(('=','+','-','@')): s="'"+s
    return s

def review_csv(report,lineage):
    verify_report(report,lineage)
    out=io.StringIO(newline='')
    writer=csv.writer(out,quoting=csv.QUOTE_ALL,lineterminator='\n')
    writer.writerow(REVIEW_COLUMNS)
    for row in report['unreviewed_citation_context_work_orders']:
        writer.writerow([row['work_order_sha256'],row['cluster'],row['slug'],row['version'],
                         str(row['ordinal']),row['source_id'],row['body_sha256'],
                         row['context_sha256'], ';'.join(row['risk_flags_NOT_VERDICT']),
                         display(row['unabridged_local_context']), ''])
    return out.getvalue().encode('utf-8')

def quarantine_return(report,lineage,csv_bytes):
    """Only store notes as unsigned, untrusted text; no adjudication state."""
    baseline = review_csv(report,lineage)
    need(type(csv_bytes) is bytes and len(csv_bytes)<=MAX_PACKET,
         'returned worksheet missing/oversized')
    try:
        result=list(csv.reader(io.StringIO(csv_bytes.decode('utf-8','strict'),newline=''),strict=True))
        original=list(csv.reader(io.StringIO(baseline.decode('utf-8'),newline=''),strict=True))
    except (UnicodeError,csv.Error) as exc:
        raise ReviewHold('invalid UTF-8 or CSV format') from exc
    need(len(result)==len(original) and result[0]==list(REVIEW_COLUMNS),
         'returned reviewer packet census/columns differ')
    notes=[]
    for n,(row,ref) in enumerate(zip(result[1:],original[1:]),1):
        need(len(row)==len(REVIEW_COLUMNS) and row[:-1]==ref[:-1],
             'returned worksheet altered protected evidence row '+str(n))
        note=row[-1]
        need(len(note)<=3000 and not any(ord(c)<32 or ord(c)==127 or c in INVALID_NOTE
                                          for c in note) and
             not note.lstrip().startswith(('=','+','-','@')),
             'untrusted note is unsafe/spoofed/formula-like')
        if note:
            notes.append({'work_order_sha256':ref[0], 'row_ordinal':n,
                          'untrusted_note_NOT_VERIFIED':note,
                          'review_status':'UNTRUSTED_NOT_REVIEWED'})
    packet={'schema':'r62-unsigned-annotation-quarantine-v1','release_state':'HOLD',
            'machine_only':True,'parent_R62_fingerprint_sha256':report['fingerprint_sha256'],
            'returned_csv_sha256':hashlib.sha256(csv_bytes).hexdigest(),
            'unsigned_untrusted_notes':notes,
            **{f:False for f in HOLD_FIELDS}}
    packet['fingerprint_sha256']=digest(packet)
    return packet

def strict_load(data):
    def check(pairs):
        out={}
        for k,v in pairs:
            need(k not in out,'duplicate JSON field')
            out[k]=v
        return out
    def bad_constant(v):raise ReviewHold('invalid JSON constant')
    return json.loads(data,object_pairs_hook=check,parse_constant=bad_constant)

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[2])
    parser.add_argument('--remote',default='origin')
    parser.add_argument('--summary',action='store_true')
    parser.add_argument('--csv',action='store_true')
    args=parser.parse_args(argv)
    need(re.fullmatch('[A-Za-z0-9_-]+',args.remote),'invalid remote ref name')
    parent=Path(__file__).with_name('r61_contributor_version_source_lineage.py')
    need(parent.is_file() and not parent.is_symlink(),'R61 original gate missing')
    cmd=[sys.executable,'-I',str(parent),'--repo-root',str(args.repo_root),
         '--remote',args.remote]
    # Real trusted Git checkout required; never read a cached/report-only approval.
    p=subprocess.run(cmd,capture_output=True,timeout=120,check=False)
    need(p.returncode==0 and 0<len(p.stdout)<=MAX_PACKET,
         'R61 exact Git-object provenance recheck unavailable/failed closed')
    doc=strict_load(p.stdout.decode('utf-8','strict'))
    report=make_report(doc)
    if args.csv:
        sys.stdout.buffer.write(review_csv(report,doc))
    else:
        print(json.dumps({'schema':SCHEMA,'release_state':'HOLD',
                          'counts':report['counts'],
                          'fingerprint_sha256':report['fingerprint_sha256']}
              if args.summary else report,sort_keys=True,indent=2,ensure_ascii=False))
    return 0

if __name__=='__main__':
    try:raise SystemExit(main())
    except (ReviewHold,OSError,ValueError,UnicodeError,subprocess.TimeoutExpired) as exc:
        print('R62 PRIVATE EVIDENCE HOLD: '+str(exc),file=sys.stderr)
        raise SystemExit(2)