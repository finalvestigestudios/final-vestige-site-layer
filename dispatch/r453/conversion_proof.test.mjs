/** Dispatch R453 Node 20+ assertions. Offline synthetic fixtures ONLY; no actual email or order data. */
import test from 'node:test';
import assert from 'node:assert/strict';
import { RELEASE_STATE, assessProviderCounts, validateCampaign, assessSignup, assessUtm, sumRevenue, dedupeConfirmedSignups } from './conversion_proof.mjs';

const proof = { verified: true, source_ref: 'provider:synthetic-receipt', checked_at: '2026-11-18T18:35:00Z' };
const campaign = { issues: [1,2,3,4,5,6].map(number => ({
  number, kind: [3,5].includes(number) ? 'commercial' : 'editorial',
  product: number === 3 ? 'Zen12' : number === 5 ? 'Hypnosis Live' : null,
  send_status:'HOLD_UNSENT',
})) };
const feeds = {
  newsletter:{total:3,confirmed:3,unconfirmed:2},
  statsSubscribers:{email:3,reader:0,unconfirmed:2},
  statsFollowers:{email:0,wpcom:3},
};
const signup = {type:'provider_confirmation',provider:'jetpack',prior_status:'unconfirmed',new_status:'confirmed_email',
 existing_confirmed:false,is_reader_only:false,is_suppressed:false,provider_proof:proof};
const utm = {utm_source:'youtube',utm_medium:'organic_social',utm_campaign:'mind_pilot_2026_11',utm_content:'YT_1234'};
const order = {order_id:'opaque-order-1',type:'paid_affiliate_commission',state:'settled',gross_cents:2900,
 fees_cents:300,refunds_cents:200,settlement_proof:proof,attribution_proof:proof,campaign:utm};
const ledger = {qualified_human_sessions:200,sessions_proof:proof,orders_complete:true,order_ledger_proof:proof,orders:[order]};
test('immutable HOLD default', () => assert.equal(RELEASE_STATE,'HOLD_UNSENT'));
test('six editions exactly preserved 4 editorial 2 commercial', () => assert.deepEqual(validateCampaign(campaign).errors,[]));
test('valid campaign still cannot send', () => assert.equal(validateCampaign(campaign).can_send,false));
test('missing edition fails', () => assert.ok(validateCampaign({issues:campaign.issues.slice(0,5)}).errors.length));
test('wrong Zen12 SKU fails', () => assert.ok(validateCampaign({issues:campaign.issues.map((x,i)=>i===2?{...x,product:'Brainwave Shots'}:x)}).errors.includes('zen12_identity')));
test('wrong Hypnosis Live identity fails', () => assert.ok(validateCampaign({issues:campaign.issues.map((x,i)=>i===4?{...x,product:'Total Focus'}:x)}).errors.includes('hypnosislive_identity')));
test('any send status change fails', () => assert.ok(validateCampaign({issues:campaign.issues.map((x,i)=>i===0?{...x,send_status:'READY'}:x)}).errors.includes('issue_1_not_held')));
test('current subscriber feeds disagree', () => assert.equal(assessProviderCounts(feeds).status,'DISAGREE'));
test('both subscriber classification axes conflict', () => assert.equal(assessProviderCounts(feeds).conflicts.length,2));
test('do not infer acquired users', () => assert.equal(assessProviderCounts(feeds).independently_acquired_leads,null));
test('do not infer welcome receipt', () => assert.equal(assessProviderCounts(feeds).welcomes_delivered,null));
test('matching synthetic feed accepted', () => assert.equal(assessProviderCounts({...feeds,statsSubscribers:{email:3,reader:3,unconfirmed:2},statsFollowers:{email:3,wpcom:3}}).status,'AGREE'));
test('invalid counts unknown', () => assert.equal(assessProviderCounts({...feeds,newsletter:{total:3,confirmed:-1,unconfirmed:2}}).status,'UNKNOWN'));
test('actual provider-confirmed new signup can be counted with proof', () => assert.equal(assessSignup(signup).counted,true));
test('PDF click never signup', () => assert.equal(assessSignup({...signup,type:'download_click'}).counted,false));
test('existing subscriber excluded', () => assert.equal(assessSignup({...signup,existing_confirmed:true}).counted,false));
test('Reader-only excluded', () => assert.equal(assessSignup({...signup,is_reader_only:true}).counted,false));
test('suppressed excluded', () => assert.equal(assessSignup({...signup,is_suppressed:true}).counted,false));
test('no source proof excluded', () => assert.equal(assessSignup({...signup,provider_proof:null}).counted,false));
test('valid Grok canonical UTM accepted', () => assert.equal(assessUtm(utm),true));
test('wrong traffic medium rejected', () => assert.equal(assessUtm({...utm,utm_medium:'paid_search'}),false));
test('PII-looking asset content disallowed', () => assert.equal(assessUtm({...utm,utm_content:'private@email.com'}),false));
test('true synthetic net = gross less fees and refunds', () => assert.equal(sumRevenue(ledger).net_cents,2400));
test('1k-session normalized metric uses qualified human denominator', () => assert.equal(sumRevenue(ledger).net_revenue_per_1000_cents,12000));
test('identical duplicate transaction counted once', () => assert.equal(sumRevenue({...ledger,orders:[order,order]}).orders,1));
test('conflicting duplicate blocked', () => assert.equal(sumRevenue({...ledger,orders:[order,{...order,gross_cents:3000}]}).status,'UNCOMPUTABLE'));
test('unattributed order cannot inherit source', () => assert.equal(sumRevenue({...ledger,orders:[{...order,attribution_proof:null}]}).orders_with_independently_justified_campaign_attribution,0));
test('unverified settlement blocks revenue claim', () => assert.equal(sumRevenue({...ledger,orders:[{...order,settlement_proof:null}]}).status,'UNCOMPUTABLE'));
test('refund beyond gross invalid', () => assert.equal(sumRevenue({...ledger,orders:[{...order,refunds_cents:3500}]}).status,'UNCOMPUTABLE'));
test('zero qualified sessions produces null per-1000', () => assert.equal(sumRevenue({...ledger,qualified_human_sessions:0}).net_revenue_per_1000_cents,null));
test('missing audited denominator proof blocks', () => assert.equal(sumRevenue({...ledger,sessions_proof:null}).status,'UNCOMPUTABLE'));
test('missing complete provider settlement ledger blocks', () => assert.equal(sumRevenue({...ledger,order_ledger_proof:null}).status,'UNCOMPUTABLE'));
test('clicks and incomplete reports never provide real revenue', () => assert.equal(sumRevenue({clicks:99,checkout_starts:3}).status,'UNCOMPUTABLE'));

const eventToken={...signup,dedupe_token:'opaque-test-0001'};
test('one verified new signup',()=>assert.equal(dedupeConfirmedSignups([eventToken]).confirmed_new,1));
test('duplicate signup never double counted',()=>assert.equal(dedupeConfirmedSignups([eventToken,eventToken]).confirmed_new,1));
test('unconfirmed attempt not counted',()=>assert.equal(dedupeConfirmedSignups([{...eventToken,type:'signup_attempt'}]).confirmed_new,0));
test('new confirmation without opaque dedupe token fails',()=>assert.equal(dedupeConfirmedSignups([signup]).status,'UNCOMPUTABLE'));
test('invalid or PII-looking dedupe token fails',()=>assert.equal(dedupeConfirmedSignups([{...eventToken,dedupe_token:'someone@example.com'}]).status,'UNCOMPUTABLE'));
