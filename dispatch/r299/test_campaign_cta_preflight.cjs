"use strict";
const test=require("node:test"),assert=require("node:assert/strict");
const {auditCampaign,PDF}=require("./campaign_cta_preflight.cjs");
const base=()=>({
 status:"DRAFT_UNSENT_NO_SCHEDULING",
 issues:Array.from({length:6},(_,i)=>({
 number:i+1,kind:[2,4].includes(i)?"commercial-review-pending":"editorial",
 subject:"Subject "+(i+1),preheader:"Intro "+(i+1),
 editorial_cta:i===5?"https://finalvestige.com/focus/":i===1?"https://finalvestige.com/story/":i===0?"https://finalvestige.com/story/":[2,4].includes(i)?"[[APPROVED_GUIDE_REQUIRED]]":"https://finalvestige.com/history/",
 merchant_affiliate_url:null
 }))
});
const bodies=m=>m.issues.map(x=>[
 "UNSENT DRAFT",x.subject,x.preheader,
 "[[VALID_POSTAL_ADDRESS_REQUIRED]]",
 "[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]",
 x.kind==="commercial-review-pending"?"Commercial disclosure: pending APPROVED_ partner link":""
 ].join("\n"));
test("six edition allocation remains four editorial and two commercial",()=>{
 const m=base(),r=auditCampaign(m,bodies(m));
 assert.equal(r.count,6);assert.equal(r.allocation.editorial,4);assert.equal(r.allocation.commercial,2);assert.equal(r.status,"HOLD_UNSENT");
});
test("real-world source and provider evidence never imply permission to send",()=>{
 const m=base(),r=auditCampaign(m,bodies(m),{providerEligibleCountVerified:true,receivedWelcomeVerified:true,jetpackNativePreviewVerified:true,founderFinalCampaignApproval:true,validPublisherPostalAddressInReceivedEmail:true,functionalUnsubscribeInReceivedEmail:true});
 assert.equal(r.status,"HOLD_UNSENT");assert.ok(r.issues.every(x=>x.decision==="HOLD_UNSENT"));assert.equal(r.netRevenuePerThousandQualifiedSessions,null);
});
test("repeat destination and existing-subscriber signup loop are visible",()=>{
 const m=base(),r=auditCampaign(m,bodies(m));
 assert.ok(r.issues[1].findings.includes("ADJACENT_EMAILS_SHARE_CTA_DESTINATION"));
 assert.ok(r.issues[5].findings.includes("EXISTING_SUBSCRIBER_REENTERS_SIGNUP_LANDING"));
 m.issues[5].editorial_cta=PDF;
 assert.ok(!auditCampaign(m,bodies(m)).issues[5].findings.includes("EXISTING_SUBSCRIBER_REENTERS_SIGNUP_LANDING"));
});
test("dangerous commercial mutation never accepted",()=>{
 const m=base(),b=bodies(m);m.issues[2].merchant_affiliate_url="https://merchant.example/unsafe";
 assert.ok(auditCampaign(m,b).issues[2].findings.includes("UNAUTHORIZED_MERCHANT_URL"));
 m.issues[2].merchant_affiliate_url=null;m.issues[2].editorial_cta="https://merchant.example/unsafe";
 assert.ok(auditCampaign(m,b).issues[2].findings.includes("UNVERIFIED_COMMERCIAL_CTA"));
});
test("missing source and legal holds visibly fail",()=>{
 const m=base(),b=bodies(m);b[0]="UNSENT DRAFT";
 const flags=auditCampaign(m,b).issues[0].findings;
 for(const key of ["SUBJECT_SOURCE_MISMATCH","PREHEADER_SOURCE_MISMATCH","POSTAL_HOLD_MISSING","UNSUBSCRIBE_HOLD_MISSING"])assert.ok(flags.includes(key));
});
test("both commercial editions fail closed and native preheader is unverified",()=>{
 const m=base(),r=auditCampaign(m,bodies(m));
 for(const i of [2,4]){
  assert.ok(r.issues[i].findings.includes("GUIDE_NOT_LIVE"));
  assert.ok(r.issues[i].findings.includes("MERCHANT_EMAIL_PERMISSION_UNVERIFIED"));
 }
 assert.ok(r.issues.every(x=>x.findings.includes("PREHEADER_NATIVE_JETPACK_RENDER_UNVERIFIED")));
});
test("unknown audience, welcome, address and opt-out reported as missing",()=>{
 const m=base(),r=auditCampaign(m,bodies(m));
 for(const k of ["ELIGIBLE_EMAIL_AUDIENCE_UNKNOWN","FIELD_BOOK_WELCOME_RECEIPT_UNKNOWN","LEGAL_POSTAL_FOOTER_UNVERIFIED","UNSUBSCRIBE_RENDER_UNVERIFIED","FOUNDER_SEND_APPROVAL_ABSENT"])assert.ok(r.systemic.includes(k));
});