"""Synthetic/adversarial R345 tests: no real source edits, no QD or release PASS."""
import copy
from hashlib import sha256
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import r345_conflicted_source_claim_quarantine as m


def sample():
    records = {'register.json': []}
    tickets = []
    for i, (sid, pair) in enumerate(sorted(m.CONFLICT_FILES.items())):
        records['register.json'].append({'id': sid, 'url': 'https://www.example.gov/' + sid,
            'title': 'starting point', 'supports': '', 'verified_on': None})
        for j, fn in enumerate(pair):
            records.setdefault(fn, []).append({'id': sid,
                'url': 'https://www.example.gov/' + sid,
                'title': 'Evidence for ' + sid + ' #' + str(j),
                'publisher': 'Agency', 'kind': 'regulator',
                'supports': 'Documented scope ' + str(j),
                'verified_on': '2026-10-' + ('29' if j == 0 else '30'),
                'human_link_check': False})
        tickets.append({'ticket_id': '%024x' % (i + 1), 'source_id': sid,
                        'kind': 'articles', 'slug': 'sample-article-' + str(i),
                        'heading': 'example', 'claim_text_sha256': 'a' * 64,
                        'human_claim_source_adjudication': 'UNREVIEWED_REQUIRED'})
    return records, tickets


class TestCore(unittest.TestCase):
    def test_01_baseline(self):
        r, t = sample(); x = m.make_packets(r, t)
        self.assertEqual(x['errors'], [])
        self.assertEqual(x['impacted_tickets'], 4)
        self.assertEqual(x['impacted_distinct_documents'], 4)
        self.assertEqual(len(x['packets']), 4)

    def test_02_always_unapproved(self):
        r, t = sample(); x = m.make_packets(r, t)
        self.assertTrue(all(p['candidate_selected'] is None for p in x['packets']))
        self.assertTrue(all(p['human_claim_source_adjudication'] == 'UNREVIEWED_REQUIRED' for p in x['packets']))
        self.assertTrue(all(p['review_disposition'] == 'QUARANTINED_SOURCE_ID' for p in x['packets']))
        self.assertTrue(all(v is False for v in m.HOLD.values()))

    def test_03_repeat_deterministic(self):
        r, t = sample()
        self.assertEqual(m.canonical_json(m.make_packets(r, t)), m.canonical_json(m.make_packets(copy.deepcopy(r), copy.deepcopy(t))))

    def test_04_row_order_independent(self):
        r, t = sample(); x = m.make_packets(r, t)
        for item in r.values(): item.reverse()
        t.reverse()
        self.assertEqual(m.canonical_json(x), m.canonical_json(m.make_packets(r, t)))

    def test_05_no_claim_text_or_url_exposed(self):
        r, t = sample(); x = m.make_packets(r, t)
        serialized = json.dumps(x)
        self.assertNotIn('https://www.example.gov/', serialized)
        self.assertNotIn('Documented scope', serialized)
        self.assertNotIn('sample private full text', serialized)

    def test_06_report_has_unique_impact(self):
        r, t = sample(); t.append({**t[0], 'ticket_id': 'f' * 24, 'slug': t[0]['slug']})
        x = m.make_packets(r, t)
        self.assertEqual(x['impacted_tickets'], 5)
        self.assertEqual(x['impacted_distinct_documents'], 4)

    def test_07_non_conflict_ticket_not_counted(self):
        r, t = sample(); r['register.json'].append({'id': 'ordinary-source', 'url': 'https://www.example.gov/ordinary'})
        t.append({**t[0], 'ticket_id': 'f' * 24, 'source_id': 'ordinary-source'})
        x = m.make_packets(r, t)
        self.assertEqual(x['errors'], [])
        self.assertEqual(x['impacted_tickets'], 4)

    def test_08_unknown_source_fails(self):
        r, t = sample(); t[0]['source_id'] = 'not-real'
        self.assertTrue(any('UNKNOWN_CITED_SOURCE' in e for e in m.make_packets(r, t)['errors']))

    def test_09_duplicate_ticket_fails(self):
        r, t = sample(); t.append(copy.deepcopy(t[0]))
        self.assertIn('INVALID_OR_DUPLICATE_CITATION_TICKET_ID', m.make_packets(r, t)['errors'])

    def test_10_missing_tickets_fails(self):
        r, _ = sample()
        self.assertIn('CITATION_TICKETS_REQUIRED', m.make_packets(r, None)['errors'])

    def test_11_non_mapping_fails(self):
        self.assertIn('SOURCE_RECORD_MAP_REQUIRED', m.make_packets([], [])['errors'])

    def test_12_bad_source_rows(self):
        r, t = sample(); r['register.json'] = 'not-list'
        self.assertIn('INVALID_SOURCE_FILE_ROWS', m.make_packets(r, t)['errors'])

    def test_13_bad_row(self):
        r, t = sample(); r['register.json'].append(12)
        self.assertTrue(any('INVALID_SOURCE_ROW' in e for e in m.make_packets(r, t)['errors']))

    def test_14_forged_approval(self):
        r, t = sample(); t[0]['human_claim_source_adjudication'] = 'QD_PASS'
        self.assertTrue(any('FORGED_CLAIM_REVIEW_STATE' in e for e in m.make_packets(r, t)['errors']))

    def test_15_missing_approval_state(self):
        r, t = sample(); del t[0]['human_claim_source_adjudication']
        self.assertTrue(any('FORGED_CLAIM_REVIEW_STATE' in e for e in m.make_packets(r, t)['errors']))

    def test_16_bad_ticket(self):
        r, t = sample(); t.append('raw string')
        self.assertIn('INVALID_CITATION_TICKET', m.make_packets(r, t)['errors'])

    def test_17_bad_ticket_id(self):
        r, t = sample(); t[0]['ticket_id'] = '123'
        self.assertIn('INVALID_OR_DUPLICATE_CITATION_TICKET_ID', m.make_packets(r, t)['errors'])

    def test_18_invalid_doc_kind(self):
        r, t = sample(); t[0]['kind'] = 'public'
        self.assertTrue(any('INVALID_IMPACT_DOCUMENT_ID' in e for e in m.make_packets(r, t)['errors']))

    def test_19_invalid_doc_slug(self):
        r, t = sample(); t[0]['slug'] = '../../secrets'
        self.assertTrue(any('INVALID_IMPACT_DOCUMENT_ID' in e for e in m.make_packets(r, t)['errors']))

    def test_20_invalid_claim_digest(self):
        r, t = sample(); t[0]['claim_text_sha256'] = 'not-sha'
        self.assertTrue(any('INVALID_IMPACT_CLAIM_DIGEST' in e for e in m.make_packets(r, t)['errors']))

    def test_21_no_authentic_checkout(self):
        with tempfile.TemporaryDirectory() as d:
            report = m.native_audit(Path(d))
            self.assertEqual(report['state'], 'INVALID_HARD_HOLD')
            self.assertFalse(report['may_publish'])
            self.assertFalse(report['qualified_qd_pass'])

    def test_22_git_blob(self):
        self.assertEqual(m.git_blob(b'hello'), 'b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0')

    def test_23_source_missing(self):
        with tempfile.TemporaryDirectory() as d:
            _, errs = m._native_source_records(Path(d), {'register.json': '0'*40})
            self.assertTrue(any('MISSING_OR_SYMLINK' in e for e in errs))

    def test_24_source_valid(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'sources'; p.mkdir()
            b = b'{"sources":[]}'
            (p / 'register.json').write_bytes(b)
            rows, errs = m._native_source_records(Path(d), {'register.json': m.git_blob(b)})
            self.assertEqual(errs, [])
            self.assertEqual(rows['register.json'], [])

    def test_25_source_modified(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'sources'; p.mkdir()
            (p / 'register.json').write_bytes(b'{"sources":[]}')
            _, errs = m._native_source_records(Path(d), {'register.json': '0'*40})
            self.assertIn('SOURCE_BLOB_DRIFT:register.json', errs)

    def test_26_source_extra(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'sources'; p.mkdir()
            (p / 'register.json').write_bytes(b'{"sources":[]}')
            (p / 'injected.json').write_bytes(b'{"sources":[]}')
            _, errs = m._native_source_records(Path(d), {'register.json': m.git_blob(b'{"sources":[]}')})
            self.assertIn('SOURCE_FILE_SET_DRIFT', errs)

    def test_27_source_symlink(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'sources'; p.mkdir()
            target = Path(d) / 'real.json'; target.write_bytes(b'{"sources":[]}')
            (p / 'register.json').symlink_to(target)
            _, errs = m._native_source_records(Path(d), {'register.json': m.git_blob(target.read_bytes())})
            self.assertIn('MISSING_OR_SYMLINK_SOURCE:register.json', errs)

    def test_28_source_bad_json(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'sources'; p.mkdir()
            b = b'{'
            (p / 'register.json').write_bytes(b)
            _, errs = m._native_source_records(Path(d), {'register.json': m.git_blob(b)})
            self.assertIn('UNREADABLE_SOURCE:register.json', errs)


# Each distinct source variant gets its own independent named adversarial test.
def add_case(name, modify, expected_error):
    def run(self):
        records, tickets = sample()
        modify(records, tickets)
        result = m.make_packets(records, tickets)
        self.assertTrue(any(expected_error in e for e in result['errors']), (name, result['errors']))
    setattr(TestCore, 'test_generated_' + name, run)


for sid, pair in m.CONFLICT_FILES.items():
    tag = sid.replace('-', '_')

    def missing(r, t, sid=sid, pair=pair):
        r[pair[1]] = [x for x in r[pair[1]] if x['id'] != sid]
    add_case(tag + '_missing_variant', missing, 'VERIFIED_CONFLICT')

    def altered_file(r, t, sid=sid, pair=pair):
        for row in r[pair[1]]:
            if row['id'] == sid: row['id'] = sid + '-alternate'
    add_case(tag + '_renamed_source', altered_file, 'VERIFIED_CONFLICT')

    def wrong_url(r, t, sid=sid, pair=pair):
        for row in r[pair[1]]:
            if row['id'] == sid: row['url'] += '/changed'
    add_case(tag + '_divergent_url', wrong_url, 'CONFLICT_URL')

    def duplicate_local(r, t, sid=sid, pair=pair):
        row = next(x for x in r[pair[0]] if x['id'] == sid)
        r[pair[0]].append(copy.deepcopy(row))
    add_case(tag + '_same_file_duplicate', duplicate_local, 'DUPLICATED_SOURCE')

    def identical(r, t, sid=sid, pair=pair):
        a = next(x for x in r[pair[0]] if x['id'] == sid)
        b = next(x for x in r[pair[1]] if x['id'] == sid)
        b.clear(); b.update(copy.deepcopy(a))
    add_case(tag + '_false_identical_conflict', identical, 'REVIEW_CONFLICT_VARIANTS_IDENTICAL')

    def extra_verified(r, t, sid=sid, pair=pair):
        r.setdefault('fragments/unapproved.json', []).append(copy.deepcopy(next(x for x in r[pair[0]] if x['id'] == sid)))
    add_case(tag + '_third_verified_variant', extra_verified, 'VERIFIED_CONFLICT')

    def fake_selected(r, t, sid=sid):
        ix = next(i for i, item in enumerate(t) if item['source_id'] == sid)
        t[ix]['human_claim_source_adjudication'] = 'approved'
    add_case(tag + '_forged_review', fake_selected, 'FORGED_CLAIM')

    def invalid_ticket_digest(r, t, sid=sid):
        ix = next(i for i, item in enumerate(t) if item['source_id'] == sid)
        t[ix]['claim_text_sha256'] = '0' * 63
    add_case(tag + '_bad_claim_fingerprint', invalid_ticket_digest, 'INVALID_IMPACT_CLAIM_DIGEST')

    def invalid_ticket_slug(r, t, sid=sid):
        ix = next(i for i, item in enumerate(t) if item['source_id'] == sid)
        t[ix]['slug'] = 'not a slug'
    add_case(tag + '_bad_doc_id', invalid_ticket_slug, 'INVALID_IMPACT_DOCUMENT_ID')

    def unverified(r, t, sid=sid, pair=pair):
        for row in r[pair[1]]:
            if row['id'] == sid: row['verified_on'] = None
    add_case(tag + '_downgraded_verification', unverified, 'VERIFIED_CONFLICT')

if __name__ == '__main__':
    unittest.main()
