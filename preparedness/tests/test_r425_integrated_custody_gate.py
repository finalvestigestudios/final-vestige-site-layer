"""R425 synthetic, local-only 35-article/source/export/offer custody tests.

NO test is a qualified source adjudication, publication or commercial receipt.
"""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import r425_integrated_custody_gate as gate

def material():
    originals=[];manifest=[];rows=[];exports={};candidates={}
    for n in range(1,36):
        slug=f'article-{n:02d}'
        bodies=[(f'<article><h1>Original article {n}</h1><p>Original independently held numbered manuscript {n} is not safety reviewed.</p></article>').encode()]
        if n==15:
            bodies.append(b'<article><h1>Alternate manuscript</h1><p>Original fork retained; no choice.</p></article>')
        pins=[gate.r409.blob(b) for b in bodies]
        for sha,body in zip(pins,bodies):candidates[(slug,sha)]=body
        html=(f'<article><h1>Article {n}</h1><p>Original draft words left for qualified review, not public or safe.</p></article>').encode()
        exports[slug]=(html,html)
        path=f'/preparedness/{slug}/'
        source_ids=[f'source-{n:02d}']
        originals.append({'slug':slug,'body_candidate_git_blobs':pins})
        manifest.append({'slug':slug,'canonical_path':path,'sources':source_ids})
        rows.append({'slug':slug,'canonical_path':path,'source_ids':list(source_ids),
                     'original_git_blobs':sorted(pins),'wordpress_sha256':hashlib.sha256(html).hexdigest(),
                     'preview_sha256':hashlib.sha256(html).hexdigest()})
    original={'original_articles':originals}
    m={'articles':manifest,'schema':1,'approved':False,'release_state':'DRAFT_HARD_HOLD'}
    lock={'schema':1,'issue':136,'release_state':'DRAFT_HARD_HOLD','approved':False,
          'original_docket_git_blob':gate.r409.PIN,'articles':rows}
    return original,m,exports,candidates,lock

def audit(o=None,m=None,e=None,c=None,l=None):
    base=material()
    return gate.lock_audit(*(x if x is not None else default for x,default in zip((o,m,e,c,l),base)))

class Baseline(unittest.TestCase):
    def test_35_articles_covered(self):
        errors,details,digest=audit();self.assertEqual(errors,[]);self.assertEqual(len(details),35)
        self.assertRegex(digest,r'^[0-9a-f]{64}$')
    def test_all_sources_matched(self):
        self.assertEqual(sum(x['source_id_count'] for x in audit()[1]),35)
    def test_unselected_fork_retained(self):
        self.assertEqual(next(x for x in audit()[1] if x['slug']=='article-15')['original_candidate_count'],2)
    def test_review_hash_is_deterministic(self):
        self.assertEqual(audit()[2],audit()[2])
    def test_does_not_mutate_inputs(self):
        a=material(); b=copy.deepcopy(a); gate.lock_audit(*a);self.assertEqual(a,b)
    def test_digest_order_independent(self):
        o,m,e,c,l=material();l['articles'].reverse();m['articles'].reverse();self.assertEqual(audit()[2],audit(o,m,e,c,l)[2])
    def test_never_emits_real_paid_sales(self):
        result=gate.held([]);self.assertIsNone(result['verified_paid_orders']);self.assertFalse(result['eligible'])
    def test_never_emits_qd_approval(self):
        result=gate.held([]);self.assertFalse(result['qualified_safety_approved'])
    def test_never_emits_publication_approval(self):
        result=gate.held([]);self.assertFalse(result['publication_approved'])
    def test_held_state_even_with_mock_satisfactory_gates(self):
        s={'integrity_ok':True,'errors':[]};c={'structural_integrity_ok':True,'errors':[]}
        r=gate.held([],source=s,campaign=c,digest='a'*64)
        self.assertTrue(r['structural_integrity_ok']);self.assertFalse(r['eligible']);self.assertEqual(r['release_state'],'DRAFT_HARD_HOLD')
    def test_missing_real_original_fails_closed(self):
        o,m,e,c,l=material();r=gate.validate(o,m,e,c,l,{'invalid':True},raw_original=None)
        self.assertFalse(r['structural_integrity_ok']);self.assertIn('R425_AUTHENTIC_ORIGINAL_DOCKET_GIT_BLOB_MISSING',r['errors'])

class MutationTests(unittest.TestCase):pass
MODS=[
 ('wrong_schema',lambda o,m,e,c,l:l.update(schema=2),'R425_LOCK_IDENTITY_OR_APPROVAL_DRIFT'),
 ('wrong_issue',lambda o,m,e,c,l:l.update(issue=820),'R425_LOCK_IDENTITY_OR_APPROVAL_DRIFT'),
 ('approve_true',lambda o,m,e,c,l:l.update(approved=True),'R425_LOCK_IDENTITY_OR_APPROVAL_DRIFT'),
 ('state_live',lambda o,m,e,c,l:l.update(release_state='LIVE'),'R425_LOCK_IDENTITY_OR_APPROVAL_DRIFT'),
 ('wrong_docket_pin',lambda o,m,e,c,l:l.update(original_docket_git_blob='b'*40),'R425_LOCK_IDENTITY_OR_APPROVAL_DRIFT'),
 ('missing_field',lambda o,m,e,c,l:l.pop('approved'),'R425_LOCK_IDENTITY_OR_APPROVAL_DRIFT'),
 ('extra_field',lambda o,m,e,c,l:l.update(paid_revenue=200),'R425_LOCK_IDENTITY_OR_APPROVAL_DRIFT'),
 ('missing_original',lambda o,m,e,c,l:o['original_articles'].pop(),'R425_REQUIRED_35_ARTICLE_COVERAGE'),
 ('missing_manifest',lambda o,m,e,c,l:m['articles'].pop(),'R425_REQUIRED_35_ARTICLE_COVERAGE'),
 ('missing_lock_article',lambda o,m,e,c,l:l['articles'].pop(),'R425_REQUIRED_35_ARTICLE_COVERAGE'),
 ('duplicate_original',lambda o,m,e,c,l:o['original_articles'][1].update(slug='article-01'),'R425_ORIGINAL_DUPLICATE_OR_INVALID_SLUG'),
 ('duplicate_manifest',lambda o,m,e,c,l:m['articles'][1].update(slug='article-01'),'R425_MANIFEST_DUPLICATE_OR_INVALID_SLUG'),
 ('duplicate_lock',lambda o,m,e,c,l:l['articles'][1].update(slug='article-01'),'R425_LOCK_DUPLICATE_OR_INVALID_SLUG'),
 ('unsafe_slug',lambda o,m,e,c,l:l['articles'][0].update(slug='../article-01'),'R425_LOCK_DUPLICATE_OR_INVALID_SLUG'),
 ('extra_lock_article',lambda o,m,e,c,l:l['articles'].append(copy.deepcopy(l['articles'][0])),'R425_REQUIRED_35_ARTICLE_COVERAGE'),
 ('route_changed',lambda o,m,e,c,l:l['articles'][0].update(canonical_path='/elsewhere/'),'R425_DUPLICATE_OR_DRIFTED_ROUTE_article-01'),
 ('manifest_route_changed',lambda o,m,e,c,l:m['articles'][0].update(canonical_path='/preparedness/wrong/'),'R425_DUPLICATE_OR_DRIFTED_ROUTE_article-01'),
 ('source_added',lambda o,m,e,c,l:l['articles'][0]['source_ids'].append('fake-source'),'R425_SOURCE_ID_ORDER_OR_SET_DRIFT_article-01'),
 ('source_removed',lambda o,m,e,c,l:l['articles'][0].update(source_ids=[]),'R425_SOURCE_ID_ORDER_OR_SET_DRIFT_article-01'),
 ('source_reordered',lambda o,m,e,c,l:(m['articles'][0]['sources'].append('source-extra'),l['articles'][0].update(source_ids=['source-extra','source-01'])),'R425_SOURCE_ID_ORDER_OR_SET_DRIFT_article-01'),
 ('duplicate_sources',lambda o,m,e,c,l:m['articles'][0]['sources'].append('source-01'),'R425_SOURCE_ID_ORDER_OR_SET_DRIFT_article-01'),
 ('source_invalid_id',lambda o,m,e,c,l:m['articles'][0].update(sources=['../bad']),'R425_SOURCE_ID_ORDER_OR_SET_DRIFT_article-01'),
 ('fork_removed',lambda o,m,e,c,l:l['articles'][14]['original_git_blobs'].pop(),'R425_UNSELECTED_ORIGINAL_FORKS_LOST_article-15'),
 ('fork_reordered',lambda o,m,e,c,l:l['articles'][14]['original_git_blobs'].reverse(),'R425_UNSELECTED_ORIGINAL_FORKS_LOST_article-15'),
 ('fork_inserted',lambda o,m,e,c,l:l['articles'][14]['original_git_blobs'].append('a'*40),'R425_UNSELECTED_ORIGINAL_FORKS_LOST_article-15'),
 ('invalid_git_blob',lambda o,m,e,c,l:o['original_articles'][0]['body_candidate_git_blobs'].append('x'*40),'R425_UNSELECTED_ORIGINAL_FORKS_LOST_article-01'),
 ('changed_original_bytes',lambda o,m,e,c,l:c.__setitem__(('article-01',o['original_articles'][0]['body_candidate_git_blobs'][0]),b'wrong'),'R425_MISSING_OR_CHANGED_ORIGINAL_CANDIDATE_article-01'),
 ('missing_original_candidate',lambda o,m,e,c,l:c.pop(('article-01',o['original_articles'][0]['body_candidate_git_blobs'][0])),'R425_MISSING_OR_CHANGED_ORIGINAL_CANDIDATE_article-01'),
 ('extra_candidate',lambda o,m,e,c,l:c.__setitem__(('extra','a'*40),b'x'),'R425_CANDIDATE_COMPLETENESS_OR_EXTRA_OBJECT'),
 ('missing_export',lambda o,m,e,c,l:e.pop('article-01'),'R425_ORIGINAL_MANIFEST_LOCK_EXPORT_IDENTITY_DRIFT'),
 ('export_changed_wp',lambda o,m,e,c,l:e.__setitem__('article-01',(e['article-01'][0]+b' EDIT',e['article-01'][1])),'R425_EXPORT_CONTENT_SHA256_DRIFT_article-01_wordpress'),
 ('export_changed_preview',lambda o,m,e,c,l:e.__setitem__('article-01',(e['article-01'][0],e['article-01'][1]+b' EDIT')),'R425_EXPORT_CONTENT_SHA256_DRIFT_article-01_preview'),
 ('export_invalid_type',lambda o,m,e,c,l:e.__setitem__('article-01',('html',b'other')),'R425_MISSING_OR_INVALID_EXPORT_LOCK_article-01_wordpress'),
 ('export_missing_channel',lambda o,m,e,c,l:e.__setitem__('article-01',[b'just one']),'R425_MISSING_PAIRED_EXPORT_article-01'),
 ('bad_export_hash',lambda o,m,e,c,l:l['articles'][0].update(wordpress_sha256='X'*64),'R425_MISSING_OR_INVALID_EXPORT_LOCK_article-01_wordpress'),
 ('extra_lock_row_key',lambda o,m,e,c,l:l['articles'][0].update(published=True),'R425_LOCK_ROW_SHAPE_article-01'),
]
for i,(name,mutate,expected) in enumerate(MODS):
    def check(self,f=mutate,err=expected):
        o,m,e,c,l=material(); f(o,m,e,c,l)
        errors,_,digest=gate.lock_audit(o,m,e,c,l)
        self.assertTrue(any(x.startswith(err) for x in errors),(err,errors))
        self.assertIsNone(digest)
    setattr(MutationTests,f'test_{i:02d}_{name}',check)

class PathAndCli(unittest.TestCase):
    def with_bundle(self):
        td=tempfile.TemporaryDirectory();root=Path(td.name)
        o,m,e,c,l=material()
        (root/'wordpress').mkdir();(root/'preview').mkdir();(root/'candidates').mkdir()
        for slug,(wp,preview) in e.items():
            (root/'wordpress'/f'{slug}.html').write_bytes(wp)
            (root/'preview'/f'{slug}.html').write_bytes(preview)
        for (slug,pin),body in c.items():
            (root/'candidates'/slug).mkdir(exist_ok=True)
            (root/'candidates'/slug/f'{pin}.txt').write_bytes(body)
        for name,obj in (('original.json',o),('manifest.json',m),('lock.json',l)):
            (root/name).write_text(json.dumps(obj))
        receipt=json.loads((ROOT/'reviews'/'r421_offer_funnel_hard_hold.json').read_text())
        (root/'receipt.json').write_text(json.dumps(receipt))
        return td,root
    def paths(self,root):
        return (root/'original.json',root/'manifest.json',root,root/'candidates',root/'lock.json',root/'receipt.json')
    def test_synthetic_bundle_can_be_read(self):
        td,root=self.with_bundle()
        try:
            o,m,e,c,l,r,raw=gate.load_bundle(*self.paths(root))
            self.assertEqual(len(e),35);self.assertEqual(len(c),36);self.assertTrue(raw)
            self.assertEqual(gate.lock_audit(o,m,e,c,l)[0],[])
        finally:td.cleanup()
    def test_missing_original_export_fails(self):
        td,root=self.with_bundle()
        try:
            (root/'wordpress'/'article-01.html').unlink()
            with self.assertRaises((OSError,ValueError)):gate.load_bundle(*self.paths(root))
        finally:td.cleanup()
    def test_unknown_export_fails(self):
        td,root=self.with_bundle()
        try:
            (root/'wordpress'/'extra.html').write_text('extra')
            with self.assertRaises(ValueError):gate.load_bundle(*self.paths(root))
        finally:td.cleanup()
    def test_extra_original_candidate_fails(self):
        td,root=self.with_bundle()
        try:
            (root/'candidates'/'article-01'/'extra.txt').write_text('extra')
            with self.assertRaises(ValueError):gate.load_bundle(*self.paths(root))
        finally:td.cleanup()
    def test_symlink_export_root_fails(self):
        td,root=self.with_bundle()
        try:
            (root/'redirect').symlink_to(root/'wordpress',target_is_directory=True)
            with self.assertRaises(ValueError):gate.safe_path(root/'redirect'/'article-01.html',root)
        finally:td.cleanup()
    def test_symlink_file_fails(self):
        td,root=self.with_bundle()
        try:
            path=root/'wordpress'/'article-01.html';path.unlink();path.symlink_to(root/'preview'/'article-01.html')
            with self.assertRaises(ValueError):gate.load_bundle(*self.paths(root))
        finally:td.cleanup()
    def test_json_duplicate_key_fails(self):
        td,root=self.with_bundle()
        try:
            (root/'lock.json').write_text('{"schema":1,"schema":2}')
            with self.assertRaises(ValueError):gate.load_bundle(*self.paths(root))
        finally:td.cleanup()
    def test_json_nonstandard_number_fails(self):
        td,root=self.with_bundle()
        try:
            (root/'lock.json').write_text('{"schema":NaN}')
            with self.assertRaises(ValueError):gate.load_bundle(*self.paths(root))
        finally:td.cleanup()
    def test_main_always_exit_two(self):
        td,root=self.with_bundle()
        try:
            result=subprocess.run([sys.executable,'-I',str(ROOT/'tools'/'r425_integrated_custody_gate.py'),
                              *(str(p) for p in self.paths(root))],capture_output=True,text=True,timeout=30)
            self.assertEqual(result.returncode,2,result.stderr)
            doc=json.loads(result.stdout);self.assertFalse(doc['eligible'])
            self.assertIn('R425_AUTHENTIC_ORIGINAL_DOCKET_GIT_BLOB_MISSING',doc['errors'])
        finally:td.cleanup()
    def test_main_missing_input_fail_closed(self):
        td,root=self.with_bundle()
        try:
            (root/'original.json').unlink()
            result=subprocess.run([sys.executable,'-I',str(ROOT/'tools'/'r425_integrated_custody_gate.py'),
                              *(str(p) for p in self.paths(root))],capture_output=True,text=True,timeout=30)
            self.assertEqual(result.returncode,2,result.stderr)
            self.assertIn('R425_AUTHENTIC_COMPLETE_EVIDENCE_UNAVAILABLE_FileNotFoundError',json.loads(result.stdout)['errors'])
        finally:td.cleanup()
    def test_real_pin_required_regardless_of_lock(self):
        o,m,e,c,l=material();receipt={'not_authentic':True}
        result=gate.validate(o,m,e,c,l,receipt,raw_original=b'not git pinned')
        self.assertFalse(result['structural_integrity_ok'])
        self.assertFalse(result['publication_approved'])

if __name__=='__main__':unittest.main()
