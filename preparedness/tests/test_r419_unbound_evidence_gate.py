"""R419 disposable 35-article synthetic-only unbound visible evidence tests.

A green result proves only structural provenance on synthetic data. The actual
unpublished 35 original manuscripts, 35 paired exports and qualified QD review
are unavailable in this bundle and remain HARD HOLD.
"""
from __future__ import annotations
import copy
from pathlib import Path
import json
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'tests')]
from test_r418_uncited_claim_custody_gate import fixture as inherited_fixture
import r418_uncited_claim_custody_gate as previous
import r419_unbound_evidence_gate as gate


def inject_both(append):
    d,m,e,c=inherited_fixture()
    old=e['guide-0'][0]
    html=old.replace('</article>',append+'</article>')
    e['guide-0']=(html,html)
    return d,m,e,c


def mutate_one(append,which):
    d,m,e,c=inherited_fixture()
    old=e['guide-0'][0]
    html=old.replace('</article>',append+'</article>')
    e['guide-0']=(html,old) if which=='wordpress' else (old,html)
    return d,m,e,c


class UnboundEvidence(unittest.TestCase):
    def test_baseline_35_articles_all_channels_test_only_pass_structural_gate(self):
        d,m,e,c=inherited_fixture()
        r=gate.check(d,m,e,c,test_only=True)
        self.assertTrue(r['integrity_ok'],r['errors'])
        self.assertEqual(r['draft_checks'],70)
        self.assertEqual(len(r['details']),70)
        self.assertEqual({x['channel'] for x in r['details']},{'wordpress','private_preview'})
        self.assertFalse(r['eligible']);self.assertFalse(r['publication_approved'])
        self.assertFalse(r['qualified_safety_approved'])
        self.assertFalse(r['merchant_offer_verified'])
        self.assertEqual(r['release_state'],'DRAFT_HARD_HOLD')

    def test_reproduced_r418_unbound_safety_verdict_bypass_rejected(self):
        d,m,e,c=inject_both('<div class="prep-tip">Homemade jerky is shelf stable.</div>')
        self.assertTrue(previous.check(d,m,e,c,test_only=True)['integrity_ok'])
        r=gate.check(d,m,e,c,test_only=True)
        self.assertFalse(r['integrity_ok'],r['errors'])
        self.assertTrue(any('R419 visible prose' in s for s in r['errors']))

    def test_reproduced_r418_inline_safety_claim_bypass_rejected(self):
        d,m,e,c=inject_both('<aside><span>Water from the old cistern is</span> <em>drinkable.</em></aside>')
        self.assertTrue(previous.check(d,m,e,c,test_only=True)['integrity_ok'])
        self.assertFalse(gate.check(d,m,e,c,test_only=True)['integrity_ok'])

    def test_reproduced_r418_unbound_generator_instruction_bypass_rejected(self):
        d,m,e,c=inject_both('<section>Place the operating generator beside the sleeping area.</section>')
        self.assertTrue(previous.check(d,m,e,c,test_only=True)['integrity_ok'])
        self.assertFalse(gate.check(d,m,e,c,test_only=True)['integrity_ok'])

    def test_nonnumeric_generic_uncited_unbound_prose_also_requires_review(self):
        d,m,e,c=inject_both('<aside>The committee filed another ledger after the winter voyage.</aside>')
        self.assertTrue(previous.check(d,m,e,c,test_only=True)['integrity_ok'])
        self.assertFalse(gate.check(d,m,e,c,test_only=True)['integrity_ok'])

    def test_only_wordpress_derivative_unbound_injection_rejected(self):
        d,m,e,c=mutate_one('<div>Water from this cistern is potable.</div>','wordpress')
        self.assertFalse(gate.check(d,m,e,c,test_only=True)['integrity_ok'])

    def test_only_private_preview_derivative_unbound_injection_rejected(self):
        d,m,e,c=mutate_one('<aside>Run that generator near the doorway.</aside>','private')
        self.assertFalse(gate.check(d,m,e,c,test_only=True)['integrity_ok'])

    def test_unchanged_structural_wrapper_does_not_create_new_claim(self):
        d,m,e,c=inherited_fixture()
        wrapped=e['guide-0'][0].replace('<article>','<article><div class="article-body">').replace('</article>','</div></article>')
        e['guide-0']=(wrapped,wrapped)
        r=gate.check(d,m,e,c,test_only=True)
        self.assertTrue(r['integrity_ok'],r['errors'])

    def test_inline_markup_inside_semantic_paragraph_is_not_new_orphan(self):
        d,m,e,c=inherited_fixture()
        s=e['guide-0'][0].replace('river crossing was delayed','river <strong>crossing was</strong> delayed')
        e['guide-0']=(s,s)
        self.assertTrue(gate.check(d,m,e,c,test_only=True)['integrity_ok'])

    def test_source_markdown_is_not_misread_as_a_new_html_orphan(self):
        source='# Original\n\nA long historical archive paragraph with many references.'
        self.assertEqual(gate.unbound_groups(source,candidate=True),{})
        self.assertNotEqual(gate.unbound_groups(source,candidate=False),{})

    def test_standalone_aside_original_is_html_and_preserved(self):
        source='<aside>Original context persists.</aside>'
        self.assertFalse(gate.is_markdown_original(source))
        self.assertEqual(gate.unbound_fidelity(source,source),(1,0,0,0,0,0))

    def test_html_original_orphan_preserved(self):
        source='<article><h1>Archive</h1><aside>Original context persists.</aside><p>Body note.</p></article>'
        self.assertEqual(gate.unbound_fidelity(source,source),(1,0,0,0,0,0))

    def test_html_original_orphan_removed_flags_missing(self):
        source='<article><h1>Archive</h1><aside>Original context persists.</aside><p>Body note.</p></article>'
        dest=source.replace('<aside>Original context persists.</aside>','')
        self.assertEqual(gate.unbound_fidelity(source,dest),(1,1,0,3,0,0))

    def test_html_original_orphan_changed_flags_missing_and_added(self):
        source='<article><h1>Archive</h1><aside>Original context persists.</aside></article>'
        dest=source.replace('persists','vanishes')
        self.assertEqual(gate.unbound_fidelity(source,dest),(1,1,1,3,3,0))

    def test_duplicate_orphan_copy_flags_extra_occurrence(self):
        s='<article><aside>Archive remark.</aside></article>'
        r='<article><aside>Archive remark.</aside><aside>Archive remark.</aside></article>'
        self.assertEqual(gate.unbound_fidelity(s,r),(1,0,1,0,2,0))

    def test_same_original_orphans_different_order_currently_multiset_only(self):
        s='<article><aside>Alpha note.</aside><aside>Beta note.</aside></article>'
        r='<article><aside>Beta note.</aside><aside>Alpha note.</aside></article>'
        self.assertEqual(gate.unbound_fidelity(s,r),(2,0,0,0,0,1))
        # Original orphan source-prose order is now protected too.

    def test_compound_inline_text_inside_single_div_stays_one_group(self):
        s='<div><span>Old</span> <em>preparedness</em> <strong>claim</strong>.</div>'
        self.assertEqual(gate.unbound_groups(s),{('old','preparedness','claim'):1})

    def test_orphan_wrapped_in_p_is_not_unbound(self):
        s='<article><aside><p>Existing advice.</p></aside></article>'
        self.assertEqual(gate.unbound_groups(s),{})

    def test_outside_container_root_text_captured(self):
        self.assertEqual(gate.unbound_groups('Orphan root prose.'),{('orphan','root','prose'):1})

    def test_inert_script_text_not_counted(self):
        s='<article><script>Unsafe text.</script><p>Reader text.</p></article>'
        self.assertEqual(gate.unbound_groups(s),{})

    def test_no_exposure_of_unreviewed_manuscript_text_in_results(self):
        d,m,e,c=inject_both('<aside>Confidential hypothetical household detail.</aside>')
        r=gate.check(d,m,e,c,test_only=True)
        self.assertNotIn('Confidential hypothetical',json.dumps(r))
        self.assertNotIn('river crossing was delayed',json.dumps(r))

    def test_input_maps_untouched(self):
        d,m,e,c=inject_both('<section>New unreviewed historical information.</section>')
        original=copy.deepcopy((d,m,e,c))
        gate.check(d,m,e,c,test_only=True)
        self.assertEqual((d,m,e,c),original)

    def test_normal_mode_not_authentic_without_pinned_originals(self):
        d,m,e,c=inherited_fixture();r=gate.check(d,m,e,c)
        self.assertFalse(r['integrity_ok'])
        self.assertFalse(r['publication_approved'])

    def test_cli_missing_native_inputs_hard_holds_exit_two(self):
        p=subprocess.run([sys.executable,'-I',str(ROOT/'tools'/'r419_unbound_evidence_gate.py'),
            '/missing/r397.json','/missing/manifest.json','/missing/export','/missing/originals'],
            capture_output=True,text=True)
        self.assertEqual(p.returncode,2)
        self.assertEqual(json.loads(p.stdout)['release_state'],'DRAFT_HARD_HOLD')
        self.assertFalse(json.loads(p.stdout)['integrity_ok'])

    def test_git_blob_mutation_detected(self):
        d,m,e,c=inherited_fixture();key=next(iter(c));c[key]+=b'tampered'
        self.assertFalse(gate.check(d,m,e,c,test_only=True)['integrity_ok'])

    def test_malformed_unclosed_html_is_rejected(self):
        with self.assertRaises(ValueError):gate.unbound_groups('<article><aside>Unclosed')

    def test_repeated_original_legacy_claims_remain_unselected(self):
        d,m,e,c=inherited_fixture()
        self.assertEqual(len(d['original_articles']),35)
        self.assertEqual(len(d['original_fork_disputes']),9)
        self.assertEqual(len(d['source_evidence_disputes']),5)
        self.assertEqual(gate.check(d,m,e,c,test_only=True)['release_state'],'DRAFT_HARD_HOLD')

    def test_character_reference_decoded_before_orphan_comparison(self):
        s='<article><aside>Old text remains.</aside></article>'
        r='<article><aside>Old text remain&#115;.</aside></article>'
        self.assertEqual(gate.unbound_fidelity(s,r),(1,0,0,0,0,0))

    def test_new_synthetic_approval_field_never_enables_publish(self):
        d,m,e,c=inherited_fixture();m['qualified_safety_approved']=True
        r=gate.check(d,m,e,c,test_only=True)
        self.assertFalse(r['integrity_ok']);self.assertFalse(r['publication_approved'])

    def test_empty_unbound_words_does_not_create_new_group(self):
        self.assertEqual(gate.unbound_groups('<article><div> . ; ! </div><p>Existing.</p></article>'),{})

    def test_unsafe_empty_input_is_rejected(self):
        with self.assertRaises(ValueError):gate.unbound_groups('')

    def test_multiple_unbound_groups_counted_separately(self):
        g=gate.unbound_groups('<article><aside>First old record.</aside><div>Second old record.</div></article>')
        self.assertEqual(sum(g.values()),2)


class UnboundInjectionCorpus(unittest.TestCase):
    """42 synthetically altered BOTH-export cases invisible to old block gate."""

INJECTIONS = [
    '<aside>Old household rainwater is drinkable.</aside>',
    '<div>Generator exhaust is harmless indoors.</div>',
    '<section>Raw meat is safe after brief sunlight exposure.</section>',
    '<figure>Emergency instructions may be ignored now.</figure>',
    '<footer>That unapproved medicine is okay for infants.</footer>',
    '<header>Store fuel beside your heater.</header>',
    '<div><span>That water</span> <strong>is potable.</strong></div>',
    '<aside><em>Place charcoal near sleeping rooms.</em></aside>',
    '<section><span>Home canning</span> <em>is always reliable.</em></section>',
    '<div>This archive confirms a new historical discovery.</div>',
    '<aside>Historical records now say the practice was accepted.</aside>',
    '<div>Medical devices do not need backup power.</div>',
    '<section>Keep a generator inside the garage overnight.</section>',
    '<figure>Boiled seawater is safe for drinking.</figure>',
    '<aside>Use stored gasoline for indoor warmth.</aside>',
    '<div>Jerky prepared at room temperature is shelf stable.</div>',
    '<section>Infant formula can be made with untreated water.</section>',
    '<div>Run the generator beneath the open bedroom window.</div>',
    '<aside>Food in a warm freezer stays fresh indefinitely.</aside>',
    '<div><small>Old remedies are guaranteed to work.</small></div>',
    '<section>Salted fish can be stored anywhere.</section>',
    '<aside>Drink from an untreated rain barrel.</aside>',
    '<figure>A homemade filter removes every contaminant.</figure>',
    '<div>Fire exits may stay blocked during a drill.</div>',
    '<div>Exhaust fumes are not dangerous.</div>',
    '<aside><span>All cistern</span> water <em>is safe.</em></aside>',
    '<div>Children should meet strangers at unknown locations.</div>',
    '<section>Prepare older recipes without modern tests.</section>',
    '<aside>Every portable heater works indoors.</aside>',
    '<div>Old food safety guidance is always enough.</div>',
    '<figure>Emergency responders will reach everyone immediately.</figure>',
    '<aside>Mix cleaning chemicals for extra strength.</aside>',
    '<div>Store medications in direct sunlight.</div>',
    '<section>Use any fuel in any generator.</section>',
    '<aside>Do not read the current manufacturer guidance.</aside>',
    '<div><span>Boiling</span> is enough for <strong>every chemical.</strong></div>',
    '<div>Archives report the caravan reached the valley sooner.</div>',
    '<section>History omitted the original letter entirely.</section>',
    '<aside>Another uncited anecdote appeared in the record.</aside>',
    '<div>Local warning protocols never change.</div>',
    '<figure><span>Every household</span> can rely on <em>this method.</em></figure>',
    '<section>That archival signature was verified yesterday.</section>',
]
for idx,html in enumerate(INJECTIONS):
    def dynamic(self, addition=html):
        d,m,e,c=inject_both(addition)
        self.assertTrue(previous.check(d,m,e,c,test_only=True)['integrity_ok'],addition)
        r=gate.check(d,m,e,c,test_only=True)
        self.assertFalse(r['integrity_ok'],addition)
        self.assertEqual(r['release_state'],'DRAFT_HARD_HOLD')
        self.assertTrue(any('R419 visible prose' in x for x in r['errors']),addition)
    setattr(UnboundInjectionCorpus,'test_unbound_injection_'+str(idx).zfill(2),dynamic)

if __name__=='__main__':unittest.main()
