/* FV Dispatch R152: offline-only source-link contract. No network, cookies, user data, email send, or analytics writes. */
(function(root,factory) {
  const api=factory();
  if(typeof module!=="undefined" && module.exports) module.exports=api;
  else root.FVAttribution=api;
})(globalThis,function() {
  "use strict";
  const SOURCE=new Set(["youtube","tiktok","instagram","facebook","pinterest","snapchat","bluesky","linkedin","x"]);
  const FIELDS=["utm_source","utm_medium","utm_campaign","utm_content"];
  const CLUSTERS=new Set(["perception","investigation","preparedness","history","focus","education","archive"]);
  const NO_SEND="HOLD_UNSENT";
  function stop(){throw Error("INVALID_OR_PRIVATE_SOURCE_URL");}
  function token(x){return typeof x==="string" && /^[a-z0-9][a-z0-9_-]{0,63}$/.test(x);}
  function decode(s) {try {return decodeURIComponent(s.replace(/\+/g," "));}catch(e){stop();}}
  function unpack(raw) {
    if(typeof raw!=="string" || raw.length>600 || /[\r\n\t]/.test(raw)) stop();
    const m=/^https:\/\/finalvestige\.com(\/[^?#]*)(?:\?([^#]*))?$/.exec(raw);
    if(!m) stop();
    const path=m[1],query=m[2]; 
    if(!path || /%|\\|\/\/|\.\./.test(path) || path.length>180 || !/^\/[a-zA-Z0-9/_-]*\/$/.test(path) || !query) stop();
    const pairs=query.split("&");if(pairs.length!==4) stop();
    const params=Object.create(null);
    for(const pair of pairs) {
      const i=pair.indexOf("="); if(i<=0) stop();
      const k=decode(pair.slice(0,i)),v=decode(pair.slice(i+1));
      if(!FIELDS.includes(k) || Object.prototype.hasOwnProperty.call(params,k)) stop();
      params[k]=v;
    }
    if(FIELDS.some(x=>!(x in params))) stop();
    for(const v of Object.values(params)) if(!token(v)) stop();
    return {path,params};
  }
  function inspectGrokLink(url){
    const {path,params:p}=unpack(url);
    if(!SOURCE.has(p.utm_source)||p.utm_medium!=="organic_social"||!/^([a-z]+)_pilot_(20\d\d)_(0[1-9]|1[0-2])$/.test(p.utm_campaign)) stop();
    const cluster=p.utm_campaign.split("_pilot_")[0];
    if(!CLUSTERS.has(cluster))stop();
    if(!(/^(\/focus\/|\/dispatch\/|\/mind\/|\/free-resources\/[a-z0-9/-]+\/|\/investigations\/[a-z0-9/-]+\/)$/).test(path))stop();
    if(p.utm_content.startsWith("issue_"))stop();
    return Object.freeze({kind:"GROK_OWNED_ASSET",platform:p.utm_source,campaign:p.utm_campaign,asset_id:p.utm_content,landing_path:path,release:NO_SEND,verified_live_post:false,verified_human_session:false,verified_signup:false,verified_order:false});
  }
  function inspectDispatchLink(url){
    const {path,params:p}=unpack(url);
    if(p.utm_source!=="dispatch"||p.utm_medium!=="email"||p.utm_campaign!=="dispatch_mind_pilot_2026_11"||!/^issue_0[1-6]$/.test(p.utm_content))stop();
    if(!(/^(\/focus\/|\/dispatch\/|\/mind\/|\/free-resources\/[a-z0-9/-]+\/|\/investigations\/[a-z0-9/-]+\/)$/).test(path))stop();
    return Object.freeze({kind:"DRAFT_EMAIL_CTA",issue:p.utm_content,landing_path:path,release:NO_SEND,verified_jetpack_render:false,verified_unsubscribe:false,verified_order:false});
  }
  function auditGrokProposals(records){
    if(!Array.isArray(records)||records.length>100)stop();
    const ids=new Set(),out=[],blocked=[];
    for(const row of records){
      if(!row||typeof row!=="object"||Array.isArray(row)||Object.keys(row).sort().join(",")!=="proposed_url,working_label")stop();
      if(typeof row.working_label!=="string"||!token(row.working_label))stop();
      const parsed=inspectGrokLink(row.proposed_url);
      if(ids.has(parsed.asset_id)){blocked.push("REUSED_ASSET_ID");continue;}
      ids.add(parsed.asset_id);out.push(parsed);
    }
    return Object.freeze({all_links_draft:true,posting_authorized:false,conversion_measured:false,unique_asset_ids:out.length,blocked,links:out});
  }
  function bridgeContract(){
    return Object.freeze({
      creator_source:"proposed_utm_tags_only",
      landing_to_signup:"NO_NATIVE_PROVIDER_EVENT_LINK_OBSERVED",
      native_confirmed_signup:"UNOBSERVABLE_WITH_CURRENT_READ_ACCESS",
      subscriber_to_email:"NO_RECEIVED_JETPACK_CAMPAIGN",
      email_to_paid_order:"NO_INDEPENDENT_MERCHANT_SETTLEMENT",
      qualified_sessions:null,confirmed_new_leads:null,paid_orders:null,net_revenue_per_1000:null,
      is_email_sending_authorized:false,is_affiliate_email_authorized:false,
      reason:"UTM_URL_IS_NOT_PERSON_ID_OR_PROOF_OF_CONVERSION"
    });
  }
  return Object.freeze({inspectGrokLink,inspectDispatchLink,auditGrokProposals,bridgeContract});
});