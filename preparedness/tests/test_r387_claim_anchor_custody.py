"""Adversarial synthetic R387 tests; not original-source human approval."""
import importlib.util
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

HERE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('r387',HERE/'tools/r387_claim_anchor_custody.py')
G=importlib.util.module_from_spec(spec);spec.loader.exec_module(G)
spec384=importlib.util.spec_from_file_location('r384',HERE/'tools/r384_variant_review_packet.py')
R=importlib.util.module_from_spec(spec384);spec384.loader.exec_module(R)

C1='<sup class="pa-cite"><a href="#src-1" aria-label="Source 1: Gov">[1]</a></sup>'
C2='<sup class="pa-cite"><a href="#src-2" aria-label="Source 2: Gov">[2]</a></sup>'
O='<p>Prepare a contact plan {{cite:alpha}} before school pickup.</p><p>Review the plan {{cite:alpha}} every year.</p><h2>Backup</h2><p>Keep copies {{cite:beta}} in the kit.</p>'
D=f'<p>Prepare a contact plan {C1} before school pickup.</p><p>Review the plan {C1} every year.</p><h2>Backup</h2><p>Keep copies {C2} in the kit.</p>'

class ClaimIntegrityTests(unittest.TestCase):
    def audit(self,orig=O,render=D):return G.compare_claim_positions(orig,render)
    def test_clean_synthetic_body(self):self.assertEqual(self.audit(),[])
    def test_original_bytes(self):self.assertEqual(self.audit(O.encode(),D),[])
    def test_no_claims_in_empty_inputs(self):self.assertEqual(self.audit('',''),[])
    def test_both_types_unsupported_rejected(self):self.assertIn('INVALID_CLAIM_INPUT',self.audit(None,D))
    def test_changed_words_detected(self):self.assertIn('CLAIM_PROSE_OR_TAG_DRIFT:1',self.audit(render=D.replace('contact plan','contact list')))
    def test_unapproved_block_delete_detected(self):self.assertIn('CLAIM_BLOCK_COUNT_DRIFT',self.audit(render=D.replace('<h2>Backup</h2>','')))
    def test_swap_claim_blocks_detected(self):
        self.assertIn('CLAIM_PROSE_OR_TAG_DRIFT:1',self.audit(render=D.replace('Prepare a contact plan','Review the contact plan')))
    def test_single_claim_relocation_same_order(self):
        s=D.replace('plan '+C1+' before','plan before '+C1)
        self.assertIn('CITATION_CLAIM_BOUNDARY_DRIFT:1',self.audit(render=s))
    def test_cross_claim_relocation_same_repeated_source(self):
        s=D.replace('plan '+C1+' before','plan before').replace('Review the plan '+C1,'Review '+C1+' the plan '+C1)
        err=self.audit(render=s)
        self.assertIn('CITATION_CLAIM_BOUNDARY_DRIFT:1',err)
        self.assertIn('CITATION_CLAIM_BOUNDARY_DRIFT:2',err)
    def test_one_source_three_occurrences_cannot_substitute(self):
        s=D.replace('Keep copies '+C2,'Keep copies '+C1)
        self.assertIn('CITATION_CLAIM_BOUNDARY_DRIFT:4',self.audit(render=s))
    def test_no_publication_flag_in_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=G.audit_original_candidates({'status':'REVIEW_PACKET_HARD_HOLD','publication_approved':False,'qualified_safety_approved':False,'articles':[], 'unselected_conflicts':[]},Path(tmp),lambda _:b'')
            self.assertFalse(out['publication_approved']);self.assertEqual(out['status'],'INVALID_HARD_HOLD')
    def test_reject_approved_packet(self):
        x=G.audit_original_candidates({'status':'REVIEW_PACKET_HARD_HOLD','publication_approved':True,'qualified_safety_approved':False},Path('/x'),lambda _:b'')
        self.assertIn('UNAUTHENTIC_PACKET',x['errors'])
    def test_missing_nine_forks(self):
        x=G.audit_original_candidates({'status':'REVIEW_PACKET_HARD_HOLD','publication_approved':False,'qualified_safety_approved':False,'articles':[], 'unselected_conflicts':[]},Path('/x'),lambda _:b'')
        self.assertIn('ORIGINAL_INVENTORY_MISMATCH',x['errors'])
    def test_native_missing_git_checkout_still_exit_2(self):
        proc=subprocess.run(['python','-I',str(HERE/'tools/r387_claim_anchor_custody.py'),'--repo','/no/such/repo'],capture_output=True,text=True)
        self.assertEqual(proc.returncode,2);self.assertIn('INVALID_HARD_HOLD',proc.stdout)
    def test_no_write_to_tested_export(self):
        orig=O.encode();sha=R.blob_sha(orig)
        with tempfile.TemporaryDirectory() as tmp:
            wp=Path(tmp)
            for i in range(35):
                slug=f'article-{i:02d}'
                (wp/f'{slug}.html').write_text(f'<div class="pa-article" data-slug="{slug}"><div class="pa-body">{D}</div></div>')
            packet={'status':'REVIEW_PACKET_HARD_HOLD','publication_approved':False,'qualified_safety_approved':False,
                    'articles':[{'slug':f'article-{i:02d}','variants':[{'branch':'claude/prep-start-bbfeb8','body_sha':sha}]} for i in range(35)],
                    'unselected_conflicts':[{'path':str(i)} for i in range(9)]}
            before={p.name:(p.stat().st_size,p.stat().st_mtime_ns) for p in wp.iterdir()}
            x=G.audit_original_candidates(packet,wp,lambda s:orig)
            after={p.name:(p.stat().st_size,p.stat().st_mtime_ns) for p in wp.iterdir()}
            self.assertEqual(before,after);self.assertEqual(x['status'],'CLAIM_POSITION_REVIEW_HARD_HOLD')
            self.assertEqual(x['counts']['checked_exports'],35)
            self.assertEqual(len(x['articles'][0]['matching_original_candidates']),1)
            self.assertFalse(x['publication_approved'])
    def test_sha_tamper_fails_closed(self):
        sha='a'*40
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);(p/'one.html').write_text('<div class="pa-article"><div class="pa-body"><p>x</p></div></div>')
            x=G.audit_original_candidates({'status':'REVIEW_PACKET_HARD_HOLD','publication_approved':False,'qualified_safety_approved':False,
                'articles':[{'slug':'one','variants':[{'branch':'x','body_sha':sha}]}],'unselected_conflicts':[{}]*9},p,lambda _:b'<p>x</p>')
            self.assertTrue(any('CANNOT_VALIDATE_ORIGINAL' in i for i in x['errors']))

# Each case is a distinct mutation with a separately reported unittest.
# Markers have a stable aggregate sequence unless the test explicitly targets
# malformed or missing footnote links. This closes a blind spot in R386.
CASES=[
('first_claim_one_word_right',D.replace('plan '+C1+' before','plan before '+C1),'CITATION_CLAIM_BOUNDARY_DRIFT:1'),
('first_claim_one_word_left',D.replace('plan '+C1,' '+C1+'plan'),'CITATION_CLAIM_BOUNDARY_DRIFT:1'),
('first_claim_before_contact',D.replace('contact plan '+C1,C1+' contact plan'),'CITATION_CLAIM_BOUNDARY_DRIFT:1'),
('first_claim_after_school',D.replace(C1+' before school', 'before school '+C1),'CITATION_CLAIM_BOUNDARY_DRIFT:1'),
('second_claim_after_every',D.replace(C1+' every year', 'every '+C1+' year'),'CITATION_CLAIM_BOUNDARY_DRIFT:2'),
('second_claim_at_end',D.replace(C1+' every year', 'every year '+C1),'CITATION_CLAIM_BOUNDARY_DRIFT:2'),
('second_claim_at_start',D.replace('Review the plan '+C1,C1+' Review the plan'),'CITATION_CLAIM_BOUNDARY_DRIFT:2'),
('second_claim_after_review',D.replace('Review the plan '+C1,'Review '+C1+' the plan'),'CITATION_CLAIM_BOUNDARY_DRIFT:2'),
('third_claim_before_keep',D.replace('Keep copies '+C2,C2+' Keep copies'),'CITATION_CLAIM_BOUNDARY_DRIFT:4'),
('third_claim_after_in',D.replace(C2+' in the kit', 'in '+C2+' the kit'),'CITATION_CLAIM_BOUNDARY_DRIFT:4'),
('third_claim_at_end',D.replace(C2+' in the kit', 'in the kit '+C2),'CITATION_CLAIM_BOUNDARY_DRIFT:4'),
('third_claim_after_the',D.replace(C2+' in the kit', 'in the '+C2+' kit'),'CITATION_CLAIM_BOUNDARY_DRIFT:4'),
('first_link_targets_two',D.replace('href="#src-1"','href="#src-2"',1),'CITATION_CLAIM_BOUNDARY_DRIFT:1'),
('third_link_targets_one',D.replace('href="#src-2"','href="#src-1"'),'CITATION_CLAIM_BOUNDARY_DRIFT:4'),
('first_link_targets_99',D.replace('href="#src-1"','href="#src-99"',1),'CITATION_CLAIM_BOUNDARY_DRIFT:1'),
('first_link_target_zero',D.replace('href="#src-1"','href="#src-0"',1),'RENDERED:MALFORMED_CLAIM_CITATION'),
('first_link_leading_zero',D.replace('href="#src-1"','href="#src-01"',1),'RENDERED:MALFORMED_CLAIM_CITATION'),
('first_link_missing_hash',D.replace('href="#src-1"','href="src-1"',1),'RENDERED:MALFORMED_CLAIM_CITATION'),
('first_link_javascript',D.replace('href="#src-1"','href="javascript:evil()"',1),'RENDERED:MALFORMED_CLAIM_CITATION'),
('first_link_empty',D.replace('href="#src-1"','href=""',1),'RENDERED:MALFORMED_CLAIM_CITATION'),
('first_link_removed',D.replace('href="#src-1"','',1),'RENDERED:MALFORMED_CLAIM_CITATION'),
('second_link_duplicates',D.replace(C1, C1+C1,1),'CITATION_CLAIM_BOUNDARY_DRIFT:1'),
('first_citation_removed',D.replace(C1,'',1),'CITATION_CLAIM_BOUNDARY_DRIFT:1'),
('third_citation_removed',D.replace(C2,''),'CITATION_CLAIM_BOUNDARY_DRIFT:4'),
('new_paragraph',D.replace('<h2>Backup</h2>','<p>New text</p><h2>Backup</h2>'),'CLAIM_BLOCK_COUNT_DRIFT'),
('changed_h2_to_h3',D.replace('<h2>Backup</h2>','<h3>Backup</h3>'),'CLAIM_PROSE_OR_TAG_DRIFT:3'),
('changed_h2_title',D.replace('<h2>Backup</h2>','<h2>Support</h2>'),'CLAIM_PROSE_OR_TAG_DRIFT:3'),
('changed_first_phrase',D.replace('before school pickup','after school pickup'),'CLAIM_PROSE_OR_TAG_DRIFT:1'),
('changed_second_phrase',D.replace('every year','every month'),'CLAIM_PROSE_OR_TAG_DRIFT:2'),
('changed_third_phrase',D.replace('in the kit','in the bag'),'CLAIM_PROSE_OR_TAG_DRIFT:4'),
('deleted_third_p',D.replace('<p>Keep copies '+C2+' in the kit.</p>',''),'CLAIM_BLOCK_COUNT_DRIFT'),
('added_heading',D+'<h3>Marketing promise</h3>','CLAIM_BLOCK_COUNT_DRIFT'),
('sup_outside_claim','<p>Prepare a contact plan before school pickup.</p>'+C1+D,'RENDERED:ORPHAN_CITATION_OUTSIDE_CLAIM'),
('removed_sup_close',D.replace('</a></sup>','</a>',1),'RENDERED:MALFORMED_CITATION_NESTING'),
('malformed_first_anchor',D.replace(C1,C1.replace('</a>',''),1),'RENDERED:MALFORMED_CITATION_NESTING'),
('no_first_sup_class',D.replace('class="pa-cite"','class="cite"',1),'CITATION_CLAIM_BOUNDARY_DRIFT:1'),
('double_href',D.replace('href="#src-1"','href="#src-1" href="#src-2"',1),'RENDERED:DUPLICATE_HTML_ATTRIBUTE'),
('first_block_no_close',D.replace('</p>','',1),'RENDERED:UNCLOSED_HTML_TAG'),
('dangling_end',D+'</span>','RENDERED:UNEXPECTED_CLOSING_TAG'),
('crossed_html',D.replace('</p>','</div></p>',1),'RENDERED:MALFORMED_CLAIM_HTML'),
('stripped_all_citations',D.replace(C1,'').replace(C2,''),'CITATION_CLAIM_BOUNDARY_DRIFT:1'),
]

def make_test(label,mutated,code):
    def test(self):self.assertIn(code,G.compare_claim_positions(O,mutated))
    test.__name__='test_adversarial_'+label
    return test
for label,value,code in CASES:setattr(ClaimIntegrityTests,'test_adversarial_'+label,make_test(label,value,code))

if __name__=='__main__':unittest.main()
