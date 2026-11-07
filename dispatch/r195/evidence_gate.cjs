"use strict";
/* OFFLINE/SYNTHETIC ONLY. Does not authorize email sends. */
function gate(e){
 const m=[];
 for(const k of ["final_founder_approval","eligible_aggregate_provider_verified","native_jetpack_received_preview","publisher_physical_address_verified","real_unsubscribe_verified","consent_scope_verified"]){if(e?.[k]!==true)m.push(k)}
 if(e?.issue==="03"||e?.issue==="05"){for(const k of ["named_merchant_acceptance","email_channel_permission","account_issued_earning_link","live_vetted_guide","product_claims_reviewed"]){if(e?.[k]!==true)m.push(k)}}
 return {status:"HOLD_UNSENT",missing:m,send_allowed:false};
}
function confirmed(e,seen){
 if(!e||e.origin!=="authenticated_jetpack_provider"||e.subscription!=="Subscribed"||e.transition!=="confirmed"||e.opted_out!==false||e.scope!=="dispatch_newsletter"||!e.private_subscriber_id||!e.private_transition_id||!e.provider_confirmation_utc)return {emit:false,reason:"no_provider_proof"};
 const key=e.private_subscriber_id+"#"+e.private_transition_id;
 if(seen.has(key))return {emit:false,reason:"duplicate"};
 seen.add(key); return {emit:true,event:{name:"confirmed_signup",proof_level:"provider_confirmed",source:"jetpack"}}; 
}
function kpi(x){
 if(!x||x.provider_settlement_reconciled!==true||x.qualified_sessions_verified!==true||!x.period_complete||!Number.isFinite(x.sessions)||x.sessions<=0||!Array.isArray(x.orders)||x.orders.length===0&&x.provider_zero_orders_attested!==true)return null;
 if(x.orders.some(o=>o.settled!==true||!Number.isFinite(o.net)))return null;
 return 1000*x.orders.reduce((n,o)=>n+o.net,0)/x.sessions;
}
module.exports={gate,confirmed,kpi};
