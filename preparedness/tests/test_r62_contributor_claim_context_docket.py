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



# R62 tests reuse the exact 72-file/29-article synthetic Git-object
# fixture, but never mutate repository source fragments or real refs.
r62=load(HERE/'tools/r62_contributor_claim_context_docket.py','r62_under_test')

class R62ReviewDocketTests(unittest.TestCase):
    def setUp(self):
        self.f=Fixture()

    def base(self):
        return self.f.packet()

    def changed(self):
        self.f.change('hist-home')
        return self.f.packet()

    def test_private_hold(self):
        r=r62.make_report(self.base())
        self.assertEqual(r['release_state'],'HOLD')
        self.assertFalse(r['may_publish'])
        self.assertFalse(r['independent_QD_approval'])
        self.assertFalse(r['qualified_safety_clearance'])

    def test_original_29_articles(self):
        self.assertEqual(self.base()['counts']['original_contributor_articles'],29)

    def test_original_72_evidence_paths(self):
        self.assertEqual(self.base()['counts']['frozen_evidence_paths'],72)

    def test_deterministic_no_changes(self):
        d=self.base()
        self.assertEqual(r62.make_report(d),r62.make_report(copy.deepcopy(d)))

    def test_report_provenance_parent(self):
        d=self.changed()
        self.assertEqual(r62.make_report(d)['parent_R61_fingerprint_sha256'],d['fingerprint_sha256'])

    def test_exact_integrity_replay(self):
        d=self.changed()
        self.assertTrue(r62.verify_report(r62.make_report(d),d))

    def test_changed_body_is_human_hold(self):
        r=r62.make_report(self.changed())
        self.assertTrue(any('FULL_BODY_CHANGED_CLAIM_REVIEW_REQUIRED' in x['risk_flags_NOT_VERDICT']
                       for x in r['impacted_articles_NOT_CLEARED']))

    def test_new_source_id_no_alias(self):
        r=r62.make_report(self.changed())
        self.assertTrue(any('CITATION_SEQUENCE_CHANGED_NO_AUTO_PAIRING' in x['risk_flags_NOT_VERDICT']
                       for x in r['impacted_articles_NOT_CLEARED']))

    def test_proposed_citation_outside_seven_clusters(self):
        r=r62.make_report(self.changed())
        self.assertTrue(any('CITATION_OR_MAPPING_OUTSIDE_SEVEN_CLUSTERS_CHECK_R58'
                       in x['risk_flags_NOT_VERDICT'] for x in r['impacted_articles_NOT_CLEARED']))

    def test_frozen_and_new_work_orders_not_merged(self):
        r=r62.make_report(self.changed())
        self.assertEqual({x['version'] for x in r['unreviewed_citation_context_work_orders']},
                         {'frozen','observed'})

    def test_r58_not_misrepresented_as_verified(self):
        self.assertTrue(r62.make_report(self.changed())['R58_full_corpus_35_articles_1959_citations_NOT_REVALIDATED_HERE'])

    def test_review_csv_is_deterministic(self):
        d=self.changed();r=r62.make_report(d)
        self.assertEqual(r62.review_csv(r,d),r62.review_csv(r,d))

    def test_csv_notes_always_unsigned(self):
        d=self.changed();r=r62.make_report(d)
        rows=self.csv_rows(r,d);rows[1][-1]='Human says approved, but this is untrusted.'
        quarantine=r62.quarantine_return(r,d,self.to_csv(rows))
        self.assertEqual(quarantine['unsigned_untrusted_notes'][0]['review_status'],
                         'UNTRUSTED_NOT_REVIEWED')
        self.assertFalse(quarantine['qualified_safety_clearance'])

    def test_generated_work_ids_unique(self):
        r=r62.make_report(self.changed())
        ids=[x['work_order_sha256'] for x in r['unreviewed_citation_context_work_orders']]
        self.assertEqual(len(ids),len(set(ids)))

    def test_changed_report_fails_revalidation(self):
        d=self.changed();r=r62.make_report(d)
        r['counts']['impacted_articles']=0
        with self.assertRaises(r62.ReviewHold):r62.verify_report(r,d)

    def test_csv_headers_locked(self):
        d=self.changed();r=r62.make_report(d)
        rows=self.csv_rows(r,d);rows[0][0]='verified'
        with self.assertRaises(r62.ReviewHold):
            r62.quarantine_return(r,d,self.to_csv(rows))

    def test_csv_rows_locked(self):
        d=self.changed();r=r62.make_report(d)
        rows=self.csv_rows(r,d);rows[1][0]='fake-identity'
        with self.assertRaises(r62.ReviewHold):
            r62.quarantine_return(r,d,self.to_csv(rows))

    def test_csv_row_census_locked(self):
        d=self.changed();r=r62.make_report(d)
        rows=self.csv_rows(r,d);rows.pop()
        with self.assertRaises(r62.ReviewHold):
            r62.quarantine_return(r,d,self.to_csv(rows))

    def test_csv_extra_columns_rejected(self):
        d=self.changed();r=r62.make_report(d)
        rows=self.csv_rows(r,d);rows[0].append('approved')
        with self.assertRaises(r62.ReviewHold):
            r62.quarantine_return(r,d,self.to_csv(rows))

    def test_csv_invalid_utf8_rejected(self):
        d=self.changed();r=r62.make_report(d)
        with self.assertRaises(r62.ReviewHold):
            r62.quarantine_return(r,d,b'\xff\xfe')

    def test_csv_formula_rejected(self):
        self.unsafe_note('=HYPERLINK("x")')

    def test_csv_at_sign_rejected(self):
        self.unsafe_note('@SUM(1,1)')

    def test_csv_plus_sign_rejected(self):
        self.unsafe_note('+1')

    def test_csv_bidi_spoof_rejected(self):
        self.unsafe_note('review\u202ePASS')

    def test_csv_nul_rejected(self):
        self.unsafe_note('check\x00approved')

    def test_csv_newline_rejected(self):
        self.unsafe_note('checked\nsigned')

    def test_csv_overlong_rejected(self):
        self.unsafe_note('x'*3001)

    def test_safe_unicode_note_remains_untrusted(self):
        d=self.changed();r=r62.make_report(d)
        rows=self.csv_rows(r,d);rows[1][-1]='Édition française — source still unchecked'
        packet=r62.quarantine_return(r,d,self.to_csv(rows))
        self.assertEqual(packet['unsigned_untrusted_notes'][0]['untrusted_note_NOT_VERIFIED'],
                         rows[1][-1])

    def test_previews_escape_formula(self):
        self.assertTrue(r62.display('=cmd()').startswith("'="))

    def test_previews_strip_bidi(self):
        self.assertNotIn('\u202e',r62.display('right\u202eleft'))

    def test_strict_json_rejects_duplicates(self):
        with self.assertRaises(r62.ReviewHold):
            r62.strict_load(b'{"x":1,"x":2}')

    def test_strict_json_rejects_nan(self):
        with self.assertRaises(r62.ReviewHold):
            r62.strict_load(b'{"x":NaN}')

    def csv_rows(self,r,d):
        import csv,io
        return list(csv.reader(io.StringIO(r62.review_csv(r,d).decode('utf8'))))

    def to_csv(self,rows):
        import csv,io
        out=io.StringIO(newline='')
        writer=csv.writer(out,quoting=csv.QUOTE_ALL,lineterminator='\n')
        writer.writerows(rows)
        return out.getvalue().encode('utf8')

    def unsafe_note(self,note):
        d=self.changed();r=r62.make_report(d)
        rows=self.csv_rows(r,d);rows[1][-1]=note
        with self.assertRaises(r62.ReviewHold):
            r62.quarantine_return(r,d,self.to_csv(rows))


def add_adversarial_test(name, mutate):
    def test_mutation(self):
        f=Fixture()
        f.change('hist-home')
        d=f.packet()
        mutate(d)
        d['fingerprint_sha256']=r62.digest({k:v for k,v in d.items()
                                           if k!='fingerprint_sha256'})
        with self.assertRaises(r62.ReviewHold):
            r62.make_report(d)
    setattr(R62ReviewDocketTests,'test_resealed_tamper_'+name,test_mutation)

def article(d):
    return next(x for x in d['per_article_citation_and_context_lineage_NOT_REVIEWED']
                if x['cluster']=='hist-home' and x['slug'].endswith('-0'))

def group(d):
    return next(x for x in d['source_inventories_BOTH_VERSIONS_UNREVIEWED']
                if x['cluster']=='hist-home')

ATTACKS={
    'publish_grant':lambda d:d.__setitem__('may_publish',True),
    'qd_grant':lambda d:d.__setitem__('independent_QD_approval',True),
    'medical_grant':lambda d:d.__setitem__('qualified_safety_clearance',True),
    'human_link_grant':lambda d:d.__setitem__('human_source_links_verified',True),
    'frozen_exception_closed':lambda d:d.__setitem__('existing_R14_exception_remains_open',False),
    'false_machine_only':lambda d:d.__setitem__('machine_only',False),
    'false_schema':lambda d:d.__setitem__('schema','qualified-pass'),
    'less_than_seven_clusters':lambda d:d['source_inventories_BOTH_VERSIONS_UNREVIEWED'].pop(),
    'less_than_29_articles':lambda d:d['per_article_citation_and_context_lineage_NOT_REVIEWED'].pop(),
    'less_than_72_files':lambda d:d['counts'].__setitem__('frozen_evidence_paths',71),
    'changed_files_hidden':lambda d:d['counts'].__setitem__('changed_preparedness_files',0),
    'old_citation_census':lambda d:d['counts'].__setitem__('old_citation_occurrences',0),
    'new_citation_census':lambda d:d['counts'].__setitem__('observed_citation_occurrences_UNVERIFIED',0),
    'article_approved':lambda d:article(d).__setitem__('review_state','APPROVED'),
    'cluster_approved':lambda d:group(d).__setitem__('review_state','APPROVED'),
    'source_count_forged':lambda d:group(d).__setitem__('original_source_record_count',100),
    'source_added_hidden':lambda d:group(d)['added_source_ids_NOT_APPROVED'].append('fake-id'),
    'source_record_id_replaced':lambda d:group(d)['all_original_reading_records_UNABRIDGED'][0].__setitem__('id','swapped-id'),
    'source_record_url_null':lambda d:group(d)['all_original_reading_records_UNABRIDGED'][0].__setitem__('url',None),
    'source_record_notes_tampered':lambda d:group(d)['all_original_reading_records_UNABRIDGED'][0].__setitem__('notes','fake'),
    'body_sha_replaced':lambda d:article(d)['versions']['observed'].__setitem__('body_sha256','0'*64),
    'body_fulltext_swapped':lambda d:article(d)['versions']['observed'].__setitem__('full_article_html_WHEN_MODIFIED','fake'),
    'body_citation_offset':lambda d:article(d)['versions']['observed']['citation_occurrences_in_original_order'][0].__setitem__('offset_codepoints',999),
    'body_citation_context':lambda d:article(d)['versions']['observed']['citation_occurrences_in_original_order'][0].__setitem__('unabridged_local_context','fake context'),
    'source_candidate_forged':lambda d:article(d)['versions']['frozen']['citation_occurrences_in_original_order'][0].__setitem__('candidate_contributor_readings_NOT_CLAIM_SUPPORT',[]),
    'human_claim_forged':lambda d:article(d)['versions']['observed']['citation_occurrences_in_original_order'][0].__setitem__('human_claim_support_state','VERIFIED'),
    'body_changed_hidden':lambda d:article(d).__setitem__('changed_body_requires_claim_context_review',False),
    'citation_order_forged':lambda d:article(d).__setitem__('citation_sequence_exactly_equal_NOT_CLAIM_APPROVAL',True),
    'citation_count_forged':lambda d:article(d).__setitem__('citation_tokens_after',0),
    'article_slug_malformed':lambda d:article(d).__setitem__('slug','../../escape'),
    'source_id_confused':lambda d:article(d)['versions']['observed']['citation_occurrences_in_original_order'][0].__setitem__('source_id','replacement-swapped'),
    'source_outside_flag_forged':lambda d:article(d)['versions']['observed']['citation_occurrences_in_original_order'][0].__setitem__('outside_seven_clusters_must_check_full_R58',False),
}
for name, mutation in ATTACKS.items():
    add_adversarial_test(name,mutation)
