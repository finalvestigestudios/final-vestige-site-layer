import test from 'node:test';
import assert from 'node:assert/strict';
import {classifyPageSignal, evaluateProviderRead, evaluateCommercialRelease, SITE_SIGNALS} from '../focus_consent_gate.mjs';

const good = () => ({
 source:'authenticated_jetpack_subscriber_read',source_verified:true,email_status:'subscribed',
 consent_scope:'dispatch_newsletter',email_delivery_preference:'on',opaque_provider_id:'opaque_TEST_123',
 confirmed_at:'2026-11-16T10:34:00Z',proof_ref:'private:jetpack:proof001',already_emitted:false,
 is_bounced:false,email_paused:false,is_suppressed:false
});

test('no public signal alone is a confirmed signup', () => {
 for(const s of SITE_SIGNALS){const a=classifyPageSignal({[s]:true});assert.equal(a.confirmed_signup,false);assert.equal(a.event,null);assert.ok(a.observed.includes(s));}
});
test('combinations of client signals still fail',()=>{const a=classifyPageSignal(Object.fromEntries(SITE_SIGNALS.map(k=>[k,true])));assert.equal(a.event,null);});
test('provider read may advance to review candidate but does not send',()=>{const a=evaluateProviderRead(good());assert.equal(a.status,'PROVIDER_PROOF_CANDIDATE');assert.equal(a.event,'confirmed_signup_v1');});
for(const [field,value,missing] of [
 ['source','browser', 'provider_authentication'],['source_verified',false,'provider_authentication'],
 ['email_status','not_subscribed','not_email_subscribed'],['email_status','not_confirmed','not_email_subscribed'],
 ['consent_scope','generic_follow','consent_scope'],['email_delivery_preference','paused','delivery_preference'],
 ['opaque_provider_id','email@example.com','opaque_provider_id'],['opaque_provider_id','', 'opaque_provider_id'],
 ['confirmed_at','invalid','confirmed_at'],['confirmed_at',null,'confirmed_at'],
 ['proof_ref','public?pii=1','private_proof_ref'],['already_emitted',true,'deduplicated'],
 ['is_bounced',true,'email_ineligible'],['email_paused',true,'email_ineligible'],['is_suppressed',true,'email_ineligible']
]) test('provider reject '+field+'='+value,()=>{const a=evaluateProviderRead({...good(),[field]:value});assert.equal(a.event,null);assert.ok(a.failures.includes(missing));});
test('commercial all-false HOLD',()=>{const a=evaluateCommercialRelease({});assert.equal(a.can_send,false);assert.ok(a.missing.length>=12);});
test('commercial all-true remains human-review only',()=>{
 const fields=['founder_campaign_approval','authorized_eligible_recipients','native_preview_inspected','fv_physical_address_verified','functional_unsubscribe_verified','partner_fv_acceptance','sku_scope_approved','merchant_email_permission','merchant_link_issued','approved_guide_published','current_checkout_terms_verified','claims_disclosure_approved'];
 const a=evaluateCommercialRelease({...Object.fromEntries(fields.map(k=>[k,true])),has_live_vendor_url:false});
 assert.equal(a.ready_for_human_review_only,true);assert.equal(a.can_send,false);assert.equal(a.status,'HOLD');
});
test('commercial live vendor URL blocks readiness',()=>{
 const fields=['founder_campaign_approval','authorized_eligible_recipients','native_preview_inspected','fv_physical_address_verified','functional_unsubscribe_verified','partner_fv_acceptance','sku_scope_approved','merchant_email_permission','merchant_link_issued','approved_guide_published','current_checkout_terms_verified','claims_disclosure_approved'];
 const a=evaluateCommercialRelease({...Object.fromEntries(fields.map(k=>[k,true])),has_live_vendor_url:true});
 assert.equal(a.ready_for_human_review_only,false);assert.ok(a.missing.includes('premature_vendor_url'));
});
