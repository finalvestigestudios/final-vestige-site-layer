"""Pure offline attack-fixture tests; never touch authentic Preparedness source files."""
from __future__ import annotations
import copy
import json
import unittest
from unittest.mock import patch
from preparedness.tools import r329_agency_service_citation_hold as g


def synthetic():
    bodies={'a_body':[],'t_body':[]}
    for ident,role,needle,cite,risk,url in g.CLAIMS:
        text='Context '+needle+' remains under review.'
        if cite:
            text+='{{cite:'+cite+'}}'
        bodies[role].append('<p>'+text+'</p>')
    docs={k:'\n'.join(v).encode('utf-8') for k,v in bodies.items()}
    for role,n,slug,bodykey in [('a_meta',15,'family-communication-plan','a_body'),
                                 ('t_meta',104,'family-reunification-card','t_body')]:
        cites=set(g.CITE.findall(docs[bodykey].decode('utf8')))
        docs[role]=json.dumps({'n':n,'slug':slug,'status':{'editorial':'drafted','publish':'draft'},
           'safety_review':{'state':'pending','reviewer':None,'date':None},
           'source_use':{c:'Synthetic - never an actual evidence attestation' for c in cites}},
           sort_keys=True).encode('utf8')
    return docs


def rewrite_meta(docs,role,fn):
    data=json.loads(docs[role]);fn(data);docs[role]=json.dumps(data,sort_keys=True).encode()


class BaselineTests(unittest.TestCase):
    def test_complete_synthetic_witnesses_still_hard_hold(self):
        out=g.inspect(synthetic())
        self.assertEqual(out['state'],'DRAFT_HARD_HOLD',out['errors'])
        self.assertEqual(out['claim_review_count'],7)
        self.assertEqual(out['independently_approved_count'],0)
        self.assertFalse(any(out['release'].values()))
        self.assertTrue(all(not x['current_claim_support_proven'] for x in out['claims']))
    def test_stable_output_for_same_bytes(self):
        a,b=g.inspect(synthetic()),g.inspect(synthetic())
        self.assertEqual(json.dumps(a,sort_keys=True),json.dumps(b,sort_keys=True))
    def test_authentic_pins_match_r328(self):
        self.assertEqual(len(g.previous.DOCS),4)
        self.assertEqual(len(set(x[0] for x in g.CLAIMS)),7)
        self.assertEqual(set(x[1] for x in g.CLAIMS),{'a_body','t_body'})
    def test_qa_review_is_not_claimed(self):
        out=g.inspect(synthetic())
        self.assertIn('DRAFT',out['state'])
        self.assertTrue(all(c['review_status']=='UNRESOLVED_QUALIFIED_REVIEW' for c in out['claims']))
    def test_missing_everything_fails(self):
        out=g.inspect({})
        self.assertEqual(out['state'],'INVALID_HARD_HOLD')
        self.assertFalse(any(out['release'].values()))
    def test_non_dict_fails(self):
        self.assertEqual(g.inspect(None)['state'],'INVALID_HARD_HOLD')
    def test_additional_role_rejected(self):
        d=synthetic();d['unexpected']=b'hello'
        self.assertIn('FOUR_REQUIRED_DOCUMENT_ROLES',g.inspect(d)['errors'])
    def test_non_byte_body_rejected(self):
        d=synthetic();d['a_body']=d['a_body'].decode()
        self.assertIn('MISSING_OR_NONBYTE_A_BODY',g.inspect(d)['errors'])
    def test_nonut8_rejected(self):
        d=synthetic();d['t_body']=b'\xff'
        self.assertIn('BAD_UTF8_OR_JSON_T_BODY',g.inspect(d)['errors'])
    def test_bad_json_rejected(self):
        d=synthetic();d['a_meta']=b'{invalid json}'
        self.assertIn('BAD_UTF8_OR_JSON_A_META',g.inspect(d)['errors'])
    def test_json_duplicate_keys_rejected(self):
        d=synthetic();d['a_meta']=d['a_meta'][:-1]+b',"n":15}'
        self.assertIn('BAD_UTF8_OR_JSON_A_META',g.inspect(d)['errors'])
    def test_empty_registry_rejected(self):
        d=synthetic();rewrite_meta(d,'t_meta',lambda m:m.update(source_use={}))
        self.assertIn('CITATION_REGISTRY_DRIFT_T_META',g.inspect(d)['errors'])
    def test_citation_malformed_rejected(self):
        d=synthetic();d['t_body']+=b'<p>{{cite:NOT-VALID}}</p>'
        self.assertIn('MALFORMED_CITATION_T_META',g.inspect(d)['errors'])
    def test_gitrejects_mismatched_blob(self):
        d=synthetic()
        o=g.audit(lambda p: next(d[k] for k,(path,_) in g.previous.DOCS.items() if path==p))
        self.assertEqual(o['state'],'INVALID_HARD_HOLD')
        self.assertEqual(o['authenticated_git_objects'],0)
        self.assertEqual(len([s for s in o['errors'] if s.startswith('PINNED_GIT_OBJECT_')]),4)
    def test_git_missing_file_is_fail_closed(self):
        out=g.audit(lambda p: (_ for _ in ()).throw(OSError('blocked')))
        self.assertEqual(out['state'],'INVALID_HARD_HOLD')
        self.assertEqual(out['authenticated_git_objects'],0)
    def test_no_network_write_actions_in_module(self):
        # The scanner's only external input is an injected reader; not a deployer.
        self.assertFalse(hasattr(g,'publish'))
        self.assertFalse(hasattr(g,'post_to_wordpress'))


class ClaimMutationTests(unittest.TestCase):
    pass


def add_attack(name, transform, expected_error):
    def test(self):
        d=synthetic()
        transform(d)
        out=g.inspect(d)
        self.assertEqual(out['state'],'INVALID_HARD_HOLD')
        self.assertIn(expected_error,out['errors'],out['errors'])
        self.assertFalse(any(out['release'].values()))
    setattr(ClaimMutationTests,'test_'+name,test)


for idx, (ident,role,needle,cite,risk,url) in enumerate(g.CLAIMS):
    safeid=ident.lower().replace('-','_')
    def remove(d,role=role,needle=needle):
        d[role]=d[role].replace(needle.encode(),b'removed sensitive advice',1)
    add_attack(f'{idx:02d}_{safeid}_deleted',remove,'ANCHOR_MISSING_OR_DUPLICATED_'+ident)
    def duplicate(d,role=role,needle=needle):
        # Repeating exact excerpt is not an independent source or adjudication.
        d[role]+=b'<p>'+needle.encode()+b'</p>'
    add_attack(f'{idx:02d}_{safeid}_duplicated',duplicate,'ANCHOR_MISSING_OR_DUPLICATED_'+ident)
    def naked(d,role=role,needle=needle,cite=cite):
        # Remove the surrounding paragraph without changing the text.
        body=d[role].decode()
        target=next(p for p in body.split('\n') if needle in p)
        d[role]=body.replace(target,target.replace('<p>','<div>').replace('</p>','</div>')).encode()
    add_attack(f'{idx:02d}_{safeid}_no_paragraph',naked,'CLAIM_HAS_NO_UNIQUE_BLOCK_'+ident)
    if cite:
        def moved(d,role=role,needle=needle,cite=cite):
            b=d[role].decode()
            target=next(p for p in b.split('\n') if needle in p)
            d[role]=b.replace(target,target.replace('{{cite:'+cite+'}}','')+'\n<p>{{cite:'+cite+'}}</p>').encode()
        add_attack(f'{idx:02d}_{safeid}_moved_cite',moved,'CITATION_NOT_ADJACENT_'+ident)
        def undeclare(d,role=role,cite=cite):
            meta='a_meta' if role=='a_body' else 't_meta'
            rewrite_meta(d,meta,lambda m:m['source_use'].pop(cite))
        add_attack(f'{idx:02d}_{safeid}_undeclared',undeclare,'SOURCE_USE_NOT_DECLARED_'+ident)

for role in ('a_meta','t_meta'):
    for label,fn in [
        ('published',lambda m:m['status'].update(publish='published')),
        ('editorial_approved',lambda m:m['status'].update(editorial='approved')),
        ('fake_safety_pass',lambda m:m['safety_review'].update(state='approved')),
        ('fake_reviewer',lambda m:m['safety_review'].update(reviewer='Synthetic Reviewer')),
        ('fake_date',lambda m:m['safety_review'].update(date='2026-11-12')),
        ('wrong_number',lambda m:m.update(n=102)),
        ('wrong_slug',lambda m:m.update(slug='reunification-plan')),
        ('no_safety',lambda m:m.pop('safety_review')),
        ('no_source_use',lambda m:m.pop('source_use')),
        ('not_a_dict',lambda m:m.update(source_use=['shelter-fcc-comms'])),
    ]:
        add_attack(role+'_'+label,lambda d,r=role,f=fn:rewrite_meta(d,r,f),
                   'UNSAFE_OR_DRIFTED_IDENTITY_'+role.upper())

if __name__=='__main__':unittest.main()
