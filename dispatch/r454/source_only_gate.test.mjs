/** Dispatch R454 native Node regression definitions; no network, WordPress or send.
 * Synthetic fixtures are NOT Final Vestige results.
 */
import test from "node:test";
import assert from "node:assert/strict";
import {HARD_HOLD,proof,hasSafeEnvelope,classifyAudience,reviewEdition,planSix,classifyMoney} from "./source_only_gate.mjs";
const P={verified:true,source_ref:"provider:test-evidence",checked_at:"2026-11-18T19:32:00Z"};
const baseBody="A documented historical claim needs both the original record and a second source. ".repeat(6);
const makeIssue=(i)=>({number:i,kind:([3,5].includes(i)?"commercial":"editorial"),
  product:i===3?"Zen12":i===5?"Hypnosis Live":null,status:HARD_HOLD,
  subject:"The record and the reader",preheader:"A careful reading of contested historical evidence",
  body:baseBody,sources:["https://finalvestige.com/editorial-standards/","https://finalvestige.com/focus/"],
  cta:{label:"Read the source",url:[3,5].includes(i)?null:"https://finalvestige.com/focus/"},
  near_cta_disclosure:[3,5].includes(i)?"Commercial relationship under review. No earning link is active.":null});
const ctx=()=>({site:{email_new_posts_by_default:false,email_content_format:"full",
  newsletter_categories_enabled:false,reply_to:"no-reply"}});
test("permanent HARD HOLD always false",()=>assert.equal(HARD_HOLD,"HOLD_UNSENT"));
for(const [name,v] of [["null",null],["empty",{}],["synthetic flag",{verified:true}],
  ["relative ref",{...P,source_ref:"/test"}],["no timestamp",{...P,checked_at:null}],
  ["false",{...P,verified:false}]])
  test("reject proof "+name,()=>assert.equal(proof(v),false));
test("recognize structurally complete proof only",()=>assert.equal(proof(P),true));
for(const [name,value] of [["markdown","** Subject"],["html","<b>Subject</b>"],["linebreak","Hello\nBCC:injected"],
  ["guarantee","Miracle cure guaranteed"],["whitespace","   "],["null",null]])
  test("reject subject "+name,()=>assert.equal(hasSafeEnvelope(value),false));
test("clean subject accepted",()=>assert.equal(hasSafeEnvelope("Measured evidence, not magic"),true));
test("three contradictory WordPress surfaces remain CONFLICT",()=>{
  const x=classifyAudience({newsletter:{total:3,confirmed:3,unconfirmed:2},
    subscribers:{email:3,reader:0,unconfirmed:2},followers:{email:0,wpcom:3}});
  assert.equal(x.status,"CONFLICT");assert.equal(x.conflicts.length,2);
  assert.equal(x.confirmed_new,null);assert.equal(x.unique_external_readers,null);
});
test("agreement still not external audience proof",()=>{
  assert.match(classifyAudience({newsletter:{total:3,confirmed:3,unconfirmed:2},
    subscribers:{email:3,reader:3,unconfirmed:2},followers:{email:3,wpcom:3}}).status,/AGREEMENT/);
});
test("invalid provider count becomes unknown",()=>{
  assert.equal(classifyAudience({newsletter:{total:3,confirmed:"3",unconfirmed:2},
    subscribers:{email:3,reader:0,unconfirmed:2},followers:{email:0,wpcom:3}}).status,"UNKNOWN");
});
test("missing provider source becomes unknown",()=>assert.equal(classifyAudience({}).status,"UNKNOWN"));
test("editorial issue cannot transmit with all declared proof",()=>{
  const all={...ctx(),actual_native_preview:P,publisher_postal_address:P,functional_unsubscribe:P,
    actual_received_welcome:P,founder_selection:P,founder_final_send_authorization:P};
  const r=reviewEdition(makeIssue(1),all);
  assert.equal(r.status,HARD_HOLD);assert.equal(r.can_send,false);
});
test("editorial missing evidence flags footer, preview, welcome and approval",()=>{
  const r=reviewEdition(makeIssue(1),ctx());
  for(const k of ["native_jetpack_preview_not_witnessed","valid_fv_postal_not_witnessed",
    "functional_opt_out_not_witnessed","actual_welcome_delivery_not_witnessed",
    "founder_final_send_approval_missing"])assert.ok(r.problems.includes(k));
});
test("commercial has unique partner/rights/guide/checkout hold",()=>{
  const r=reviewEdition(makeIssue(3),ctx());
  for(const k of ["named_partner_approval_missing","email_permission_missing",
    "live_guide_missing","earning_url_missing","checkout_terms_missing"])
    assert.ok(r.problems.includes(k));
});
test("commercial CTA cannot be switched to a URL even if first-party",()=>{
  const r=reviewEdition({...makeIssue(5),cta:{label:"Read buyer guide",url:"https://finalvestige.com/focus/"}},ctx());
  assert.ok(r.problems.includes("commercial_destination_must_stay_inactive_until_release"));
});
test("commercial proof attestations still cannot authorize send",()=>{
  const r=reviewEdition(makeIssue(3),{...ctx(),partner_approval:P,email_channel_rights:P,
    offer_specific_creative:P,live_approved_guide:P,merchant_issued_link:P,checkout_terms:P,
    actual_native_preview:P,publisher_postal_address:P,functional_unsubscribe:P,
    actual_received_welcome:P,founder_selection:P,founder_final_send_authorization:P});
  assert.equal(r.can_send,false);assert.equal(r.status,HARD_HOLD);
  assert.equal(r.static_review,"HUMAN_REVALIDATION_REQUIRED");
});
test("internal reviewer text detection",()=>{
  const r=reviewEdition({...makeIssue(1),body:baseBody+"START REVIEWER NOTES\n"},ctx());
  assert.ok(r.problems.includes("reviewer_notes_leak"));
});
test("wrong kind fails original 4:2",()=>{
  const r=reviewEdition({...makeIssue(2),kind:"commercial"},ctx());
  assert.ok(r.problems.includes("incorrect_4_2_identity"));
});
test("wrong exact product identity fails",()=>{
  const r=reviewEdition({...makeIssue(3),product:"Total Focus"},ctx());
  assert.ok(r.problems.includes("incorrect_product"));
});
test("send state mutation fails",()=>{
  const r=reviewEdition({...makeIssue(1),status:"READY"},ctx());
  assert.ok(r.problems.includes("attempted_release_state_mutation"));
});
test("unsafe external or email destination fails",()=>{
  const r=reviewEdition({...makeIssue(1),cta:{label:"Click",url:"https://seller.example/"}},ctx());
  assert.ok(r.problems.includes("unapproved_cta_destination"));
});
test("no source chain fails",()=>{
  const r=reviewEdition({...makeIssue(1),sources:["http://bad.test"]},ctx());
  assert.ok(r.problems.includes("insufficient_https_sources"));
});
test("unexpected newsletter auto-send flag fails",()=>{
  const r=reviewEdition(makeIssue(1),{...ctx(),site:{...ctx().site,email_new_posts_by_default:true}});
  assert.ok(r.problems.includes("newsletter_auto_send_default_not_off"));
});
test("unexpected excerpt transport fails",()=>{
  const r=reviewEdition(makeIssue(1),{...ctx(),site:{...ctx().site,email_content_format:"excerpt"}});
  assert.ok(r.problems.includes("current_full_content_transport_mismatch"));
});
test("no unsupported segmentation assumptions",()=>{
  const r=reviewEdition(makeIssue(1),{...ctx(),site:{...ctx().site,newsletter_categories_enabled:true}});
  assert.ok(r.problems.includes("segmentation_must_be_reverified"));
});
test("all six preserved with no release channel",()=>{
  const r=planSix([1,2,3,4,5,6].map(makeIssue),Array.from({length:6},ctx));
  assert.deepEqual(r.allocation,{editorial:4,commercial:2});
  assert.ok(r.results.every(x=>x.status===HARD_HOLD&&!x.can_send));
});
test("missing slot rejected",()=>assert.equal(planSix([makeIssue(1)],[]).can_send,false));
test("reordered slot rejected",()=>{
  const issues=[1,2,3,4,5,6].map(makeIssue);[issues[0],issues[1]]=[issues[1],issues[0]];
  assert.ok(planSix(issues,Array.from({length:6},ctx)).problems.includes("order_or_identity_invalid"));
});
test("incomplete real-world revenue is uncomputable",()=>{
  assert.equal(classifyMoney({orders:[],qualified_human_sessions:3}).status,"UNCOMPUTABLE");
});
test("no zero denominator revenue fabrication",()=>{
  assert.equal(classifyMoney({settlement_proof:P,qualified_human_sessions_proof:P,
    ledger_complete:true,orders:[],qualified_human_sessions:0}).net_per_1000_cents,null);
});
test("synthetic complete settlement math is provisional only",()=>{
  const x=classifyMoney({settlement_proof:P,qualified_human_sessions_proof:P,ledger_complete:true,
    qualified_human_sessions:100,orders:[{id:"synthetic-1",kind:"merchant_order",
      status:"settled",proof:P,gross_cents:1000,fees_cents:100,refund_cents:200}]});
  assert.equal(x.status,"PROVISIONAL_AUDIT_ONLY");assert.equal(x.net_per_1000_cents,7000);
});
test("bad refund accounting rejected",()=>{
  const x=classifyMoney({settlement_proof:P,qualified_human_sessions_proof:P,ledger_complete:true,
    qualified_human_sessions:100,orders:[{id:"synthetic-1",kind:"merchant_order",
      status:"settled",proof:P,gross_cents:100,fees_cents:90,refund_cents:20}]});
  assert.equal(x.status,"UNCOMPUTABLE");
});
test("duplicate settlements rejected, no double count",()=>{
  const order={id:"synthetic-1",kind:"merchant_order",status:"settled",proof:P,
    gross_cents:100,fees_cents:10,refund_cents:0};
  assert.equal(classifyMoney({settlement_proof:P,qualified_human_sessions_proof:P,
    ledger_complete:true,qualified_human_sessions:100,orders:[order,order]}).status,"UNCOMPUTABLE");
});
