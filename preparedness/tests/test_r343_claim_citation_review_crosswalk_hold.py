"""R343 hostile/positive pure tests; artificial evidence NEVER qualifies QD."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import tempfile
import unittest

from preparedness.tools import r343_claim_citation_review_crosswalk_hold as m


def meta(slug='sample-emergency-plan', sources=None):
    return {'slug':slug,'status':{'editorial':'drafted','publish':'draft'},
            'safety_review':{'state':'pending','reviewer':None},
            'source_use':sources if sources is not None else {
                'ready-plan':'Specific claim reference, independently unreviewed.',
                'cdc-water':'Separate operational source, unreviewed.'}}


TEXT = 'Families should have a written emergency contact plan and periodically review it.'
HTML = '<h2 id="plan">The household plan</h2><p>'+TEXT+'{{cite:ready-plan}}</p>'


class ClaimTickets(unittest.TestCase):
    def check(self, html=HTML, metadata=None, ids=None):
        return m.analyze_entry('articles','sample-emergency-plan',html,meta() if metadata is None else metadata,
                               {'ready-plan','cdc-water'} if ids is None else ids)

    def test_basic_ticket_hard_hold(self):
        r=self.check()
        self.assertEqual(r['errors'],[])
        self.assertEqual(len(r['tickets']),1)
        self.assertEqual(r['tickets'][0]['heading'],'plan')
        self.assertEqual(r['tickets'][0]['human_claim_source_adjudication'],'UNREVIEWED_REQUIRED')
        self.assertEqual(r['tickets'][0]['citation_meaning'],m.CITED_SOURCE_NOTE)
    def test_repeat_is_deterministic(self):
        self.assertEqual(self.check(),self.check())
    def test_immutable_under_source_order(self):
        d=meta();d['source_use']=dict(reversed(list(d['source_use'].items())))
        self.assertEqual(self.check()['tickets'],self.check(metadata=d)['tickets'])
    def test_heading_captured(self):
        r=self.check('<h2 id="state-specific">Emergency guidance</h2><li>'+TEXT+'{{cite:ready-plan}}</li>')
        self.assertEqual(r['tickets'][0]['heading'],'state-specific')
    def test_heading_without_id_uses_text(self):
        r=self.check('<h2>State specific <em>review</em></h2><p>'+TEXT+'{{cite:ready-plan}}</p>')
        self.assertEqual(r['tickets'][0]['heading'],'State specific review')
    def test_unheaded_keeps_status(self):
        self.assertEqual(self.check('<p>'+TEXT+'{{cite:ready-plan}}</p>')['tickets'][0]['heading'],'unheaded')
    def test_html_entities_normalized(self):
        r=self.check('<p>Names &amp; phone numbers must be treated carefully.{{cite:ready-plan}}</p>')
        self.assertIn('Names & phone',r['tickets'][0]['excerpt'])
    def test_citation_not_in_excerpt(self):
        self.assertNotIn('{{cite:',self.check()['tickets'][0]['excerpt'])
    def test_full_text_not_stored(self):
        big='x '*500
        r=self.check('<p>'+big+'{{cite:ready-plan}}</p>')
        self.assertEqual(len(r['tickets'][0]['excerpt']),420)
        self.assertGreater(r['tickets'][0]['full_text_utf8_length'],420)
    def test_source_use_digest_is_stable(self):
        r=self.check()
        self.assertEqual(r['tickets'][0]['source_use_sha256'],m.fingerprint(meta()['source_use']['ready-plan']))
    def test_source_rationale_changes_digest(self):
        d=meta();d['source_use']['ready-plan']='Updated research statement'
        self.assertNotEqual(self.check()['tickets'][0]['source_use_sha256'],self.check(metadata=d)['tickets'][0]['source_use_sha256'])
    def test_source_rationale_does_not_automatically_approve(self):
        d=meta();d['source_use']['ready-plan']='A qualified reviewer approved this, trust me.'
        self.assertEqual(self.check(metadata=d)['tickets'][0]['human_claim_source_adjudication'],'UNREVIEWED_REQUIRED')
    def test_empty_rationale_rejected(self):
        d=meta();d['source_use']['ready-plan']=' \t '
        self.assertTrue(any('EMPTY_SOURCE_USE_RATIONALE' in x for x in self.check(metadata=d)['errors']))
    def test_missing_metadata_id_rejected(self):
        d=meta();del d['source_use']['ready-plan']
        self.assertTrue(any('CITED_SOURCE_NOT_DECLARED' in x for x in self.check(metadata=d)['errors']))
    def test_missing_catalog_id_rejected(self):
        self.assertTrue(any('CITED_SOURCE_NOT_IN_NATIVE_REGISTER' in x for x in self.check(ids={'cdc-water'})['errors']))
    def test_none_catalog_allowed_only_for_synthetic(self):
        self.assertEqual(m.analyze_entry('articles','sample-emergency-plan',HTML,meta(),None)['errors'],[])
    def test_uncited_declarations_are_reported(self):
        self.assertEqual(self.check()['unused_source_use'],['cdc-water'])
    def test_two_citations_one_block(self):
        s=TEXT+'{{cite:ready-plan}}{{cite:cdc-water}}'
        r=self.check('<p>'+s+'</p>')
        self.assertEqual([x['source_id'] for x in r['tickets']],['ready-plan','cdc-water'])
        self.assertEqual([x['citation_ordinal'] for x in r['tickets']],[0,1])
        self.assertNotEqual(r['tickets'][0]['ticket_id'],r['tickets'][1]['ticket_id'])
    def test_two_blocks_one_source_unique(self):
        r=self.check('<p>'+TEXT+'{{cite:ready-plan}}</p><p>'+TEXT+'{{cite:ready-plan}}</p>')
        self.assertEqual(len(r['tickets']),2)
        self.assertEqual(len({t['ticket_id'] for t in r['tickets']}),2)
    def test_reorder_changes_block_locator(self):
        base='<p>'+TEXT+'{{cite:ready-plan}}</p>'
        r1=self.check(base)['tickets'][0]['ticket_id']
        r2=self.check('<p>Additional paragraph without a citation.</p>'+base)['tickets'][0]['ticket_id']
        self.assertNotEqual(r1,r2)
    def test_same_block_markup_preserves_plain_text_hash(self):
        a=self.check()['tickets'][0]['claim_text_sha256']
        b=self.check('<p>Families should have a written <strong>emergency contact plan</strong> and periodically review it.{{cite:ready-plan}}</p>')['tickets'][0]['claim_text_sha256']
        self.assertEqual(a,b)
    def test_unrendered_script_rejected(self):
        r=self.check('<script>'+TEXT+'{{cite:ready-plan}}</script><p>'+TEXT+'</p>')
        self.assertIn('CITATION_TOKEN_IN_SCRIPT_STYLE_OR_INPUT',r['errors'])
    def test_unrendered_style_rejected(self):
        self.assertIn('CITATION_TOKEN_IN_SCRIPT_STYLE_OR_INPUT',self.check('<style>{{cite:ready-plan}}</style>')['errors'])
    def test_unrendered_textarea_rejected(self):
        self.assertIn('CITATION_TOKEN_IN_SCRIPT_STYLE_OR_INPUT',self.check('<textarea>{{cite:ready-plan}}</textarea>')['errors'])
    def test_attribute_cite_rejected(self):
        self.assertIn('CITATION_TOKEN_IN_HTML_ATTRIBUTE',self.check('<p title="{{cite:ready-plan}}">'+TEXT+'</p>')['errors'])
    def test_comment_cite_rejected(self):
        self.assertIn('CITATION_HIDDEN_IN_HTML_COMMENT',self.check('<!-- {{cite:ready-plan}} --><p>'+TEXT+'</p>')['errors'])
    def test_outside_block_cite_rejected(self):
        self.assertIn('CITATION_NOT_IN_CLAIM_BLOCK',self.check('<div>'+TEXT+'{{cite:ready-plan}}</div>')['errors'])
    def test_heading_cite_rejected(self):
        self.assertIn('CITATION_NOT_IN_CLAIM_BLOCK',self.check('<h2>'+TEXT+'{{cite:ready-plan}}</h2>')['errors'])
    def test_malformed_no_braces_rejected(self):
        self.assertIn('MALFORMED_OR_SPLIT_CITATION_TOKEN',self.check('<p>'+TEXT+'{{cite:ready-plan}</p>')['errors'])
    def test_bad_uppercase_citation_rejected(self):
        self.assertIn('MALFORMED_OR_SPLIT_CITATION_TOKEN',self.check('<p>'+TEXT+'{{Cite:READY}}</p>')['errors'])
    def test_missing_body_citations_rejected(self):
        self.assertIn('NO_VISIBLE_CLAIM_CITATIONS:sample-emergency-plan',self.check('<p>'+TEXT+'</p>')['errors'])
    def test_empty_claim_rejected(self):
        r=self.check('<p>{{cite:ready-plan}}</p>')
        self.assertTrue(any('CITATION_WITHOUT_VISIBLE_CLAIM' in x for x in r['errors']))
    def test_too_short_context_rejected(self):
        r=self.check('<p>Hi {{cite:ready-plan}}</p>')
        self.assertTrue(any('CITED_BLOCK_TOO_SHORT_FOR_CONTEXT' in x for x in r['errors']))
    def test_long_claim_hash_changes_on_edit(self):
        a=self.check()['tickets'][0]['claim_text_sha256']
        b=self.check(HTML.replace('periodically','regularly'))['tickets'][0]['claim_text_sha256']
        self.assertNotEqual(a,b)
    def test_nested_block_not_double_counted(self):
        r=self.check('<ul><li><p>'+TEXT+'{{cite:ready-plan}}</p></li></ul>')
        self.assertEqual(r['citation_occurrences'],1)
        self.assertEqual(len(r['tickets']),1)
    def test_tag_path_protected(self):
        self.assertIn('INVALID_KIND_OR_SLUG',m.analyze_entry('articles','../secrets',HTML,meta())['errors'])
    def test_titlecase_slug_protected(self):
        self.assertIn('INVALID_KIND_OR_SLUG',m.analyze_entry('articles','Family',HTML,meta())['errors'])
    def test_unsupported_kind_protected(self):
        self.assertIn('INVALID_KIND_OR_SLUG',m.analyze_entry('page','sample-emergency-plan',HTML,meta())['errors'])
    def test_missing_source_use_rejected(self):
        d=meta();del d['source_use'];self.assertIn('SOURCE_USE_DECLARATIONS_REQUIRED',self.check(metadata=d)['errors'])
    def test_non_object_source_use_rejected(self):
        d=meta();d['source_use']=[];self.assertIn('SOURCE_USE_DECLARATIONS_REQUIRED',self.check(metadata=d)['errors'])
    def test_metadata_slug_collision_rejected(self):
        d=meta();d['slug']='another-plan';self.assertTrue(any('ORIGINAL_DRAFT_IDENTITY_OR_STATE_CHANGED' in x for x in self.check(metadata=d)['errors']))
    def test_published_state_rejected(self):
        d=meta();d['status']['publish']='published';self.assertTrue(any('ORIGINAL_DRAFT_IDENTITY_OR_STATE_CHANGED' in x for x in self.check(metadata=d)['errors']))
    def test_unrecognized_review_state_rejected(self):
        d=meta();d['safety_review']['state']='QD_PASS';self.assertTrue(any('UNRECOGNIZED_SAFETY_REVIEW_STATE' in x for x in self.check(metadata=d)['errors']))
    def test_approved_metadata_does_not_approve_crosswalk(self):
        d=meta();d['safety_review']['state']='approved'
        self.assertEqual(self.check(metadata=d)['tickets'][0]['human_claim_source_adjudication'],'UNREVIEWED_REQUIRED')
    def test_report_always_hard_hold(self):
        r=m.report([])
        self.assertEqual(r['state'],'DRAFT_HARD_HOLD')
        for k,v in m.HOLD_FIELDS.items():self.assertEqual(r[k],v)
    def test_report_errors_invalid(self):
        self.assertEqual(m.report(['unsafe'])['state'],'INVALID_HARD_HOLD')
    def test_report_no_fake_revenue(self):
        r=m.report([]);self.assertFalse(r['paid_orders_verified']);self.assertFalse(r['realized_net_revenue_verified'])
    def test_report_preserves_original_conflicts(self):
        r=m.report([])
        self.assertEqual((r['original_legacy_editorial_conflicts_remaining'],r['original_article15_tool104_review_obligations_remaining']),(15,17))
    def test_missing_native_checkout_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            r=m.audit_native(Path(d));self.assertEqual(r['state'],'INVALID_HARD_HOLD')
            self.assertTrue(any('R337_41_ENTRY_PINNED_GIT' in x for x in r['errors']))
    def test_ticket_does_not_contain_full_text(self):
        long='family emergency contact plan '*200
        t=self.check('<p>'+long+'{{cite:ready-plan}}</p>')['tickets'][0]
        self.assertNotIn(long,t.values())
    def test_link_token_not_a_citation(self):
        r=self.check('<p>'+TEXT+'{{link:other-article|Read more}}{{cite:ready-plan}}</p>')
        self.assertEqual(len(r['tickets']),1)
    def test_source_catalog_is_not_fabricated_in_report(self):
        self.assertEqual(m.report([])['source_catalog'],{})
    def test_html_line_preserved(self):
        self.assertEqual(self.check('<h2>Header</h2>\n\n<p>'+TEXT+'{{cite:ready-plan}}</p>')['tickets'][0]['html_line'],3)
    def test_block_tag_captured(self):
        self.assertEqual(self.check('<li>'+TEXT+'{{cite:ready-plan}}</li>')['tickets'][0]['block_tag'],'li')
    def test_malformed_blocks_rejected(self):
        self.assertIn('UNCLOSED_CLAIM_BLOCK',self.check('<p>'+TEXT+'{{cite:ready-plan}}')['errors'])
    def test_plaintext_entropy_remains_unverified(self):
        r=self.check()
        self.assertEqual(r['tickets'][0]['citation_meaning'],m.CITED_SOURCE_NOTE)


class SourceCatalog(unittest.TestCase):
    def build(self, register=None, fragments=None):
        td=tempfile.TemporaryDirectory();base=Path(td.name);(base/'sources/fragments').mkdir(parents=True)
        (base/'sources/register.json').write_text(json.dumps({'sources':register if register is not None else [
            {'id':'ready-plan','url':'https://example.gov/plan','verified_on':None,'human_link_check':False}]}))
        for name,items in (fragments if fragments is not None else {'safety.json':[
            {'id':'cdc-water','url':'https://example.gov/water','verified_on':'2026-10-20','human_link_check':False}]}).items():
            (base/'sources/fragments'/name).write_text(json.dumps({'sources':items}))
        return td,base
    def test_basic_catalog(self):
        td,base=self.build()
        try:
            catalog,errors=m._source_catalog(base)
            self.assertEqual(errors,[])
            self.assertEqual(set(catalog),{'ready-plan','cdc-water'})
        finally:td.cleanup()
    def test_placeholder_upgrade_allowed_but_not_claim_pass(self):
        td,base=self.build(fragments={'upgrade.json':[
            {'id':'ready-plan','verified_on':'2026-11-01','human_link_check':False}]})
        try:
            catalog,errors=m._source_catalog(base)
            self.assertEqual(errors,[])
            self.assertFalse(catalog['ready-plan']['human_link_check'])
        finally:td.cleanup()
    def test_verified_source_duplicate_rejected(self):
        td,base=self.build(register=[{'id':'ready-plan','verified_on':'2026-10-01'}],fragments={'override.json':[
            {'id':'ready-plan','verified_on':'2026-11-01'}]})
        try:self.assertTrue(any('UNSAFE_DUPLICATE_OR_DOWNGRADE' in x for x in m._source_catalog(base)[1]))
        finally:td.cleanup()
    def test_unverified_duplicate_rejected(self):
        td,base=self.build(fragments={'override.json':[{'id':'ready-plan','verified_on':None}]})
        try:self.assertTrue(any('UNSAFE_DUPLICATE_OR_DOWNGRADE' in x for x in m._source_catalog(base)[1]))
        finally:td.cleanup()
    def test_source_path_traversal_id_rejected(self):
        td,base=self.build(register=[{'id':'../secret','verified_on':None}])
        try:self.assertTrue(any('INVALID_SOURCE_CATALOG_ID' in x for x in m._source_catalog(base)[1]))
        finally:td.cleanup()
    def test_malformed_fragment_rejected(self):
        td,base=self.build()
        try:
            (base/'sources/fragments/safety.json').write_text('not-json')
            self.assertTrue(any('INVALID_SOURCE_REGISTER_FRAGMENT' in x for x in m._source_catalog(base)[1]))
        finally:td.cleanup()
    def test_missing_fragment_rejected(self):
        td,base=self.build(fragments={})
        try:self.assertIn('MISSING_NATIVE_SOURCE_REGISTER_OR_FRAGMENTS',m._source_catalog(base)[1])
        finally:td.cleanup()
    def test_symlink_source_rejected(self):
        td,base=self.build()
        try:
            f=base/'sources/fragments/safety.json';f.unlink();f.symlink_to(base/'sources/register.json')
            self.assertTrue(any('SYMLINK_OR_MISSING_SOURCE_RECORD' in x for x in m._source_catalog(base)[1]))
        finally:td.cleanup()
    def test_no_actual_http_checks_claimed(self):
        td,base=self.build()
        try:
            catalog,_=m._source_catalog(base)
            self.assertNotIn('claim_support_verified',catalog['ready-plan'])
        finally:td.cleanup()


class RiskHints(unittest.TestCase):
    def test_risk_hints_are_labels_not_decisions(self):
        for hint, sentence in [
            ('emergency-dispatch','Call 911 only for emergencies and discuss the jurisdiction.'),
            ('child-reunification','Plan school pickup arrangements with the authorized guardian.'),
            ('medicine-and-devices','Keep refrigerated medicine under the prescriber guidance.'),
            ('water-and-chemicals','Chemical contamination and drinking water need local authority guidance.'),
            ('food-preservation','Use tested canning procedures and food preservation sources.'),
            ('fire-and-power','A generator and carbon monoxide present a life safety issue.'),
            ('evacuation-and-shelter','Shelter instructions and evacuation rules vary with the incident.'),
            ('privacy','Do not put medical information on a public contact card.')]:
            with self.subTest(hint=hint):
                body='<p>'+sentence+'{{cite:ready-plan}}</p>'
                r=m.analyze_entry('articles','sample-emergency-plan',body,meta(),{'ready-plan'})
                self.assertIn(hint,r['tickets'][0]['risk_hints_not_safety_findings'])
                self.assertEqual(r['tickets'][0]['human_claim_source_adjudication'],'UNREVIEWED_REQUIRED')
    def test_no_risk_hint_does_not_mean_safe(self):
        r=m.analyze_entry('articles','sample-emergency-plan','<p>Maintain a simple paper reference for your family.{{cite:ready-plan}}</p>',meta(),{'ready-plan'})
        self.assertEqual(r['tickets'][0]['risk_hints_not_safety_findings'],[])
        self.assertEqual(r['tickets'][0]['human_claim_source_adjudication'],'UNREVIEWED_REQUIRED')


if __name__ == '__main__':unittest.main()
