"use strict";
/* Pure, non-sending QA. No network, cookies, identifiers, storage, or mutations. */
function assess(x) {
  const errors=[],holds=[];
  if (!x || typeof x!=="object" || Array.isArray(x)) return {errors:["invalid snapshot"],holds:[],release_authorized:false};
  function fail(id,passed,reason){if(!passed)holds.push({id,reason});}
  function integer(v){return Number.isSafeInteger(v)&&v>=0;}
  function privateKeys(o){
    if(!o||typeof o!=="object")return false;
    return Object.entries(o).some(([k,v])=>/^(email|email_address|subscriber_email|subscriber_name|user_id|subscription_id|full_name|ip_address)$/i.test(k)||privateKeys(v));
  }
  if(privateKeys(x))errors.push("private subscriber identifiers forbidden in public QA snapshot");
  const c=x.provider_counts||{},p=x.provider_proof||{},w=x.wordpress||{},m=x.merchant||{},r=x.receipts||{},a=x.attribution||{};
  if(!["1.0"].includes(String(x.schema_version)))errors.push("unsupported schema version");
  if(!integer(c.dashboard_total)||!integer(c.confirmed)||!integer(c.unconfirmed)||!integer(c.email_filter_total)||!integer(c.reader_only_total))errors.push("invalid aggregate count");
  const observed=!!p.authoritative_filter_read&&p.email_rows_all_subscribed===true&&p.email_rows_all_email_subscriber===true&&c.email_filter_total===c.confirmed&&c.dashboard_total===c.confirmed&&c.reader_only_total===0&&!errors.length;
  fail("provider_email_eligibility",observed,"Need current authoritative Subscribers filter with each row status=Subscribed and email_subscriber=true; dashboard/Reader counters alone never suffice");
  fail("confirmed_signup_event",p.provider_event_join_validated===true,"Eligibility snapshot is not proof of a newly confirmed_signup event, nor permission to infer an attribution join");
  fail("welcome_delivery",p.received_welcome_with_fieldbook===true,"Configured welcome and PDF Media Library entry do not prove a received message/download");
  fail("native_jetpack_preview",p.native_non_sending_preview_witnessed===true,"Offline HTML preview is not rendered WordPress/Jetpack email");
  fail("public_promise",w.dispatch_copy_matches_manual_cadence===true,"Live Dispatch copy implies per-post email while automatic new-post mail is off");
  fail("publisher_postal",w.final_vestige_valid_postal_witnessed===true,"FTC publisher address is required; Automattic/vendor postal address is not the publisher's");
  fail("working_unsubscribe",w.working_unsubscribe_witnessed===true,"Verify genuine recipient unsubscribe rendering and opt-out operation without contacting list");
  fail("editorial_subject",w.founder_selected_corrected_editorial_copy===true,"Original Apollo 1 subject and duplicated CTA candidates have not been selected");
  fail("founder_campaign_approval",w.final_founder_release_approval===true,"Draft approval does not authorize sending, audience or schedule");
  fail("default_off",w.new_post_default_off===true,"The site's deliberate default-off safety control must remain unchanged");
  fail("canonical_offer_03",m.issue03==="Zen12","Issue 03 must remain Zen12 until founder changes canonical scope");
  fail("canonical_offer_05",m.issue05==="Hypnosis Live","Issue 05 must remain Hypnosis Live; do not substitute Total Focus");
  for(const n of ["03","05"]){
    const o=(m.by_issue||{})[n]||{};
    fail("merchant_"+n+"_email_permission",o.named_partner_email_permission===true,"Account-specific permitted EMAIL channel not documented");
    fail("merchant_"+n+"_guide",o.vetted_live_guide===true,"Guide must be a reviewed, public, functioning destination owned by Mind Studio");
    fail("merchant_"+n+"_offer",o.exact_merchant_sku_and_earning_url===true,"Account-issued earning link, offer identity and channel format not established");
    fail("merchant_"+n+"_terms",o.live_checkout_refund_claims_verified===true,"Claims, actual price, product format and refund limitations not independently cleared");
    fail("merchant_"+n+"_disclosure",o.adjacent_offer_disclosure_verified===true,"Near-guide and near-earning-link disclosures must be visible");
  }
  fail("settlement_source",r.independent_merchant_settlements_verified===true,"Clicks, signup and checkout starts are not paid settlements");
  fail("human_denominator",a.qualified_human_sessions_audited===true&&integer(a.qualified_human_sessions)&&a.qualified_human_sessions>0,"Real source-tagged, bot-filtered session denominator absent");
  fail("cohort_maturity",r.cohort_mature_and_refunds_fees_complete===true,"7/30-day cohort, refunds and fees not independently complete");
  const revenueReady=r.independent_merchant_settlements_verified===true&&r.cohort_mature_and_refunds_fees_complete===true&&a.qualified_human_sessions_audited===true&&integer(a.qualified_human_sessions)&&a.qualified_human_sessions>0&&Number.isSafeInteger(r.realized_net_cents);
  const revenuePer1000=revenueReady?Math.round((r.realized_net_cents/100)*1000/a.qualified_human_sessions*100)/100:null;
  return {
    schema_version:"1.0", observed_email_eligible_rows:observed?c.email_filter_total:null,
    proof_scope:"provider status snapshot only; not delivery, open, human buyer or permission for commercial email",
    editorial_reviewable:!holds.some(h=>["provider_email_eligibility","native_jetpack_preview","public_promise","publisher_postal","working_unsubscribe","editorial_subject"].includes(h.id))&&errors.length===0,
    merchant_issues_ready:false, /* no connected partner attestation/release even in synthetic fixtures */
    realized_net_per_1000_human_sessions:revenuePer1000,
    errors,holds,release_authorized:false
  };
}
module.exports={assess};
