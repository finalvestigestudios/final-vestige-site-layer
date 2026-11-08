'use strict';
/* Dispatch R199, isolated synthetic-only decision logic. No WordPress network, PII or active links. */
const ISO = s => typeof s==='string' && Number.isFinite(Date.parse(s)) && /Z$/.test(s);
const HOLD = (why) => ({state:'HOLD',fail:why});
function eligibleAggregate(e={}) {
 const missing=[];
 if(e.provenance!=='provider_filtered_email_subscribed_aggregate')missing.push('NO_AUTHORITATIVE_FILTERED_AGGREGATE');
 if(!ISO(e.observed_at))missing.push('MISSING_UTC_TIME');
 if(!Number.isInteger(e.deduplicated_eligible)||e.deduplicated_eligible<0)missing.push('NOT_DEDUPLICATED');
 if(e.excludes_unsubscribed!==true||e.excludes_suppressed!==true||e.excludes_paused!==true)missing.push('SUPPRESSION_UNKNOWN');
 if(e.dispatch_marketing_consent_verified!==true)missing.push('CONSENT_SCOPE_UNVERIFIED');
 if(e.total_counter_only===true||e.reader_followers_only===true||e.browser_success_only===true)missing.push('WRONG_SOURCE');
 return missing.length?HOLD(missing):{state:'PROVIDER_AGGREGATE_ONLY',count:e.deduplicated_eligible,not_approval_to_send:true};
}
function releaseGate({founder={},subscriber={},native={},offer={},issue_number=0}={}) {
 const fail=[];
 if(![1,2,3,4,5,6].includes(issue_number))fail.push('BAD_ISSUE');
 if(eligibleAggregate(subscriber).state==='HOLD')fail.push('NO_VERIFIED_ELIGIBLE_AGGREGATE');
 if(founder.final_specific_send_authorized!==true||!ISO(founder.approved_at)||founder.issue_number!==issue_number)fail.push('NO_EXPLICIT_FOUNDER_SEND_APPROVAL');
 for(const field of ['actual_received_jetpack_mime','publisher_identity_checked','final_vestige_physical_address_visible','unsub_visible','unsub_function_test_authorized_and_passed','html_and_plaintext_received_checked'])if(native[field]!==true)fail.push('NATIVE_'+field.toUpperCase());
 if([3,5].includes(issue_number)) {
  for(const field of ['named_fv_affiliate_account','email_channel_permission','fv_issued_approved_earning_url','guide_live_and_source_audited','checkout_refund_terms_verified','near_link_disclosure_verified'])if(offer[field]!==true)fail.push('MERCHANT_'+field.toUpperCase());
 }
 return fail.length?HOLD(fail):{state:'HUMAN_RELEASE_REVIEW_ONLY',not_sending:true};
}
function measuredRevenue({session_report={},merchant_report={},cohort={}}={}) {
 const fail=[];
 if(!['7d','30d'].includes(cohort.window)||!ISO(cohort.start)||!ISO(cohort.end)||Date.parse(cohort.end)<=Date.parse(cohort.start))fail.push('NO_VALID_COHORT');
 if(session_report.independently_audited!==true||session_report.deduplicated!==true||!Number.isInteger(session_report.qualified_humans)||session_report.qualified_humans<=0)fail.push('NO_AUDITED_HUMAN_DENOMINATOR');
 if(!session_report.campaign||session_report.campaign!==merchant_report.campaign||session_report.campaign!==cohort.campaign)fail.push('CAMPAIGN_MISMATCH');
 if(merchant_report.independently_reconciled!==true||merchant_report.complete_order_coverage!==true||merchant_report.refund_window_closed!==true||merchant_report.fees_reconciled!==true)fail.push('NO_COMPLETE_SETTLED_MERCHANT_LEDGER');
 if(merchant_report.cohort_start!==cohort.start||merchant_report.cohort_end!==cohort.end||session_report.cohort_start!==cohort.start||session_report.cohort_end!==cohort.end)fail.push('WINDOW_MISMATCH');
 if(!Array.isArray(merchant_report.orders))fail.push('NO_ORDER_RECORDS');
 const orders=Array.isArray(merchant_report.orders)?merchant_report.orders:[];
 const seen=new Set();let gross=0,refund=0,fee=0;
 for(const o of orders){
  if(typeof o.private_order_key!=='string'||!o.private_order_key.startsWith('synthetic:')||seen.has(o.private_order_key)) {fail.push('ORDER_ID_UNSAFE_OR_DUPLICATE');continue;}
  seen.add(o.private_order_key);
  if(o.settlement_verified!==true||o.campaign!==cohort.campaign||![o.gross_usd,o.refunds_usd,o.fees_usd].every(v=>typeof v==='number'&&Number.isFinite(v)&&v>=0)){fail.push('UNRECONCILED_ORDER');continue;}
  gross+=o.gross_usd;refund+=o.refunds_usd;fee+=o.fees_usd;
 }
 if(orders.length===0&&merchant_report.explicit_zero_orders_attested!==true)fail.push('ZERO_ORDERS_NOT_ATTESTED');
 if(fail.length)return {state:'NOT_COMPUTABLE',fail:[...new Set(fail)]};
 const net=gross-refund-fee;
 return {state:'COMPUTABLE_SYNTHETIC_ONLY',cohort:cohort.window,orders:orders.length,gross_usd:+gross.toFixed(2),refunds_usd:+refund.toFixed(2),fees_usd:+fee.toFixed(2),net_usd:+net.toFixed(2),net_per_1000_qhs:+(1000*net/session_report.qualified_humans).toFixed(2),tiny_sample:session_report.qualified_humans<1000,do_not_report_as_actual:true};
}
module.exports={eligibleAggregate,releaseGate,measuredRevenue};
