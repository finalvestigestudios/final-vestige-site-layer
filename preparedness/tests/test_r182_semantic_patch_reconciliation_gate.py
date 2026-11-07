"""Synthetic semantic/mutation tests for R182. No live repository or writes required."""
from __future__ import annotations
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

MODULE_PATH = Path(__file__).with_name('r182_semantic_patch_reconciliation_gate.py')
spec = importlib.util.spec_from_file_location('r182_gate', MODULE_PATH)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

PLAN = '''<section><ul><li><strong>The simulated-outage evening.</strong>
Pretend the power is out. Switch off nonessential lights. Leave on everything that keeps people safe,
including smoke and carbon monoxide alarms, and all medical or safety-critical equipment.
Do not switch off the main breaker as a drill.</li></ul></section>'''
KIT = '''<article><p><span>Editor's note</span> Do not stop, throw away or ration a medicine you depend on.
Ask your prescriber or pharmacist, before an emergency, whether each of your medicines needs refrigeration,
how long it can safely stay warm, and what the plan is for getting a replacement.
If you are already in an outage and unsure, call your doctor or pharmacist.</p>
<p>Ask your pharmacist what interim-use and replacement plan they recommend if a refrigerated medicine warms up.
{{cite:start-cdc-pyh-prescriptions}}</p></article>'''
TAX = {'slate': [{'slug': f'guide-{i}', 'track': 'modern' if i < 20 else 'lost-ways',
                  'gate': i < 20, 'n': i + 1} for i in range(35)]}
for i, slug in enumerate(gate.REQUIRED_FAMILY):
    TAX['slate'][i]['slug'] = slug
SOURCES = {'sources': [{'id': 'start-redcross-older-adults', 'publisher': 'American Red Cross',
                        'kind': 'nonprofit'}]}
TESTS = '''
class Test:
    def test_fragment_may_upgrade_a_placeholder_but_not_a_verified_source(self):
        with tempfile.TemporaryDirectory() as td:
            sandbox = td
            shutil.copytree(ROOT, sandbox)
            lib = build.Library(root=sandbox)
            assert "duplicate source id" == "duplicate source id"
    def test_register_fragments_cannot_duplicate_ids(self):
        with tempfile.TemporaryDirectory() as td:
            sandbox = td
            shutil.copytree(ROOT, sandbox)
            lib = build.Library(root=sandbox)
            assert "duplicate source id" == "duplicate source id"
    def test_unverified_source_cannot_be_cited(self):
        fixture_id = "test-fixture-unverified-source"
        verified_on = None
    def test_every_modern_slate_item_is_gated(self):
        assert True
    def test_red_cross_cannot_be_called_a_regulator(self):
        assert "not a regulator"
'''

def valid_fixture():
    return {'plan': PLAN, 'kit': KIT, 'sources': json.dumps(SOURCES),
            'taxonomy': json.dumps(TAX), 'tests': TESTS}

def digest_fixture(fixture):
    return {k: gate.blob_sha(v) for k,v in fixture.items()}


class BaselineTests(unittest.TestCase):
    def test_synthetic_baseline_accepts_content_but_not_release(self):
        result = gate.check_sources(valid_fixture(), digest_fixture(valid_fixture()))
        self.assertEqual(result['safety_adjudicated'], False)
        self.assertEqual(result['citation_claims_verified'], False)
        self.assertEqual(result['article_roster'], 35)

    def test_blob_sha_is_git_blob_not_plain_sha1(self):
        self.assertEqual(gate.blob_sha('test content'), '08cf6101416f0ce0dda3c80e627f333854c4085c')

    def test_default_release_status_hard_hold(self):
        self.assertEqual(gate.HOLD, 'DRAFT_HARD_HOLD')
        self.assertEqual(gate.INVALID, 'INVALID_HARD_HOLD')

    def test_original_PR_heads_pinned(self):
        self.assertEqual(set(gate.DRAFT_PR_HEADS), {157, 169, 973})
        self.assertEqual(gate.DRAFT_PR_HEADS[973], '4d40996a559b0124d74a9bb3bdcd481ad1992aa8')

    def test_missing_repo_returns_hold_nonzero(self):
        with tempfile.TemporaryDirectory() as td:
            ret = subprocess.run([sys.executable, str(MODULE_PATH), '--repo', td],
                                 text=True, capture_output=True, check=False)
            self.assertEqual(ret.returncode, 2)
            self.assertIn('INVALID_HARD_HOLD', ret.stdout)
            self.assertNotIn('QD PASS', ret.stdout)

    def test_reject_missing_values(self):
        f = valid_fixture(); del f['plan']
        with self.assertRaisesRegex(ValueError, 'five source items'):
            gate.check_sources(f, digest_fixture(f))

    def test_reject_sha_mismatch_even_with_semantics_intact(self):
        f = valid_fixture(); expected = digest_fixture(f); f['plan'] += 'a'
        with self.assertRaisesRegex(ValueError, 'blob SHA drift'):
            gate.check_sources(f, expected)

    def test_reject_invalid_python_syntax(self):
        f = valid_fixture(); f['tests'] = 'invalid python syntax!!!'
        with self.assertRaises(SyntaxError):
            gate.check_sources(f, digest_fixture(f))

    def test_no_original_article_edits_offered(self):
        self.assertTrue(all(x.startswith('preparedness/') for x in gate.FILES.values()))
        self.assertEqual(set(gate.PINNED_BLOBS), set(gate.FILES))


MUTATIONS = []
# Article-context attacks and negative safety phrasing changes.
for before, after in [
    ('simulated-outage evening', 'blackout drill'),
    ('Switch off nonessential lights', 'Switch off the main power'),
    ('Leave on everything that keeps people safe', 'Save electricity everywhere'),
    ('smoke and carbon monoxide alarms', 'night lights'),
    ('medical or safety-critical equipment', 'optional electronic devices'),
    ('Do not switch off the main breaker', 'Switch off the main breaker'),
    ('Do not switch off the main breaker', 'Switch off the main breaker for an evening'),
    ('Do not switch off the main breaker', 'Disconnect the breaker'),
    ('simulated-outage evening', 'lights-out activity'),
    ('Switch off nonessential lights', 'Unplug all refrigerators'),
]:
    MUTATIONS.append(('plan', before, after))
for before, after in [
    ('Do not stop, throw away or ration', 'Stop, throw away or ration'),
    ('prescriber or pharmacist', 'neighbor or friend'),
    ('each of your medicines', 'all items'),
    ('refrigeration', 'rotation'),
    ('replacement', 'alternatives'),
    ('If you are already in an outage', 'When things are normal'),
    ('interim-use and replacement plan', 'general advice'),
    ('refrigerated medicine', 'bottled water'),
    ('pharmacist', 'travel agent'),
    ('{{cite:start-cdc-pyh-prescriptions}}', ''),
]:
    MUTATIONS.append(('kit', before, after))
for new in ['regulator', 'commercial', 'government', 'hospital', 'blog', 'unknown', '', 'ngo', 'unverified', 'consultant']:
    MUTATIONS.append(('source-kind', 'nonprofit', new))
for new in ['Private Company', 'America Cross', '', 'Red Cross LLC', 'Fictional Agency']:
    MUTATIONS.append(('source-publisher', 'American Red Cross', new))
for new in ['none', 'unsafe', 'candidate', 'not-required', 'not-tested', '0', 'deprecated']:
    MUTATIONS.append(('taxonomy', 'gate', new))
for new in ['def test_unverified_source_cannot_be_cited',
            'def test_every_modern_slate_item_is_gated',
            'def test_red_cross_cannot_be_called_a_regulator',
            'TemporaryDirectory', 'copytree', 'root=sandbox', 'duplicate source id',
            'test-fixture-unverified-source', 'not a regulator']:
    MUTATIONS.append(('tests', new, 'removed-safety-guard'))


def run_mutation(case):
    field, original, replacement = case
    f = valid_fixture()
    if field in ('plan', 'kit', 'tests'):
        assert original in f[field], case
        f[field] = f[field].replace(original, replacement)
    elif field in ('source-kind', 'source-publisher'):
        data = copy.deepcopy(SOURCES)
        target = 'kind' if field == 'source-kind' else 'publisher'
        data['sources'][0][target] = replacement
        f['sources'] = json.dumps(data)
    elif field == 'taxonomy':
        data = copy.deepcopy(TAX)
        data['slate'][0]['gate'] = False
        f['taxonomy'] = json.dumps(data)
    with unittest.TestCase().assertRaises((ValueError, SyntaxError)):
        gate.check_sources(f, digest_fixture(f))


class MutationTests(unittest.TestCase):
    pass

# Each independent mutation is its own reported unittest, not a hidden subtest.
for idx, case in enumerate(MUTATIONS):
    def run(self, mutation=case):
        run_mutation(mutation)
    setattr(MutationTests, f'test_mutation_{idx+1:02d}_{case[0].replace("-", "_")}', run)


class ExtraTests(unittest.TestCase):
    def test_does_not_accept_36_item_slate(self):
        f = valid_fixture(); t = copy.deepcopy(TAX); t['slate'].append({'slug': 'extra'})
        f['taxonomy'] = json.dumps(t)
        with self.assertRaisesRegex(ValueError, '35-article'):
            gate.check_sources(f, digest_fixture(f))

    def test_does_not_accept_duplicate_slug(self):
        f = valid_fixture(); t = copy.deepcopy(TAX); t['slate'][1]['slug'] = t['slate'][0]['slug']
        f['taxonomy'] = json.dumps(t)
        with self.assertRaisesRegex(ValueError, 'duplicate slate slugs'):
            gate.check_sources(f, digest_fixture(f))

    def test_missing_family_gate(self):
        f = valid_fixture(); t = copy.deepcopy(TAX); t['slate'][1]['gate'] = False
        f['taxonomy'] = json.dumps(t)
        with self.assertRaisesRegex(ValueError, 'ungated modern'):
            gate.check_sources(f, digest_fixture(f))

    def test_reject_buyer_link(self):
        f = valid_fixture(); f['kit'] += '<a href="https://payhip.com/b/example">BUY</a>'
        with self.assertRaisesRegex(ValueError, 'merchant redirect'):
            gate.check_sources(f, digest_fixture(f))

    def test_reject_shared_root_write(self):
        f = valid_fixture(); f['tests'] += '\nROOT.write_text("corruption")\n'
        with self.assertRaisesRegex(ValueError, 'shared ROOT'):
            gate.check_sources(f, digest_fixture(f))

    def test_unsafe_bibliography_cannot_fake_local_warning(self):
        f = valid_fixture()
        f['plan'] = f['plan'].replace('Do not switch off the main breaker as a drill.', '')
        f['plan'] += '<footer>Do not switch off the main breaker as a drill.</footer>'
        with self.assertRaisesRegex(ValueError, 'household rehearsal safety phrase'):
            gate.check_sources(f, digest_fixture(f))

    def test_tamper_citation_claim_without_edits(self):
        f = valid_fixture(); f['kit'] = f['kit'].replace('{{cite:start-cdc-pyh-prescriptions}}', '{{cite:wrong-source}}')
        with self.assertRaisesRegex(ValueError, 'provenance'):
            gate.check_sources(f, digest_fixture(f))

    def test_unsafe_script_no_approval_toggling(self):
        result = gate.check_sources(valid_fixture(), digest_fixture(valid_fixture()))
        self.assertNotIn('publication_authorized', result)
        self.assertFalse(result['safety_adjudicated'])

if __name__ == '__main__':
    unittest.main()
