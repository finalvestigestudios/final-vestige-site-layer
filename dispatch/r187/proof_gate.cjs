
'use strict';
// Offline verification only. Provider records and real-world payment settlements must be authenticated elsewhere.
const bannedKeys=['email','email_address','recipient_email','phone','ip_address','user_agent'];
function rejectPII(x){
 if(x===null||typeof x!=='object')return;
 for(const [k,v] of Object.entries(x)){if(bannedKeys.includes(k.toLowerCase()))throw Error('raw identity field not permitted');rejectPII(v);}
}
function summary(counts){
 rejectPII(counts);
 for(const k of ['total','confirmed','unconfirmed','suppressed'])if(!Number.isInteger(counts[k])||counts[k]<0)throw Error('invalid '+k);
 if(counts.confirmed>counts.total)throw Error('confirmed greater than total');
 return {counted:counts.total,confirmed:counts.confirmed,pending:counts.unconfirmed,email_eligible:null,interpretation:'Nonadditive; email subscribed status not known'};
}
function emailEligibleAggregate(e){
 rejectPII(e);
 if(!e || e.source!=='jetpack_subscribers_filter' || e.status!=='Subscribed' || !Number.isInteger(e.count) || e.count<0 ||
 e.independently_attested!==true || typeof e.private_receipt!=='string' ||
 !/^internal:[a-z0-9/_-]+$/i.test(e.private_receipt))
 return {count:null,proof:'UNKNOWN'};
 return {count:e.count,proof:'INDEPENDENT_PROVIDER_RECEIPT_REQUIRED'};
}
function confirmedSignup(e){
 rejectPII(e);
 return Boolean(e && e.source==='jetpack' && e.status==='Subscribed' && e.consent_scope==='Dispatch' &&
 e.provider_confirmed===true && e.receipt_independently_attested===true &&
 typeof e.opaque_key==='string' && /^subref_[a-z0-9_-]{8,}$/i.test(e.opaque_key) &&
 typeof e.private_receipt==='string' && /^internal:[a-z0-9/_-]+$/i.test(e.private_receipt));
}
function uniqueConfirmed(events){
 if(!Array.isArray(events))throw Error('array required');let keys=new Set();
 for(const e of events)if(confirmedSignup(e))keys.add(e.opaque_key);
 return {count:keys.size,kind:'policy-fixture-only'};
}
const shared=['founder_send_approval','eligible_recipients_attested','native_jetpack_preview_reviewed','fv_physical_postal_in_email','recipient_unsubscribe_verified','final_content_schedule_approved'];
const merchant=['fv_partner_approved','email_channel_allowed','exact_earning_link_approved','live_vetted_guide','seller_claims_checked','checkout_refund_terms_current','disclosure_beside_offer'];
function release(e){
 rejectPII(e);
 if(!e || !e.shared || !shared.every(k=>e.shared[k]===true))return {send:false,reason:'HOLD_SHARED'};
 if(e.kind==='commercial' && (!e.merchant || !merchant.every(k=>e.merchant[k]===true)))return {send:false,reason:'HOLD_MERCHANT'};
 if(e.kind!=='commercial' && e.kind!=='editorial')return {send:false,reason:'HOLD_UNKNOWN_KIND'};
 return {send:true,reason:'ONLY_AFTER_VERIFIED_FOUNDER_APPROVAL'};
}
function emailAttribution(e){
 rejectPII(e);
 if(!e || e.utm_source!=='jetpack'||e.utm_medium!=='email'|| !/^dsp_0[1-6]$/.test(e.utm_campaign) ||
 !/^issue_0[1-6]$/.test(e.utm_content)|| !/^https:\/\/finalvestige\.com\//.test(e.destination||''))
 return {accepted:false};
 return {accepted:true,classification:'VISIT_OR_CLICK_NOT_PURCHASE'};
}
function revenuePerThousand(x){
 rejectPII(x);
 if(!x || x.independently_reconciled!==true || !Number.isInteger(x.qualified_human_sessions) ||
 x.qualified_human_sessions<1 || ![x.gross,x.refunds,x.fees].every(n=>Number.isFinite(n)&&n>=0))return null;
 return 1000*(x.gross-x.refunds-x.fees)/x.qualified_human_sessions;
}
module.exports={summary,emailEligibleAggregate,confirmedSignup,uniqueConfirmed,release,emailAttribution,revenuePerThousand};
