"""R416 deterministic synthetic claim-block fidelity tests. NO clinical/safety PASS."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'tests')]
from test_r414_citation_locality_escrow_gate import fixture, ANCHOR, BEFORE
import r415_global_citation_alignment_gate as old
import r416_cited_claim_block_gate as gate


def modify(fn):
    d,m,e,c=fixture()
    s=fn(e['guide-0'][0])
    e['guide-0']=(s,s)
    return d,m,e,c


class BasicBehavior(unittest.TestCase):
    def test_complete_synthetic_35_slate_structural_only(self):
        d,m,e,c=fixture();r=gate.check(d,m,e,c,test_only=True)
        self.assertTrue(r['integrity_ok'],r['errors']);self.assertEqual(r['draft_checks'],70)
        self.assertEqual(r['release_state'],'DRAFT_HARD_HOLD')
        for key in ('eligible','publication_approved','qualified_safety_approved'):self.assertFalse(r[key])
    def test_source_warnings_do_not_disclose_private_text(self):
        d,m,e,c=fixture();s=json.dumps(gate.check(d,m,e,c,test_only=True))
        self.assertNotIn('A museum ledger records',s);self.assertNotIn('synthetic placeholder',s)
    def test_does_not_mutate_inputs(self):
        d,m,e,c=fixture();before=copy.deepcopy((d,m,e,c))
        gate.check(d,m,e,c,test_only=True);self.assertEqual((d,m,e,c),before)
    def test_cli_missing_escrow_exits_two(self):
        p=subprocess.run([sys.executable,'-I',str(ROOT/'tools'/'r416_cited_claim_block_gate.py'),
             '/no/original','/no/manifest','/no/exports','/no/candidates'],capture_output=True,text=True)
        self.assertEqual(p.returncode,2)
        self.assertFalse(json.loads(p.stdout)['eligible'])
    def test_missing_authentic_original_fails(self):
        d,m,e,c=fixture();r=gate.check(d,m,e,c)
        self.assertFalse(r['integrity_ok']);self.assertFalse(r['publication_approved'])
    def test_no_citation_release_claim(self):
        d,m,e,c=fixture();r=gate.check(d,m,e,c,test_only=True)
        self.assertTrue(any('does not establish' in w for w in r['warnings']))
    def test_noncritical_standalone_appendix_allowed(self):
        d,m,e,c=modify(lambda s:s.replace('</article>','<p>Unrelated museum index entries.</p></article>'))
        r=gate.check(d,m,e,c,test_only=True);self.assertTrue(r['integrity_ok'],r['errors'])
    def test_noncritical_appendix_html_whitespace_allowed(self):
        d,m,e,c=modify(lambda s:s.replace('</article>','\n<p>An additional archived record.</p>\n</article>'))
        r=gate.check(d,m,e,c,test_only=True);self.assertTrue(r['integrity_ok'],r['errors'])
    def test_new_risk_statement_quarantined_even_if_uncited(self):
        d,m,e,c=modify(lambda s:s.replace('</article>',
            '<p>Medical guidance must follow a named qualified reviewer.</p></article>'))
        r=gate.check(d,m,e,c,test_only=True)
        self.assertFalse(r['integrity_ok'])
        self.assertTrue(any('new unreviewed high-consequence' in x for x in r['errors']))
    def test_missing_one_original_pin_fails(self):
        d,m,e,c=fixture();c.pop(next(iter(c)))
        self.assertFalse(gate.check(d,m,e,c,test_only=True)['integrity_ok'])
    def test_one_sided_wordpress_change_blocks(self):
        d,m,e,c=fixture();e['guide-0']=(e['guide-0'][0].replace('sequence of objects','sequence of revised objects',1),e['guide-0'][1])
        self.assertFalse(gate.check(d,m,e,c,test_only=True)['integrity_ok'])
    def test_changed_source_link_order_blocks(self):
        d,m,e,c=modify(lambda s:s.replace(ANCHOR,'')+ANCHOR)
        self.assertFalse(gate.check(d,m,e,c,test_only=True)['integrity_ok'])
    def test_paragraph_parser_handles_emphasis(self):
        p=gate.extract('<article><p>Alpha <em>beta</em> gamma <a data-source-id="x">Source name</a>.</p></article>')
        self.assertEqual(gate.signatures(p)[0][1],('alpha','beta','gamma','source','name'))
    def test_markdown_source_cite_blocks(self):
        p=gate.extract(b'# Header\n\nOne two three {{cite:src-a}} four five\n\nAnother paragraph',candidate=True)
        self.assertEqual(gate.signatures(p),[('src-a',('one','two','three','four','five'))])
    def test_bare_source_anchor_attach_to_previous_paragraph(self):
        p=gate.extract('<article><p>Evidence paragraph follows source scope.</p><a data-source-id="x">Official source</a></article>')
        self.assertEqual(gate.signatures(p),[('x',('evidence','paragraph','follows','source','scope'))])
    def test_duplicate_source_occurrences_preserved(self):
        p=gate.extract('<article><p>First <a data-source-id="x">Source A</a></p><p>Second <a data-source-id="x">Source B</a></p></article>')
        self.assertEqual(len(gate.signatures(p)),2)
        self.assertNotEqual(gate.signatures(p)[0][1],gate.signatures(p)[1][1])
    def test_source_anchor_orphan_rejected(self):
        with self.assertRaises(ValueError):gate.signatures(gate.extract('<article><a data-source-id="x">No block</a></article>'))
    def test_unclosed_block_rejected(self):
        with self.assertRaises(ValueError):gate.extract('<article><p>Unclosed text')
    def test_oversized_document_rejected(self):
        with self.assertRaises(ValueError):gate.extract('<p>'+'word '*12001+'</p>')
    def test_invalid_utf8_rejected(self):
        with self.assertRaises(UnicodeError):gate.extract(b'\xff')
    def test_report_counts_not_content(self):
        d,m,e,c=fixture();r=gate.check(d,m,e,c,test_only=True)
        self.assertEqual(set(r['details'][0]) & {'content','manuscript','html','text'},set())


class DemonstratedPriorGap(unittest.TestCase):
    def test_new_gate_rejects_distant_claim_expansion_r415_accepts(self):
        d,m,e,c=modify(lambda s:s.replace('sequence of objects','sequence of medically safe objects',1))
        old_r=old.check(d,m,e,c,test_only=True)
        new_r=gate.check(d,m,e,c,test_only=True)
        self.assertTrue(old_r['integrity_ok'],old_r['errors'])
        self.assertFalse(new_r['integrity_ok'])
        self.assertTrue(any('cited evidence block modified' in x for x in new_r['errors']))
    def test_reference_url_and_sha_unchanged_during_attack(self):
        d,m,e,c=modify(lambda s:s.replace('sequence of objects','sequence of medically safe objects',1))
        self.assertEqual(len(c),35)
        self.assertIn(ANCHOR,e['guide-0'][0])
        self.assertEqual(e['guide-0'][0],e['guide-0'][1])


class CitedBlockMutations(unittest.TestCase):pass


def make_mutation(index,addition):
    def t(self):
        d,m,e,c=modify(lambda s:s.replace('sequence of objects','sequence of '+addition+' objects',1))
        r=gate.check(d,m,e,c,test_only=True)
        self.assertFalse(r['integrity_ok'],addition)
        self.assertFalse(r['eligible']);self.assertFalse(r['publication_approved'])
        self.assertTrue(any('R416 original cited evidence block modified' in x for x in r['errors']))
    t.__name__='test_distant_nonwarning_claim_mutation_'+str(index).zfill(2)
    return t

ADDITIONS=[
'verified','unverified','scientifically','medically','safe','unsafe','approved',
'unapproved','proven','unproven','always','never','untested','definitively',
'possibly','falsely','carefully','not','potentially','allegedly','withheld',
'incomplete','disputed','unconfirmed','correct','incorrect','temporary','permanent',
'current','historical','new','old','implied','explicitly','independently','privately',
'publicly','conditionally','universally','locally','federally','unfounded','unrelated',
'inferred','speculative','limited','absolute','reported','presumed','risky','secure'
]
for i,v in enumerate(ADDITIONS):
    setattr(CitedBlockMutations,'test_distant_nonwarning_claim_mutation_'+str(i).zfill(2),make_mutation(i,v))

class NewRiskReview(unittest.TestCase):pass
RISK_EXAMPLES=[
'Medical staff should review the updated paragraph.',
'Water treatment must be handled by qualified operators.',
'Generator safety requires independently vetted source documentation.',
'Boiling instructions should be reviewed by an external expert.',
'Emergency actions must follow the local authority instructions.',
'An approved medication plan is required to proceed.',
'Canning safety must be reviewed by the cited institution.',
'Pressure treatment should use a documented testing protocol.',
'Freezing instructions must be linked to an appropriate study.',
'Carbon monoxide protection requires specialist review.',
]

def make_risk(idx,para):
    def t(self):
        d,m,e,c=modify(lambda s:s.replace('</article>','<p>'+para+'</p></article>'))
        r=gate.check(d,m,e,c,test_only=True)
        self.assertFalse(r['integrity_ok']);self.assertTrue(any('R416 new unreviewed high-consequence' in x for x in r['errors']),r['errors'])
    return t
for i,v in enumerate(RISK_EXAMPLES):
    setattr(NewRiskReview,'test_unreviewed_added_claim_'+str(i).zfill(2),make_risk(i,v))

if __name__=='__main__': unittest.main()
