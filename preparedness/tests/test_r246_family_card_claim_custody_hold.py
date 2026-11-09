"""Isolated negative controls for R246; not a native Preparedness build."""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

FILE = Path(__file__).resolve().parents[1] / 'tools' / 'r246_family_card_claim_custody_hold.py'
spec = importlib.util.spec_from_file_location('r246_gate', FILE)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


def fixtures():
    return {
        g.A: b'<p>{{link:family-reunification-card|fold-over wallet card}} keeps what you type on your own device</p>',
        g.T: (b'{{cite:shelter-fcc-comms}} It is not sent or saved. Closing the tab clears it. '
              b'It prints only the out-of-area contact, a phone and the first meeting place. '
              b'Minimal version: only the out-of-area contact, a phone number, the first meeting place and the review date'),
        g.M: json.dumps({'n': 104, 'slug': 'family-reunification-card', 'kind': 'tool',
                         'status': {'publish': 'draft'}, 'safety_review': {'state': 'pending'},
                         'description': 'Nothing is stored.'}).encode(),
        g.J: (b'function rcModel(fields, minimal) { row("Household", c.hhName); '
              b'row("Phone", c.hhPhone); row("Out-of-area contact", c.outName); '
              b'var back = minimal; "Kept in our written plan at home."; }'),
        g.C: b'function paDownloadText(filename, text) {}',
    }


def pins(x):
    return {path: g.git_blob(raw) for path, raw in x.items()}


class R246ClaimsHold(unittest.TestCase):
    def test_baseline_held_never_approved(self):
        original = fixtures()
        result = g.assess_source_custody(original, pins(original))
        self.assertEqual(result['state'], g.HOLD)
        self.assertEqual(result['source_count'], 5)
        self.assertEqual(result['held_claim_count'], 7)
        for flag in ('claim_truth_evaluated', 'runtime_privacy_certified', 'release_authorized',
                     'independent_qd_pass', 'source_review_approved', 'medical_safety_verified',
                     'merchant_approved'):
            self.assertIs(result[flag], False)

    def test_replay_same_receipt(self):
        original = fixtures()
        a = g.assess_source_custody(original, pins(original))
        b = g.assess_source_custody(dict(reversed(list(original.items()))), pins(original))
        self.assertEqual(a, b)

    def test_reject_unregistered_additional_file(self):
        x = fixtures(); x['tools/new.js'] = b'x'
        with self.assertRaisesRegex(ValueError, 'exact five-source'):
            g.assess_source_custody(x, pins(fixtures()))

    def test_reject_missing_file(self):
        x = fixtures(); x.pop(g.C)
        with self.assertRaisesRegex(ValueError, 'exact five-source'):
            g.assess_source_custody(x, pins(fixtures()))

    def test_duplicate_metadata_json(self):
        x = fixtures(); x[g.M] = b'{"n":104,"n":104}'
        with self.assertRaisesRegex(ValueError, 'duplicate metadata'):
            g.assess_source_custody(x, pins(x))

    def test_missing_tool_draft_state(self):
        x = fixtures(); m=json.loads(x[g.M]); m['status']['publish']='publish'; x[g.M]=json.dumps(m).encode()
        with self.assertRaisesRegex(ValueError, 'state changed'):
            g.assess_source_custody(x, pins(x))

    def test_privacy_claim_changes_need_human_docket(self):
        for path, old in ((g.A,b'keeps what you type on your own device'),
                          (g.T,b'It is not sent or saved. Closing the tab clears it.'),
                          (g.T,b'It prints only the out-of-area contact, a phone and the first meeting place.'),
                          (g.T,b'Minimal version: only the out-of-area contact, a phone number, the first meeting place and the review date'),
                          (g.M,b'Nothing is stored.'),
                          (g.J,b'row("Household", c.hhName)'),
                          (g.J,b'Kept in our written plan at home.')):
            with self.subTest(path=path, claim=old):
                x=fixtures(); x[path]=x[path].replace(old,b'REVIEW REQUIRED')
                with self.assertRaisesRegex(ValueError, 'held-claim witness changed'):
                    g.assess_source_custody(x, pins(x))

    def test_original_pin_cannot_be_bypassed_by_changed_code(self):
        for path in g.SOURCES:
            with self.subTest(path=path):
                x=fixtures(); ref=pins(x); x[path] += b'\nmutation'
                with self.assertRaisesRegex(ValueError, 'source identity changed'):
                    g.assess_source_custody(x, ref)

    def test_source_link_removed_even_under_new_pin(self):
        x=fixtures(); x[g.A]=x[g.A].replace(b'{{link:family-reunification-card|fold-over wallet card}}',b'outbound product')
        with self.assertRaisesRegex(ValueError, 'link provenance'):
            g.assess_source_custody(x, pins(x))

    def test_tool_citation_removed_even_under_new_pin(self):
        x=fixtures(); x[g.T]=x[g.T].replace(b'{{cite:shelter-fcc-comms}}',b'uncited')
        with self.assertRaisesRegex(ValueError, 'source citation'):
            g.assess_source_custody(x, pins(x))

    def test_refuses_null_bytes(self):
        x=fixtures(); x[g.J] += b'\x00'
        with self.assertRaisesRegex(ValueError, 'invalid source bytes'):
            g.assess_source_custody(x, pins(x))

    def test_bad_metadata_id(self):
        for value in (None, 101, 0, '104', 35, True):
            with self.subTest(value=value):
                x=fixtures(); m=json.loads(x[g.M]); m['n']=value; x[g.M]=json.dumps(m).encode()
                with self.assertRaisesRegex(ValueError,'state changed'):
                    g.assess_source_custody(x, pins(x))


def create_mutation_test(index):
    def test(self):
        x=fixtures(); base=pins(x)
        path=list(g.SOURCES)[index % 5]
        raw=x[path]
        x[path]=raw + bytes([65 + index % 26]) + b'\n'
        with self.assertRaisesRegex(ValueError, 'source identity changed'):
            g.assess_source_custody(x, base)
    return test

for i in range(55):
    setattr(R246ClaimsHold, f'test_source_mutation_{i:02d}', create_mutation_test(i))

if __name__ == '__main__':
    unittest.main()
