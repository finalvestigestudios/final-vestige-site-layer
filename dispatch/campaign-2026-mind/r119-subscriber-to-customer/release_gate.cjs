"use strict";
/* FV R119: OFFLINE evidence evaluator. Never accesses network, WordPress or an email service. */
const proofKeys=["native_wp_confirmed_consent","eligible_email_subscription","received_fieldbook_welcome","fieldbook_public_retrieval","jetpack_editor_preview","received_email_footer","valid_publisher_postal_address","working_unsubscribe","founder_send_release","merchant_account_accepted","merchant_email_channel_allowed","merchant_link_verified","approved_live_buyer_guide","current_checkout_terms","merchant_privacy_safe_paid_reporting"];
const commercial=new Set([3,5]);
function validProof(x,role){
  return !!(x && x.passed===true && typeof x.evidenceRef==="string" && /^PRIVATE-[A-Z0-9_-]{6,}$/.test(x.evidenceRef) && typeof x.observedAt==="string" && /^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$/.test(x.observedAt) && (!role || x.authority===role));
}
function normalizeEvidence(evidence){
  if(!evidence || typeof evidence!=="object" || Array.isArray(evidence))return {};
  const copy={};for(const k of proofKeys){copy[k]=validProof(evidence[k],k==="merchant_email_channel_allowed"?"merchant":undefined);}
  return copy;
}
function inspect(spec,evidence={}){
  if(!spec || spec.schema!=="FV_DISPATCH_R119_2026_11_04" || !Array.isArray(spec.editions) || spec.editions.length!==6) throw Error("Invalid manifest");
  if(spec.wordpress.newsletter_enabled!==true||spec.wordpress.send_new_posts_default!==false||spec.wordpress.email_format!=="excerpt") throw Error("State changed; reverify WordPress before any decision");
  const n=spec.wordpress.counts;
  if(!Number.isInteger(n.total)||n.total<0||!Number.isInteger(n.confirmed)||n.confirmed<0||!Number.isInteger(n.unconfirmed)||n.unconfirmed<0)throw Error("Invalid subscriber count");
  const p=normalizeEvidence(evidence);
  const contactReady=p.native_wp_confirmed_consent && p.eligible_email_subscription && p.received_fieldbook_welcome && p.fieldbook_public_retrieval;
  const legalTransportReady=p.jetpack_editor_preview && p.received_email_footer && p.valid_publisher_postal_address && p.working_unsubscribe;
  const merchantReady=p.merchant_account_accepted && p.merchant_email_channel_allowed && p.merchant_link_verified && p.approved_live_buyer_guide && p.current_checkout_terms && p.merchant_privacy_safe_paid_reporting;
  const editorialCanRelease=contactReady&&legalTransportReady&&p.founder_send_release;
  const editions=spec.editions.map(x=>{
    const isCommercial=commercial.has(x.n);
    const hold=[...(!contactReady?["CONSENT_REACHABILITY_WELCOME_UNPROVEN"]:[]),...(!legalTransportReady?["JETPACK_POSTAL_UNSUBSCRIBE_UNPROVEN"]:[]),...(!p.founder_send_release?["FOUNDER_RELEASE_UNAPPROVED"]:[]),...(isCommercial&&!merchantReady?["MERCHANT_CHANNEL_GUIDE_PAYOUT_UNVERIFIED"]:[]),...(x.n===4?["ORIGINAL_UNSUPPORTED_APOLLO_SUBJECT"]:[])];
    return {edition:x.n,kind:x.kind,hold,eligibleForApproval:!hold.length,sendAction:"NEVER_AUTO_SEND",destination:isCommercial?null:x.destination,attributionCandidate:"utm_source=dispatch&utm_medium=email&utm_campaign=dispatch_mind_pilot_2026_11&utm_content=issue_0"+x.n};
  });
  return {release:"HOLD_ALL_UNSENT",subscriberCountsNonadditive:true,reportedTotal:n.total,confirmed:n.confirmed,unconfirmed:n.unconfirmed,reachableEmailRecipients:"UNKNOWN_NOT_INFERRED",fieldbookActuallyReceived:p.received_fieldbook_welcome?"PRIVATE_EVIDENCE_REVIEWED":"NOT_VERIFIED",contactReady,legalTransportReady,merchantReady,editorialCanRelease,editions,paidOrders:"NOT_VERIFIED",netPer1000QualifiedHumanSessions:"NOT_COMPUTABLE"};
}
function revenuePer1000({qualifiedSessions,orders,refunds,fees}={}){
  if(!Number.isInteger(qualifiedSessions)||qualifiedSessions<=0||!Array.isArray(orders)||!Array.isArray(refunds)||!Array.isArray(fees))return {state:"NOT_COMPUTABLE",reason:"MISSING_QUALIFIED_HUMAN_DENOMINATOR_OR_SETTLED_TRANSACTION_RECORDS"};
  const check=(a)=>a.every(x=>x&&typeof x.opaqueOrderRef==="string"&&/^[A-Za-z0-9_-]{6,64}$/.test(x.opaqueOrderRef)&&Number.isFinite(x.amountCents)&&Number.isInteger(x.amountCents)&&x.amountCents>=0&&x.authority==="merchant_report");
  if(!check(orders)||!check(refunds)||!check(fees)||orders.some(x=>x.settled!==true)||new Set(orders.map(x=>x.opaqueOrderRef)).size!==orders.length)return {state:"NOT_COMPUTABLE",reason:"TRANSACTION_NOT_INDEPENDENTLY_VERIFIED_OR_DUPLICATED"};
  if(orders.length===0)return {state:"NOT_COMPUTABLE",reason:"NO_AUTHORITATIVE_PAID_ORDER_COHORT_RECORDED"};
  const ids=new Set(orders.map(x=>x.opaqueOrderRef));if([...refunds,...fees].some(x=>!ids.has(x.opaqueOrderRef)))return {state:"NOT_COMPUTABLE",reason:"UNMATCHED_REFUND_OR_FEE"};
  const gross=orders.reduce((s,x)=>s+x.amountCents,0),deduct=[...refunds,...fees].reduce((s,x)=>s+x.amountCents,0);
  return {state:"COMPUTABLE_FROM_PROVIDED_EVIDENCE_ONLY",qualifiedSessions,confirmedOrders:orders.length,grossCents:gross,netCents:gross-deduct,netRevenuePer1000QualifiedSessionsCents:Math.round((gross-deduct)*1000/qualifiedSessions)};
}
module.exports={inspect,normalizeEvidence,revenuePer1000,validProof};
