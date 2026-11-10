"use strict";
const assert=require("node:assert/strict");
const {test}=require("node:test");
const {auditSignupSnapshot}=require("../signup_gate.cjs");
const {auditReceivedSpecimen}=require("../receipt_gate.cjs");
const fallback=id=>'<div class="wp-block-jetpack-subscriptions"><a href="https://finalvestige.com/?post_type=page&amp;p='+id+'">Subscribe</a></div>';
test("self linking REST fallback does not prove live form broken",()=>{
 const x=auditSignupSnapshot({blockHtml:fallback(523),expectedPageId:523});
 assert.equal(x.self_linking_subscribe_fallback,true);assert.equal(x.live_signup_working,null);
 assert.equal(x.requires_real_browser_render_and_keyboard_QA,true);
});
test("Focus Fieldbook button-only copy also counts as self page link",()=>{
 const h='<div class="wp-block-jetpack-subscriptions"><a href="https://finalvestige.com/?post_type=page&#038;p=1579">Send me the fieldbook</a></div>';
 const x=auditSignupSnapshot({blockHtml:h,expectedPageId:1579});
 assert.equal(x.self_linking_subscribe_fallback,true);assert.equal(x.live_signup_working,null);
});
test("different page link is not matching fallback",()=>assert.equal(auditSignupSnapshot({blockHtml:fallback(1579),expectedPageId:523}).self_linking_subscribe_fallback,false));
test("actually present form does not trigger fallback",()=>{
 const x=auditSignupSnapshot({blockHtml:fallback(523)+'<form><input type="email"></form>',expectedPageId:523});
 assert.equal(x.requires_real_browser_render_and_keyboard_QA,false);
});
const baseline={
 kind:"received_from_provider",receiptProofRef:"evidence/receipt_0001",renderProofRef:"evidence/render_0001",
 inboxProofRef:"evidence/inbox_00001",optoutProofRef:"evidence/optout_0001",optoutResult:"PASS",
 expectedSubject:"The mind is not a camera",
 expectedPreheader:"What an old record can teach us about the difference between seeing and knowing.",
 observedInboxPreview:"What an old record can teach us about the difference between seeing and knowing.",
 rawHeaders:"From: Final Vestige Studios <donotreply@wordpress.com>\nSubject: The mind is not a camera",
 renderedText:"An original evidence-first newsletter from Final Vestige.\nPostal: 123 Example Avenue, Sample City, CA 99999\nYou can unsubscribe anytime via this link.",
 renderedHtml:'<html><body><p>Original article content.</p><a href="https://example.invalid/opt-out">Unsubscribe</a></body></html>',
 publisherPostal:"123 Example Avenue, Sample City, CA 99999"
};
test("synthetic complete specimen never authorizes sending or proves welcome",()=>{
 const q=auditReceivedSpecimen(baseline); assert.equal(q.local_candidate_only,true);
 assert.equal(q.authorized_to_send,false);assert.equal(q.double_opt_in_proven,false);
 assert.equal(q.independently_settled_revenue,null);
});
const mutations=[
 ["no receipt artifact",{receiptProofRef:""},"real_receipt_artifact"],
 ["untrusted artifact",{receiptProofRef:"http://public.test/a"},"real_receipt_artifact"],
 ["fake type",{kind:"screenshot_only"},"real_receipt_artifact"],
 ["wrong subject",{expectedSubject:"Wrong"},"subject_exact"],
 ["missing sender",{rawHeaders:"From: Ads <example@example.org>\nSubject: The mind is not a camera"},"sender_matches_expected"],
 ["no rendering",{renderProofRef:""},"visible_body_evidence"],
 ["short rendering",{renderedText:"hello"},"visible_body_evidence"],
 ["no preheader photo",{inboxProofRef:""},"preheader_in_inbox"],
 ["inbox mismatch",{observedInboxPreview:"Nothing"},"preheader_in_inbox"],
 ["no address",{publisherPostal:""},"publisher_postal"],
 ["wrong address",{publisherPostal:"5 Fiction Rd, Faraway"},"publisher_postal"],
 ["provider address substituted",{publisherPostal:"Automattic Inc, 123 Placeholder Street"},"publisher_postal"],
 ["no unsubscribe text",{renderedText:"This is a long synthetic message without opt-out instruction, duplicated across many words for a valid length."},"unsubscribe_exposed"],
 ["no unsubscribe html",{renderedHtml:"<p>Unsubscribe</p>"},"unsubscribe_exposed"],
 ["no optout proof",{optoutProofRef:""},"unsubscribe_functional_separate_proof"],
 ["optout failed",{optoutResult:"FAIL"},"unsubscribe_functional_separate_proof"],
 ["postal token",{renderedText:baseline.renderedText+" [[VALID_POSTAL_ADDRESS_REQUIRED]]"},"no_unresolved_tokens"],
 ["footer token",{renderedHtml:baseline.renderedHtml+" [[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]"},"no_unresolved_tokens"],
 ["merchant href",{renderedHtml:baseline.renderedHtml+'<a href="https://zen12.com/hnp">Purchase</a>'},"no_active_merchant_url"]
];
for(const [name,change,failKey] of mutations)test(name,()=>{
 const q=auditReceivedSpecimen({...baseline,...change});
 assert.equal(q.checks[failKey],false);assert.equal(q.released,false);
});
