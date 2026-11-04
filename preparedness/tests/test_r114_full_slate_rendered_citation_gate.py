"""R114: 70+ independent local synthetic adversaries, no repository fixture writes."""
import copy
import importlib.util
from pathlib import Path
import unittest

PATH=Path(__file__).resolve().parents[1]/'tools/r114_full_slate_rendered_citation_gate.py'
spec=importlib.util.spec_from_file_location('r114',PATH)
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
BODY=('<section><h2>Household planning</h2>'
      +''.join('<p id="p%i">Plan ahead and check local officials. %s {{cite:s1}}</p>'%
               (i, 'Practice your meeting points and review trusted resources. '*9)
               for i in range(16))
      +'<p>{{link:guide-2|Other guide}}</p></section>')

def fixture():
    slate=[{'n':i,'slug':f'guide-{i}','section':'start-here',
            'track':'modern'} for i in range(1,36)]
    docs={r['slug']:{'slug':r['slug'],'section':'start-here','track':'modern',
                      '_body':BODY,'source_use':{'s1':'Use this source for planning'},
                      'safety_review':{'state':'pending'}} for r in slate}
    docs['worksheet']={'kind':'tool'}
    return {'base_path':'/preparedness/','slate':slate},docs

def ok_source(meta,sid):
    return {'id':sid,'url':'https://www.ready.gov/plan','verified_on':'2026-10-29'}

def scan():
    t,a=fixture();return g.audit_slate(t,a,ok_source)

class Core(unittest.TestCase):
    def test_full_35_item_census(self):
        x=scan();self.assertEqual(x['slate_count'],35)
        self.assertEqual(x['article_drafts_found'],35)
        self.assertEqual(x['complete_tool_count'],1)
    def test_always_hold_even_if_metadata_claims_approved(self):
        t,a=fixture()
        for item in a.values():
            if item.get('_body'): item['safety_review']['state']='approved'
        x=g.audit_slate(t,a,ok_source)
        self.assertFalse(x['may_publish']);self.assertFalse(x['independent_QD_PASS'])
        self.assertFalse(x['source_or_safety_review_verified'])
    def test_reproducibility(self):
        self.assertEqual(scan(),scan())
    def test_no_mutation(self):
        t,a=fixture();b=copy.deepcopy((t,a));g.audit_slate(t,a,ok_source)
        self.assertEqual((t,a),b)
    def test_no_pii_or_raw_article_in_report(self):
        s=str(scan());self.assertNotIn('Practice your meeting',s)
        self.assertNotIn('ready.gov',s)
    def test_no_source_claim_accuracy_asserted(self):
        x=scan();self.assertFalse(x['rows_NOT_APPROVED'][0]['author_support_verified'])
        self.assertIn('QUALIFIED_SAFETY_REVIEW_NOT_ESTABLISHED',x['rows_NOT_APPROVED'][0]['review_flags'])
    def test_missing_body_flagged_without_publishing(self):
        t,a=fixture();del a['guide-4'];x=g.audit_slate(t,a,ok_source)
        self.assertEqual(x['article_drafts_found'],34)
        self.assertIn('MISSING_ARTICLE_DRAFT',x['rows_NOT_APPROVED'][3]['review_flags'])
    def test_unbuilt_internal_link_not_dead_url(self):
        t,a=fixture();del a['guide-2'];x=g.audit_slate(t,a,ok_source)
        self.assertIn('RELATED_ARTICLE_NOT_YET_BUILDABLE',x['rows_NOT_APPROVED'][0]['review_flags'])
    def test_valid_article_has_no_structural_flags(self):
        t,a=fixture();d=g.audit_article('guide-1',a['guide-1'],{k:True for k in a},ok_source)
        self.assertEqual(d['review_flags'],['QUALIFIED_SAFETY_REVIEW_NOT_ESTABLISHED'])
    def test_article_body_mutated_keeps_hold(self):
        t,a=fixture();a['guide-1']['_body']+='<p>New claim</p>'
        self.assertFalse(g.audit_slate(t,a,ok_source)['may_merge'])
    def test_single_tool_required(self):
        t,a=fixture();del a['worksheet']
        with self.assertRaises(g.PreflightError):g.audit_slate(t,a,ok_source)

TAG_ATTEMPTS=[
 ('comment','<!-- {{cite:s1}} -->'),('attribute','<p title="{{cite:s1}}"></p>'),
 ('link_attribute','<p title="{{link:guide-2|Go}}"></p>'),
 ('hidden','<p hidden>{{cite:s1}}</p>'),('inert','<p inert>{{cite:s1}}</p>'),
 ('aria','<span aria-hidden="true">{{cite:s1}}</span>'),
 ('display_none','<p style=" display : none ">{{cite:s1}}</p>'),
 ('visibility','<p style="visibility:hidden">{{cite:s1}}</p>'),
 ('opacity','<p style="opacity:0">{{cite:s1}}</p>'),
 ('cv','<p style="content-visibility:hidden">{{cite:s1}}</p>'),
 ('sr_only','<p class="sr-only">{{cite:s1}}</p>'),
 ('visually_hidden','<p class="visually-hidden">{{cite:s1}}</p>'),
 ('screen_reader_text','<p class="screen-reader-text">{{cite:s1}}</p>'),
 ('d_none','<p class="d-none">{{cite:s1}}</p>'),
 ('is_hidden','<p class="is-hidden">{{cite:s1}}</p>'),
 ('hidden_ancestor','<div hidden><p>{{cite:s1}}</p></div>'),
 ('svg','<svg><text>{{cite:s1}}</text></svg>'),
 ('script','<script>{{cite:s1}}</script>'),
 ('style','<style>{{cite:s1}}</style>'),
 ('template','<template>{{cite:s1}}</template>'),
 ('noscript','<noscript>{{cite:s1}}</noscript>'),
 ('iframe','<iframe>{{cite:s1}}</iframe>'),
 ('canvas','<canvas>{{cite:s1}}</canvas>'),
 ('object','<object>{{cite:s1}}</object>'),
 ('nested_hidden_link','<div inert><p>{{link:guide-2|Go}}</p></div>'),
 ('comment_link','<!-- {{link:guide-2|Go}} -->'),
 ('javascript_link','<a href="javascript:alert(1)">Go</a>'),
 ('data_link','<a href="data:text/html,boom">Go</a>'),
 ('file_link','<a href="file:///etc/passwd">Go</a>'),
 ('vbscript_link','<a href="vbscript:msgbox(1)">Go</a>'),
 ('duplicate_id','<p id="p3">duplicate</p>'),
 ('unclosed','<div>'),('stray_end','</aside>'),
 ('unknown_token','<p>{{untrusted:claim}}</p>'),
 ('malformed_cite','<p>{{cite:s1</p>'),
 ('malformed_link','<p>{{link:guide-2|Go</p>'),
]
for name,tail in TAG_ATTEMPTS:
    def check(s):
        def f(self):
            t,a=fixture();a['guide-1']['_body']+=s
            row=g.audit_slate(t,a,ok_source)['rows_NOT_APPROVED'][0]
            self.assertTrue(row['review_flags'],s)
            self.assertTrue(any(x not in ('QUALIFIED_SAFETY_REVIEW_NOT_ESTABLISHED',)
                                for x in row['review_flags']),s)
            self.assertFalse(row['may_publish'])
        return f
    setattr(Core,'test_html_mutation_'+name,check(tail))

META_ATTEMPTS=[
 ('no_scopes',lambda d:d.pop('source_use')),
 ('blank_scope',lambda d:d['source_use'].update(s1='  ')),
 ('unknown_source',lambda d:d.update(_body=d['_body'].replace('cite:s1','cite:s99'))),
 ('no_visible_citation',lambda d:d.update(_body=d['_body'].replace('{{cite:s1}}',''))),
 ('source_use_wrong_type',lambda d:d.update(source_use=['s1'])),
 ('wrong_slug',lambda d:d.update(slug='wrong')),
 ('wrong_section',lambda d:d.update(section='lost-ways')),
 ('wrong_track',lambda d:d.update(track='lost-ways')),
 ('thin_article',lambda d:d.update(_body='<p>Short {{cite:s1}}</p>')),
 ('unregistered_link',lambda d:d.update(_body=d['_body']+'<p>{{link:not-here|Go}}</p>')),
 ('no_review',lambda d:d.pop('safety_review')),
]
for name,fn in META_ATTEMPTS:
    def check(m):
        def f(self):
            t,a=fixture();m(a['guide-1'])
            d=g.audit_slate(t,a,ok_source)['rows_NOT_APPROVED'][0]
            self.assertTrue(any(q!='QUALIFIED_SAFETY_REVIEW_NOT_ESTABLISHED' for q in d['review_flags']))
            self.assertFalse(d['may_publish'])
        return f
    setattr(Core,'test_metadata_mutation_'+name,check(fn))

TAX_ATTEMPTS=[
 ('bad_base',lambda t:t.update(base_path='/unknown/')),
 ('short_count',lambda t:t['slate'].pop()),
 ('duplicate_number',lambda t:t['slate'][1].update(n=1)),
 ('extra_number',lambda t:t['slate'][1].update(n=88)),
 ('duplicate_slug',lambda t:t['slate'][1].update(slug='guide-1')),
 ('section_slash',lambda t:t['slate'][1].update(section='../food')),
 ('section_upper',lambda t:t['slate'][1].update(section='Food')),
 ('slug_slash',lambda t:t['slate'][1].update(slug='../guide')),
 ('slug_unicode',lambda t:t['slate'][1].update(slug='guidé-2')),
 ('empty_slug',lambda t:t['slate'][1].update(slug='')),
 ('slug_duplicate_url',lambda t:t['slate'][1].update(slug='guide-1',section='start-here')),
]
for name,fn in TAX_ATTEMPTS:
    def check(m):
        def f(self):
            t,a=fixture();m(t)
            with self.assertRaises(g.PreflightError):g.audit_slate(t,a,ok_source)
        return f
    setattr(Core,'test_taxonomy_mutation_'+name,check(fn))

class SourceFailures(unittest.TestCase):
    def _run(self,source):
        t,a=fixture()
        return g.audit_article('guide-1',a['guide-1'],{'guide-2':True},source)['review_flags']
    def test_missing_source(self):
        def fail(m,s):raise KeyError(s)
        self.assertIn('AUTHOR_SCOPED_SOURCE_UNRESOLVED',self._run(fail))
    def test_wrong_id(self):
        self.assertIn('AUTHOR_SCOPED_SOURCE_ID_MISMATCH',self._run(lambda m,s:{'id':'other'}))
    def test_unverified_source(self):
        self.assertIn('SOURCE_REQUIRES_HUMAN_VERIFICATION',self._run(lambda m,s:{'id':s}))
    def test_missing_source_dict(self):
        self.assertIn('AUTHOR_SCOPED_SOURCE_ID_MISMATCH',self._run(lambda m,s:None))
    def test_source_invalid_type(self):
        def bad(m,s):raise TypeError('bad')
        self.assertIn('AUTHOR_SCOPED_SOURCE_UNRESOLVED',self._run(bad))

if __name__=='__main__':unittest.main()
