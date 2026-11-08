"""R215 isolated synthetic regression tests. No authentic checkout or safety signoff."""
import copy
import hashlib
import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('r215',Path(__file__).resolve().parents[1]/'tools'/'r215_wp_claim_transport_gate.py')
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
S7='cdc-find-clean-water';S20='start-ready-plan'
SOURCES={S7:'https://www.cdc.gov/water-emergency/',S20:'https://www.ready.gov/plan'}
PHRASE='A household identifies safe sources before emergencies and checks alerts carefully.'


def fixture():
    source={7:(f'<article><h2>Water</h2><p>{PHRASE} {{{{cite:{S7}}}}}</p>'
               f'<p>Water suspected of chemical or fuel contamination needs specific professional advice. {{{{cite:{S7}}}}}</p></article>').encode(),
            20:(f'<section><p>Family communication plans should account for language and accessibility needs. {{{{cite:{S20}}}}}</p></section>').encode()}
    claims=[]
    for n in (7,20):
        for index,sid in enumerate(g.CITE.findall(source[n].decode()),1):
            claims.append({'article':n,'citation_occurrence':index,'source_id':sid,
                           'source_url':SOURCES[sid], 'body_git_blob_sha1':g.sha(source[n]),
                           'receipt_sha256':hashlib.sha256(f'{n}-{index}-{sid}'.encode()).hexdigest(),
                           'human_source_claim_review':'REQUIRED','editorial_decision':'PENDING'})
    dossier={'schema':'fv-preparedness-r214-complete-claim-block-v1','state':g.HOLD,'claims':claims,
             'human_claim_verified':False,'medical_safety_verified':False,
             'independent_qd_pass':False,'publication_authorized':False}
    rendered={}
    for n,body in source.items():
        order=list(dict.fromkeys(g.CITE.findall(body.decode())))
        s=body.decode()
        for idx,sid in enumerate(order,1):
            s=s.replace('{{cite:'+sid+'}}',f'<sup class="pa-cite"><a href="#src-{idx}">[{idx}]</a></sup>')
        sources=''.join(f'<li id="src-{idx}"><a href="{SOURCES[sid]}">{sid}</a></li>' for idx,sid in enumerate(order,1))
        inner=(f'<div class="pa pa-article"><header><ul class="pa-chips"><li>Draft: not public</li>'
               f'<li>Safety review pending</li></ul></header><div class="pa-shell"><div class="pa-body">{s}</div></div>'
               f'<section class="pa-sources"><ol>{sources}</ol></section>'
               '<section class="pa-review">Pending. A human safety review is required before this page can be published.</section></div>')
        rendered[n]={'wp':('<!-- wp:html -->'+inner+'<!-- /wp:html -->').encode(),
                     'preview':('<!doctype html><html><body>'+inner+'</body></html>').encode()}
    return dossier,source,rendered


class TestGate(unittest.TestCase):
    def test_hold_baseline(self):
        d,b,r=fixture();o=g.evaluate(d,b,r)
        self.assertEqual(o['state'],g.HOLD,o)
        self.assertEqual([a['article'] for a in o['articles']],[7,20])
        self.assertEqual(o['articles'][0]['citation_occurrences'],2)
        self.assertEqual(o['articles'][1]['citation_occurrences'],1)
        self.assertIs(o['publication_authorized'],False)
        self.assertIs(o['independent_qd_pass'],False)
    def test_deterministic_digest(self):
        d,b,r=fixture();self.assertEqual(g.evaluate(d,b,r),g.evaluate(d,b,r))
    def test_state_injection(self):
        for key in ('human_claim_verified','medical_safety_verified','publication_authorized','independent_qd_pass'):
            d,b,r=fixture();d[key]=True
            with self.subTest(key=key):
                self.assertEqual(g.evaluate(d,b,r)['state'],g.INVALID)
    def test_missing_draft(self):
        d,b,r=fixture();del r[20]['preview']
        self.assertEqual(g.evaluate(d,b,r)['state'],g.INVALID)
    def test_duplicate_held_receipt(self):
        d,b,r=fixture();d['claims'][1]['receipt_sha256']=d['claims'][0]['receipt_sha256']
        self.assertEqual(g.evaluate(d,b,r)['state'],g.INVALID)
    def test_source_href_swap(self):
        d,b,r=fixture();r[7]['wp']=r[7]['wp'].replace(b'https://www.cdc.gov/water-emergency/',b'https://attacker.example')
        out=g.evaluate(d,b,r);self.assertEqual(out['state'],g.INVALID,out)
        self.assertIn('destination',' '.join(out['errors']))
    def test_duplicate_source_target(self):
        d,b,r=fixture();r[20]['wp']=r[20]['wp'].replace(b'</ol>',b'<li id="src-1"><a href="https://www.ready.gov/plan">Again</a></li></ol>')
        self.assertEqual(g.evaluate(d,b,r)['state'],g.INVALID)
    def test_unapproved_draft_label_removed(self):
        d,b,r=fixture();r[20]['preview']=r[20]['preview'].replace(b'Draft: not public',b'Published')
        out=g.evaluate(d,b,r);self.assertEqual(out['state'],g.INVALID)
        self.assertIn('draft/safety',' '.join(out['errors']))
    def test_unapproved_safety_label_removed(self):
        d,b,r=fixture();r[7]['wp']=r[7]['wp'].replace(b'Safety review pending',b'Safe for everyone')
        self.assertEqual(g.evaluate(d,b,r)['state'],g.INVALID)
    def test_hidden_warning_rejected_in_chips(self):
        d,b,r=fixture();r[7]['wp']=r[7]['wp'].replace(b'<li>Draft: not public</li>',b'<li hidden>Draft: not public</li>')
        out=g.evaluate(d,b,r);self.assertEqual(out['state'],g.INVALID,out)
    def test_script_only_review_warning_rejected(self):
        d,b,r=fixture();r[20]['preview']=r[20]['preview'].replace(b'A human safety review is required',b'<script>A human safety review is required</script>')
        self.assertEqual(g.evaluate(d,b,r)['state'],g.INVALID)
    def test_warning_forged_outside_scope_rejected(self):
        d,b,r=fixture();r[20]['wp']=r[20]['wp'].replace(b'Draft: not public',b'Missing draft').replace(b'<!-- wp:html -->',b'<!-- wp:html -->Draft: not public')
        self.assertEqual(g.evaluate(d,b,r)['state'],g.INVALID)
    def test_hidden_review_section_rejected(self):
        d,b,r=fixture();r[20]['wp']=r[20]['wp'].replace(b'<section class="pa-review">',b'<section class="pa-review" style="display: none">')
        self.assertEqual(g.evaluate(d,b,r)['state'],g.INVALID)
    def test_duplicate_chips_scope_rejected(self):
        d,b,r=fixture();r[7]['wp']=r[7]['wp'].replace(b'</header>',b'<ul class="pa-chips"><li>Draft: not public</li><li>Safety review pending</li></ul></header>')
        self.assertEqual(g.evaluate(d,b,r)['state'],g.INVALID)
    def test_malicious_script_in_body(self):
        d,b,r=fixture();r[7]['wp']=r[7]['wp'].replace(b'<div class="pa-body">',b'<div class="pa-body"><script>alert(1)</script>')
        self.assertEqual(g.evaluate(d,b,r)['state'],g.INVALID)
    def test_hidden_cited_text(self):
        d,b,r=fixture();r[7]['wp']=r[7]['wp'].replace(b'<p>A household',b'<p hidden>A household')
        self.assertEqual(g.evaluate(d,b,r)['state'],g.INVALID)
    def test_missing_source_section(self):
        d,b,r=fixture();r[7]['preview']=r[7]['preview'].replace(b'pa-sources',b'pa-unrecognized')
        self.assertEqual(g.evaluate(d,b,r)['state'],g.INVALID)
    def test_missing_body_section(self):
        d,b,r=fixture();r[20]['wp']=r[20]['wp'].replace(b'pa-body',b'pa-unrecognized')
        self.assertEqual(g.evaluate(d,b,r)['state'],g.INVALID)
    def test_citation_number_changed(self):
        d,b,r=fixture();r[7]['wp']=r[7]['wp'].replace(b'#src-1',b'#src-2',1)
        self.assertEqual(g.evaluate(d,b,r)['state'],g.INVALID)
    def test_nonbyte_draft(self):
        d,b,r=fixture();r[20]['wp']=r[20]['wp'].decode()
        self.assertEqual(g.evaluate(d,b,r)['state'],g.INVALID)
    def test_extra_article_forbidden(self):
        d,b,r=fixture();r[21]=r[20]
        self.assertEqual(g.evaluate(d,b,r)['state'],g.INVALID)
    def test_reject_citation_order_change_with_same_text(self):
        d,b,r=fixture();r[7]['wp']=r[7]['wp'].replace(b'<a href="#src-1">',b'<a href="#src-2">')
        self.assertEqual(g.evaluate(d,b,r)['state'],g.INVALID)


def rendered_mutation(i,channel):
    def test(self):
        d,b,r=fixture();self.assertEqual(g.evaluate(d,b,r)['state'],g.HOLD)
        a=bytearray(r[7][channel]);p=a.index(PHRASE.encode())+i
        a[p]=ord('X') if a[p]!=ord('X') else ord('Y')
        r[7][channel]=bytes(a)
        out=g.evaluate(d,b,r)
        self.assertEqual(out['state'],g.INVALID,out)
        self.assertIn('reading depth',' '.join(out['errors']))
    return test


def authored_mutation(i):
    def test(self):
        d,b,r=fixture();self.assertEqual(g.evaluate(d,b,r)['state'],g.HOLD)
        a=bytearray(b[7]);p=a.index(PHRASE.encode())+i
        a[p]=ord('X') if a[p]!=ord('X') else ord('Y')
        b[7]=bytes(a)
        out=g.evaluate(d,b,r)
        self.assertEqual(out['state'],g.INVALID,out)
        self.assertIn('original Git blob changed',' '.join(out['errors']))
    return test

for i in range(35):
    setattr(TestGate,f'test_wp_rendered_character_{i:02}',rendered_mutation(i,'wp'))
    setattr(TestGate,f'test_preview_rendered_character_{i:02}',rendered_mutation(i,'preview'))
    setattr(TestGate,f'test_authored_character_{i:02}',authored_mutation(i))
