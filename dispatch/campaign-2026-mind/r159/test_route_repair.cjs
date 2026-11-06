"use strict";
// Native: node --test dispatch/campaign-2026-mind/r159/test_route_repair.cjs
// Read-only compatibility tests; zero network, analytics, subscribers, mail or merchant actions.
const assert=require("node:assert/strict");
const {test}=require("node:test");
const api=require("../r152/attribution_contract.cjs");
const base="https://finalvestige.com";
function grok(path,cluster="mind",id="yt_cb_1922",source="youtube"){
  return base+path+"?utm_source="+source+"&utm_medium=organic_social&utm_campaign="+cluster+"_pilot_2026_11&utm_content="+id;
}
function mail(path,number=4){
  return base+path+"?utm_source=dispatch&utm_medium=email&utm_campaign=dispatch_mind_pilot_2026_11&utm_content=issue_0"+number;
}
const CB="/2026/11/02/change-blindness/";
const APOLLO="/2026/08/20/the-hatch-opened-inward-apollo-1/";
test("official TASK-008 campaign clusters mind and mysteries must pass",()=>{
 for(const c of ["mind","mysteries","history","preparedness"]){
  const r=api.inspectGrokLink(grok("/focus/",c));
  assert.equal(r.campaign,c+"_pilot_2026_11");
  assert.equal(r.release,"HOLD_UNSENT");
  assert.equal(r.verified_human_session,false);
  assert.equal(r.verified_signup,false);
 }
});
test("two specifically published canonical WordPress post URLs work for both source and Dispatch",()=>{
 for(const path of [CB,APOLLO]){
  assert.equal(api.inspectGrokLink(grok(path)).landing_path,path);
  assert.equal(api.inspectDispatchLink(mail(path)).landing_path,path);
  assert.equal(api.inspectDispatchLink(mail(path)).verified_order,false);
 }
});
test("previous R152 source contract remains compatible",()=>{
 const p=api.inspectGrokLink(grok("/focus/","perception","yt_old_001"));
 assert.equal(p.asset_id,"yt_old_001");
 assert.equal(api.inspectDispatchLink(mail("/free-resources/puysegurs-animal-magnetism-files/",2)).issue,"issue_02");
 const b=api.bridgeContract();
 for(const k of ["qualified_sessions","confirmed_new_leads","paid_orders","net_revenue_per_1000"])assert.equal(b[k],null);
 assert.equal(b.is_email_sending_authorized,false);
 assert.equal(b.is_affiliate_email_authorized,false);
});
test("unverified dated posts are not pre-approved; no silent wildcard",()=>{
 for(const path of [
  "/2026/11/02/not-a-live-post/",
  "/2026/11/03/change-blindness/",
  "/2026/11/02/change-blindness/extra/",
  "/2026/11/02//change-blindness/",
  "/2026/11/02/change-blindness/../",
  "/shop/","/checkout/","/wp-admin/","/unsubscribe/"
 ]){
  assert.throws(()=>api.inspectGrokLink(grok(path)),path);
  assert.throws(()=>api.inspectDispatchLink(mail(path)),path);
 }
});
test("private identifiers, other origins, manipulated campaigns, query repeats fail",()=>{
 for(const url of [
  grok(CB).replace("utm_content=yt_cb_1922","utm_content=bob%40mail.com"),
  grok(CB).replace("utm_content=yt_cb_1922","utm_content=issue_01"),
  grok(CB).replace("utm_source=youtube","utm_source=mailinglist"),
  grok(CB).replace("mind_pilot_2026_11","mind_pilot_2026_13"),
  grok(CB)+"&subscriber=123",
  grok(CB).replace("https://finalvestige.com","https://another.example"),
  grok(CB).replace("https://finalvestige.com","https://finalvestige.com@other.example"),
  grok(CB).replace("utm_source=youtube","utm_source=youtube&utm_source=tiktok")
 ])assert.throws(()=>api.inspectGrokLink(url),url);
});
test("collisions remain blocked; URLs never authorize social publication or email",()=>{
 const x=api.auditGrokProposals([
  {working_label:"a",proposed_url:grok(CB,"mind","yt_same")},
  {working_label:"b",proposed_url:grok(APOLLO,"history","yt_same")}
 ]);
 assert.equal(x.unique_asset_ids,1);
 assert.deepEqual(x.blocked,["REUSED_ASSET_ID"]);
 assert.equal(x.posting_authorized,false);
 assert.equal(x.conversion_measured,false);
 assert.equal(x.links[0].verified_live_post,false);
});
test("no affiliate link, PII, invented buy, or approved send behavior added",()=>{
 for(const url of [
  "https://zen12.com/?utm_source=dispatch",
  "https://hypnosislive.com/mental-skills/total-focus",
  grok("/focus/").replace("https://","http://"),
  mail(CB).replace("utm_source=dispatch","utm_source=zen12"),
  mail(APOLLO).replace("issue_04","issue_05&customer_id=100")
 ]){assert.throws(()=>api.inspectGrokLink(url));assert.throws(()=>api.inspectDispatchLink(url));}
 const e=api.inspectDispatchLink(mail(APOLLO));
 assert.equal(e.release,"HOLD_UNSENT");
 assert.equal(e.verified_jetpack_render,false);
 assert.equal(e.verified_unsubscribe,false);
});
