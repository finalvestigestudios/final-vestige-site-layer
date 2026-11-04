"""R127 sandbox-only adversarial tests; never touch working-tree fixtures."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

MODULE = Path(__file__).resolve().parents[1] / 'tools' / 'r127_qa_safety_disagreement_gate.py'
spec = importlib.util.spec_from_file_location('r127_gate', MODULE)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def seed():
    slate = [{'slug': f'other-{i:02d}', 'gate': False} for i in range(31)]
    slate += [{'slug': s, 'gate': True} for s in ('household-emergency-plan',
               'three-day-kit', 'go-bags', 'preparedness-real-households')]
    source = {'sources': [{'id': 'start-redcross-older-adults', 'kind': 'nonprofit',
                           'human_link_check': False}]}
    doc = {}
    for v in ('candidate', 'qa'):
        label = 'simulated-outage evening' if v == 'candidate' else 'lights-out evening'
        extra = ' Also keep refrigeration on.' if v == 'candidate' else ' Keep refrigeration powered.'
        plan = (f'<ul><li><strong>The {label}.</strong> Leave alarms and medical equipment '
                'powered; do not switch off the main breaker.' + extra + '</li></ul>')
        kit = ('<p>For refrigerated medicine consult a pharmacist for product-specific '
               'handling. {{cite:start-ready-power}}' + (' Ask before an outage.' if v == 'qa' else '') + '</p>')
        doc[v] = {'plan': plan.encode(), 'kit': kit.encode(),
                  'source': json.dumps(source).encode(),
                  'taxonomy': json.dumps({'base_path': '/preparedness/', 'slate': slate}).encode()}
    pins = {v: {k: gate.gitblob(raw) for k, raw in doc[v].items()} for v in doc}
    return doc, pins


class Basic(unittest.TestCase):
    def test_positive_holds(self):
        d, pins = seed()
        x = gate.audit(d, pins=pins)
        self.assertEqual(x['status'], 'HOLD_HUMAN_ADJUDICATION')
        self.assertEqual(len(x['review_items']), 4)
        self.assertEqual(x['article_count'], 35)
        self.assertFalse(x['publish_permitted'])
        self.assertFalse(x['independent_QD_PASS'])
        self.assertFalse(x['medical_safety_verified'])
        self.assertTrue(x['electrical_drill_wording_differs'])
        self.assertTrue(x['medication_wording_differs'])
        self.assertTrue(all(not a['approved'] for a in x['review_items']))

    def test_sha256_is_not_a_git_sha1_blob(self):
        self.assertEqual(gate.gitblob(b'hello'), 'b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0')

    def test_absent_version(self):
        d, p = seed()
        del d['qa']
        with self.assertRaisesRegex(gate.Hold, 'VERSION_ROSTER'):
            gate.audit(d, pins=p)

    def test_unexpected_version(self):
        d, p = seed()
        d['production'] = {}
        with self.assertRaisesRegex(gate.Hold, 'VERSION_ROSTER'):
            gate.audit(d, pins=p)

    def test_nonbyte_evidence(self):
        d, p = seed()
        d['candidate']['kit'] = 'text'
        with self.assertRaisesRegex(gate.Hold, 'NON_BYTE_EVIDENCE'):
            gate.audit(d, pins=p)

    def test_missing_files(self):
        d, p = seed()
        del d['qa']['source']
        with self.assertRaisesRegex(gate.Hold, 'FILE_ROSTER'):
            gate.audit(d, pins=p)

    def test_wrong_blob_pin(self):
        d, p = seed()
        p['candidate']['plan'] = '0'*40
        with self.assertRaisesRegex(gate.Hold, 'EVIDENCE_BLOB_MISMATCH'):
            gate.audit(d, pins=p)

    def test_identical_drills_not_assumed_reviewed(self):
        d, p = seed()
        d['qa']['plan'] = d['candidate']['plan']
        p['qa']['plan'] = gate.gitblob(d['qa']['plan'])
        with self.assertRaisesRegex(gate.Hold, 'REVIEW_COMPARISON_UNEXPECTEDLY_IDENTICAL'):
            gate.audit(d, pins=p)

    def test_identical_medicine_not_assumed_reviewed(self):
        d, p = seed()
        d['qa']['kit'] = d['candidate']['kit']
        p['qa']['kit'] = gate.gitblob(d['qa']['kit'])
        with self.assertRaisesRegex(gate.Hold, 'REVIEW_COMPARISON_UNEXPECTEDLY_IDENTICAL'):
            gate.audit(d, pins=p)


def replace_doc(doc, version, key, transform):
    """Apply a mutation with updated synthetic blob identity; prove semantic gates run."""
    src = doc[version][key].decode()
    doc[version][key] = transform(src).encode()


def mutate_json(doc, version, key, transform):
    obj = json.loads(doc[version][key])
    transform(obj)
    doc[version][key] = json.dumps(obj).encode()


CASES = [
    ('breaker_warning_deleted', 'plan', lambda s:s.replace('do not switch off the main breaker', 'run the kit rehearsal'), 'UNPROTECTED_MAIN_BREAKER_DRILL'),
    ('breaker_warning_weakened', 'plan', lambda s:s.replace('do not switch off the main breaker', 'switch off the main breaker'), 'UNPROTECTED_MAIN_BREAKER_DRILL'),
    ('breaker_warning_partial', 'plan', lambda s:s.replace('do not switch off the main breaker', 'do not switch off power'), 'UNPROTECTED_MAIN_BREAKER_DRILL'),
    ('breaker_warning_case_change', 'plan', lambda s:s.replace('do not switch off the main breaker', 'never switch main electricity'), 'UNPROTECTED_MAIN_BREAKER_DRILL'),
    ('critical_alarm_missing', 'plan', lambda s:s.replace('alarms', 'ordinary lights'), 'MISSING_SAFETY_CRITICAL_EQUIPMENT'),
    ('critical_medical_missing', 'plan', lambda s:s.replace('medical', 'optional'), 'MISSING_SAFETY_CRITICAL_EQUIPMENT'),
    ('practice_item_missing', 'plan', lambda s:s.replace('simulated-outage evening', 'routine') .replace('lights-out evening', 'routine'), 'AMBIGUOUS_OR_MISSING_PASSAGE'),
    ('duplicate_practice_items', 'plan', lambda s:s + s, 'AMBIGUOUS_OR_MISSING_PASSAGE'),
    ('medication_no_pharmacist', 'kit', lambda s:s.replace('pharmacist', 'an advertisement'), 'NO_PRODUCT_SPECIFIC_MEDICATION_REFERRAL'),
    ('medication_no_citation', 'kit', lambda s:s.replace('{{cite:start-ready-power}}', ''), 'MISSING_MEDICATION_SOURCE_CITATION'),
    ('medication_topic_missing', 'kit', lambda s:s.replace('refrigerated medicine', 'packed food'), 'AMBIGUOUS_OR_MISSING_PASSAGE'),
    ('duplicate_medicine_advice', 'kit', lambda s:s+s, 'AMBIGUOUS_OR_MISSING_PASSAGE'),
    ('unclosed_medicine_paragraph', 'kit', lambda s:s.replace('</p>', ''), 'AMBIGUOUS_OR_MISSING_PASSAGE'),
]

JSON_CASES = [
    ('source_not_regulator', 'source', lambda o:o['sources'][0].update(kind='regulator'), 'REDCROSS_MISCLASSIFIED'),
    ('source_not_generic', 'source', lambda o:o['sources'][0].update(kind='agency'), 'REDCROSS_MISCLASSIFIED'),
    ('source_link_check_claim', 'source', lambda o:o['sources'][0].update(human_link_check=True), 'UNAUTHORIZED_HUMAN_LINK_CHECK'),
    ('source_link_check_missing', 'source', lambda o:o['sources'][0].pop('human_link_check'), 'UNAUTHORIZED_HUMAN_LINK_CHECK'),
    ('source_not_present', 'source', lambda o:o.update(sources=[]), 'REDCROSS_SOURCE_ID'),
    ('source_duplicate', 'source', lambda o:o['sources'].append(dict(o['sources'][0])), 'REDCROSS_SOURCE_ID'),
    ('source_wrong_identifier', 'source', lambda o:o['sources'][0].update(id='redcross-other'), 'REDCROSS_SOURCE_ID'),
    ('source_no_records', 'source', lambda o:o.pop('sources'), 'MISSING_SOURCES'),
    ('taxonomy_too_short', 'taxonomy', lambda o:o['slate'].pop(), 'MISSING_35_ARTICLE_SLATE'),
    ('taxonomy_duplicate', 'taxonomy', lambda o:o['slate'].__setitem__(0, dict(o['slate'][1])), 'DUPLICATE_OR_INVALID_ARTICLE_ROUTE'),
    ('taxonomy_renamed_base', 'taxonomy', lambda o:o.update(base_path='/other/'), 'UNEXPECTED_BASE_PATH'),
    ('taxonomy_ungated_plan', 'taxonomy', lambda o:next(a for a in o['slate'] if a['slug']=='household-emergency-plan').update(gate=False), 'MISSING_START_HERE_SAFETY_GATE'),
    ('taxonomy_ungated_kit', 'taxonomy', lambda o:next(a for a in o['slate'] if a['slug']=='three-day-kit').update(gate=False), 'MISSING_START_HERE_SAFETY_GATE'),
    ('taxonomy_ungated_bags', 'taxonomy', lambda o:next(a for a in o['slate'] if a['slug']=='go-bags').update(gate=False), 'MISSING_START_HERE_SAFETY_GATE'),
    ('taxonomy_ungated_real', 'taxonomy', lambda o:next(a for a in o['slate'] if a['slug']=='preparedness-real-households').update(gate=False), 'MISSING_START_HERE_SAFETY_GATE'),
    ('taxonomy_nonboolean', 'taxonomy', lambda o:next(a for a in o['slate'] if a['slug']=='go-bags').update(gate='true'), 'MISSING_START_HERE_SAFETY_GATE'),
    ('taxonomy_missing_gate', 'taxonomy', lambda o:next(a for a in o['slate'] if a['slug']=='go-bags').pop('gate'), 'MISSING_START_HERE_SAFETY_GATE'),
    ('taxonomy_missing_plan', 'taxonomy', lambda o:next(a for a in o['slate'] if a['slug']=='household-emergency-plan').update(slug='other-extra'), 'MISSING_START_HERE_SAFETY_GATE'),
]


def add_mutation_tests():
    for version in ('candidate', 'qa'):
        for title, key, operation, code in CASES:
            def check(self, v=version, k=key, op=operation, expected=code):
                d, p = seed()
                replace_doc(d, v, k, op)
                p[v][k] = gate.gitblob(d[v][k])
                with self.assertRaisesRegex(gate.Hold, expected):
                    gate.audit(d, pins=p)
            setattr(Basic, f'test_{version}_{title}', check)
        for title, key, operation, code in JSON_CASES:
            def check(self, v=version, k=key, op=operation, expected=code):
                d, p = seed()
                mutate_json(d, v, k, op)
                p[v][k] = gate.gitblob(d[v][k])
                with self.assertRaisesRegex(gate.Hold, expected):
                    gate.audit(d, pins=p)
            setattr(Basic, f'test_{version}_{title}', check)


add_mutation_tests()

if __name__ == '__main__':
    unittest.main()
