"""R432 isolated synthetic regression suite; never a QD, safety or revenue proof."""
from __future__ import annotations
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_r431_fork_content_delta_gate import materials

SCRIPT=Path(__file__).resolve().parents[1]/'tools'/'r432_passage_citation_custody_gate.py'
spec=importlib.util.spec_from_file_location('r432_passage_citation_custody_gate',SCRIPT)
g=importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


def inv(html): return g.passage_inventory(html.encode('utf-8'))


class ParagraphCustody(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.d,self.blobs=materials(self.root)

    def audited(self): return g.audit(self.d,self.root,raw_docket=json.dumps(self.d,sort_keys=True).encode(),test_only=True)

    def test_four_body_forks(self):
        x=self.audited()
        self.assertEqual(x['body_forks_covered'],4,x['errors'])
        self.assertEqual(len(x['body_review_cases']),4)
        self.assertEqual(sum(len(z['candidates']) for z in x['body_review_cases']),8)
        self.assertFalse(x['errors'])

    def test_all_evidence_still_hard_hold(self):
        x=self.audited()
        for k in ('eligible','publication_approved','qualified_safety_approved'):
            self.assertIs(x[k],False)
        self.assertIsNone(x['verified_paid_orders'])
        self.assertIsNone(x['net_revenue_per_1000_qualified_human_sessions'])
        self.assertEqual(x['native_35_article_build'],'NOT_TESTED_BY_R432')

    def test_deterministic_review_receipt(self):
        x=self.audited()['review_receipt_sha256']
        self.assertEqual(x,self.audited()['review_receipt_sha256'])
        self.assertEqual(len(x),64)

    def test_candidate_order_stability(self):
        original=self.audited()['review_receipt_sha256']
        self.d['original_fork_disputes'][0]['variants'].reverse()
        self.assertEqual(original,self.audited()['review_receipt_sha256'])

    def test_fork_order_stability(self):
        original=self.audited()['review_receipt_sha256']
        self.d['original_fork_disputes'].reverse()
        self.assertEqual(original,self.audited()['review_receipt_sha256'])

    def test_removes_one_paragraph_even_when_new_version_longer(self):
        a=inv('<p>Important original generator instruction {{cite:a}}</p><p>keep here</p>')
        b=inv('<p>New very long irrelevant commentary text repeated again again again.</p><p>keep here</p>')
        c=g.compare(a,b)
        self.assertGreater(c['visible_word_delta_b_minus_a'],0)
        self.assertEqual(c['original_words_in_lost_or_changed_passages'],4)
        self.assertEqual(c['passages_added_or_changed_count'],1)
        self.assertEqual(c['passages_lost_or_changed'][0]['risk_review_tags'],['combustion_power'])

    def test_context_reassignment_without_citation_count_change(self):
        a=inv('<p>Keep medication cool {{cite:agency}}</p>')
        b=inv('<p>Leave medication warm {{cite:agency}}</p>')
        c=g.compare(a,b)
        self.assertEqual(c['citation_context_reassignments'][0]['source_id'],'agency')
        self.assertEqual(c['citation_context_reassignments'][0]['old_context_occurrences_lost'],1)

    def test_citation_moved_between_paragraphs(self):
        a=inv('<p>Alpha {{cite:agency}}</p><p>Beta</p>')
        b=inv('<p>Alpha</p><p>Beta {{cite:agency}}</p>')
        self.assertEqual(len(g.compare(a,b)['citation_context_reassignments']),1)

    def test_citation_added_to_identical_passage_not_moved(self):
        a=inv('<p>Same claim</p>')
        b=inv('<p>Same claim {{cite:source}}</p>')
        self.assertEqual(g.compare(a,b)['original_words_in_lost_or_changed_passages'],0)
        self.assertEqual(g.compare(a,b)['citation_context_reassignments'],[])

    def test_repeated_paragraph_occurrence_count(self):
        a=inv('<p>Duplicate</p><p>Duplicate</p>')
        b=inv('<p>Duplicate</p>')
        self.assertEqual(g.compare(a,b)['passages_lost_or_changed'][0]['count'],1)

    def test_unchanged_paragraph_sequence(self):
        a=inv('<h2>Heading</h2><p>Original {{cite:source}}</p>')
        self.assertTrue(g.compare(a,a)['same_full_passage_sequence'])
        self.assertEqual(g.compare(a,a)['passages_lost_or_changed'],[])

    def test_reordered_paragraphs_not_identical_sequence(self):
        a=inv('<p>Alpha</p><p>Beta</p>')
        b=inv('<p>Beta</p><p>Alpha</p>')
        self.assertFalse(g.compare(a,b)['same_full_passage_sequence'])
        self.assertEqual(g.compare(a,b)['passages_lost_or_changed'],[])

    def test_heading_loss(self):
        a=inv('<h2>Family Contact</h2><p>Body</p>')
        b=inv('<p>Body</p>')
        self.assertEqual(g.compare(a,b)['headings_lost_or_changed_count'],1)

    def test_html_hidden_material_excluded(self):
        x=inv('<script>script is hidden</script><p>Visible</p><div hidden>hidden</div>')
        self.assertEqual(x['passage_words_estimate'],1)

    def test_inline_citation_token_stripped_from_word_hash(self):
        a=inv('<p>Some text</p>')
        b=inv('<p>Some {{cite:agency}} text</p>')
        self.assertEqual(a['passages'][0]['body_sha256'],b['passages'][0]['body_sha256'])

    def test_unanchored_standalone_text_flagged(self):
        a=inv('<div>standalone body words</div><p>Proper text</p>')
        self.assertTrue(a['unanchored_text_found'])

    def test_missing_blob_fails_parent_custody(self):
        f=self.root/(next(iter(self.blobs))+'.blob')
        f.unlink()
        out=self.audited()
        self.assertIn('R432_ORIGINAL_R431_CUSTODY_FAILED',out['errors'])
        self.assertIsNone(out['review_receipt_sha256'])

    def test_unpinned_fixture_fails(self):
        out=g.audit(self.d,self.root,raw_docket=json.dumps(self.d).encode())
        self.assertIn('R432_ORIGINAL_R431_CUSTODY_FAILED',out['errors'])

    def test_cli_missing_docket_hard_hold(self):
        p=subprocess.run([sys.executable,'-I',str(SCRIPT),str(self.root/'absent.json'),str(self.root)],capture_output=True,text=True,timeout=15)
        self.assertEqual(p.returncode,2)
        self.assertFalse(json.loads(p.stdout)['eligible'])

    def test_json_does_not_embed_unredacted_full_paragraphs(self):
        out=json.dumps(self.audited())
        self.assertNotIn('Detailed original passage',out)

    def test_dropped_citation_review_not_auto_verification(self):
        a=inv('<p>Emergency plan source {{cite:one}}</p>')
        b=inv('<p>Emergency plan source</p>')
        self.assertIs(g.compare(a,b)['requires_human_claim_and_source_review'],True)
        self.assertIs(g.held([])['qualified_safety_approved'],False)


# 42 distinct editorial-control scenarios, each checks that a citation, safety topic,
# passage identity, visibility state, or reviewer boundary does not disappear silently.
VARIANTS = [
    ('child contact revised', 'child contact wrong', 'emergency_contacts_privacy'),
    ('school pickup revised', 'school pickup wrong', 'emergency_contacts_privacy'),
    ('reunification location clarified', 'reunification location omitted', 'emergency_contacts_privacy'),
    ('privacy sensitive information', 'privacy data retained', 'emergency_contacts_privacy'),
    ('contact a family member', 'contact a neighbor', 'emergency_contacts_privacy'),
    ('insulin requires backup', 'insulin has alternative', 'medical_dependency'),
    ('oxygen device power', 'oxygen device battery', 'medical_dependency'),
    ('medical device guidance', 'medical device alternative', 'medical_dependency'),
    ('refrigerated medication advice', 'refrigerated medication new advice', 'medical_dependency'),
    ('medication dosage instructions', 'medication packaging directions', 'medical_dependency'),
    ('generator combustion risks', 'generator distance changed', 'combustion_power'),
    ('carbon monoxide alarm', 'carbon monoxide detection', 'combustion_power'),
    ('exhaust route outside', 'exhaust direction new', 'combustion_power'),
    ('gas appliance warning', 'gas appliance revised', 'combustion_power'),
    ('fumes outside room', 'fumes across room', 'combustion_power'),
    ('evacuate when directed', 'evacuate later perhaps', 'evacuation_fire'),
    ('evacuation assembly point', 'evacuation assembly alternative', 'evacuation_fire'),
    ('fire escape ladder', 'fire escape stairs', 'evacuation_fire'),
    ('smoke under door', 'smoke around window', 'evacuation_fire'),
    ('shelter in place direction', 'shelter policy alternative', 'evacuation_fire'),
    ('Family contact one', 'Family contact two', 'emergency_contacts_privacy'),
    ('Child school event one', 'Child school event two', 'emergency_contacts_privacy'),
    ('Medical device event one', 'Medical device event two', 'medical_dependency'),
    ('Medication backup one', 'Medication backup two', 'medical_dependency'),
    ('Generator safety one', 'Generator safety two', 'combustion_power'),
    ('Carbon monoxide one', 'Carbon monoxide two', 'combustion_power'),
    ('Emergency fire exit one', 'Emergency fire exit two', 'evacuation_fire'),
    ('Evacuate first one', 'Evacuate first two', 'evacuation_fire'),
    ('School contact card first', 'School contact card second', 'emergency_contacts_privacy'),
    ('Privacy records first', 'Privacy records second', 'emergency_contacts_privacy'),
    ('Insulin cooler first', 'Insulin cooler second', 'medical_dependency'),
    ('Oxygen supply first', 'Oxygen supply second', 'medical_dependency'),
    ('Gas shutoff first', 'Gas shutoff second', 'combustion_power'),
    ('Fumes vent first', 'Fumes vent second', 'combustion_power'),
    ('Shelter warning first', 'Shelter warning second', 'evacuation_fire'),
    ('Smoke warning first', 'Smoke warning second', 'evacuation_fire'),
    ('Child reunification local plan', 'Child reunification new local plan', 'emergency_contacts_privacy'),
    ('School closure notice', 'School closure procedure', 'emergency_contacts_privacy'),
    ('Medication cooling advice', 'Medication cooling changes', 'medical_dependency'),
    ('Generator ventilation note', 'Generator ventilation revision', 'combustion_power'),
    ('Emergency evacuation triggers', 'Emergency evacuation choices', 'evacuation_fire'),
    ('Contact list privacy', 'Contact list exposure', 'emergency_contacts_privacy'),
]
for i,(old,new,tag) in enumerate(VARIANTS):
    def test_case(self,o=old,n=new,t=tag):
        a=inv('<p>'+o+' {{cite:source}}</p>')
        b=inv('<p>'+n+' {{cite:source}}</p>')
        out=g.compare(a,b)
        self.assertEqual(len(out['citation_context_reassignments']),1)
        self.assertIn(t,out['passages_lost_or_changed'][0]['risk_review_tags'])
        self.assertEqual(out['visible_word_delta_b_minus_a'],len(g.WORD.findall(n))-len(g.WORD.findall(o)))
    setattr(ParagraphCustody,'test_adversarial_context_%02d'%i,test_case)

if __name__=='__main__': unittest.main()
