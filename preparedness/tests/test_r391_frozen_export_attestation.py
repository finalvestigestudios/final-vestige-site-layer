"""Synthetic only: never authenticates safety or a WordPress production release."""
from __future__ import annotations
import copy
import importlib.util
from pathlib import Path
import os
import tempfile
import unittest

P = Path(__file__).resolve().parents[1] / 'tools' / 'r391_frozen_export_attestation.py'
sp = importlib.util.spec_from_file_location('r391', P)
G = importlib.util.module_from_spec(sp); sp.loader.exec_module(G)


class FrozenExportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.wp = Path(self.tmp.name) / 'wp'; self.pv = Path(self.tmp.name) / 'preview'
        self.wp.mkdir(); self.pv.mkdir()
        self.original = [f'guide-{i:02d}' for i in range(35)]
        self.slugs = self.original + [f'tool-{i:02d}' for i in range(15)]
        for slug in self.slugs:
            (self.wp / (slug + '.html')).write_text(f'wp {slug}', encoding='utf-8')
            (self.pv / (slug + '.html')).write_text(f'preview {slug}', encoding='utf-8')

    def reports(self):
        wp = G._snapshot(self.wp)['files']; pv = G._snapshot(self.pv)['files']
        rows = [{'slug': s, 'wp_sha256': wp[s]['sha256'], 'preview_sha256': pv[s]['sha256'],
                 'wp_bytes': wp[s]['size'], 'preview_bytes': pv[s]['size'],
                 'errors': [], 'release_allowed': False, 'qualified_review_required': True}
                for s in sorted(wp)]
        render = {'status': 'RENDER_PARITY_REVIEW_HARD_HOLD','errors':[],
                  'publication_approved':False,'qualified_safety_approved':False}
        anchor = {'status': 'CLAIM_POSITION_REVIEW_HARD_HOLD','errors':[],
                  'publication_approved':False,'qualified_safety_approved':False}
        full = {'status':'ALL_EXPORT_BYTES_REVIEW_HARD_HOLD','errors':[], 'exports':rows}
        return {'render':render,'anchor':anchor,'full':full}

    def audit(self, callback=None, originals=None):
        return G.audit_frozen(self.wp,self.pv,self.original if originals is None else originals, callback or self.reports)

    def failed(self, code=None, callback=None):
        x=self.audit(callback)
        self.assertEqual(x['status'],'INVALID_HARD_HOLD', x)
        self.assertFalse(x['publication_approved'])
        self.assertFalse(x['qualified_safety_approved'])
        self.assertFalse(x['live_release_allowed'])
        if code:self.assertTrue(any(code in e for e in x['errors']),x['errors'])
        return x

    def test_valid_50_synthetic_only_review(self):
        x=self.audit();self.assertEqual(x['status'],'FROZEN_EXPORT_REVIEW_HARD_HOLD')
        self.assertEqual(x['matched_snapshot_pairs'],50)
        self.assertFalse(x['publication_approved']); self.assertFalse(x['merchant_offer_verified'])

    def test_sha_repeatable(self):
        self.assertEqual(self.audit()['snapshot_sha256'], self.audit()['snapshot_sha256'])

    def test_distinct_wp_preview_bytes_are_acceptable(self):
        self.assertNotEqual(G._snapshot(self.wp)['files']['guide-00']['sha256'], G._snapshot(self.pv)['files']['guide-00']['sha256'])
        self.assertEqual(self.audit()['status'], 'FROZEN_EXPORT_REVIEW_HARD_HOLD')

    def test_mutate_during_render(self):
        def f():
            r=self.reports();(self.wp/'guide-00.html').write_text('different')
            return r
        self.failed('EXPORT_MUTATION_DURING_VALIDATION',f)

    def test_mutate_before_reports_generated(self):
        def f():
            (self.wp/'guide-00.html').write_text('different')
            return self.reports()
        self.failed('EXPORT_MUTATION_DURING_VALIDATION',f)

    def test_swap_identical_file_during_audit(self):
        def f():
            r=self.reports()
            old=self.wp/'guide-00.html'; new=self.wp/'newfile'
            new.write_bytes(old.read_bytes()); os.replace(new,old)
            return r
        self.failed('EXPORT_MUTATION_DURING_VALIDATION',f)

    def test_modified_file_restored_during_callback_detected_when_timestamp_changes(self):
        def f():
            r=self.reports(); p=self.wp/'guide-00.html'
            p.write_text('tampered');p.write_text('wp guide-00')
            return r
        self.failed('EXPORT_MUTATION_DURING_VALIDATION',f)

    def test_new_file_race(self):
        def f():
            r=self.reports(); (self.wp/'tool-extra.html').write_text('new')
            return r
        self.failed('EXPORT_MUTATION_DURING_VALIDATION',f)

    def test_deleted_file_race(self):
        def f():
            r=self.reports(); (self.wp/'tool-00.html').unlink()
            return r
        self.failed('EXPORT_MUTATION_DURING_VALIDATION',f)

    def test_symlink_entry(self):
        (self.wp/'guide-00.html').unlink();(self.wp/'guide-00.html').symlink_to(self.pv/'guide-00.html')
        self.failed('SNAPSHOT_UNAVAILABLE')

    def test_hardlinked_entry(self):
        orig=self.wp/'guide-00.html';os.link(orig,self.wp/'extra')
        self.failed('SNAPSHOT_UNAVAILABLE')

    def test_unexpected_file(self):
        (self.wp/'note.txt').write_text('x')
        self.failed('SNAPSHOT_UNAVAILABLE')

    def test_empty_file(self):
        (self.wp/'guide-00.html').write_bytes(b'')
        self.failed('SNAPSHOT_UNAVAILABLE')

    def test_overlarge_file(self):
        with (self.wp/'guide-00.html').open('wb') as f:f.truncate(3_000_001)
        self.failed('SNAPSHOT_UNAVAILABLE')

    def test_missing_dir(self):
        for f in self.pv.iterdir():f.unlink()
        self.pv.rmdir();self.failed('SNAPSHOT_UNAVAILABLE')

    def test_directory_symlink(self):
        self.wp.rename(Path(self.tmp.name)/'orig')
        self.wp.symlink_to(Path(self.tmp.name)/'orig',target_is_directory=True)
        self.failed('SNAPSHOT_UNAVAILABLE')

    def test_missing_preview_pair(self):
        (self.pv/'tool-02.html').unlink();self.failed('INCOMPLETE_OR_NONPAIR_EXPORT_SET')

    def test_narrow_slate(self):
        x=self.audit(originals=self.original[:-1]);self.assertEqual(x['status'],'INVALID_HARD_HOLD')

    def test_duplicate_original(self):
        x=self.audit(originals=self.original[:-1]+[self.original[0]])
        self.assertEqual(x['status'],'INVALID_HARD_HOLD')

    def test_invalid_slug(self):
        x=self.audit(originals=self.original[:-1]+['../foo'])
        self.assertEqual(x['status'],'INVALID_HARD_HOLD')

    def test_callback_raises_oserror(self):
        self.failed('SNAPSHOT_UNAVAILABLE',lambda:(_ for _ in ()).throw(OSError('IO')))

    def test_runtime_exception_fails_closed(self):
        self.failed('SNAPSHOT_UNAVAILABLE', lambda: (_ for _ in ()).throw(RuntimeError('unexpected')))

    def test_empty_callback_report(self):
        self.failed('MISSING_INDEPENDENT_AUDITS',lambda:{})

    def test_r390_missing_row(self):
        def f():
            r=self.reports();r['full']['exports'].pop();return r
        self.failed('R390_EXPORT_ROWS_UNBOUND',f)

    def test_r390_extra_row(self):
        def f():
            r=self.reports();r['full']['exports'].append(copy.deepcopy(r['full']['exports'][0]));return r
        self.failed('R390_EXPORT_ROWS_UNBOUND',f)

    def test_r390_duplicate_slug(self):
        def f():
            r=self.reports();r['full']['exports'][1]['slug']=r['full']['exports'][0]['slug'];return r
        self.failed('R390_EXPORT_ROWS_UNBOUND',f)

    def test_r390_unmatched_slug(self):
        def f():
            r=self.reports();r['full']['exports'][0]['slug']='impostor';return r
        self.failed('R390_EXPORT_ROWS_UNBOUND',f)

    def test_no_r390_report(self):
        def f():
            r=self.reports();del r['full'];return r
        self.failed('MISSING_INDEPENDENT_AUDITS',f)


def inject(name, change, expected):
    def test(self):
        def f():
            r=self.reports();change(r);return r
        self.failed(expected,f)
    setattr(FrozenExportTests, 'test_'+name, test)


for field,value in [('wp_sha256','0'*64),('preview_sha256','0'*64),('wp_bytes',2000),
                    ('preview_bytes',2000),('errors',['hidden-citation']),('release_allowed',True),
                    ('qualified_review_required',False)]:
    inject('r390_'+field+'_mutated',lambda r,f=field,v=value: r['full']['exports'][0].__setitem__(f,v),
           'R390_HASH_OR_REVIEW_DRIFT')

for label,status in [('render','RENDER_PARITY_REVIEW_HARD_HOLD'),('anchor','CLAIM_POSITION_REVIEW_HARD_HOLD'),
                     ('full','ALL_EXPORT_BYTES_REVIEW_HARD_HOLD')]:
    inject(label+'_incorrect_status',lambda r,l=label:r[l].__setitem__('status','PASS'),
           'R390_AUDIT_FAILED' if label=='full' else 'DEPENDENT_AUDIT_NOT_CLEAR')
    inject(label+'_errors',lambda r,l=label:r[l].__setitem__('errors',['failing']),
           'R390_AUDIT_FAILED' if label=='full' else 'DEPENDENT_AUDIT_NOT_CLEAR')

for label in ('render','anchor'):
    for field,value in [('publication_approved',True),('qualified_safety_approved',True)]:
        inject(label+'_'+field,lambda r,l=label,f=field,v=value:r[l].__setitem__(f,v),
               'DEPENDENT_AUDIT_NOT_CLEAR')

# Twelve remaining distinct source/render drift scenarios across original and supplemental pairs.
for i in range(12):
    def _case(self, idx=i):
        slug=self.slugs[idx+35] if idx<6 else self.slugs[idx-6]
        target=self.wp if idx%2==0 else self.pv
        def f():
            r=self.reports();(target/(slug+'.html')).write_text('changed in callback')
            return r
        self.failed('EXPORT_MUTATION_DURING_VALIDATION',f)
    setattr(FrozenExportTests, 'test_export_race_scenario_'+str(i), _case)

if __name__ == '__main__':unittest.main()