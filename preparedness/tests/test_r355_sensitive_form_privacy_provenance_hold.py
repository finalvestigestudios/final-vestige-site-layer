"""Adversarial, local/synthetic fixtures only; never replace native/QD tests."""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import r355_sensitive_form_privacy_provenance_hold as gate


FORM = '''<section><p>Private by design: what you type stays on this page. It is not sent or saved. Closing the tab clears it.{{cite:shelter-ready-plan}}</p>
<form id="rc" onsubmit="return false"><input id="rc-name" type="text" autocomplete="off">
%s</form><script>{{inline-js:shelter_common.js}}{{inline-js:reunion_card.js}}</script></section>''' % ''.join('<input id="rc-field%d" type="text" autocomplete="off">' % i for i in range(10))


def fixture():
    docs = {}
    for i in range(35):
        slug = 'article-%02d' % i
        docs[slug] = {'body': '<p>Guide{{cite:agency-one}}</p>', 'meta': {'slug':slug, 'status':{'publish':'draft'},
                'safety_review':{'state':'pending'}, 'source_use':{'agency-one':'Research reference'}, 'kind':'article'}}
    tools = ['family-reunification-card', 'water-planner', 'home-fire-escape-worksheet', 'power-outage-planner','reunification-plan','kit-builder']
    for slug in tools:
        body = FORM if slug == 'family-reunification-card' else '<form><input name="field"></form>'
        docs[slug] = {'body': body, 'meta': {'slug':slug, 'kind':'tool', 'status':{'publish':'draft'},
             'safety_review':{'state':'pending'}, 'source_use': {'shelter-ready-plan':'Research citation'},
             'description': 'Nothing is stored. Local-only' if slug == tools[0] else 'Free field worksheet',
             'dek': 'Runs locally' if slug == tools[0] else 'Practical worksheet', 'tags':['Printable']}}
    taxonomy = {'tools': [{'slug':s,'status':'drafted-pending-safety-review'} for s in tools] +
                  [{'slug':s,'status':'not-started'} for s in ['pantry-worksheet','checklists','offline-reference']],
                'sections': [{'slug':'field-tools','blurb':'Free forms that keep your information on your device.'}]}
    return docs, taxonomy


class TestCore(unittest.TestCase):
    def setUp(self):
        self.docs, self.tax = fixture()

    def res(self):
        return gate.review(self.docs, self.tax)

    def test_safe_fixture_is_review_hold_not_approval(self):
        self.assertEqual(self.res()['status'], 'PRIVACY_PROVENANCE_REVIEW_REQUIRED_HARD_HOLD')

    def test_review_always_no_publish(self):
        self.assertIs(self.res()['may_publish'], False)

    def test_review_always_no_merge(self):
        self.assertIs(self.res()['may_merge'], False)

    def test_review_always_not_medical_clear(self):
        self.assertIs(self.res()['qualified_qd_pass'], False)

    def test_review_never_certifies_browser_network(self):
        self.assertIs(self.res()['browser_network_safety_verified'], False)

    def test_review_never_certifies_print(self):
        self.assertIs(self.res()['print_accessibility_verified'], False)

    def test_review_never_certifies_child_card(self):
        self.assertIs(self.res()['child_card_safe'], False)

    def test_review_never_certifies_purchase(self):
        self.assertIs(self.res()['verified_paid_orders'], False)

    def test_private_copy_is_not_disclosed(self):
        self.assertNotIn('Closing the tab', json.dumps(self.res()))

    def test_source_text_is_hashed(self):
        self.assertEqual(len(self.res()['input_form_dockets'][0]['source_body_sha256']), 64)

    def test_invalid_documents_list(self):
        self.assertEqual(gate.review([], self.tax)['status'],'INVALID_HARD_HOLD')

    def test_invalid_taxonomy_list(self):
        self.assertEqual(gate.review(self.docs, [])['status'],'INVALID_HARD_HOLD')

    def test_bad_document_key_fails_closed(self):
        self.docs[99] = self.docs.pop('article-02')
        self.assertEqual(self.res()['status'], 'INVALID_HARD_HOLD')

    def test_bad_tool_plan_slug_array_fails_closed(self):
        self.tax['tools'][0]['slug'] = ['nested']
        self.assertEqual(self.res()['status'], 'INVALID_HARD_HOLD')

    def test_bad_tool_plan_slug_dict_fails_closed(self):
        self.tax['tools'][0]['slug'] = {'x': 1}
        self.assertEqual(self.res()['status'], 'INVALID_HARD_HOLD')

    def test_bad_tool_plan_none_fails_closed(self):
        self.tax['tools'][0]['slug'] = None
        self.assertEqual(self.res()['status'], 'INVALID_HARD_HOLD')

    def test_bad_baseline_key_fails_closed(self):
        self.assertEqual(gate.review(self.docs, self.tax, baseline={None:{}})['status'],'INVALID_HARD_HOLD')

    def test_native_not_checkout(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(gate.native_review(Path(td))['status'], 'INVALID_HARD_HOLD')

    def test_git_blob_deterministic(self):
        self.assertEqual(gate.git_blob(b'abc'), hashlib.sha1(b'blob 3\0abc').hexdigest())

    def test_source_sha_deterministic(self):
        self.assertEqual(gate.sha256('abc'), hashlib.sha256(b'abc').hexdigest())

    def test_renders_citation_token_binding(self):
        self.assertEqual(gate.CITE.findall(FORM),['shelter-ready-plan'])

    def test_runtime_inline_dependencies(self):
        self.assertEqual(set(gate.INCLUDE.findall(FORM)), {'shelter_common.js','reunion_card.js'})

    def test_taxonomy_promise_docket(self):
        self.assertIn('taxonomy/field-tools', [d['slug'] for d in self.res()['input_form_dockets']])

    def test_another_form_is_reviewed(self):
        self.assertTrue(any(d['slug']=='water-planner' for d in self.res()['input_form_dockets']))

    def test_model_counts_all_41(self):
        self.assertEqual(self.res()['inspected_documents'], 41)

    def test_claim_dockets_deterministic(self):
        self.assertEqual(self.res(), self.res())

    def test_citations_within_unchanged_content(self):
        self.assertNotIn('UNDECLARED_BODY_SOURCE', ''.join(self.res()['errors']))

    def test_reject_baseline_change(self):
        original=self.docs['family-reunification-card']
        baseline={'family-reunification-card':{'body_sha256':gate.sha256(original['body']),
            'meta_sha256':gate.sha256(json.dumps(original['meta'], sort_keys=True,ensure_ascii=False))}}
        self.docs['family-reunification-card']['body']+=' changed'
        r=gate.review(self.docs,self.tax,baseline=baseline)
        self.assertIn('SOURCE_BODY_EDIT_REQUIRES_ADJUDICATION:family-reunification-card',r['errors'])

    def test_reject_meta_baseline_change(self):
        original=self.docs['family-reunification-card']
        baseline={'family-reunification-card':{'body_sha256':gate.sha256(original['body']),
            'meta_sha256':gate.sha256(json.dumps(original['meta'], sort_keys=True,ensure_ascii=False))}}
        self.docs['family-reunification-card']['meta']['description']='changed'
        self.assertIn('SOURCE_META_EDIT_REQUIRES_ADJUDICATION:family-reunification-card',
                      gate.review(self.docs,self.tax,baseline=baseline)['errors'])

    def test_unusable_baseline_rejected(self):
        self.assertEqual(gate.review(self.docs,self.tax,baseline=[])['status'],'INVALID_HARD_HOLD')

    def test_invalid_source_support_no_false_pass(self):
        self.docs['family-reunification-card']['meta']['source_use']={}
        self.assertEqual(self.res()['status'],'INVALID_HARD_HOLD')

    def test_absolute_privacy_claim_detection(self):
        entries = [p['claim'] for d in self.res()['input_form_dockets'] if d['slug']=='family-reunification-card' for p in d['privacy_claims']]
        self.assertIn('no_transmission',entries)
        self.assertIn('no_storage',entries)
        self.assertIn('closing_clears',entries)
        self.assertIn('local_guarantee',entries)

    def test_external_script_inventory_is_count_only(self):
        self.docs['water-planner']['body']='<form><input id="x"></form><script src="https://example.com/a.js"></script>'
        row=next(d for d in self.res()['input_form_dockets'] if d['slug']=='water-planner')
        self.assertEqual(row['external_script_count'],1)
        self.assertNotIn('example.com',str(row))

    def test_inline_event_handlers_not_approval(self):
        row=next(d for d in self.res()['input_form_dockets'] if d['slug']=='family-reunification-card')
        self.assertTrue(row['inline_handlers_present'])
        self.assertFalse(self.res()['browser_network_safety_verified'])


# Each independent scenario is a separate unittest test method, not a subtest count.
ERROR_CASES = {
 'missing_article': ('article-00', 'remove', 'ORIGINAL_41_DOCUMENT_INVENTORY_INCOMPLETE'),
 'missing_card': ('family-reunification-card', 'remove', 'TOOL104_FORM_NOT_FOUND'),
 'wrong_slug': ('article-02', 'meta_slug', 'SLUG_IDENTITY_DRIFT'),
 'published_article': ('article-04', 'publish', 'PUBLICATION_STATE_NOT_DRAFT'),
 'published_tool': ('water-planner', 'publish', 'PUBLICATION_STATE_NOT_DRAFT'),
 'approved_tool': ('kit-builder', 'review', 'SAFETY_REVIEW_STATE_UNACCEPTABLE'),
 'approved_card': ('family-reunification-card', 'review', 'SAFETY_REVIEW_STATE_UNACCEPTABLE'),
 'unknown_cite': ('article-03', 'cite', 'UNDECLARED_BODY_SOURCE'),
 'unregistered_card_cite': ('family-reunification-card', 'cite', 'UNDECLARED_BODY_SOURCE'),
 'empty_article': ('article-05', 'empty', 'BODY_EMPTY_OR_SOURCE_USE_MISSING'),
 'empty_tool': ('reunification-plan', 'empty', 'BODY_EMPTY_OR_SOURCE_USE_MISSING'),
 'invalid_source_use': ('article-06', 'source', 'BODY_EMPTY_OR_SOURCE_USE_MISSING'),
 'no_status': ('article-07', 'nostatus', 'PUBLICATION_STATE_NOT_DRAFT'),
 'no_safety': ('article-08', 'nosafety', 'SAFETY_REVIEW_STATE_UNACCEPTABLE'),
 'null_body': ('article-09', 'nullbody', 'BODY_OR_META_MISSING'),
 'null_meta': ('article-10', 'nullmeta', 'BODY_OR_META_MISSING'),
 'nested_meta_wrong': ('article-11', 'badmeta', 'SLUG_IDENTITY_DRIFT'),
 'lost_privacy_promise': ('family-reunification-card', 'promise', 'TOOL104_ORIGINAL_PROMISE_FINGERPRINT_CHANGED_REVIEW_REQUIRED'),
 'lost_runtime_dependency': ('family-reunification-card', 'include', 'TOOL104_INLINE_DEPENDENCY_CHANGED_REVIEW_REQUIRED'),
 'lost_form_fields': ('family-reunification-card', 'shortform', 'TOOL104_FORM_FIELDS_CHANGED_REVIEW_REQUIRED'),
 'unbalanced_form': ('water-planner', 'form', 'FORM_MARKUP_UNBALANCED'),
 'malformed_card_form': ('family-reunification-card', 'form', 'FORM_MARKUP_UNBALANCED'),
 'bad_tool_slug': ('kit-builder', 'meta_slug', 'SLUG_IDENTITY_DRIFT'),
 'bad_tool_status': ('power-outage-planner', 'nostatus', 'PUBLICATION_STATE_NOT_DRAFT'),
 'bad_tool_review': ('home-fire-escape-worksheet', 'nosafety', 'SAFETY_REVIEW_STATE_UNACCEPTABLE'),
}


def make_case(slug, op, expected):
    def check(self):
        docs,tax=fixture()
        obj=docs[slug]
        if op=='remove': del docs[slug]
        elif op=='meta_slug': obj['meta']['slug']='different-slug'
        elif op=='publish': obj['meta']['status']['publish']='published'
        elif op=='review': obj['meta']['safety_review']['state']='approved'
        elif op=='cite': obj['body']+='{{cite:unknown-reference}}'
        elif op=='empty': obj['body']=''
        elif op=='source': obj['meta']['source_use']=None
        elif op=='nostatus': obj['meta'].pop('status')
        elif op=='nosafety': obj['meta'].pop('safety_review')
        elif op=='nullbody': obj['body']=None
        elif op=='nullmeta': obj['meta']=None
        elif op=='badmeta': obj['meta']['slug']=None
        elif op=='promise': obj['body']=obj['body'].replace('Closing the tab clears it.', 'Please manage private information.')
        elif op=='include': obj['body']=obj['body'].replace('{{inline-js:reunion_card.js}}','')
        elif op=='shortform': obj['body']=obj['body'].replace(''.join('<input id="rc-field%d" type="text" autocomplete="off">' % i for i in range(10)), '')
        elif op=='form': obj['body']+='<form>'
        result=gate.review(docs,tax)
        self.assertEqual(result['status'],'INVALID_HARD_HOLD')
        self.assertTrue(any(x.startswith(expected) for x in result['errors']), result['errors'])
    return check


class TestMutations(unittest.TestCase):
    pass

for case_name, args in ERROR_CASES.items():
    setattr(TestMutations, 'test_'+case_name, make_case(*args))


if __name__ == '__main__':
    unittest.main()
