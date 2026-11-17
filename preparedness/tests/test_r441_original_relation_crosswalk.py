"""R441 adversarial original R397 relational custody tests; review-only, no publication."""
from __future__ import annotations
import copy
import unittest
from test_r440_original_slate_evidence_replay import g, fake_docket

def fixture():
    d=fake_docket()
    d['original_git_blob_pins']={name:str(i)*40 for i,name in enumerate(
        ('manifest','source_fragment_crosswalk','base_source_register'),start=4)}
    branches=[r['branch'] for r in d['branch_pins']]
    cross=d['all_original_source_id_crosswalk']
    for i,x in enumerate(cross):
        x['variants'][0]['url']=f'https://agency.example/source-{i//2 if i<34 else i}'
        if i<77:
            x['variants'].append({'branch':branches[1], 'source_blob':f'{i+100:040x}',
                                  'url':x['variants'][0]['url']})
    d['shared_exact_url_review_groups']=[{'url':f'https://agency.example/source-{i}',
       'ids':[f'source-{2*i}',f'source-{2*i+1}'],'review_required':True} for i in range(17)]
    for i,p in enumerate(d['source_evidence_disputes']):
        p['variants']=[dict(v,supports_exact='Original scoped claim',
                            reading_scope_notes_exact='Exact source read') for v in cross[i]['variants']]
    forks=[]
    for i in range(4):
        slug=f'article-{i}'
        variants=[{'branch':branches[j],
           'git_blob_sha':f'{400+i*20+j if i!=1 or j!=2 else 400+i*20+1:040x}',
           'byte_length':100+j} for j in range(3)]
        d['original_articles'][i]['body_candidate_git_blobs']=[v['git_blob_sha'] for v in variants]
        forks.append({'path':f'preparedness/content/articles/{slug}.body.html',
                      'decision':'HUMAN_REVIEW_REQUIRED','selected_sha':None,'variants':variants})
        forks.append({'path':f'preparedness/content/articles/{slug}.meta.json',
                      'decision':'HUMAN_REVIEW_REQUIRED','selected_sha':None,
                      'variants':[{'branch':branches[j],'git_blob_sha':f'{500+i*10+j:040x}',
                                   'byte_length':200+j} for j in range(2)]})
    forks.append({'path':'preparedness/sources/fragments/shelter.json',
                  'decision':'HUMAN_REVIEW_REQUIRED','selected_sha':None,
                  'variants':[{'branch':branches[j], 'git_blob_sha':f'{600+j:040x}',
                               'byte_length':300+j} for j in range(2)]})
    d['original_fork_disputes']=forks
    return d

class Custody(unittest.TestCase):
    def setUp(self):self.d=fixture()
    def errors(self):return g.inspect_original_relationships(self.d)
    def test_valid_fixture(self):self.assertEqual([],self.errors())
    def test_deterministic(self):self.assertEqual(self.errors(),g.inspect_original_relationships(copy.deepcopy(self.d)))
    def test_equal_blob_different_branch_is_valid(self):
        a=self.d['original_articles'][1]['body_candidate_git_blobs']
        self.assertEqual((3,2),(len(a),len(set(a))))
        self.assertEqual([],self.errors())
        self.assertFalse(any('INVALID_ORIGINAL_BODY_OBJECTS' in e for e in g.inspect_docket(self.d)))
    def test_280_occurrences(self):self.assertEqual(280,sum(len(x['variants']) for x in self.d['all_original_source_id_crosswalk']))
    def test_17_groups(self):self.assertEqual(17,len(self.d['shared_exact_url_review_groups']))
    def test_5_disputes(self):self.assertEqual(5,len(self.d['source_evidence_disputes']))
    def test_9_forks(self):self.assertEqual(9,len(self.d['original_fork_disputes']))
    def test_35_articles(self):self.assertEqual(35,len(self.d['original_articles']))
    def test_hard_hold_always(self):
        r=g.audit(self.d)
        for key in ('eligible','publication_approved','qualified_safety_approved','merchant_offer_verified'):
            self.assertIs(r[key],False)
    def test_no_checkout_is_blocker(self):self.assertIn('AUTHENTIC_CHECKOUT_NOT_PROVIDED',g.audit(self.d)['errors'])
    def test_invalid_docket_type(self):self.assertIn('RELATION_INVALID_DOCKET',g.inspect_original_relationships(None))
    def test_missing_relations(self):self.assertIn('RELATION_MISSING_ORIGINAL_SETS',g.inspect_original_relationships({}))

def add_case(name,mutate,error):
    def test(self):
        mutate(self.d)
        messages=self.errors()
        self.assertTrue(any(error in e for e in messages),
                        f'{name}: expected {error}; received {messages}')
    setattr(Custody,'test_'+name,test)

CASES=[
 ('manifest_pin_missing',lambda d:d['original_git_blob_pins'].pop('manifest'),'ORIGINAL_INPUT_GIT_PINS_LOST'),
 ('base_pin_missing',lambda d:d['original_git_blob_pins'].pop('base_source_register'),'ORIGINAL_INPUT_GIT_PINS_LOST'),
 ('fragment_pin_missing',lambda d:d['original_git_blob_pins'].pop('source_fragment_crosswalk'),'ORIGINAL_INPUT_GIT_PINS_LOST'),
 ('extra_pin',lambda d:d['original_git_blob_pins'].__setitem__('fourth','f'*40),'ORIGINAL_INPUT_GIT_PINS_LOST'),
 ('bad_pin',lambda d:d['original_git_blob_pins'].__setitem__('manifest','bad'),'ORIGINAL_INPUT_GIT_PINS_LOST'),
 ('bad_pin_type',lambda d:d.__setitem__('original_git_blob_pins',None),'ORIGINAL_INPUT_GIT_PINS_LOST'),
 ('body_fork_unknown',lambda d:d['original_fork_disputes'][0].__setitem__('path','preparedness/content/articles/missing.body.html'),'BODY_FORK_ARTICLE_IDENTITY_LOST'),
 ('body_fork_sha_changed',lambda d:d['original_fork_disputes'][0]['variants'][0].__setitem__('git_blob_sha','f'*40),'BODY_FORK_PROVENANCE_MULTIPLICITY_DRIFT'),
 ('body_fork_article_sha_removed',lambda d:d['original_articles'][0]['body_candidate_git_blobs'].pop(),'BODY_FORK_PROVENANCE_MULTIPLICITY_DRIFT'),
 ('body_fork_candidate_repeated',lambda d:d['original_articles'][0]['body_candidate_git_blobs'].append('a'*40),'BODY_FORK_PROVENANCE_MULTIPLICITY_DRIFT'),
 ('body_fork_variant_removed',lambda d:d['original_fork_disputes'][0]['variants'].pop(),'BODY_FORK_PROVENANCE_MULTIPLICITY_DRIFT'),
 ('body_fork_branch_duplicate',lambda d:d['original_fork_disputes'][0]['variants'][1].__setitem__('branch',d['original_fork_disputes'][0]['variants'][0]['branch']),'BODY_FORK_BRANCH_COLLISION'),
 ('body_fork_unpinned',lambda d:d['original_fork_disputes'][0]['variants'][1].__setitem__('branch','unknown'),'BODY_FORK_BRANCH_NOT_PINNED'),
 ('body_fork_removed',lambda d:d['original_fork_disputes'].pop(0),'FOUR_ORIGINAL_BODY_FORKS_CHANGED'),
 ('body_fork_duplicated',lambda d:d['original_fork_disputes'].append(copy.deepcopy(d['original_fork_disputes'][0])),'RELATION_FORK_PATH_COLLISION'),
 ('body_fork_variants_bad_type',lambda d:d['original_fork_disputes'][0].__setitem__('variants',None),'BODY_FORK_CANDIDATE_SET_MISSING'),
 ('body_fork_variant_bad_row',lambda d:d['original_fork_disputes'][0]['variants'].__setitem__(0,None),'BODY_FORK_INVALID_VARIANT'),
 ('crosswalk_row_removed',lambda d:d['all_original_source_id_crosswalk'].pop(),'CROSSWALK_VARIANT_OCCURRENCE_DRIFT'),
 ('crosswalk_variant_removed',lambda d:d['all_original_source_id_crosswalk'][0]['variants'].pop(),'CROSSWALK_VARIANT_OCCURRENCE_DRIFT'),
 ('crosswalk_variant_added',lambda d:d['all_original_source_id_crosswalk'][99]['variants'].append(dict(d['all_original_source_id_crosswalk'][99]['variants'][0],branch=d['branch_pins'][2]['branch'])),'CROSSWALK_VARIANT_OCCURRENCE_DRIFT'),
 ('crosswalk_source_id_collision',lambda d:d['all_original_source_id_crosswalk'][100].__setitem__('source_id','source-99'),'RELATION_SOURCE_ID_COLLISION'),
 ('crosswalk_empty_variants',lambda d:d['all_original_source_id_crosswalk'][100].__setitem__('variants',[]),'RELATION_SOURCE_VARIANTS_MISSING'),
 ('crosswalk_bad_source_row',lambda d:d['all_original_source_id_crosswalk'].__setitem__(100,None),'RELATION_INVALID_SOURCE_ROW'),
 ('crosswalk_bad_sha',lambda d:d['all_original_source_id_crosswalk'][99]['variants'][0].__setitem__('source_blob','bad'),'SOURCE_VARIANT_INVALID_GIT_BLOB'),
 ('crosswalk_branch_collision',lambda d:d['all_original_source_id_crosswalk'][0]['variants'][1].__setitem__('branch',d['branch_pins'][0]['branch']),'SOURCE_VARIANT_BRANCH_COLLISION'),
 ('crosswalk_branch_unpinned',lambda d:d['all_original_source_id_crosswalk'][99]['variants'][0].__setitem__('branch','unknown'),'SOURCE_VARIANT_UNPINNED_BRANCH'),
 ('crosswalk_bad_variant_row',lambda d:d['all_original_source_id_crosswalk'][99]['variants'].__setitem__(0,None),'RELATION_SOURCE_VARIANT_INVALID'),
 ('crosswalk_null_url',lambda d:d['all_original_source_id_crosswalk'][99]['variants'][0].__setitem__('url',None),'SOURCE_VARIANT_INVALID_URL'),
 ('crosswalk_http_url',lambda d:d['all_original_source_id_crosswalk'][99]['variants'][0].__setitem__('url','http://agency.example/a'),'SOURCE_VARIANT_UNSAFE_URL'),
 ('crosswalk_script_url',lambda d:d['all_original_source_id_crosswalk'][99]['variants'][0].__setitem__('url','javascript:alert(1)'),'SOURCE_VARIANT_UNSAFE_URL'),
 ('crosswalk_credentials_url',lambda d:d['all_original_source_id_crosswalk'][99]['variants'][0].__setitem__('url','https://a:b@agency.example/a'),'SOURCE_VARIANT_UNSAFE_URL'),
 ('crosswalk_fragment_url',lambda d:d['all_original_source_id_crosswalk'][99]['variants'][0].__setitem__('url','https://agency.example/a#frag'),'SOURCE_VARIANT_UNSAFE_URL'),
 ('crosswalk_control_url',lambda d:d['all_original_source_id_crosswalk'][99]['variants'][0].__setitem__('url','https://agency.example/\na'),'SOURCE_VARIANT_UNSAFE_URL'),
 ('shared_group_removed',lambda d:d['shared_exact_url_review_groups'].pop(),'INFERRED_SHARED_URL_GROUP_SET_DRIFT'),
 ('shared_group_added',lambda d:d['shared_exact_url_review_groups'].append({'url':'https://other.example','ids':['source-1','source-2'],'review_required':True}),'INFERRED_SHARED_URL_GROUP_SET_DRIFT'),
 ('shared_group_wrong_ids',lambda d:d['shared_exact_url_review_groups'][0].__setitem__('ids',['source-0','source-2']),'INFERRED_SHARED_URL_SOURCE_IDS_DRIFT'),
 ('shared_group_duplicate_ids',lambda d:d['shared_exact_url_review_groups'][0].__setitem__('ids',['source-0','source-0']),'RELATION_GROUP_REVIEW_OR_ID_COLLISION'),
 ('shared_group_review_omitted',lambda d:d['shared_exact_url_review_groups'][0].__setitem__('review_required',False),'RELATION_GROUP_REVIEW_OR_ID_COLLISION'),
 ('shared_group_duplicate_row',lambda d:d['shared_exact_url_review_groups'].append(copy.deepcopy(d['shared_exact_url_review_groups'][0])),'RELATION_DUPLICATE_SHARED_URL'),
 ('shared_group_invalid_ids',lambda d:d['shared_exact_url_review_groups'][0].__setitem__('ids','source-0'),'RELATION_INVALID_GROUP_IDS'),
 ('shared_group_invalid_row',lambda d:d['shared_exact_url_review_groups'].__setitem__(0,None),'RELATION_INVALID_SHARED_URL_ROW'),
 ('dispute_unknown_id',lambda d:d['source_evidence_disputes'][0].__setitem__('source_id','unknown'),'DISPUTED_ID_NOT_IN_SOURCE_CROSSWALK'),
 ('dispute_wrong_branch',lambda d:d['source_evidence_disputes'][0]['variants'][0].__setitem__('branch','unknown'),'SOURCE_DISPUTE_TO_CROSSWALK_DRIFT'),
 ('dispute_wrong_sha',lambda d:d['source_evidence_disputes'][0]['variants'][0].__setitem__('source_blob','f'*40),'SOURCE_DISPUTE_TO_CROSSWALK_DRIFT'),
 ('dispute_wrong_url',lambda d:d['source_evidence_disputes'][0]['variants'][0].__setitem__('url','https://other.example'),'SOURCE_DISPUTE_TO_CROSSWALK_DRIFT'),
 ('dispute_variant_removed',lambda d:d['source_evidence_disputes'][0]['variants'].pop(),'SOURCE_DISPUTE_TO_CROSSWALK_DRIFT'),
 ('dispute_auto_selected',lambda d:d['source_evidence_disputes'][0].__setitem__('selected_record','x'),'SOURCE_DISPUTE_PREMATURE_SELECTION'),
 ('dispute_status_pass',lambda d:d['source_evidence_disputes'][0].__setitem__('decision','PASS'),'SOURCE_DISPUTE_PREMATURE_SELECTION'),
 ('dispute_notes_removed',lambda d:d['source_evidence_disputes'][0]['variants'][0].__setitem__('reading_scope_notes_exact',''),'SOURCE_DISPUTE_READING_SCOPE_MISSING'),
 ('dispute_support_removed',lambda d:d['source_evidence_disputes'][0]['variants'][0].__setitem__('supports_exact',''),'SOURCE_DISPUTE_READING_SCOPE_MISSING'),
]
for case in CASES:
    add_case(*case)
