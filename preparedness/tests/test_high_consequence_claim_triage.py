"""R13 synthetic source/action triage: never mistake a citation for approval."""
from __future__ import annotations
import copy
import csv
from io import StringIO
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parent))
import high_consequence_claim_triage as gate

META = {'slug':'water-safety', 'status':{'publish':'draft'},
        'source_use':{'cdc-water':'Directly relevant to described action', 'epa-water':'Relevant limit'}}
BODY = ('<section><h2>What to do now</h2><ol>'
        '<li><strong>Boil water for one minute.</strong> {{cite:cdc-water}}</li>'
        '<li>Do not use fuel-contaminated water for drinking.</li>'
        '<li>Read stories about an old ship at sea.</li>'
        '</ol><p>Medical device batteries should be checked. {{cite:epa-water}}</p></section>')


def scan(body=BODY, meta=None, n=2):
    return gate.triage_article('water-safety', copy.deepcopy(META if meta is None else meta), body,
                               expected_citations=n)


class TriageTests(unittest.TestCase):
    def test_original_claim_order(self):
        result=scan()
        self.assertEqual(result['visible_block_citation_occurrences'], 2)
        self.assertEqual(result['triaged'], 3)
        self.assertEqual(result['without_same_block_citation'], 1)
        self.assertEqual([x['citation_proximity'] for x in result['flags']],
                         ['SAME_VISIBLE_BLOCK','NO_SAME_BLOCK_CITATION','SAME_VISIBLE_BLOCK'])

    def test_citation_not_approval(self):
        for x in scan()['flags']:
            self.assertEqual(x['review_state'], gate.STATUS)
            self.assertIn('HUMAN', x['review_reason'])

    def test_uncited_note_prioritized(self):
        self.assertIn('NO_SAME_BLOCK', scan()['flags'][1]['review_reason'])

    def test_body_digest_binds_change(self):
        a=scan(); b=scan(BODY.replace('one minute','two minutes'))
        self.assertNotEqual(a['body_sha256'],b['body_sha256'])
        self.assertNotEqual(a['flags'][0]['flag_sha256'],b['flags'][0]['flag_sha256'])

    def test_determinism(self):
        self.assertEqual(scan(),scan())

    def test_tamper_changed_source_id(self):
        with self.assertRaisesRegex(gate.TriageFailure,'unannotated source'):
            scan(BODY.replace('cite:cdc-water','cite:ghost'))

    def test_non_draft_rejected(self):
        m=copy.deepcopy(META); m['status']['publish']='publish'
        with self.assertRaisesRegex(gate.TriageFailure,'not a private draft'):
            scan(meta=m)

    def test_missing_meta_rejected(self):
        with self.assertRaises(gate.TriageFailure): gate.triage_article('water-safety',{}, BODY)

    def test_blank_source_use_rejected(self):
        m=copy.deepcopy(META); m['source_use']['cdc-water']=' '
        with self.assertRaises(gate.TriageFailure): scan(meta=m)

    def test_unknown_slug_rejected(self):
        with self.assertRaises(gate.TriageFailure): gate.triage_article('../danger',META,BODY)

    def test_missing_citation_fails_inventory(self):
        with self.assertRaisesRegex(gate.TriageFailure,'citation count'):
            scan(BODY.replace('{{cite:cdc-water}}',''))

    def test_duplicated_citation_fails_inventory(self):
        with self.assertRaisesRegex(gate.TriageFailure,'citation count'):
            scan(BODY.replace('{{cite:cdc-water}}','{{cite:cdc-water}}{{cite:cdc-water}}'))

    def test_hidden_citation_cannot_satisfy_count(self):
        body='<p>Boil water.</p><script>{{cite:cdc-water}}</script>'
        with self.assertRaisesRegex(gate.TriageFailure,'citation count'):
            scan(body, n=1)

    def test_aria_hidden_citation_cannot_satisfy_count(self):
        body='<p aria-hidden="true">Boil water {{cite:cdc-water}}</p>'
        with self.assertRaisesRegex(gate.TriageFailure,'citation count'):
            scan(body, n=1)

    def test_css_hidden_citation_cannot_satisfy_count(self):
        body='<p style="color: red; display:none">Boil water {{cite:cdc-water}}</p>'
        with self.assertRaisesRegex(gate.TriageFailure,'citation count'):
            scan(body, n=1)

    def test_comment_citation_not_counted(self):
        self.assertEqual(scan('<p>Boil water.</p><!-- {{cite:cdc-water}} -->', n=0)['visible_block_citation_occurrences'],0)

    def test_head_not_reader_claim(self):
        self.assertEqual(scan('<head><title>Boil water.</title></head><p>History of boots.</p>',n=0)['triaged'],0)

    def test_heading_citations_counted_independently_of_leaf_blocks(self):
        body='<h2>Water guidance {{cite:cdc-water}}</h2><p>Boil water.</p>'
        self.assertEqual(scan(body,n=1)['visible_block_citation_occurrences'],1)

    def test_visible_citation_no_semantic_block_counted(self):
        body='<div>Boil water {{cite:cdc-water}}</div>'
        self.assertEqual(scan(body,n=1)['visible_block_citation_occurrences'],1)

    def test_attribute_citation_not_counted(self):
        self.assertEqual(scan('<p title="{{cite:cdc-water}}">Boil water.</p>', n=0)['visible_block_citation_occurrences'],0)

    def test_malformed_html_rejected(self):
        with self.assertRaises(gate.TriageFailure): scan('<p>Boil water.</li>',n=0)

    def test_incomplete_html_rejected(self):
        with self.assertRaises(gate.TriageFailure): scan('<p>Boil water.',n=0)

    def test_nul_rejected(self):
        with self.assertRaises(gate.TriageFailure): scan('<p>Boil water.\x00</p>',n=0)

    def test_large_body_rejected(self):
        with self.assertRaises(gate.TriageFailure): scan('<p>'+'x'*gate.MAX_BODY_BYTES+'</p>',n=0)

    def test_nested_leaf_blocks_do_not_duplicate_citation(self):
        body='<ol><li>In 2026 <p>Boil water {{cite:cdc-water}}.</p> Avoid fuel.</li></ol>'
        x=scan(body,n=1)
        self.assertEqual(x['visible_block_citation_occurrences'],1)
        self.assertEqual(sum(len(r['citations']) for r in gate.scan_html(body)),1)

    def test_source_order_occurrences_retained(self):
        body='<p>Boil water {{cite:cdc-water}} {{cite:epa-water}} {{cite:cdc-water}}</p>'
        self.assertEqual(scan(body,n=3)['flags'][0]['source_ids_in_same_block'], ['cdc-water','epa-water'])
        self.assertEqual(scan(body,n=3)['flags'][0]['citation_occurrences_in_same_block'],3)

    def test_emphasis_text_preserved(self):
        self.assertIn('Boil water',gate.scan_html('<p><b>Boil</b> water</p>')[0]['text'])

    def test_entities_normalized(self):
        self.assertEqual(gate.scan_html('<p>Boil&nbsp;water &amp; wait</p>')[0]['text'],'Boil water & wait')

    def test_innocent_history_not_flagged(self):
        self.assertEqual(scan('<p>Ancient voyagers carried food on ships.</p>',n=0)['triaged'],0)

    def test_hazard_without_action_not_flagged(self):
        self.assertEqual(scan('<p>Insulin is a medical topic.</p>',n=0)['triaged'],0)

    def test_action_without_hazard_not_flagged(self):
        self.assertEqual(scan('<p>Place your old book on a shelf.</p>',n=0)['triaged'],0)

    def test_malformed_cite_id_rejected_when_flagged(self):
        with self.assertRaisesRegex(gate.TriageFailure,'malformed cite'):
            scan('<p>Boil water {{CITE:cdc-water}}</p>',n=0)

    def test_cited_but_restriction_pending(self):
        flag=scan()['flags'][0]
        self.assertEqual(flag['review_state'],'PENDING_HUMAN_EVIDENCE_AND_SAFETY_REVIEW')

    def test_csv_formula_excerpts_escaped(self):
        body='<p>=SUM(1,1) -- never use a generator indoors.</p>'
        x=scan(body,n=0)
        report={'articles':[x]}
        lines=list(csv.reader(StringIO(gate.csv_export(report))))
        self.assertTrue(lines[1][-1].startswith("'="))

    def test_report_frozen_inventory(self):
        class Lib:
            articles={'water-safety':dict(META,_body=BODY)}
        with self.assertRaisesRegex(gate.TriageFailure,'inventory changed'):
            gate.build_triage(Lib())

    def test_canonical_absent_works_only_in_test_mode(self):
        class Lib:
            articles={'water-safety':dict(META,_body=BODY)}
        x=gate.build_triage(Lib(),expected_items=1)
        self.assertEqual(x['release_state'],'HOLD')
        self.assertIs(x['may_publish'],False)
        self.assertEqual(x['independent_human_source_checks_verified'],0)
        self.assertEqual(x['qualified_safety_approvals'],0)

    def test_canonical_without_evidence_rejected(self):
        class Lib:
            articles={'water-safety':dict(META,_body=BODY)}
        with self.assertRaises(gate.TriageFailure):
            gate.build_triage(Lib(),expected_items=1,expected_occurrences=2,canonical={'claims':[]})

    def test_canonical_release_claim_rejected(self):
        class Lib:
            articles={'water-safety':dict(META,_body=BODY)}
        canonical={'claims':[{'article':'water-safety'}]*2,'release_state':'PASS','may_publish':True}
        with self.assertRaisesRegex(gate.TriageFailure,'unauthorized release'):
            gate.build_triage(Lib(),expected_items=1,expected_occurrences=2,canonical=canonical)

    def test_canonical_count_mismatch_rejected(self):
        class Lib:
            articles={'water-safety':dict(META,_body=BODY)}
        canonical={'claims':[{'article':'water-safety'}]*3,'release_state':'HOLD','may_publish':False}
        with self.assertRaisesRegex(gate.TriageFailure,'citation count'):
            gate.build_triage(Lib(),expected_items=1,expected_occurrences=3,canonical=canonical)

    def test_canonical_correct(self):
        class Lib:
            articles={'water-safety':dict(META,_body=BODY)}
        canonical={'claims':[{'article':'water-safety'}]*2,'release_state':'HOLD','may_publish':False}
        x=gate.build_triage(Lib(),expected_items=1,expected_occurrences=2,canonical=canonical)
        self.assertEqual(x['draft_items'],1)
        self.assertEqual(x['articles'][0]['visible_block_citation_occurrences'],2)
        self.assertTrue(x['regex_heuristics_have_false_negatives'])

    def test_unknown_canonical_slug_rejected(self):
        class Lib:
            articles={'water-safety':dict(META,_body=BODY)}
        canonical={'claims':[{'article':'missing'}]*2,'release_state':'HOLD','may_publish':False}
        with self.assertRaises(gate.TriageFailure):
            gate.build_triage(Lib(),expected_items=1,expected_occurrences=2,canonical=canonical)

    def test_report_hash_deterministic(self):
        class Lib:
            articles={'water-safety':dict(META,_body=BODY)}
        self.assertEqual(gate.build_triage(Lib(),expected_items=1),gate.build_triage(Lib(),expected_items=1))


class HazardVocabularyTests(unittest.TestCase):
    pass


HAZARD_CASES={
    'water-treatment': ['Boil contaminated water.', 'Never add bleach to fuel-tainted water.',
                        'Check the chlorine wait time.', 'Only use filters for water if supported.',
                        'Do not treat cistern water without testing.', 'Wait 10 minutes before drinking filtered water.'],
    'food-preservation': ['Use a pressure canner properly.', 'Never eat spoiled jerky.',
                          'Check food safety after an outage.', 'Refrigerate leftovers for 2 hours.',
                          'Stop dehydrating foods without validation.', 'Do not use untreated brine.'],
    'combustion-fire': ['Never run a generator indoors.', 'Place charcoal outside.',
                        'Check your carbon monoxide detector.', 'Evacuate during a fire.',
                        'Do not use a propane grill indoors.', 'Stay out of heavy smoke.'],
    'medical-dependency': ['Call for help with insulin questions.', 'Do not ration medication.',
                           'Check your medical device battery.', 'Seek emergency help for severe injury.',
                           'Avoid a faulty oxygen cylinder.', 'Call your pharmacist about a prescription.'],
    'vulnerable-households': ['Keep infant formula sterile as directed.', 'Call your baby caregiver.',
                              'Check wheelchair battery backups.', 'Plan for mobility device access.',
                              'Help elderly neighbors evacuate.', 'Store supplies for service animals.'],
}
for family, phrases in HAZARD_CASES.items():
    for number, phrase in enumerate(phrases):
        def make_test(fam=family, line=phrase):
            def test(self):
                item=scan('<p>'+line+'</p>',n=0)
                self.assertIn(fam,item['flags'][0]['risk_families'])
                self.assertEqual(item['without_same_block_citation'],1)
            return test
        setattr(HazardVocabularyTests,'test_'+family.replace('-','_')+'_'+str(number),make_test())


class NumericInstructionTests(unittest.TestCase):
    pass


for number, phrase in enumerate([
    'Water at 100 degrees Fahrenheit is discussed.', 'Water at 10°C is discussed.',
    'Insulin should be at 5 C.', 'Food at 40 F was recorded.',
    'Generator placed 20 feet away.', 'Water stands for 30 minutes.',
    'Boil water for 1 hour.', 'Store water 4 days.',
    'Medication for 2 weeks.', 'Food stores for 3 months.',
    'Water for 20 seconds.', 'Water: 2 gallons.', 'Water: 3 liters.',
    'Water: 2 ounces.', 'Bleach: 4 drops.', 'Water: 2 teaspoons.',
    'Water: 1 tablespoon.', 'Water chlorine at 3 ppm.',
    'Insulin measurement 200 mg.', 'Water sample 50 ml.'
]):
    def make_numeric_test(line=phrase):
        def test(self):
            out=scan('<p>'+line+'</p>',n=0)
            self.assertEqual(out['triaged'],1)
            self.assertTrue(out['flags'][0]['has_numeric_instruction'] or out['flags'][0]['has_action_language'])
        return test
    setattr(NumericInstructionTests,'test_unit_'+str(number),make_numeric_test())


if __name__=='__main__': unittest.main()
