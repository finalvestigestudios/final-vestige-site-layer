/** FV Dispatch R454: source-only release & proof adjudicator.
 * Pure functions. No file/network/user data IO; NEVER capable of sending mail.
 * A proof flag is a declaration to audit, not independent verification.
 */
export const HARD_HOLD = "HOLD_UNSENT";
export const EXPECTED_KINDS = Object.freeze(["editorial","editorial","commercial","editorial","commercial","editorial"]);
export const EXPECTED_PRODUCTS = Object.freeze([null,null,"Zen12",null,"Hypnosis Live",null]);

export function proof(p) {
  return !!p && typeof p === "object" && p.verified === true
    && typeof p.source_ref === "string"
    && /^(https:\/\/|provider:|sha256:)/.test(p.source_ref)
    && typeof p.checked_at === "string"
    && /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/.test(p.checked_at);
}
export function hasSafeEnvelope(value) {
  return typeof value === "string" && value.trim().length >= 8
    && value.length <= 145 && !/[\r\n]/.test(value)
    && !/^\s*(\*\*|__|#{1,6}\s|>\s)/.test(value)
    && !/<[^>]+>|\*\*|__/.test(value)
    && !/\b(guaranteed|100% effective|miracle cure)\b/i.test(value);
}
export function classifyAudience(s) {
  if(!s || !s.newsletter || !s.subscribers || !s.followers)
    return {status:"UNKNOWN",reason:"missing_provider_surfaces",confirmed_new:null};
  const n=s.newsletter,a=s.subscribers,f=s.followers;
  const values=[n.total,n.confirmed,n.unconfirmed,a.email,a.reader,a.unconfirmed,f.email,f.wpcom];
  if(values.some(v => !Number.isSafeInteger(v) || v<0))
    return {status:"UNKNOWN",reason:"invalid_bucket",confirmed_new:null};
  const conflicts=[];
  if(n.confirmed!==a.email)conflicts.push("newsletter_vs_stats_subscribers_email");
  if(a.email!==f.email)conflicts.push("stats_subscribers_vs_followers_email");
  if(a.reader!==f.wpcom)conflicts.push("stats_subscribers_vs_followers_reader");
  if(n.unconfirmed!==a.unconfirmed)conflicts.push("unconfirmed_buckets");
  return {status:conflicts.length?"CONFLICT":"AGREEMENT_NOT_INDEPENDENT_AUDIENCE_PROOF",
    conflicts,reported_confirmed:n.confirmed,reported_unconfirmed:n.unconfirmed,
    confirmed_new:null,delivered_welcome:null,unique_external_readers:null};
}
export function reviewEdition(issue,context={}) {
  const problems=[];
  if(!issue || !Number.isSafeInteger(issue.number) || issue.number<1 || issue.number>6)
    return {status:HARD_HOLD,can_send:false,problems:["invalid_issue_number"]};
  const i=issue.number-1;
  if(issue.kind!==EXPECTED_KINDS[i])problems.push("incorrect_4_2_identity");
  if((issue.product??null)!==EXPECTED_PRODUCTS[i])problems.push("incorrect_product");
  if(issue.status!==HARD_HOLD)problems.push("attempted_release_state_mutation");
  if(!hasSafeEnvelope(issue.subject) || issue.subject.length>78)
    problems.push("subject_requires_human_review");
  if(!hasSafeEnvelope(issue.preheader))problems.push("preheader_requires_human_review");
  if(typeof issue.body!=="string" || issue.body.trim().length<250)
    problems.push("insufficient_editorial_value");
  if(/INTERNAL REVIEWER NOTES|START REVIEWER NOTES|DO NOT SEND THIS REVIEW/i.test(issue.body||""))
    problems.push("reviewer_notes_leak");
  if(!Array.isArray(issue.sources) || issue.sources.length<2 || issue.sources.some(x=>typeof x!=="string" || !/^https:\/\//.test(x)))
    problems.push("insufficient_https_sources");
  if(!issue.cta || typeof issue.cta.label!=="string" || !issue.cta.label.trim())
    problems.push("missing_cta_copy");
  if(issue.cta?.url && (!/^https:\/\/finalvestige\.com\//.test(issue.cta.url) || issue.cta.url.includes("@")))
    problems.push("unapproved_cta_destination");
  if(issue.kind==="commercial") {
    if(issue.cta?.url)problems.push("commercial_destination_must_stay_inactive_until_release");
    if(!issue.near_cta_disclosure || !/commercial|affiliate|commission|relationship/i.test(issue.near_cta_disclosure))
      problems.push("missing_adjacent_commercial_disclosure");
    if(!proof(context.partner_approval))problems.push("named_partner_approval_missing");
    if(!proof(context.email_channel_rights))problems.push("email_permission_missing");
    if(!proof(context.offer_specific_creative))problems.push("offer_creative_rights_missing");
    if(!proof(context.live_approved_guide))problems.push("live_guide_missing");
    if(!proof(context.merchant_issued_link))problems.push("earning_url_missing");
    if(!proof(context.checkout_terms))problems.push("checkout_terms_missing");
  }
  if(context.site?.email_new_posts_by_default!==false)problems.push("newsletter_auto_send_default_not_off");
  if(context.site?.email_content_format!=="full")problems.push("current_full_content_transport_mismatch");
  if(context.site?.newsletter_categories_enabled!==false)problems.push("segmentation_must_be_reverified");
  if(context.site?.reply_to!=="no-reply")problems.push("reply_to_setting_changed_reverify");
  if(!proof(context.actual_native_preview))problems.push("native_jetpack_preview_not_witnessed");
  if(!proof(context.publisher_postal_address))problems.push("valid_fv_postal_not_witnessed");
  if(!proof(context.functional_unsubscribe))problems.push("functional_opt_out_not_witnessed");
  if(!proof(context.actual_received_welcome))problems.push("actual_welcome_delivery_not_witnessed");
  if(!proof(context.founder_selection))problems.push("founder_editorial_selection_missing");
  if(!proof(context.founder_final_send_authorization))problems.push("founder_final_send_approval_missing");
  // Even all audit flags supplied cannot authorize sending. Runtime has no transport.
  return {status:HARD_HOLD,can_send:false,
    static_review:problems.length?"GAPS":"HUMAN_REVALIDATION_REQUIRED",
    problems,commercial:issue.kind==="commercial",
    note:"Evidence refs are untrusted attestations until externally checked. This tool cannot authorize transmission."};
}
export function planSix(issues,contexts) {
  if(!Array.isArray(issues) || issues.length!==6 || !Array.isArray(contexts) || contexts.length!==6)
    return {status:HARD_HOLD,can_send:false,problems:["six_slot_campaign_required"]};
  if(issues.some((i,n)=>i?.number!==n+1))
    return {status:HARD_HOLD,can_send:false,problems:["order_or_identity_invalid"]};
  const results=issues.map((issue,n)=>reviewEdition(issue,contexts[n]));
  return {status:HARD_HOLD,can_send:false,
    allocation:{editorial:results.filter(x=>!x.commercial).length,commercial:results.filter(x=>x.commercial).length},
    results};
}
export function classifyMoney(x) {
  if(!x || !proof(x.settlement_proof) || !proof(x.qualified_human_sessions_proof)
    || !Number.isSafeInteger(x.qualified_human_sessions) || x.qualified_human_sessions<=0
    || x.ledger_complete!==true || !Array.isArray(x.orders))
    return {status:"UNCOMPUTABLE",net_per_1000_cents:null};
  const seen=new Set(); let net=0, paid=0;
  for(const row of x.orders) {
    if(!row || typeof row.id!=="string" || !row.id || seen.has(row.id)
      || row.status!=="settled" || !proof(row.proof)
      || !["merchant_order","affiliate_commission"].includes(row.kind)
      || ![row.gross_cents,row.fees_cents,row.refund_cents].every(n=>Number.isSafeInteger(n)&&n>=0)
      || row.fees_cents+row.refund_cents>row.gross_cents)
      return {status:"UNCOMPUTABLE",net_per_1000_cents:null};
    seen.add(row.id); net+=row.gross_cents-row.fees_cents-row.refund_cents; paid++;
  }
  return {status:"PROVISIONAL_AUDIT_ONLY",settled_count:paid,
    net_cents:net,net_per_1000_cents:Math.round(net*1000/x.qualified_human_sessions),
    warning:"Proof objects must be independently checked and orders attributed; no real-site revenue supplied."};
}
