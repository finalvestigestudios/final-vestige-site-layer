"""R63 synthetic/adversarial source-custody tests. No network/CMS/publishing."""
from __future__ import annotations

import copy
import csv
import importlib.util
import io
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def import_file(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


previous = import_file(
    ROOT / 'tests/test_r62_contributor_claim_context_docket.py',
    'r63_parent_synthetic_git_fixture')
r63 = import_file(ROOT / 'tools/r63_contributor_source_impact_crosswalk.py',
                  'r63_under_test')
r62 = previous.r62
Fixture = previous.Fixture


def source_change(f, group='hist-home', operation='notes'):
    path = 'preparedness/sources/fragments/' + group + '.json'
    entry = next(x for x in f.manifest['branches'] if x['name'] == group)
    raw = f.storage[(entry['contributor_commit_sha'], path)]
    doc = json.loads(raw.decode('utf-8'))
    if operation == 'notes':
        doc['sources'][0]['notes'] = 'NEW unreviewed claim; do not replace original.'
    elif operation == 'url':
        doc['sources'][0]['url'] = 'https://new.example.invalid/unreviewed'
    elif operation == 'new':
        doc['sources'].append({
            'id': 'new-archival-catalogue', 'url': 'https://catalogue.example.invalid/entry',
            'notes': 'New catalogue only; primary text not read',
            'human_link_check': False})
    elif operation == 'delete':
        doc['sources'].clear()
    elif operation == 'rename':
        doc['sources'][0]['id'] = 'changed-source-identity'
    elif operation == 'same_id':
        doc['sources'][0]['id'] = 'src-hist-home'
    elif operation == 'same_url':
        doc['sources'][0]['url'] = 'https://example.invalid/hist-home'
    else:
        raise ValueError(operation)
    f.change(group, path, json.dumps(doc, ensure_ascii=False,
                                     sort_keys=True).encode('utf-8'))


def rows(data):
    return list(csv.reader(io.StringIO(data.decode('utf-8'), newline=''),
                           strict=True))


def encode(rows_):
    out = io.StringIO(newline='')
    writer = csv.writer(out, quoting=csv.QUOTE_ALL, lineterminator='\n')
    writer.writerows(rows_)
    return out.getvalue().encode('utf-8')


class R63SourceCrosswalk(unittest.TestCase):
    def setUp(self):
        self.f = Fixture()

    def generate(self):
        lineage = self.f.packet()
        docket = r62.make_report(lineage)
        return lineage, docket, r63.make_report(lineage, docket)

    def test_all_seven_cluster_sources_preserved(self):
        a, b, report = self.generate()
        self.assertEqual(report['counts']['original_source_records'], 7)
        self.assertEqual(report['counts']['observed_source_records_UNVERIFIED'], 7)

    def test_no_source_disappears_when_citations_unchanged(self):
        a, b, report = self.generate()
        self.assertEqual(report['counts']['work_orders'], 7)

    def test_original_29_articles_not_overstated_as_full_corpus(self):
        a, b, report = self.generate()
        self.assertEqual(a['counts']['original_contributor_articles'], 29)
        self.assertTrue(report['full_35_article_R58_custody_NOT_REVALIDATED'])

    def test_citation_occurrences_all_candidate_mappings(self):
        a, b, report = self.generate()
        self.assertEqual(report['counts']['candidate_citation_links_BOTH_VERSIONS'],
                         {'frozen': 58, 'observed': 58})

    def test_source_use_notes_all_candidate_mappings(self):
        a, b, report = self.generate()
        self.assertEqual(report['counts']['source_use_links_BOTH_VERSIONS'],
                         {'frozen': 29, 'observed': 29})

    def test_full_source_notes_survive(self):
        a, b, report = self.generate()
        record = report['source_work_orders_ALL_IDENTITIES_BOTH_VERSIONS'][0]
        self.assertIn('Long original reading depth',
                      record['versions']['frozen'][
                          'unabridged_contributor_reading_NOT_HUMAN_CHECKED']['notes'])

    def test_source_use_notes_survive(self):
        a, b, report = self.generate()
        record = report['source_work_orders_ALL_IDENTITIES_BOTH_VERSIONS'][0]
        self.assertEqual(record['versions']['frozen'][
            'article_source_use_notes_UNABRIDGED_NOT_SUPPORT_PROOF'][0][
            'source_use_note_UNABRIDGED_NOT_CLAIM_PROOF'], 'original full reading note')

    def test_original_context_survives_in_linkage(self):
        a, b, report = self.generate()
        record = report['source_work_orders_ALL_IDENTITIES_BOTH_VERSIONS'][0]
        self.assertIn('{{cite:', record['versions']['frozen'][
            'candidate_citation_occurrences_NOT_SUPPORT_PROOF'][0][
            'unabridged_context_NOT_SUPPORT_PROOF'])

    def test_all_unchanged_sources_not_reverified(self):
        a, b, report = self.generate()
        self.assertEqual(report['counts']['kinds'],
                         {'UNCHANGED_NOT_REVERIFIED': 7})

    def test_hold_fields_never_passed(self):
        a, b, report = self.generate()
        for k in r63.HOLD:
            self.assertIs(report[k], False)
        self.assertEqual(report['release_state'], 'HOLD')

    def test_original_r14_exception_retained(self):
        a, b, report = self.generate()
        self.assertTrue(report['original_R14_contributor_provenance_HOLD'])

    def test_fingerprint_is_deterministic(self):
        a, b, report = self.generate()
        self.assertEqual(report, r63.make_report(copy.deepcopy(a), copy.deepcopy(b)))

    def test_exact_report_replays(self):
        a, b, report = self.generate()
        self.assertTrue(r63.verify_report(report, a, b))

    def test_csv_deterministic(self):
        a, b, report = self.generate()
        self.assertEqual(r63.csv_workbook(report, a, b),
                         r63.csv_workbook(report, a, b))

    def test_csv_never_contains_raw_source_urls(self):
        a, b, report = self.generate()
        self.assertNotIn(b'https://', r63.csv_workbook(report, a, b))

    def test_csv_never_contains_original_source_notes(self):
        a, b, report = self.generate()
        self.assertNotIn(b'Long original reading depth',
                         r63.csv_workbook(report, a, b))

    def test_csv_contains_all_sources(self):
        a, b, report = self.generate()
        self.assertEqual(len(rows(r63.csv_workbook(report, a, b))), 8)

    def test_same_source_url_change_does_not_alias(self):
        source_change(self.f, operation='url')
        a, b, report = self.generate()
        row = next(x for x in report['source_work_orders_ALL_IDENTITIES_BOTH_VERSIONS']
                   if x['cluster'] == 'hist-home')
        self.assertEqual(row['change_kind'], 'CHANGED_NOT_APPROVED')
        self.assertEqual(row['changed_source_fields_NOT_APPROVED'], ['url'])
        self.assertNotEqual(row['versions']['frozen']['record_sha256'],
                            row['versions']['observed']['record_sha256'])

    def test_changed_notes_are_not_silently_accepted(self):
        source_change(self.f)
        a, b, report = self.generate()
        row = next(x for x in report['source_work_orders_ALL_IDENTITIES_BOTH_VERSIONS']
                   if x['cluster'] == 'hist-home')
        self.assertEqual(row['changed_source_fields_NOT_APPROVED'], ['notes'])
        self.assertEqual(row['human_source_review'], 'NOT_REVIEWED')

    def test_new_uncited_source_gets_work_order(self):
        source_change(self.f, operation='new')
        a, b, report = self.generate()
        row = next(x for x in report['source_work_orders_ALL_IDENTITIES_BOTH_VERSIONS']
                   if x['source_id'] == 'new-archival-catalogue')
        self.assertEqual(row['change_kind'], 'ADDED_NOT_APPROVED')
        self.assertIsNone(row['versions']['frozen'])
        self.assertEqual(row['versions']['observed'][
            'candidate_citation_occurrences_NOT_SUPPORT_PROOF'], [])

    def test_removed_source_is_not_auto_aliased(self):
        source_change(self.f, operation='delete')
        a, b, report = self.generate()
        row = next(x for x in report['source_work_orders_ALL_IDENTITIES_BOTH_VERSIONS']
                   if x['source_id'] == 'src-hist-home')
        self.assertEqual(row['change_kind'], 'REMOVED_NOT_ALIASED')
        self.assertIsNone(row['versions']['observed'])

    def test_source_id_rename_is_two_distinct_work_orders(self):
        source_change(self.f, operation='rename')
        a, b, report = self.generate()
        matches = [x for x in report['source_work_orders_ALL_IDENTITIES_BOTH_VERSIONS']
                   if x['cluster'] == 'hist-home']
        self.assertEqual({x['change_kind'] for x in matches},
                         {'REMOVED_NOT_ALIASED', 'ADDED_NOT_APPROVED'})

    def test_changed_article_citation_outside_contributors_retained(self):
        self.f.change('hist-home', content=b'<p>New {{cite:external-source}}.</p>')
        a, b, report = self.generate()
        outside = report[
            'citation_or_source_use_outside_seven_clusters_NOT_ALIASED']['observed']
        self.assertTrue(any(x['ref']['source_id'] == 'external-source'
                            for x in outside))

    def test_changed_article_context_not_claim_verified(self):
        self.f.change('hist-home', content=b'<p>Different instruction {{cite:src-hist-home}}.</p>')
        a, b, report = self.generate()
        self.assertTrue(report['full_35_article_R58_custody_NOT_REVALIDATED'])
        self.assertIs(report['qualified_safety_clearance'], False)

    def test_cross_cluster_source_id_collisions_not_merged(self):
        source_change(self.f, group='hist-field', operation='same_id')
        a, b, report = self.generate()
        self.assertTrue(report['source_id_collisions_NO_ALIAS']['observed'])
        row = next(x for x in report['source_work_orders_ALL_IDENTITIES_BOTH_VERSIONS']
                   if x['cluster'] == 'hist-home')
        self.assertEqual(row['change_kind'], 'UNCHANGED_NOT_REVERIFIED')

    def test_cross_cluster_exact_url_collisions_not_merged(self):
        source_change(self.f, group='hist-field', operation='same_url')
        a, b, report = self.generate()
        self.assertTrue(report['exact_url_shared_identity_groups_NO_DEDUP']['observed'])
        hits = [x for x in report['source_work_orders_ALL_IDENTITIES_BOTH_VERSIONS']
                if x['cluster'] in ('hist-home', 'hist-field')]
        self.assertTrue(all(x['versions']['observed'][
            'same_exact_url_distinct_identity_NOT_ALIAS'] for x in hits))

    def test_source_change_with_same_article_citations_is_reviewed(self):
        source_change(self.f)
        a, b, report = self.generate()
        row = next(x for x in report['source_work_orders_ALL_IDENTITIES_BOTH_VERSIONS']
                   if x['cluster'] == 'hist-home')
        self.assertEqual(row['change_kind'], 'CHANGED_NOT_APPROVED')
        self.assertEqual(len(row['versions']['observed'][
            'candidate_citation_occurrences_NOT_SUPPORT_PROOF']), 10)

    def test_original_notes_are_not_replaced_by_proposed_notes(self):
        source_change(self.f)
        a, b, report = self.generate()
        row = next(x for x in report['source_work_orders_ALL_IDENTITIES_BOTH_VERSIONS']
                   if x['cluster'] == 'hist-home')
        before = row['versions']['frozen'][
            'unabridged_contributor_reading_NOT_HUMAN_CHECKED']['notes']
        after = row['versions']['observed'][
            'unabridged_contributor_reading_NOT_HUMAN_CHECKED']['notes']
        self.assertNotEqual(before, after)
        self.assertIn('Long original', before)

    def test_note_acceptance_remains_unsigned(self):
        a, b, report = self.generate()
        data = rows(r63.csv_workbook(report, a, b))
        data[1][-1] = 'I checked this reference; further human review needed.'
        saved = r63.quarantine_notes(report, a, b, encode(data))
        self.assertEqual(saved['unsigned_untrusted_source_notes'][0][
            'review_state'], 'UNTRUSTED_NOT_REVIEWED')
        self.assertFalse(saved['human_source_links_verified'])

    def test_note_can_contain_safe_unicode(self):
        a, b, report = self.generate()
        data = rows(r63.csv_workbook(report, a, b))
        data[1][-1] = 'Björk — méthode non vérifiée'
        saved = r63.quarantine_notes(report, a, b, encode(data))
        self.assertEqual(saved['unsigned_untrusted_source_notes'][0][
            'untrusted_note_NOT_VERIFIED'], data[1][-1])

    def test_note_absence_not_approval(self):
        a, b, report = self.generate()
        saved = r63.quarantine_notes(report, a, b,
                                    r63.csv_workbook(report, a, b))
        self.assertEqual(saved['unsigned_untrusted_source_notes'], [])
        self.assertFalse(saved['may_publish'])

    def test_says_approved_does_not_change_status(self):
        a, b, report = self.generate()
        data = rows(r63.csv_workbook(report, a, b))
        data[1][-1] = 'APPROVED by me (untrusted assertion).'
        saved = r63.quarantine_notes(report, a, b, encode(data))
        self.assertFalse(saved['independent_QD_approval'])

    def test_reordered_rows_rejected(self):
        a, b, report = self.generate()
        data = rows(r63.csv_workbook(report, a, b))
        data[1], data[2] = data[2], data[1]
        with self.assertRaises(r63.SourceHold):
            r63.quarantine_notes(report, a, b, encode(data))

    def test_missing_rows_rejected(self):
        a, b, report = self.generate()
        data = rows(r63.csv_workbook(report, a, b))
        data.pop()
        with self.assertRaises(r63.SourceHold):
            r63.quarantine_notes(report, a, b, encode(data))

    def test_duplicate_rows_rejected(self):
        a, b, report = self.generate()
        data = rows(r63.csv_workbook(report, a, b))
        data.insert(2, data[1])
        with self.assertRaises(r63.SourceHold):
            r63.quarantine_notes(report, a, b, encode(data))

    def test_extra_approval_column_rejected(self):
        a, b, report = self.generate()
        data = rows(r63.csv_workbook(report, a, b))
        data[0].append('human_approved')
        with self.assertRaises(r63.SourceHold):
            r63.quarantine_notes(report, a, b, encode(data))

    def test_invalid_utf8_rejected(self):
        a, b, report = self.generate()
        with self.assertRaises(r63.SourceHold):
            r63.quarantine_notes(report, a, b, b'\xff\xfe')

    def test_non_bytes_rejected(self):
        a, b, report = self.generate()
        with self.assertRaises(r63.SourceHold):
            r63.quarantine_notes(report, a, b, 'untrusted')

    def test_large_csv_packet_rejected(self):
        a, b, report = self.generate()
        with self.assertRaises(r63.SourceHold):
            r63.quarantine_notes(report, a, b, b'0' * (r63.MAX_CSV_BYTES + 1))

    def test_no_untrusted_input_replaces_report(self):
        a, b, report = self.generate()
        original = copy.deepcopy(report)
        data = rows(r63.csv_workbook(report, a, b))
        data[1][-1] = 'needs field verification'
        r63.quarantine_notes(report, a, b, encode(data))
        self.assertEqual(report, original)


def first(report):
    return report['source_work_orders_ALL_IDENTITIES_BOTH_VERSIONS'][0]


REPORT_ATTACKS = {
    'publish_flag': lambda x: x.__setitem__('may_publish', True),
    'human_link_flag': lambda x: x.__setitem__('human_source_links_verified', True),
    'qualified_flag': lambda x: x.__setitem__('qualified_safety_clearance', True),
    'qd_flag': lambda x: x.__setitem__('independent_QD_approval', True),
    'release_state': lambda x: x.__setitem__('release_state', 'APPROVED'),
    'fingerprint': lambda x: x.__setitem__('fingerprint_sha256', 'f' * 64),
    'parent_R61': lambda x: x.__setitem__('parent_R61_sha256', 'a' * 64),
    'parent_R62': lambda x: x.__setitem__('parent_R62_sha256', 'a' * 64),
    'lost_source': lambda x: x['source_work_orders_ALL_IDENTITIES_BOTH_VERSIONS'].pop(),
    'reversed_sources': lambda x: x['source_work_orders_ALL_IDENTITIES_BOTH_VERSIONS'].reverse(),
    'duplicate_source': lambda x: x['source_work_orders_ALL_IDENTITIES_BOTH_VERSIONS'].append(
        copy.deepcopy(first(x))),
    'changed_source_id': lambda x: first(x).__setitem__('source_id', 'fake-id'),
    'changed_source_cluster': lambda x: first(x).__setitem__('cluster', 'fake'),
    'changed_record_sha': lambda x: first(x)['versions']['frozen'].__setitem__(
        'record_sha256', 'b' * 64),
    'changed_reading_note': lambda x: first(x)['versions']['frozen'][
        'unabridged_contributor_reading_NOT_HUMAN_CHECKED'].__setitem__('notes', 'altered'),
    'changed_citation_count': lambda x: x['counts'][
        'candidate_citation_links_BOTH_VERSIONS'].__setitem__('frozen', 0),
    'changed_source_use_count': lambda x: x['counts'][
        'source_use_links_BOTH_VERSIONS'].__setitem__('observed', 0),
    'removed_citation_ref': lambda x: first(x)['versions']['frozen'][
        'candidate_citation_occurrences_NOT_SUPPORT_PROOF'].pop(),
    'changed_citation_ref': lambda x: first(x)['versions']['frozen'][
        'candidate_citation_occurrences_NOT_SUPPORT_PROOF'][0].__setitem__(
            'offset_codepoints', 9999),
    'removed_source_use': lambda x: first(x)['versions']['frozen'][
        'article_source_use_notes_UNABRIDGED_NOT_SUPPORT_PROOF'].pop(),
    'source_kind_grant': lambda x: first(x).__setitem__('change_kind', 'APPROVED'),
    'review_state_grant': lambda x: first(x).__setitem__('human_source_review', 'APPROVED'),
    'safety_state_grant': lambda x: first(x).__setitem__(
        'qualified_claim_safety_review', 'APPROVED'),
    'drop_outside_hold': lambda x: x.pop('full_35_article_R58_custody_NOT_REVALIDATED'),
    'remove_collision_inventory': lambda x: x.pop('source_id_collisions_NO_ALIAS'),
    'wrong_work_order': lambda x: first(x).__setitem__('work_order_sha256', '0' * 64),
}


def add_report_attack(name, mutate):
    def test(self):
        lineage, docket, report = self.generate()
        altered = copy.deepcopy(report)
        mutate(altered)
        with self.assertRaises(r63.SourceHold):
            r63.verify_report(altered, lineage, docket)
    setattr(R63SourceCrosswalk, 'test_report_tamper_' + name, test)


for attack_name, mutation in REPORT_ATTACKS.items():
    add_report_attack(attack_name, mutation)


NOTE_ATTACKS = {
    'formula_equals': '=HYPERLINK("https://example.invalid")',
    'formula_plus': '+1+2',
    'formula_minus': '-CMD',
    'formula_at': '@SUM(A1:A2)',
    'formula_spaces': '  =IMPORTRANGE()',
    'fullwidth_formula': '\uff1dHYPERLINK()',
    'tabs': 'review\tpassed',
    'newline': 'review\npassed',
    'carriage_return': 'review\rpassed',
    'nul': 'review\x00passed',
    'bidi_override': 'review\u202epassed',
    'left_to_right_override': '\u202dapproved',
    'zero_width_space': 'review\u200bpassed',
    'word_joiner': 'review\u2060passed',
    'byte_order_mark': '\ufeffPASS',
    'unicode_line_separator': 'review\u2028passed',
    'unicode_paragraph_separator': 'review\u2029passed',
    'del': 'review\x7fpassed',
    'too_long': 'x' * 3001,
}


def add_note_attack(name, note):
    def test(self):
        lineage, docket, report = self.generate()
        data = rows(r63.csv_workbook(report, lineage, docket))
        data[1][-1] = note
        with self.assertRaises(r63.SourceHold):
            r63.quarantine_notes(report, lineage, docket, encode(data))
    setattr(R63SourceCrosswalk, 'test_note_tamper_' + name, test)


for attack_name, note in NOTE_ATTACKS.items():
    add_note_attack(attack_name, note)


if __name__ == '__main__':
    unittest.main()
