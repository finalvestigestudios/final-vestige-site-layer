"""R278 deterministic synthetic/adversarial checks; NOT original repository build."""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

module = Path(__file__).resolve().parents[1] / 'tools' / 'r279_reconciliation_citation_guard.py'
spec = importlib.util.spec_from_file_location('r278_guard', module)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)
CHANGED = (1, 2, 6, 7, 12, 13, 14, 15, 16, 20, 21, 24, 25, 27, 32, 33, 34)
BODIES = (1, 2, 12, 13, 14, 15, 16, 20, 24, 25, 27, 32, 33, 34)
METAS = (2, 6, 7, 12, 13, 14, 15, 20, 21, 24, 25, 34)
SHORT = (24, 25, 27, 32, 33, 34)


def oid(s):
    return g.git_blob(s.encode())


def fixture():
    heads = {c: oid('frozen-'+c) for c in g.CLUSTERS}
    original = dict(schema='fv-preparedness-r200-seven-cluster-35-article-frozen-custody-v1',
                    state=g.HOLD, artifact_count=35, export_target_count_with_six_tools=41,
                    branch_heads=heads, articles=[], publication_authorized=False,
                    independent_qd_pass=False, medical_safety_verified=False)
    integrated = dict(schema='fv-r276-all-slate-identity-v1', state=g.HOLD,
                      snapshot_ref='df96120007ceb33290764392a5900e356e04deac',
                      entries=[], source_review=dict(shared_url_groups=32,duplicate_id_groups=15,held_occurrences=3),
                      **{k:False for k in (*g.FLAGS, 'merchant_offer_approved')})
    recon = dict(schema='fv-r277-source-baseline-erratum-v1', state=g.HOLD,
                 source_refs=dict(r200_manifest_blob=g.PINS[g.ORIGINAL], r276_integrated_manifest_blob=g.PINS[g.INTEGRATED]),
                 release={**{k:False for k in g.FLAGS},'commercial_offer_approved':False},
                 source_review=dict(unadjudicated_shared_url_groups=32, unadjudicated_duplicate_id_groups=15, held_cdc_ready_gov_occurrences=3),
                 branch_heads=[dict(origin=c, head_sha_at_check=heads[c], r200_frozen_sha=heads[c],
                                    compare_status='identical',ahead=0,behind=0) for c in g.CLUSTERS],
                 comparison_census=dict(r200_current_matches=7, r276_older_crosswalk_matches=2,
                                        older_provenance_differences=5, unreviewed_new_branch_changes_identified=0),
                 article_snapshot=dict(r200_articles=35,r275_integrated_articles=35,
                                       baseline_different_articles=17,body_blob_differences=14,
                                       meta_blob_differences=12,route_duplicate_count=0,differences=[]))
    depth=dict(schema='fv-r277-source-depth-structure-unapproved-v1', state=g.HOLD,
               r200_manifest_blob=g.PINS[g.ORIGINAL],integrated_manifest_blob=g.PINS[g.INTEGRATED],
               release={k:False for k in g.FLAGS},rows=[],article_html_changed=14,
               body_html_shorter_in_bytes=6,body_html_shorter_article_numbers=list(SHORT),
               word_counts_lower=0,heading_counts_lower=0,citation_occurrence_counts_lower=0,
               removed_citation_id_sets=0)
    for n in range(1,36):
        slug=f'article-{n}'
        route=f'/preparedness/start-here/{slug}/'
        old_body, old_meta = oid(f'old-body-{n}'), oid(f'old-meta-{n}')
        new_body = oid(f'new-body-{n}') if n in BODIES else old_body
        new_meta = oid(f'new-meta-{n}') if n in METAS else old_meta
        old_bytes=100+n
        delta=-5 if n in SHORT else 20 if n in BODIES else 0
        original['articles'].append(dict(n=n,slug=slug,source_cluster='start',
                                         branch_sha=heads['start'],route=route,
                                         body_oid=old_body,meta_oid=old_meta,body_bytes=old_bytes))
        for part, suffix, sha, size in (('body','body.html',new_body,old_bytes+delta),
                                         ('meta','meta.json',new_meta,50+n)):
            integrated['entries'].append(dict(path=f'content/articles/{slug}.{suffix}',
                                              role='article_'+part,sha=sha,size=size))
        if n in CHANGED:
            recon['article_snapshot']['differences'].append(dict(n=n,slug=slug,
                    source_cluster='start',route=route,r200_body_blob=old_body,
                    r200_meta_blob=old_meta,r275_body_blob=new_body,r275_meta_blob=new_meta,
                    body_diff=n in BODIES, meta_diff=n in METAS))
        if n in BODIES:
            depth['rows'].append(dict(n=n,slug=slug,r200_blob=old_body,r275_blob=new_body,
                     body_bytes_old=old_bytes,body_bytes_integrated=old_bytes+delta,
                     body_byte_delta=delta,word_count_old=200,word_count_integrated=200,
                     heading_count_old=3,heading_count_integrated=3,citation_occurrences_old=10,
                     citation_occurrences_integrated=10,lost_citation_ids=[],introduced_citation_ids=[],
                     structural_reading_depth_never_decreased=True))
    for i in range(26):
        integrated['entries'].append(dict(path=f'custody/safe-{i}',role='auxiliary',sha=oid(f'aux-{i}'),size=10))
    return [original, integrated, recon, depth]


class GuardTests(unittest.TestCase):
    def test_positive_synthetic_roster(self):
        report=g.inspect(*fixture());self.assertEqual(report['state'],g.HOLD)
        self.assertEqual((report['changed_articles'],report['changed_bodies'],report['changed_metadata']), (17,14,12))
        self.assertTrue(report['requires_human_source_review']);self.assertFalse(report['publication_authorized'])
    def test_git_blob_identity(self):
        self.assertEqual(g.git_blob(b'hello'),'b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0')
    def test_duplicate_json_key_rejected(self):
        with self.assertRaises(ValueError):g.strict_json(b'{"x":1,"x":2}')
    def test_nonfinite_json_rejected(self):
        with self.assertRaises(ValueError):g.strict_json(b'{"a":NaN}')
    def test_no_implicit_local_approval(self):
        r=g.audit('/nonexistent/preparedness')
        self.assertEqual(r['state'],g.INVALID);self.assertFalse(r['publication_authorized'])
    def test_bytes_only_git_blob(self):
        with self.assertRaises(ValueError):g.git_blob('hello')


MUTATIONS={
 'bad_r200_schema':lambda x:x[0].update(schema='invalid'),
 'bad_integrated_schema':lambda x:x[1].update(schema='invalid'),
 'bad_recon_schema':lambda x:x[2].update(schema='invalid'),
 'bad_depth_schema':lambda x:x[3].update(schema='invalid'),
 'r200_release':lambda x:x[0].update(publication_authorized=True),
 'integrated_release':lambda x:x[1].update(publication_authorized=True),
 'recon_release':lambda x:x[2]['release'].update(publication_authorized=True),
 'depth_release':lambda x:x[3]['release'].update(publication_authorized=True),
 'independent_qd':lambda x:x[2]['release'].update(independent_qd_pass=True),
 'medical_approval':lambda x:x[3]['release'].update(medical_safety_verified=True),
 'privacy_approval':lambda x:x[2]['release'].update(privacy_approved=True),
 'implicit_merge':lambda x:x[2]['release'].pop('may_merge'),
 'missing_original':lambda x:x[0]['articles'].pop(),
 'missing_integrated':lambda x:x[1]['entries'].pop(),
 'missing_difference':lambda x:x[2]['article_snapshot']['differences'].pop(),
 'missing_depth':lambda x:x[3]['rows'].pop(),
 'dupe_number':lambda x:x[0]['articles'][1].update(n=1),
 'dupe_route':lambda x:x[0]['articles'][1].update(route=x[0]['articles'][0]['route']),
 'dupe_slug':lambda x:x[0]['articles'][1].update(slug=x[0]['articles'][0]['slug']),
 'invented_article':lambda x:x[0]['articles'][0].update(n=36),
 'branch_head_mismatch':lambda x:x[0]['branch_heads'].update(start=oid('altered')),
 'wrong_article_provenance':lambda x:x[0]['articles'][0].update(branch_sha=oid('wrong')),
 'missing_cluster':lambda x:x[0]['branch_heads'].pop('food'),
 'altered_integrated_sha':lambda x:x[1]['entries'][0].update(sha=oid('unexpected')),
 'invalid_integrated_sha':lambda x:x[1]['entries'][0].update(sha='0'),
 'invalid_integrated_size':lambda x:x[1]['entries'][0].update(size=True),
 'source_hold_gone':lambda x:x[1]['source_review'].update(shared_url_groups=0),
 'disputed_cites_removed':lambda x:x[2]['source_review'].update(held_cdc_ready_gov_occurrences=0),
 'incorrect_r200_pin':lambda x:x[2]['source_refs'].update(r200_manifest_blob=oid('wrong')),
 'incorrect_depth_pin':lambda x:x[3].update(r200_manifest_blob=oid('wrong')),
 'current_head_drift':lambda x:x[2]['branch_heads'][0].update(head_sha_at_check=oid('new')),
 'false_branch_identical':lambda x:x[2]['branch_heads'][0].update(compare_status='ahead'),
 'nonzero_branch_ahead':lambda x:x[2]['branch_heads'][0].update(ahead=1),
 'nonzero_branch_behind':lambda x:x[2]['branch_heads'][0].update(behind=1),
 'dupe_branch_origin':lambda x:x[2]['branch_heads'][0].update(origin='food'),
 'five_false_intake':lambda x:x[2]['comparison_census'].update(unreviewed_new_branch_changes_identified=5),
 'historic_older_count':lambda x:x[2]['comparison_census'].update(r276_older_crosswalk_matches=7),
 'wrong_17_total':lambda x:x[2]['article_snapshot'].update(baseline_different_articles=16),
 'wrong_14_total':lambda x:x[2]['article_snapshot'].update(body_blob_differences=13),
 'wrong_12_total':lambda x:x[2]['article_snapshot'].update(meta_blob_differences=11),
 'route_collision':lambda x:x[2]['article_snapshot'].update(route_duplicate_count=1),
 'difference_loses_id':lambda x:x[2]['article_snapshot']['differences'][0].update(n=99),
 'difference_loses_route':lambda x:x[2]['article_snapshot']['differences'][0].update(route='/somewhere-else/'),
 'difference_loses_source':lambda x:x[2]['article_snapshot']['differences'][0].update(r200_body_blob=oid('wrong')),
 'false_body_flag':lambda x:x[2]['article_snapshot']['differences'][0].update(body_diff=False),
 'false_meta_flag':lambda x:x[2]['article_snapshot']['differences'][0].update(meta_diff=True),
 'changed_depth_id':lambda x:x[3]['rows'][0].update(n=36),
 'changed_depth_slug':lambda x:x[3]['rows'][0].update(slug='fake'),
 'changed_depth_blob':lambda x:x[3]['rows'][0].update(r200_blob=oid('wrong')),
 'changed_depth_integrated_sha':lambda x:x[3]['rows'][0].update(r275_blob=oid('wrong')),
 'changed_depth_old_bytes':lambda x:x[3]['rows'][0].update(body_bytes_old=5),
 'changed_depth_new_bytes':lambda x:x[3]['rows'][0].update(body_bytes_integrated=5),
 'changed_depth_delta':lambda x:x[3]['rows'][0].update(body_byte_delta=0),
 'drop_word_count':lambda x:x[3]['rows'][0].update(word_count_integrated=1),
 'drop_heading_count':lambda x:x[3]['rows'][0].update(heading_count_integrated=1),
 'drop_citation_occurrences':lambda x:x[3]['rows'][0].update(citation_occurrences_integrated=1),
 'lose_cited_source':lambda x:x[3]['rows'][0].update(lost_citation_ids=['official-fema']),
 'pretend_depth_false':lambda x:x[3]['rows'][0].update(structural_reading_depth_never_decreased=False),
 'drop_shorter_article':lambda x:x[3].update(body_html_shorter_article_numbers=[24,25,27,32,33]),
 'wrong_shorter_count':lambda x:x[3].update(body_html_shorter_in_bytes=5),
 'false_citation_loss_total':lambda x:x[3].update(citation_occurrence_counts_lower=1),
 'wrong_integrated_snapshot':lambda x:x[1].update(snapshot_ref='main'),
 'r200_wrong_article_count':lambda x:x[0].update(artifact_count=34),
 'r200_wrong_export_total':lambda x:x[0].update(export_target_count_with_six_tools=40),
}
for label, change in MUTATIONS.items():
    def runner(self, fn=change):
        data=fixture();fn(data)
        with self.assertRaises((ValueError,TypeError,KeyError,AttributeError)):
            g.inspect(*data)
    setattr(GuardTests,'test_reject_'+label,runner)


class RawCitationErratumTests(unittest.TestCase):
    def make(self, n=24, count=1):
        orig=("{{cite:nchfp-jerky}}" * count + "{{cite:shared}}").encode()
        inte=("{{cite:hist-food-nchfp-jerky}}" * count + "{{cite:shared}}").encode()
        witness=dict(r200_blob=g.git_blob(orig),r275_blob=g.git_blob(inte),
            citation_occurrences_old=count+1,citation_occurrences_integrated=count+1,
            lost_citation_ids=[],introduced_citation_ids=[])
        return n,orig,inte,witness

    def test_article24_actual_raw_remap(self):
        a,b,c,w=self.make()
        self.assertEqual(g.check_raw_ids(a,b,c,w)['replaced_occurrences'],1)
    def test_article25_seven_uses(self):
        a,b,c,w=self.make(25,7)
        self.assertEqual(g.check_raw_ids(a,b,c,w)['replaced_occurrences'],7)
    def test_no_equivalence_approval(self):
        a,b,c,w=self.make()
        self.assertFalse(g.check_raw_ids(a,b,c,w)['independent_equivalence_approved'])
    def test_citation_multiplicity(self):
        self.assertEqual(g.raw_cites(b'{{cite:a}}{{cite:a}}{{cite:b}}'),{'a':2,'b':1})
    def test_missing_git_fails_closed(self):
        with self.assertRaises(ValueError):
            g.git_show(Path('/nonexistent'), '0'*40, 'fake')
    def test_native_audit_requires_git(self):
        r=g.audit(Path('/nonexistent'))
        self.assertEqual(r['state'],g.INVALID)
    def test_identical_ids_are_distinct_raw(self):
        self.assertNotEqual(g.raw_cites(b'{{cite:nchfp-jerky}}'),
                            g.raw_cites(b'{{cite:hist-food-nchfp-jerky}}'))

for label, mutate in {
    'wrong_source_sha':lambda n,a,b,w:w.update(r200_blob='0'*40),
    'wrong_integrated_sha':lambda n,a,b,w:w.update(r275_blob='0'*40),
    'false_old_citation_count':lambda n,a,b,w:w.update(citation_occurrences_old=99),
    'false_new_citation_count':lambda n,a,b,w:w.update(citation_occurrences_integrated=99),
    'altered_original':lambda n,a,b,w:None,
    'altered_new':lambda n,a,b,w:None,
    'missing_raw_loss_receipt':lambda n,a,b,w:w.update(lost_citation_ids=['nchfp-jerky']),
    'false_raw_new_id_receipt':lambda n,a,b,w:w.update(introduced_citation_ids=['hist-food-nchfp-jerky']),
    'wrong_jerky_mapping_count':lambda n,a,b,w:None,
    'old_id_retained':lambda n,a,b,w:None,
    'new_id_absent':lambda n,a,b,w:None,
    'unexpected_new_id':lambda n,a,b,w:None,
}.items():
    for article,repeats in ((24,1),(25,7)):
        def test(self,label=label,mutate=mutate,article=article,repeats=repeats):
            n,a,b,w=self.make(article,repeats)
            mutate(n,a,b,w)
            if label=='altered_original':a+=b'!'
            elif label=='altered_new':b+=b'!'
            elif label=='wrong_jerky_mapping_count':b=b'{{cite:hist-food-nchfp-jerky}}'+b
            elif label=='old_id_retained':b=b.replace(b'hist-food-nchfp-jerky',b'nchfp-jerky',1)
            elif label=='new_id_absent':b=b.replace(b'hist-food-nchfp-jerky',b'other-id')
            elif label=='unexpected_new_id':b=b.replace(b'hist-food-nchfp-jerky',b'unknown-id')
            with self.assertRaises((ValueError,KeyError)):
                g.check_raw_ids(n,a,b,w)
        setattr(RawCitationErratumTests,'test_reject_'+label+'_'+str(article),test)

if __name__ == '__main__':unittest.main()
