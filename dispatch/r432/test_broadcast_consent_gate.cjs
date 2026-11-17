"use strict";
const assert = require("node:assert/strict");
const {evaluate,revenueProof,sourceAttribution,ISSUE_KINDS,REQUIRED_SHARED,REQUIRED_COMMERCIAL} = require("./broadcast_consent_gate.cjs");
let n=0;const eq=(x,y)=>{assert.deepEqual(x,y);n++};const has=(x,y)=>{assert.ok(x.includes(y));n++};const throws=(f)=>{assert.throws(f);n++};
const snapshot={settings:{subscriptions:true,email_new_posts_by_default:false,newsletter_categories_enabled:false,welcome_message:"Configured welcome"},subscribers:{total:3,confirmed:3,unconfirmed:2},followers:{email:0,wpcom:3}};
const allShared=Object.fromEntries(REQUIRED_SHARED.map(k=>[k,true]));
const offer = key=>({key,...Object.fromEntries(REQUIRED_COMMERCIAL.map(k=>[k,true]))});
const pending=evaluate(snapshot,{},1);
eq(pending.status,"HOLD_UNSENT");eq(pending.sendAuthorized,false);eq(pending.targeting,"BROADCAST_ONLY_NO_SUBSCRIBER_SEGMENTS");
eq(pending.recipientCount,null);eq(pending.flags.zeroDirectEmailFollowersReported,true);has(pending.issues,"SUBSCRIBER_BUCKETS_NONADDITIVE");
has(pending.issues,"NO_DIRECT_EMAIL_FOLLOWERS_REPORTED_NOT_ZERO_ELIGIBLE_PEOPLE_PROVEN");has(pending.issues,"ELIGIBLE_RECIPIENTS_UNVERIFIED");
eq(pending.flags.welcomeConfiguredNotReceipt,true);eq(pending.flags.categoryTargetingOff,true);eq(ISSUE_KINDS.filter(x=>x==="editorial").length,4);eq(ISSUE_KINDS.filter(x=>x==="commercial").length,2);
for(let i=1;i<=6;i++){let result=evaluate(snapshot,allShared,i, i===3?[offer("zen12")]:i===5?[offer("total_focus")]:[]);
  eq(result.sendAuthorized,false);eq(result.status,"HOLD_UNSENT");has(result.issues,"SUBSCRIBER_BUCKETS_NONADDITIVE");}
const consistent={...snapshot,subscribers:{total:3,confirmed:3,unconfirmed:0},followers:{email:2,wpcom:1}};
for(let i=1;i<=6;i++){const r=evaluate(consistent,allShared,i,i===3?[offer("zen12")]:i===5?[offer("total_focus")]:[]);eq(r.status,"HUMAN_REVIEW_ONLY");eq(r.sendAuthorized,false);eq(r.recipientCount,null);}
const missing={...allShared,workingUnsubscribe:false};has(evaluate(consistent,missing,1).issues,"MISSING_workingUnsubscribe");
has(evaluate(consistent,allShared,3,[]).issues,"EXACTLY_ONE_APPROVED_OFFER_REQUIRED");
has(evaluate(consistent,allShared,3,[offer("zen12"),offer("total_focus")]).issues,"EXACTLY_ONE_APPROVED_OFFER_REQUIRED");
has(evaluate(consistent,allShared,3,[offer("total_focus")]).issues,"OFFER_DOES_NOT_MATCH_EDITION");
has(evaluate(consistent,allShared,5,[offer("zen12")]).issues,"OFFER_DOES_NOT_MATCH_EDITION");
has(evaluate(consistent,allShared,4,[offer("zen12")]).issues,"EDITORIAL_ISSUE_MUST_NOT_INCLUDE_AN_OFFER");
has(evaluate(consistent,allShared,3,[{...offer("zen12"),emailChannelAllowed:false}]).issues,"MERCHANT_MISSING_emailChannelAllowed");
for(const key of REQUIRED_COMMERCIAL){has(evaluate(consistent,allShared,3,[{...offer("zen12"),[key]:false}]).issues,"MERCHANT_MISSING_"+key)}
for(const key of REQUIRED_SHARED){has(evaluate(consistent,{...allShared,[key]:false},1).issues,"MISSING_"+key)}
const auto={...consistent,settings:{...consistent.settings,email_new_posts_by_default:true}};
has(evaluate(auto,allShared,1).issues,"AUTOMATIC_SENDING_DEFAULT_UNSAFE");
const categories={...consistent,settings:{...consistent.settings,newsletter_categories_enabled:true}};
has(evaluate(categories,allShared,1).issues,"CATEGORY_CONFIGURATION_DRIFT_REQUIRES_REVIEW");
throws(()=>evaluate(consistent,allShared,0));throws(()=>evaluate(consistent,allShared,7));throws(()=>evaluate(consistent,{...allShared,subscriber_email:"redacted"},1));
eq(revenueProof({}).status,"NOT_COMPUTABLE");eq(revenueProof({}).netRevenuePer1000,null);
eq(revenueProof({independentSettlements:true,qualifiedHumanSessions:true,refundsAndFees:true,joinedCreatorAssetIds:true}).status,"SOURCE_DATA_READY_FOR_INDEPENDENT_ACCOUNTING");
for(let i=1;i<=6;i++){const u=sourceAttribution(i);eq(u.utm_content,`issue_${String(i).padStart(2,"0")}`);eq(u.status,"PROPOSED_NOT_LIVE");}
throws(()=>sourceAttribution(8));
console.log(`PASS ${n}/${n} native Node assertions; NO_SEND; no merchant links; all real-world recipient/merchant proofs HOLD`);
