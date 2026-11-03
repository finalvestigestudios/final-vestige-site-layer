"""Stage 4 additions to the R15 parity gate: allowlisted re-pin reference and proven EOL-only exceptions.

Synthetic fixtures only. Passing is Git-object identity, never a content review,
source verification, safety clearance or permission to publish.
"""
from __future__ import annotations

import copy
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from test_cluster_git_parity_gate import digest, fixture, gate, run  # noqa: E402

REF = next(iter(gate.REPIN_REFERENCES))
EOL_PATH = 'preparedness/content/articles/hist-home-1.body.html'
CRLF = b'<p>one</p>\r\n<p>two</p>\r\n'
LF = b'<p>one</p>\n<p>two</p>\n'


def repinned_fixture():
    """hist-home re-pinned: one article body stored CRLF by the contributor, LF in the integration."""
    m, bm, refs = fixture()
    old, new = digest('crlf-body'), digest('lf-body')
    branch = next(b for b in m['branches'] if b['name'] == 'hist-home')
    branch['integrated_reference_sha'] = REF
    contributor = branch['contributor_commit_sha']
    for f in branch['files']:
        bm[(REF, f['path'])] = f['integrated_blob_sha']
        if f['path'] == EOL_PATH:
            f.update(contributor_blob_sha=old, integrated_blob_sha=new, identical=False)
            for commit in (contributor,):
                bm[(commit, f['path'])] = old
            for commit in (REF, gate.R13_SHA, gate.R14_SHA):
                bm[(commit, f['path'])] = new
    branch['exact_matches'] -= 1
    branch['nonidentical_paths'] += 1
    m['exceptions'].append({'branch': 'hist-home', 'path': EOL_PATH,
                            'state': gate.EOL_ONLY_STATE, 'contributor_blob_sha': old,
                            'integrated_blob_sha': new, 'identical': False})
    m['totals'].update(exact_matches=70, nonidentical_paths=2)
    contents = {old: CRLF, new: LF}
    return m, bm, refs, contents


def go(m, bm, refs, contents, **kw):
    return run(m, bm, refs, content_lookup=lambda d: contents.get(d), **kw)


class RepinAndEolOnly(unittest.TestCase):
    def setUp(self):
        self.m, self.bm, self.refs, self.contents = repinned_fixture()

    def test_default_report_is_unchanged_without_a_repin(self):
        m, bm, refs = fixture()
        report = run(m, bm, refs)
        self.assertEqual(report['identical_paths'], 71)
        self.assertNotIn('eol_only_paths_proven_from_blob_contents', report)

    def test_allowlisted_reference_and_proven_eol_only_difference_are_accepted(self):
        report = go(self.m, self.bm, self.refs, self.contents)
        self.assertEqual(report['identical_paths'], 70)
        self.assertEqual(report['eol_only_paths_proven_from_blob_contents'], 1)
        self.assertEqual(report['repinned_clusters_to_allowlisted_reference'], ['hist-home'])
        self.assertEqual(report['release_state'], 'HOLD')
        self.assertIs(report['may_publish'], False)
        self.assertIs(report['qualified_safety_review_complete'], False)

    def test_reference_commit_chosen_by_the_manifest_is_refused(self):
        next(b for b in self.m['branches'] if b['name'] == 'hist-home')['integrated_reference_sha'] = digest('x')
        with self.assertRaisesRegex(gate.ParityFailure, 'allowlisted re-pin point'):
            go(self.m, self.bm, self.refs, self.contents)

    def test_eol_claim_without_blob_contents_cannot_be_proven(self):
        with self.assertRaisesRegex(gate.ParityFailure, 'without blob contents'):
            run(self.m, self.bm, self.refs)

    def test_eol_claim_over_a_real_content_change_is_refused(self):
        self.contents[self.m['exceptions'][-1]['integrated_blob_sha']] = b'<p>one</p>\n<p>CHANGED</p>\n'
        with self.assertRaisesRegex(gate.ParityFailure, 'not line endings only'):
            go(self.m, self.bm, self.refs, self.contents)

    def test_integrated_blob_that_still_contains_carriage_returns_is_refused(self):
        self.contents[self.m['exceptions'][-1]['integrated_blob_sha']] = CRLF
        self.contents[self.m['exceptions'][-1]['contributor_blob_sha']] = CRLF + b' '
        with self.assertRaises(gate.ParityFailure):
            go(self.m, self.bm, self.refs, self.contents)

    def test_eol_exception_is_refused_on_a_cluster_that_was_not_re_pinned(self):
        del next(b for b in self.m['branches'] if b['name'] == 'hist-home')['integrated_reference_sha']
        for f in next(b for b in self.m['branches'] if b['name'] == 'hist-home')['files']:
            self.bm[(gate.R13_SHA, f['path'])] = f['integrated_blob_sha']
        with self.assertRaisesRegex(gate.ParityFailure, 'only allowed on a re-pinned cluster'):
            go(self.m, self.bm, self.refs, self.contents)

    def test_unregistered_extra_difference_still_closes_the_gate(self):
        m = copy.deepcopy(self.m)
        m['exceptions'] = [e for e in m['exceptions'] if e.get('state') != gate.EOL_ONLY_STATE]
        with self.assertRaisesRegex(gate.ParityFailure, 'new or missing Git-blob discrepancy'):
            go(m, self.bm, self.refs, self.contents)

    def test_totals_must_match_the_proven_mismatches(self):
        self.m['totals'].update(exact_matches=71, nonidentical_paths=1)
        with self.assertRaisesRegex(gate.ParityFailure, 'totals are not canonical'):
            go(self.m, self.bm, self.refs, self.contents)

    def test_duplicate_eol_exception_is_refused(self):
        self.m['exceptions'].append(copy.deepcopy(self.m['exceptions'][-1]))
        with self.assertRaises(gate.ParityFailure):
            go(self.m, self.bm, self.refs, self.contents)

    def test_a_moved_branch_still_closes_a_re_pinned_cluster(self):
        self.refs[gate.BRANCHES['hist-home']] = digest('moved-again')
        with self.assertRaisesRegex(gate.ParityFailure, 'live contributor branch moved'):
            go(self.m, self.bm, self.refs, self.contents)


if __name__ == '__main__':
    unittest.main()
