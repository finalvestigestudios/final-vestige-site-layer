"use strict";
/* FV Dispatch R373 OFFLINE reviewer. No network, sends, email addresses or production tracking.
   Synthetic evidence attestations do not prove any real person, merchant or sale. */
const SHARED = Object.freeze([
"founder_final_send_approval","provider_email_eligibility_reviewed","received_welcome_fieldbook_verified",
"native_jetpack_preview_verified","fv_postal_address_verified",
"rendered_unsubscribe_verified","editorial_claims_and_cta_reviewed"]);
const COMMERCIAL = Object.freeze([
"named_affiliate_account_approved","exact_sku_email_channel_permitted",
"issued_earning_url_verified_privately","warmup_guide_live_and_approved",
"referred_checkout_terms_verified","offer_disclosure_adjacent_to_cta"]);
const OPAQUE=/^[a-f0-9]{32,64}$/i, PROOF=/^proof:[a-z0-9_-]{8,80}$/i;
function reviewEdition(edition,attestations={}){
if(![1,2,3,4,5,6].includes(edition)) throw new TypeError("edition must be 1..6");
const commercial=edition===3||edition===5,required=commercial?[...SHARED,...COMMERCIAL]:[...SHARED];
const missing=required.filter(k=>attestations[k]!==true);
return {edition,lane:commercial?"commercial":"editorial",
state:missing.length?(commercial?"HOLD_UNSENT_HOLD_MERCHANT":"HOLD_UNSENT"):"REVIEW_CANDIDATE_ONLY",
send_authorized:false,missing};
}
function confirmedSignup(record){
if(!record||typeof record!=="object") return false;
return record.event==="confirmed_signup"&&record.provider==="jetpack"
&&record.email_subscription==="Subscribed"&&record.provider_status_verified===true
&&typeof record.confirmed_at==="string"&&/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$/.test(record.confirmed_at)
&&OPAQUE.test(record.opaque_key||"")&&PROOF.test(record.provider_evidence_ref||"");
}
function summarizeProofs({signups=[],orders=[],sessions=null}={}){
const validSignups=new Set();
for(const record of signups)if(confirmedSignup(record))validSignups.add(record.opaque_key.toLowerCase());
const validOrders=new Map();
for(const order of orders){
if(!order||order.status!=="settled"||order.source!=="merchant_settlement"
||!OPAQUE.test(order.opaque_order_id||"")||!PROOF.test(order.settlement_evidence_ref||"")
||![order.gross,order.refunds,order.fees].every(n=>typeof n==="number"&&Number.isFinite(n)&&n>=0)
||order.refunds>order.gross||order.fees>order.gross)continue;
if(!validOrders.has(order.opaque_order_id.toLowerCase()))validOrders.set(order.opaque_order_id.toLowerCase(),order);
}
const settled=[...validOrders.values()],moneyKnown=settled.length>0;
const qualifiedKnown=!!(sessions&&sessions.source==="audited_human_sessions"
&&sessions.filter_reviewed===true&&Number.isSafeInteger(sessions.count)&&sessions.count>=0
&&PROOF.test(sessions.evidence_ref||""));
const round=n=>Math.round(n*100)/100;
const gross=moneyKnown?round(settled.reduce((s,x)=>s+x.gross,0)):null;
const refunds=moneyKnown?round(settled.reduce((s,x)=>s+x.refunds,0)):null;
const fees=moneyKnown?round(settled.reduce((s,x)=>s+x.fees,0)):null;
const net=moneyKnown?round(gross-refunds-fees):null;
const denom=qualifiedKnown?sessions.count:null;
return {confirmed_signup_count:validSignups.size,
settled_order_count:moneyKnown?settled.length:null,
gross_revenue:gross,refunds,fees,net_revenue:net,qualified_human_sessions:denom,
net_revenue_per_1000_qualified_human_sessions:moneyKnown&&qualifiedKnown&&denom>0?round(net*1000/denom):null,
attribution_to_specific_asset_verified:false,synthetic_contract_only:true};
}
module.exports={SHARED,COMMERCIAL,reviewEdition,confirmedSignup,summarizeProofs};
