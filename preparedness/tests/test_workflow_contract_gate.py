"""R19 synthetic/adversarial tests; do not treat as review of real source claims."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

TOOL = Path(__file__).resolve().parents[1] / 'tools' / 'workflow_contract_gate.py'
WORKFLOW = Path(__file__).resolve().parents[2] / '.github/workflows/preparedness-private-preflight.yml'
spec = importlib.util.spec_from_file_location('r19_workflow_contract_gate', TOOL)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
SHA = 'f' * 40
DIGEST = 'a' * 64


def good_receipt():
    steps = []
    for name in gate.GATE_NAMES:
        item = {'gate': name, 'exit_code': 0,
                'stdout_sha256': DIGEST, 'stderr_sha256': DIGEST}
        if name == 'native_unit_suite':
            item['native_test_count'] = 715
        elif name not in ('native_validation', 'private_draft_build'):
            item.update(state='HOLD', receipt_sha256=DIGEST)
        steps.append(item)
    result = {'schema_version': 1, 'authority': 'MACHINE_LOCAL_DRAFT_CUSTODY_ONLY',
              'issue': 136, 'exact_checkout_sha': SHA,
              'release_state': 'HOLD', 'may_publish': False,
              'wordpress_publishing_performed': False,
              'independent_QD_approval': False,
              'source_claim_accuracy_verified': False,
              'qualified_medical_or_emergency_safety_review': False,
              'all_required_machine_gates_executed': True,
              'steps': steps}
    result['fingerprint_sha256'] = hashlib.sha256(gate.canonical_bytes(result)).hexdigest()
    return result


class WorkflowContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='r19-draft-ci-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'checkout'
        p = self.root / gate.WORKFLOW_PATH
        p.parent.mkdir(parents=True)
        p.write_bytes(WORKFLOW.read_bytes())
        self.file = p

    def test_good_exact_workflow_is_hold(self):
        result = gate.check_workflow(self.root)
        self.assertEqual(result['release_state'], 'HOLD')
        self.assertIs(result['may_publish'], False)
        self.assertEqual(result['workflow_sha256'], gate.WORKFLOW_SHA256)

    def test_workflow_digest_matches_pinned_action_review(self):
        self.assertEqual(hashlib.sha256(WORKFLOW.read_bytes()).hexdigest(),
                         gate.WORKFLOW_SHA256)

    def test_workflow_does_not_reference_credentials_or_publishing(self):
        text = WORKFLOW.read_text()
        for forbidden in ('pull_request_target:', 'workflow_run:', 'contents: write',
                          'secrets.', 'wp-admin', 'wordpress.com', 'curl ',
                          'upload-artifact', 'deploy', 'push:', 'schedule:',
                          'workflow_dispatch:', 'issue_comment:', 'release:'):
            self.assertNotIn(forbidden, text)
        self.assertIn('persist-credentials: false', text)
        self.assertIn('fetch-depth: 0', text)
        self.assertIn('permissions:\n  contents: read', text)
        self.assertIn('private_release_preflight.py', text)
        self.assertIn('workflow_contract_gate.py', text)
        self.assertIn('"$GITHUB_SHA"', text)

    def test_missing_workflow_fails(self):
        self.file.unlink()
        with self.assertRaises(gate.ContractHold): gate.check_workflow(self.root)

    def test_symlink_workflow_fails(self):
        p = self.file.with_suffix('.original')
        self.file.rename(p)
        self.file.symlink_to(p)
        with self.assertRaises(gate.ContractHold): gate.check_workflow(self.root)

    def test_missing_repo_fails(self):
        with self.assertRaises(gate.ContractHold): gate.check_workflow(self.root / 'absent')

    def test_symlink_repo_fails(self):
        alias = self.root.parent / 'link'
        alias.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(gate.ContractHold): gate.check_workflow(alias)

    def test_oversized_workflow_fails(self):
        self.file.write_bytes(b'x' * 20_000)
        with self.assertRaises(gate.ContractHold): gate.check_workflow(self.root)


class ReceiptContractTests(unittest.TestCase):
    def test_good_receipt_is_hold(self):
        result = gate.verify_receipt(good_receipt(), SHA)
        self.assertIs(result['may_publish'], False)
        self.assertEqual(result['verified_machine_step_count'], 13)
        self.assertEqual(result['native_test_count'], 715)

    def test_reject_wrong_expected_head(self):
        with self.assertRaises(gate.ContractHold): gate.verify_receipt(good_receipt(), 'abc')

    def test_accept_exact_minimum_36_tests(self):
        r = good_receipt()
        r['steps'][2]['native_test_count'] = 36
        without = {k: v for k, v in r.items() if k != 'fingerprint_sha256'}
        r['fingerprint_sha256'] = hashlib.sha256(gate.canonical_bytes(without)).hexdigest()
        self.assertEqual(gate.verify_receipt(r, SHA)['native_test_count'], 36)

    def test_json_duplicate_keys_denied(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / 'receipt.json'
            p.write_text('{"release_state":"HOLD","may_publish":false,"may_publish":true}')
            with self.assertRaises(gate.ContractHold): gate.read_receipt(p)

    def test_json_nan_denied(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / 'receipt.json'
            p.write_text('{"x":NaN}')
            with self.assertRaises(gate.ContractHold): gate.read_receipt(p)

    def test_json_symlink_denied(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / 'receipt.json'
            q = Path(td) / 'alias.json'
            p.write_text('{}')
            q.symlink_to(p)
            with self.assertRaises(gate.ContractHold): gate.read_receipt(q)

    def test_json_oversized_denied(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / 'receipt.json'
            p.write_bytes(b' ' * (gate.RECEIPT_LIMIT + 1))
            with self.assertRaises(gate.ContractHold): gate.read_receipt(p)

    def test_json_invalid_unicode_denied(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / 'receipt.json'
            p.write_bytes(b'\xff\xfe')
            with self.assertRaises(gate.ContractHold): gate.read_receipt(p)

    def test_canonical_receipt_fingerprint(self):
        r = good_receipt()
        self.assertEqual(r['fingerprint_sha256'], hashlib.sha256(
            gate.canonical_bytes({k:v for k,v in r.items() if k != 'fingerprint_sha256'})).hexdigest())


def workflow_mutation_case(find, replacement):
    def check(self):
        src = WORKFLOW.read_text()
        self.assertIn(find, src)
        self.file.write_text(src.replace(find, replacement, 1))
        with self.assertRaises(gate.ContractHold): gate.check_workflow(self.root)
    return check


WORKFLOW_MUTATIONS = [
    ('pull_request:', 'pull_request_target:'),
    ('pull_request:', 'push:'),
    ('pull_request:', 'workflow_run:'),
    ('pull_request:', 'workflow_dispatch:'),
    ('contents: read', 'contents: write'),
    ('contents: read', 'actions: write'),
    ('contents: read', 'contents: none'),
    ('persist-credentials: false', 'persist-credentials: true'),
    ('persist-credentials: false', 'persist-credentials: ${{ secrets.TOKEN }}'),
    ('fetch-depth: 0', 'fetch-depth: 1'),
    ('fetch-depth: 0', 'fetch-depth: 2'),
    ('fetch-depth: 0', 'fetch-depth: false'),
    ('submodules: false', 'submodules: true'),
    ('lfs: false', 'lfs: true'),
    ('ubuntu-latest', 'self-hosted'),
    ('timeout-minutes: 30', 'timeout-minutes: 300'),
    ('cancel-in-progress: true', 'cancel-in-progress: false'),
    ('pull_request.number', 'actor'),
    ('python-version: \'3.12\'', 'python-version: \'3.13\''),
    ('python-version: \'3.12\'', 'python-version: latest'),
    ('opened, synchronize, reopened', 'opened'),
    ("'preparedness/**'", "'**'"),
    ("'.github/workflows/preparedness-private-preflight.yml'", "'.github/workflows/*.yml'"),
    ('actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683', 'actions/checkout@v4'),
    ('actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065', 'actions/setup-python@v5'),
    ('set -euo pipefail', 'set +e'),
    ('set -euo pipefail', 'set -e'),
    ('test "$(git rev-parse HEAD)" = "$GITHUB_SHA"', 'echo pinned'),
    ('--expected-head "$GITHUB_SHA"', '--expected-head "0000000000000000000000000000000000000000"'),
    ('--repo-root .', '--repo-root /tmp'),
    ('--receipt "$RUNNER_TEMP/preparedness-private-hold.json"', '--receipt /tmp/supplied.json'),
    ('private_release_preflight.py', 'some_other_script.py'),
    ('workflow_contract_gate.py', 'echo.py'),
    ('--expected-head "$GITHUB_SHA"', '--expected-head "${{ secrets.SHA }}"'),
    ('printf \'%s\\n\'', 'curl -sI https://example.com; printf \'%s\\n\''),
    ('PYTHONDONTWRITEBYTECODE: \'1\'', 'PYTHONDONTWRITEBYTECODE: \'0\''),
    ('shell: bash', 'shell: powershell'),
    ('run: |', 'run: echo PASS'),
    ('Machine integrity only - publication HOLD', 'QD PASSED'),
    ('No human source review', 'All claims independently verified'),
    ('No human source review', 'Medical review complete'),
]
for i, (old, new) in enumerate(WORKFLOW_MUTATIONS, 1):
    setattr(WorkflowContractTests, f'test_reject_workflow_mutation_{i:02d}',
            workflow_mutation_case(old, new))


def receipt_mutation_case(mutator):
    def check(self):
        receipt = good_receipt()
        mutator(receipt)
        with self.assertRaises(gate.ContractHold):
            gate.verify_receipt(receipt, SHA)
    return check


RECEIPT_MUTATIONS = [
    lambda d: d.update(schema_version=2),
    lambda d: d.update(issue=137),
    lambda d: d.update(exact_checkout_sha='0'*40),
    lambda d: d.update(authority='INDEPENDENT_APPROVAL'),
    lambda d: d.update(release_state='PASS'),
    lambda d: d.update(may_publish=True),
    lambda d: d.update(wordpress_publishing_performed=True),
    lambda d: d.update(independent_QD_approval=True),
    lambda d: d.update(source_claim_accuracy_verified=True),
    lambda d: d.update(qualified_medical_or_emergency_safety_review=True),
    lambda d: d.update(all_required_machine_gates_executed=False),
    lambda d: d.update(steps=d['steps'][:-1]),
    lambda d: d['steps'].append(deepcopy(d['steps'][-1])),
    lambda d: d['steps'].reverse(),
    lambda d: d['steps'][2].update(native_test_count=35),
    lambda d: d['steps'][2].update(native_test_count=True),
    lambda d: d['steps'][2].update(native_test_count=0),
    lambda d: d['steps'][2].update(native_test_count=-1),
    lambda d: d['steps'][2].update(native_test_count=100001),
    lambda d: d['steps'][2].update(native_test_count='715'),
    lambda d: d['steps'][0].update(exit_code=1),
    lambda d: d['steps'][0].update(exit_code=False),
    lambda d: d['steps'][4].update(state='VERIFIED'),
    lambda d: d['steps'][4].pop('receipt_sha256'),
    lambda d: d['steps'][4].update(receipt_sha256='0'),
    lambda d: d['steps'][4].update(stdout_sha256='0'),
    lambda d: d['steps'][4].update(stderr_sha256='q'*64),
    lambda d: d['steps'][2].update(receipt_sha256=DIGEST),
    lambda d: d['steps'][2].update(state='HOLD'),
    lambda d: d['steps'][0].update(receipt_sha256=DIGEST),
    lambda d: d['steps'][0].update(native_test_count=715),
    lambda d: d['steps'][2].update(gate='wrong_gate'),
    lambda d: d.update(extra_approval=True),
    lambda d: d.pop('fingerprint_sha256'),
    lambda d: d.update(fingerprint_sha256='0'*64),
]
for i, mutate in enumerate(RECEIPT_MUTATIONS, 1):
    setattr(ReceiptContractTests, f'test_reject_receipt_mutation_{i:02d}',
            receipt_mutation_case(mutate))

if __name__ == '__main__':
    unittest.main()
