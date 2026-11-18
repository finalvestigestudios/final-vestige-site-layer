"""R447 synthetic attack/acceptance tests; no external safety or sales approval."""
from __future__ import annotations
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1]/'tools'/'r447_adjudication_proposal_guard.py'
spec = importlib.util.spec_from_file_location('r447', SCRIPT)
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


def fixture():
    pins = [{'branch': f'claude/prep-{n}', 'sha': f'{n:040x}'} for n in range(9)]
    articles = [{'slug': f'original-article-{n}', 'body_candidate_git_blobs':[f'{n+500:040x}']} for n in range(35)]
    src = [{'source_id': k, 'original_decision': 'HUMAN_REVIEW_REQUIRED',
            'proposed_selection': None, 'reviewer':None, 'review_evidence':None, 'qualified_safety_approved':False, 'source_variants': [
             {'branch': pins[j]['branch'], 'source_blob':f'{i*5+j+100:040x}',
              'url':f'https://www.example.gov/source/{i}', 'supports_exact':f'claim {i}-{j}',
              'reading_scope_notes_exact':f'read pages {j}'} for j in range(2)]}
           for i,k in enumerate(['fsis-power-failure','loc-pioneer-diaries','loc-prairie-traveler',
                                 'nchfp-home','nchfp-jerky'])]
    forks = [{'path':f'preparedness/articles/fork-{i}.md', 'original_decision':'HUMAN_REVIEW_REQUIRED',
              'proposed_selection': None, 'reviewer':None, 'review_evidence':None, 'qualified_safety_approved':False, 'original_variants':[
                 {'branch':pins[j]['branch'],'body_blob':f'{i*3+j+1000:040x}'} for j in range(2)]}
             for i in range(9)]
    groups = [{'url':f'https://www.example.gov/group/{i}', 'source_ids':[f'id-{i}',f'ID-{i}'],
               'decision':'UNSELECTED','merge_authorized':False} for i in range(17)]
    p={'schema':'R446_ORIGINAL_ADJUDICATION_REVIEW_ONLY_v1','release_state':r.STATE,
       'issue':136,'business_coordination_issue':820,'original_docket':{'git_blob':r.ORIGINAL_BLOB},
       'qualified_review_approved':False,'publishable':False,'safety_approved':False,
       'merchant_offer_verified':False,'article_identities':articles, 'source_scope_review':src,
       'manuscript_fork_review':forks,'duplicate_exact_url_review':groups,'branch_pins':pins}
    return p, {x['branch']:x['sha'] for x in pins}


def check(packet=None, draft=None, heads=None):
    p,h = fixture()
    p=packet if packet is not None else p
    if heads is not None: h=heads
    if draft is None: draft=r.template(p)
    raw=r.canonical(p).encode()
    original = r.PACKET_BLOB
    try:
        r.PACKET_BLOB=r.git_blob(raw)
        draft['packet_git_blob']=r.PACKET_BLOB
        return r.assess(p,draft,raw,h)
    finally:
        r.PACKET_BLOB=original


class Baseline(unittest.TestCase):
    def test_clean_synthetic_structure_not_a_release(self):
        x=check()
        self.assertTrue(x['structural_evidence_pass'],x['errors'])
        self.assertEqual(x['unselected'],{'sources':5,'forks':9,'shared_url_groups':17})
        self.assertEqual(x['release_state'],'DRAFT_HARD_HOLD')
        self.assertFalse(x['qd_pass'])
        self.assertFalse(x['verified_paid_offer'])
        self.assertFalse(x['publishable'])
    def test_template_is_deterministic(self):
        p,_=fixture()
        self.assertEqual(r.canonical(r.template(p)),r.canonical(r.template(copy.deepcopy(p))))
    def test_source_candidate_hashes_are_distinct(self):
        x=check()
        self.assertEqual(len(x['source_variant_candidates_by_id']),5)
        self.assertTrue(all(len(set(v))==2 for v in x['source_variant_candidates_by_id'].values()))
    def test_fork_candidate_hashes_are_distinct(self):
        x=check()
        self.assertEqual(len(x['fork_variant_candidates_by_path']),9)
        self.assertTrue(all(len(set(v))==2 for v in x['fork_variant_candidates_by_path'].values()))
    def test_authentic_pin_rejects_unpinned_fixture(self):
        p,h=fixture()
        x=r.assess(p,r.template(p),r.canonical(p).encode(),h)
        self.assertIn('AUTHENTIC_PACKET_BLOB_NOT_PROVEN',x['errors'])
    def test_missing_heads_is_hold(self):
        x=check(heads={})
        self.assertIn('CURRENT_NINE_HEADS_NOT_PROVEN',x['errors'])
    def test_source_proposal_remains_hold(self):
        p,h=fixture(); d=r.template(p); item=d['sources'][0]
        item['candidate_digest']=r.digest(p['source_scope_review'][0]['source_variants'][0]); item['reviewer']='Qualified reviewer'
        item['evidence_urls']=['https://example.gov/records']; item['reading_scope_confirmation']='Read complete source, pages and revision checked'; item['safety_review_note']='Scope is limited; requires separate food-safety signoff'
        x=check(p,d,h)
        self.assertTrue(x['structural_evidence_pass'],x['errors'])
        self.assertEqual(x['proposals_documented_not_approved']['sources'],1)
        self.assertFalse(x['qd_pass']);self.assertFalse(x['publishable'])
    def test_fork_proposal_remains_hold(self):
        p,h=fixture(); d=r.template(p); item=d['forks'][0]
        item['candidate_digest']=r.digest(p['manuscript_fork_review'][0]['original_variants'][0]); item['reviewer']='History evidence reviewer'
        item['evidence_urls']=['https://example.gov/records']; item['reading_depth_confirmation']='Compared both manuscripts line by line and preserved depth'; item['citations_confirmation']='Every substantial claim and citation requires qualified verification'
        x=check(p,d,h)
        self.assertTrue(x['structural_evidence_pass'],x['errors'])
        self.assertEqual(x['unselected']['forks'],8)
        self.assertFalse(x['qd_pass'])
    def test_distinct_url_identity_proposal_remains_hold(self):
        p,h=fixture(); d=r.template(p); item=d['url_groups'][0]
        item['decision']='KEEP_DISTINCT_PROPOSED'; item['reviewer']='Source trace reviewer'
        item['evidence_urls']=['https://example.gov/records']; item['notes']='Two source IDs reference same URL but different claims and scopes'
        x=check(p,d,h)
        self.assertTrue(x['structural_evidence_pass'],x['errors'])
        self.assertEqual(x['unselected']['shared_url_groups'],16)
        self.assertFalse(x['qd_pass'])
    def test_no_implicit_merge(self):
        p,_=fixture();d=r.template(p);d['url_groups'][0]['decision']='MERGE'
        self.assertIn('UNAPPROVED_URL_ID_MERGE_OR_DECISION',check(p,d)['errors'])
    def test_missing_doc_is_hold(self):
        self.assertFalse(r.assess(None,None)['publishable'])
    def test_human_link_cannot_be_http(self):
        self.assertFalse(r.safe_https('http://example.gov/records'))
    def test_human_link_cannot_be_javascript(self):
        self.assertFalse(r.safe_https('javascript:alert(1)'))
    def test_credentials_in_url_rejected(self):
        self.assertFalse(r.safe_https('https://admin:pw@example.gov/path'))
    def test_unscoped_fragments_rejected(self):
        self.assertFalse(r.safe_https('https://example.gov/#review'))
    def test_unicode_whitespace_in_url_rejected(self):
        self.assertFalse(r.safe_https('https://example.gov/with\nline'))
    def test_duplicate_json_keys_rejected(self):
        with self.assertRaises(ValueError):json.loads('{"a":1,"a":2}',object_pairs_hook=r.unique_object)
    def test_dict_order_does_not_change_source_hash(self):
        self.assertEqual(r.digest({'b':2,'a':1}),r.digest({'a':1,'b':2}))
    def test_candidate_text_mutation_changes_hash(self):
        v={'supports_exact':'true','reading_scope_notes_exact':'read whole'}
        self.assertNotEqual(r.digest(v),r.digest(dict(v, supports_exact='false')))
    def test_missing_original_blob_is_hold(self):
        p,h=fixture(); d=r.template(p)
        self.assertIn('AUTHENTIC_PACKET_BLOB_NOT_PROVEN',r.assess(p,d,None,h)['errors'])


# Independent mutation cases: each dynamically installed test is a distinct
# reproducible tampering scenario and must fail structurally, not become a PASS.
ATTACKS = {
 'erase_article':lambda p,d,h: p['article_identities'].pop(),
 'duplicate_slug':lambda p,d,h: p['article_identities'][1].update(slug=p['article_identities'][0]['slug']),
 'erase_source':lambda p,d,h: p['source_scope_review'].pop(),
 'erase_fork':lambda p,d,h: p['manuscript_fork_review'].pop(),
 'erase_url_group':lambda p,d,h: p['duplicate_exact_url_review'].pop(),
 'erase_branch':lambda p,d,h: p['branch_pins'].pop(),
 'swap_issue':lambda p,d,h: p.update(issue=999),
 'swap_commerce_issue':lambda p,d,h: p.update(business_coordination_issue=999),
 'change_docket_pin':lambda p,d,h: p['original_docket'].update(git_blob='deadbeef'),
 'change_packet_schema':lambda p,d,h: p.update(schema='LIVE'),
 'change_packet_release':lambda p,d,h: p.update(release_state='APPROVED'),
 'change_packet_qd':lambda p,d,h: p.update(qualified_review_approved=True),
 'change_packet_publishable':lambda p,d,h: p.update(publishable=True),
 'change_packet_safety':lambda p,d,h: p.update(safety_approved=True),
 'change_packet_merchant':lambda p,d,h: p.update(merchant_offer_verified=True),
 'change_proposal_schema':lambda p,d,h: d.update(schema='APPROVED'),
 'change_proposal_release':lambda p,d,h: d.update(release_state='APPROVED'),
 'change_proposal_qd':lambda p,d,h: d.update(qualified_review_approved=True),
 'change_proposal_publishable':lambda p,d,h: d.update(publishable=True),
 'change_proposal_safety':lambda p,d,h: d.update(safety_approved=True),
 'change_proposal_merchant':lambda p,d,h: d.update(merchant_offer_verified=True),
 'erase_proposed_source':lambda p,d,h: d['sources'].pop(),
 'duplicate_source_identity':lambda p,d,h: d['sources'][1].update(source_id=d['sources'][0]['source_id']),
 'fabricate_source_identity':lambda p,d,h: d['sources'][0].update(source_id='fake-source'),
 'erase_proposed_fork':lambda p,d,h: d['forks'].pop(),
 'duplicate_fork_identity':lambda p,d,h: d['forks'][1].update(path=d['forks'][0]['path']),
 'fabricate_fork_path':lambda p,d,h: d['forks'][0].update(path='fake.md'),
 'erase_proposed_url':lambda p,d,h: d['url_groups'].pop(),
 'duplicate_url_identity':lambda p,d,h: d['url_groups'][1].update(url=d['url_groups'][0]['url']),
 'fabricate_url_identity':lambda p,d,h: d['url_groups'][0].update(url='https://bad.example/new'),
 'source_candidate_not_original':lambda p,d,h: d['sources'][0].update(candidate_digest='a'*64),
 'fork_candidate_not_original':lambda p,d,h: d['forks'][0].update(candidate_digest='b'*64),
 'source_claim_without_reviewer':lambda p,d,h: d['sources'][0].update(candidate_digest=r.digest(p['source_scope_review'][0]['source_variants'][0])),
 'fork_claim_without_evidence':lambda p,d,h: d['forks'][0].update(candidate_digest=r.digest(p['manuscript_fork_review'][0]['original_variants'][0])),
 'claim_extra_authority_key':lambda p,d,h: d['sources'][0].update(approved=True),
 'fork_extra_authority_key':lambda p,d,h: d['forks'][0].update(approved=True),
 'url_extra_authority_key':lambda p,d,h: d['url_groups'][0].update(approved=True),
 'source_ghost_reviewer':lambda p,d,h: d['sources'][0].update(reviewer='No one'),
 'fork_ghost_evidence':lambda p,d,h: d['forks'][0].update(evidence_urls=['https://example.gov']),
 'url_ghost_reviewer':lambda p,d,h: d['url_groups'][0].update(reviewer='No one'),
 'url_merge_request':lambda p,d,h: d['url_groups'][0].update(decision='MERGE_PROPOSED'),
 'url_false_approved':lambda p,d,h: d['url_groups'][0].update(decision='APPROVED'),
 'url_false_release':lambda p,d,h: p['duplicate_exact_url_review'][0].update(merge_authorized=True),
 'source_false_preset':lambda p,d,h: p['source_scope_review'][0].update(proposed_selection='source'),
 'fork_false_preset':lambda p,d,h: p['manuscript_fork_review'][0].update(proposed_selection='body'),
 'observed_head_mismatch':lambda p,d,h: h.update({p['branch_pins'][0]['branch']:'badsha'}),
 'source_unspecified_scope':lambda p,d,h: d['sources'][0].update(candidate_digest=r.digest(p['source_scope_review'][0]['source_variants'][0]),reviewer='Researcher',evidence_urls=['https://example.gov'],reading_scope_confirmation='Short',safety_review_note='Short'),
 'fork_unspecified_scope':lambda p,d,h: d['forks'][0].update(candidate_digest=r.digest(p['manuscript_fork_review'][0]['original_variants'][0]),reviewer='Researcher',evidence_urls=['https://example.gov'],reading_depth_confirmation='Short',citations_confirmation='Short'),
 'url_unsubstantiated':lambda p,d,h: d['url_groups'][0].update(decision='KEEP_DISTINCT_PROPOSED'),
 'source_blank_review_note':lambda p,d,h: d['sources'][0].update(safety_review_note='not read'),
 'fork_blank_citation_note':lambda p,d,h: d['forks'][0].update(citations_confirmation='not read'),
}

class Mutations(unittest.TestCase):
    pass


def install_case(name, attack):
    def test(self):
        p,h=fixture();d=r.template(p)
        attack(p,d,h)
        result=check(p,d,h)
        self.assertFalse(result['structural_evidence_pass'],name)
        self.assertTrue(result['errors'],name)
        self.assertEqual(result['release_state'],r.STATE)
        self.assertFalse(result['publishable'])
        self.assertFalse(result['qd_pass'])
    return test

for label, mutation in ATTACKS.items():
    setattr(Mutations, 'test_reject_'+label, install_case(label, mutation))


if __name__=='__main__':
    unittest.main()
