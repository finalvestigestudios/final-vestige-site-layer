/** FINAL VESTIGE DISPATCH R453 | SOURCE ONLY | NO EMAIL, PAYMENT OR NETWORK IO.
 * Pure privacy-preserving evidence checks. This module NEVER sends or authorizes an email.
 * Strictly distinguish a validated conversion witness from unverified counts or clicks.
 */
export const RELEASE_STATE = "HOLD_UNSENT";

export function validProof(p) {
  return !!p && typeof p==="object" && p.verified===true && typeof p.source_ref==="string" && /^https:\/\/|^sha256:|^provider:/.test(p.source_ref) && typeof p.checked_at==="string" && /^\d{4}-\d{2}-\d{2}T/.test(p.checked_at);
}

export function assessProviderCounts(feeds) {
  if(!feeds || !feeds.newsletter || !feeds.statsSubscribers || !feeds.statsFollowers) return {status:"UNKNOWN",reason:"not_all_three_feeds_available"};
  const n=feeds.newsletter,s=feeds.statsSubscribers,f=feeds.statsFollowers;
  const nums=[n.confirmed,n.unconfirmed,n.total,s.email,s.reader,f.email,f.wpcom];
  if(nums.some(x=>!Number.isSafeInteger(x)||x<0)) return {status:"UNKNOWN",reason:"invalid_provider_count"};
  const conflicts=[];
  if(n.confirmed!==s.email) conflicts.push("newsletter_confirmed_vs_subscriber_email");
  if(s.email!==f.email) conflicts.push("subscriber_email_vs_followers_email");
  if(s.reader!==f.wpcom) conflicts.push("subscriber_reader_vs_followers_reader");
  if(n.unconfirmed!==s.unconfirmed) conflicts.push("newsletter_unconfirmed_vs_subscribers_unconfirmed");
  return {status:conflicts.length?"DISAGREE":"AGREE",conflicts,provider_reported_email_eligible:n.confirmed,independently_acquired_leads:null,welcomes_delivered:null,unique_people:null};
}

export function validateCampaign(campaign) {
  if(!campaign||!Array.isArray(campaign.issues)||campaign.issues.length!==6) return {status:"HOLD",errors:["six_issues_required"]};
  const expected=["editorial","editorial","commercial","editorial","commercial","editorial"];
  const errors=[];
  for(let i=0;i<6;i++){
    const issue=campaign.issues[i];
    if(!issue||issue.number!==i+1||issue.kind!==expected[i]) errors.push(`issue_${i+1}_kind_or_number`);
    if(issue?.send_status!=="HOLD_UNSENT") errors.push(`issue_${i+1}_not_held`);
    if(i===2&&issue?.product!=="Zen12") errors.push("zen12_identity");
    if(i===4&&issue?.product!=="Hypnosis Live") errors.push("hypnosislive_identity");
  }
  return {status:"HOLD",errors,can_send:false,reason:"founder_final_send_approval_and_external_proofs_not_attested"};
}

export function assessSignup(event) {
  if(!event||event.type!=="provider_confirmation"||event.provider!=="jetpack")return {counted:false,reason:"not_a_provider_confirmation"};
  if(event.prior_status!=="unconfirmed"||event.new_status!=="confirmed_email")return {counted:false,reason:"not_a_new_email_confirmation"};
  if(event.existing_confirmed===true||event.is_reader_only===true||event.is_suppressed===true)return {counted:false,reason:"not_a_new_eligible_contact"};
  if(!validProof(event.provider_proof))return {counted:false,reason:"no_confirmed_transition_proof"};
  return {counted:true,reason:"verified_new_confirmation"};
}

export function assessUtm(event) {
  const platforms=["youtube","tiktok","instagram","facebook","pinterest","x","bluesky"];
  if(!event||!platforms.includes(event.utm_source)||event.utm_medium!=="organic_social")return false;
  if(!/^[a-z0-9_]+_pilot_20\d{2}_\d{2}$/.test(event.utm_campaign||""))return false;
  return typeof event.utm_content==="string" && /^[a-zA-Z0-9_-]{3,96}$/.test(event.utm_content);
}

export function sumRevenue(windowData) {
  if(!windowData||!Number.isSafeInteger(windowData.qualified_human_sessions)||windowData.qualified_human_sessions<0)return {status:"UNCOMPUTABLE",reason:"audited_session_denominator_absent"};
  if(!validProof(windowData.sessions_proof))return {status:"UNCOMPUTABLE",reason:"session_proof_missing"};
  if(!windowData.orders_complete||!validProof(windowData.order_ledger_proof)||!Array.isArray(windowData.orders))return {status:"UNCOMPUTABLE",reason:"settlement_ledger_not_complete"};
  const seen=new Map();let gross=0,fees=0,refunds=0,orders=0,attributed=0;
  for(const item of windowData.orders) {
    if(!item||typeof item.order_id!=="string"||!item.order_id||!["paid_order","paid_affiliate_commission"].includes(item.type)||item.state!=="settled"||!validProof(item.settlement_proof))return {status:"UNCOMPUTABLE",reason:"order_not_independently_settled"};
    if([item.gross_cents,item.fees_cents,item.refunds_cents].some(x=>!Number.isSafeInteger(x)||x<0)||item.fees_cents+item.refunds_cents>item.gross_cents)return {status:"UNCOMPUTABLE",reason:"invalid_settlement_accounting"};
    const fingerprint=JSON.stringify([item.type,item.gross_cents,item.fees_cents,item.refunds_cents,item.state,item.attribution_proof?.source_ref||""]);
    if(seen.has(item.order_id)){
      if(seen.get(item.order_id)!==fingerprint)return {status:"UNCOMPUTABLE",reason:"conflicting_duplicate_order"};
      continue;
    }
    seen.set(item.order_id,fingerprint);
    gross+=item.gross_cents;fees+=item.fees_cents;refunds+=item.refunds_cents;orders++;
    if(validProof(item.attribution_proof)&&assessUtm(item.campaign))attributed++;
  }
  const net=gross-fees-refunds;
  const denom=windowData.qualified_human_sessions;
  return {status:denom>0?"COMPUTABLE":"UNCOMPUTABLE",reason:denom>0?null:"zero_qualified_sessions",orders,orders_with_independently_justified_campaign_attribution:attributed,gross_cents:gross,fees_cents:fees,refunds_cents:refunds,net_cents:net,net_revenue_per_1000_cents:denom>0?Math.round(net*1000/denom):null,warning:"A conversion is attributed only with a separate evidence reference. This is a reporting-window metric, not a causal experiment or an acquisition cohort."};
}
