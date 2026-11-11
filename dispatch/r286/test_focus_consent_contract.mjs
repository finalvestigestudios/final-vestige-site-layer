import test from 'node:test';
import assert from 'node:assert/strict';
import { assessSignup, assessPaidConversion } from './focus_consent_contract.mjs';
const good = () => ({ provenance:'provider-confirmed',subscription:'active', emailPermission:true, confirmedAt:'2026-11-11T18:00:00Z',opaqueSubscriptionId:'opaque_sub_1234',lifecycleId:'cycle_1234567',suppressed:false,unsubscribed:false });
const cases = [
 ['missing provenance',{provenance:'client'}],['pending status',{subscription:'pending'}],['revoked permission',{emailPermission:false}],
 ['unsubscribed',{unsubscribed:true}],['suppressed',{suppressed:true}],['missing time',{confirmedAt:null}],
 ['short opaque ID',{opaqueSubscriptionId:'x'}],['short lifecycle',{lifecycleId:'x'}],
 ['query success',{urlSubscribe:'success'}],['unknown query',{urlSubscribe:'unknown_state'}],
 ['client success',{clientSuccess:true}],['CSS class',{jetpackCssClass:'is-subscriber'}],
 ['PDF click',{pdfDownloaded:true}],['PII email',{email:'example@example.com'}],['PII ip',{ip:'192.0.2.1'}],
 ['PII name',{fullName:'Someone'}],['PII phone',{phone:'555-0000'}]
];
for(const [name, patch] of cases) test('Signup rejects '+name,()=>assert.equal(assessSignup({...good(),...patch}).ok,false));
test('Confirmed provider subscription accepted',()=>{const r=assessSignup(good());assert.equal(r.ok,true);assert.equal(r.event,'confirmed_signup')});
test('Duplicate confirmation lifecycle rejected',()=>{const g=good();assert.deepEqual(assessSignup(g,new Set([g.opaqueSubscriptionId+':'+g.lifecycleId])).blockers,['already_recorded']);});
test('Same provider ID with new lifecycle is not a reactivation without new verified record',()=>{const g=good();g.lifecycleId='cycle_new_0987';assert.equal(assessSignup(g,new Set(['opaque_sub_1234:cycle_1234567'])).ok,true);});
test('Cannot infer signup from missing record',()=>assert.equal(assessSignup(null).ok,false));
const settled=()=>({source:'authenticated_merchant_settlement',status:'settled',orderId:'order_123456',grossCents:3000,refundCents:0,feeCents:600});
test('Net derives from verified settlement fields',()=>assert.deepEqual(assessPaidConversion(settled()),{ok:true,netCents:2400}));
for(const [name,patch] of [['click',{source:'affiliate_click',affiliateClick:true}],['pending',{status:'pending'}],['missing order',{orderId:null}],['price invented',{grossCents:NaN}],['refund omitted',{refundCents:undefined}],['negative net',{refundCents:9999}]]) test('Order rejects '+name,()=>assert.equal(assessPaidConversion({...settled(),...patch}).ok,false));
