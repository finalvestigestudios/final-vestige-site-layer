"use strict";
// Pure, offline, consent-only validation. NO integrations, NO network, NO sending.
// Do not use frontend UI signals to create a confirmed_signup.
const UI_ONLY = new Set([
  "focus_signup_click","focus_pdf_click","focus_download_panel_shown",
  "subscribe_query","jetpack_ui_subscriber_class","reader_follow",
  "wordpress_reader_follower","newsletter_dashboard_count","welcome_configured"
]);
const DISALLOWED_KEYS = ["email","email_address","ip","ip_address","name","phone","email_hash"];
function classify(observation) {
  if (!observation || typeof observation !== "object" || Array.isArray(observation))
    return {kind:"invalid",confirmed:false,reason:"not an evidence object"};
  const type=observation.type;
  if (UI_ONLY.has(type)) return {kind:"ui_or_summary",confirmed:false,reason:"not provider-authoritative"};
  if (type !== "provider_subscription_transition")
    return {kind:"invalid",confirmed:false,reason:"unrecognized evidence type"};
  if (DISALLOWED_KEYS.some(k=>Object.prototype.hasOwnProperty.call(observation,k)))
    return {kind:"invalid",confirmed:false,reason:"personal information prohibited"};
  const required=["provider","opaque_id","previous_status","current_status","evidence_ref","consent_scope","effective_at","email_subscription","delivery_eligible"];
  if (required.some(k=>!Object.prototype.hasOwnProperty.call(observation,k)))
    return {kind:"invalid",confirmed:false,reason:"required provider evidence absent"};
  if (observation.provider!=="wordpress_jetpack" ||
      typeof observation.opaque_id!=="string" || !/^[A-Za-z0-9_-]{6,128}$/.test(observation.opaque_id) ||
      typeof observation.evidence_ref!=="string" || !/^[A-Za-z0-9_:/.#-]{8,256}$/.test(observation.evidence_ref))
    return {kind:"invalid",confirmed:false,reason:"provider identity or evidence reference invalid"};
  if (observation.consent_scope!=="dispatch" ||
      !["pending","unconfirmed","none"].includes(observation.previous_status) ||
      observation.current_status!=="subscribed" ||
      observation.email_subscription!=="subscribed" ||
      observation.delivery_eligible!==true)
    return {kind:"invalid",confirmed:false,reason:"no qualifying provider consent transition"};
  if (typeof observation.effective_at!=="string" ||
      !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$/.test(observation.effective_at) ||
      Number.isNaN(Date.parse(observation.effective_at)))
    return {kind:"invalid",confirmed:false,reason:"non-UTC or invalid provider timestamp"};
  return {kind:"provider_confirmed",confirmed:true,reason:"opaque qualified provider transition"};
}
function aggregateConfirmed(events) {
  if (!Array.isArray(events)) throw new TypeError("events must be an array");
  const seen=new Set();let confirmed=0,duplicates=0,rejected=0,non_lead=0;
  for (const e of events) {
    const status=classify(e);
    if (!status.confirmed) {if(status.kind==="ui_or_summary")non_lead++;else rejected++;continue;}
    const key=e.provider+":"+e.opaque_id;
    if (seen.has(key)){duplicates++;continue;}
    seen.add(key);confirmed++;
  }
  return {confirmed_signup:confirmed,duplicates,rejected,non_lead,
    recipients_count_known:false,authorized_to_send:false};
}
function giftPanelVisible({subscribeQuery=null,isSubscriberClass=false}={}) {
  const blocked=["invalid_email","error","blocked_email","opted_out","blocked"];
  return (typeof subscribeQuery==="string" && subscribeQuery!=="" && !blocked.includes(subscribeQuery)) ||
    isSubscriberClass===true;
}
function releaseDecision() {return {authorized_to_send:false,reason:"no authority to send from software evidence"};}
module.exports={classify,aggregateConfirmed,giftPanelVisible,releaseDecision};
