"""R15: real Git object tests + synthetic seven-cluster adversarial fixtures.

Passing tests do not constitute factual claim review, qualified safety clearance
or QD permission. Never touch WordPress, network, or production sources.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cluster_git_parity_gate as gate


def digest(s):
    return hashlib.sha1(s.encode('utf-8')).hexdigest()


def fixture():
    branch_shas = {name: digest('branch-commit-' + name) for name in gate.EXPECTED}
    blob_map = {}
    ref_map = {gate.BRANCHES[k]: v for k, v in branch_shas.items()}
    entries = []
    for name, n in gate.EXPECTED.items():
        slugs = (["household-emergency-plan", "three-day-kit", "go-bags",
                  "preparedness-real-households"] if name == 'start'
                 else [f'{name}-{i}' for i in range(n)])
        paths = [f'preparedness/content/articles/{slug}.{typ}'
                 for slug in slugs for typ in ['body.html', 'meta.json']]
        paths += [f'preparedness/docs/CLUSTER-{name}.md',
                  f'preparedness/sources/fragments/{name}.json']
        files = []
        for path in paths:
            old = digest('contributor|' + path)
            new = old
            if path == gate.EXCEPTION_PATH:
                old, new = gate.EXCEPTION_OLD, gate.EXCEPTION_NEW
            files.append({'path': path, 'contributor_blob_sha': old,
                          'integrated_blob_sha': new, 'identical': old == new})
            blob_map[(branch_shas[name], path)] = old
            blob_map[(gate.R13_SHA, path)] = new
            blob_map[(gate.R14_SHA, path)] = new
        exceptions = sum(not f['identical'] for f in files)
        entries.append({'name': name, 'contributor_commit_sha': branch_shas[name],
                        'article_count': n, 'scoped_paths': len(files),
                        'exact_matches': len(files) - exceptions,
                        'nonidentical_paths': exceptions, 'files': files})
    m = {'schema_version': 1, 'authority': 'GIT_BLOB_PARITY_ONLY_NOT_FACT_OR_SAFETY_APPROVAL',
         'generated_date_utc': '2026-10-31', 'issue': 136, 'release_state': 'HOLD',
         'may_publish': False, 'reference_integrated_commit_sha': gate.R13_SHA,
         'human_source_review_complete': False,
         'independent_human_source_checks_verified': 0,
         'qualified_emergency_safety_clearance': False, 'branches': entries,
         'totals': {'contributor_branches': 7, 'cluster_authored_articles': 29,
                    'scoped_blob_paths': 72, 'exact_matches': 71, 'nonidentical_paths': 1},
         'exceptions': [{'branch': 'start', 'path': gate.EXCEPTION_PATH,
                         'state': 'NEEDS_HUMAN_DIFF_REVIEW',
                         'contributor_blob_sha': gate.EXCEPTION_OLD,
                         'integrated_blob_sha': gate.EXCEPTION_NEW,
                         'identical': False,
                         'observed_additive_difference': 'Source-use scope added; unresolved.'}]}
    return m, blob_map, ref_map


def run(m, bm, refs, **kwargs):
    return gate.check_manifest(m, lambda commit, path: bm.get((commit, path)),
                               lambda branch: refs.get(branch), **kwargs)


class PositiveTests(unittest.TestCase):
    def setUp(self):
        self.m, self.bm, self.refs = fixture()

    def test_seven_cluster_exact_manifest(self):
        result = run(self.m, self.bm, self.refs)
        self.assertEqual(result['contributor_branches'], 7)
        self.assertEqual(result['cluster_articles'], 29)
        self.assertEqual(result['inspected_paths'], 72)
        self.assertEqual(result['git_blob_checks'], 216)
        self.assertEqual(result['unresolved_contributor_metadata_differences'], 1)
        self.assertEqual(result['other_integration_articles_outside_scope'], 6)
        self.assertEqual(result['unpublished_water_planner_outside_scope'], 1)
        self.assertEqual(result['release_state'], 'HOLD')
        self.assertFalse(result['may_publish'])
        self.assertFalse(result['source_links_independently_verified'])
        self.assertFalse(result['qualified_safety_review_complete'])

    def test_order_independence(self):
        first = run(self.m, self.bm, self.refs)['verified_rows_digest_sha256']
        self.m['branches'].reverse()
        for b in self.m['branches']:
            b['files'].reverse()
        self.assertEqual(first, run(self.m, self.bm, self.refs)['verified_rows_digest_sha256'])

    def test_manifest_json_roundtrip(self):
        self.m = json.loads(json.dumps(self.m))
        self.assertEqual(72, run(self.m, self.bm, self.refs)['inspected_paths'])

    def test_sha_changes_detected(self):
        self.bm[(gate.R14_SHA, gate.EXCEPTION_PATH)] = digest('changed-unreviewed-metadata')
        with self.assertRaisesRegex(gate.ParityFailure, 'current integration Git blob drift'):
            run(self.m, self.bm, self.refs)

    def test_moved_contributor_branch_detected(self):
        self.refs[gate.BRANCHES['start']] = digest('new-release')
        with self.assertRaisesRegex(gate.ParityFailure, 'branch moved'):
            run(self.m, self.bm, self.refs)

    def test_missing_object_is_fail_closed(self):
        self.bm.pop((gate.R13_SHA, 'preparedness/docs/CLUSTER-health.md'))
        with self.assertRaises(gate.ParityFailure):
            run(self.m, self.bm, self.refs)

    def test_missing_remote_ref_is_fail_closed(self):
        self.refs.pop(gate.BRANCHES['start'])
        with self.assertRaises(gate.ParityFailure):
            run(self.m, self.bm, self.refs)

    def test_integrated_head_may_change_only_if_all_provenance_bytes_preserved(self):
        new = digest('new-integration-head')
        for (sha, path), value in list(self.bm.items()):
            if sha == gate.R14_SHA:
                self.bm[(new, path)] = value
        self.assertEqual(new, run(self.m, self.bm, self.refs, integrated_head=new)['audited_integration_sha'])

    def test_integrated_head_missing_object_fails(self):
        with self.assertRaises(gate.ParityFailure):
            run(self.m, self.bm, self.refs, integrated_head=digest('missing'))

    def test_outside_scope_flag_is_not_implicit_success(self):
        result = run(self.m, self.bm, self.refs)
        self.assertTrue(result['full_native_validator_and_QD_still_required'])
        self.assertEqual(result['exception_state'], 'NEEDS_HUMAN_DIFF_REVIEW')


class GitObjectTests(unittest.TestCase):
    def setUp(self):
        if not shutil.which('git'):
            self.skipTest('git executable not available')
        self.tmp = tempfile.TemporaryDirectory(prefix='fv-prep-r15-git-')
        self.root = Path(self.tmp.name)
        for args in (('init', '-q'), ('config', 'user.email', 'r15@example.invalid'),
                     ('config', 'user.name', 'Synthetic Fixture')):
            subprocess.run(['git', '-C', str(self.root), *args], check=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        dest = self.root / 'preparedness/docs'
        dest.mkdir(parents=True)
        (dest / 'CLUSTER-health.md').write_text('synthetic body\n', encoding='utf-8')
        subprocess.run(['git', '-C', str(self.root), 'add', '.'], check=True)
        subprocess.run(['git', '-C', str(self.root), 'commit', '-qm', 'synthetic'], check=True)
        self.sha = subprocess.check_output(['git','-C',str(self.root),'rev-parse','HEAD'], text=True).strip()

    def tearDown(self):
        if hasattr(self, 'tmp'):
            self.tmp.cleanup()

    def test_reads_actual_git_blob(self):
        result = gate.git_blob(self.root, self.sha, 'preparedness/docs/CLUSTER-health.md')
        self.assertEqual(40, len(result))

    def test_rejects_missing_git_path(self):
        with self.assertRaises(gate.ParityFailure):
            gate.git_blob(self.root, self.sha, 'preparedness/docs/CLUSTER-food.md')

    def test_rejects_commit_sha_injection(self):
        with self.assertRaises(gate.ParityFailure):
            gate.git_blob(self.root, 'HEAD; rm -rf /', 'preparedness/docs/CLUSTER-health.md')

    def test_rejects_path_traversal(self):
        with self.assertRaises(gate.ParityFailure):
            gate.git_blob(self.root, self.sha, 'preparedness/../x')

    def test_rejects_directory_path(self):
        with self.assertRaises(gate.ParityFailure):
            gate.git_blob(self.root, self.sha, 'preparedness/docs/')

    def test_rejects_missing_branch(self):
        with self.assertRaises(gate.ParityFailure):
            gate.git_ref(self.root, gate.BRANCHES['health'])

    def test_checks_live_remote_ref(self):
        subprocess.run(['git','-C',str(self.root),'update-ref',
                        f'refs/remotes/origin/{gate.BRANCHES["health"]}',self.sha],check=True)
        self.assertEqual(self.sha, gate.git_ref(self.root, gate.BRANCHES['health']))

    def test_rejects_git_ref_injection(self):
        with self.assertRaises(gate.ParityFailure):
            gate.git_ref(self.root, 'origin/main; touch pwned')

    def test_rejects_nonregular_symlink_blob(self):
        p = self.root / 'preparedness/docs/CLUSTER-health.md'
        p.unlink()
        try:
            p.symlink_to('external-file')
        except (OSError, NotImplementedError):
            self.skipTest('symlinks unavailable')
        subprocess.run(['git','-C',str(self.root),'add','-A'], check=True)
        subprocess.run(['git','-C',str(self.root),'commit','-qm','symlink'], check=True)
        s=subprocess.check_output(['git','-C',str(self.root),'rev-parse','HEAD'],text=True).strip()
        with self.assertRaisesRegex(gate.ParityFailure, 'nonregular'):
            gate.git_blob(self.root,s,'preparedness/docs/CLUSTER-health.md')

    def test_fails_on_missing_git_repository(self):
        with tempfile.TemporaryDirectory() as other:
            with self.assertRaises(gate.ParityFailure):
                gate.git_blob(Path(other),self.sha,'preparedness/docs/CLUSTER-health.md')


class MutationTests(unittest.TestCase):
    def setUp(self):
        self.m, self.bm, self.refs = fixture()


def mutation(name, act):
    def test(self):
        m, bm, refs = fixture()
        act(m, bm, refs)
        with self.assertRaises(gate.ParityFailure, msg=name):
            run(m, bm, refs)
    setattr(MutationTests, 'test_mutation_' + name, test)


def find(m, branch='start', index=0):
    return next(b for b in m['branches'] if b['name'] == branch)['files'][index]


MUTATIONS = {
    'bad_schema': lambda m,b,r: m.update(schema_version=2),
    'wrong_issue': lambda m,b,r: m.update(issue=157),
    'wrong_authority': lambda m,b,r: m.update(authority='ALL_SOURCES_VERIFIED'),
    'publish_true': lambda m,b,r: m.update(may_publish=True),
    'publish_string_false': lambda m,b,r: m.update(may_publish='false'),
    'release_pass': lambda m,b,r: m.update(release_state='PASS'),
    'human_review_true': lambda m,b,r: m.update(human_source_review_complete=True),
    'human_review_blank': lambda m,b,r: m.update(human_source_review_complete=None),
    'checks_claimed': lambda m,b,r: m.update(independent_human_source_checks_verified=1),
    'checks_string_zero': lambda m,b,r: m.update(independent_human_source_checks_verified='0'),
    'qualified_approved': lambda m,b,r: m.update(qualified_emergency_safety_clearance=True),
    'different_baseline': lambda m,b,r: m.update(reference_integrated_commit_sha=digest('new')),
    'remove_branches': lambda m,b,r: m.update(branches=[]),
    'duplicate_branch': lambda m,b,r: m['branches'].__setitem__(1,copy.deepcopy(m['branches'][0])),
    'remove_branch': lambda m,b,r: m['branches'].pop(),
    'rename_branch': lambda m,b,r: m['branches'][0].update(name='unknown'),
    'replace_branch_sha': lambda m,b,r: m['branches'][0].update(contributor_commit_sha=digest('forged')),
    'branch_sha_bad': lambda m,b,r: m['branches'][0].update(contributor_commit_sha='xyz'),
    'article_count_wrong': lambda m,b,r: m['branches'][0].update(article_count=5),
    'files_count_wrong': lambda m,b,r: m['branches'][0].update(scoped_paths=111),
    'exact_match_wrong': lambda m,b,r: m['branches'][0].update(exact_matches=10),
    'nonidentical_wrong': lambda m,b,r: m['branches'][0].update(nonidentical_paths=0),
    'remove_article_body': lambda m,b,r: m['branches'][0]['files'].pop(0),
    'remove_article_meta': lambda m,b,r: m['branches'][0]['files'].pop(1),
    'remove_source_fragment': lambda m,b,r: m['branches'][0]['files'].pop(),
    'remove_cluster_doc': lambda m,b,r: m['branches'][0]['files'].pop(-2),
    'duplicate_path_in_same_branch': lambda m,b,r: m['branches'][0]['files'].__setitem__(1,copy.deepcopy(m['branches'][0]['files'][0])),
    'swap_cross_branch_path': lambda m,b,r: m['branches'][1]['files'][0].update(path=m['branches'][0]['files'][0]['path']),
    'bad_article_slug': lambda m,b,r: find(m).update(path='preparedness/content/articles/Foo.body.html'),
    'path_traversal': lambda m,b,r: find(m).update(path='preparedness/content/articles/../secrets.body.html'),
    'absolute_path': lambda m,b,r: find(m).update(path='/tmp/x.body.html'),
    'word_press_path': lambda m,b,r: find(m).update(path='wp-content/themes/publish.php'),
    'hidden_dot_path': lambda m,b,r: find(m).update(path='preparedness/content/articles/.env.body.html'),
    'foreign_cluster_doc': lambda m,b,r: m['branches'][0]['files'][-2].update(path='preparedness/docs/CLUSTER-food.md'),
    'foreign_source_fragment': lambda m,b,r: m['branches'][0]['files'][-1].update(path='preparedness/sources/fragments/food.json'),
    'empty_blob_sha': lambda m,b,r: find(m).update(contributor_blob_sha=''),
    'uppercase_blob_sha': lambda m,b,r: find(m).update(contributor_blob_sha='A'*40),
    'wrong_contributor_blob': lambda m,b,r: find(m).update(contributor_blob_sha=digest('altered')),
    'wrong_integrated_blob': lambda m,b,r: find(m).update(integrated_blob_sha=digest('altered')),
    'false_identical_flag': lambda m,b,r: find(m).update(identical=False),
    'missing_identical_flag': lambda m,b,r: find(m).pop('identical'),
    'unknown_fifth_file_type': lambda m,b,r: find(m).update(path='preparedness/content/articles/three-day-kit.docx'),
    'duplicate_exception': lambda m,b,r: m['exceptions'].append(copy.deepcopy(m['exceptions'][0])),
    'missing_exception': lambda m,b,r: m.update(exceptions=[]),
    'exception_auto_approved': lambda m,b,r: m['exceptions'][0].update(state='QD_PASS'),
    'exception_reassigned_branch': lambda m,b,r: m['exceptions'][0].update(branch='food'),
    'exception_changed_path': lambda m,b,r: m['exceptions'][0].update(path='preparedness/content/articles/three-day-kit.meta.json'),
    'exception_changed_old_sha': lambda m,b,r: m['exceptions'][0].update(contributor_blob_sha=digest('new')),
    'exception_changed_new_sha': lambda m,b,r: m['exceptions'][0].update(integrated_blob_sha=digest('new')),
    'exception_identical_claim': lambda m,b,r: m['exceptions'][0].update(identical=True),
    'totals_changed_articles': lambda m,b,r: m['totals'].update(cluster_authored_articles=30),
    'totals_changed_paths': lambda m,b,r: m['totals'].update(scoped_blob_paths=71),
    'totals_changed_equal': lambda m,b,r: m['totals'].update(exact_matches=72),
    'totals_changed_mismatch': lambda m,b,r: m['totals'].update(nonidentical_paths=0),
    'totals_changed_branch_count': lambda m,b,r: m['totals'].update(contributor_branches=6),
    'unknown_totals_value': lambda m,b,r: m['totals'].update(new_approval=True),
    'remove_totals': lambda m,b,r: m.pop('totals'),
    'null_file_record': lambda m,b,r: m['branches'][0]['files'].__setitem__(0,None),
    'null_branch_record': lambda m,b,r: m['branches'].__setitem__(0,None),
    'no_exceptions_key': lambda m,b,r: m.pop('exceptions'),
    'nonlist_exceptions': lambda m,b,r: m.update(exceptions={}),
    'nonlist_branches': lambda m,b,r: m.update(branches={}),
    'nonlist_files': lambda m,b,r: m['branches'][0].update(files={}),
    'unknown_head_sha': lambda m,b,r: r.__setitem__(gate.BRANCHES['start'], None),
    'unset_commit_object': lambda m,b,r: b.pop((gate.R13_SHA,gate.EXCEPTION_PATH)),
    'tamper_source_doc_blob': lambda m,b,r: b.__setitem__((gate.R14_SHA,'preparedness/docs/CLUSTER-start.md'),digest('new')),
    'tamper_fragment_blob': lambda m,b,r: b.__setitem__((gate.R14_SHA,'preparedness/sources/fragments/start.json'),digest('new')),
    'tamper_second_contributor': lambda m,b,r: b.__setitem__((m['branches'][1]['contributor_commit_sha'],m['branches'][1]['files'][0]['path']),digest('new')),
}
for mutation_name, action in MUTATIONS.items():
    mutation(mutation_name, action)


if __name__ == '__main__':
    unittest.main(verbosity=2)
