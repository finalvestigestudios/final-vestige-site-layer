"""Deterministic synthetic tests; no real article safety or merchant verification."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

PATH=Path(__file__).resolve().parents[1]/'tools/r208_citation_destination_gate.py'
spec=importlib.util.spec_from_file_location('r208',PATH)
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)

SOURCE={
 'source-a':{'url':'https://www.ready.gov/plan','title':'Make a Plan','publisher':'Ready.gov',
             'human_link_check':True},
 'source-b':{'url':'https://www.cdc.gov/emergency','title':'Emergency Resources','publisher':'CDC',
             'human_link_check':True}}

def sample():
 rows=[];materials={};wp={};previews={}
 for n in range(1,36):
  slug=f'article-{n}';route=f'/preparedness/start-here/{slug}/'
  rows.append({'slug':slug,'route':route})
 for r in rows:
  slug=r['slug'];body=(f'<section><h2>Essential facts for {slug}</h2><p>Plan ahead. {{{{cite:source-a}}}}'
       '<a href="https://www.ready.gov/plan">Read original</a></p></section>'
       '<section><p>Also use <b>contacts</b> and {{link:article-1|the first article}}.'
       '{{cite:source-b}}</p></section>')
  meta={'slug':slug,'status':{'publish':'draft'},'safety_review':{'state':'pending'},
        'source_use':{'source-a':'Official emergency planning checklist',
                      'source-b':'Emergency resources and disaster planning'}}
  materials[slug]={'body':body,'meta':meta}
  def render_cite(m):
   no={'source-a':1,'source-b':2}[m.group(1)]
   return f'<sup class="pa-cite"><a href="#src-{no}" aria-label="Source">[{no}]</a></sup>'
  import re
  done=g.CITE.sub(render_cite,body)
  done=g.LINK.sub(lambda m:f'<a href="/preparedness/start-here/{m.group(1)}/">{m.group(2)}</a>',done)
  refs=''.join(f'<li id="src-{idx}"><a href="{src["url"]}" rel="noopener">{src["title"]}</a>. '
     f'{src["publisher"]}. <span class="pa-src-use">Used for: {meta["source_use"][sid]}</span></li>'
     for idx,(sid,src) in enumerate(SOURCE.items(),1))
  doc=f'<div class="pa-article"><div class="pa-body" id="pa-main">{done}</div><section class="pa-sources"><ol>{refs}</ol></section></div>'
  wp[slug]=doc;previews[slug]=doc
 return rows,materials,wp,previews,copy.deepcopy(SOURCE)

class GateTests(unittest.TestCase):
 def test_normal_structural_hold(self):
  result=g.audit(*sample());self.assertEqual(result['state'],g.HOLD,str(result['errors']))
  self.assertEqual(len(result['articles']),35)
  self.assertEqual(result['exceptions'],[])
  self.assertFalse(result['publication_authorized'])
 def test_absent_source_use_retained_as_exception(self):
  data=sample();data[1]['article-7']['meta']['source_use'].pop('source-a')
  result=g.audit(*data);self.assertEqual(result['state'],g.HOLD,str(result['errors']))
  self.assertEqual([x['type'] for x in result['exceptions']],['missing_article_source_use']*2)
 def test_human_link_check_false_is_not_safety_approved(self):
  data=sample();data[4]['source-a']['human_link_check']=False
  result=g.audit(*data);self.assertEqual(result['state'],g.HOLD)
  self.assertEqual(len(result['exceptions']),70)
  self.assertFalse(result['independent_qd_pass'])
 def test_unsupported_http_source_rejected(self):
  data=sample();data[4]['source-a']['url']='http://www.ready.gov/plan'
  self.assertEqual(g.audit(*data)['state'],g.INVALID)
 def test_no_source_inventory(self):
  data=list(sample());data[4]={};self.assertEqual(g.audit(*data)['state'],g.INVALID)
 def test_forged_approval(self):
  data=sample();data[1]['article-1']['meta']['safety_review']['state']='approved'
  self.assertEqual(g.audit(*data)['state'],g.INVALID)
 def test_synthetic_article_bodies_are_two_sections(self):
  data=sample();order,links=g.expected_body(data[1]['article-1']['body'],{r['slug']:r['route'] for r in data[0]})
  self.assertEqual(len(links),4);self.assertEqual(len(order),2)
 def test_protocols(self):
  for href in ('javascript:alert(1)','data:text/html,hi','//phishing.example','../unsafe','https://u:p@example.com',' https://ok.com'):
   with self.subTest(href=href),self.assertRaises(g.GateError):g.safe_href(href)
  for href in ('/preparedness/','#src-1','https://www.ready.gov/plan'):
   self.assertEqual(g.safe_href(href),href)
 def test_fail_closed_missing_checkout(self):
  self.assertEqual(g.main(['--repo','/nonexistent']),3)


def per_article_link_mutation(n):
 def test(self):
  data=sample();slug=f'article-{n}';data[2][slug]=data[2][slug].replace('/preparedness/start-here/article-1/', '/redirect-out/',1)
  self.assertEqual(g.audit(*data)['state'],g.INVALID)
 return test

def per_article_bibliography_mutation(n):
 def test(self):
  data=sample();slug=f'article-{n}';data[3][slug]=data[3][slug].replace('https://www.ready.gov/plan','https://attacker.example.net/',1)
  self.assertEqual(g.audit(*data)['state'],g.INVALID)
 return test

for n in range(1,36):
 setattr(GateTests,f'test_body_link_mutation_{n:02}',per_article_link_mutation(n))
 setattr(GateTests,f'test_bibliography_mutation_{n:02}',per_article_bibliography_mutation(n))

if __name__=='__main__':unittest.main()
