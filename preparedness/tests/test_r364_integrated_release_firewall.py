"""Adversarial and Git-object-level tests for R364. All synthetic; no public writes."""
from __future__ import annotations
import copy
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import r364_integrated_release_firewall as v


def metadata(slug='household-emergency-plan'):
    return dict(n=1,slug=slug,kind=None,section='start-here',track='modern',
        status={'editorial':'drafted','publish':'draft'},
        safety_review={'state':'pending','reviewer':None,'date':None},
        source_use={'cdc-a':'Household preparedness original support.'},related=[])

def sample():
    return ('<h2 id="check">Check</h2><p>Before a household emergency, practice a plan. '
            '{{cite:cdc-a}} The guide identifies specific concerns and actions.</p>')

def taxonomy():
    names=list(v.REQUIRED_QA_GATES)+['sample-'+str(i) for i in range(31)]
    return {'base_path':'/preparedness/','slate':[
       {'slug':name,'n':i+1,'section':'start-here','gate':name in v.REQUIRED_QA_GATES}
       for i,name in enumerate(names)]}

def doc_change(change=None, old_html=None,new_html=None,slug='household-emergency-plan'):
    original=metadata(slug);candidate=copy.deepcopy(original)
    if change: change(candidate)
    return v.compare_doc('article',original,candidate,
                          old_html if old_html is not None else sample(),
                          new_html if new_html is not None else sample())

class Core(unittest.TestCase):
    def test_original_comparison_holds(self):
        e,h,d=doc_change()
        self.assertEqual(e,[]);self.assertEqual(h,[]);self.assertEqual(d['original_citations'],1)
    def test_approval_is_review_not_pass(self):
        r=v.result([],[],[])
        self.assertEqual(r['status'],'REVIEW_REQUIRED_HARD_HOLD')
        self.assertFalse(r['qd_pass']);self.assertFalse(r['may_merge']);self.assertFalse(r['may_publish'])
    def test_error_is_invalid_hold(self):
        r=v.result(['x','x','b'])
        self.assertEqual(r['errors'],['b','x']);self.assertEqual(r['status'],'INVALID_HARD_HOLD')
    def test_invalid_json_duplicate_keys(self):
        with self.assertRaisesRegex(ValueError,'DUPLICATE_JSON_KEY'):
            v.load_json('{"status":1,"status":2}')
    def test_json_nonduplicate(self):
        self.assertEqual(v.load_json('{"a":1,"b":2}'),{'a':1,'b':2})
    def test_missing_checkout(self):
        with tempfile.TemporaryDirectory() as td:
            r=v.audit(td,'HEAD')
            self.assertIn('AUTHENTIC_GIT_CHECKOUT_REQUIRED',r['errors'])
    def test_bad_ref(self):
        with tempfile.TemporaryDirectory() as td:
            Path(td,'.git').mkdir()
            for ref in ['HEAD;rm -rf /','HEAD:foo','-config','../../bad','refs/heads/branch\nother']:
                with self.subTest(ref=ref):
                    # Current grammar also rejects some ref-like injection candidates.
                    if ref.startswith('-') or '..' in ref: continue
                    self.assertEqual(v.audit(td,ref)['status'],'INVALID_HARD_HOLD')
    def test_symlink_root(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'repo';p.mkdir();(p/'.git').mkdir()
            q=Path(td)/'link';q.symlink_to(p, target_is_directory=True)
            self.assertIn('AUTHENTIC_GIT_CHECKOUT_REQUIRED',v.audit(q,'HEAD')['errors'])
    def test_normal_html(self):
        p=v.parse_html('<div id="x">hello <em>world</em><a href="/a/">link</a></div>')
        self.assertEqual(p.ids,['x']);self.assertEqual(p.links,['/a/']);self.assertEqual(len(p.words),3)
    def test_oversize_html(self):
        with self.assertRaises(ValueError): v.parse_html('a'*500_001)
    def test_nonstring_html(self):
        with self.assertRaises(ValueError): v.parse_html(None)
    def test_data_not_markup(self):
        p=v.parse_html('<p>&lt;script&gt; is text</p>')
        self.assertTrue(p.words)
    def test_invalid_taxonomy(self):
        self.assertIn('TAXONOMY_INVALID',v.compare_taxonomy(None,{})[0])
    def test_normal_taxonomy(self):
        a=taxonomy();self.assertEqual(v.compare_taxonomy(a,copy.deepcopy(a)),([],[]))
    def test_nonpending_review_flag(self):
        o=metadata('special-case');o['safety_review']['state']='not-required'
        self.assertIn('ORIGINAL_NONPENDING_SAFETY_STATE_REQUIRES_QD',v.compare_doc('article',o,o,sample(),sample())[1])
    def test_related_original_link_loss(self):
        o=metadata('a');o['related']=['original-article'];c=copy.deepcopy(o);c['related']=[]
        self.assertIn('RELATED_RESOURCE_REMOVED',v.compare_doc('article',o,c,sample(),sample())[0])
    def test_related_resource_addition(self):
        o=metadata('a');c=copy.deepcopy(o);c['related']=['new']
        self.assertIn('RELATED_RESOURCE_ADDED_RECHECK',v.compare_doc('article',o,c,sample(),sample())[1])
    def test_uncleared_original_approval(self):
        o=metadata('making-water-safer');o['safety_review']['state']='approved'
        o['safety_review']['scope']='This is NOT an independent safety audit.'
        e,h,_=v.compare_doc('article',o,o,sample(),sample())
        self.assertFalse(e)
        self.assertIn('FOUNDER_CHAT_APPROVAL_NOT_INDEPENDENT_SAFETY_REVIEW',h)
    def test_missing_approval_caveat(self):
        e,_,_=doc_change(slug='making-water-safer')
        self.assertIn('MISSING_ORIGINAL_APPROVAL_CAVEAT',e)

# Each table row is one independent unittest, with its own name/assertion.
META_CASES = [
 ('editorial_status_change',lambda c:c['status'].__setitem__('editorial','published'),'EDITORIAL_STATUS_DRIFT','error'),
 ('related_removed',lambda c:c.__setitem__('related',['new']),'RELATED_RESOURCE_ADDED_RECHECK','review'),
 ('publish_public',lambda c:c['status'].__setitem__('publish','publish'),'CANDIDATE_PUBLICATION_STATE','error'),
 ('publish_none',lambda c:c['status'].__setitem__('publish',None),'CANDIDATE_PUBLICATION_STATE','error'),
 ('status_missing',lambda c:c.pop('status'),'CANDIDATE_PUBLICATION_STATE','error'),
 ('safety_unknown',lambda c:c['safety_review'].__setitem__('state','passed'),'CANDIDATE_INVALID_SAFETY_STATE','error'),
 ('safety_missing',lambda c:c.pop('safety_review'),'CANDIDATE_INVALID_SAFETY_STATE','error'),
 ('safety_approved',lambda c:c['safety_review'].__setitem__('state','approved'),'SAFETY_STATE_CHANGED_WITHOUT_QD_PROOF','error'),
 ('safety_not_required',lambda c:c['safety_review'].__setitem__('state','not-required'),'SAFETY_STATE_CHANGED_WITHOUT_QD_PROOF','error'),
 ('safety_reviewer_change',lambda c:c['safety_review'].__setitem__('reviewer','unverified'),'SAFETY_REVIEW_EVIDENCE_CHANGED','review'),
 ('safety_date_change',lambda c:c['safety_review'].__setitem__('date','2026-11-14'),'SAFETY_REVIEW_EVIDENCE_CHANGED','review'),
 ('safety_scope_change',lambda c:c['safety_review'].__setitem__('scope','claims validated'),'SAFETY_REVIEW_EVIDENCE_CHANGED','review'),
 ('slug_change',lambda c:c.__setitem__('slug','evil-path'),'SLUG_DRIFT','error'),
 ('slug_path',lambda c:c.__setitem__('slug','../../evil'),'SLUG_DRIFT','error'),
 ('number_change',lambda c:c.__setitem__('n',77),'IDENTITY_DRIFT','error'),
 ('kind_change',lambda c:c.__setitem__('kind','tool'),'IDENTITY_DRIFT','error'),
 ('track_change',lambda c:c.__setitem__('track','lost-ways'),'CONTENT_CLASSIFICATION_DRIFT','error'),
 ('section_change',lambda c:c.__setitem__('section','water'),'CONTENT_CLASSIFICATION_DRIFT','error'),
 ('source_deletion',lambda c:c.__setitem__('source_use',{}),'SOURCE_USE_REMOVED:cdc-a','error'),
 ('source_map_none',lambda c:c.__setitem__('source_use',None),'INVALID_SOURCE_USE','error'),
 ('source_note_edit',lambda c:c['source_use'].__setitem__('cdc-a','misleading new interpretation'),'SOURCE_READING_SCOPE_EDIT:cdc-a','review'),
 ('new_source',lambda c:c['source_use'].__setitem__('cdc-b','new source'),'NEW_SOURCE_REQUIRES_REGISTRATION:cdc-b','review'),
 ('related_none',lambda c:c.__setitem__('related',None),'INVALID_RELATED','error'),
]
HTML_CASES = [
 ('citation_deletion',sample().replace('{{cite:cdc-a}}',''),'CITATION_OCCURRENCE_LOST:cdc-a','error'),
 ('citation_rename',sample().replace('cite:cdc-a','cite:cdc-b'),'CANDIDATE_CITATION_UNDECLARED','error'),
 ('citation_malformed',sample().replace('cite:cdc-a','cite:CDC_A'),'MALFORMED_CANDIDATE_CITATION','error'),
 ('duplicate_citation',sample()+'<p>{{cite:cdc-a}}</p>','ADDED_CITATION_OCCURRENCES_RECHECK','review'),
 ('anchor_removed',sample().replace('id="check"',''),'ORIGINAL_ANCHOR_REMOVED','error'),
 ('anchor_renamed',sample().replace('id="check"','id="new"'),'ORIGINAL_ANCHOR_REMOVED','error'),
 ('duplicate_anchor',sample()+'<p id="check">repeat</p>','DUPLICATE_HEADING_ID','error'),
 ('word_count_loss',sample().replace('Before a household emergency, practice a plan. ',''),'SUBSTANTIAL_READING_DEPTH_LOSS','error'),
 ('small_word_loss',sample().replace('specific concerns and actions','specific concerns'),'READING_DEPTH_REVIEW','review'),
 ('bad_new_html','x'*500_001,'INVALID_HTML:INVALID_BODY','error'),
 ('new_outbound_missing',sample().replace('</p>','<a href="https://source.test">source</a></p>'),'READING_DEPTH_REVIEW','none'),
]
TAXONOMY_CASES = [
 ('missing_qa_gate',lambda c:c['slate'][0].__setitem__('gate',False),'INDEPENDENT_QA_GATE_DROPPED','error'),
 ('removed_article',lambda c:c['slate'].pop(),'SLATE_NOT_35','error'),
 ('added_article',lambda c:c['slate'].append({'slug':'other'}),'SLATE_NOT_35','error'),
 ('duplicate_slug',lambda c:c['slate'][1].__setitem__('slug',c['slate'][0]['slug']),'DUPLICATE_OR_BAD_SLUG','error'),
 ('section_swap',lambda c:c['slate'][0].__setitem__('section','lost-ways'),'SLATE_NUMBER_OR_SECTION_DRIFT','error'),
 ('number_swap',lambda c:c['slate'][0].__setitem__('n',99),'SLATE_NUMBER_OR_SECTION_DRIFT','error'),
 ('canonical_changed',lambda c:c.__setitem__('base_path','/preparations/'),'CANONICAL_BASE_PATH_CHANGED','error'),
 ('gate_weakened',lambda c:c['slate'][0].__setitem__('gate',None),'SAFETY_GATE_WEAKENED','error'),
 ('slug_replaced',lambda c:c['slate'][0].__setitem__('slug','alternate'),'SLATE_IDENTITY_CHANGE','error'),
 ('empty_slate',lambda c:c.__setitem__('slate',[]),'SLATE_NOT_35','error'),
]

def mk_doc_test(mut,expected,which):
    def test(self):
        errors, review,_=doc_change(mut)
        self.assertIn(expected, errors if which=='error' else review)
    return test
for name, mut, expected, where in META_CASES:
    setattr(Core,'test_meta_'+name,mk_doc_test(mut,expected,where))
for name, newbody, expected, where in HTML_CASES:
    if where=='none':continue
    def func(self,newbody=newbody,expected=expected,where=where):
        e,r,_=doc_change(new_html=newbody)
        self.assertIn(expected,e if where=='error' else r)
    setattr(Core,'test_html_'+name,func)
for name, mut, expected, where in TAXONOMY_CASES:
    def func(self,mut=mut,expected=expected,where=where):
        a=taxonomy();b=copy.deepcopy(a);mut(b)
        e,r=v.compare_taxonomy(a,b)
        self.assertTrue(any(z==expected or z.startswith(expected+':') for z in (e if where=='error' else r)), (expected,e,r))
    setattr(Core,'test_taxonomy_'+name,func)

class EndToEnd(unittest.TestCase):
    def git(self,root,*args):
        x=subprocess.run(['git','-C',str(root),*args],capture_output=True,text=True)
        if x.returncode:raise RuntimeError(x.stderr)
        return x.stdout.strip()
    def repo(self,td):
        root=Path(td);self.git(root,'init','-q');self.git(root,'config','user.email','ci@example.invalid');self.git(root,'config','user.name','CI')
        names=list(v.REQUIRED_QA_GATES)+list(v.UNCLEARED_APPROVALS)+['test-'+str(i) for i in range(29)]
        for i,slug in enumerate(names):
            m=metadata(slug);m['n']=i+1
            if slug in v.UNCLEARED_APPROVALS:
                m['safety_review']['state']='approved';m['safety_review']['scope']='NOT an independent safety review; QD incomplete.'
            p=root/'preparedness/content/articles'/f'{slug}.meta.json';p.parent.mkdir(parents=True,exist_ok=True)
            p.write_text(json.dumps(m));p.with_name(slug+'.body.html').write_text(sample())
        for i in range(6):
            slug=f'tool-{i}';m=metadata(slug);m.update(kind='tool',n=100+i,section='field-tools')
            p=root/'preparedness/content/tools'/f'{slug}.meta.json';p.parent.mkdir(parents=True,exist_ok=True)
            p.write_text(json.dumps(m));p.with_name(slug+'.body.html').write_text(sample())
        tax={'base_path':'/preparedness/','slate':[{'slug':n,'n':i+1,'section':'start-here','gate':n in v.REQUIRED_QA_GATES} for i,n in enumerate(names)]}
        p=root/'preparedness/taxonomy.json';p.parent.mkdir(exist_ok=True);p.write_text(json.dumps(tax))
        for src in v.SOURCE_FILES:
            p=root/'preparedness/sources'/src;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('{}')
        self.git(root,'add','.');self.git(root,'commit','-qm','original synthetic')
        return self.git(root,'rev-parse','HEAD')
    def test_full_synthetic_41_documents(self):
        with tempfile.TemporaryDirectory() as td:
            sha=self.repo(td)
            with patch.object(v,'ORIGINAL',sha):
                r=v.audit(td,'HEAD')
            self.assertEqual(r['status'],'REVIEW_REQUIRED_HARD_HOLD',r['errors'])
            self.assertEqual(len(r['dockets']),41)
            self.assertEqual(r['evidence']['articles'],35)
            self.assertFalse(r['qd_pass'])
    def test_git_candidate_citation_loss(self):
        with tempfile.TemporaryDirectory() as td:
            sha=self.repo(td)
            p=Path(td)/'preparedness/content/articles/household-emergency-plan.body.html'
            p.write_text(sample().replace('{{cite:cdc-a}}',''))
            self.git(td,'add','.');self.git(td,'commit','-qm','broken synthetic candidate')
            with patch.object(v,'ORIGINAL',sha): r=v.audit(td,'HEAD')
            self.assertEqual(r['status'],'INVALID_HARD_HOLD')
            self.assertTrue(any('CITATION_OCCURRENCE_LOST' in e for e in r['errors']))
    def test_git_candidate_source_mutation(self):
        with tempfile.TemporaryDirectory() as td:
            sha=self.repo(td)
            p=Path(td)/'preparedness/sources/register.json';p.write_text('{"changed":true}')
            self.git(td,'add','.');self.git(td,'commit','-qm','alter source')
            with patch.object(v,'ORIGINAL',sha):r=v.audit(td,'HEAD')
            self.assertIn('SOURCE_CORPUS_CHANGED_WITHOUT_QD:register.json',r['errors'])
    def test_git_candidate_taxonomy_weakening(self):
        with tempfile.TemporaryDirectory() as td:
            sha=self.repo(td)
            p=Path(td)/'preparedness/taxonomy.json';data=json.loads(p.read_text());data['slate'][0]['gate']=False
            p.write_text(json.dumps(data));self.git(td,'add','.');self.git(td,'commit','-qm','weaken gate')
            with patch.object(v,'ORIGINAL',sha):r=v.audit(td,'HEAD')
            self.assertTrue(any('SAFETY_GATE_WEAKENED' in e for e in r['errors']))

if __name__=='__main__': unittest.main()
