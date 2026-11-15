"""R380: native link grammar, taxonomy tools and original safety-state custody.

Strictly synthetic adversarial tests. The remote original 35 article snapshots
are a separate GitHub-backed read-only spot inspection, not a native build.
"""
import copy
import unittest
from test_r379_all_article_source_scope_gate import (fixture, altered, SLUGS, SHELTER, BRANCHES)
from test_r379_all_article_source_scope_gate import gate


def taxonomy():
    return {'slate':[{'slug':slug} for slug in SLUGS],
            'tools':[{'slug':'family-reunification-card'}, {'slug':'reunification-plan'},
                     {'slug':'home-fire-escape-worksheet'}]}


def validate(docs, taxonomy_doc=None):
    m,x,reg,store=docs
    return gate.evaluate(m,x,reg,lambda sha:store[sha],taxonomy_doc)


def modify_body(docs,slug,rewrite):
    m,x,reg,store=docs
    altered(m,store,slug,'body.html',rewrite)


def modify_meta(docs,slug,rewrite):
    m,x,reg,store=docs
    altered(m,store,slug,'meta.json',rewrite)


class R380Tests(unittest.TestCase):
    def setUp(self):
        self.docs=fixture()
    def test_native_token_parser(self):
        self.assertEqual(gate.LINK.findall('A {{link:water-math|Water math}}.'), [('water-math','Water math')])
    def test_reject_old_grammar(self):
        modify_body(self.docs,SLUGS[4],lambda b:b+' {{link:water-math}}')
        self.assertIn('malformed or unparsed internal link token', ' '.join(validate(self.docs)['errors']))
    def test_reject_unknown_slug(self):
        modify_body(self.docs,SLUGS[4],lambda b:b+' {{link:alien-nonexistent|False destination}}')
        r=validate(self.docs,taxonomy())
        self.assertTrue(any('unresolved original article/tool link targets' in x for x in r['errors']))
    def test_permit_known_article_link(self):
        modify_body(self.docs,SLUGS[4],lambda b:b+' {{link:'+SLUGS[3]+'|Open this}}')
        r=validate(self.docs,taxonomy())
        self.assertEqual(r['status'],'CUSTODY_COMPLETE_REVIEW_REQUIRED',r['errors'])
        self.assertIn(SLUGS[3],next(x for x in r['per_variant'] if x['slug']==SLUGS[4])['internal_link_targets'])
    def test_private_tool_link_is_not_public_availability(self):
        modify_body(self.docs,SLUGS[4],lambda b:b+' {{link:family-reunification-card|Wallet tool}}')
        r=validate(self.docs,taxonomy())
        self.assertEqual(r['status'],'CUSTODY_COMPLETE_REVIEW_REQUIRED',r['errors'])
        self.assertTrue(any('private tool links require independently reviewed destination' in x for x in r['warnings']))
        self.assertFalse(r['publication_approved'])
    def test_unknown_tool_rejected_if_not_in_taxonomy(self):
        modify_body(self.docs,SLUGS[4],lambda b:b+' {{link:fake-tool|Fake}}')
        self.assertTrue(any('unresolved original' in x for x in validate(self.docs,taxonomy())['errors']))
    def test_duplicate_taxonomy_tool_rejected(self):
        t=taxonomy();t['tools'].append({'slug':'reunification-plan'})
        self.assertTrue(any('duplicate or colliding tool slug' in x for x in validate(self.docs,t)['errors']))
    def test_tool_slug_colliding_with_article_rejected(self):
        t=taxonomy();t['tools'].append({'slug':SLUGS[0]})
        self.assertTrue(any('duplicate or colliding tool slug' in x for x in validate(self.docs,t)['errors']))
    def test_taxonomy_article_missing_rejected(self):
        t=taxonomy();t['slate'].pop()
        self.assertTrue(any('35-article slate mismatch' in x for x in validate(self.docs,t)['errors']))
    def test_taxonomy_invalid_type_rejected(self):
        self.assertTrue(any('taxonomy input must be' in x for x in validate(self.docs,'forged')['errors']))
    def test_original_approved_label_with_dated_reviewer_retained_not_independent(self):
        slug=SLUGS[6]
        modify_meta(self.docs,slug,lambda m:{**m,'safety_review':{'state':'approved','reviewer':'Named founder','date':'2026-10-29'}})
        r=validate(self.docs)
        self.assertEqual(r['status'],'CUSTODY_COMPLETE_REVIEW_REQUIRED',r['errors'])
        self.assertTrue(any('independent source/safety/QD' in x for x in r['warnings']))
        self.assertEqual(next(x for x in r['per_variant'] if x['slug']==slug)['original_safety_label'],'approved')
        self.assertFalse(r['qualified_safety_approved'])
        self.assertTrue(r['historical_approval_is_not_independent_qd'])
    def test_original_not_required_label_retained_not_independent(self):
        slug=SLUGS[6];modify_meta(self.docs,slug,lambda m:{**m,'safety_review':{'state':'not-required'}})
        r=validate(self.docs)
        self.assertEqual(r['status'],'CUSTODY_COMPLETE_REVIEW_REQUIRED',r['errors'])
        self.assertTrue(any('not independent QD clearance' in x for x in r['warnings']))
        self.assertFalse(r['publication_approved'])
    def test_forged_approved_label_lacks_named_reviewer(self):
        slug=SLUGS[6];modify_meta(self.docs,slug,lambda m:{**m,'safety_review':{'state':'approved','reviewer':'','date':'2026-10-29'}})
        self.assertTrue(any('lacks dated reviewer' in x for x in validate(self.docs)['errors']))
    def test_forged_approved_label_missing_date(self):
        slug=SLUGS[6];modify_meta(self.docs,slug,lambda m:{**m,'safety_review':{'state':'approved','reviewer':'A'}})
        self.assertTrue(any('lacks dated reviewer' in x for x in validate(self.docs)['errors']))
    def test_unknown_state_rejected(self):
        slug=SLUGS[6];modify_meta(self.docs,slug,lambda m:{**m,'safety_review':{'state':'QD PASS'}})
        self.assertTrue(any('unrecognized original safety label' in x for x in validate(self.docs)['errors']))
    def test_meta_missing_source_use_rejected(self):
        slug=SLUGS[6];modify_meta(self.docs,slug,lambda m:{**m,'source_use':{'local-ref':'yes'}})
        self.assertTrue(any('body/metadata cite mismatch' in x for x in validate(self.docs)['errors']))
    def test_no_auto_deploy_with_all_citations(self):
        r=validate(self.docs,taxonomy());self.assertEqual(r['status'],'CUSTODY_COMPLETE_REVIEW_REQUIRED',r['errors'])
        self.assertFalse(r['publication_approved']);self.assertFalse(r['qualified_safety_approved'])
        self.assertFalse(r['verified_paid_offer']);self.assertIsNone(r['verified_net_revenue'])
    def test_multiple_native_links_are_counted(self):
        slug=SLUGS[4];modify_body(self.docs,slug,lambda b:b+' {{link:'+SLUGS[3]+'|One}} {{link:'+SLUGS[0]+'|Two}}')
        self.assertEqual(len(next(x for x in validate(self.docs,taxonomy())['per_variant'] if x['slug']==slug)['internal_link_targets']),3)
    def test_invalid_link_without_label_is_error(self):
        slug=SLUGS[4];modify_body(self.docs,slug,lambda b:b+' {{link:water-math|}}')
        self.assertTrue(any('malformed or unparsed internal link' in x for x in validate(self.docs)['errors']))
    def test_history_and_modern_not_promoted_by_citation_parity(self):
        r=validate(self.docs,taxonomy());self.assertTrue(all(x['independent_qd_approved'] is False for x in r['per_variant']))


def gen_missing_target(slug):
    def case(self):
        modify_body(self.docs,slug,lambda b:b+' {{link:unregistered-tool-999|False CTA}}')
        r=validate(self.docs,taxonomy())
        self.assertTrue(any('unresolved original article/tool link targets: '+slug in x for x in r['errors']),r['errors'])
        self.assertFalse(r['publication_approved'])
    return case

for i,slug in enumerate(SLUGS):
    setattr(R380Tests,f'test_slate_{i+1:02d}_reject_unknown_target',gen_missing_target(slug))

if __name__=='__main__':
    unittest.main()
