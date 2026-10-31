"""R17 structural custody only; all examples synthetic and release HOLD."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import source_crosswalk_truth_gate as g


def make_fixture(root: Path) -> tuple[dict, dict]:
    rows = {}
    for origin, path in g.SOURCE_PATHS.items():
        url = 'https://example.org/shared' if origin in {'base', 'food'} else f'https://example.org/{origin}'
        sid = 'same-id' if origin in {'base', 'food'} else f'{origin}-source'
        row = {'id': sid, 'url': url, 'title': f'{origin} source',
               'supports': f'{origin} read a different page portion',
               'notes': f'{origin} original reading depth and limitations',
               'human_link_check': False,
               'verified_on': None if origin == 'base' else '2026-10-30'}
        rows[origin] = {'sources': [row]}
        p = root/path
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(json.dumps(rows[origin]), encoding='utf-8')
    assert len(rows)==8
    cw = {'schema_version': 1,
          'status':'DRAFT_CROSSWALK_ALL_SHARED_SOURCE_GROUPS_UNRESOLVED',
          'source_head_commits':{**g.AUTHOR_HEADS,'food':g.KNOWN_NONAUTHOR_ALIAS['food']},
          'source_files': [],'raw_source_rows':8,'unique_source_urls':7,
          'duplicate_url_groups':1,'duplicate_id_groups':1,'groups': []}
    for o, p in g.SOURCE_PATHS.items():
        cw['source_files'].append({'origin':o,'path':p,
             'git_blob_sha':g.git_blob((root/p).read_bytes()),'count':1})
    cw['groups']=[{'url':'https://example.org/shared',
                   'canonical_url':'https://example.org/shared',
                   'review_status':g.PENDING,'reviewer':None,'reviewed_on':None,
                   'identities':[{'origin':o,'id':rows[o]['sources'][0]['id'],'row_index':0}
                                 for o in ('base','food')],
                   'variants':[{'origin':o,'row_index':0,'source_file':g.SOURCE_PATHS[o],
                                'source':copy.deepcopy(rows[o]['sources'][0])}
                               for o in ('base','food')] }]
    write_crosswalk(root,cw)
    return rows,cw


def write_crosswalk(root: Path, cw: dict) -> None:
    p=root/g.CROSSWALK
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(cw,sort_keys=True),encoding='utf-8')


EX = dict(source_rows=8, unique_urls=7, shared_urls=1,
          duplicate_id_groups=1, unread_placeholders=1)


class Fixture(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory(prefix='fvs-r17-')
        self.addCleanup(t.cleanup)
        self.root=Path(t.name)
        self.rows,self.cw=make_fixture(self.root)

    def audit(self, **kwargs):
        return g.audit(self.root,expected=EX,**kwargs)

    def write(self):
        write_crosswalk(self.root,self.cw)

    def test_structural_success_is_hold(self):
        r=self.audit()
        self.assertEqual(r['release_state'],'HOLD')
        self.assertIs(r['may_publish'],False)
        self.assertIs(r['article_claim_accuracy_verified'],False)
        self.assertIs(r['qualified_safety_clearance'],False)
        self.assertIs(r['human_source_reviews_complete'],False)

    def test_known_non_author_fixture_alias_is_visible(self):
        a=self.audit()['non_author_source_head_aliases']
        self.assertEqual(len(a),1)
        self.assertEqual(a[0]['origin'],'food')
        self.assertEqual(a[0]['actual_author_sha'],g.AUTHOR_HEADS['food'])
        self.assertEqual(a[0]['recorded_sha'],g.KNOWN_NONAUTHOR_ALIAS['food'])
        self.assertEqual(a[0]['independent_live_ref_check'],'REQUIRED')

    def test_original_author_head_does_not_need_alias(self):
        self.cw['source_head_commits']['food']=g.AUTHOR_HEADS['food']
        self.write()
        self.assertEqual(self.audit()['non_author_source_head_aliases'],[])

    def test_exact_group_custody_preserves_different_reading_depth(self):
        q=self.audit()['source_group_review_queue'][0]
        self.assertEqual(q['distinct_machine_use_explanations'],2)
        self.assertTrue(q['has_unread_placeholder'])
        self.assertEqual(q['identity_count'],2)
        self.assertEqual(q['origins'],['base','food'])

    def test_deterministic_output(self):
        a=self.audit()
        b=self.audit()
        self.assertEqual(a,b)
        self.assertEqual(len(a['audit_fingerprint']),64)

    def test_variants_can_appear_in_different_order(self):
        self.cw['groups'][0]['variants'].reverse()
        self.cw['groups'][0]['identities'].reverse()
        self.write()
        self.assertEqual(self.audit()['unresolved_shared_url_groups'],1)

    def test_reject_modified_source_record_bytes(self):
        p=self.root/g.SOURCE_PATHS['food']
        p.write_text(p.read_text()+'\n')
        with self.assertRaisesRegex(g.CustodyError,'blob drift'):
            self.audit()

    def test_reject_modified_source_note_even_if_crosswalk_is_rewritten(self):
        p=self.root/g.SOURCE_PATHS['food']
        self.rows['food']['sources'][0]['notes']='truncated'
        p.write_text(json.dumps(self.rows['food']),encoding='utf-8')
        next(x for x in self.cw['source_files'] if x['origin']=='food')['git_blob_sha']=g.git_blob(p.read_bytes())
        self.write()
        with self.assertRaisesRegex(g.CustodyError,'reading-depth drift'):
            self.audit()

    def test_source_archive_does_not_write(self):
        before={p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.audit()
        after={p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before,after)

    def test_sha1_git_blob_vector(self):
        self.assertEqual(g.git_blob(b'hello'),'b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0')

    def test_cli_failure_exit_without_public_state(self):
        proc=subprocess.run([sys.executable,'-I',str(Path(g.__file__)),'--repo-root',str(self.root)],
                            capture_output=True,text=True)
        self.assertEqual(proc.returncode,2)  # fixture intentionally differs from frozen 224
        a=json.loads(proc.stdout)
        self.assertEqual(a['release_state'],'HOLD')
        self.assertIs(a['may_publish'],False)


def make_mutation(name, action, error=''):
    def check(self):
        action(self)
        self.write()
        with self.assertRaises(g.CustodyError) as ctx:
            self.audit()
        if error:
            self.assertIn(error,str(ctx.exception))
    check.__name__='test_reject_'+name
    return check


def source_row(self, origin, field, value, *, sync_blob=True):
    self.rows[origin]['sources'][0][field]=value
    path=self.root/g.SOURCE_PATHS[origin]
    path.write_text(json.dumps(self.rows[origin]),encoding='utf-8')
    if sync_blob:
        next(x for x in self.cw['source_files'] if x['origin']==origin)['git_blob_sha']=g.git_blob(path.read_bytes())


MUTATIONS = {
    'schema_unknown':lambda s:s.cw.update(schema_version=4),
    'approved_status':lambda s:s.cw.update(status='APPROVED'),
    'may_publish_true':lambda s:s.cw.update(may_publish=True),
    'qualified_safety_true':lambda s:s.cw.update(qualified_safety_clearance=True),
    'human_source_review_true':lambda s:s.cw.update(human_source_review_complete=True),
    'missing_origin':lambda s:s.cw['source_head_commits'].pop('start'),
    'invented_origin':lambda s:s.cw['source_head_commits'].update(unknown='a'*40),
    'arbitrary_food_head':lambda s:s.cw['source_head_commits'].update(food='b'*40),
    'truncated_sha':lambda s:s.cw['source_head_commits'].update(start='c'*8),
    'switch_shelter_to_food':lambda s:s.cw['source_head_commits'].update(shelter=g.AUTHOR_HEADS['food']),
    'source_path_forged':lambda s:s.cw['source_files'][0].update(path='other.json'),
    'source_path_extra':lambda s:s.cw['source_files'].append(dict(s.cw['source_files'][0])),
    'source_path_missing':lambda s:s.cw['source_files'].pop(),
    'source_path_duplicate':lambda s:s.cw['source_files'][1].update(origin='base'),
    'source_sha_drift':lambda s:s.cw['source_files'][0].update(git_blob_sha='a'*40),
    'source_row_count_drift':lambda s:s.cw['source_files'][0].update(count=99),
    'crosswalk_raw_count_drift':lambda s:s.cw.update(raw_source_rows=99),
    'crosswalk_url_count_drift':lambda s:s.cw.update(unique_source_urls=99),
    'crosswalk_group_count_drift':lambda s:s.cw.update(duplicate_url_groups=0),
    'crosswalk_dupe_id_drift':lambda s:s.cw.update(duplicate_id_groups=0),
    'group_deleted':lambda s:s.cw['groups'].clear(),
    'group_duplicated':lambda s:s.cw['groups'].append(copy.deepcopy(s.cw['groups'][0])),
    'group_url_swapped':lambda s:s.cw['groups'][0].update(url='https://example.org/unknown'),
    'canonical_url_changed':lambda s:s.cw['groups'][0].update(canonical_url='https://example.org/redirect'),
    'group_review_approved':lambda s:s.cw['groups'][0].update(review_status='approved'),
    'group_reviewer_forged':lambda s:s.cw['groups'][0].update(reviewer='robot'),
    'group_review_date_forged':lambda s:s.cw['groups'][0].update(reviewed_on='2026-10-31'),
    'group_identity_missing':lambda s:s.cw['groups'][0]['identities'].pop(),
    'group_identity_duplicate':lambda s:s.cw['groups'][0]['identities'][1].update(origin='base'),
    'group_identity_rename':lambda s:s.cw['groups'][0]['identities'][0].update(id='renamed'),
    'group_identity_row_index':lambda s:s.cw['groups'][0]['identities'][0].update(row_index=9),
    'group_variant_missing':lambda s:s.cw['groups'][0]['variants'].pop(),
    'group_variant_duplicate':lambda s:s.cw['groups'][0]['variants'][1].update(origin='base',source=copy.deepcopy(s.cw['groups'][0]['variants'][0]['source'])),
    'group_variant_file_swap':lambda s:s.cw['groups'][0]['variants'][0].update(source_file=g.SOURCE_PATHS['food']),
    'group_variant_truncated_supports':lambda s:s.cw['groups'][0]['variants'][0]['source'].update(supports=''),
    'group_variant_truncated_notes':lambda s:s.cw['groups'][0]['variants'][1]['source'].update(notes=''),
    'group_variant_title_mutation':lambda s:s.cw['groups'][0]['variants'][1]['source'].update(title='wrong source'),
    'group_variant_fake_human':lambda s:s.cw['groups'][0]['variants'][1]['source'].update(human_link_check=True),
    'source_real_fake_human':lambda s:source_row(s,'food','human_link_check',True),
    'source_machine_verified_bool':lambda s:source_row(s,'food','verified_on',True),
    'source_url_credentials':lambda s:source_row(s,'start','url','https://user:password@example.org/start'),
    'source_url_http':lambda s:source_row(s,'start','url','http://example.org/start'),
    'source_url_fragment':lambda s:source_row(s,'start','url','https://example.org/start#jump'),
    'source_url_missing':lambda s:source_row(s,'start','url',None),
    'source_url_null_byte':lambda s:source_row(s,'start','url','https://example.org/\x00start'),
    'source_url_host_missing':lambda s:source_row(s,'start','url','https:///missing-host'),
    'source_url_scheme_relative':lambda s:source_row(s,'start','url','//example.org/start'),
    'source_url_bad_scheme':lambda s:source_row(s,'start','url','javascript:alert(1)'),
    'source_url_too_long':lambda s:source_row(s,'start','url','https://example.org/'+'z'*3000),
    'source_duplicate_id_inventory':lambda s:source_row(s,'start','id','same-id'),
    'source_placeholder_inventory':lambda s:source_row(s,'start','verified_on',None),
    'source_url_group_inventory':lambda s:source_row(s,'start','url','https://example.org/shared'),
}

for name,action in MUTATIONS.items():
    setattr(Fixture,'test_reject_'+name,make_mutation(name,action))


if __name__=='__main__':
    unittest.main()
