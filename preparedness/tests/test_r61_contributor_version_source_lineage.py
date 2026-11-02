"""R61 synthetic source/citation drift and tamper tests; no network/CMS writes."""
from __future__ import annotations
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).parents[1]

def load(path, name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

r61=load(HERE/'tools/r61_contributor_version_source_lineage.py','r61_under_test')
r60=load(HERE/'tools/r60_contributor_provenance_drift_docket.py','r60_fixture_dependency')
COUNTS={'start':4,'shelter':4,'food':4,'health':3,'hist-food':6,'hist-home':5,'hist-field':3}

def hash_ref(text):
    return hashlib.sha1(text.encode()).hexdigest()

class Fixture:
    def __init__(self):
        self.manifest={'release_state':'HOLD','may_publish':False,
             'independent_human_source_checks_verified':0,'branches':[]}
        self.heads,self.storage,self.changed,self.branches={},{},{},{}
        for group, count in COUNTS.items():
            sha=hash_ref('frozen-'+group)
            self.heads[group]=sha
            self.branches[group]='claude/prep-'+group
            paths=[]
            for i in range(count):
                slug=group+'-guide-'+str(i)
                sid='src-'+group
                body=f'preparedness/content/articles/{slug}.body.html'
                meta=f'preparedness/content/articles/{slug}.meta.json'
                paths.extend([(body,('<p>Old advice {{cite:'+sid+'}}. A second '+'{{cite:'+sid+'}}.</p>').encode()),
                       (meta,json.dumps({'slug':slug,'source_use':{sid:'original full reading note'},
                       'status':{'publish':'draft'},'safety_review':{'state':'pending'}}).encode())])
            paths.append((f'preparedness/docs/CLUSTER-{group}.md',b'# Notes\n'))
            paths.append((f'preparedness/sources/fragments/{group}.json',json.dumps({
                'sources':[{'id':'src-'+group,'url':'https://example.invalid/'+group,
                   'notes':'Long original reading depth; source must be human checked',
                   'human_link_check':False}]}).encode()))
            files=[]
            for path,data in paths:
                self.storage[(sha,path)]=data
                files.append({'path':path,'contributor_blob_sha':r60.blob_sha(data)})
            self.manifest['branches'].append({'name':group,'contributor_commit_sha':sha,'files':files})
        assert sum(len(e['files']) for e in self.manifest['branches'])==72
    def change(self, group='hist-home', path=None, content=None):
        frozen=next(x['contributor_commit_sha'] for x in self.manifest['branches'] if x['name']==group)
        live=hash_ref('observed-'+group)
        if self.heads[group]==frozen:
            for (sha,p),data in list(self.storage.items()):
                if sha==frozen: self.storage[(live,p)]=data
            self.changed[(frozen,live)]=[]
        self.heads[group]=live
        if path is None:
            path=f'preparedness/content/articles/{group}-guide-0.body.html'
        if content is None:
            content=b'<p>Different text {{cite:replacement}}; keep context.</p>'
        self.storage[(live,path)]=content
        if path not in self.changed[(frozen,live)]:
            self.changed[(frozen,live)].append(path)
        return path
    def lookup(self,sha,path):
        v=self.storage.get((sha,path))
        return r60.blob_sha(v) if v is not None else None
    def read(self,sha,path):
        return self.storage[(sha,path)]
    def paths(self,old,new):
        return self.changed.get((old,new),[])
    def frozen_check(self,d):
        if d is not self.manifest:
            raise r60.DriftHold('unexpected manifest')
    def report(self):
        return r60.report(self.manifest,self.heads,self.paths,self.lookup,self.read,
                          self.frozen_check,self.branches)
    def packet(self):
        return r61.prepare(self.manifest,self.report(),self.lookup,self.read)

class LineageTests(unittest.TestCase):
    def setUp(self): self.f=Fixture()
    def test_frozen_census(self):
        d=self.f.packet()
        self.assertEqual(d['counts']['clusters'],7)
        self.assertEqual(d['counts']['original_contributor_articles'],29)
        self.assertEqual(d['counts']['frozen_evidence_paths'],72)
    def test_all_original_citations_not_lost(self):
        d=self.f.packet()
        self.assertEqual(d['counts']['old_citation_occurrences'],58)
        self.assertEqual(d['counts']['observed_citation_occurrences_UNVERIFIED'],58)
    def test_moved_branch_with_body_change(self):
        self.f.change()
        d=self.f.packet()
        self.assertEqual(d['counts']['contributor_heads_moved'],1)
        self.assertEqual(d['counts']['articles_with_body_changes'],1)
    def test_source_version_both_preserved(self):
        path='preparedness/sources/fragments/hist-home.json'
        frozen=next(e['contributor_commit_sha'] for e in self.f.manifest['branches'] if e['name']=='hist-home')
        obj=json.loads(self.f.storage[(frozen,path)])
        obj['sources'][0]['url']='https://example.invalid/different'
        self.f.change('hist-home',path,json.dumps(obj).encode())
        row=next(e for e in self.f.packet()['source_inventories_BOTH_VERSIONS_UNREVIEWED'] if e['cluster']=='hist-home')
        self.assertNotEqual(row['all_original_reading_records_UNABRIDGED'],
                            row['all_observed_reading_records_UNABRIDGED_UNVERIFIED'])
        self.assertEqual(row['modified_same_id_source_records_NOT_APPROVED'],['src-hist-home'])
    def test_added_id_not_silently_replaces_removed(self):
        path='preparedness/sources/fragments/hist-food.json'
        self.f.change('hist-food',path,b'{"sources":[{"id":"new-jerky","notes":"not human verified"}]}')
        row=next(e for e in self.f.packet()['source_inventories_BOTH_VERSIONS_UNREVIEWED'] if e['cluster']=='hist-food')
        self.assertEqual(row['added_source_ids_NOT_APPROVED'],['new-jerky'])
        self.assertEqual(row['removed_source_ids_NOT_ALIASED'],['src-hist-food'])
    def test_source_reference_can_resolve_cross_cluster_without_alias(self):
        self.f.change(content=b'<p>{{cite:src-food}}</p>')
        item=next(x for x in self.f.packet()['per_article_citation_and_context_lineage_NOT_REVIEWED'] if x['slug']=='hist-home-guide-0')
        citation=item['versions']['observed']['citation_occurrences_in_original_order'][0]
        self.assertEqual(citation['candidate_contributor_readings_NOT_CLAIM_SUPPORT'][0]['cluster'],'food')
    def test_unresolved_source_flag_does_not_forge_missing_global_evidence(self):
        self.f.change(content=b'<p>{{cite:some-global-integration-source}}</p>')
        item=next(x for x in self.f.packet()['per_article_citation_and_context_lineage_NOT_REVIEWED'] if x['slug']=='hist-home-guide-0')
        self.assertTrue(item['versions']['observed']['citation_occurrences_in_original_order'][0]['outside_seven_clusters_must_check_full_R58'])
    def test_repeated_citation_positions_preserved(self):
        item=self.f.packet()['per_article_citation_and_context_lineage_NOT_REVIEWED'][0]
        self.assertEqual(len(item['versions']['frozen']['citation_occurrences_in_original_order']),2)
        self.assertLess(item['versions']['frozen']['citation_occurrences_in_original_order'][0]['offset_codepoints'],
                        item['versions']['frozen']['citation_occurrences_in_original_order'][1]['offset_codepoints'])
    def test_modified_body_retains_both_unabridged_versions(self):
        self.f.change()
        item=next(x for x in self.f.packet()['per_article_citation_and_context_lineage_NOT_REVIEWED'] if x['slug']=='hist-home-guide-0')
        self.assertIn('Old advice',item['versions']['frozen']['full_article_html_WHEN_MODIFIED'])
        self.assertIn('Different text',item['versions']['observed']['full_article_html_WHEN_MODIFIED'])
    def test_source_notes_not_truncated(self):
        item=self.f.packet()['source_inventories_BOTH_VERSIONS_UNREVIEWED'][0]
        self.assertIn('Long original reading depth',str(item['all_original_reading_records_UNABRIDGED']))
    def test_no_automatic_approval(self):
        d=self.f.packet()
        self.assertEqual(d['release_state'],'HOLD')
        self.assertFalse(d['may_publish'])
        self.assertFalse(d['qualified_safety_clearance'])
        self.assertFalse(d['independent_QD_approval'])
    def test_modified_meta_requires_review(self):
        path='preparedness/content/articles/hist-home-guide-0.meta.json'
        frozen=next(e['contributor_commit_sha'] for e in self.f.manifest['branches'] if e['name']=='hist-home')
        obj=json.loads(self.f.storage[(frozen,path)])
        obj['safety_review']['state']='approved'
        self.f.change('hist-home',path,json.dumps(obj).encode())
        item=next(x for x in self.f.packet()['per_article_citation_and_context_lineage_NOT_REVIEWED'] if x['slug']=='hist-home-guide-0')
        self.assertTrue(item['changed_metadata_requires_provenance_review'])
        self.assertFalse(self.f.packet()['qualified_safety_clearance'])
    def test_malformed_citation_blocks_export(self):
        self.f.change(content=b'<p>{{cite:Not Allowed}}</p>')
        with self.assertRaisesRegex(r61.LineageHold,'malformed citation'):self.f.packet()
    def test_duplicate_json_keys_blocks_export(self):
        self.f.change('hist-home','preparedness/sources/fragments/hist-home.json',
                      b'{"sources":[],"sources":[]}')
        with self.assertRaisesRegex(r61.LineageHold,'duplicate key'):self.f.packet()
    def test_missing_frozen_blob_fails(self):
        self.f.storage.pop((self.f.heads['food'],'preparedness/sources/fragments/food.json'))
        with self.assertRaises((r61.LineageHold,r60.DriftHold)):self.f.packet()
    def test_wrong_git_bytes_fails(self):
        self.f.change()
        original=self.f.read
        self.f.read=lambda sha,path: b'fake' if sha==self.f.heads['hist-home'] and path.endswith('.body.html') else original(sha,path)
        with self.assertRaises((r61.LineageHold,r60.DriftHold)):self.f.packet()
    def test_repeated_same_source_id_in_fragment_fails(self):
        path='preparedness/sources/fragments/hist-home.json'
        self.f.change('hist-home',path,b'{"sources":[{"id":"x"},{"id":"x"}]}')
        with self.assertRaises((r61.LineageHold,r60.DriftHold)):self.f.packet()
    def test_sha_fingerprint_deterministic(self):
        self.f.change()
        self.assertEqual(self.f.packet(),self.f.packet())
    def test_human_notes_not_accepted_as_signed_approval(self):
        self.f.change()
        packet=self.f.packet(); packet['human_reviewers_signed']=['fake']
        with self.assertRaises(r61.LineageHold):
            r61.verify(packet,self.f.manifest,self.f.report(),self.f.lookup,self.f.read)
    def test_missing_report_change_row_rejected(self):
        self.f.change()
        report=self.f.report(); report['changed_files'].clear()
        with self.assertRaises(r61.LineageHold):
            r61.prepare(self.f.manifest,report,self.f.lookup,self.f.read)
    def test_altered_report_digest_rejected(self):
        self.f.change()
        report=self.f.report(); report['fingerprint_sha256']='0'*64
        with self.assertRaises(r61.LineageHold):
            r61.prepare(self.f.manifest,report,self.f.lookup,self.f.read)
    def test_repeated_contributor_drift_file_rejected(self):
        self.f.change()
        report=self.f.report(); report['changed_files'].append(copy.deepcopy(report['changed_files'][0]))
        report['changed_file_count']+=1
        report['fingerprint_sha256']=r61.digest({k:v for k,v in report.items() if k!='fingerprint_sha256'})
        with self.assertRaises(r61.LineageHold):
            r61.prepare(self.f.manifest,report,self.f.lookup,self.f.read)

class AdversarialRegeneration(unittest.TestCase):
    def setUp(self):
        self.f=Fixture()
        self.f.change()
        self.original=self.f.packet()

def attack(name,fn):
    def test(self):
        forged=copy.deepcopy(self.original)
        fn(forged)
        with self.assertRaises(r61.LineageHold,msg=name):
            r61.verify(forged,self.f.manifest,self.f.report(),self.f.lookup,self.f.read)
    setattr(AdversarialRegeneration,'test_refuse_'+name,test)

ATTACKS={
'change_issue': lambda d:d.update(issue=999),
'change_schema':lambda d:d.update(schema='approved'),
'publish':lambda d:d.update(may_publish=True),
'remove_hold':lambda d:d.update(release_state='PASS'),
'machine_false':lambda d:d.update(machine_only=False),
'qd_pass':lambda d:d.update(independent_QD_approval=True),
'safety_pass':lambda d:d.update(qualified_safety_clearance=True),
'link_pass':lambda d:d.update(human_source_links_verified=True),
'overwrite_digest':lambda d:d.update(fingerprint_sha256='0'*64),
'claimed35':lambda d:d['counts'].update(original_contributor_articles=35),
'claimed72':lambda d:d['counts'].update(frozen_evidence_paths=0),
'claimed7':lambda d:d['counts'].update(clusters=1),
'claimed_no_move':lambda d:d['counts'].update(contributor_heads_moved=0),
'claimed_no_change':lambda d:d['counts'].update(changed_preparedness_files=0),
'claim_no_original_cites':lambda d:d['counts'].update(old_citation_occurrences=0),
'claim_new_cites':lambda d:d['counts'].update(observed_citation_occurrences_UNVERIFIED=999),
'clear_inventory':lambda d:d['source_inventories_BOTH_VERSIONS_UNREVIEWED'].clear(),
'clear_articles':lambda d:d['per_article_citation_and_context_lineage_NOT_REVIEWED'].clear(),
'clear_git_changes':lambda d:d['unreviewed_git_file_change_docket'].clear(),
'rewrite_frozen_manifest':lambda d:d.update(frozen_manifest_blob_sha='0'*40),
'parent_fingerprint':lambda d:d.update(parent_R60_fingerprint_sha256='0'*64),
'remove_exception':lambda d:d.update(existing_R14_exception_remains_open=False),
'fake_six_approved':lambda d:d.update(other_six_integrated_articles_OUTSIDE_R14_SCOPE=0),
'fake_r58_pass':lambda d:d.update(complete_35_article_1959_occurrence_R58_custody_unchanged_NOT_REVALIDATED_HERE=False),
'new_source_approved':lambda d:d['source_inventories_BOTH_VERSIONS_UNREVIEWED'][0].update(review_state='PASS'),
'source_old_clear':lambda d:d['source_inventories_BOTH_VERSIONS_UNREVIEWED'][0].pop('all_original_reading_records_UNABRIDGED'),
'source_new_clear':lambda d:d['source_inventories_BOTH_VERSIONS_UNREVIEWED'][0].pop('all_observed_reading_records_UNABRIDGED_UNVERIFIED'),
'source_sha_change':lambda d:d['source_inventories_BOTH_VERSIONS_UNREVIEWED'][0].update(frozen_fragment_sha256='x'),
'source_oid_change':lambda d:d['source_inventories_BOTH_VERSIONS_UNREVIEWED'][0].update(frozen_commit='0'*40),
'source_count_change':lambda d:d['source_inventories_BOTH_VERSIONS_UNREVIEWED'][0].update(original_source_record_count=0),
'cover_source_notes':lambda d:d['source_inventories_BOTH_VERSIONS_UNREVIEWED'][0]['all_original_reading_records_UNABRIDGED'][0].update(notes='TRUNCATED'),
'omit_article':lambda d:d['per_article_citation_and_context_lineage_NOT_REVIEWED'].pop(),
'change_article_slug':lambda d:d['per_article_citation_and_context_lineage_NOT_REVIEWED'][0].update(slug='other'),
'change_article_cluster':lambda d:d['per_article_citation_and_context_lineage_NOT_REVIEWED'][0].update(cluster='other'),
'change_article_review':lambda d:d['per_article_citation_and_context_lineage_NOT_REVIEWED'][0].update(review_state='PASS'),
'change_token_count':lambda d:d['per_article_citation_and_context_lineage_NOT_REVIEWED'][0].update(citation_tokens_before=0),
'clear_citation_ids':lambda d:d['per_article_citation_and_context_lineage_NOT_REVIEWED'][0].update(original_citation_id_counts={}),
'change_html_sha':lambda d:d['per_article_citation_and_context_lineage_NOT_REVIEWED'][0]['versions']['frozen'].update(body_sha256='0'*64),
'change_source_use':lambda d:d['per_article_citation_and_context_lineage_NOT_REVIEWED'][0]['versions']['frozen'].update(full_source_use_mapping_UNABRIDGED={}),
'clear_citations':lambda d:d['per_article_citation_and_context_lineage_NOT_REVIEWED'][0]['versions']['frozen']['citation_occurrences_in_original_order'].clear(),
'change_offset':lambda d:d['per_article_citation_and_context_lineage_NOT_REVIEWED'][0]['versions']['frozen']['citation_occurrences_in_original_order'][0].update(offset_codepoints=9000),
'change_token_id':lambda d:d['per_article_citation_and_context_lineage_NOT_REVIEWED'][0]['versions']['frozen']['citation_occurrences_in_original_order'][0].update(source_id='new'),
'claim_human_support':lambda d:d['per_article_citation_and_context_lineage_NOT_REVIEWED'][0]['versions']['frozen']['citation_occurrences_in_original_order'][0].update(human_claim_support_state='VERIFIED'),
'claim_source_support':lambda d:d['per_article_citation_and_context_lineage_NOT_REVIEWED'][0]['versions']['frozen']['citation_occurrences_in_original_order'][0].update(candidate_contributor_readings_NOT_CLAIM_SUPPORT=[{'fake':True}]),
'disguise_missing':lambda d:d['per_article_citation_and_context_lineage_NOT_REVIEWED'][0]['versions']['frozen']['citation_occurrences_in_original_order'][0].update(outside_seven_clusters_must_check_full_R58=True),
'change_citation_excerpt':lambda d:d['per_article_citation_and_context_lineage_NOT_REVIEWED'][0]['versions']['frozen']['citation_occurrences_in_original_order'][0].update(unabridged_local_context='APPROVED'),
'change_limitations':lambda d:d.update(limitations='Human approved.'),
}
for name,fn in ATTACKS.items():attack(name,fn)
