'use strict';
/** Read-only synthetic evidence gate. Never infer real consent, receipt, sale or permission from a display or counter. */
function subscriber(s={}) {
 const fail=[];
 if(s.source!=='jetpack_authoritative_provider')fail.push('NO_PROVIDER_PROOF');
 if(s.email_subscription!=='Subscribed'||s.confirmed_opt_in!==true||!Number.isFinite(Date.parse(s.confirmed_at||'')))fail.push('NO_CURRENT_CONFIRMED_EMAIL_OPT_IN');
 if(s.suppressed!==false||s.unsubscribed!==false)fail.push('SUPPRESSION_UNRESOLVED');
 if(s.consent_scope!=='final_vestige_dispatch')fail.push('WRONG_CONSENT_SCOPE');
 return {state:fail.length?'HOLD':'PROOF_SUPPLIED_FOR_REVIEW',fail};
}
function receipt(x={}) {
 const required=['sender_identity_verified','subject_truthful_verified','html_render_verified','plaintext_render_verified','publisher_physical_address_visible_verified','unsubscribe_visible_verified','unsubscribe_operational_verified','optouts_honored_verified'];
 const fail=x.source==='actual_received_jetpack_mime'?[]:['NO_ACTUAL_RECEIVED_EMAIL'];
 for(const f of required){if(x[f]!==true)fail.push('MISSING_'+f.toUpperCase());}
 return {state:fail.length?'HOLD':'PROOF_SUPPLIED_FOR_REVIEW',fail};
}
function merchant(m={}) {
 const required=['named_fv_account_approved','email_channel_explicitly_permitted','fv_issued_link_verified','approved_creative_checked','offer_guide_live_and_source_audited','checkout_terms_checked','inline_disclosure_verified'];
 const fail=required.filter(k=>m[k]!==true).map(k=>'MISSING_'+k.toUpperCase());
 return {state:fail.length?'HOLD_MERCHANT':'PROOF_SUPPLIED_FOR_REVIEW',fail};
}
function campaign(c={}) {
 const fail=[];
 if(c.issue_count!==6||c.editorial_count!==4||c.commercial_count!==2)fail.push('ALLOCATION_CHANGED');
 if(c.final_founder_send_approval!==true)fail.push('NO_FINAL_FOUNDER_APPROVAL');
 if(subscriber(c.recipient).fail.length)fail.push('NO_ELIGIBLE_RECIPIENT');
 if(receipt(c.email).fail.length)fail.push('NO_ACTUAL_EMAIL_EVIDENCE');
 if(c.is_commercial===true&&merchant(c.merchant).fail.length)fail.push('NO_APPROVED_EMAIL_OFFER');
 return {state:fail.length?'HOLD_UNSENT':'MANUAL_RELEASE_REVIEW_ONLY',fail};
}
function revenue(r={}) {
 if(r.independent_paid_order_report!==true||r.fees_and_refunds_reconciled!==true||r.qualified_human_sessions_audited!==true||
 !Number.isInteger(r.orders_count)||r.orders_count<0||!Number.isFinite(r.settled_gross_usd)||r.settled_gross_usd<0||
 !Number.isFinite(r.refunds_usd)||r.refunds_usd<0||!Number.isFinite(r.fees_usd)||r.fees_usd<0||
 !Number.isInteger(r.qhs)||r.qhs<=0||!['7d','30d'].includes(r.cohort_window)||
 (r.refunds_usd+r.fees_usd>r.settled_gross_usd&&r.negative_net_reconciled!==true))return {state:'NOT_COMPUTABLE'};
 const net=r.settled_gross_usd-r.refunds_usd-r.fees_usd;
 return {state:'COMPUTABLE_ON_ATTESTED_DATA',net_usd:+net.toFixed(2),net_per_1000_qhs:+(net*1000/r.qhs).toFixed(2),orders_count:r.orders_count,cohort_window:r.cohort_window,tiny_sample:r.qhs<1000};
}
module.exports={subscriber,receipt,merchant,campaign,revenue};
