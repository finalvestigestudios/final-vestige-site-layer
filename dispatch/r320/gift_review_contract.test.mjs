import test from 'node:test';
import assert from 'node:assert/strict';
import {evaluateGiftReview} from './gift_review_contract.mjs';
test('arbitrary URL subscription values never constitute widget proof',()=>{
 for(const value of ['hello','success','blocked','anything','true']){
  const v=evaluateGiftReview({url_subscribe:value});
  assert.equal(v.gift_visible,false);assert.equal(v.confirmed_signup,null);
 }
});
test('CSS class is not provider confirmation',()=>{
 const r=evaluateGiftReview({widget_class:'is-subscriber'});
 assert.equal(r.gift_visible,false);assert.equal(r.counted_as_lead,false);
});
test('a widget acknowledgement may reveal a UX gift, but never a confirmed signup',()=>{
 const r=evaluateGiftReview({user_action:'submitted_subscribe_form',
  widget_response:'acknowledged_attempt',adapter_origin:'validated_jetpack_ui_adapter',
  adapter_attestation:true});
 assert.equal(r.gift_visible,true);assert.equal(r.confirmed_signup,null);
 assert.equal(r.email_delivery_eligible,null);assert.equal(r.welcome_received,null);
 assert.equal(r.counted_as_sale,false);assert.equal(r.send_authorized,false);
});
test('all four UI preconditions are necessary',()=>{
 const full={user_action:'submitted_subscribe_form',widget_response:'acknowledged_attempt',
  adapter_origin:'validated_jetpack_ui_adapter',adapter_attestation:true};
 for(const key of Object.keys(full)){
  const v={...full};delete v[key];assert.equal(evaluateGiftReview(v).gift_visible,false,key);
 }
});
test('failed widget response is not success',()=>{
 assert.equal(evaluateGiftReview({user_action:'submitted_subscribe_form',
  widget_response:'failed',adapter_origin:'validated_jetpack_ui_adapter',
  adapter_attestation:true}).gift_visible,false);
});
test('no status can authorize a send or infer a paid sale',()=>{
 for(const v of [{},{url_subscribe:'ok'},{user_action:'submitted_subscribe_form',
  widget_response:'acknowledged_attempt',adapter_origin:'validated_jetpack_ui_adapter',
  adapter_attestation:true}]){
  const r=evaluateGiftReview(v);assert.equal(r.send_authorized,false);
  assert.equal(r.counted_as_sale,false);assert.equal(r.counted_as_lead,false);
 }
});
test('reject PII keys rather than echo private subscriber records',()=>{
 for(const key of ['email','subscriber_email','phone','contact_name','ip_address']){
  assert.throws(()=>evaluateGiftReview({[key]:'PRIVATE'}),/PII_FIELD_REJECTED/);
 }
});
test('reject malformed input and preserve immutable result',()=>{
 for(const input of [null,[],3,'not-an-object'])assert.throws(()=>evaluateGiftReview(input),/BAD_INPUT/);
 assert.equal(Object.isFrozen(evaluateGiftReview({})),true);
});