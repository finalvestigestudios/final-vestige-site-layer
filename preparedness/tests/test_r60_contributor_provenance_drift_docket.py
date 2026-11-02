"""R60 standalone synthetic and Git plumbing tests (no network, no CMS writes)."""
from __future__ import annotations
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('r60_tested',
    Path(__file__).parents[1] / 'tools/r60_contributor_provenance_drift_docket.py')
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

COUNTS = {'start': 4, 'shelter': 4, 'food': 4, 'health': 3,
          'hist-food': 6, 'hist-home': 5, 'hist-field': 3}


def h(s):
    return hashlib.sha1(s.encode()).hexdigest()


class Fixture:
    def __init__(self):
        self.manifest = {'schema_version': 1, 'release_state': 'HOLD',
                         'may_publish': False, 'independent_human_source_checks_verified': 0,
                         'branches': []}
        self.heads, self.data, self.changed, self.branches = {}, {}, {}, {}
        for group, num in COUNTS.items():
            sha = h('frozen-' + group)
            self.heads[group] = sha
            self.branches[group] = 'claude/prep-' + group
            paths = []
            for i in range(num):
                slug = group + '-guide-' + str(i)
                body = 'preparedness/content/articles/' + slug + '.body.html'
                meta = 'preparedness/content/articles/' + slug + '.meta.json'
                paths.append((body, ('<p>{{cite:src-'+group+'}} two mentions '
                                      '{{cite:src-'+group+'}}</p>\n').encode()))
                paths.append((meta, json.dumps({'slug': slug, 'source_use': {},
                    'status': {'publish': 'draft'}, 'safety_review': {'state': 'pending'}},
                    sort_keys=True).encode()))
            paths.append(('preparedness/docs/CLUSTER-' + group + '.md', b'# Frozen notes\n'))
            paths.append(('preparedness/sources/fragments/' + group + '.json',
                json.dumps({'sources': [{'id': 'src-'+group, 'url': 'https://example.invalid/'+group,
                         'human_link_check': False}]}).encode()))
            rows = []
            for path, data in paths:
                self.data[(sha, path)] = data
                rows.append({'path': path, 'contributor_blob_sha': gate.blob_sha(data)})
            self.manifest['branches'].append({'name': group,
                'contributor_commit_sha': sha, 'files': rows})
        assert sum(len(b['files']) for b in self.manifest['branches']) == 72

    def branch(self, group):
        return next(b for b in self.manifest['branches'] if b['name'] == group)

    def change(self, group='hist-food', path=None, new=b'changed substantive content\n'):
        entry = self.branch(group)
        prior, live = self.heads[group], h('observed-' + group)
        old = entry['contributor_commit_sha']
        # Each new commit contains the same frozen tree plus changed paths.
        if prior == old:
            for row in entry['files']:
                self.data[(live, row['path'])] = self.data[(old, row['path'])]
            self.changed[(old, live)] = []
        self.heads[group] = live
        if path is None:
            path = next(x['path'] for x in entry['files'] if x['path'].endswith('.body.html'))
        self.data[(live, path)] = new
        if path not in self.changed[(old, live)]:
            self.changed[(old, live)].append(path)
        return path

    def lookup(self, sha, path):
        value = self.data.get((sha, path))
        return gate.blob_sha(value) if value is not None else None

    def read(self, sha, path):
        return self.data[(sha, path)]

    def diff(self, before, after):
        return self.changed.get((before, after), [])

    def validate_frozen(self, m):
        if m != self.manifest:
            raise gate.DriftHold('frozen manifest not the tested baseline')
        if sum(len(b['files']) for b in m['branches']) != 72:
            raise gate.DriftHold('72 frozen paths required')
        if sum(COUNTS.values()) != 29:
            raise gate.DriftHold('29 authored articles required')

    def args(self):
        return (self.manifest, self.heads, self.diff, self.lookup, self.read,
                self.validate_frozen, self.branches)

    def run(self):
        return gate.report(*self.args())


class BaselineTests(unittest.TestCase):
    def setUp(self):
        self.f = Fixture()

    def test_seven_branches_and_72_scoped_paths(self):
        x = self.f.run()
        self.assertEqual(x['checked_clusters'], 7)
        self.assertEqual(x['changed_file_count'], 0)
        self.assertEqual(len(x['moved_contributor_heads']), 0)

    def test_no_drift_is_not_approval(self):
        x = self.f.run()
        for field in ('may_publish', 'qualified_safety_clearance',
                      'independent_QD_approval', 'human_source_links_verified'):
            self.assertIs(x[field], False)
        self.assertEqual(x['release_state'], 'HOLD')

    def test_original_data_not_mutated(self):
        m = copy.deepcopy(self.f.manifest)
        self.f.change()
        self.f.run()
        self.assertEqual(self.f.manifest, m)

    def test_content_change_is_not_lineending_only(self):
        self.f.change()
        r = self.f.run()['changed_files'][0]
        self.assertEqual(r['classification_NOT_APPROVAL'], 'CONTENT_OR_SOURCE_ID_CHANGE')
        self.assertFalse(r['normalized_line_endings_equivalent'])

    def test_exact_line_ending_conversions_explicit(self):
        p = self.f.branch('hist-food')['files'][0]['path']
        old = self.f.read(self.f.heads['hist-food'], p)
        self.f.change(path=p, new=old.replace(b'\n', b'\r\n'))
        x = self.f.run()['changed_files'][0]
        self.assertEqual(x['classification_NOT_APPROVAL'], 'LINE_ENDINGS_ONLY')

    def test_frozen_scope_row_preserved(self):
        self.f.change()
        self.assertTrue(self.f.run()['changed_files'][0]['in_frozen_72_path_scope'])

    def test_missing_diff_file_fails_closed(self):
        self.f.change()
        self.f.changed.clear()
        with self.assertRaisesRegex(gate.DriftHold, 'omitted'):
            self.f.run()

    def test_invented_diff_file_fails_closed(self):
        self.f.change()
        pair = next(iter(self.f.changed))
        self.f.changed[pair].append('preparedness/docs/CLUSTER-start.md')
        with self.assertRaises(gate.DriftHold):
            self.f.run()

    def test_new_source_addition_flag(self):
        group = 'hist-home'
        p = 'preparedness/sources/fragments/'+group+'.json'
        o = json.loads(self.f.read(self.f.heads[group], p))
        o['sources'].append({'id': 'new-archive', 'url': 'https://example.invalid/new',
                             'human_link_check': False})
        self.f.change(group, p, json.dumps(o).encode())
        c = self.f.run()['changed_files'][0]['source_and_citation_change_clues_NOT_VERIFIED']
        self.assertEqual(c['source_ids_added'], ['new-archive'])
        self.assertEqual(c['human_link_checks_after'], 0)

    def test_source_removal_flag(self):
        group = 'hist-home'
        p = 'preparedness/sources/fragments/'+group+'.json'
        self.f.change(group, p, b'{"sources":[]}')
        c = self.f.run()['changed_files'][0]['source_and_citation_change_clues_NOT_VERIFIED']
        self.assertEqual(c['source_ids_removed'], ['src-hist-home'])

    def test_same_source_id_url_change_is_flagged(self):
        group = 'food'
        p = 'preparedness/sources/fragments/food.json'
        obj = json.loads(self.f.read(self.f.heads[group], p))
        obj['sources'][0]['url'] = 'https://example.invalid/changed'
        self.f.change(group, p, json.dumps(obj).encode())
        c = self.f.run()['changed_files'][0]['source_and_citation_change_clues_NOT_VERIFIED']
        self.assertEqual(c['source_ids_modified'], ['src-food'])

    def test_meta_source_use_renaming_flag(self):
        group = 'hist-food'
        p = self.f.branch(group)['files'][1]['path']
        meta = json.loads(self.f.read(self.f.heads[group], p))
        meta['source_use'] = {'renamed-source': 'context'}
        self.f.change(group, p, json.dumps(meta).encode())
        c = self.f.run()['changed_files'][0]['source_and_citation_change_clues_NOT_VERIFIED']
        self.assertEqual(c['source_use_added'], ['renamed-source'])

    def test_safety_state_change_remains_pending(self):
        group = 'hist-home'
        p = self.f.branch(group)['files'][1]['path']
        meta = json.loads(self.f.read(self.f.heads[group], p))
        meta['safety_review']['state'] = 'approved'
        self.f.change(group, p, json.dumps(meta).encode())
        x = self.f.run()
        self.assertTrue(x['changed_files'][0]['source_and_citation_change_clues_NOT_VERIFIED']['safety_review_changed'])
        self.assertFalse(x['qualified_safety_clearance'])

    def test_publication_state_change_not_approval(self):
        group = 'food'
        p = self.f.branch(group)['files'][1]['path']
        meta = json.loads(self.f.read(self.f.heads[group], p))
        meta['status']['publish'] = 'publish'
        self.f.change(group, p, json.dumps(meta).encode())
        x = self.f.run()
        self.assertTrue(x['changed_files'][0]['source_and_citation_change_clues_NOT_VERIFIED']['publication_status_changed'])
        self.assertFalse(x['may_publish'])

    def test_citation_occurrence_count_preserved(self):
        group = 'hist-food'
        p = self.f.branch(group)['files'][0]['path']
        self.f.change(group, p, b'{{cite:replacement}} {{cite:replacement}} {{cite:replacement}}')
        c = self.f.run()['changed_files'][0]['source_and_citation_change_clues_NOT_VERIFIED']
        self.assertEqual(c['citation_added_occurrences'], {'replacement': 3})
        self.assertEqual(c['citation_removed_occurrences'], {'src-hist-food': 2})

    def test_added_new_preparedness_path_kept(self):
        self.f.change(path='preparedness/docs/CLUSTER-review-new.md')
        x = self.f.run()['changed_files'][0]
        self.assertFalse(x['in_frozen_72_path_scope'])
        self.assertEqual(x['classification_NOT_APPROVAL'], 'ADDED')

    def test_deleted_existing_path_kept(self):
        g='hist-home'; p='preparedness/docs/CLUSTER-hist-home.md'
        self.f.change(g,p)
        del self.f.data[(self.f.heads[g],p)]
        x=self.f.run()['changed_files'][0]
        self.assertEqual(x['classification_NOT_APPROVAL'], 'DELETED')

    def test_multiple_changed_groups_sorted(self):
        self.f.change('hist-home')
        self.f.change('hist-food')
        x=self.f.run()
        self.assertEqual([r['cluster'] for r in x['changed_files']], ['hist-food','hist-home'])
        self.assertEqual(len(x['moved_contributor_heads']),2)

    def test_deterministic_repeated_report(self):
        self.f.change()
        self.assertEqual(self.f.run(), self.f.run())

    def test_regeneration_accepts_unchanged_report_only(self):
        self.f.change()
        self.assertTrue(gate.verify_report(self.f.run(), *self.f.args()))

    def test_invalid_missing_cluster_fails(self):
        self.f.heads.pop('health')
        with self.assertRaises(gate.DriftHold): self.f.run()

    def test_unknown_observed_cluster_fails(self):
        self.f.heads['other']=h('other')
        with self.assertRaises(gate.DriftHold): self.f.run()

    def test_injected_invalid_commit_fails(self):
        self.f.heads['hist-food']='1234'
        with self.assertRaises(gate.DriftHold): self.f.run()

    def test_duplicate_changed_paths_fails(self):
        self.f.change()
        key=next(iter(self.f.changed))
        self.f.changed[key].append(self.f.changed[key][0])
        with self.assertRaises(gate.DriftHold): self.f.run()

    def test_git_blob_byte_mismatch_fails(self):
        self.f.change()
        original=self.f.read
        self.f.read=lambda sha,p: b'F O R G E D' if sha==self.f.heads['hist-food'] else original(sha,p)
        with self.assertRaisesRegex(gate.DriftHold, 'Git blob bytes'):
            self.f.run()

    def test_changed_fragment_invalid_json_fails(self):
        self.f.change('food','preparedness/sources/fragments/food.json',b'{bad')
        with self.assertRaises(ValueError): self.f.run()

    def test_duplicate_source_id_in_changed_fragment_fails(self):
        value={'sources':[{'id':'duplicate'},{'id':'duplicate'}]}
        self.f.change('hist-food','preparedness/sources/fragments/hist-food.json',
                      json.dumps(value).encode())
        with self.assertRaises(gate.DriftHold): self.f.run()

    def test_oversized_new_blob_fails(self):
        self.f.change(new=b'x'*(gate.MAX_FILE+1))
        with self.assertRaises(gate.DriftHold): self.f.run()

    def test_path_traversal_in_diff_fails(self):
        self.f.change()
        key=next(iter(self.f.changed))
        self.f.changed[key]=['preparedness/../secret']
        with self.assertRaises(gate.DriftHold): self.f.run()

    def test_frozen_manifest_modified_refused(self):
        replacement=copy.deepcopy(self.f.manifest)
        replacement['may_publish']=True
        with self.assertRaises(gate.DriftHold):
            gate.report(replacement,self.f.heads,self.f.diff,self.f.lookup,
                        self.f.read,self.f.validate_frozen,self.f.branches)


class TamperProofTests(unittest.TestCase):
    def setUp(self):
        self.f=Fixture()
        self.f.change()
        self.original=self.f.run()


def attack(name,mutate):
    def test(self):
        forged=copy.deepcopy(self.original)
        mutate(forged)
        with self.assertRaises(gate.DriftHold,msg=name):
            gate.verify_report(forged,*self.f.args())
    setattr(TamperProofTests,'test_reject_'+name,test)


ATTACKS={
 'publish_enabled':lambda x:x.update(may_publish=True),
 'qd_claim':lambda x:x.update(independent_QD_approval=True),
 'safety_claim':lambda x:x.update(qualified_safety_clearance=True),
 'links_claim':lambda x:x.update(human_source_links_verified=True),
 'hold_to_pass':lambda x:x.update(release_state='PASS'),
 'human_approval':lambda x:x['changed_files'][0].update(human_provenance_review_state='APPROVED'),
 'unfreeze_manifest':lambda x:x.update(frozen_manifest_blob_sha='0'*40),
 'decrease_branch_count':lambda x:x.update(checked_clusters=6),
 'decrease_file_count':lambda x:x.update(changed_file_count=0),
 'drop_moved_head':lambda x:x.update(moved_contributor_heads=[]),
 'replace_head':lambda x:x['moved_contributor_heads'][0].update(observed_commit_sha='f'*40),
 'replace_base':lambda x:x['moved_contributor_heads'][0].update(frozen_commit_sha='e'*40),
 'rename_cluster':lambda x:x['changed_files'][0].update(cluster='other'),
 'rename_path':lambda x:x['changed_files'][0].update(path='preparedness/other'),
 'drop_row':lambda x:x['changed_files'].clear(),
 'clone_row':lambda x:x['changed_files'].append(copy.deepcopy(x['changed_files'][0])),
 'mark_out_of_scope':lambda x:x['changed_files'][0].update(in_frozen_72_path_scope=False),
 'switch_label':lambda x:x['changed_files'][0].update(classification_NOT_APPROVAL='LINE_ENDINGS_ONLY'),
 'change_old_blob':lambda x:x['changed_files'][0].update(frozen_blob_sha='0'*40),
 'change_new_blob':lambda x:x['changed_files'][0].update(observed_blob_sha='0'*40),
 'change_old_sha256':lambda x:x['changed_files'][0].update(frozen_sha256='0'*64),
 'change_new_sha256':lambda x:x['changed_files'][0].update(observed_sha256='0'*64),
 'make_normalized':lambda x:x['changed_files'][0].update(normalized_line_endings_equivalent=True),
 'change_cite_added':lambda x:x['changed_files'][0]['source_and_citation_change_clues_NOT_VERIFIED'].update(citation_added_occurrences={'forged':9}),
 'change_cite_removed':lambda x:x['changed_files'][0]['source_and_citation_change_clues_NOT_VERIFIED'].update(citation_removed_occurrences={}),
 'change_cite_before':lambda x:x['changed_files'][0]['source_and_citation_change_clues_NOT_VERIFIED'].update(citation_total_before=99),
 'change_cite_after':lambda x:x['changed_files'][0]['source_and_citation_change_clues_NOT_VERIFIED'].update(citation_total_after=99),
 'clear_source_clues':lambda x:x['changed_files'][0].update(source_and_citation_change_clues_NOT_VERIFIED={}),
 'replace_schema':lambda x:x.update(schema='r60-approved'),
 'change_issue':lambda x:x.update(issue=777),
 'remove_machine_only':lambda x:x.pop('machine_only'),
 'change_machine_only':lambda x:x.update(machine_only=False),
 'remove_exception':lambda x:x.update(existing_R14_exception_remains_open=False),
 'replace_limitations':lambda x:x.update(limitations='Everything is verified.'),
 'remove_fingerprint':lambda x:x.pop('fingerprint_sha256'),
 'replace_fingerprint':lambda x:x.update(fingerprint_sha256='f'*64),
 'add_fake_approval':lambda x:x.update(approved_by='Doctor Example'),
 'rewrite_state_with_same_hash':lambda x:x['changed_files'][0].update(human_provenance_review_state='QD_PASS'),
 'rewrite_fragment':lambda x:x['changed_files'][0].update(source_and_citation_change_clues_NOT_VERIFIED={'source_ids_added':['forged']}),
 'replace_row_with_dict':lambda x:x['changed_files'].__setitem__(0,{}),
}
for key, fn in ATTACKS.items():
    attack(key,fn)


class GitReadOnlyTests(unittest.TestCase):
    def setUp(self):
        if not shutil.which('git'):
            self.skipTest('git CLI unavailable')
        self.tmp=tempfile.TemporaryDirectory(prefix='r60-safe-git-')
        self.root=Path(self.tmp.name)
        for args in [('init','-q'),('config','user.name','R60 Test'),
                     ('config','user.email','nobody@example.invalid')]:
            subprocess.run(['git','-C',str(self.root),*args],check=True,
                           stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        p=self.root/'preparedness/docs/CLUSTER-hist-home.md'
        p.parent.mkdir(parents=True)
        p.write_bytes(b'one\n')
        subprocess.run(['git','-C',str(self.root),'add','.'],check=True)
        subprocess.run(['git','-C',str(self.root),'commit','-qm','frozen'],check=True)
        self.old=subprocess.check_output(['git','-C',str(self.root),'rev-parse','HEAD'],text=True).strip()
        p.write_bytes(b'one\r\n')
        subprocess.run(['git','-C',str(self.root),'add','.'],check=True)
        subprocess.run(['git','-C',str(self.root),'commit','-qm','new'],check=True)
        self.new=subprocess.check_output(['git','-C',str(self.root),'rev-parse','HEAD'],text=True).strip()
        self.path='preparedness/docs/CLUSTER-hist-home.md'

    def tearDown(self):
        if hasattr(self,'tmp'): self.tmp.cleanup()

    def test_actual_git_object_sha(self):
        o=gate.git_blob(self.root,self.old,self.path)
        self.assertEqual(o,gate.blob_sha(b'one\n'))

    def test_exact_changed_paths(self):
        self.assertEqual(gate.git_changed(self.root,self.old,self.new),[self.path])

    def test_read_git_bytes(self):
        self.assertEqual(gate.git_read(self.root,self.new,self.path),b'one\r\n')

    def test_missing_blob_is_none(self):
        self.assertIsNone(gate.git_blob(self.root,self.old,
                          'preparedness/docs/CLUSTER-other.md'))

    def test_reject_traversal(self):
        with self.assertRaises(gate.DriftHold):
            gate.git_blob(self.root,self.new,'preparedness/../secret')

    def test_reject_hash_injection(self):
        with self.assertRaises(gate.DriftHold):
            gate.git_changed(self.root,self.old+';touch bad',self.new)


if __name__ == '__main__': unittest.main()
