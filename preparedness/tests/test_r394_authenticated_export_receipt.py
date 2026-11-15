"""Synthetic-only R394 object/export review tests. NOT QD or native-build evidence."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
import r394_authenticated_export_receipt as mod

ORIG_BRANCHES = list(mod.BRANCH_PINS)


def make_inputs(root):
    wp, preview = root / 'wp', root / 'private'
    wp.mkdir(); preview.mkdir()
    objects = []
    store = {}
    def add(path, records):
        obj = {'path': path, 'selected_sha': None, 'variants': []}
        for branch, raw in records:
            sha = mod.originals.blob_sha(raw)
            store[sha] = raw
            obj['variants'].append({'branch': branch, 'sha': sha, 'size': len(raw)})
        objects.append(obj)
    for n in range(35):
        slug = f'guide-{n:02d}'
        branch = ORIG_BRANCHES[n % 7]
        rec = [(branch, f'<article><p>Original {slug} paragraph {{' + '{cite:official-source}}' + '</p></article>')]
        body = [(b, content.encode()) for b, content in rec]
        meta = [(branch, json.dumps({'slug': slug, 'status': {'publish':'draft'},
              'safety_review': {'state':'pending'},
              'source_use': {'official-source': 'This source addresses the indicated claim'}},
              sort_keys=True).encode())]
        if n < 4:
            shelter = ORIG_BRANCHES[7]
            body.append((shelter, (f'<article><p>Original {slug} different but unapproved source context '
                                   '{{cite:official-source}}</p></article>').encode()))
            meta.append((shelter, json.dumps({'slug':slug, 'status':{'publish':'draft'},
                  'safety_review':{'state':'pending'}, 'source_use':{
                  'official-source':'Alternate unapproved reading scope for human review'}},
                  sort_keys=True).encode()))
        add(f'preparedness/content/articles/{slug}.body.html', body)
        add(f'preparedness/content/articles/{slug}.meta.json', meta)
    for n in range(7):
        first = (ORIG_BRANCHES[n], f'{{"source":{n},"state":"pending"}}'.encode())
        records = [first]
        if n == 0:
            records.append((ORIG_BRANCHES[8], b'{"source":0,"state":"unreviewed-alternate"}'))
        add(f'preparedness/sources/fragments/cluster-{n}.json', records)
    manifest = {'release_state':'DRAFT_HARD_HOLD','article_count':35,'conflict_count':9,
                'branch_pins':[{'branch':b,'sha':s} for b,s in mod.BRANCH_PINS.items()],
                'objects': objects}
    manifest_bytes = mod.canonical(manifest)
    orig = mod.originals.build_packet(manifest, store.__getitem__)
    assert orig['status'] == 'REVIEW_PACKET_HARD_HOLD', orig['errors']
    assert len(orig['unselected_conflicts']) == 9
    candidates = lambda row: [{'branch':v['branch'],'body_sha':v['body_sha']} for v in row['variants']]
    article_rows = orig['articles']
    render = {'status':'RENDER_PARITY_REVIEW_HARD_HOLD','errors':[],
              'publication_approved':False,'qualified_safety_approved':False,
              'articles':[{'slug':r['slug'],'matching_variant_candidates':candidates(r)} for r in article_rows]}
    anchor = {'status':'CLAIM_POSITION_REVIEW_HARD_HOLD','errors':[],
              'publication_approved':False,'qualified_safety_approved':False,
              'articles':[{'slug':r['slug'],'matching_original_candidates':candidates(r)} for r in article_rows]}
    for n in range(50):
        slug = f'guide-{n:02d}' if n < 35 else f'page-{n:02d}'
        (wp / f'{slug}.html').write_text(f'<article><p>Original {slug} private draft WP.</p></article>', encoding='utf-8')
        (preview / f'{slug}.html').write_text(f'<article><p>Original {slug} private preview.</p></article>', encoding='utf-8')
    snapshot_wp = mod.frozen_audit._snapshot(wp)['files']
    snapshot_pv = mod.frozen_audit._snapshot(preview)['files']
    exports = [{'slug':s, 'wp_sha256':snapshot_wp[s]['sha256'], 'preview_sha256':snapshot_pv[s]['sha256'],
                'wp_bytes':snapshot_wp[s]['size'], 'preview_bytes':snapshot_pv[s]['size'],
                'errors':[], 'release_allowed':False, 'qualified_review_required':True}
               for s in sorted(snapshot_wp)]
    full = {'status':'ALL_EXPORT_BYTES_REVIEW_HARD_HOLD','errors':[],
            'publication_approved':False,'qualified_safety_approved':False,'exports':exports}
    inventory = {'preview':{s:v['sha256'] for s,v in sorted(snapshot_pv.items())},
                 'wp':{s:v['sha256'] for s,v in sorted(snapshot_wp.items())}}
    frozen = {'status':'FROZEN_EXPORT_REVIEW_HARD_HOLD','release_state':'DRAFT_HARD_HOLD',
              'publication_approved':False,'qualified_safety_approved':False,'errors':[],
              'matched_snapshot_pairs':50,'snapshot_sha256':mod._sha256(mod.canonical(inventory)),
              'reports':{'render':render,'anchor':anchor,'full':full}}
    integrated = {'status':'INTEGRATED_REVIEW_HARD_HOLD','release_state':'DRAFT_HARD_HOLD',
                  'publication_approved':False,'qualified_safety_approved':False,'errors':[],
                  'counts':{'original_articles':35,'unselected_manuscript_forks':9,
                            'unselected_source_collisions':5,'wp_exports':50,
                            'private_previews':50,'candidate_intersection_articles':35},
                  'candidate_intersections':[{'slug':r['slug'], 'matching_review_candidates':candidates(r),
                                              'auto_selected':False,'qualified_review_required':True} for r in article_rows]}
    witness = mod.cross_gate.check(orig, integrated, frozen)
    assert witness['status'] == 'CROSS_GATE_WITNESS_REVIEW_HARD_HOLD', witness['errors']
    return {'manifest_bytes':manifest_bytes,'store':store,'orig':orig,'integrated':integrated,
            'frozen':frozen,'witness':witness,'wp':wp,'preview':preview,
            'manifest_sha':mod.originals.blob_sha(manifest_bytes)}


def run(data, **kwargs):
    return mod.attest(data['manifest_bytes'], data['store'].__getitem__,
                      data['orig'], data['integrated'], data['frozen'],
                      data['witness'], data['wp'], data['preview'],
                      expected_manifest_sha=kwargs.get('expected_manifest_sha',data['manifest_sha']),
                      expected_branch_pins=kwargs.get('expected_branch_pins',mod.BRANCH_PINS))


def mutations():
    return [
        lambda d:d['orig'].update(status='PASS'),
        lambda d:d['orig'].update(errors=['not cleared']),
        lambda d:d['orig'].update(release='APPROVED'),
        lambda d:d['orig'].update(publication_approved=True),
        lambda d:d['orig'].update(qualified_safety_approved=True),
        lambda d:d['orig']['articles'].pop(),
        lambda d:d['orig']['articles'][0].update(slug='a-fake-guide'),
        lambda d:d['orig']['articles'][0]['variants'][0].update(body_sha='e'*40),
        lambda d:d['orig']['articles'][0]['variants'][0].update(meta_sha='d'*40),
        lambda d:d['orig']['articles'][0]['variants'][0].update(words=100000),
        lambda d:d['orig']['articles'][0]['variants'][0].update(safety_state='approved'),
        lambda d:d['orig']['articles'][0]['variants'][0].update(source_use={}),
        lambda d:d['orig']['articles'][0]['variants'][0].update(blocks=[]),
        lambda d:d['orig']['review_deltas'].append({'fake':'review'}),
        lambda d:d['orig']['unselected_conflicts'].pop(),
        lambda d:d['orig']['unselected_conflicts'][0].update(selected_sha='a'*40),
        lambda d:d['integrated'].update(publication_approved=True),
        lambda d:d['integrated'].update(status='PASS'),
        lambda d:d['integrated']['candidate_intersections'][0].update(auto_selected=True),
        lambda d:d['integrated']['candidate_intersections'][0]['matching_review_candidates'][0].update(body_sha='c'*40),
        lambda d:d['integrated']['counts'].update(unselected_source_collisions=4),
        lambda d:d['integrated']['counts'].update(unselected_manuscript_forks=8),
        lambda d:d['frozen'].update(qualified_safety_approved=True),
        lambda d:d['frozen'].update(snapshot_sha256='e'*64),
        lambda d:d['frozen'].update(matched_snapshot_pairs=49),
        lambda d:d['frozen']['reports']['anchor'].update(status='PASS'),
        lambda d:d['frozen']['reports']['render']['articles'].pop(),
        lambda d:d['frozen']['reports']['full']['exports'].pop(),
        lambda d:d['frozen']['reports']['full']['exports'][0].update(wp_sha256='e'*64),
        lambda d:d['frozen']['reports']['full']['exports'][0].update(preview_sha256='e'*64),
        lambda d:d['frozen']['reports']['full']['exports'][0].update(wp_bytes=1),
        lambda d:d['frozen']['reports']['full']['exports'][0].update(preview_bytes=1),
        lambda d:d['frozen']['reports']['full']['exports'][0].update(release_allowed=True),
        lambda d:d['frozen']['reports']['full']['exports'][0].update(qualified_review_required=False),
        lambda d:d['frozen']['reports']['full']['exports'][0].update(errors=['hidden']),
        lambda d:d['witness'].update(status='PASS'),
        lambda d:d['witness'].update(publication_approved=True),
        lambda d:d['witness'].update(witness_sha256='0'*64),
        lambda d:d['witness'].update(article_count=34),
        lambda d:(d['wp']/'guide-00.html').write_text('<article>Changed!</article>',encoding='utf-8'),
        lambda d:(d['preview']/'guide-00.html').write_text('<article>Changed!</article>',encoding='utf-8'),
        lambda d:(d['wp']/'guide-00.html').unlink(),
        lambda d:(d['preview']/'guide-00.html').unlink(),
        lambda d:(d['wp']/'page-49.html').unlink(),
        lambda d:(d['preview']/'page-49.html').unlink(),
        lambda d:(d['wp']/'surprise.html').write_text('<p>Extra</p>',encoding='utf-8'),
        lambda d:(d['preview']/'surprise.html').write_text('<p>Extra</p>',encoding='utf-8'),
        lambda d:(d['wp']/'bad name.html').write_text('<p>Unsafe</p>',encoding='utf-8'),
        lambda d:(d['preview']/'bad name.html').write_text('<p>Unsafe</p>',encoding='utf-8'),
    ]


class R394Tests(unittest.TestCase):
    def setUp(self):
        self.ctx = tempfile.TemporaryDirectory(prefix='r394-')
        self.data = make_inputs(Path(self.ctx.name))
    def tearDown(self):
        self.ctx.cleanup()
    def test_valid_authentic_synthetic_still_hold(self):
        a=run(self.data)
        self.assertEqual(a['status'],'AUTHENTIC_OBJECT_AND_EXPORT_REVIEW_HARD_HOLD',a['errors'])
        self.assertFalse(a['qualified_safety_approved'])
        self.assertEqual(a['counts'], {'original_articles':35,'original_conflicts':9,
                                      'original_manifest_objects':77,'wp_private_pairs':50})
    def test_receipt_is_stable(self):
        self.assertEqual(run(self.data)['custody_sha256'], run(self.data)['custody_sha256'])
    def test_manifest_pin_must_match(self):
        self.assertIn('ORIGINAL_MANIFEST_GIT_BLOB_PIN_MISMATCH',run(self.data,expected_manifest_sha='a'*40)['errors'])
    def test_original_branches_must_match(self):
        self.assertIn('ORIGINAL_CONTRIBUTOR_BRANCH_PIN_DRIFT',run(self.data,expected_branch_pins={})['errors'])
    def test_missing_native_cli_stays_fail_closed(self):
        self.assertEqual(mod.main(['--repo','/no-repository','--original','/missing',
            '--integrated','/missing','--frozen','/missing','--witness','/missing',
            '--wp','/missing','--preview','/missing']), 2)
    def test_custody_digest_changes_with_evidence_not_only_counts(self):
        initial=run(self.data)['custody_sha256']
        self.data['integrated']['extra_review_note']='not a safety approval'
        updated=run(self.data)
        self.assertNotEqual(initial,updated['custody_sha256'])
    def test_unreadable_object_never_passes(self):
        key=next(iter(self.data['store']))
        del self.data['store'][key]
        self.assertEqual(run(self.data)['status'],'INVALID_HARD_HOLD')
    def test_symlink_export_rejected(self):
        target=self.data['wp']/'guide-00.html'
        target.unlink()
        target.symlink_to(self.data['wp']/'guide-01.html')
        self.assertEqual(run(self.data)['status'],'INVALID_HARD_HOLD')
    def test_hardlinked_export_rejected(self):
        import os
        target=self.data['wp']/'guide-00.html'
        target.unlink()
        os.link(self.data['wp']/'guide-01.html',target)
        self.assertEqual(run(self.data)['status'],'INVALID_HARD_HOLD')


def _make_case(idx):
    def case(self):
        mutations()[idx](self.data)
        r = run(self.data)
        self.assertEqual(r['status'],'INVALID_HARD_HOLD',f'mutation #{idx}: {r}')
        self.assertFalse(r['publication_approved'])
        self.assertIsNone(r['custody_sha256'])
    return case

for index in range(len(mutations())):
    setattr(R394Tests,f'test_mutation_{index:02d}',_make_case(index))

if __name__ == '__main__':
    unittest.main()
