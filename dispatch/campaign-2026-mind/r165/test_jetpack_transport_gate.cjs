'use strict';
const assert=require('node:assert/strict');
const test=require('node:test');
const {inspectSnapshot,inspectProposedWordPressPost,canReportRevenue}=require('./jetpack_transport_gate.cjs');
const fs=require('node:fs');
const path=require('node:path');
const snapshot=JSON.parse(fs.readFileSync(path.join(__dirname,'canonical_transport_audit.json'),'utf8'));
const evidence={provider_email_preview_verified:true,publisher_address_verified:true,unsubscribe_verified:true,email_eligibility_verified:true,welcome_delivery_verified:true,named_affiliate_accepted:true,email_promotion_allowed:true,earning_link_approved:true,live_warmup_guide_verified:true};
const draft={type:'post',status:'draft',send_subscription:false,publish_at:null,title:'Fourteen seconds. A much longer explanation.',body:'An evidence-led historical email preview draft describing surviving archival records, limitations and a reading destination.',issue_kind:'editorial'};
test('canonical six issues remain four editorial and two commercial',()=>{const r=inspectSnapshot(snapshot);assert.equal(r.status,'HOLD_UNSENT');assert.equal(r.subscriber_counts_additive,false);assert.equal(r.verified_email_eligible,null);});
test('provider counters are not eligible-recipient proof',()=>{assert.equal(inspectSnapshot(snapshot).reported_total,3);assert.equal(inspectSnapshot(snapshot).reported_unconfirmed,2);assert.equal(inspectSnapshot(snapshot).confirmed_leads,null);});
test('only a strictly configured synthetic draft can qualify for review, never send',()=>{const r=inspectProposedWordPressPost(draft,evidence);assert.equal(r.preview_candidate,true);assert.equal(r.send_authorized,false);assert.equal(r.status,'HOLD_UNSENT');});
for(const [field,value] of [['type','page'],['status','publish'],['status','future'],['send_subscription',true],['send_subscription',null],['publish_at','2026-11-12T00:00:00Z'],['body','<script>bad()</script>'],['body','[[VALID_POSTAL_ADDRESS_REQUIRED]]'],['body','UNSENT DRAFT pre-send compliance block']]){
 test('deny draft mutation '+field+' '+String(value),()=>{assert.equal(inspectProposedWordPressPost({...draft,[field]:value},evidence).preview_candidate,false);});
}
for(const key of ['provider_email_preview_verified','publisher_address_verified','unsubscribe_verified','email_eligibility_verified','welcome_delivery_verified']){
 test('missing independent evidence '+key,()=>{const r=inspectProposedWordPressPost(draft,{...evidence,[key]:false});assert.equal(r.preview_candidate,false);assert.equal(r.send_authorized,false);});
}
test('commercial needs adjacent disclosure',()=>{const r=inspectProposedWordPressPost({...draft,issue_kind:'commercial-review-pending'},evidence);assert.equal(r.preview_candidate,false);});
for(const key of ['named_affiliate_accepted','email_promotion_allowed','earning_link_approved','live_warmup_guide_verified']){
 test('commercial merchant requirement '+key,()=>{const r=inspectProposedWordPressPost({...draft,body:'Commercial disclosure: FV may earn a commission. '+draft.body,issue_kind:'commercial-review-pending'},{...evidence,[key]:false});assert.equal(r.preview_candidate,false);});
}
test('commercial remains unsent even if synthetic flags are all true',()=>{const r=inspectProposedWordPressPost({...draft,body:'Commercial disclosure: FV may earn a commission. '+draft.body,issue_kind:'commercial-review-pending'},evidence);assert.equal(r.status,'HOLD_UNSENT');assert.equal(r.send_authorized,false);});
test('no revenue from clicks or unverified paid receipts',()=>{assert.equal(canReportRevenue({sessions:200,clicks:40,receipts:100}).net_per_1000,null);});
test('settled example algebra only when all independent evidence is explicitly attested',()=>{const r=canReportRevenue({qualified_human_sessions_verified:true,provider_paid_orders_verified:true,attribution_verified:true,fees_refunds_reconciled:true,sessions:100,receipts:30,fees:5,refunds:4});assert.equal(r.net_per_1000,210);});
