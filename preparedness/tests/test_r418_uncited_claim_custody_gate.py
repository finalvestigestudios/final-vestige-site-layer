"""R418 synthetic-only 35-article unreviewed source/citation custody tests."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'tests')]
from test_r417_quantitative_claim_provenance_gate import fixture as prior_fixture
import r417_quantitative_claim_provenance_gate as prior
import r418_uncited_claim_custody_gate as gate

PROSE='<p>The archival ledger records that the river crossing was delayed by flooding.</p>'


def fixture():
    docket,manifest,exports,candidates=prior_fixture()
    first=docket['original_articles'][0]
    old=first['body_candidate_git_blobs'][0]
    body=candidates.pop(('guide-0',old)).decode('utf-8')
    body=body.replace('</article>',PROSE+'</article>')
    pin=gate._r409.blob(body.encode('utf-8'))
    first['body_candidate_git_blobs']=[pin]
    candidates[('guide-0',pin)]=body.encode('utf-8')
    exports['guide-0']=(body,body)
    return docket,manifest,exports,candidates


def revise_both(transform):
    docket,manifest,exports,candidates=fixture()
    html=transform(exports['guide-0'][0])
    exports['guide-0']=(html,html)
    return docket,manifest,exports,candidates


class OriginalClaimCustody(unittest.TestCase):
    def test_synthetic_complete_35_articles_remain_held_even_when_intact(self):
        d,m,e,c=fixture();r=gate.check(d,m,e,c,test_only=True)
        self.assertTrue(r['integrity_ok'],r['errors'])
        self.assertEqual(r['draft_checks'],70)
        self.assertFalse(r['publication_approved'])
        self.assertFalse(r['qualified_safety_approved'])
        self.assertEqual(r['release_state'],'DRAFT_HARD_HOLD')
    def test_reproduced_prior_silent_uncited_fact_edit_is_now_rejected(self):
        d,m,e,c=revise_both(lambda s:s.replace('was delayed by flooding','was welcomed by officials'))
        self.assertTrue(prior.check(d,m,e,c,test_only=True)['integrity_ok'])
        r=gate.check(d,m,e,c,test_only=True)
        self.assertFalse(r['integrity_ok'],r['errors'])
        self.assertIn('original uncited prose changed',str(r['errors']))
    def test_negation_deletion_in_ordinary_prose(self):
        d,m,e,c=revise_both(lambda s:s.replace('river crossing was delayed','river crossing was not delayed'))
        self.assertTrue(prior.check(d,m,e,c,test_only=True)['integrity_ok'])
        self.assertFalse(gate.check(d,m,e,c,test_only=True)['integrity_ok'])
    def test_whole_original_uncited_paragraph_removed(self):
        d,m,e,c=revise_both(lambda s:s.replace(PROSE,''))
        self.assertFalse(gate.check(d,m,e,c,test_only=True)['integrity_ok'])
    def test_duplicate_original_prose_replay_rejected(self):
        d,m,e,c=revise_both(lambda s:s.replace('</article>',PROSE+'</article>'))
        self.assertFalse(gate.check(d,m,e,c,test_only=True)['integrity_ok'])
    def test_new_unrelated_archival_appendix_preserves_original_evidence(self):
        d,m,e,c=revise_both(lambda s:s.replace('</article>',
            '<p>Archives added further cataloging notes about paper records.</p></article>'))
        self.assertTrue(gate.check(d,m,e,c,test_only=True)['integrity_ok'])
    def test_repaired_whitespace_and_markup_preserves_text(self):
        d,m,e,c=revise_both(lambda s:s.replace('river crossing was delayed',
            'river <em>crossing was</em> delayed'))
        self.assertTrue(gate.check(d,m,e,c,test_only=True)['integrity_ok'])
    def test_wordpress_only_change_is_rejected(self):
        d,m,e,c=fixture()
        e['guide-0']=(e['guide-0'][0].replace('river crossing','river bridge'),e['guide-0'][1])
        self.assertFalse(gate.check(d,m,e,c,test_only=True)['integrity_ok'])
    def test_preview_only_change_is_rejected(self):
        d,m,e,c=fixture()
        e['guide-0']=(e['guide-0'][0],e['guide-0'][1].replace('was delayed','was avoided'))
        self.assertFalse(gate.check(d,m,e,c,test_only=True)['integrity_ok'])
    def test_implicit_safety_verdict_without_r416_or_r417_trigger_is_held(self):
        d,m,e,c=revise_both(lambda s:s.replace('</article>',
            '<p>Homemade jerky is shelf stable.</p></article>'))
        self.assertTrue(prior.check(d,m,e,c,test_only=True)['integrity_ok'])
        r=gate.check(d,m,e,c,test_only=True)
        self.assertFalse(r['integrity_ok']);self.assertIn('unreviewed safety verdict',str(r['errors']))
    def test_uncited_water_drinkability_verdict_without_number_is_held(self):
        d,m,e,c=revise_both(lambda s:s.replace('</article>',
            '<p>Water from the old cistern is drinkable.</p></article>'))
        self.assertTrue(prior.check(d,m,e,c,test_only=True)['integrity_ok'])
        self.assertFalse(gate.check(d,m,e,c,test_only=True)['integrity_ok'])
    def test_content_reporting_does_not_leak_private_original_text(self):
        d,m,e,c=fixture();r=gate.check(d,m,e,c,test_only=True)
        serialized=json.dumps(r)
        self.assertNotIn('river crossing was delayed',serialized)
        self.assertNotIn('Historical ledger',serialized)
    def test_input_maps_untouched(self):
        d,m,e,c=fixture();original=copy.deepcopy((d,m,e,c))
        gate.check(d,m,e,c,test_only=True);self.assertEqual((d,m,e,c),original)
    def test_real_mode_is_not_authentic_without_original_pinned_bytes(self):
        d,m,e,c=fixture();r=gate.check(d,m,e,c)
        self.assertFalse(r['integrity_ok'])
    def test_cli_missing_authenticated_inputs_returns_exit_two(self):
        p=subprocess.run([sys.executable,'-I',str(ROOT/'tools'/'r418_uncited_claim_custody_gate.py'),
            '/missing/original','/missing/manifest','/missing/export','/missing/manuscripts'],
            capture_output=True,text=True)
        self.assertEqual(p.returncode,2)
        self.assertEqual(json.loads(p.stdout)['release_state'],'DRAFT_HARD_HOLD')
    def test_candidate_git_blob_tamper_rejected(self):
        d,m,e,c=fixture();key=next(iter(c));c[key]+=b'corrupt'
        self.assertFalse(gate.check(d,m,e,c,test_only=True)['integrity_ok'])
    def test_held_release_flags_cannot_be_asserted(self):
        d,m,e,c=fixture();m['approved']=True
        r=gate.check(d,m,e,c,test_only=True)
        self.assertFalse(r['integrity_ok']);self.assertFalse(r['eligible'])
    def test_original_short_blocks_not_silently_dropped(self):
        a=gate._r416.extract('<article><h1>Title</h1><p>No.</p><p>Go.</p></article>',candidate=True)
        b=gate._r416.extract('<article><h1>Title</h1><p>No.</p></article>')
        self.assertEqual(gate.ordinary_fidelity(a,b),(2,1))
    def test_repeated_original_paragraphs_can_remain_unchanged(self):
        a=gate._r416.extract('<article><h1>Title</h1><p>Old archival fact.</p><p>Old archival fact.</p></article>',candidate=True)
        b=gate._r416.extract('<article><h1>Title</h1><p>Old archival fact.</p><p>Old archival fact.</p></article>')
        self.assertEqual(gate.ordinary_fidelity(a,b),(2,0))
    def test_repeated_original_paragraph_count_change_fails(self):
        a=gate._r416.extract('<article><h1>Title</h1><p>Old archival fact.</p><p>Old archival fact.</p></article>',candidate=True)
        b=gate._r416.extract('<article><h1>Title</h1><p>Old archival fact.</p></article>')
        self.assertEqual(gate.ordinary_fidelity(a,b),(2,2))
    def test_source_verdict_not_new_when_unchanged(self):
        src=gate._r416.extract('<article><p>Water was recorded as potable.</p></article>')
        self.assertEqual(gate.verdict_blocks(src),gate.verdict_blocks(src))
    def test_r418_no_source_truth_inference(self):
        d,m,e,c=fixture();r=gate.check(d,m,e,c,test_only=True)
        self.assertTrue(any('does not establish' in x for x in r['warnings']))


class ChangedSourceClaim(unittest.TestCase): pass
# These word-level changes maintain original length/citations/URLs and affect both
# private derivatives identically, so predecessor's coarse shingle check passes.
REPLACEMENTS=['recorded','accelerated','avoided','postponed','welcomed','canceled',
    'forgotten','hidden','celebrated','authorized','forbidden','misreported',
    'invented','confirmed','reversed','reconsidered','rewritten','minimized',
    'disputed','rejected','proposed','misdated','misread','approved','recalled',
    'investigated','amended','relocated','reinterpreted','restored','ignored',
    'dismissed','moved','overruled','corrected','reclassified','retold','modified',
    'eliminated','rearranged','misfiled','verified','suspended','suppressed']
for idx,replacement in enumerate(REPLACEMENTS):
    def dynamic(self,rp=replacement):
        d,m,e,c=revise_both(lambda s:s.replace('was delayed by flooding','was '+rp+' by flooding'))
        r=gate.check(d,m,e,c,test_only=True)
        self.assertFalse(r['integrity_ok'],rp)
        self.assertEqual(r['release_state'],'DRAFT_HARD_HOLD')
    setattr(ChangedSourceClaim,'test_uncited_lexical_change_'+str(idx).zfill(2),dynamic)


class NewUnreviewedVerdict(unittest.TestCase): pass
NEW_VERDICTS=['Homemade jerky is shelf stable.','Cistern water is drinkable.',
    'Stored water is potable.','That emergency generator is reliable.',
    'Old canning recipes are harmless.','Pet medical supplies are adequate.',
    'Freezer foods are nonperishable.','That medicine is suitable.',
    'An emergency shelter is sufficient.','Old bleach mixtures are effective.',
    'Household fuel is nontoxic.','Food storage here is certified.',
    'The infant plan is approved.','That old generator is riskless.',
    'The child medication is sterile.','The baby feeding plan is okay.']
for idx,verdict in enumerate(NEW_VERDICTS):
    def dynamic(self,claim=verdict):
        d,m,e,c=revise_both(lambda s:s.replace('</article>','<p>'+claim+'</p></article>'))
        r=gate.check(d,m,e,c,test_only=True)
        self.assertFalse(r['integrity_ok'],claim)
        self.assertTrue(any('R418 newly introduced unreviewed safety verdict' in x for x in r['errors']))
    setattr(NewUnreviewedVerdict,'test_added_unsupported_verdict_'+str(idx).zfill(2),dynamic)

if __name__=='__main__':
    unittest.main()
