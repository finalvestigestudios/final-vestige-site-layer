"use strict";
// Native command: node dispatch/r435/test_confirmed_signup_contract.cjs
const {classify,aggregateConfirmed,giftPanelVisible,releaseDecision}=require("./confirmed_signup_contract.cjs");
let checks=0;
function assert(truth,msg){checks++;if(!truth)throw Error("FAILED "+msg);}
const sample={type:"provider_subscription_transition",provider:"wordpress_jetpack",opaque_id:"provider_K77",
  previous_status:"unconfirmed",current_status:"subscribed",email_subscription:"subscribed",
  delivery_eligible:true,evidence_ref:"provider:event/777",consent_scope:"dispatch",
  effective_at:"2026-11-17T21:00:00Z"};
const candidate=changes=>({...sample,...changes});
for(const type of ["focus_signup_click","focus_pdf_click","focus_download_panel_shown",
  "subscribe_query","jetpack_ui_subscriber_class","reader_follow","wordpress_reader_follower",
  "newsletter_dashboard_count","welcome_configured"]){
  assert(classify({type}).confirmed===false,"UI signal blocked "+type);
}
assert(classify(sample).confirmed===true,"provider evidence accepted");
for(const [field,value] of [
  ["provider","other"],["opaque_id","bad id"],["previous_status","subscribed"],
  ["current_status","pending"],["email_subscription","unconfirmed"],
  ["delivery_eligible",false],["consent_scope","other"],["effective_at","tomorrow"],
  ["evidence_ref","weak"]
])assert(!classify(candidate({[field]:value})).confirmed,"invalid "+field);
for(const key of ["email","email_hash","ip","phone","name"])
  assert(!classify(candidate({[key]:"private"})).confirmed,"no pii "+key);
assert(!classify({type:"provider_subscription_transition"}).confirmed,"no magic type");
assert(!classify(null).confirmed,"null rejected");
assert(!classify([]).confirmed,"array rejected");
assert(!classify({type:"unknown"}).confirmed,"unknown rejected");
const tally=aggregateConfirmed([sample,sample,candidate({opaque_id:"provider_K78"}),
  {type:"focus_signup_click"},candidate({current_status:"pending"})]);
assert(tally.confirmed_signup===2,"dedupe one per provider subscription key");
assert(tally.duplicates===1,"duplicate observed");
assert(tally.non_lead===1 && tally.rejected===1,"nonleads separated");
assert(tally.recipients_count_known===false,"no false recipient count");
assert(tally.authorized_to_send===false,"aggregates cannot authorize send");
for(const q of ["pending","anything","success"])
 assert(giftPanelVisible({subscribeQuery:q})===true,"live UI can show gift for "+q);
for(const q of ["invalid_email","error","blocked_email","opted_out","blocked",""])
 assert(giftPanelVisible({subscribeQuery:q})===false,"blocked or blank UI "+q);
assert(giftPanelVisible({isSubscriberClass:true})===true,"class reveals gift but not consent");
assert(releaseDecision().authorized_to_send===false,"never issue send authorization");
assert(classify(sample).confirmed && !releaseDecision().authorized_to_send,"qualified evidence still not release");
assert(!("email" in tally),"aggregate no PII");
console.log("PASS: "+checks+" offline/consent assertions. No real recipients, provider writes, emails, or paid sales.");
