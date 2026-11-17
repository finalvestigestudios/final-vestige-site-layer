// R423 proof-boundary checker. READ ONLY; cannot authorize or execute a send.
// Pure function: accepts opaque aggregate proof metadata, no subscriber PII.
export function assessDispatchLedger(input) {
  const defects = [];
  const o = input && typeof input === "object" && !Array.isArray(input) ? input : {};
  if (o.schema !== "fv-dispatch-proof-boundary-v1") defects.push("schema_not_recognized");
  const issues = Array.isArray(o.issues) ? o.issues : [];
  if (issues.length !== 6 || new Set(issues.map(x => x.slot)).size !== 6 ||
      ![1,2,3,4,5,6].every(n => issues.some(x => x.slot === n)))
    defects.push("six_distinct_issues_required");
  if (issues.filter(x => x.kind === "commercial").length !== 2 ||
      issues.filter(x => x.kind === "editorial").length !== 4 ||
      ![3,5].every(n => issues.some(x => x.slot === n && x.kind === "commercial")))
    defects.push("original_4_to_2_mix_violation");
  const allowedStatuses = ["HOLD_UNSENT","HOLD_MERCHANT","HOLD_COPY"];
  if (issues.some(x => !allowedStatuses.includes(x.status))) defects.push("original_release_hold_missing");
  const snap = o.live_settings || {};
  if (snap.post_auto_send !== false) defects.push("automatic_sends_changed");
  if (snap.newsletter_enabled !== true) defects.push("newsletter_state_unexpected");
  if (!o.dashboard || ![o.dashboard.total,o.dashboard.confirmed,o.dashboard.unconfirmed].every(n=>Number.isInteger(n)&&n>=0))
    defects.push("invalid_dashboard_aggregate");
  if (!o.follower_stats || o.follower_stats.partial !== false ||
      ![o.follower_stats.reader,o.follower_stats.email].every(n=>Number.isInteger(n)&&n>=0))
    defects.push("follower_diagnostics_missing");
  // A dashboard 'confirmed' metric is NOT a recipient-audience attestation.
  const eligible = Number.isInteger(o.unique_eligible_recipients) && o.unique_eligible_recipients >= 1;
  if (!eligible) defects.push("unique_email_eligible_audience_unverified");
  if (o.welcome_email_received_verified !== true) defects.push("welcome_receipt_unverified");
  if (o.native_jetpack_preview_verified !== true) defects.push("jetpack_native_preview_unverified");
  if (o.final_vestige_postal_address_verified !== true) defects.push("sender_physical_postal_address_unverified");
  if (o.functional_unsubscribe_verified !== true) defects.push("unsubscribe_not_witnessed");
  if (o.merchant_partner_named_approval_verified !== true) defects.push("named_partner_approval_missing");
  if (o.merchant_email_channel_permission_verified !== true) defects.push("merchant_EMAIL_permission_missing");
  if (o.merchant_specific_affiliate_link_verified !== true) defects.push("issued_affiliate_link_missing");
  if (o.approved_live_warmup_guide_verified !== true) defects.push("approved_warmup_guide_not_live");
  if (o.referred_sku_checkout_verified !== true) defects.push("actual_referred_checkout_unverified");
  // No content in this checker can establish authenticity of an external attestation.
  const s = JSON.stringify(o);
  if (/@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/.test(s)) defects.push("email_address_PII_in_public_ledger");
  if (/https?:\/\/[^"\s]+(?:[?&](?:aff|affiliate|subid|ref|click_id|token|utm_email)=)/i.test(s))
    defects.push("active_tracking_or_private_partner_url_in_public_ledger");
  const revenue = o.audit_revenue || {};
  const audited = o.qualified_human_sessions_audited === true &&
                  o.merchant_attributed_settled_orders_verified === true &&
                  Number.isInteger(revenue.qualified_human_sessions) &&
                  revenue.qualified_human_sessions > 0 &&
                  Number.isFinite(revenue.net_revenue);
  if (!audited && revenue.net_revenue_per_1000_qualified_human_sessions !== null)
    defects.push("unverified_revenue_quoted");
  // A green preflight can never authorize sending by itself.
  const verdict = defects.length ? "HOLD_UNSENT" : "FOUNDER_REVIEW_REQUIRED_NO_SEND";
  return { verdict, defects: [...new Set(defects)].sort(), qualifiedAudienceCount: eligible ? o.unique_eligible_recipients : null,
    netRevenuePer1000: audited ? revenue.net_revenue*1000/revenue.qualified_human_sessions : null,
    authorityToSend: false };
}
