// R387 — SOURCE-ONLY; never send, subscribe, publish or expose PII.
// Proof requirements are conservative, not substitutes for provider, legal, merchant or founder review.
export function reconcileAudience(subscribers,followers) {
  const required=["total","confirmed","unconfirmed","suppressed"];
  const counts={};
  for(const k of required) {
    if(!Number.isSafeInteger(subscribers?.[k])||subscribers[k]<0) return {status:"INVALID_EVIDENCE",reason:`subscriber.${k} invalid`,email_eligible_inboxes:null};
    counts[k]=subscribers[k];
  }
  if(!Number.isSafeInteger(followers?.email)||followers.email<0||!Number.isSafeInteger(followers?.wpcom)||followers.wpcom<0)
    return {status:"INVALID_EVIDENCE",reason:"follower source unavailable",email_eligible_inboxes:null};
  return {
    status:"REQUIRES_PRIVATE_PROVIDER_ELIGIBILITY_CHECK",
    wpcom_count:followers.wpcom,direct_email_follower_count:followers.email,
    subscribers:counts,nonadditive_count_conflict:counts.total!==counts.confirmed+counts.unconfirmed,
    email_eligible_inboxes:null,confirmed_signup_events:null,
    reason:"Reader followers, confirmed subscribers, pending confirmations and eligible inboxes are different measures; no identity/status join is proven",
    privacy:"No addresses, exports or imports; check provider filtered Email Subscription eligibility privately"
  };
}

export function acceptSignupEvidence(event) {
  if(!event||event.event_name!=="confirmed_signup_v1"||event.source!=="jetpack-authoritative"||
     event.subscription_state!=="confirmed"||event.email_eligible!==true||event.consent_basis!=="provider_record")
    return {accepted:false,reason:"provider email-eligible confirmation absent"};
  if(typeof event.opaque_id!=="string"||!/^opaque_[a-zA-Z0-9_-]{8,}$/.test(event.opaque_id)||
     typeof event.evidence_ref!=="string"||!/^proof:[a-zA-Z0-9/_-]{6,}$/.test(event.evidence_ref))
    return {accepted:false,reason:"non-PII opaque identity and proof reference required"};
  const flat=JSON.stringify(event).toLowerCase();
  if(/"email"|"email_address"|"address"|"ip"|"name":/.test(flat)||/@/.test(flat))
    return {accepted:false,reason:"PII rejected"};
  return {accepted:true,id:event.opaque_id,proof:event.evidence_ref};
}

export function dedupeConfirmedSignups(events) {
  if(!Array.isArray(events)) return {status:"INVALID_EVIDENCE",count:null};
  const seen=new Set(),accepted=[],rejected=[];
  for(const ev of events){
    const p=acceptSignupEvidence(ev);
    if(!p.accepted){rejected.push(p.reason);continue;}
    if(seen.has(p.id)){rejected.push("duplicate provider identity");continue;}
    seen.add(p.id);accepted.push({opaque_id:p.id,proof:p.proof});
  }
  return {status:"PROVIDER_PROOF_ONLY",count:accepted.length,accepted,rejected};
}

export function connectAttribution(row) {
  if(!row||!/^grok_[a-zA-Z0-9_-]{4,}$/.test(row.asset_id||"")||
      !/^fv_[a-zA-Z0-9_-]{4,}$/.test(row.utm_campaign||"")||
      !/^opaque_[a-zA-Z0-9_-]{8,}$/.test(row.signup_id||"")||
      !/^proof:[a-zA-Z0-9/_-]{6,}$/.test(row.signed_join_proof||"")||
      row.provider_join_verified!==true||row.human_session_verified!==true)
    return {status:"UNATTRIBUTED",reason:"No verified privacy-preserving session→signup join"};
  if(Object.keys(row).some(k=>["email","ip","full_name","phone"].includes(k))||JSON.stringify(row).includes("@"))
    return {status:"UNATTRIBUTED",reason:"PII in attribution evidence"};
  return {status:"ATTRIBUTED_CONFIRMED_LEAD",asset_id:row.asset_id,campaign:row.utm_campaign,signup_id:row.signup_id};
}

export function netPublisherRevenue(data) {
  if(!data||data.human_sessions_audited!==true||!Number.isSafeInteger(data.qualified_human_sessions)||data.qualified_human_sessions<=0||
    data.partner_report_complete!==true||!Array.isArray(data.commissions))
    return {status:"NOT_COMPUTABLE",reason:"missing audited human-session denominator or complete merchant report",net_per_1000:null};
  const seen=new Set();let net=0;let paid=0;
  for(const c of data.commissions) {
    if(!c||c.source!=="partner-settlement"||c.status!=="settled"||
       typeof c.order_id!=="string"||!/^order_[a-zA-Z0-9_-]{6,}$/.test(c.order_id)||
       !Number.isFinite(c.publisher_commission_usd)||!Number.isFinite(c.refunds_usd)||!Number.isFinite(c.fees_usd)||
       c.publisher_commission_usd<0||c.refunds_usd<0||c.fees_usd<0||seen.has(c.order_id)||
       Object.hasOwn(c,"retail_total_usd"))
      return {status:"NOT_COMPUTABLE",reason:"invalid/duplicate/unsettled/retail-source commission record",net_per_1000:null};
    seen.add(c.order_id);net+=c.publisher_commission_usd-c.refunds_usd-c.fees_usd;paid++;
  }
  return {status:"COMPUTABLE_FROM_VERIFIED_RECORDS",paid_orders:paid,net_usd:Math.round(net*100)/100,
    net_per_1000:Math.round((net*1000/data.qualified_human_sessions)*100)/100,
    warning:data.qualified_human_sessions<100?"TINY_SAMPLE_NO_INFERENCE":"Descriptive cohort only; not causal"};
}

export function editionGate(number,proof) {
  if(![1,2,3,4,5,6].includes(number))return {state:"INVALID_ISSUE",holds:["not in approved six"]};
  const needs=["founder_final_approval","native_preview_verified","exact_subject_verified","preheader_handling_verified",
    "publisher_postal_verified","native_unsubscribe_verified","eligible_recipient_scope_verified","consent_verified","welcome_delivery_verified"];
  if(number===4)needs.push("apollo_1_correction_approved");
  if(number===3||number===5)needs.push("named_affiliate_approval","sku_specific_email_permission","issued_affiliate_url",
    "approved_live_presell_guide","product_claim_review","referred_checkout_terms_verified","near_offer_disclosure_verified");
  const holds=needs.filter(x=>proof?.[x]!==true);
  return {state:holds.length?"HOLD_UNSENT":"HUMAN_APPROVED_RELEASE_CANDIDATE_ONLY",holds,kind:[3,5].includes(number)?"commercial":"editorial",
    note:"Even a complete offline attestation is not an email send or WordPress publication"};
}
