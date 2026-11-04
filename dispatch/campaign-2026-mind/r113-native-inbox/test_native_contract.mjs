/** Offline Node tests. No WordPress writes, email, or network. */
import { test } from "node:test";
import assert from "node:assert/strict";
import { auditNativeInbox, ORIGINAL_CAMPAIGN_HEAD } from "./native_contract.mjs";
const issues=[
[1,"editorial","The mind is not a camera"],
[2,"editorial","Before hypnosis had a name"],
[3,"commercial-review-pending","The twelve-minute meditation question"],
[4,"editorial","Fourteen seconds. A much longer explanation."],
[5,"commercial-review-pending","Before you press play on a hypnosis audio"],
[6,"editorial","What did seven days of attention reveal?"]
].map(([number,kind,subject])=>({number,kind,subject,preheader:"Copy exists in original manifest"}));
const campaign={source_head:ORIGINAL_CAMPAIGN_HEAD,issues};
const wordpress={subscriptions:true,email_new_posts_by_default:false,email_content_format:"excerpt",total:2,confirmed:2,unconfirmed:2};
const audit=(opts={})=>auditNativeInbox({campaign,wordpress,...opts});
test("six distinct subjects and four/two split preserved",()=>{
 const out=audit(); assert.equal(out.issues.length,6);
 assert.equal(out.issues.filter(i=>i.kind==="editorial").length,4);
 assert.equal(out.issues.filter(i=>i.kind==="commercial-review-pending").length,2);
});
test("no email or paid sale ever assumed",()=>{
 const out=audit(); assert.equal(out.sender_capability,false);
 assert.equal(out.campaign_release,"HOLD_UNSENT");
 assert.equal(out.deliverable_recipients,null);
 assert.equal(out.metric_net_revenue_per_1000_qualified_sessions,null);
 assert.ok(out.issues.every(i=>i.verified_paid_orders===null&&i.release==="HOLD_UNSENT"));
});
test("native WordPress title is subject; preheader unverified",()=>{
 const out=audit();assert.ok(out.issues.every(i=>i.holds.includes("WP_POST_TITLE_MUST_MATCH_SUBJECT")));
 assert.ok(out.issues.every(i=>i.estimated_preheader==="NOT_VERIFIED"));
});
test("excerpt must be explicitly reviewed; don't infer CTA delivery",()=>{
 const out=audit();assert.ok(out.issues.every(i=>i.holds.includes("CUSTOM_EXCERPT_NOT_REVIEWED")));
 assert.ok(out.issues.every(i=>i.holds.includes("FIRST_PARTY_CTA_NOT_VALIDATED")));
});
test("preview is not actual received email",()=>{
 const out=audit({previewEvidence:{1:{desktop_capture_id:"mock",mobile_capture_id:"mock",tablet_capture_id:"mock"}}});
 assert.ok(!out.issues[0].holds.includes("ACTUAL_WP_EDITOR_PREVIEW_NOT_OBSERVED"));
 assert.ok(out.issues[0].holds.includes("ACTUAL_RECEIVED_MIME_NOT_OBSERVED"));
});
test("postal and functional unsubscribe require actual proof",()=>{
 const out=audit();assert.ok(out.issues.every(i=>i.holds.includes("PUBLISHER_POSTAL_NOT_VERIFIED_IN_RECEIVED_EMAIL")));
 assert.ok(out.issues.every(i=>i.holds.includes("FUNCTIONAL_UNSUBSCRIBE_NOT_VERIFIED")));
});
test("commercial issues 03 and 05 have independent merchant holds",()=>{
 const out=audit();for(const i of [2,4]){assert.ok(out.issues[i].holds.includes("MERCHANT_EMAIL_RIGHTS_NOT_VERIFIED"));assert.ok(out.issues[i].holds.includes("COMMERCIAL_DISCLOSURE_MISSING_FROM_INBOX_EXCERPT"));}
 assert.ok(!out.issues[0].holds.includes("MERCHANT_EMAIL_RIGHTS_NOT_VERIFIED"));
});
test("source SHA mismatch fails closed",()=>{
 assert.ok(audit({campaign:{...campaign,source_head:"not-original"}}).global_holds.includes("CAMPAIGN_SHA_NOT_LOCKED"));
});
test("six count and commercial mix mismatches fail closed",()=>{
 assert.ok(audit({campaign:{...campaign,issues:issues.slice(1)}}).global_holds.includes("SIX_ISSUE_MANIFEST_NOT_VERIFIED"));
 assert.ok(audit({campaign:{...campaign,issues:issues.map(i=>({...i,kind:"editorial"}))}}).global_holds.includes("FOUR_TWO_MIX_NOT_VERIFIED"));
});
test("native settings drift fails closed",()=>{
 assert.ok(audit({wordpress:{...wordpress,email_new_posts_by_default:true}}).global_holds.includes("AUTO_SEND_NOT_CONFIRMED_OFF"));
 assert.ok(audit({wordpress:{...wordpress,email_content_format:"full"}}).global_holds.includes("OBSERVED_EXCERPT_MODE_DRIFT"));
});
test("invalid merchant CTA is blocked even with a post title",()=>{
 const a=audit({editions:{3:{post_title:issues[2].subject,custom_excerpt:"We may receive a commission.",cta_url:"https://zen12.com"}}});
 assert.ok(a.issues[2].holds.includes("FIRST_PARTY_CTA_NOT_VALIDATED"));
});
test("approved-looking synthetic attestation never authorizes release",()=>{
 const a=audit({attestation:{merchant_email_rights_3:true,approved_guide_live_3:true,earning_link_format_3:true,merchant_claims_fresh_3:true}});
 assert.equal(a.issues[2].release,"HOLD_UNSENT");
 assert.equal(a.campaign_release,"HOLD_UNSENT");
});
test("previous source and two subscribers do not assert deliverability",()=>{
 const a=audit();assert.equal(a.deliverable_recipients,null);
 assert.equal(a.newsletter_auto_send,false);
});
