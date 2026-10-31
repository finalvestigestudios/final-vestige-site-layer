"""R24 adversarial preflight tests. Synthetic fixtures, no live safety approvals.

These tests ensure R23's actual 81-file custody gate is *mandatory* in the
private CI preflight, and that HOLD-only subprocesses cannot smuggle approval
flags in otherwise valid machine receipts.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

TOOLS = Path(__file__).resolve().parents[1] / 'tools'
sys.path.insert(0, str(TOOLS))
import private_release_preflight as preflight
import workflow_contract_gate as contract

GATE = 'frozen_81_file_archive_custody'
SCRIPT = 'source_group_review_gate.py'
AUTHORITIES = (
    'qualified_safety_clearance', 'human_source_reviews_complete',
    'human_source_review_complete', 'human_source_reviews_completed',
    'external_human_qa_proven', 'article_claim_accuracy_verified',
    'independent_human_source_checks_verified',
    'source_links_independently_verified', 'source_claim_accuracy_verified',
    'link_and_claim_accuracy_independently_verified',
    'medical_safety_approved', 'qualified_emergency_or_medical_safety_review',
    'qualified_medical_or_emergency_safety_review',
    'independent_qd_pass', 'independent_QD_approval',
    'wordpress_publishing_performed', 'may_publish',
)


def receipt():
    steps = []
    for name in contract.GATE_NAMES:
        row = {'gate': name, 'exit_code': 0,
               'stdout_sha256': 'a' * 64, 'stderr_sha256': 'b' * 64}
        if name == 'native_unit_suite':
            row['native_test_count'] = 36
        elif name not in ('native_validation', 'private_draft_build'):
            row.update(state='HOLD', receipt_sha256='c' * 64)
        steps.append(row)
    data = {'schema_version': 1, 'issue': 136,
            'authority': 'MACHINE_LOCAL_DRAFT_CUSTODY_ONLY',
            'exact_checkout_sha': 'd' * 40,
            'release_state': 'HOLD', 'may_publish': False,
            'wordpress_publishing_performed': False,
            'independent_QD_approval': False,
            'source_claim_accuracy_verified': False,
            'qualified_medical_or_emergency_safety_review': False,
            'all_required_machine_gates_executed': True, 'steps': steps}
    return rehash(data)


def rehash(data):
    data['fingerprint_sha256'] = hashlib.sha256(contract.canonical_bytes(
        {key: value for key, value in data.items() if key != 'fingerprint_sha256'}
    )).hexdigest()
    return data


class MandatoryStage(unittest.TestCase):
    def test_stage_present_exactly_once_in_runtime(self):
        self.assertEqual([row[0] for row in preflight.STEPS].count(GATE), 1)

    def test_stage_present_exactly_once_in_receipt_contract(self):
        self.assertEqual(contract.GATE_NAMES.count(GATE), 1)

    def test_stage_lists_identical(self):
        self.assertEqual(tuple(s[0] for s in preflight.STEPS), contract.GATE_NAMES)

    def test_stage_points_to_original_native_r23_gate(self):
        self.assertIn((GATE, SCRIPT, 'hold'), preflight.STEPS)

    def test_stage_script_located_in_preparedness_only(self):
        self.assertTrue((TOOLS / SCRIPT).is_file())

    def test_stage_command_is_exact_readonly_python(self):
        cmd = {s.name: s.command for s in preflight.commands(
            Path('/untrusted-fake-repo'), 'd' * 40)}[GATE]
        self.assertEqual(cmd, (sys.executable, '-I', '-B', 'preparedness/tools/' + SCRIPT))

    def test_no_stage_invokes_wordpress_or_publishing(self):
        for stage in preflight.STEPS:
            self.assertNotIn('wordpress', stage[1].lower())
            self.assertNotIn('publish', stage[1].lower())

    def test_good_13_stage_receipt_is_machine_hold(self):
        result = contract.verify_receipt(receipt(), 'd' * 40)
        self.assertEqual(result['verified_machine_step_count'], 13)
        self.assertIs(result['may_publish'], False)
        self.assertIs(result['qualified_safety_clearance'], False)

    def test_fail_closed_when_stage_missing_even_if_rehashed(self):
        data = receipt()
        data['steps'] = [x for x in data['steps'] if x['gate'] != GATE]
        with self.assertRaises(contract.ContractHold):
            contract.verify_receipt(rehash(data), 'd' * 40)

    def test_fail_closed_when_stage_reordered_even_if_rehashed(self):
        data = receipt()
        data['steps'][-1], data['steps'][-2] = data['steps'][-2], data['steps'][-1]
        with self.assertRaises(contract.ContractHold):
            contract.verify_receipt(rehash(data), 'd' * 40)

    def test_fail_closed_when_stage_labeled_approved(self):
        data = receipt()
        data['steps'][-1]['state'] = 'APPROVED'
        with self.assertRaises(contract.ContractHold):
            contract.verify_receipt(rehash(data), 'd' * 40)

    def test_fail_closed_when_stage_falsifies_a_successful_exit(self):
        data = receipt()
        data['steps'][-1]['exit_code'] = 2
        with self.assertRaises(contract.ContractHold):
            contract.verify_receipt(rehash(data), 'd' * 40)

    def test_fail_closed_on_wrong_frozen_archive_stage_name(self):
        data = receipt()
        data['steps'][-1]['gate'] = 'skip_archive_custody'
        with self.assertRaises(contract.ContractHold):
            contract.verify_receipt(rehash(data), 'd' * 40)


class HoldAuthority(unittest.TestCase):
    def test_plain_hold_output_is_accepted(self):
        self.assertIs(preflight.verify_hold_json(b'{"release_state":"HOLD","may_publish":false}')['may_publish'], False)

    def test_all_explicit_false_flags_accepted(self):
        data = {'release_state': 'HOLD', 'may_publish': False}
        data.update({flag: False for flag in AUTHORITIES})
        self.assertIs(preflight.verify_hold_json(json.dumps(data).encode())['may_publish'], False)

    def test_published_not_allowed_even_with_hold(self):
        data = {'release_state': 'HOLD', 'may_publish': False,
                'wordpress_publishing_performed': True}
        with self.assertRaises(preflight.PreflightHold):
            preflight.verify_hold_json(json.dumps(data).encode())


def authority_mutation(flag, wrong):
    def run(self):
        data = {'release_state': 'HOLD', 'may_publish': False}
        data[flag] = wrong
        with self.assertRaises(preflight.PreflightHold):
            preflight.verify_hold_json(json.dumps(data, allow_nan=False).encode())
    return run


for i, flag in enumerate(AUTHORITIES, 1):
    for suffix, value in [('true', True), ('one', 1), ('string', 'true'), ('null', None)]:
        setattr(HoldAuthority, f'test_authority_{i:02d}_{suffix}_rejected',
                authority_mutation(flag, value))


def step_mutation(index, prop):
    def run(self):
        data = receipt()
        if prop == 'omit':
            del data['steps'][index]
        elif prop == 'duplicate':
            data['steps'].insert(index, copy.deepcopy(data['steps'][index]))
        elif prop == 'reorder':
            data['steps'][index], data['steps'][(index + 1) % len(data['steps'])] = (
                data['steps'][(index + 1) % len(data['steps'])], data['steps'][index])
        with self.assertRaises(contract.ContractHold):
            contract.verify_receipt(rehash(data), 'd' * 40)
    return run


for i in range(len(contract.GATE_NAMES)):
    for prop in ('omit', 'duplicate', 'reorder'):
        setattr(MandatoryStage, f'test_all_gate_{i:02}_{prop}_denied',
                step_mutation(i, prop))


if __name__ == '__main__':
    unittest.main()
