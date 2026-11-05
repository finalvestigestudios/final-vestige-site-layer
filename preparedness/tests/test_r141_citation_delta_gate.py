"""Isolated synthetic/adversarial tests. Not a 35-article corpus or safety review."""
import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('r141_citation_delta_gate', HERE / 'r141_citation_delta_gate.py')
assert spec and spec.loader
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
DOC = json.loads((HERE / 'citation_occurrence_docket.json').read_text())
TOTAL = {
'go-bags':(73,72,3638,3397), 'household-emergency-plan':(57,57,3434,3193),
'preparedness-real-households':(64,64,3400,3171),'three-day-kit':(79,75,3790,3326),
'family-communication-plan':(69,62,3563,3026),'home-fire-escape-plan':(73,70,4256,3746),
'outage-heat-cold-generators':(121,116,4463,4196),'shelter-or-evacuate':(59,50,4193,3437),
'pemmican-and-dried-meats':(46,46,2413,2413),'pioneer-travel-rations':(39,39,2350,2350),
'root-cellars-cool-storage':(42,42,2793,2793),'sanitation-before-germ-theory':(48,48,2673,2673),
'navigation-before-gps':(47,47,2889,2889),'pioneer-supply-chains-failed':(63,63,3136,3136)
}

def fixture():
    rows = []
    for row in DOC['article_deltas']:
        old, new, ow, nw = TOTAL[row['slug']]
        counts = row['counts']
        rows.append(dict(slug=row['slug'],cluster=row['cluster'],baseline_blob=row['rc_blob'],
                         contributor_blob=row['contributor_blob'], baseline_citations=old,
                         contributor_citations=new, baseline_words=ow, contributor_words=nw,
                         removed_source_ids=[x['id'] for x in counts if x['rc'] and not x['contributor']],
                         added_source_ids=[x['id'] for x in counts if x['contributor'] and not x['rc']]))
    # R140's frozen record omitted one independently observed source disappearance.
    next(x for x in rows if x['slug']=='three-day-kit')['removed_source_ids'].remove('start-cdc-power-outage')
    source = dict(schema='R140-INTAKE-1', rc_sha=DOC['r140_rc_sha'],
        branch_heads={k:'0'*39+str(i) for i,k in enumerate(sorted(m.EXPECTED_CLUSTERS),1)},
        drifts=rows, source_note='32 groups require human review')
    raw = json.dumps(source,sort_keys=True).encode('utf-8')
    return source, raw

class DocketTests(unittest.TestCase):
    def setUp(self):
        self.manifest, self.raw = fixture()
        self.pin = patch.object(m, 'R140_MANIFEST_BLOB', m.git_blob(self.raw))
        self.pin.start()
        self.addCleanup(self.pin.stop)
        self.docket = copy.deepcopy(DOC)
        self.docket['r140_manifest_blob'] = m.R140_MANIFEST_BLOB

    def check(self, docket=None):
        return m.validate_docket(self.manifest, self.raw, docket or self.docket)

    def test_all_14_rows_and_total_30_source_count_differences(self):
        report=self.check()
        self.assertEqual(len(report),14)
        self.assertEqual(sum(x['changed_source_counts'] for x in report),30)
        self.assertTrue(all(x['human_review']=='REQUIRED' for x in report))

    def test_declines_false_human_approval(self):
        self.docket['review_state']='APPROVED'
        with self.assertRaises(ValueError): self.check()

    def test_declines_publisher_flag(self):
        self.docket['publish']=True
        with self.assertRaises(ValueError): self.check()

    def test_no_retired_water_sku_or_merchant_approval(self):
        self.docket['merchant_approved']=True
        with self.assertRaises(ValueError): self.check()

    def test_manifest_changed_without_independent_rebase(self):
        with self.assertRaises(ValueError): m.validate_docket(self.manifest,self.raw+b' ',self.docket)

    def test_duplicate_row(self):
        self.docket['article_deltas'][0]=copy.deepcopy(self.docket['article_deltas'][1])
        with self.assertRaises(ValueError): self.check()

    def test_fewer_rows(self):
        self.docket['article_deltas'].pop()
        with self.assertRaises(ValueError): self.check()

    def test_extra_row(self):
        self.docket['article_deltas'].append(copy.deepcopy(self.docket['article_deltas'][0]))
        with self.assertRaises(ValueError): self.check()

    def test_missing_contributor_cluster(self):
        self.manifest['branch_heads'].pop('food')
        with self.assertRaises(ValueError): self.check()

    def test_empty_counts_provenance_rows_stay_human_hold(self):
        report=self.check()
        self.assertEqual(sum(x['kind']=='PROSE_OR_PROVENANCE_DRIFT_HOLD' for x in report),6)

    def test_r140_incomplete_legacy_identity_is_exposed(self):
        report=self.check()
        row=next(x for x in report if x['slug']=='three-day-kit')
        self.assertEqual(row['r140_omitted_removed_source_ids'],['start-cdc-power-outage'])

    def test_histfood_retarget_is_not_collapsed(self):
        report=self.check()
        self.assertEqual(sum(x['kind']=='SOURCE_IDENTITY_RETARGET_HOLD' for x in report),7)

    def test_loss_and_gain_cannot_cancel_without_detailed_counts(self):
        row=next(x for x in self.docket['article_deltas'] if x['slug']=='home-fire-escape-plan')
        self.assertTrue(any(x['rc']<x['contributor'] for x in row['counts']))
        self.assertTrue(any(x['rc']>x['contributor'] for x in row['counts']))
        row['counts']=[x for x in row['counts'] if x['id']!='shelter-nfpa-escape']
        with self.assertRaises(ValueError): self.check()

    def test_removed_source_identity_must_stay_traceable(self):
        row=next(x for x in self.docket['article_deltas'] if x['slug']=='pemmican-and-dried-meats')
        row['counts']=[x for x in row['counts'] if x['id']!='hist-food-nchfp-jerky']
        with self.assertRaises(ValueError): self.check()

    def test_incidental_publication_metadata_is_forbidden(self):
        self.docket['article_deltas'][0]['status']='publish'
        with self.assertRaises(ValueError): self.check()

    def test_cite_extractor_preserves_literal_author_id(self):
        found=m.citation_counts(b'{{cite:hist-food-nchfp-jerky}}{{cite:nchfp-jerky}}{{cite:hist-food-nchfp-jerky}}')
        self.assertEqual(found['hist-food-nchfp-jerky'],2)
        self.assertEqual(found['nchfp-jerky'],1)

    def test_blob_byte_change_detected(self):
        self.assertNotEqual(m.git_blob(b'one'),m.git_blob(b'one\n'))

    def test_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td)
            (base/'real.html').write_text('ok')
            (base/'link.html').symlink_to(base/'real.html')
            with self.assertRaises(ValueError): m._check_unsafe_path(base/'link.html',base)

    def test_local_staged_rc_verification_is_byte_exact(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            folder=root/'preparedness/content/articles';folder.mkdir(parents=True)
            rows=copy.deepcopy(DOC['article_deltas'])
            for r in rows:
                data=('BODY:'+r['slug']).encode()
                (folder/(r['slug']+'.body.html')).write_bytes(data)
                r['rc_blob']=m.git_blob(data)
            self.assertEqual(len(m.verify_files(root,rows,version='rc')),14)
            (folder/(rows[0]['slug']+'.body.html')).write_bytes(b'tamper')
            with self.assertRaises(ValueError): m.verify_files(root,rows,version='rc')

    def test_excerpt_count_integrity_actual_file(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            folder=root/'preparedness/content/articles';folder.mkdir(parents=True)
            rows=copy.deepcopy(DOC['article_deltas']); orig=copy.deepcopy(self.manifest)
            for r in rows:
                counts={x['id']:x['rc'] for x in r['counts']}
                html=''.join(('{{cite:'+id+'}}')*c for id,c in counts.items())
                filler=TOTAL[r['slug']][0]-sum(counts.values())
                html+='{{cite:some-other-source}}'*filler
                (folder/(r['slug']+'.body.html')).write_text(html)
                r['rc_blob']=m.git_blob(html.encode())
            docket={'article_deltas':rows}
            self.assertEqual(m.verify_occurrences(root,docket,orig,version='rc'),14)
            (folder/(rows[0]['slug']+'.body.html')).write_text('')
            with self.assertRaises(ValueError):m.verify_occurrences(root,docket,orig,version='rc')


def install_mutation_tests():
    for index in range(14):
        def make(which,idx):
            def t(self):
                r=self.docket['article_deltas'][idx]
                if which=='slug': r['slug']='../../etc/passwd'
                elif which=='sha': r['rc_blob']='f'*40
                elif which=='owner': r['cluster']='evil'
                else:
                    r['counts'].append({'id':'BAD.source','rc':2,'contributor':1})
                with self.assertRaises(ValueError): self.check()
            return t
        for which in ('slug','sha','owner','source'):
            setattr(DocketTests,f'test_{index:02d}_{which}_rejects_forgery',make(which,index))

install_mutation_tests()

if __name__=='__main__': unittest.main()
