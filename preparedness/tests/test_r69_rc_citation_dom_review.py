"""R69: isolated deterministic synthetic and adversarial tests, no network/writes."""
from __future__ import annotations
from copy import deepcopy
import csv
import importlib.util
import io
from pathlib import Path
import unittest

TOOL=Path(__file__).resolve().parents[1] / 'tools' / 'r69_rc_citation_dom_review.py'
spec=importlib.util.spec_from_file_location('r69_dom_audit_test',TOOL)
gate=importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
N=(2,2,3,3,4)


def reseal(obj):
    obj.pop('fingerprint_sha256',None)
    obj['fingerprint_sha256']=gate.digest(obj)
    return obj


def task(kind,slug,html,sid):
    citations=[{
        'ordinal':i,'source_id':m.group(1),
        'unicode_codepoint_offset_in_candidate_html':m.start(),
        'exact_citation_token':m.group(0),
        'human_claim_support':'NOT_REVIEWED',
        'scoped_candidate_source_identity_OR_NULL':['base',sid],
        'all_possible_origin_and_id_pairs_NOT_MERGED':[['base',sid]],
    } for i,m in enumerate(gate.CITE.finditer(html),1)]
    row={
        'kind':kind, 'slug':slug,
        'proposed_WordPress_url_DRAFT_ONLY':'/preparedness/field-tools/'+slug+'/',
        'RC_metadata_UNABRIDGED_NOT_SAFETY_CLEARED':{'status':{'publish':'draft'}},
        'RC_body_HTML_UNABRIDGED_NOT_SAFETY_CLEARED':html,
        'RC_body_utf8_sha256':gate.raw_sha(html),
        'all_RC_citation_occurrences_NOT_CLAIM_SUPPORT':citations,
        'review_flags_NOT_SAFETY_VERDICTS':[],
        'human_claim_review':'NOT_REVIEWED',
        'human_source_review':'NOT_REVIEWED',
        'qualified_safety_review':'NOT_REVIEWED',
        'independent_QD_review':'NOT_REVIEWED',
    }
    row['task_sha256']=gate.digest(row)
    return row


def parent_fixture():
    docs=[
      task('article','a-guide','<h2 id="water">Water safety</h2>\n<p>Water advice {{cite:s1}} for readers.</p>','s1'),
      task('article','b-guide','<p>Medicine and storage {{cite:s2}} matter.</p>','s2'),
      task('tool','water-planner','<div><p>Planning {{cite:s1}} today.</p></div>','s1'),
      task('tool','quick-card','<ul><li>Go now {{cite:s3}}</li></ul>','s3')]
    r={'schema':gate.PARENT_SCHEMA,'release_state':'HOLD','machine_only':True,
       'counts':{'original_articles_conserved':2,'candidate_tools':2,
         'original_citations_preserved_under_R66':3,
         'candidate_sources_conserved_under_R67':3,
         'RC_citation_occurrences_UNREVIEWED':4,
         'human_source_or_claim_checks_performed_BY_R68':0},
       'RC_git_commit_sha256_NOT_RELEASE_APPROVAL':'ddb3528ba6494dada1fa1c3a142ce746e3a67706',
       'all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED':docs,
       **{k:False for k in gate.HOLD}}
    return reseal(r)


def rebuild_doc(parent, idx, body):
    old=parent['all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED'][idx]
    sid=old['all_RC_citation_occurrences_NOT_CLAIM_SUPPORT'][0]['source_id']
    updated=task(old['kind'],old['slug'],body,sid)
    parent['all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED'][idx]=updated
    parent['counts']['RC_citation_occurrences_UNREVIEWED']=sum(len(x['all_RC_citation_occurrences_NOT_CLAIM_SUPPORT']) for x in parent['all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED'])
    reseal(parent)
    return parent


def run(parent=None,expected=N):
    return gate.construct(parent if parent is not None else parent_fixture(),expected=expected)


class CoreCases(unittest.TestCase):
    def setUp(self):
        self.parent=parent_fixture()

    def test_hold_and_census(self):
        p=run(self.parent)
        self.assertEqual(p['schema'],gate.SCHEMA)
        self.assertEqual(p['counts']['candidate_citation_occurrences_accounted_for'],4)
        self.assertFalse(p['may_publish'])
        self.assertEqual(p['counts']['human_claim_or_safety_checks_performed_BY_R69'],0)

    def test_repeat_bitwise_determinism(self):
        self.assertEqual(run(self.parent),run(self.parent))

    def test_sealed_output_integrity(self):
        p=run(self.parent)
        self.assertEqual(p['fingerprint_sha256'],gate.digest({k:v for k,v in p.items() if k!='fingerprint_sha256'}))

    def test_full_text_and_all_citations_preserved(self):
        p=run(self.parent)
        self.assertEqual(sum(len(x['citation_visibility_audit_NOT_BROWSER_PROOF']) for x in p['all_document_DOM_text_and_citation_review_orders_NOT_APPROVED']),4)
        full_text=''.join(x['DOM_TEXT_UNABRIDGED_NOT_BROWSER_VERIFIED'] for d in p['all_document_DOM_text_and_citation_review_orders_NOT_APPROVED'] for x in d['full_DOM_text_blocks_UNABRIDGED_NOT_SOURCE_APPROVED'])
        self.assertIn('Medicine and storage',full_text)

    def test_mixed_nested_text_block_and_keyword_topic(self):
        p=run(self.parent)
        first=next(x for x in p['all_document_DOM_text_and_citation_review_orders_NOT_APPROVED'] if x['slug']=='a-guide')
        blocks=first['full_DOM_text_blocks_UNABRIDGED_NOT_SOURCE_APPROVED']
        self.assertTrue(any('WATER_SANITATION' in x['review_topic_signals_NOT_SAFETY_CLASSIFICATION'] for x in blocks))
        self.assertTrue(any('Water safety' in x['DOM_TEXT_UNABRIDGED_NOT_BROWSER_VERIFIED'] for x in blocks))

    def test_visible_data_default_is_not_browser_verified(self):
        rows=run(self.parent)['all_document_DOM_text_and_citation_review_orders_NOT_APPROVED']
        self.assertTrue(all(c['DOM_CLASSIFICATION_NOT_BROWSER_PROOF']=='DOM_TEXT_POTENTIALLY_VISIBLE_NOT_BROWSER_VERIFIED' for d in rows for c in d['citation_visibility_audit_NOT_BROWSER_PROOF']))

    def test_hazards_without_same_block_citation_triaged_not_condemned(self):
        p=run(self.parent)
        self.assertGreaterEqual(p['counts']['review_topic_blocks_without_same_block_citation'],1)
        self.assertFalse(p['qualified_safety_clearance'])

    def test_script_citation_suppressed(self):
        build=rebuild_doc(self.parent,0,'<script>const ref="{{cite:s1}}"</script>')
        p=run(build)
        self.assertEqual(p['counts']['citations_in_suppressed_or_a11y_hidden_DOM_text'],1)
        self.assertEqual(p['counts']['citations_in_potentially_visible_DOM_text'],3)

    def test_hidden_attribute_citation_suppressed(self):
        build=rebuild_doc(self.parent,0,'<p hidden>Hidden {{cite:s1}}</p>')
        self.assertEqual(run(build)['counts']['citations_in_suppressed_or_a11y_hidden_DOM_text'],1)

    def test_aria_hidden_citation_suppressed(self):
        build=rebuild_doc(self.parent,0,'<p aria-hidden="true">Hidden {{cite:s1}}</p>')
        self.assertEqual(run(build)['counts']['citations_in_suppressed_or_a11y_hidden_DOM_text'],1)

    def test_style_display_none_citation_suppressed(self):
        build=rebuild_doc(self.parent,0,'<div style="DISPLAY: none !important;"><p>{{cite:s1}}</p></div>')
        self.assertEqual(run(build)['counts']['citations_in_suppressed_or_a11y_hidden_DOM_text'],1)

    def test_style_visibility_hidden_citation_suppressed(self):
        build=rebuild_doc(self.parent,0,'<p style="visibility: hidden">{{cite:s1}}</p>')
        self.assertEqual(run(build)['counts']['citations_in_suppressed_or_a11y_hidden_DOM_text'],1)

    def test_inert_citation_suppressed(self):
        build=rebuild_doc(self.parent,0,'<div inert><p>{{cite:s1}}</p></div>')
        self.assertEqual(run(build)['counts']['citations_in_suppressed_or_a11y_hidden_DOM_text'],1)

    def test_template_citation_suppressed(self):
        build=rebuild_doc(self.parent,0,'<template>{{cite:s1}}</template>')
        self.assertEqual(run(build)['counts']['citations_in_suppressed_or_a11y_hidden_DOM_text'],1)

    def test_comment_citation_not_dom_data(self):
        build=rebuild_doc(self.parent,0,'<!-- {{cite:s1}} -->')
        self.assertEqual(run(build)['counts']['citations_outside_HTML_data_nodes'],1)

    def test_attribute_citation_not_dom_data(self):
        build=rebuild_doc(self.parent,0,'<div data-cite="{{cite:s1}}">No visible citation</div>')
        self.assertEqual(run(build)['counts']['citations_outside_HTML_data_nodes'],1)

    def test_all_citations_even_attribute_and_comment_conserved(self):
        build=rebuild_doc(self.parent,0,'<div data-cite="{{cite:s1}}"><!-- {{cite:s1}} --><p>{{cite:s1}}</p></div>')
        p=run(build,expected=(2,2,3,3,6))
        self.assertEqual(p['counts']['citations_outside_HTML_data_nodes'],2)
        self.assertEqual(p['counts']['candidate_citation_occurrences_accounted_for'],6)

    def test_unicode_codepoints_not_utf8_bytes(self):
        body='<p>🍋咖啡\nAnother line {{cite:s1}}</p>'
        build=rebuild_doc(self.parent,0,body)
        row=run(build)['all_document_DOM_text_and_citation_review_orders_NOT_APPROVED'][0]['citation_visibility_audit_NOT_BROWSER_PROOF'][0]
        self.assertEqual(row['unicode_codepoint_offset'],body.index('{{cite:s1}}'))

    def test_newlines_crlf_and_entities_keep_source_offsets(self):
        body='<p>First &amp; second\r\nLine 2 {{cite:s1}}</p>'
        build=rebuild_doc(self.parent,0,body)
        self.assertEqual(run(build)['counts']['citations_in_potentially_visible_DOM_text'],4)

    def test_void_self_closing_tags_do_not_hide_citation(self):
        build=rebuild_doc(self.parent,0,'<p><br/><img alt="icon">{{cite:s1}}</p>')
        self.assertEqual(run(build)['counts']['citations_in_potentially_visible_DOM_text'],4)

    def test_html_text_only_with_nested_strong(self):
        build=rebuild_doc(self.parent,0,'<p>Keep <strong>water</strong> {{cite:s1}}.</p>')
        d=run(build)['all_document_DOM_text_and_citation_review_orders_NOT_APPROVED'][0]
        self.assertTrue(any('Keep water' in b['DOM_TEXT_UNABRIDGED_NOT_BROWSER_VERIFIED'] for b in d['full_DOM_text_blocks_UNABRIDGED_NOT_SOURCE_APPROVED']))

    def test_csv_four_rows(self):
        rows=list(csv.DictReader(io.StringIO(gate.csv_tasks(run(self.parent)))))
        self.assertEqual(len(rows),4)
        self.assertEqual({x['human_review_state'] for x in rows},{'NOT_REVIEWED'})

    def test_csv_must_not_accept_modified_signature(self):
        report=run(self.parent);report['counts']['candidate_articles']=100
        with self.assertRaises(gate.ReviewHold):gate.csv_tasks(report)

    def test_csv_must_not_accept_publish_true_even_resealed(self):
        report=run(self.parent);report['may_publish']=True;reseal(report)
        with self.assertRaises(gate.ReviewHold):gate.csv_tasks(report)

    def test_csv_formula_escape_for_adversarial_slug(self):
        self.parent['all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED'][0]['slug']='=HYPERLINK("url")'
        target=self.parent['all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED'][0]
        target['task_sha256']=gate.digest({k:v for k,v in target.items() if k!='task_sha256'})
        reseal(self.parent)
        rows=list(csv.DictReader(io.StringIO(gate.csv_tasks(run(self.parent)))))
        self.assertIn("'=HYPERLINK",rows[0]['slug'])

    def test_non_citation_body_blocks_are_not_removed(self):
        build=rebuild_doc(self.parent,0,'<p>Medicine refrigeration without link.</p><p>{{cite:s1}}</p>')
        r=run(build)
        texts=[b['DOM_TEXT_UNABRIDGED_NOT_BROWSER_VERIFIED'] for d in r['all_document_DOM_text_and_citation_review_orders_NOT_APPROVED'] for b in d['full_DOM_text_blocks_UNABRIDGED_NOT_SOURCE_APPROVED']]
        self.assertTrue(any('without link' in x for x in texts))

    def test_parent_input_unmodified(self):
        before=deepcopy(self.parent);run(self.parent)
        self.assertEqual(self.parent,before)

    def test_block_ids_stable(self):
        one=run(self.parent);two=run(self.parent)
        self.assertEqual(one['all_document_DOM_text_and_citation_review_orders_NOT_APPROVED'][0]['full_DOM_text_blocks_UNABRIDGED_NOT_SOURCE_APPROVED'],two['all_document_DOM_text_and_citation_review_orders_NOT_APPROVED'][0]['full_DOM_text_blocks_UNABRIDGED_NOT_SOURCE_APPROVED'])


BAD_CASES={
  'missing_parent_signature': lambda p:p.pop('fingerprint_sha256'),
  'parent_schema':lambda p:p.__setitem__('schema','forged-schema'),
  'parent_release':lambda p:p.__setitem__('release_state','READY'),
  'parent_machine_false':lambda p:p.__setitem__('machine_only',False),
  'parent_machine_string':lambda p:p.__setitem__('machine_only','true'),
  'parent_missing_articles':lambda p:p['counts'].__setitem__('original_articles_conserved',1),
  'parent_missing_tools':lambda p:p['counts'].__setitem__('candidate_tools',1),
  'parent_missing_orig_cites':lambda p:p['counts'].__setitem__('original_citations_preserved_under_R66',2),
  'parent_missing_sources':lambda p:p['counts'].__setitem__('candidate_sources_conserved_under_R67',2),
  'parent_missing_rc_cites':lambda p:p['counts'].__setitem__('RC_citation_occurrences_UNREVIEWED',3),
  'parent_fake_human_reviews':lambda p:p['counts'].__setitem__('human_source_or_claim_checks_performed_BY_R68',1),
  'parent_missing_documents':lambda p:p.pop('all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED'),
  'parent_bad_document_type':lambda p:p.__setitem__('all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED','oops'),
  'parent_missing_one_doc':lambda p:p['all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED'].pop(),
  'parent_duplicate_one_doc':lambda p:p['all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED'].__setitem__(1,deepcopy(p['all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED'][0])),
  'task_malformed':lambda p:p['all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED'].__setitem__(0,[]),
  'task_bad_hash':lambda p:p['all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED'][0].__setitem__('task_sha256','0'*64),
  'task_missing_hash':lambda p:p['all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED'][0].pop('task_sha256'),
  'task_false_claim_clear':lambda p:p['all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED'][0].__setitem__('human_claim_review','VERIFIED'),
  'task_false_source_clear':lambda p:p['all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED'][0].__setitem__('human_source_review','VERIFIED'),
  'task_false_safety_clear':lambda p:p['all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED'][0].__setitem__('qualified_safety_review','VERIFIED'),
  'task_false_QD_clear':lambda p:p['all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED'][0].__setitem__('independent_QD_review','VERIFIED'),
  'task_missing_body':lambda p:p['all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED'][0].pop('RC_body_HTML_UNABRIDGED_NOT_SAFETY_CLEARED'),
  'task_edited_body':lambda p:p['all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED'][0].__setitem__('RC_body_HTML_UNABRIDGED_NOT_SAFETY_CLEARED','new text'),
  'task_modified_sha':lambda p:p['all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED'][0].__setitem__('RC_body_utf8_sha256','a'*64),
  'task_empty_body':lambda p:p['all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED'][0].__setitem__('RC_body_HTML_UNABRIDGED_NOT_SAFETY_CLEARED',''),
  'task_invalid_kind':lambda p:p['all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED'][0].__setitem__('kind','published'),
  'task_duplicate_slug':lambda p:p['all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED'][1].__setitem__('slug','a-guide'),
  'task_duplicate_url':lambda p:p['all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED'][1].__setitem__('proposed_WordPress_url_DRAFT_ONLY','/preparedness/field-tools/a-guide/'),
  'task_url_escape':lambda p:p['all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED'][0].__setitem__('proposed_WordPress_url_DRAFT_ONLY','https://attacker.org/'),
  'task_published':lambda p:p['all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED'][0]['RC_metadata_UNABRIDGED_NOT_SAFETY_CLEARED']['status'].__setitem__('publish','published'),
  'task_bad_citation_list':lambda p:p['all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED'][0].__setitem__('all_RC_citation_occurrences_NOT_CLAIM_SUPPORT',[]),
  'task_citation_id':lambda p:p['all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED'][0]['all_RC_citation_occurrences_NOT_CLAIM_SUPPORT'][0].__setitem__('source_id','replacement'),
  'task_citation_offset':lambda p:p['all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED'][0]['all_RC_citation_occurrences_NOT_CLAIM_SUPPORT'][0].__setitem__('unicode_codepoint_offset_in_candidate_html',99),
  'task_citation_token':lambda p:p['all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED'][0]['all_RC_citation_occurrences_NOT_CLAIM_SUPPORT'][0].__setitem__('exact_citation_token','{{cite:fake}}'),
  'task_citation_ordinal':lambda p:p['all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED'][0]['all_RC_citation_occurrences_NOT_CLAIM_SUPPORT'][0].__setitem__('ordinal',42),
  'task_citation_review_fake':lambda p:p['all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED'][0]['all_RC_citation_occurrences_NOT_CLAIM_SUPPORT'][0].__setitem__('human_claim_support','VERIFIED'),
  'task_citation_variants_fake':lambda p:p['all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED'][0]['all_RC_citation_occurrences_NOT_CLAIM_SUPPORT'][0].__setitem__('all_possible_origin_and_id_pairs_NOT_MERGED','aliased'),
  'task_missing_token':lambda p:p['all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED'][0].__setitem__('RC_body_HTML_UNABRIDGED_NOT_SAFETY_CLEARED','<p>No citation token</p>'),
  'task_malformed_token':lambda p:p['all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED'][0].__setitem__('RC_body_HTML_UNABRIDGED_NOT_SAFETY_CLEARED','<p>{{cite:broken</p>'),
}


def _make_bad(name, transform):
    def check(self):
        p=parent_fixture()
        transform(p)
        for d in p.get('all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED', []):
            if type(d) is dict and name not in ('task_bad_hash','task_missing_hash'):
                d['task_sha256']=gate.digest({k:v for k,v in d.items() if k!='task_sha256'})
        if name not in ('missing_parent_signature',):
            reseal(p)
        with self.assertRaises((gate.ReviewHold,TypeError,KeyError,AttributeError)):
            run(p)
    check.__name__='test_tamper_'+name
    return check

for _name,_fn in BAD_CASES.items():
    setattr(CoreCases,'test_tamper_'+_name,_make_bad(_name,_fn))


class OtherCases(unittest.TestCase):
    def test_invalid_contracts(self):
        for contract in [(), (0,2,3,3,4), (2,0,3,3,4), (2,-1,3,3,4),
                         (2,2,'3',3,4), [2,2,3,3,4], (2,2,3,3), (2,2,3,0,4)]:
            with self.subTest(contract=contract),self.assertRaises(gate.ReviewHold):
                run(expected=contract)
    def test_topic_signal_not_medical_verdict(self):
        p=run()
        self.assertIn('never safety findings',p['limitations'])
        self.assertFalse(p['qualified_safety_clearance'])
    def test_csv_unicode_utf8(self):
        self.assertIn('private_draft_url',gate.csv_tasks(run()))
    def test_direct_html_parser_hidden_after_unclosed_style(self):
        html='<style>.a{}</style><p>{{cite:s1}}</p>'
        audit=gate.CitationDomAudit(html);audit.feed(html);audit.close()
        self.assertEqual(audit.by_offset[html.index('{{cite:s1}}')]['classification'],
            'DOM_TEXT_POTENTIALLY_VISIBLE_NOT_BROWSER_VERIFIED')
    def test_direct_html_parser_nested_hidden_style_scope(self):
        html='<div hidden><p>{{cite:s1}}</p></div><p>{{cite:s2}}</p>'
        audit=gate.CitationDomAudit(html);audit.feed(html)
        self.assertNotEqual(audit.by_offset[html.index('{{cite:s1}}')]['classification'],
            audit.by_offset[html.index('{{cite:s2}}')]['classification'])
    def test_direct_html_parser_no_network(self):
        html='<img src="https://example.com/private"><p>{{cite:s1}}</p>'
        audit=gate.CitationDomAudit(html);audit.feed(html)
        self.assertEqual(len(audit.by_offset),1)

if __name__=='__main__':unittest.main()
