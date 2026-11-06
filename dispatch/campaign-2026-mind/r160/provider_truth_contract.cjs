/* Final Vestige Dispatch R160 — evidence-classification ONLY. No network, writes, signup, email or purchase actions. */
(function(root,factory) {
  const api=factory();
  if (typeof module!=="undefined" && module.exports) module.exports=api;
  else root.FVDispatchProviderTruth=api;
})(globalThis,function(){
  "use strict";
  const URL="https://finalvestige.com";
  const EXPECTED_PDF=URL+"/wp-content/uploads/2026/10/Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf";
  const PAGES=Object.freeze({dispatch:{id:523,url:URL+"/dispatch/"},focus:{id:1579,url:URL+"/focus/"}});
  const STATUS=Object.freeze({UNKNOWN:"NOT_VERIFIED",HOLD:"HOLD_UNSENT",MERCHANT:"HOLD_MERCHANT",ASSET:"PROVIDER_MEDIA_ASSET_MATCHED",SIGNUP:"GUEST_SIGNUP_NOT_PROVEN"});
  function plain(x){return x&&typeof x==="object"&&!Array.isArray(x);}
  function finiteNonnegative(x){return Number.isInteger(x)&&x>=0&&x<=1000000000;}
  function checkSnapshot(s){
    if(!plain(s)||!plain(s.newsletter)||!plain(s.counts)||!plain(s.pages)||!plain(s.media)) throw Error("SNAPSHOT_SHAPE_INCOMPLETE");
    if(s.site!==URL)throw Error("WRONG_SITE");
    for(const k of ["total","confirmed","unconfirmed","suppressed","paid"])
      if(!finiteNonnegative(s.counts[k]))throw Error("INVALID_AGGREGATE_"+k.toUpperCase());
    if(typeof s.newsletter.enabled!=="boolean"||typeof s.newsletter.new_post_default!=="boolean"
      ||typeof s.newsletter.can_send!=="boolean"||typeof s.newsletter.email_format!=="string")throw Error("INVALID_PROVIDER_SETTINGS");
    for(const name of Object.keys(PAGES)){
      const p=s.pages[name];
      if(!plain(p)||p.id!==PAGES[name].id||p.url!==PAGES[name].url||p.publish_state!=="publish")
        throw Error("MISSING_PUBLISHED_"+name.toUpperCase());
      if(typeof p.api_contains_email_input!=="boolean"||typeof p.api_self_anchor!=="boolean"
        ||typeof p.screenshot_ready!=="boolean")throw Error("MISSING_API_OBSERVATION");
    }
    if(!plain(s.media)||!finiteNonnegative(s.media.filesize))throw Error("INVALID_MEDIA");
    return s;
  }
  function evaluate(s){
    checkSnapshot(s);
    const exactPdf=s.media.url===EXPECTED_PDF && s.media.mime_type==="application/pdf" && s.media.filesize>0;
    const api=Object.keys(PAGES).map(k=>{
      const p=s.pages[k];
      return Object.freeze({page:k,provider_page_id:p.id,published:true,
        api_subscribe_self_link:p.api_self_anchor,
        api_email_input_visible:p.api_contains_email_input,
        screenshot_capture_ready:p.screenshot_ready,
        guest_interactive_form:STATUS.UNKNOWN,
        verified_subscribe_completion:STATUS.UNKNOWN,
        explanation:"WordPress content API and mshots are not a signed-out, interactive browser or consent confirmation."});
    });
    const warnings=[];
    if(s.counts.total!==s.counts.confirmed)warnings.push("TOTAL_AND_CONFIRMED_DIFFER");
    if(s.counts.unconfirmed>0)warnings.push("UNCONFIRMED_IS_NOT_ADDITIVE_TO_TOTAL");
    if(s.newsletter.can_send)warnings.push("TECHNICAL_SEND_CAPABILITY_IS_NOT_FOUNDER_AUTHORIZATION");
    if(s.newsletter.new_post_default)warnings.push("AUTO_SEND_DEFAULT_ON_DANGEROUS");
    if(s.newsletter.email_format!=="full")warnings.push("EMAIL_BODY_FORMAT_NEEDS_REVIEW");
    return Object.freeze({
      mode:"READ_ONLY_EVIDENCE_CLASSIFIER_NO_LIVE_EXPERIMENT",
      source_url:URL,newsletter_enabled:s.newsletter.enabled,
      new_posts_default_off:!s.newsletter.new_post_default,
      posted_or_sent_anything:false,
      provider_reported:{total:s.counts.total,confirmed:s.counts.confirmed,unconfirmed:s.counts.unconfirmed,suppressed:s.counts.suppressed,paid:s.counts.paid},
      authoritative_email_eligibility:STATUS.UNKNOWN,
      net_new_confirmed_signup_events:STATUS.UNKNOWN,
      subscriber_categories_additive:false,
      fieldbook_pdf_asset:exactPdf?STATUS.ASSET:STATUS.UNKNOWN,
      fieldbook_pdf_meta:exactPdf?{wordpress_media_id:s.media.id,filesize_bytes:s.media.filesize}:null,
      welcome_configuration_known:typeof s.newsletter.welcome_points_to_fieldbook==="boolean"&&s.newsletter.welcome_points_to_fieldbook,
      actual_received_welcome:STATUS.UNKNOWN,download_completed:STATUS.UNKNOWN,
      api_pages:api,actual_guest_first_click:STATUS.SIGNUP,
      native_email_preview:STATUS.UNKNOWN,verified_postal_footer:STATUS.UNKNOWN,functioning_unsubscribe:STATUS.UNKNOWN,
      affiliate_zen12_email_permission:STATUS.UNKNOWN,affiliate_total_focus_email_permission:STATUS.UNKNOWN,
      approved_zen12_guide_live:STATUS.UNKNOWN,approved_total_focus_guide_live:STATUS.UNKNOWN,
      independently_reported_paid_orders:STATUS.UNKNOWN,realized_net_revenue_per_1000_qualified_sessions:null,
      newsletter_release:[1,2,3,4,5,6].map(i=>({issue:i,status:STATUS.HOLD,merchant_gate:i===3||i===5?STATUS.MERCHANT:null})),
      warnings,
      evidence_needed:["Signed-out, no-submit interactive form inspection on both published pages",
        "Private provider-native Email subscription eligibility and deduplicated confirmation transition",
        "Permissioned inspection of actual delivered Fieldbook welcome, without sending",
        "Non-sending Jetpack editor Preview email; later authorized received-message footer/unsubscribe QA",
        "Valid Final Vestige physical postal address and verified commercial opt-out",
        "Named Inspire3 account approval, exact email-channel permission, authorized affiliate link, first-party live buyer guide",
        "Independent paid order/commission settlement, fees/refunds and qualified-human session denominator"]
    });
  }
  return Object.freeze({evaluate,checkSnapshot,EXPECTED_PDF,STATUS});
});