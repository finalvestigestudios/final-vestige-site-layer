"use strict";
// Run node dispatch/r263/route_contract.js; read-only, no network or CMS writes.
function check(c){
 const errors=[];
 const f=(code)=>errors.push(code);
 if(!c||typeof c!=="object")return {pass:false,errors:["missing_contract"]};
 if(c.state!=="DRAFT_UNSENT_NO_SCHEDULING"||c.founder_send_approval!==false)f("sending_not_frozen");
 const types=["editorial","editorial","commercial-review-pending","editorial","commercial-review-pending","editorial"];
 if(!Array.isArray(c.editions)||c.editions.length!==6)return {pass:false,errors:[...errors,"not_six_editions"]};
 const expectedOffers={3:"zen12",5:"hypnosis-total-focus"};
 function safePublishedCta(s){
  return typeof s==="string"&&/^https:\/\/finalvestige\.com\/[a-z0-9/_-]+\/?$/i.test(s)&&
   !/\/\//.test(s.slice("https://".length))&&!/%/.test(s)&&!/\\/.test(s);
 }
 c.editions.forEach((e,i)=>{
  const n=i+1;
  if(e.n!==n||e.type!==types[i]||!e.subject||/\[\[/.test(e.subject))f("edition_identity_"+n);
  if(n===3||n===5){
    const expected="[[APPROVED_"+(n===3?"ZEN12":"HYPNOSIS_LIVE")+"_WARMUP_GUIDE_URL_REQUIRED]]";
    if(e.release!=="HOLD_MERCHANT"||e.cta!==expected||e.offer!==expectedOffers[n])f("offer_route_"+n);
    if(e.disclosure_at_offer!==true||!/Final Vestige may earn a commission/.test(e.disclosure||""))f("offer_disclosure_"+n);
  } else if(e.release!=="HOLD"||!safePublishedCta(e.cta))f("editorial_route_"+n);
 });
 if(c.actual_email_eligible_audience!==null||c.verified_welcome_receipt!==false||c.verified_received_unsubscribe!==false||c.verified_received_fv_postal_address!==false)f("fabricated_eligibility_or_delivery");
 if(c.wordpress?.auto_new_posts!==false||c.wordpress?.newsletter_enabled!==true)f("newsletter_production_drift");
 for(const name of ["zen12","hypnosis-total-focus"]){
  const o=c.offers?.[name];
  if(!o){f("missing_offer_"+name);continue;}
  for(const k of ["verified_fv_affiliate_approval","verified_email_marketing_permission","verified_current_terms","product_specific_efficacy_verified"])if(o[k]!==false)f("unverified_partner_attestation_"+name+"_"+k);
  for(const k of ["price","verified_earning_url","verified_live_fv_guide"])if(o[k]!==null)f("unapproved_sale_or_url_"+name+"_"+k);
 }
 if(c.offers?.zen12?.merchant_free_trial_separate_newsletter!==true)f("vendor_list_conflated");
 if(c.offers?.["hypnosis-total-focus"]?.observed_price_variance!==true)f("pricing_conflict_suppressed");
 if(!c.metrics||!c.metrics.source_rule?.includes("utm_source=actual_platform")||!c.metrics.source_rule.includes("utm_medium=organic_social"))f("campaign_attribution_drift");
 for(const key of ["confirmed_paid_orders","realized_net_revenue","net_revenue_per_1000_qualified_human_sessions"])if(c.metrics?.[key]!==null)f("fabricated_paid_metric_"+key);
 if(!c.release_gates||Object.values(c.release_gates).some(v=>v!==false))f("unverified_release_gate_activated");
 return {pass:errors.length===0,errors};
}
if(typeof module!=="undefined")module.exports={check};
if(typeof require!=="undefined"&&typeof module!=="undefined"&&require.main===module){
 const fs=require("node:fs"),path=require("node:path");
 const c=JSON.parse(fs.readFileSync(path.join(__dirname,"OFFER_ROUTE_CONTRACT.json"),"utf8"));
 const result=check(c);process.stdout.write(JSON.stringify(result,null,2)+"\n");process.exitCode=result.pass?0:1;
}
