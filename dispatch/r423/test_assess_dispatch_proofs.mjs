// Exact GitHub source can run in V8 or native Node. All fixtures synthetic.
// This test runner deliberately does not interact with WordPress, email or commerce.
export function runProofTests(assess, original) {
  let passed = 0;
  const copy = x => JSON.parse(JSON.stringify(x));
  const check = (condition, label) => { if (!condition) throw new Error("FAIL: "+label); passed++; };
  const baseline = assess(original);
  check(baseline.verdict === "HOLD_UNSENT","baseline held");
  check(baseline.authorityToSend === false,"baseline no send");
  check(baseline.qualifiedAudienceCount === null,"no invented eligible recipients");
  check(baseline.netRevenuePer1000 === null,"no invented monetization");
  check(baseline.defects.includes("merchant_EMAIL_permission_missing"),"email rights missing");
  check(baseline.defects.includes("jetpack_native_preview_unverified"),"native preview missing");
  check(baseline.defects.includes("sender_physical_postal_address_unverified"),"postal address missing");
  check(baseline.defects.includes("unsubscribe_not_witnessed"),"unsub missing");
  check(baseline.defects.includes("unique_email_eligible_audience_unverified"),"stats not consent proof");
  const sourceMutation = mutate => {let x=copy(original); mutate(x); return assess(x);};
  check(sourceMutation(x=>x.live_settings.post_auto_send=true).defects.includes("automatic_sends_changed"),"detect auto-on drift");
  check(sourceMutation(x=>x.issues[0].kind="commercial").defects.includes("original_4_to_2_mix_violation"),"reject 3 commercial");
  check(sourceMutation(x=>x.issues[5].slot=1).defects.includes("six_distinct_issues_required"),"reject repeated issue");
  check(sourceMutation(x=>x.issues[0].status="READY_TO_SEND").defects.includes("original_release_hold_missing"),"reject send-ready status");
  check(sourceMutation(x=>x.dashboard.total=-1).defects.includes("invalid_dashboard_aggregate"),"reject negative totals");
  check(sourceMutation(x=>x.dashboard.confirmed=3.5).defects.includes("invalid_dashboard_aggregate"),"reject fractional totals");
  check(sourceMutation(x=>x.follower_stats.partial=true).defects.includes("follower_diagnostics_missing"),"reject partial stats");
  check(sourceMutation(x=>x.source_links.push("mailto:private@example.com")).defects.includes("email_address_PII_in_public_ledger"),"reject email PII");
  check(sourceMutation(x=>x.source_links.push("https://merchant.example/offer?affiliate=private")).defects.includes("active_tracking_or_private_partner_url_in_public_ledger"),"reject tracked outbound");
  check(sourceMutation(x=>x.audit_revenue.net_revenue_per_1000_qualified_human_sessions=100).defects.includes("unverified_revenue_quoted"),"reject fake revenue");
  check(sourceMutation(x=>x.unique_eligible_recipients=0).qualifiedAudienceCount===null,"zero not confirmed people");
  check(sourceMutation(x=>x.unique_eligible_recipients=3).verdict==="HOLD_UNSENT","raw count not sufficient");
  check(sourceMutation(x=>x.welcome_email_received_verified=true).verdict==="HOLD_UNSENT","welcome alone insufficient");
  check(sourceMutation(x=>x.merchant_partner_named_approval_verified=true).verdict==="HOLD_UNSENT","generic approval alone insufficient");
  check(sourceMutation(x=>x.native_jetpack_preview_verified=true).verdict==="HOLD_UNSENT","preview alone insufficient");
  check(sourceMutation(x=>x.follower_stats.email=0).verdict==="HOLD_UNSENT","no-email follower count not send authority");
  check(sourceMutation(x=>x.follower_stats.reader=999).qualifiedAudienceCount===null,"Reader audience not email audience");
  let full=copy(original);
  for(let k of Object.keys(full)) if(k.endsWith("_verified")) full[k]=true;
  full.unique_eligible_recipients=3;
  let end=assess(full);
  check(end.authorityToSend === false,"even full self-attestation cannot send");
  check(["HOLD_UNSENT","FOUNDER_REVIEW_REQUIRED_NO_SEND"].includes(end.verdict),"human approval still required");
  // Synthetic financial arithmetic is never reported as real: 'demonstration' only.
  full.qualified_human_sessions_audited=true;
  full.merchant_attributed_settled_orders_verified=true;
  full.audit_revenue.qualified_human_sessions=100;
  full.audit_revenue.net_revenue=20;
  check(assess(full).netRevenuePer1000===200,"synthetic arithmetic");
  check(assess({}).authorityToSend===false,"null evidence cannot authorize");
  check(assess(null).authorityToSend===false,"null input cannot authorize");
  return {passed,fixture:"synthetic",sender:"NONE",status:"PASS",authorityToSend:false};
}
