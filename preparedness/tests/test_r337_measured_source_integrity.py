"""R337 disposable 41-entry adversarial tests. Not original-slate clearance."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from preparedness.tests.test_r336_frozen_archive_integrity import tree
from preparedness.tools import r337_measured_source_integrity as gate


def make_fixture(root):
    witness=tree(root)
    all_rows=[]
    for e in witness['entries']:
        path=root/'content'/e['kind']/f"{e['slug']}.body.html"
        m=gate.measured(path.read_text('utf-8'))
        e['body_min_bytes']=len(path.read_bytes())
        all_rows.append({**{k:e[k] for k in ('kind','slug','route','body_blob','meta_blob')},
                         'min_utf8_bytes':len(path.read_bytes()),**m})
    (root/'audits'/'r336_frozen_41_entry_witness.json').write_text(json.dumps(witness),encoding='utf-8')
    for number,start,end in gate.PARTS:
        part={'schema':gate.SCHEMA,'source_commit':gate.SOURCE_COMMIT,
              'r336_witness_blob':gate.PRIOR_WITNESS_BLOB,'part':number,'range':[start,end],
              'rows':all_rows[start:end]}
        (root/'audits'/f'r337_source_metrics_part_{number:02d}.json').write_text(json.dumps(part),encoding='utf-8')
    return witness,all_rows


class MeasuredSourceIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='fv-r337-SYNTHETIC-')
        cls.root=Path(cls.temp.name)
        cls.witness,cls.rows=make_fixture(cls.root)
    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()
    def audit(self):return gate.audit(self.root,prior_witness=self.witness)
    def test_disk_authentic_witness_pin_required(self):
        self.assertEqual(gate.audit(self.root)["errors"],["R336_WITNESS_GIT_BLOB_DRIFT"])
    def change(self,path,transform):
        before=path.read_bytes()
        try:
            path.write_bytes(transform(before))
            return self.audit()['errors']
        finally:path.write_bytes(before)
    def change_manifest(self,num,mut):
        p=self.root/'audits'/f'r337_source_metrics_part_{num:02d}.json'
        b=p.read_bytes()
        try:
            obj=json.loads(b);mut(obj);p.write_text(json.dumps(obj),encoding='utf-8')
            return self.audit()['errors']
        finally:p.write_bytes(b)
    def test_clean_still_hard_hold(self):
        r=self.audit();self.assertEqual(r['state'],'DRAFT_HARD_HOLD',r['errors'])
        self.assertFalse(r['may_publish']);self.assertFalse(r['qualified_qd_pass'])
        self.assertEqual(r['entries_checked'],41)
    def test_missing_root_rejects(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertEqual(gate.audit(Path(t))['state'],'INVALID_HARD_HOLD')
    def test_5_disjoint_parts(self):
        self.assertEqual([(a,b) for _,a,b in gate.PARTS],[(0,9),(9,18),(18,27),(27,36),(36,41)])
    def test_order_duplicate_rejected(self):
        errors=self.change_manifest(2,lambda p:p['rows'][0].update({'slug':'article-01'}))
        self.assertTrue(any('MEASUREMENT_IDENTITY_DRIFT:' in e for e in errors))
    def test_wrong_source_commit(self):
        self.assertIn('MEASUREMENT_SOURCE_COMMIT_DRIFT:02',self.change_manifest(2,lambda p:p.update(source_commit='b'*40)))
    def test_wrong_prior_witness(self):
        self.assertIn('MEASUREMENT_PREVIOUS_WITNESS_PIN_DRIFT:01',self.change_manifest(1,lambda p:p.update(r336_witness_blob='b'*40)))
    def test_part_id_drift(self):
        self.assertIn('MEASUREMENT_PART_IDENTITY_DRIFT:03',self.change_manifest(3,lambda p:p.update(part=999)))
    def test_part_count_drift(self):
        self.assertIn('MEASUREMENT_PART_COUNT_DRIFT:03',self.change_manifest(3,lambda p:p['rows'].pop()))
    def test_fake_word_increase_rejected(self):
        self.assertIn('MEASURED_READING_DEPTH_DRIFT:articles:article-01',self.change_manifest(1,lambda p:p['rows'][0].update(word_units=999999)))
    def test_fake_citation_count_rejected(self):
        self.assertIn('CITATION_COUNTS_DRIFT:articles:article-01',self.change_manifest(1,lambda p:p['rows'][0].update(citations={'source-one':20})))
    def test_fake_heading_rejected(self):
        self.assertIn('HEADING_IDS_DRIFT:articles:article-01',self.change_manifest(1,lambda p:p['rows'][0].update(headings=['unrelated'])))
    def test_fake_link_count_rejected(self):
        self.assertIn('INTERNAL_LINK_COUNTS_DRIFT:articles:article-01',self.change_manifest(1,lambda p:p['rows'][0].update(links={'false':10})))
    def test_metadata_publish_rejected(self):
        p=self.root/'content'/'articles'/'article-01.meta.json'
        def mut(b):
            x=json.loads(b);x['status']['publish']='published';return json.dumps(x).encode()
        self.assertIn('PUBLICATION_STATE_CHANGED:articles:article-01',self.change(p,mut))
    def test_missing_part_rejected(self):
        p=self.root/'audits'/'r337_source_metrics_part_04.json';b=p.read_bytes()
        try:
            p.unlink();self.assertIn('MISSING_OR_INVALID_MEASURED_PART:04',self.audit()['errors'])
        finally:p.write_bytes(b)
    def test_source_citation_not_in_source_use(self):
        p=self.root/'content'/'articles'/'article-01.meta.json'
        def mut(b):
            x=json.loads(b);x['source_use']={};return json.dumps(x).encode()
        self.assertIn('CITATION_NOT_IN_SOURCE_USE:articles:article-01',self.change(p,mut))
    def test_lexical_tokenizer_deterministic(self):
        m=gate.measured('<h2 id="z">Hello &amp; world 2026</h2><p>Three-word {{cite:a}} {{cite:a}} {{link:b|Here}}</p>')
        self.assertEqual(m['word_units'],4)
        self.assertEqual(m['citations'],{'a':2});self.assertEqual(m['links'],{'b':1});self.assertEqual(m['headings'],['z'])


def attach_mutations():
    for i in range(41):
        kind='articles' if i<35 else 'tools'
        slug=f'article-{i+1:02d}' if i<35 else f'tool-{i-34:02d}'
        def damage_words(self,k=kind,s=slug):
            p=self.root/'content'/k/f'{s}.body.html'
            errors=self.change(p,lambda b:b.replace(b'Relevant background evidence with context. ',b''))
            self.assertIn('MEASURED_READING_DEPTH_DRIFT:'+k+':'+s,errors)
            self.assertIn('SOURCE_CHANGED_REQUIRES_HUMAN_REPIN:'+k+':'+s,errors)
        def damage_cite(self,k=kind,s=slug):
            p=self.root/'content'/k/f'{s}.body.html'
            errors=self.change(p,lambda b:b.replace(b'{{cite:source-one}}',b''))
            self.assertIn('CITATION_COUNTS_DRIFT:'+k+':'+s,errors)
        setattr(MeasuredSourceIntegrity,'test_word_loss_'+slug.replace('-','_'),damage_words)
        setattr(MeasuredSourceIntegrity,'test_cite_loss_'+slug.replace('-','_'),damage_cite)
attach_mutations()
if __name__=='__main__':unittest.main()
