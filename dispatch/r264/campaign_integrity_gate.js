"use strict";
/**
 * Dispatch R264: a non-sending, fail-closed integrity check of the R263
 * snapshot against the founder's ORIGINAL six-issue master manifest.
 * Read-only; this is NOT a send authorization engine.
 */
const {check: priorCheck} = require("../r263/route_contract.js");
const OWN = Object.freeze({
  state:"DRAFT_UNSENT_NO_SCHEDULING",
  schema:"FV-Dispatch-R263-2026-11-10",
  canonical:{original_pr:175,readiness_pr:201,base_pr:1935,dispatch_issue:174,mind_issue:171,focus_issue:129,conversion_issue:820},
  gates:["received_jetpack_preview","received_message_footer","functional_opt_out","postal_address_for_fv","confirmed_consent_and_eligible_count","partner_email_permission","founder_campaign_approval"],
  sources:{
    zen12:["https://zen12.com/hnp","https://zen12.com/secret/","https://zen12.com/welcome","https://zen12.com/freeaudio"],
    "hypnosis-total-focus":["https://hypnosislive.com/mental-skills/total-focus"]
  },
  metricRule:"utm_source=actual_platform;utm_medium=organic_social;utm_campaign=cluster_pilot_2026_11;utm_content=verified_asset_id"
});
function sameKeys(actual,wanted){
  return !!actual && typeof actual==="object" && !Array.isArray(actual) &&
    JSON.stringify(Object.keys(actual).sort())===JSON.stringify([...wanted].sort());
}
function same(a,b){return JSON.stringify(a)===JSON.stringify(b);}
function audit(c,original){
  const errors=[];
  function fail(code){errors.push(code);}
  try {
    const p=priorCheck(c);
    if(!p.pass) errors.push(...p.errors.map(e=>"r263:"+e));
  } catch(e){fail("r263_exception");}
  if(!c||typeof c!=="object"||Array.isArray(c)) return {pass:false,errors:[...errors,"missing_snapshot"]};
  if(!original||typeof original!=="object"||Array.isArray(original)) return {pass:false,errors:[...errors,"missing_original_manifest"]};
  const rootKeys=["schema","state","founder_send_approval","canonical","actual_email_eligible_audience","verified_welcome_receipt","verified_received_unsubscribe","verified_received_fv_postal_address","wordpress","editions","offers","metrics","release_gates"];
  if(!sameKeys(c,rootKeys)) fail("snapshot_key_drift");
  if(c.schema!==OWN.schema || c.state!==OWN.state) fail("snapshot_identity");
  if(!sameKeys(c.canonical,Object.keys(OWN.canonical)) || !same(c.canonical,OWN.canonical)) fail("canonical_issue_identity");
  if(!sameKeys(c.release_gates,OWN.gates) || OWN.gates.some(k=>c.release_gates?.[k]!==false)) fail("release_gate_missing_or_claimed");
  if(!sameKeys(c.offers,Object.keys(OWN.sources))) fail("offer_identity");
  for(const name of Object.keys(OWN.sources)){
    const offer=c.offers?.[name];
    if(!offer || !same(offer.official_sources,OWN.sources[name])) fail("merchant_sources_"+name);
  }
  if(!sameKeys(c.metrics,["source_rule","confirmed_paid_orders","realized_net_revenue","net_revenue_per_1000_qualified_human_sessions"]) ||
      c.metrics?.source_rule!==OWN.metricRule) fail("attribution_contract");
  for(const key of ["confirmed_paid_orders","realized_net_revenue","net_revenue_per_1000_qualified_human_sessions"])
    if(c.metrics?.[key]!==null) fail("settlement_unverified_"+key);
  const wp=c.wordpress;
  const countKeys=["total","confirmed_counter","unconfirmed_requests","jetpack_email_followers_last_observed","wpcom_followers_last_observed"];
  for(const key of countKeys){
    if(!Number.isSafeInteger(wp?.[key]) || wp[key]<0) fail("wordpress_counter_invalid_"+key);
  }
  if(c.actual_email_eligible_audience!==null || c.verified_welcome_receipt!==false)
    fail("not_provider_verified");
  if(original.status!==OWN.state || !original.mix || original.mix.editorial!==4 ||
     original.mix.commercial_review_pending!==2 || !Array.isArray(original.issues) ||
     original.issues.length!==6) fail("original_manifest_drift");
  if(!Array.isArray(c.editions)||c.editions.length!==6) fail("edition_count");
  else if(Array.isArray(original.issues)&&original.issues.length===6){
    for(let i=0;i<6;i++){
      const e=c.editions[i]??{},m=original.issues[i]??{};
      if(e.n!==m.number || e.subject!==m.subject || e.cta!==m.editorial_cta ||
         e.type!==m.kind || m.publish_state!=="hold" || m.merchant_affiliate_url!==null ||
         typeof m.preheader!=="string" || !m.preheader.trim()) fail("master_manifest_conflict_"+(i+1));
      if(i===2||i===4){
        if(e.release!=="HOLD_MERCHANT" || e.disclosure_at_offer!==true ||
           !e.disclosure?.includes("Final Vestige may earn a commission"))
          fail("commercial_release_and_disclosure_"+(i+1));
      } else if(e.release!=="HOLD") fail("editorial_release_"+(i+1));
    }
  }
  return {pass:errors.length===0,errors};
}
module.exports={audit};
if(require.main===module){
  const fs=require("node:fs"),path=require("node:path");
  const c=JSON.parse(fs.readFileSync(path.join(__dirname,"../r263/OFFER_ROUTE_CONTRACT.json"),"utf8"));
  const original=JSON.parse(fs.readFileSync(path.join(__dirname,"../campaign-2026-mind/manifest.json"),"utf8"));
  const result=audit(c,original);
  process.stdout.write(JSON.stringify(result,null,2)+"\n");
  process.exitCode=result.pass?0:1;
}
