"""R111 private synthetic fail-closed tests: no repository or fixture writes."""
import copy
import importlib.util
from pathlib import Path
import unittest

SRC = Path(__file__).resolve().parents[1] / 'tools' / 'r111_converged_source_review_gate.py'
spec = importlib.util.spec_from_file_location('r111_hold', SRC)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)

def seal(obj, field):
    obj.pop(field, None)
    obj[field] = g.digest(obj)
    return obj

def fixture():
    origins = ['start','shelter','food','health','hist-food','hist-home','hist-field']
    tips = [{'origin':o, 'frozen_commit_sha':'a'*40, 'observed_commit_sha':'b'*40,
             'human_lineage_approval':'NOT_REVIEWED', 'is_direct_descendant':True} for o in origins]
    old, new, claim, adjacent = [], [], [], []
    for n in range(23):
        origin = origins[n % len(origins)]
        kind = 'body' if n < 7 else ('meta' if n < 13 else 'fragment' if n < 17 else 'doc')
        path = ('preparedness/content/articles/' if kind in ('body','meta') else
                'preparedness/sources/fragments/' if kind == 'fragment' else 'preparedness/docs/') + f'entry{n}.{kind}'
        old.append({'origin':origin,'path':path,'classification':kind,
                    'frozen_blob_sha':'c'*40,'current_blob_sha':'d'*40,
                    'human_provenance_review':'NOT_REVIEWED',
                    'human_source_and_claim_review':'NOT_REVIEWED','may_publish':False})
        new.append({'origin':origin,'path':path,'category':kind,
                    'frozen_oid':'c'*40,'observed_oid':'d'*40,
                    'human_source_or_claim_review':'NOT_REVIEWED',
                    'human_safety_review':'NOT_REVIEWED','may_publish':False})
        if kind == 'body':
            common = {'origin':origin,'path':path,
                      'frozen_oid':'c'*40,'observed_oid':'d'*40,'may_publish':False}
            claim.append({**common,'human_claim_review':'NOT_REVIEWED',
                          'citation_neighborhood_review_NOT_APPROVED':{'may_publish':False}})
            adjacent.append({**common,'human_source_review':'NOT_REVIEWED',
                             'cross_paragraph_review_NOT_APPROVED':{'may_publish':False}})
    url_groups = []
    for n in range(30):
        contexts = [{'article_slug':'art-'+str(n), 'selected_source_origin':'start',
                     'source_id_as_authored':f'src-{n}',
                     'author_scoped_source_use':'original limited reading',
                     'existing_article_safety_state_without_new_approval':'pending'}]
        url_groups.append({'literal_url':f'https://example.org/source/{n}',
            'review_state':'pending-human-source-and-reading-scope-review',
            'human_review':'NOT_REVIEWED','same_url_is_not_shared_claim_authority':True,
            'variant_count':2, 'variants':[
                {'origin':'start','source_id':f'src-{n}','variant_sha256':'1'*64},
                {'origin':'shelter','source_id':f'src-b-{n}','variant_sha256':'2'*64}],
            'citation_occurrences':1,'citing_articles':['art-'+str(n)],
            'author_bound_citation_contexts':contexts})
    lineage = seal({'schema':'r107-seven-contributor-lineage-adoption-hold-v1',
        'release_state':'HOLD','may_publish':False,
        'changed_path_count':23,'moved_branch_count':5,
        'original_evidence_paths':72,'distinct_original_articles':29,
        'frozen_R14_historical_exception_open':True,
        'mandatory_R15_seven_cluster_parity':'FAIL_CLOSED_ON_MOVED_REFS',
        'source_or_claim_accuracy_verified':False,
        'qualified_emergency_or_medical_safety_review':False,
        'independent_QD_PASS':False,'unreviewed_shared_url_groups':30,
        'human_safety_exceptions_unresolved':15,'editorial_decisions_unresolved':22,
        'seven_contributor_commit_ancestry':tips,
        'contributor_reviewer_queue_NOT_APPROVED':old},'sha256_NOT_A_SIGNATURE')
    impacts = seal({'schema':'r108-source-citation-change-impact-HOLD-v1',
        'release_state':'HOLD','may_publish':False,
        'R107_queue_sha256_NOT_A_SIGNATURE':lineage['sha256_NOT_A_SIGNATURE'],
        'row_count':23,'factual_claim_support_approved':False,
        'qualified_emergency_safety_approved':False,
        'independent_QD_PASS':False,
        'unreviewed_shared_source_url_groups':30,
        'rows_NOT_APPROVED':new},'sha256_NOT_A_SIGNATURE')
    claims = seal({'schema':'r109-citation-neighborhood-custody-HOLD-v1',
        'release_state':'HOLD','may_publish':False,
        'R108_sha256_NOT_A_SIGNATURE':impacts['sha256_NOT_A_SIGNATURE'],
        'changed_body_review_count':7,
        'qualified_emergency_safety_approved':False,
        'independent_QD_PASS':False,
        'rows_NOT_APPROVED':claim},'sha256_NOT_A_SIGNATURE')
    caveats = seal({'schema':'r110-adjacent-uncited-caveat-custody-HOLD-v1',
        'release_state':'HOLD','may_publish':False,
        'R109_sha256_NOT_A_SIGNATURE':claims['sha256_NOT_A_SIGNATURE'],
        'changed_body_review_count':7,
        'qualified_emergency_safety_approved':False,
        'independent_QD_PASS':False,
        'rows_NOT_APPROVED':adjacent},'sha256_NOT_A_SIGNATURE')
    collisions = seal({'schema':'r102-author-scoped-citation-collision-workorder-v1',
        'release_state':'HOLD','may_publish':False,'may_merge':False,
        'source_claim_support_review':'NOT_REVIEWED',
        'qualified_safety_review':'NOT_REVIEWED',
        'independent_QD':'NOT_REVIEWED','original_article_drafts':35,
        'actual_buildable_tools':1, 'additional_planned_tools_not_buildable':5,
        'literal_url_collision_groups_pending_human_review':30,
        'collision_citation_occurrences':30,'groups':url_groups},'sha256_seal')
    return (lineage, impacts, claims, caveats, collisions)

class Baseline(unittest.TestCase):
    def test_valid_synthetic_reports_remain_hold(self):
        v=g.compose(*fixture())
        self.assertEqual(v['changed_contributor_paths_pending_review'],23)
        self.assertEqual(v['changed_article_bodies_pending_review'],7)
        self.assertEqual(v['shared_url_groups_pending_review'],30)
        self.assertEqual(v['shared_url_citation_occurrences_pending_review'],30)
        self.assertEqual(v['article_count'],35)
        self.assertFalse(v['may_publish'])
        self.assertFalse(v['may_merge'])
        self.assertFalse(v['independent_QD_PASS'])
        self.assertFalse(v['qualified_safety_review_approved'])
        self.assertFalse(v['wordpress_writes'])
        self.assertFalse(v['source_rewrites'])
        self.assertNotIn('example.org',g.canonical(v))
        self.assertEqual(len(v['contributor_worklist_NOT_APPROVED']),23)
        self.assertEqual(len(v['shared_url_worklist_NOT_APPROVED']),30)
    def test_repeatable(self):
        self.assertEqual(g.compose(*fixture()),g.compose(*fixture()))
    def test_input_unchanged(self):
        original=fixture(); before=copy.deepcopy(original)
        g.compose(*original)
        self.assertEqual(original,before)
    def test_seal_is_not_signature_claim(self):
        self.assertEqual(len(g.compose(*fixture())['sha256_NOT_A_SIGNATURE']),64)
    def test_without_validator_does_not_claim_quality(self):
        self.assertFalse(g.compose(*fixture())['source_factual_support_verified'])

# Every mutation is self-resealed. Chain is also resealed; this tests cross-
# artifact agreement rather than simply detecting stale checksum strings.
class Adversarial(unittest.TestCase):
    def assert_rejected(self, mutator):
        records=list(fixture())
        mutator(records)
        for record, key in zip(records, ['sha256_NOT_A_SIGNATURE']*4+['sha256_seal']):
            seal(record,key)
        with self.assertRaises((g.Hold,KeyError,TypeError,ValueError)):
            g.compose(*records)

MUTATIONS = [
    (0,lambda x:x.update(release_state='PASS')),
    (0,lambda x:x.update(may_publish=True)),
    (0,lambda x:x.update(changed_path_count=22)),
    (0,lambda x:x.update(moved_branch_count=4)),
    (0,lambda x:x.update(original_evidence_paths=71)),
    (0,lambda x:x.update(distinct_original_articles=28)),
    (0,lambda x:x.update(frozen_R14_historical_exception_open=False)),
    (0,lambda x:x.update(mandatory_R15_seven_cluster_parity='PASS')),
    (0,lambda x:x.update(source_or_claim_accuracy_verified=True)),
    (0,lambda x:x.update(qualified_emergency_or_medical_safety_review=True)),
    (0,lambda x:x.update(independent_QD_PASS=True)),
    (0,lambda x:x.update(unreviewed_shared_url_groups=29)),
    (0,lambda x:x.update(human_safety_exceptions_unresolved=14)),
    (0,lambda x:x.update(editorial_decisions_unresolved=21)),
    (0,lambda x:x['seven_contributor_commit_ancestry'].pop()),
    (0,lambda x:x['seven_contributor_commit_ancestry'][0].update(human_lineage_approval='APPROVED')),
    (0,lambda x:x['seven_contributor_commit_ancestry'][0].update(is_direct_descendant=False)),
    (0,lambda x:x['contributor_reviewer_queue_NOT_APPROVED'].pop()),
    (0,lambda x:x['contributor_reviewer_queue_NOT_APPROVED'][0].update(human_provenance_review='APPROVED')),
    (0,lambda x:x['contributor_reviewer_queue_NOT_APPROVED'][0].update(may_publish=True)),
    (1,lambda x:x.update(release_state='PASS')),
    (1,lambda x:x.update(may_publish=True)),
    (1,lambda x:x.update(row_count=22)),
    (1,lambda x:x.update(factual_claim_support_approved=True)),
    (1,lambda x:x.update(qualified_emergency_safety_approved=True)),
    (1,lambda x:x.update(independent_QD_PASS=True)),
    (1,lambda x:x.update(unreviewed_shared_source_url_groups=29)),
    (1,lambda x:x['rows_NOT_APPROVED'].pop()),
    (1,lambda x:x['rows_NOT_APPROVED'][0].update(category='meta')),
    (1,lambda x:x['rows_NOT_APPROVED'][0].update(observed_oid='e'*40)),
    (1,lambda x:x['rows_NOT_APPROVED'][0].update(human_safety_review='approved')),
    (1,lambda x:x['rows_NOT_APPROVED'][0].update(may_publish=True)),
    (2,lambda x:x.update(release_state='PASS')),
    (2,lambda x:x.update(may_publish=True)),
    (2,lambda x:x.update(changed_body_review_count=6)),
    (2,lambda x:x.update(independent_QD_PASS=True)),
    (2,lambda x:x['rows_NOT_APPROVED'].pop()),
    (2,lambda x:x['rows_NOT_APPROVED'][0].update(frozen_oid='f'*40)),
    (2,lambda x:x['rows_NOT_APPROVED'][0].update(human_claim_review='approved')),
    (2,lambda x:x['rows_NOT_APPROVED'][0]['citation_neighborhood_review_NOT_APPROVED'].update(may_publish=True)),
    (3,lambda x:x.update(release_state='PASS')),
    (3,lambda x:x.update(may_publish=True)),
    (3,lambda x:x.update(changed_body_review_count=8)),
    (3,lambda x:x.update(qualified_emergency_safety_approved=True)),
    (3,lambda x:x['rows_NOT_APPROVED'].pop()),
    (3,lambda x:x['rows_NOT_APPROVED'][0].update(observed_oid='f'*40)),
    (3,lambda x:x['rows_NOT_APPROVED'][0].update(human_source_review='approved')),
    (3,lambda x:x['rows_NOT_APPROVED'][0]['cross_paragraph_review_NOT_APPROVED'].update(may_publish=True)),
    (4,lambda x:x.update(may_merge=True)),
    (4,lambda x:x.update(may_publish=True)),
    (4,lambda x:x.update(original_article_drafts=34)),
    (4,lambda x:x.update(actual_buildable_tools=2)),
    (4,lambda x:x.update(additional_planned_tools_not_buildable=4)),
    (4,lambda x:x.update(literal_url_collision_groups_pending_human_review=29)),
    (4,lambda x:x.update(source_claim_support_review='APPROVED')),
    (4,lambda x:x.update(qualified_safety_review='APPROVED')),
    (4,lambda x:x.update(independent_QD='PASS')),
    (4,lambda x:x['groups'].pop()),
    (4,lambda x:x['groups'][0].update(human_review='APPROVED')),
    (4,lambda x:x['groups'][0].update(same_url_is_not_shared_claim_authority=False)),
    (4,lambda x:x['groups'][0].update(variant_count=1)),
    (4,lambda x:x['groups'][0]['variants'].pop()),
    (4,lambda x:x['groups'][0]['author_bound_citation_contexts'][0].update(source_id_as_authored='wrong')),
    (4,lambda x:x['groups'][0]['author_bound_citation_contexts'][0].update(author_scoped_source_use='')),
    (4,lambda x:x['groups'][0].update(citing_articles=['different-article'])),
    (4,lambda x:x.update(collision_citation_occurrences=29)),
    (4,lambda x:x['groups'][1].update(literal_url=x['groups'][0]['literal_url'])),
    (4,lambda x:x['groups'][0]['variants'][1].update(source_id=x['groups'][0]['variants'][0]['source_id'],origin='start')),
]

def make_mutation_test(num,index,fun):
    def test(self):
        self.assert_rejected(lambda rec:fun(rec[index]))
    test.__name__='test_reseal_adversary_%02d'%num
    return test

for number,(index,fn) in enumerate(MUTATIONS,1):
    setattr(Adversarial,'test_reseal_adversary_%02d'%number,make_mutation_test(number,index,fn))

class Integrity(unittest.TestCase):
    def test_modified_unsealed_R107(self):
        rows=list(fixture());rows[0]['may_publish']=True
        with self.assertRaises(g.Hold):g.compose(*rows)
    def test_parent_linkage_mutation(self):
        rows=list(fixture());rows[2]['R108_sha256_NOT_A_SIGNATURE']='0'*64
        seal(rows[2],'sha256_NOT_A_SIGNATURE')
        with self.assertRaises(g.Hold):g.compose(*rows)
    def test_parent_linkage_R110(self):
        rows=list(fixture());rows[3]['R109_sha256_NOT_A_SIGNATURE']='0'*64
        seal(rows[3],'sha256_NOT_A_SIGNATURE')
        with self.assertRaises(g.Hold):g.compose(*rows)
    def test_parent_linkage_R108(self):
        rows=list(fixture());rows[1]['R107_queue_sha256_NOT_A_SIGNATURE']='0'*64
        seal(rows[1],'sha256_NOT_A_SIGNATURE')
        with self.assertRaises(g.Hold):g.compose(*rows)
    def test_document_has_no_network_or_cms_calls(self):
        src=SRC.read_text()
        self.assertNotIn('requests.',src)
        self.assertNotIn('urllib.request',src)
        self.assertNotIn('wp-json',src)
        self.assertNotIn('post(',src)

if __name__=='__main__':unittest.main()
