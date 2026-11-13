'use strict';
/**
 * Read-only, fail-closed Dispatch release adjudicator.
 * This is a reviewer, not a send authorization, enrollment tool or production analytics script.
 * All actual personal or merchant credentials MUST be kept out of the input.
 */
function decide(s){
  const reasons=[];
  if(!s || typeof s!=='object') return {result:'HOLD_UNSENT',can_send:false,reasons:['no authenticated snapshot']};
  const w=s.jetpack||{},m=s.merchant||{},a=s.attribution||{};
  if(s.send_authorized!==false) reasons.push('no founder-final send proof; boolean cannot authorize sending');
  if(w.enabled!==true) reasons.push('newsletter unavailable');
  if(w.auto_send_default!==false) reasons.push('unexpected default-email configuration');
  if(!Number.isInteger(w.total)||!Number.isInteger(w.confirmed)||!Number.isInteger(w.unconfirmed)||w.total<w.confirmed+w.unconfirmed) reasons.push('counts overlap, classify recipient by provider not arithmetic');
  if(!Number.isInteger(w.email_eligible_count)) reasons.push('real email-eligible recipient count unknown');
  if(w.actual_welcome_received!==true) reasons.push('configured welcome is not a received welcome');
  if(w.provider_email_client_preview_verified!==true) reasons.push('real Jetpack preview/receipt not verified');
  if(m.postal_address_verified!==true) reasons.push('verified Final Vestige mailing address absent');
  if(m.unsubscribe_working_verified!==true) reasons.push('native unsubscribe function absent');
  const merchantOK=m.zen12_email_marketing_permission===true&&typeof m.zen12_issued_affiliate_link==='string'&&m.zen12_issued_affiliate_link.startsWith('https://')&&m.zen12_approved_first_party_guide===true;
  if(!merchantOK) reasons.push('commercial Zen12 guide/EMAIL-rights/earning URL incomplete');
  const revenueEvidence=Number.isInteger(a.qualified_human_sessions)&&a.qualified_human_sessions>0&&Number.isInteger(a.settled_commission_cents)&&Number.isInteger(a.refund_cents)&&Number.isInteger(a.fees_cents)&&Number.isInteger(a.settled_orders);
  const net_per_1000=revenueEvidence?((a.settled_commission_cents-a.refund_cents-a.fees_cents)/100)*1000/a.qualified_human_sessions:null;
  return {result:'HOLD_UNSENT',can_send:false,release_reasons:reasons,recipient_count:'UNKNOWN_UNTIL_PROVIDER_VERIFIED',net_revenue_per_1000:net_per_1000,net_revenue_status:revenueEvidence?'SYNTHETIC_OR_SOURCE_UNVERIFIED':'NOT_COMPUTABLE',commercial_issue_status:merchantOK?'REQUIRES_INDEPENDENT_ACCOUNT_REVIEW':'HOLD_MERCHANT'};
}
module.exports={decide};
