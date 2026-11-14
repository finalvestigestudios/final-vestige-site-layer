"""Synthetic regression suite for R363; tests claim *binding*, not medical safety."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import r363_claim_source_binding_gate as g


def fixture():
    a = {'id':'src-a','url':'https://agency.test/one','supports':'only one topic',
         'verified_on':'2026-01-01','human_link_check':True}
    b = {'id':'src-b','url':'https://agency.test/two','supports':'different topic',
         'verified_on':'2026-01-02','human_link_check':True}
    meta = {'slug':'family-communication-plan','status':{'publish':'draft'},
            'safety_review':{'state':'pending'},
            'source_use':{'src-a':'Claim A','src-b':'Claim B'}}
    body = '<p>Claim A {{cite:src-a}}</p><p>Claim B {{cite:src-b}}</p>'
    sources = g.source_index({'start':[a], 'shelter':[b]})
    return meta,body,sources


class Fixed(unittest.TestCase):
    def test_clean(self):
        r = g.check(*fixture())
        self.assertEqual(r['errors'],[])
        self.assertEqual(r['review'],[])
        self.assertEqual(r['citation_count'],2)
        self.assertEqual(r['declared_source_uses'],2)
    def test_two_occurrences(self):
        m,b,s=fixture()
        r=g.check(m,b+b,s)
        self.assertEqual(len(r['occurrences']),4)
        self.assertNotEqual(r['occurrences'][0]['offset'],r['occurrences'][2]['offset'])
    def test_exact_id_not_url_alias(self):
        m,b,s=fixture()
        s['src-b'][0][2]['url']='https://agency.test/one/'
        self.assertEqual(g.check(m,b,s)['errors'],[])
    def test_error_receipt(self):
        self.assertEqual(g.report(['e'])['status'],'INVALID_HARD_HOLD')
    def test_clean_receipt_is_still_hold(self):
        self.assertEqual(g.report([])['status'],'REVIEW_REQUIRED_HARD_HOLD')
    def test_flags_cannot_be_true(self):
        self.assertFalse(any(g.report([])[k] for k in g.HOLD))
    def test_no_source_mutation(self):
        item=fixture(); expected=copy.deepcopy(item)
        g.check(*item);self.assertEqual(item,expected)
    def test_blob(self):
        self.assertEqual(g.blob(b'hello'),'b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0')
    def test_duplicate_json_key(self):
        with self.assertRaises(ValueError): json.loads('{"x":1,"x":2}',object_pairs_hook=g.unique_pairs)
    def test_missing_checkout(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertIn('AUTHENTIC_CHECKOUT_MISSING',g.audit(d)['errors'])
    def test_cli_never_passes_release(self):
        with tempfile.TemporaryDirectory() as d:
            p=subprocess.run([sys.executable,g.__file__,'--repo-root',d],capture_output=True,text=True)
            self.assertEqual(p.returncode,2)
            self.assertEqual(json.loads(p.stdout)['status'],'INVALID_HARD_HOLD')
    def test_invalid_inputs(self):
        self.assertEqual(g.check(None,'',{})['errors'],['BAD_INPUT'])
    def test_origin_field_is_stable(self):
        r=g.check(*fixture())
        self.assertEqual(r['occurrences'][0]['origins'][0]['origin'],'start')
    def test_source_index_rows(self):
        self.assertEqual(len(g.source_index({'start':[{'id':'x'}]})['x']),1)
    def test_source_rows_not_list(self):
        with self.assertRaises(ValueError):g.source_index({'start':{}})
    def test_bad_source_record(self):
        with self.assertRaises(ValueError):g.source_index({'start':[None]})


# One independently enumerated test per mutation, each checks exact threat class.
MUTATIONS = [
 ('published',lambda m,b,s:(m['status'].__setitem__('publish','published'),b),'UNAPPROVED_PUBLICATION_STATE', 'errors'),
 ('public',lambda m,b,s:(m['status'].__setitem__('publish','public'),b),'UNAPPROVED_PUBLICATION_STATE','errors'),
 ('no_status',lambda m,b,s:(m.pop('status'),b),'UNAPPROVED_PUBLICATION_STATE','errors'),
 ('approved_safety',lambda m,b,s:(m['safety_review'].__setitem__('state','approved'),b),'HUMAN_SAFETY_STATE_EVIDENCE_REQUIRED:approved','review'),
 ('not_required',lambda m,b,s:(m['safety_review'].__setitem__('state','not-required'),b),'HUMAN_SAFETY_STATE_EVIDENCE_REQUIRED:not-required','review'),
 ('no_safety',lambda m,b,s:(m.pop('safety_review'),b),'UNAPPROVED_SAFETY_STATE','errors'),
 ('bad_slug',lambda m,b,s:(m.__setitem__('slug','../escape'),b),'BAD_SLUG','errors'),
 ('empty_slug',lambda m,b,s:(m.__setitem__('slug',''),b),'BAD_SLUG','errors'),
 ('source_use_missing',lambda m,b,s:(m.pop('source_use'),b),'SOURCE_USE_MISSING','errors'),
 ('use_not_dict',lambda m,b,s:(m.__setitem__('source_use','unknown'),b),'SOURCE_USE_MISSING','errors'),
 ('undeclared_a',lambda m,b,s:(m['source_use'].pop('src-a'),b),'CITED_BUT_UNDECLARED:src-a','errors'),
 ('undeclared_b',lambda m,b,s:(m['source_use'].pop('src-b'),b),'CITED_BUT_UNDECLARED:src-b','errors'),
 ('empty_claim_a',lambda m,b,s:(m['source_use'].__setitem__('src-a',''),b),'EMPTY_SOURCE_USE:src-a','errors'),
 ('empty_claim_b',lambda m,b,s:(m['source_use'].__setitem__('src-b','  '),b),'EMPTY_SOURCE_USE:src-b','errors'),
 ('claim_bool',lambda m,b,s:(m['source_use'].__setitem__('src-a',True),b),'EMPTY_SOURCE_USE:src-a','errors'),
 ('bad_claim_key',lambda m,b,s:(m['source_use'].__setitem__('SRC-A','claim'),b),'BAD_SOURCE_USE_ID','errors'),
 ('unused_declaration',lambda m,b,s:(m['source_use'].__setitem__('extra','unused'),b),'DECLARED_NOT_CITED:extra','review'),
 ('missing_register',lambda m,b,s:(s.pop('src-a'),b),'CITED_SOURCE_NOT_REGISTERED:src-a','errors'),
 ('missing_register_b',lambda m,b,s:(s.pop('src-b'),b),'CITED_SOURCE_NOT_REGISTERED:src-b','errors'),
 ('alias_same_id',lambda m,b,s:(s['src-a'].append(('shelter',3,copy.deepcopy(s['src-a'][0][2]))),b),'MULTI_ORIGIN_SOURCE_ID:src-a','review'),
 ('alias_other_id',lambda m,b,s:(s['src-b'].append(('base',4,copy.deepcopy(s['src-b'][0][2]))),b),'MULTI_ORIGIN_SOURCE_ID:src-b','review'),
 ('no_url',lambda m,b,s:(s['src-a'][0][2].pop('url'),b),'INVALID_SOURCE_URL:src-a','errors'),
 ('http_url',lambda m,b,s:(s['src-a'][0][2].__setitem__('url','http://bad.test'),b),'INVALID_SOURCE_URL:src-a','errors'),
 ('blank_url',lambda m,b,s:(s['src-a'][0][2].__setitem__('url',''),b),'INVALID_SOURCE_URL:src-a','errors'),
 ('url_number',lambda m,b,s:(s['src-a'][0][2].__setitem__('url',7),b),'INVALID_SOURCE_URL:src-a','errors'),
 ('no_support',lambda m,b,s:(s['src-a'][0][2].pop('supports'),b),'UNSUPPORTED_READING_SCOPE:src-a','review'),
 ('blank_support',lambda m,b,s:(s['src-b'][0][2].__setitem__('supports',''),b),'UNSUPPORTED_READING_SCOPE:src-b','review'),
 ('support_numeric',lambda m,b,s:(s['src-a'][0][2].__setitem__('supports',3),b),'UNSUPPORTED_READING_SCOPE:src-a','review'),
 ('no_verified_date',lambda m,b,s:(s['src-b'][0][2].pop('verified_on'),b),'NO_VERIFICATION_DATE:src-b','review'),
 ('null_verified_date',lambda m,b,s:(s['src-a'][0][2].__setitem__('verified_on',None),b),'NO_VERIFICATION_DATE:src-a','review'),
 ('human_false_a',lambda m,b,s:(s['src-a'][0][2].__setitem__('human_link_check',False),b),'HUMAN_LINK_CHECK_PENDING:src-a','review'),
 ('human_false_b',lambda m,b,s:(s['src-b'][0][2].__setitem__('human_link_check',False),b),'HUMAN_LINK_CHECK_PENDING:src-b','review'),
 ('human_missing',lambda m,b,s:(s['src-a'][0][2].pop('human_link_check'),b),'HUMAN_LINK_CHECK_PENDING:src-a','review'),
 ('unknown_citation',lambda m,b,s:(None,b+' {{cite:missing}}'),'CITED_BUT_UNDECLARED:missing','errors'),
 ('malformed_citation',lambda m,b,s:(None,b+' {{cite:src-a}'),'MALFORMED_CITATION_TOKEN','errors'),
 ('malformed_citation2',lambda m,b,s:(None,b+' {{cite:src-a }}'),'MALFORMED_CITATION_TOKEN','errors'),
 ('malformed_citation3',lambda m,b,s:(None,b+' {{cite:}}'),'MALFORMED_CITATION_TOKEN','errors'),
 ('reordered_keys',lambda m,b,s:(m.__setitem__('source_use',{'src-b':'B','src-a':'A'}),b),None,None),
 ('repeated_a',lambda m,b,s:(None,b+' {{cite:src-a}}'),None,None),
 ('repeated_b',lambda m,b,s:(None,b+' {{cite:src-b}}'),None,None),
]


def case(name, mutate, expected, level):
    def test(self):
        m,b,s=fixture()
        result=mutate(m,b,s)
        if isinstance(result,tuple):
            b=result[1]
        found=g.check(m,b,s)
        if expected:
            self.assertIn(expected,found[level],(name,found))
        else:
            self.assertEqual(found['errors'],[],(name,found))
    return test
for name, mutate, expected, level in MUTATIONS:
    setattr(Fixed,'test_case_'+name,case(name,mutate,expected,level))


if __name__=='__main__': unittest.main()
