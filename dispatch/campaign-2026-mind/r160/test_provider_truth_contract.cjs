/* R160 native Node / JS test suite. Only synthetic aggregates: NEVER production subscriber rows. */
"use strict";
const assert=require("node:assert/strict");
const {test}=require("node:test");
const {evaluate,checkSnapshot,EXPECTED_PDF}=require("./provider_truth_contract.cjs");
const sample=()=>({
  site:"https://finalvestige.com",
  newsletter:{enabled:true,new_post_default:false,can_send:true,email_format:"full",welcome_points_to_fieldbook:true},
  counts:{total:3,confirmed:3,unconfirmed:2,suppressed:0,paid:0},
  pages:{
    dispatch:{id:523,url:"https://finalvestige.com/dispatch/",publish_state:"publish",api_contains_email_input:false,api_self_anchor:true,screenshot_ready:true},
    focus:{id:1579,url:"https://finalvestige.com/focus/",publish_state:"publish",api_contains_email_input:false,api_self_anchor:true,screenshot_ready:true}
  },
  media:{id:1737,url:EXPECTED_PDF,mime_type:"application/pdf",filesize:599946}
});
test("read-only snapshot retains nonadditive, nonpersonal aggregate counts",()=>{
  let x=evaluate(sample());assert.equal(x.provider_reported.total,3);assert.equal(x.provider_reported.unconfirmed,2);
  assert.equal(x.subscriber_categories_additive,false);assert.equal(x.authoritative_email_eligibility,"NOT_VERIFIED");
  assert.equal(x.net_new_confirmed_signup_events,"NOT_VERIFIED");
});
test("published Fieldbook media object DOES NOT prove welcome delivery or completed PDF download",()=>{
  let x=evaluate(sample());assert.equal(x.fieldbook_pdf_asset,"PROVIDER_MEDIA_ASSET_MATCHED");
  assert.equal(x.fieldbook_pdf_meta.wordpress_media_id,1737);
  assert.equal(x.actual_received_welcome,"NOT_VERIFIED");assert.equal(x.download_completed,"NOT_VERIFIED");
});
test("API self links and screenshot captures never prove a usable guest form",()=>{
  const x=evaluate(sample());assert.equal(x.api_pages.length,2);
  for(const p of x.api_pages){assert.equal(p.api_subscribe_self_link,true);assert.equal(p.screenshot_capture_ready,true);
    assert.equal(p.guest_interactive_form,"NOT_VERIFIED");assert.equal(p.verified_subscribe_completion,"NOT_VERIFIED");}
  assert.equal(x.actual_guest_first_click,"GUEST_SIGNUP_NOT_PROVEN");
});
test("all six remain HOLD; exactly two additional merchant holds",()=>{
  const x=evaluate(sample());assert.deepEqual(x.newsletter_release.map(v=>v.status),Array(6).fill("HOLD_UNSENT"));
  assert.deepEqual(x.newsletter_release.filter(v=>v.merchant_gate!==null).map(v=>v.issue),[3,5]);
  assert.equal(x.posted_or_sent_anything,false);
});
test("technical can-send does not mean authorization; zero artificial sales",()=>{
  const x=evaluate(sample());assert.ok(x.warnings.includes("TECHNICAL_SEND_CAPABILITY_IS_NOT_FOUNDER_AUTHORIZATION"));
  assert.equal(x.independently_reported_paid_orders,"NOT_VERIFIED");
  assert.equal(x.realized_net_revenue_per_1000_qualified_sessions,null);
});
test("tampered media URL and MIME cannot fake PDF asset evidence",()=>{
  for(const f of [s=>s.media.url+="/other",s=>s.media.mime_type="text/html",s=>s.media.filesize=0]){
    const s=sample();f(s);assert.equal(evaluate(s).fieldbook_pdf_asset,"NOT_VERIFIED");
  }
});
test("screenshot ready false or API input present cannot assert confirmation",()=>{
  for(const field of ["screenshot_ready","api_contains_email_input","api_self_anchor"]){
    const s=sample();s.pages.focus[field]=!s.pages.focus[field];
    const x=evaluate(s);assert.equal(x.net_new_confirmed_signup_events,"NOT_VERIFIED");
    assert.equal(x.api_pages[1].verified_subscribe_completion,"NOT_VERIFIED");
  }
});
test("even optimistic settings cannot unlock emails or affiliate income",()=>{
  const s=sample();s.newsletter.new_post_default=true;s.newsletter.can_send=true;s.newsletter.email_format="full";
  const x=evaluate(s);assert.equal(x.newsletter_release[2].merchant_gate,"HOLD_MERCHANT");
  assert.ok(x.warnings.includes("AUTO_SEND_DEFAULT_ON_DANGEROUS"));
  assert.equal(x.native_email_preview,"NOT_VERIFIED");assert.equal(x.verified_postal_footer,"NOT_VERIFIED");
  assert.equal(x.functioning_unsubscribe,"NOT_VERIFIED");
});
test("hard reject malicious/malformed, private, negative and wrong-site values",()=>{
  const mutations=[
    s=>s.site="https://attacker.example",
    s=>s.counts.total=-1,s=>s.counts.confirmed=2.5,s=>s.counts.unconfirmed="2",
    s=>s.counts.paid=Number.NaN,s=>s.counts.suppressed=Infinity,
    s=>s.newsletter.enabled="true",s=>s.newsletter.can_send=null,s=>s.newsletter.email_format=null,
    s=>s.pages.dispatch.id=1579,s=>s.pages.focus.url="https://attacker.example",
    s=>s.pages.dispatch.publish_state="draft",s=>s.pages.focus.api_self_anchor="true",
    s=>s.media.filesize=-20,s=>delete s.media,s=>delete s.pages,s=>delete s.newsletter
  ];
  for(const m of mutations){let s=sample();m(s);assert.throws(()=>evaluate(s));}
});
test("provider counts are not summed even if unconfirmed > confirmed",()=>{
  const s=sample();s.counts.total=3;s.counts.confirmed=3;s.counts.unconfirmed=18;
  const x=evaluate(s);assert.equal(x.provider_reported.total,3);assert.equal(x.subscriber_categories_additive,false);
});
test("explicit missing evidence is exposed with actionable owner handoffs",()=>{
  const x=evaluate(sample());assert.ok(x.evidence_needed.some(s=>s.includes("Signed-out")));
  assert.ok(x.evidence_needed.some(s=>s.includes("Inspire3")));
  assert.ok(x.evidence_needed.some(s=>s.includes("postal")));
  assert.equal(x.affiliate_zen12_email_permission,"NOT_VERIFIED");
  assert.equal(x.affiliate_total_focus_email_permission,"NOT_VERIFIED");
});
