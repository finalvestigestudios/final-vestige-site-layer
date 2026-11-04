"""Synthetic read-only tamper matrix for R117; no WordPress or GitHub writes."""
import copy
import importlib.util
from pathlib import Path
import unittest

P = Path(__file__).resolve().parents[1] / 'tools/r117_seven_cluster_object_parity_gate.py'
s = importlib.util.spec_from_file_location('r117', P)
gate = importlib.util.module_from_spec(s)
s.loader.exec_module(gate)
A, B, C, D = 'a'*40, 'b'*40, 'c'*40, 'd'*40
SLUGS = ['article-'+str(n) for n in range(1,36)]

def fixture():
    articles = {k+ext: A for k in SLUGS for ext in ('.body.html', '.meta.json')}
    frags = {'food.json':A,'start.json':A}
    baseline = {'role':'baseline', 'ref':'review/baseline', 'sha':A,
                'article_files':articles, 'source_fragments':frags}
    candidate = copy.deepcopy(baseline)
    candidate.update(role='candidate',ref='review/candidate',sha=B)
    candidate['article_files']['article-1.body.html'] = B
    names = sorted(gate.CLUSTERS)
    contributors=[]
    for n, name in enumerate(names):
        a = {f'article-{n+1}{ext}': A for ext in ('.body.html','.meta.json')}
        if n == 0: a['article-1.body.html'] = C
        f = {'food.json': A}
        if n == 1: f['food.json'] = C
        contributors.append({'role':'contributor','cluster':name,
                             'ref':'claude/'+name, 'sha': str(n+1)*40,
                             'article_files':a,'source_fragments':f})
    manifest={'schema':gate.SCHEMA,'issue':136,'business_issue':820,
              'governance':{'release_state':'HOLD','may_publish':False,'may_merge':False,
                            'independent_QD_PASS':False,'medical_safety_verified':False,
                            'merchant_offer_verified':False},
              'snapshots':[baseline,candidate]+contributors}
    base, cand, cs, rows, by = gate.reconstruct(manifest)
    collisions=[{'path':p,'contributors':[x['cluster'] for x in v],
                 'distinct_contributor_git_blobs':len(set(x['contributor_git_blob'] for x in v))}
                for p,v in by.items() if len(v)>1]
    docket={'schema':gate.ORDER_SCHEMA,'issue':136,'business_issue':820,
            'release_state':'HOLD','may_publish':False,'may_merge':False,
            'independent_QD_PASS':False,'baseline_sha':base['sha'],
            'candidate_sha':cand['sha'],
            'seven_contributor_heads':{x['cluster']:x['sha'] for x in cs},
            'rows':rows,'overlapping_paths':collisions,'observation_count':len(rows),
            'unique_changed_paths':len(by),
            'non_exact_candidate_observations':sum(x['disposition']!='EXACT_IN_RELEASE_CANDIDATE' for x in rows)}
    return manifest,docket

class R117ProvenanceTests(unittest.TestCase):
    def test_valid_synthetic_remains_hold(self):
        m,d=fixture(); v=gate.verify(m,d)
        self.assertEqual(v['original_article_routes'],35)
        self.assertEqual(v['release_state'],'HOLD')
        self.assertFalse(v['may_publish'])
        self.assertFalse(v['snapshot_heads_verified_locally'])

    def test_original_contributor_stale_oid_not_accepted(self):
        m,d=fixture(); m['snapshots'][2]['article_files']['article-1.body.html']=D
        with self.assertRaises(gate.Hold):gate.verify(m,d)

    def test_docket_order_is_immaterial_but_data_is_not(self):
        m,d=fixture(); d['rows'].reverse(); self.assertTrue(gate.verify(m,d))

    def test_empty_local_repo_cannot_prove_remote_heads(self):
        m,_=fixture()
        with self.assertRaisesRegex(gate.Hold,'NO_CHECKED_OUT_GIT_OBJECT_DATABASE'):
            gate.require_local_head_objects(m,Path('/nonexistent/r117-git-checkout'))

def mutation_test(label, mutate):
    def test(self):
        manifest, docket = fixture()
        mutate(manifest,docket)
        with self.assertRaises(gate.Hold, msg=label):
            gate.verify(manifest,docket)
    setattr(R117ProvenanceTests,'test_reject_'+label,test)

for i in range(35):
    slug=SLUGS[i]
    mutation_test(f'original_missing_meta_{i+1:02}',
        lambda m,d,slug=slug: m['snapshots'][0]['article_files'].pop(slug+'.meta.json'))

for i in range(7):
    mutation_test(f'contributor_head_{i+1:02}',
        lambda m,d,i=i: m['snapshots'][i+2].update(sha=D))

mutations={
 'wrong_schema':lambda m,d:m.update(schema='not-r117'),
 'wrong_workorder_schema':lambda m,d:d.update(schema='not-r117'),
 'wrong_issue':lambda m,d:m.update(issue=123),
 'wrong_business_issue':lambda m,d:d.update(business_issue=42),
 'grant_publish':lambda m,d:m['governance'].update(may_publish=True),
 'grant_merge':lambda m,d:d.update(may_merge=True),
 'grant_QD':lambda m,d:d.update(independent_QD_PASS=True),
 'grant_medical':lambda m,d:m['governance'].update(medical_safety_verified=True),
 'extra_snapshot':lambda m,d:m['snapshots'].append(copy.deepcopy(m['snapshots'][-1])),
 'swap_roles':lambda m,d:m['snapshots'][0].update(role='contributor'),
 'duplicate_cluster':lambda m,d:m['snapshots'][-1].update(cluster=m['snapshots'][-2]['cluster']),
 'invalid_oid':lambda m,d:m['snapshots'][0]['article_files'].update({'article-1.body.html':'XYZ'}),
 'untrusted_article_path':lambda m,d:m['snapshots'][0]['article_files'].update({'../escape.meta.json':A}),
 'untrusted_fragment_path':lambda m,d:m['snapshots'][0]['source_fragments'].update({'../../bad.json':A}),
 'unexpected_contributor_file':lambda m,d:m['snapshots'][2]['article_files'].update({'article-36.body.html':A,'article-36.meta.json':A}),
 'unexpected_contributor_fragment':lambda m,d:m['snapshots'][2]['source_fragments'].update({'unlisted.json':A}),
 'candidate_missing_article':lambda m,d:m['snapshots'][1]['article_files'].pop('article-1.body.html'),
 'stale_baseline_sha':lambda m,d:d.update(baseline_sha=D),
 'stale_contributor_sha':lambda m,d:d['seven_contributor_heads'].update({sorted(gate.CLUSTERS)[0]:D}),
 'delete_workorder':lambda m,d:d['rows'].pop(),
 'duplicate_workorder':lambda m,d:d['rows'].append(copy.deepcopy(d['rows'][0])),
 'fake_citation_approval':lambda m,d:d['rows'][0].update(requires_human_source_or_safety_adjudication=False),
 'swap_fragment_provenance':lambda m,d:d['rows'][-1].update(contributor_git_blob=D),
 'wrong_path_count':lambda m,d:d.update(unique_changed_paths=999),
 'wrong_observation_count':lambda m,d:d.update(observation_count=999),
 'wrong_nonexact_count':lambda m,d:d.update(non_exact_candidate_observations=999),
 'wrong_kind':lambda m,d:d['rows'][0].update(kind='pageviews'),
 'wrong_disposition':lambda m,d:d['rows'][0].update(disposition='APPROVED'),
 'missing_collision':lambda m,d:d.update(overlapping_paths=[{'path':'fake','contributors':['food'],'distinct_contributor_git_blobs':1}]),
}
for label, fn in mutations.items():mutation_test(label,fn)

if __name__=='__main__':unittest.main()
