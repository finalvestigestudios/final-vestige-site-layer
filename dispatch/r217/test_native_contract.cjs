"use strict";
const test=require("node:test"),assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path");
const {audit,audienceCount,previewClass}=require("./native_contract.cjs");
const m=JSON.parse(fs.readFileSync(path.join(__dirname,"canonical_mapping.json"),"utf8"));
test("canonical six unique, four editorial and two merchant holds",()=>{
 assert.deepEqual(m.issues.map(x=>x.number),[1,2,3,4,5,6]);
 assert.equal(m.issues.filter(x=>x.kind==="editorial").length,4);
 assert.equal(m.issues.filter(x=>x.kind==="commercial-review-pending").length,2);
});
test("all issues are unsent and uncreated",()=>{for(const x of m.issues){assert.equal(x.post_id,null);assert.equal(x.status,"HOLD_UNSENT");assert.equal(x.actual_native_preview,"NOT_TESTED");}});
test("merchant paths are inactive placeholders",()=>{for(const x of m.issues.filter(x=>x.kind==="commercial-review-pending"))assert.match(x.destination,/^\[\[APPROVED_/);});
test("missing proofs cannot release",()=>{for(const x of [{},{actual_jetpack_preview:true},{founder_final_approval:true}]){const z=audit(m,x);assert.equal(z.can_send,false);assert.equal(z.result,"HOLD_UNSENT");assert.ok(z.blockers.length>0);}});
test("even complete synthetic attestation cannot send",()=>{const z=audit(m,{actual_jetpack_preview:true,received_compliant_email:true,publisher_address_verified:true,unsubscribe_verified:true,provider_eligible_audience:true,founder_final_approval:true,named_partner_email_rights:true,issued_affiliate_url:true,live_vetted_guide:true});assert.equal(z.can_send,false);assert.equal(z.result,"HOLD_UNSENT");});
test("nonadditive counters are not audience proof",()=>{assert.equal(audienceCount({total:3,confirmed:3,unconfirmed:2}),null);assert.equal(audienceCount({source:"wpcom-followers",count:3}),null);assert.equal(audienceCount({source:"provider-deliverable-count",count:3}),3);});
test("source, preview and receipt evidence differ",()=>{assert.equal(previewClass("offline"),"SOURCE_ONLY");assert.equal(previewClass("wordpress_preview"),"VISUAL_ONLY");assert.equal(previewClass("authorized_received"),"RECEIVED_REQUIRES_QA");});
test("tampered campaign is blocked",()=>{for(const x of [{...m,send_permitted:true},{...m,issues:m.issues.slice(1)},{...m,issues:m.issues.map(v=>({...v,status:"READY"}))}])assert.ok(audit(x,{}).blockers.length>0);});
