"""R299 synthetic adversarial tests ONLY; no authenticated 41-body native run."""
from __future__ import annotations
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

P=Path(__file__).resolve().parents[1]/'tools'/'r299_native_export_source_reproduction_hold.py'
spec=importlib.util.spec_from_file_location('r299_test',P)
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)

class FakeLibrary:
 def __init__(self, metas):self.articles=metas
 def url_path(self,slug):return '/preparedness/'+self.articles[slug]['section']+'/'+slug+'/'

class FakeNativeBuilder:
 def build_article(self,lib,slug):
  import re
  meta=lib.articles[slug]
  body=meta['_body']
  seen=[]
  def cite(m):
   sid=m.group(1)
   if sid not in seen:seen.append(sid)
   n=seen.index(sid)+1
   return f'<sup class="pa-cite"><a href="#src-{n}">[{n}]</a></sup>'
  body=g.TOKEN_CITE.sub(cite,body)
  body=re.sub(r'\{\{link:([a-z0-9-]+)\|([^}]+)\}\}',lambda m:f'<a href="{lib.url_path(m.group(1))}">{m.group(2)}</a>',body)
  sources=''.join(f'<li id="src-{n}"><a href="https://example.org/{sid}">{sid}</a><span class="pa-src-use">Used for: provenance</span></li>' for n,sid in enumerate(seen,1))
  inner=(f'<div class="pa pa-article" data-slug="{slug}"><span>Independent safety/source and QD verification pending</span>'
         f'<div class="pa-body">{body}</div><section class="pa-sources">{sources}</section></div>')
  return {'slug':slug,'inner':inner,'words':len(body.split()),'minutes':5,'sources':seen,'canonical':g.SITE+lib.url_path(slug)}
 def wp_wrap(self,lib,inner):return '<!-- wp:html -->\n<style>article{}</style>\n'+inner+'\n<!-- /wp:html -->\n'

FAKE=FakeNativeBuilder()

def synthetic():
 custody={'state':'DRAFT_HARD_HOLD','artifact_count':35,'export_target_count_with_six_tools':41,
          'publication_authorized':False,'independent_qd_pass':False,'human_source_approved':False,'medical_safety_verified':False,'articles':[]}
 names=[f'guide-{i:02}' for i in range(1,36)]+sorted(g.TOOL_SLUGS)
 metas={};raw={};drafts={};rows=[]
 for i,slug in enumerate(names):
  section='field-tools' if slug in g.TOOL_SLUGS else 'start-here'
  # Eight words of a label in the link token MUST survive in exact original order.
  body=f'<h2>{slug}</h2><p>Safety context {{'+'{cite:agency-a}} matters.</p><p>Read {{link:guide-01|the complete household emergency planning guide}}.</p>'
  body+=' '.join(f'<p>Paragraph {j} has carefully retained distinct content {slug}.</p>' for j in range(18))
  body+='\n<p>Evidence note {{cite:agency-b}} with independent reading scope.</p>'
  metas[slug]={'slug':slug,'section':section,'_body':body,'status':{'publish':'draft'}}
 lib=FakeLibrary(metas)
 for i,slug in enumerate(names):
  built=FAKE.build_article(lib,slug)
  rows.append({k:built[k] for k in ('slug','canonical','sources','words','minutes')})
  drafts[f'preparedness/build/wp/{slug}.html']=FAKE.wp_wrap(lib,built['inner']).encode()
  if slug not in g.TOOL_SLUGS:
   b=metas[slug]['_body'].encode();raw[slug]=b
   custody['articles'].append({'slug':slug,'body_oid':g.oid(b),'section':'start-here',
     'route':lib.url_path(slug),'n':len(custody['articles'])+1})
 report={'articles':rows,'release_evidence':{'state':'HOLD','independent_qa_verified':False,'wordpress_publication_performed':False}}
 return custody,report,lib,drafts,raw

BASE=synthetic()

def check(mutate=None):
 custody,report,lib,drafts,raw=copy.deepcopy(BASE)
 if mutate: mutate(custody,report,lib,drafts,raw)
 return g.audit_snapshot(custody,report,lib,FAKE,drafts,raw)

class R299Tests(unittest.TestCase):
 def test_baseline(self):
  o=check();self.assertEqual(o['state'],'DRAFT_HARD_HOLD',o['errors'])
  self.assertEqual(o['native_export_byte_matches'],41)
  self.assertEqual(o['source_citation_occurrences'],82)
  self.assertEqual(o['r200_lineage_differences'],[])
 def test_never_grants_signoff(self):
  o=check()
  for key in ['lineage_human_adjudicated','all_41_exports_independently_approved','publication_authorized','independent_qd_pass','medical_safety_verified','privacy_verified','merchant_approved']:
   self.assertIs(o[key],False)
  self.assertIsNone(o['net_revenue_per_1000_qualified_sessions'])
  self.assertIsNone(o['confirmed_paid_orders'])
 def test_coherent_new_source_requires_custody_review(self):
  def drift(c,r,l,d,w):
   raw=w['guide-01']+b'<p>new unadjudicated paragraphs</p>'
   w['guide-01']=raw
   l.articles['guide-01']['_body']=raw.decode()
   b=FAKE.build_article(l,'guide-01')
   d['preparedness/build/wp/guide-01.html']=FAKE.wp_wrap(l,b['inner']).encode()
   r['articles'][0].update({k:b[k] for k in ('words','sources')})
  o=check(drift)
  self.assertEqual(o['state'],'DRAFT_HARD_HOLD')
  self.assertEqual(len(o['r200_lineage_differences']),1)
  self.assertEqual(o['r200_lineage_differences'][0]['status'],'UNADJUDICATED_LINEAGE_DRIFT')
 def test_blob_and_sha(self):
  self.assertEqual(g.oid(b'hello'),'b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0')
  self.assertEqual(len(g.sha256(b'hello')),64)
 def test_missing_pins_fail_closed(self):
  with tempfile.TemporaryDirectory() as x:
   e=g.source_pin_errors(Path(x),{'a.txt':g.oid(b'ok')})
   self.assertIn('PIN_MISSING_OR_CHANGED:a.txt',e)
 def test_changed_pins_fail_closed(self):
  with tempfile.TemporaryDirectory() as x:
   (Path(x)/'a.txt').write_bytes(b'drift')
   self.assertIn('PIN_MISSING_OR_CHANGED:a.txt',g.source_pin_errors(Path(x),{'a.txt':g.oid(b'ok')}))
 def test_identical_pins_pass(self):
  with tempfile.TemporaryDirectory() as x:
   (Path(x)/'a.txt').write_bytes(b'ok')
   self.assertEqual(g.source_pin_errors(Path(x),{'a.txt':g.oid(b'ok')}),[])
 def test_fragment_inventory_detects_extra(self):
  with tempfile.TemporaryDirectory() as x:
   p=Path(x)/'preparedness/sources/fragments';p.mkdir(parents=True)
   (p/'unexpected.json').write_text('{}')
   self.assertIn('SOURCE_FRAGMENT_INVENTORY_DRIFT',g.source_pin_errors(Path(x),{}))

# Each mutation alters one HTML, citation, source-scope, build report or approval field.
def change_html(action, slug='guide-01'):
 def f(c,r,l,d,w):
  p='preparedness/build/wp/'+slug+'.html'
  d[p]=action(d[p])
 return f

ACTIONS={
 'deleted_citation': lambda b:b.replace(b'<sup class="pa-cite"><a href="#src-1">[1]</a></sup>',b''),
 'citation_target': lambda b:b.replace(b'href="#src-1"',b'href="#src-2"'),
 'citation_wrong_number':lambda b:b.replace(b'>[1]</a>',b'>[2]</a>'),
 'citation_duplicate':lambda b:b.replace(b'<sup class="pa-cite">',b'<sup class="pa-cite"><sup class="pa-cite">',1),
 'citation_after_body':lambda b:b.replace(b'</section></div>',b'</section><sup class="pa-cite"><a href="#src-1">[1]</a></sup></div>'),
 'deleted_source_block':lambda b:b.replace(b'<section class="pa-sources">',b'<section class="pa-missing">'),
 'changed_source_url':lambda b:b.replace(b'https://example.org/agency-a',b'https://example.net/agency-a'),
 'changed_source_title':lambda b:b.replace(b'>agency-a</a>',b'>unsupported claim</a>'),
 'removed_source_scope':lambda b:b.replace(b'Used for: provenance',b''),
 'wrong_source_label':lambda b:b.replace(b'id="src-1"',b'id="src-9"'),
 'reordered_source_block':lambda b:b.replace(b'id="src-1"',b'id="src-3"'),
 'hidden_extra_citation':lambda b:b.replace(b'<div class="pa-body">',b'<div class="pa-body"><span hidden><sup class="pa-cite"><a href="#src-1">[1]</a></sup></span>'),
 'dropped_middle_paragraph':lambda b:b.replace(b'<p>Paragraph 8 has carefully retained distinct content guide-01.</p>',b''),
 'reordered_middle_paragraph':lambda b:b.replace(b'<p>Paragraph 8 has carefully retained distinct content guide-01.</p>',b'<p>Paragraph 8 has carefully retained distinct content guide-01.</p><p>Paragraph 7 has carefully retained distinct content guide-01.</p>'),
 'added_unsupported_paragraph':lambda b:b.replace(b'<div class="pa-body">',b'<div class="pa-body"><p>New unverified claim here</p>'),
 'changed_link_label':lambda b:b.replace(b'the complete household emergency planning guide',b'the watered down guide'),
 'changed_link_url':lambda b:b.replace(b'href="/preparedness/start-here/guide-01/"',b'href="/bad/"'),
 'removed_reviewer_warning':lambda b:b.replace(b'Independent safety/source and QD verification pending',b'SAFE AND APPROVED'),
 'changed_wrapper':lambda b:b.replace(b'<!-- wp:html -->',b'<!-- wp:paragraph -->'),
 'removed_tool_js':lambda b:b.replace(b'<div class="pa-body">',b'<div class="pa-body"><script>window.x=true</script>'),
 'truncated_suffix':lambda b:b.replace(b'<p>Evidence note',b'<p>'),
 'changed_css':lambda b:b.replace(b'article{}',b'article{visibility:hidden}'),
 'extra_weak_source_label':lambda b:b.replace(b'Used for: provenance',b'Human source-link check complete'),
 'added_duplicate_target':lambda b:b.replace(b'<section class="pa-sources">',b'<section class="pa-sources"><li id="src-1">NEW</li>'),
 'replaced_text_in_same_window':lambda b:b.replace(b'carefully retained distinct content',b'deliberately altered distinct content',1),
}
for name,fn in ACTIONS.items():
 def test(self,f=fn,case=name):
  o=check(change_html(f))
  self.assertEqual(o['state'],'INVALID_HARD_HOLD',(case,o['errors']))
  self.assertIn('EXPORTED_BYTES_NOT_NATIVE:guide-01',o['errors'])
  self.assertIs(o['publication_authorized'],False)
 setattr(R299Tests,'test_html_'+name,test)

MUTATIONS={
 'claim_publication': lambda c,r,l,d,w:c.update(publication_authorized=True),
 'claim_qd':lambda c,r,l,d,w:c.update(independent_qd_pass=True),
 'claim_medical':lambda c,r,l,d,w:c.update(medical_safety_verified=True),
 'custody_missing':lambda c,r,l,d,w:c['articles'].pop(),
 'custody_bad_count':lambda c,r,l,d,w:c.update(artifact_count=36),
 'custody_invalid_status':lambda c,r,l,d,w:c.update(state='RELEASE'),
 'report_missing_row':lambda c,r,l,d,w:r['articles'].pop(),
 'report_duplicate_slug':lambda c,r,l,d,w:r['articles'][-1].update(slug=r['articles'][0]['slug']),
 'report_duplicate_url':lambda c,r,l,d,w:r['articles'][-1].update(canonical=r['articles'][0]['canonical']),
 'report_wrong_url':lambda c,r,l,d,w:r['articles'][0].update(canonical='https://example.org'),
 'report_citation_removed':lambda c,r,l,d,w:r['articles'][0].update(sources=[]),
 'report_citation_reordered':lambda c,r,l,d,w:r['articles'][0].update(sources=['agency-b','agency-a']),
 'report_read_minutes_wrong':lambda c,r,l,d,w:r['articles'][0].update(minutes=999),
 'report_word_count_wrong':lambda c,r,l,d,w:r['articles'][0].update(words=0),
 'report_publication':lambda c,r,l,d,w:r['release_evidence'].update(wordpress_publication_performed=True),
 'report_QD':lambda c,r,l,d,w:r['release_evidence'].update(independent_qa_verified=True),
 'report_release_green':lambda c,r,l,d,w:r['release_evidence'].update(state='APPROVED'),
 'library_extra_article':lambda c,r,l,d,w:l.articles.update(extra=copy.deepcopy(l.articles['guide-01'])),
 'library_missing_tool':lambda c,r,l,d,w:l.articles.pop('family-reunification-card'),
 'publish_tool_status':lambda c,r,l,d,w:l.articles['kit-builder']['status'].update(publish='published'),
 'publish_article_status':lambda c,r,l,d,w:l.articles['guide-01']['status'].update(publish='published'),
 'missing_original':lambda c,r,l,d,w:w.pop('guide-01'),
 'changed_route_from_custody':lambda c,r,l,d,w:c['articles'][0].update(route='/wrong/'),
 'missing_tool_draft':lambda c,r,l,d,w:d.pop('preparedness/build/wp/kit-builder.html'),
 'changed_original_unrendered':lambda c,r,l,d,w:w.update({'guide-01':b'altered'}),
}
for name,mutation in MUTATIONS.items():
 def test(self,m=mutation,case=name):
  o=check(m)
  if case=='changed_original_unrendered':
   self.assertEqual(o['state'],'DRAFT_HARD_HOLD')
   self.assertEqual(len(o['r200_lineage_differences']),1)
  else:
   self.assertEqual(o['state'],'INVALID_HARD_HOLD',(case,o['errors']))
  self.assertIs(o['publication_authorized'],False)
 setattr(R299Tests,'test_inventory_'+name,test)

for slug in sorted(g.TOOL_SLUGS):
 def test(self,s=slug):
  o=check(change_html(lambda b:b.replace(b'Used for: provenance',b'Used for: unsupported'),s))
  self.assertIn('EXPORTED_BYTES_NOT_NATIVE:'+s,o['errors'])
 setattr(R299Tests,'test_six_tool_scope_'+slug,test)

if __name__=='__main__':unittest.main()
