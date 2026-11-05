"""R138 standalone synthetic/adversarial tests: not real article safety QA."""
from __future__ import annotations
import copy
import importlib.util
from pathlib import Path
import unittest

TOOL = Path(__file__).resolve().parents[1] / 'tools' / 'r138_cross_lane_reconciliation.py'
spec = importlib.util.spec_from_file_location('r138_cross_lane_reconciliation', TOOL)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def fixture():
    """Deliberately make R135 and R137 group index order different."""
    slugs = [f'article-{n:02d}' for n in range(35)]
    articles = [{'slug': s, 'status': 'DRAFT_HOLD',
                 'citation_occurrences': 58 if i < 5 else 57} for i, s in enumerate(slugs)]
    dossiers, tasks = [], []
    for i in range(32):
        scope_index = 32 - i
        slug = slugs[i]
        url = f'https://example.org/g/{i:02d}'
        var_a = {'origin': 'food', 'id': f'food-{i:02d}',
                 'literal_url': url, 'source_file': 'preparedness/sources/fragments/food.json',
                 'article_reading_scopes': [
                     {'article_slug': slug, 'citation_id': f'food-{i:02d}',
                      'literal_url': url, 'author_reading_scope': 'Synthetic author specific scope',
                      'citation_occurrences': i + 1}],
                 'uncited_variant_not_an_approval': False}
        var_b = {'origin': 'base', 'id': f'base-{i:02d}',
                 'literal_url': url, 'source_file': 'preparedness/sources/register.json',
                 'article_reading_scopes': [], 'uncited_variant_not_an_approval': True}
        dossiers.append({'group_index': scope_index, 'review_alias': url,
                         'status': 'UNREVIEWED_HUMAN_REQUIRED', 'witness_sha256': 'a'*64,
                         'variants': [var_a, var_b]})
        tasks.append({'task_id': 'SOURCE-'+f'{i+1:020x}',
                      'crosswalk_group_index': i + 1,
                      'decision': 'UNREVIEWED_HUMAN_REQUIRED',
                      'cited_variant_identities_only': [['food', f'food-{i:02d}', url]],
                      'citation_occurrences': i+1, 'affected_articles': [slug]})
    queue = {'status': 'HOLD_HUMAN_SOURCE_AND_SAFETY_ADJUDICATION',
             'may_publish': False, 'qd_pass': False, 'medical_safety_verified': False,
             'merchant_offer_verified': False,
             'provenance': {'candidate_parent': 'synthetic-candidate', 'article_count': 35,
                            'citation_occurrences': 2000},
             'summary': {'crosswalk_groups_requiring_human_review': 32,
                         'risk_passages_requiring_human_review': 1},
             'source_group_tasks': tasks,
             'safety_passage_tasks': [{'task_id':'PASSAGE-'+'a'*20,
                                      'decision':'UNREVIEWED_HUMAN_REQUIRED'}]}
    scope = {'status': 'HOLD_QUALIFIED_SOURCE_AND_SAFETY_REVIEW_REQUIRED',
             'may_publish': False, 'qd_pass': False, 'medical_safety_verified': False,
             'merchant_offer_verified': False,
             'candidate_parent': 'synthetic-candidate',
             'stats': {'articles':35, 'citations':2000, 'shared_groups':32,
                       'source_rows':244, 'frozen_files':80,
                       'literal_source_urls':202, 'review_aliases':201},
             'articles': articles, 'source_group_dossiers': dossiers}
    return queue, scope


class R138SuccessfulJoin(unittest.TestCase):
    def setUp(self):
        self.q, self.d = fixture()

    def test_order_mismatch_is_not_false_integrity_error(self):
        out = m.reconcile(self.q, self.d)
        self.assertEqual(out['stats']['r135_r137_group_indices_differ'], 32)
        self.assertEqual(out['stats']['shared_groups_joined'], 32)
        self.assertEqual(out['stats']['cited_group_occurrences'], sum(range(1,33)))

    def test_source_approval_never_inferred(self):
        out = m.reconcile(self.q, self.d)
        self.assertFalse(out['may_publish'])
        self.assertFalse(out['qd_pass'])
        self.assertFalse(out['medical_safety_verified'])
        self.assertFalse(out['merchant_offer_verified'])
        self.assertFalse(out['source_agreement_inferred'])
        self.assertFalse(out['human_source_review_complete'])

    def test_input_fingerprints_deterministic(self):
        a, b = m.reconcile(self.q, self.d), m.reconcile(self.q, self.d)
        self.assertEqual(a, b)
        self.assertEqual(len(a['input_queue_sha256']), 64)

    def test_article_order_does_not_affect_roster_acceptance(self):
        self.d['articles'].reverse()
        self.assertEqual(len(m.reconcile(self.q, self.d)['group_index_crosswalk']),32)

    def test_dossier_and_task_order_nonsemantic(self):
        self.d['source_group_dossiers'].reverse()
        self.q['source_group_tasks'].reverse()
        self.assertEqual(len(m.reconcile(self.q, self.d)['group_index_crosswalk']),32)


class R138Adversarial(unittest.TestCase):
    def setUp(self):
        self.q, self.d = fixture()

    def assert_hold(self):
        with self.assertRaises(m.ReconciliationHold):
            m.reconcile(self.q, self.d)

    def test_no_queue(self):
        self.q = None; self.assert_hold()

    def test_no_scope(self):
        self.d = None; self.assert_hold()

    def test_unknown_queue_hold(self):
        self.q['status'] = 'QD_PASS'; self.assert_hold()

    def test_unknown_scope_hold(self):
        self.d['status'] = 'RELEASED'; self.assert_hold()

    def test_candidate_mismatch(self):
        self.d['candidate_parent'] = 'other'; self.assert_hold()

    def test_source_rows_drift(self):
        self.d['stats']['source_rows'] = 243; self.assert_hold()

    def test_80_blobs_drift(self):
        self.d['stats']['frozen_files'] = 79; self.assert_hold()

    def test_202_literal_urls_drift(self):
        self.d['stats']['literal_source_urls'] = 201; self.assert_hold()

    def test_201_aliases_drift(self):
        self.d['stats']['review_aliases'] = 202; self.assert_hold()

    def test_2000_citation_drift(self):
        self.q['provenance']['citation_occurrences'] = 1999; self.assert_hold()

    def test_35_article_drift(self):
        self.q['provenance']['article_count'] = 34; self.assert_hold()

    def test_32_group_drift(self):
        self.q['summary']['crosswalk_groups_requiring_human_review'] = 31; self.assert_hold()

    def test_missing_source_group(self):
        self.d['source_group_dossiers'].pop(); self.assert_hold()

    def test_missing_queue_task(self):
        self.q['source_group_tasks'].pop(); self.assert_hold()

    def test_missing_variant(self):
        self.d['source_group_dossiers'][0]['variants'].pop(); self.assert_hold()

    def test_cross_group_leak(self):
        self.q['source_group_tasks'][0]['cited_variant_identities_only'].append(
            self.q['source_group_tasks'][1]['cited_variant_identities_only'][0])
        self.assert_hold()

    def test_duplicate_cited_identity(self):
        ids = self.q['source_group_tasks'][0]['cited_variant_identities_only']
        ids.append(ids[0]); self.assert_hold()

    def test_wrong_source_id(self):
        self.q['source_group_tasks'][0]['cited_variant_identities_only'][0][1]='wrong'
        self.assert_hold()

    def test_trailing_slash_source_identity_not_auto_normalized(self):
        self.q['source_group_tasks'][0]['cited_variant_identities_only'][0][2]+='/'
        self.assert_hold()

    def test_extra_cited_reference(self):
        v = self.d['source_group_dossiers'][0]['variants'][1]
        v['article_reading_scopes'].append({
            'article_slug':'article-00','citation_id':v['id'],
            'literal_url':v['literal_url'],'author_reading_scope':'New cited variant',
            'citation_occurrences':1})
        v['uncited_variant_not_an_approval']=False
        self.assert_hold()

    def test_wrong_uncited_flag(self):
        self.d['source_group_dossiers'][0]['variants'][1]['uncited_variant_not_an_approval']=False
        self.assert_hold()

    def test_duplicate_variant_across_groups(self):
        self.d['source_group_dossiers'][0]['variants'][1] = copy.deepcopy(
            self.d['source_group_dossiers'][1]['variants'][1])
        self.assert_hold()

    def test_citation_total_tampered(self):
        self.q['source_group_tasks'][0]['citation_occurrences'] += 1; self.assert_hold()

    def test_affected_articles_tampered(self):
        self.q['source_group_tasks'][0]['affected_articles'] = ['article-34']; self.assert_hold()

    def test_duplicate_affected_articles(self):
        self.q['source_group_tasks'][0]['affected_articles'].append('article-00'); self.assert_hold()

    def test_unreviewed_source_state_tampered(self):
        self.d['source_group_dossiers'][0]['status']='REVIEWED'; self.assert_hold()

    def test_upstream_queue_source_decision_tampered(self):
        self.q['source_group_tasks'][0]['decision']='SAFE'; self.assert_hold()

    def test_bad_dossier_witness(self):
        self.d['source_group_dossiers'][0]['witness_sha256']='xx'; self.assert_hold()

    def test_missing_source_file(self):
        self.d['source_group_dossiers'][0]['variants'][0]['source_file']=''
        self.assert_hold()

    def test_source_reading_scope_missing(self):
        self.d['source_group_dossiers'][0]['variants'][0]['article_reading_scopes'][0]['author_reading_scope']=''
        self.assert_hold()

    def test_unknown_article_in_group(self):
        self.d['source_group_dossiers'][0]['variants'][0]['article_reading_scopes'][0]['article_slug']='unknown'
        self.assert_hold()

    def test_wrong_article_citation_id(self):
        self.d['source_group_dossiers'][0]['variants'][0]['article_reading_scopes'][0]['citation_id']='bad'
        self.assert_hold()

    def test_duplicate_article_source_use(self):
        ref=self.d['source_group_dossiers'][0]['variants'][0]['article_reading_scopes']
        ref.append(copy.deepcopy(ref[0])); self.assert_hold()

    def test_negative_citation_count(self):
        self.d['source_group_dossiers'][0]['variants'][0]['article_reading_scopes'][0]['citation_occurrences']=-1
        self.assert_hold()

    def test_float_citation_count(self):
        self.d['source_group_dossiers'][0]['variants'][0]['article_reading_scopes'][0]['citation_occurrences']=1.0
        self.assert_hold()

    def test_duplicate_source_task_id(self):
        self.q['source_group_tasks'][1]['task_id']=self.q['source_group_tasks'][0]['task_id']
        self.assert_hold()

    def test_group_index_collision(self):
        self.d['source_group_dossiers'][1]['group_index']=self.d['source_group_dossiers'][0]['group_index']
        self.assert_hold()

    def test_wrong_safety_task_decision(self):
        self.q['safety_passage_tasks'][0]['decision']='APPROVED'
        self.assert_hold()

    def test_duplicate_article_slug(self):
        self.d['articles'][1]['slug']=self.d['articles'][0]['slug']; self.assert_hold()

    def test_missing_risk_passage_task(self):
        self.q['safety_passage_tasks']=[]; self.assert_hold()


# 35 independent tampering cases assert every article remains independently guarded.
def _article_case(index):
    def test(self):
        q,d=fixture()
        d['articles'][index]['status']='PUBLISHED'
        with self.assertRaises(m.ReconciliationHold):
            m.reconcile(q,d)
    return test

for _i in range(35):
    setattr(R138Adversarial, f'test_article_{_i:02d}_cannot_publish', _article_case(_i))


# 32 individual citation count mutations ensure every group cannot silently drift.
def _group_case(index):
    def test(self):
        q,d=fixture()
        q['source_group_tasks'][index]['citation_occurrences']+=1
        with self.assertRaises(m.ReconciliationHold):
            m.reconcile(q,d)
    return test

for _i in range(32):
    setattr(R138Adversarial, f'test_group_{_i:02d}_citation_loss', _group_case(_i))


# Reject forged true approvals regardless of which upstream ledger supplies it.
def _approval_case(side,field):
    def test(self):
        q,d=fixture()
        (q if side == 'queue' else d)[field]=True
        with self.assertRaises(m.ReconciliationHold):
            m.reconcile(q,d)
    return test

for _side in ('queue','dossiers'):
    for _field in ('may_publish','qd_pass','medical_safety_verified','merchant_offer_verified'):
        setattr(R138Adversarial, f'test_{_side}_{_field}_forged',
                _approval_case(_side, _field))


if __name__ == '__main__':
    unittest.main()
