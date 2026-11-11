"""R301 synthetic regression fixtures: never exercise real CMS or public sources."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1]/'tools/r301_body_custody_reader_fidelity_hold.py'
spec=importlib.util.spec_from_file_location('r301',SOURCE)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)


def doc(text='Plan includes everyone.',ids=('one','two','one')):
 src=f'<section><h2>Overview</h2><p>{text}'
 out=f'<div class="pa pa-article"><div class="pa-body" id="pa-main"><section><h2>Overview</h2><p>{text}'
 seen={}
 for sid in ids:
  if sid not in seen:seen[sid]=len(seen)+1
  n=seen[sid]
  src+=f'{{{{cite:{sid}}}}}'
  out+=f'<sup class="pa-cite"><a href="#src-{n}" aria-label="Source {n}">[{n}]</a></sup>'
 return src+'</p></section>',out+'</p></section></div></div>'


class ReaderParityTests(unittest.TestCase):
 def test_exact_reader_parity(self):
  a,b=doc();self.assertEqual(mod.reader_parity(a,b),[])
 def test_source_entities(self):
  a,b=doc('A &amp; B <em>together</em>');self.assertEqual(mod.reader_parity(a,b),[])
 def test_link_tokens_are_labels(self):
  a,b=doc('{{link:another-article|go here}}')
  b=b.replace('{{link:another-article|go here}}','<a href="/preparedness/x/another-article/">go here</a>')
  self.assertEqual(mod.reader_parity(a,b),[])
 def test_inline_script_not_reading_text(self):
  a,b=doc('{{inline-js:plan_builder.js}}')
  b=b.replace('{{inline-js:plan_builder.js}}','<script>window.x="nonreader"</script>')
  self.assertEqual(mod.reader_parity(a,b),[])
 def test_source_script_not_reader(self):
  a,b=doc('Ready <script>window.x=123</script> now')
  self.assertEqual(mod.reader_parity(a,b),[])
 def test_added_extra_export_text_rejected(self):
  a,b=doc();b=b.replace('everyone.','everyone. Buy the miracle pack.');self.assertIn('READER_BODY_TEXT_NOT_PRESERVED',mod.reader_parity(a,b))
 def test_citation_drop_rejected(self):
  a,b=doc();b=b.replace('<sup class="pa-cite"><a href="#src-1" aria-label="Source 1">[1]</a></sup>','',1)
  self.assertIn('BODY_CITATION_OCCURRENCE_ORDER_DRIFT',mod.reader_parity(a,b))
 def test_citation_reordered_rejected(self):
  a,b=doc();b=b.replace('href="#src-2"','href="#src-9"').replace('> [2]','> [9]')
  self.assertIn('BODY_CITATION_OCCURRENCE_ORDER_DRIFT',mod.reader_parity(a,b))
 def test_missing_main_rejected(self):
  a,b=doc();b=b.replace('id="pa-main"','id="missing"')
  self.assertIn('MISSING_OR_UNCLOSED_MAIN_BODY',mod.reader_parity(a,b))
 def test_duplicate_main_rejected(self):
  a,b=doc();b+='<div class="pa-body" id="pa-main">copy</div>'
  self.assertIn('MULTIPLE_OR_NESTED_MAIN_BODIES',mod.reader_parity(a,b))
 def test_unclosed_main_rejected(self):
  a,b=doc();b=b.removesuffix('</div></div>')
  self.assertIn('MISSING_OR_UNCLOSED_MAIN_BODY',mod.reader_parity(a,b))
 def test_malformed_citation_label_rejected(self):
  a,b=doc();b=b.replace('>[1]</a>','>[3]</a>',1)
  self.assertIn('CITATION_MARKER_NOT_VERIFIED',mod.reader_parity(a,b))
 def test_citation_href_missing_rejected(self):
  a,b=doc();b=b.replace('href="#src-1"','href="/external"',1)
  self.assertIn('INVALID_CITATION_ANCHOR',mod.reader_parity(a,b))
 def test_duplicate_anchor_in_citation_rejected(self):
  a,b=doc();b=b.replace('>[1]</a>','>[1]</a><a href="#src-2">[2]</a>',1)
  self.assertIn('INVALID_CITATION_ANCHOR',mod.reader_parity(a,b))
 def test_all_citations_removed_rejected(self):
  a,b=doc();b=mod_reader_repl(b)
  self.assertIn('BODY_CITATION_OCCURRENCE_ORDER_DRIFT',mod.reader_parity(a,b))


def mod_reader_repl(s):
 import re
 return re.sub(r'<sup class="pa-cite">.*?</sup>','',s)


class AuditTests(unittest.TestCase):
 def setUp(self):
  self.temp=TemporaryDirectory();self.root=Path(self.temp.name)
  self.rows=[];self.fake_pins={};self.raw_blob=mod.blob
  slugs=list(mod.OVERRIDES)+[f'other-{j:02}' for j in range(21)]
  self.assertEqual(len(slugs),35)
  article_dir=self.root/'preparedness/content/articles';article_dir.mkdir(parents=True)
  output=self.root/'preparedness/build/wp';output.mkdir(parents=True)
  for i,slug in enumerate(slugs):
   source,rendered=doc('Plain emergency planning text '+slug+'.',('verified-one',))
   source_bytes=source.encode();f=article_dir/(slug+'.body.html');f.write_bytes(source_bytes)
   (output/(slug+'.html')).write_text(rendered,encoding='utf-8')
   old=('0'*40 if slug in mod.OVERRIDES else self.raw_blob(source_bytes))
   self.rows.append({'slug':slug,'body_oid':old})
   if slug in mod.OVERRIDES:self.fake_pins[source_bytes]=mod.OVERRIDES[slug]
  self.custody={'articles':self.rows}
  self.prev={'state':'DRAFT_HARD_HOLD','errors':[],'article_metadata_pinned':35,
             'publication_authorized':False,'independent_qd_pass':False,
             'all_41_exports_independently_approved':False}
 def tearDown(self):self.temp.cleanup()
 def call(self,custody=None,previous='default'):
  def shim(b):return self.fake_pins.get(b,self.raw_blob(b))
  with patch.object(mod,'blob',side_effect=shim):
   return mod.audit(self.root,custody or self.custody,self.prev if previous=='default' else previous)
 def test_synthetic_clean_stays_hard_hold(self):
  r=self.call();self.assertEqual(r['errors'],[]);self.assertEqual(r['state'],'DRAFT_HARD_HOLD')
  self.assertEqual(r['body_pins_matched'],35);self.assertEqual(r['article_reader_parity_matched'],35)
  self.assertFalse(r['publication_authorized']);self.assertFalse(r['independent_qd_pass'])
  self.assertEqual(len(r['body_lineage_disputes']),14)
 def test_modified_body_rejected(self):
  p=self.root/'preparedness/content/articles/other-00.body.html';p.write_text('<p>changed</p>')
  self.assertIn('BODY_BYTES_CHANGED:other-00',self.call()['errors'])
 def test_unexpected_new_body_rejected(self):
  (self.root/'preparedness/content/articles/bonus.body.html').write_text('x')
  self.assertIn('ARTICLE_BODY_INVENTORY_CHANGED',self.call()['errors'])
 def test_missing_body_rejected(self):
  (self.root/'preparedness/content/articles/other-00.body.html').unlink()
  self.assertIn('BODY_MISSING_OR_SYMLINK:other-00',self.call()['errors'])
 def test_symlink_rejected(self):
  p=self.root/'preparedness/content/articles/other-00.body.html';p.unlink();p.symlink_to(self.root/'preparedness/content/articles/other-01.body.html')
  self.assertIn('BODY_MISSING_OR_SYMLINK:other-00',self.call()['errors'])
 def test_draft_missing_rejected(self):
  (self.root/'preparedness/build/wp/other-00.html').unlink()
  self.assertIn('DRAFT_MISSING_OR_SYMLINK:other-00',self.call()['errors'])
 def test_draft_semantic_deletion_rejected(self):
  p=self.root/'preparedness/build/wp/other-00.html';p.write_text(p.read_text().replace('planning',''))
  self.assertIn('READER_BODY_TEXT_NOT_PRESERVED:other-00',self.call()['errors'])
 def test_previous_qd_positive_rejected(self):
  p=dict(self.prev,independent_qd_pass=True)
  self.assertIn('R300_UPSTREAM_CUSTODY_NOT_VERIFIED',self.call(previous=p)['errors'])
 def test_previous_count_wrong_rejected(self):
  p=dict(self.prev,article_metadata_pinned=34)
  self.assertIn('R300_UPSTREAM_CUSTODY_NOT_VERIFIED',self.call(previous=p)['errors'])
 def test_previous_release_claim_rejected(self):
  p=dict(self.prev,publication_authorized=True)
  self.assertIn('R300_UPSTREAM_CUSTODY_NOT_VERIFIED',self.call(previous=p)['errors'])
 def test_missing_frozen_row_rejected(self):
  self.assertIn('R200_BODY_SLATE_INVALID',self.call(custody={'articles':self.rows[:-1]})['errors'])
 def test_duplicate_frozen_slug_rejected(self):
  rows=[*self.rows[:-1],self.rows[0]]
  self.assertIn('R200_BODY_SLUG_INVALID',self.call(custody={'articles':rows})['errors'])
 def test_symlink_output_rejected(self):
  p=self.root/'preparedness/build/wp/other-00.html';p.unlink();p.symlink_to(self.root/'preparedness/build/wp/other-01.html')
  self.assertIn('DRAFT_MISSING_OR_SYMLINK:other-00',self.call()['errors'])
 def test_original_r200_receipts_never_approved(self):
  r=self.call();self.assertFalse(r['body_lineage_human_adjudicated']);self.assertFalse(r['medical_safety_verified'])
  self.assertIsNone(r['verified_paid_orders']);self.assertIsNone(r['net_revenue_per_1000_qualified_sessions'])


def register_case(test_cls,name,fn):setattr(test_cls,name,fn)
for i in range(35):
 def text_mutation(self,i=i):
  original,export=doc('Plan section number '+str(i)+': retain all details.')
  export=export.replace('retain all details','omit details')
  self.assertIn('READER_BODY_TEXT_NOT_PRESERVED',mod.reader_parity(original,export))
 register_case(ReaderParityTests,'test_reject_dropped_phrase_%02d'%i,text_mutation)
for i in range(35):
 def body_mutation(self,i=i):
  slug=list(mod.OVERRIDES)[i] if i<14 else f'other-{i-14:02}'
  p=self.root/f'preparedness/content/articles/{slug}.body.html';p.write_bytes(p.read_bytes()+b'\n<p>Injected.</p>')
  self.assertIn('BODY_BYTES_CHANGED:'+slug,self.call()['errors'])
 register_case(AuditTests,'test_reject_body_change_%02d'%i,body_mutation)

if __name__=='__main__':unittest.main()
