function classifyGuest(observation) {
  if (!observation || typeof observation !== "object") return {status:"NOT_TESTED",can_submit:null};
  const publicInput=observation.public_form_email_input===true;
  const wpSelflink=observation.wp_view_self_link===true;
  if (publicInput) return {status:"VISIBLE_FORM_STRUCTURE_ONLY",can_submit:null,source_disagreement:wpSelflink};
  if (wpSelflink) return {status:"WP_VIEW_SELF_LINK_ONLY",can_submit:null,source_disagreement:false};
  return {status:"NO_FORM_EVIDENCE",can_submit:null,source_disagreement:false};
}

function reconcileSubscribers(s) {
  const fields=["total","confirmed","unconfirmed","wp_followers","direct_email_followers"];
  if (!s || fields.some(k=>!Number.isInteger(s[k])||s[k]<0)) return {state:"INVALID_SNAPSHOT",eligible_recipients:null};
  const conflict=s.total!==s.confirmed+s.unconfirmed;
  return {state:conflict?"OVERLAPPING_OR_INCONSISTENT":"AGGREGATES_ONLY",counts_non_additive:conflict,eligible_recipients:null,provider_confirmation_events:null,wp_followers:s.wp_followers,direct_email_followers:s.direct_email_followers};
}

function countConfirmedSignup(ev,seen) {
  if (!ev || !seen || typeof seen.has!=="function") return false;
  if (ev.provider!=="jetpack" || ev.status!=="confirmed" || ev.marketing_permission_verified!==true || !ev.provider_confirmation_event_id || !ev.confirmed_at || !ev.consent_provenance) return false;
  if (seen.has(ev.provider_confirmation_event_id)) return false;
  seen.add(ev.provider_confirmation_event_id);
  return true;
}

function attributeTouch(record) {
  if (!record || typeof record!=="object") return {first_touch:null,last_touch:null};
  const first=record.verified_first_touch || null;
  const last=record.verified_email_touch || null;
  return {first_touch:first,last_touch:last,first_touch_preserved:!!first};
}

function revenueKpi(input) {
  if (!input || input.owner_reconciled!==true || !Number.isInteger(input.qualified_human_sessions) || input.qualified_human_sessions<=0 || !Array.isArray(input.orders)) return {net_revenue_per_1000:null,reason:"MISSING_OWNER_ATTESTED_SESSION_AND_SETTLEMENT_EVIDENCE"};
  const seen=new Set(); let gross=0,fees=0,refunds=0,orders=0;
  for(const x of input.orders) {
    if (!x || x.independent_settlement_verified!==true || x.payment_status!=="settled" || !x.order_id || x.currency!=="USD" || !["gross_minor","fees_minor","refund_minor"].every(k=>Number.isInteger(x[k])&&x[k]>=0)) return {net_revenue_per_1000:null,reason:"UNVERIFIED_OR_INVALID_SETTLEMENT"};
    if(seen.has(x.order_id)) continue;
    seen.add(x.order_id); gross+=x.gross_minor; fees+=x.fees_minor; refunds+=x.refund_minor;orders++;
  }
  const net_minor=gross-fees-refunds;
  return {net_revenue_per_1000:Number((net_minor/100/input.qualified_human_sessions*1000).toFixed(2)),currency:"USD",verified_orders:orders,net_minor,qualified_human_sessions:input.qualified_human_sessions,tiny_sample:input.qualified_human_sessions<1000||orders<30};
}

function releaseDecision(edition,evidence) {
  const isCommercial=edition===3||edition===5;
  const held=["founder_final_creative_and_send_approval","provider_eligible_audience_receipt","received_welcome_and_fieldbook","native_jetpack_email_preview","actual_publisher_postal_address","functional_unsubscribe"];
  if(isCommercial) held.push("named_affiliate_acceptance","explicit_email_channel_permission","merchant_issued_earning_url","approved_live_guide","exact_checkout_refund_claims");
  const missing=held.filter(x=>!evidence || !evidence[x] || evidence[x].verified!==true || !evidence[x].source || !evidence[x].reviewer);
  return {status:"HOLD_UNSENT",commercial_status:isCommercial?"HOLD_MERCHANT":"EDITORIAL_HOLD",missing_evidence:missing,requires_human_final_approval:true};
}

export {classifyGuest,reconcileSubscribers,countConfirmedSignup,attributeTouch,revenueKpi,releaseDecision};
