'use strict';
/* R209: non-sending, privacy-minimized evidence reconciliation. This cannot approve publication. */
const ALLOWED_ISSUES=Object.freeze({'01':'editorial','02':'editorial','03':'commercial','04':'editorial','05':'commercial','06':'editorial'});
const FLAGS=['received_jetpack_mime_verified','publisher_postal_address_verified','functional_unsubscribe_verified','accurate_from_verified','honest_subject_verified'];
const MFLAGS=['named_partner_approval_verified','email_channel_permission_verified','issued_earning_url_verified','seller_checkout_terms_verified','buyer_guide_published_verified','adjacent_disclosure_verified'];
const SAFE=/^[A-Za-z][A-Za-z0-9_.:-]{3,119}$/;
function safeObject(v, allowed){
 if(!v||typeof v!=='object'||Array.isArray(v))throw Error('structured evidence required');
 for(const k of Object.keys(v)){if(!allowed.includes(k))throw Error('unexpected field: '+k);}
 return v;
}
function count(x){return Number.isSafeInteger(x)&&x>=0;}
function publicSnapshot(v){
 safeObject(v,['source','as_of','total','confirmed','unconfirmed','suppressed','wpcom_followers','email_only_followers','automatic_send','format']);
 if(v.source!=='wpcom_jetpack_newsletter.status'||!/^2026-\d\d-\d\dT/.test(v.as_of||'')||!['full','excerpt'].includes(v.format))throw Error('unsupported snapshot');
 for(const k of ['total','confirmed','unconfirmed','suppressed','wpcom_followers','email_only_followers'])if(!count(v[k]))throw Error('invalid aggregate '+k);
 if(typeof v.automatic_send!=='boolean')throw Error('missing auto-send state');
 return Object.freeze({total_counter:v.total,confirmed_counter:v.confirmed,unconfirmed_requests:v.unconfirmed,wpcom_followers:v.wpcom_followers,email_only_followers:v.email_only_followers,eligible_recipients:'UNKNOWN',nonadditive:true,welcome_receipt:'NOT_VERIFIED',source:v.source,as_of:v.as_of,automatic_send:v.automatic_send});
}
function providerEligibility(v){
 if(!v)return {state:'NOT_VERIFIED',eligible_recipients:'UNKNOWN'};
 safeObject(v,['source','eligible_unique','scope','deduplicated','read_at','evidence_ref']);
 if(v.source!=='provider_filtered_subscription_roster'||v.scope!=='email_subscription_subscribed'||v.deduplicated!==true||!count(v.eligible_unique)||!SAFE.test(v.evidence_ref||'')||!/^20\d\d-\d\d-\d\dT/.test(v.read_at||''))throw Error('unverified eligible-count attestation');
 return {state:'ATTESTED_NOT_INDEPENDENTLY_REPRODUCED',eligible_recipients:v.eligible_unique};
}
function assessIssue(issue, packet={}){
 if(!ALLOWED_ISSUES[issue])throw Error('unknown issue');
 safeObject(packet,['provider','legal','welcome','merchant','founder','draft_approved']);
 const blockers=[];
 let provider={state:'NOT_VERIFIED',eligible_recipients:'UNKNOWN'};
 try{provider=providerEligibility(packet.provider)}catch{blockers.push('INVALID_PROVIDER_EVIDENCE');}
 if(provider.state!=='ATTESTED_NOT_INDEPENDENTLY_REPRODUCED')blockers.push('PROVIDER_ELIGIBILITY_NOT_VERIFIED');
 const legal=packet.legal||{};
 safeObject(legal,FLAGS);
 for(const key of FLAGS)if(legal[key]!==true)blockers.push('LEGAL_'+key.toUpperCase());
 const welcome=packet.welcome||{};
 safeObject(welcome,['received_jetpack_welcome_verified','fieldbook_link_verified','consent_state_checked']);
 if(welcome.received_jetpack_welcome_verified!==true||welcome.fieldbook_link_verified!==true||welcome.consent_state_checked!==true)blockers.push('WELCOME_OR_CONSENT_NOT_VERIFIED');
 if(ALLOWED_ISSUES[issue]==='commercial'){
  const merchant=packet.merchant||{};
  safeObject(merchant,MFLAGS);
  for(const key of MFLAGS)if(merchant[key]!==true)blockers.push('MERCHANT_'+key.toUpperCase());
 }
 if(packet.draft_approved!==true)blockers.push('DRAFT_NOT_FOUNDER_APPROVED');
 if(packet.founder!==true)blockers.push('FINAL_RELEASE_NOT_APPROVED');
 return Object.freeze({issue,type:ALLOWED_ISSUES[issue],blockers,eligible_recipients:provider.eligible_recipients,review_state:blockers.length?'HOLD': 'HUMAN_REVIEW_ONLY',send_authorized:false,publish_authorized:false,paid_sales_verified:false});
}
function revenueAssessment(input){
 if(!input)return {metric:'NOT_COMPUTABLE',reason:'NO_SETTLEMENT_EVIDENCE'};
 safeObject(input,['source','complete_period','currency','qualified_human_sessions','gross','refunds','fees','settled_orders','evidence_ref']);
 if(input.source!=='independent_merchant_or_checkout_reconciliation'||input.complete_period!==true||input.currency!=='USD'||!SAFE.test(input.evidence_ref||''))return {metric:'NOT_COMPUTABLE',reason:'SOURCE_NOT_RECONCILED'};
 for(const k of ['gross','refunds','fees'])if(typeof input[k]!=='number'||!Number.isFinite(input[k])||input[k]<0)return {metric:'NOT_COMPUTABLE',reason:'INVALID_FINANCIAL_INPUT'};
 if(!count(input.settled_orders)||!count(input.qualified_human_sessions)||input.qualified_human_sessions===0||input.refunds+input.fees>input.gross)return {metric:'NOT_COMPUTABLE',reason:'DENOMINATOR_OR_SETTLEMENT_INVALID'};
 return {metric:'INPUT_BASED_ESTIMATE_NOT_INDEPENDENTLY_AUDITED',net_revenue_per_1000:Math.round((input.gross-input.refunds-input.fees)/input.qualified_human_sessions*100000)/100,currency:'USD',confirmed_paid_orders_from_input:input.settled_orders};
}
module.exports={ALLOWED_ISSUES,publicSnapshot,providerEligibility,assessIssue,revenueAssessment};
