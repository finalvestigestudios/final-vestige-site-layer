import test from 'node:test';
import assert from 'node:assert/strict';
import {SEND_ENABLED,assessScopedOffer as audit} from './offer_scope.mjs';
import {assessAttributableCohort as old} from '../r395/cohort_guard.mjs';
const t0='2026-11-01T00:00:00.000Z',t1='2026-11-08T00:00:00.000Z',ts='2026-11-10T00:00:00.000Z';
function fixture(issue=3){
  const family=issue===3?'zen12':'hypnosis_live',sku=issue===3?'synthetic_zen12_tier':'synthetic_total_focus_sku';
  return {issue,
    permission:{issue,partner:'inspire3',family,sku,publisher_account_ref:'synthetic_publisher',
      named_acceptance_ref:'synthetic_acceptance',email_channel_grant_ref:'synthetic_email_grant',
      sku_grant_ref:'synthetic_sku_grant',issued_earning_link_ref:'synthetic_earning_link',
      named_partner_accepted:true,email_marketing_permitted:true,exact_sku_permitted:true,
      email_creative_authorized:true,checkout_and_refund_checked:true,checked_at:ts},
    guide:{issue,family,sku,url:'https://finalvestige.com/mind/synthetic-buyer-guide/',
      live_http_200:true,wp_published_verified:true,claims_checked:true,disclosure_adjacent_to_cta:true,
      outbound_matches_issued_link:true,source_review_ref:'synthetic_guide_review'},
    asset:{asset_id:'synthetic_social_001',campaign_id:'synthetic_mind_pilot',
      published_post_ref:'synthetic_video_ref',independently_verified:true,
      asset_inventory_review_ref:'synthetic_social_review'},
    cohort:{campaign_id:'synthetic_mind_pilot',window_start_utc:t0,window_end_utc:t1,window_days:7,
      sessions:[{asset_id:'synthetic_social_001',report_id:'synthetic_session_report',
        campaign_id:'synthetic_mind_pilot',source_system:'first_party_analytics',
        provider_audited:true,qualified_human_sessions:100,utm_content:'synthetic_social_001',
        utm_campaign:'synthetic_mind_pilot',utm_medium:'organic_social',
        source_audit_ref:'synthetic_analytics_review',window_start_utc:t0,window_end_utc:t1}],
      ledger:{partner:'inspire3',family,sku,publisher_account_ref:'synthetic_publisher',
        issued_earning_link_ref:'synthetic_earning_link',merchant_export_ref:'synthetic_merchant_export',
        independent_reconciliation_ref:'synthetic_reconcile',source_system:'merchant_affiliate_dashboard',
        publisher_account_verified:true,email_channel_authorized:true,exact_sku_authorized:true,
        referred_guide_live_verified:true,report_reconciled:true,complete_for_cohort:true,
        merchant_report_id:'synthetic_mreport',currency:'USD',
        settlement_as_of_utc:'2026-11-15T00:00:00.000Z',
        records:[{partner:'inspire3',family,sku,issued_earning_link_ref:'synthetic_earning_link',
          issue,attribution_method:'merchant_asset_postback',attribution_proof_ref:'synthetic_join',
          evidence:'merchant_settled_commission',provider_verified:true,settlement_id:'synthetic_settlement',
          opaque_order_key:'synthetic_order',asset_id:'synthetic_social_001',
          campaign_id:'synthetic_mind_pilot',session_at_utc:'2026-11-03T00:00:00.000Z',
          settled_at_utc:ts,status:'settled',commission_cents:1000,refund_cents:100,
          fee_cents:50,reversal_cents:0}]}}};
}
function rejected(mutator){
  const f=fixture();mutator(f);
  assert.equal(audit(f).status,'NOT_COMPUTABLE');
}
test('NEVER sends anything',()=>assert.equal(SEND_ENABLED,false));
test('positive synthetic issue 03 is never send-ready',()=>{
 const r=audit(fixture());assert.equal(r.status,'SYNTHETIC_CALCULABLE_NOT_RELEASED');
 assert.equal(r.net_revenue_cents,850);assert.equal(r.send_enabled,false);
});
test('positive synthetic issue 05 remains distinct Hypnosis Live family',()=>{
 const r=audit(fixture(5));assert.equal(r.status,'SYNTHETIC_CALCULABLE_NOT_RELEASED');assert.equal(r.offer_family,'hypnosis_live');
});
test('reproduces actual prior cross-SKU missing check',()=>{
 const f=fixture();f.cohort.ledger.records[0].sku='unrelated_seller_sku';
 assert.equal(old({...f.cohort,issue:3}).status,'COMPUTABLE');
 assert.equal(audit(f).status,'NOT_COMPUTABLE');
});
test('editorial slot cannot be affiliate',()=>{const f=fixture();f.issue=2;assert.equal(audit(f).status,'NOT_COMPUTABLE');});
const cases=[
 ['merchant scope',f=>f.permission.partner='other_partner'],
 ['product family',f=>f.permission.family='hypnosis_live'],
 ['account approval',f=>f.permission.named_partner_accepted=false],
 ['email rights',f=>f.permission.email_marketing_permitted=false],
 ['exact SKU permission',f=>f.permission.exact_sku_permitted=false],
 ['email creative',f=>f.permission.email_creative_authorized=false],
 ['checkout/refund',f=>f.permission.checkout_and_refund_checked=false],
 ['missing approval reference',f=>delete f.permission.named_acceptance_ref],
 ['missing earning link reference',f=>delete f.permission.issued_earning_link_ref],
 ['unpublished guide',f=>f.guide.wp_published_verified=false],
 ['non-live guide',f=>f.guide.live_http_200=false],
 ['wrong domain',f=>f.guide.url='https://example.com/mind/guide/'],
 ['missing disclosure',f=>f.guide.disclosure_adjacent_to_cta=false],
 ['different guide SKU',f=>f.guide.sku='different_sku'],
 ['unapproved guide affiliate route',f=>f.guide.outbound_matches_issued_link=false],
 ['unreviewed claims',f=>f.guide.claims_checked=false],
 ['not an authentic social asset',f=>f.asset.independently_verified=false],
 ['social campaign mismatch',f=>f.asset.campaign_id='another_campaign'],
 ['unverified social post',f=>delete f.asset.published_post_ref],
 ['wrong UTM content',f=>f.cohort.sessions[0].utm_content='wrong_asset'],
 ['wrong UTM campaign',f=>f.cohort.sessions[0].utm_campaign='wrong_campaign'],
 ['unverified session window',f=>f.cohort.sessions[0].window_end_utc='2026-11-09T00:00:00.000Z'],
 ['missing source audit',f=>delete f.cohort.sessions[0].source_audit_ref],
 ['unrelated ledger SKU',f=>f.cohort.ledger.sku='another_sku'],
 ['unrelated account',f=>f.cohort.ledger.publisher_account_ref='another_account'],
 ['unrelated ledger earning link',f=>f.cohort.ledger.issued_earning_link_ref='other_link'],
 ['no merchant export',f=>delete f.cohort.ledger.merchant_export_ref],
 ['no independent reconciliation',f=>delete f.cohort.ledger.independent_reconciliation_ref],
 ['paid record unrelated SKU',f=>f.cohort.ledger.records[0].sku='other_sku'],
 ['paid record unrelated slot',f=>f.cohort.ledger.records[0].issue=5],
 ['paid record unrelated link',f=>f.cohort.ledger.records[0].issued_earning_link_ref='other_link'],
 ['paid record no asset postback',f=>f.cohort.ledger.records[0].attribution_method='guess'],
 ['paid record no postback evidence',f=>delete f.cohort.ledger.records[0].attribution_proof_ref],
 ['impossible settlement chronology',f=>f.cohort.ledger.records[0].settled_at_utc='2026-11-01T00:00:00.000Z'],
 ['nested PII',f=>f.permission.extra={subscriber_email:'private@example.test'}],
 ['personal data in ledger',f=>f.cohort.ledger.records[0].extra={ip_address:'127.0.0.1'}],
 ['missing merchant ledger',f=>delete f.cohort.ledger]
];
for(const [name,mutation] of cases)test('fail closed: '+name,()=>rejected(mutation));
test('empty audited merchant report remains test-only not evidence of zero real sales',()=>{
 const f=fixture();f.cohort.ledger.records=[];assert.equal(audit(f).status,'SYNTHETIC_CALCULABLE_NOT_RELEASED');
 f.cohort.ledger.complete_for_cohort=false;assert.equal(audit(f).status,'NOT_COMPUTABLE');
});
