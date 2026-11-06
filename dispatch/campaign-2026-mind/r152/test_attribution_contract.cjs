/* R152 adversarial link/continuity suite. Native: node --test r152/test_attribution_contract.cjs */
const assert = (typeof require==="function") ? require("node:assert/strict") : {
  deepEqual(a,b){if(JSON.stringify(a)!==JSON.stringify(b))throw Error("assert deepEqual");},
  equal(a,b){if(a!==b)throw Error("assert equal");},
  throws(fn){let ok=false;try{fn()}catch(e){ok=true;}if(!ok)throw Error("expected rejection");}
};
const api=(typeof require==="function") ? require("./attribution_contract.cjs") : globalThis.FVAttribution;
const grok="https://finalvestige.com/focus/?utm_source=youtube&utm_medium=organic_social&utm_campaign=perception_pilot_2026_11&utm_content=yt_change_001";
const mail="https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/?utm_source=dispatch&utm_medium=email&utm_campaign=dispatch_mind_pilot_2026_11&utm_content=issue_02";
function check(){
 const p=api.inspectGrokLink(grok);
 assert.equal(p.asset_id,"yt_change_001");assert.equal(p.landing_path,"/focus/");assert.equal(p.verified_signup,false);
 const e=api.inspectDispatchLink(mail);assert.equal(e.issue,"issue_02");assert.equal(e.verified_order,false);
 for(const p of ["http://finalvestige.com","https://evil.com/focus/","https://finalvestige.com@evil.com/focus/","https://finalvestige.com:443/focus/","https://finalvestige.com/focus/#frag","https://finalvestige.com/focus/?email=joe%40example.com","https://finalvestige.com/focus/?utm_source=tiktok"]){assert.throws(()=>api.inspectGrokLink(p));}
 const replacements=[
  ["utm_source=youtube","utm_source=wordpress"],
  ["utm_medium=organic_social","utm_medium=paid_social"],
  ["perception_pilot_2026_11","other_pilot_2026_11"],
  ["utm_content=yt_change_001","utm_content=issue_01"],
  ["utm_content=yt_change_001","utm_content=joe%40example.com"],
  ["utm_content=yt_change_001","utm_content=user-123.45"],
  ["/focus/","/checkout/"],
  ["/focus/","/focus/../../admin/"],
  ["utm_source=youtube","utm_source=youtube&utm_source=tiktok"],
  ["utm_content=yt_change_001","utm_content=yt_change_001&email=x"],
  ["utm_content=yt_change_001","utm_content=yt_change_001#fragment"],
  ["utm_campaign=perception_pilot_2026_11","utm_campaign=perception_pilot_2026_13"]
 ];
 for(const [a,b] of replacements)assert.throws(()=>api.inspectGrokLink(grok.replace(a,b)));
 for(const [a,b] of [
   ["utm_source=dispatch","utm_source=affiliate"],
   ["utm_medium=email","utm_medium=organic_social"],
   ["issue_02","issue_07"],
   ["dispatch_mind_pilot_2026_11","dispatch_mind_pilot_2026_10"],
   ["/free-resources/puysegurs-animal-magnetism-files/","/checkout/"],
   ["utm_content=issue_02","utm_content=issue_02&subscriber=abc"],
   ["utm_source=dispatch","utm_source=dispatch&utm_source=dispatch"]
 ]) assert.throws(()=>api.inspectDispatchLink(mail.replace(a,b)));
 const proposal=api.auditGrokProposals([{working_label:"sample_one",proposed_url:grok},{working_label:"sample_two",proposed_url:grok.replace("yt_change_001","yt_change_002")}]);
 assert.equal(proposal.unique_asset_ids,2);assert.equal(proposal.conversion_measured,false);
 const collision=api.auditGrokProposals([{working_label:"one",proposed_url:grok},{working_label:"two",proposed_url:grok}]);
 assert.deepEqual(collision.blocked,["REUSED_ASSET_ID"]);assert.equal(collision.unique_asset_ids,1);
 for(const bad of [{foo:"secret",working_label:"ok",proposed_url:grok},{working_label:"name@example.com",proposed_url:grok},{working_label:"ok",proposed_url:"https://other.com/"}])assert.throws(()=>api.auditGrokProposals([bad]));
 const bridge=api.bridgeContract();
 for(const key of ["qualified_sessions","confirmed_new_leads","paid_orders","net_revenue_per_1000"])assert.equal(bridge[key],null);
 assert.equal(bridge.is_email_sending_authorized,false);assert.equal(bridge.is_affiliate_email_authorized,false);
 return {passed:38,release:bridge.is_email_sending_authorized?"FAIL":"HOLD",grok_links_checked:2,commercial_authorization:false};
}
if(typeof require==="function"){
 const {test}=require("node:test");
 test("R152 cross-channel attribution, duplicate, PII and release assertions",()=>{check()});
}else globalThis.FVAttributionTest=check;
