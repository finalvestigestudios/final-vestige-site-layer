import fs from "node:fs";
import test from "node:test";
import assert from "node:assert/strict";

const D = new URL(".", import.meta.url);
const read = (name) => fs.readFileSync(new URL(name, D), "utf8");
const state = () => JSON.parse(read("RELEASE_EVIDENCE.json"));
const issue = () => read("ISSUE05_OPTIONAL.md");
const html = () => read("ISSUE05_OPTIONAL.html");
const plain = () => read("ISSUE05_OPTIONAL.txt");

test("six original slots retained", () => assert.equal(state().issues.length, 6));
test("four editorial and two commercial slots", () => {
  assert.equal(state().issues.filter(x => x.kind === "editorial").length, 4);
  assert.equal(state().issues.filter(x => x.kind === "commercial").length, 2);
});
test("all issues explicitly held", () => assert.ok(state().issues.every(x => x.state.startsWith("HOLD_"))));
test("founder has not approved sends", () => assert.equal(state().email_platform.final_founder_send_approval, false));
test("scheduled/new-post auto email remains off", () => assert.equal(state().email_platform.auto_email_new_posts, false));
test("total/confirmed/unconfirmed never additive", () => {
 const w=state().email_platform;
 assert.deepEqual([w.total_subscribers,w.confirmed,w.unconfirmed],[3,3,2]);
 assert.equal(w.counts_are_not_additive,true);
 assert.equal(w.unique_email_eligible_recipients,null);
});
test("reader follower counts kept distinct", () => {
 const w=state().email_platform;
 assert.equal(w.reader_followers_separate,3);
 assert.equal(w.direct_email_followers_separate,0);
});
test("no received welcome claim", () => assert.equal(state().email_platform.received_fieldbook_welcome_verified,false));
test("native email rendering remains unknown", () => {
 const w=state().email_platform;
 for (const k of ["native_preview_verified","native_subject_verified","native_preheader_mapping_verified"]) assert.equal(w[k],false);
});
test("sender postal and functioning unsubscribe unresolved", () => {
 const w=state().email_platform;
 assert.equal(w.fv_postal_address_verified,false);
 assert.equal(w.received_unsubscribe_verified,false);
});
test("named publisher affiliate permission absent", () => assert.equal(state().merchant.named_final_vestige_acceptance_verified,false));
test("both exact SKU email channel permissions absent", () => {
 const m=state().merchant;
 assert.equal(m.zen12_sku_email_marketing_permission_verified,false);
 assert.equal(m.total_focus_sku_email_marketing_permission_verified,false);
});
test("no earning URL or published approved guide", () => {
 const m=state().merchant;
 for (const k of ["issued_earning_url_verified","guide_03_public_and_approved","guide_05_public_and_approved"]) assert.equal(m[k],false);
});
test("no claimed settled orders or realized net revenue", () => {
 const m=state().measurement;
 for (const k of ["paid_orders_settled","gross_revenue","refunds","fees","realized_net_revenue","net_revenue_per_1000_qualified_human_sessions"]) assert.equal(m[k],null);
});
test("both 7 and 30-day denominators unverified", () => {
 const m=state().measurement;
 assert.equal(m.qualified_human_sessions_7d,null);
 assert.equal(m.qualified_human_sessions_30d,null);
});
test("strict provider confirmation contract and no PII", () => {
 const m=state().measurement;
 assert.match(m.authority,/provider/);
 assert.match(m.deduplication,/opaque/);
 assert.match(m.deduplication,/no raw email/);
});
test("commercial CTA disabled in every format", () => {
 for (const x of [issue(),html(),plain()]) assert.match(x,/DISABLED/i);
 assert.ok(!html().includes('href="https://finalvestige.com/mind/'));
});
test("commission disclosure beside disabled CTA", () => {
 const h=html();
 const a=h.indexOf("ONE PLANNED CTA");
 const b=h.indexOf("Commercial relationship disclosure");
 assert.ok(a>0 && b>a && b-a<500);
});
test("no pricing or time-limited discount quoted in actual email", () => {
 for (const x of [issue(),html(),plain()]) assert.ok(!/[$][0-9]+|act now|limited spots/i.test(x));
});
test("product-specific research and two seller sources in all formats", () => {
 const links=["wellcomecollection.org/works/bsjt9ey8","10.1016/j.concog.2025.103948","hypnosislive.com/mental-skills/total-focus","hypnosislive.com/faq"];
 for(const x of [issue(),html(),plain()]) for(const link of links) assert.ok(x.includes(link),link);
});
test("vendor claims not falsely proved", () => {
 assert.match(issue(),/seller.s promises|seller claims|seller's promises/i);
 assert.match(html(),/seller claims, not independently proven outcomes/i);
});
test("static HTML accessibility baseline", () => {
 const h=html();
 for(const x of ['lang="en"','name="viewport"','role="presentation"','<h1','<ol>','COMPLIANCE STOP']) assert.ok(h.includes(x),x);
});
test("static HTML excludes scripts, forms, trackers and active merchant CTAs", () => {
 const h=html().toLowerCase();
 for(const x of ["<script","<iframe","<form","<img","<video","<audio",'href="https://affiliates.']) assert.ok(!h.includes(x),x);
});
test("plaintext is honest about footer", () => {
 const p=plain();
 for(const x of ["SUBJECT PROPOSAL","PREHEADER PROPOSAL","SOURCES","STOP","DO NOT SEND"]) assert.ok(p.includes(x),x);
});
test("all actions that could contact or release are prohibited", () => {
 const a=state().prohibited_automated_actions;
 for(const x of ["send_email","test_email","schedule_email","publish_wordpress","subscriber_import","enable_affiliate_links","change_site_settings","merge_pull_request"]) assert.ok(a.includes(x));
});
test("exact original six master pinned", () => assert.equal(state().provenance.original_exact_sha,"d57ccdba3aee8f065e143e101c2945f4f3d01647"));
test("source ledger includes legal and provider docs", () => {
 const s=read("SOURCE_AND_PERMISSION_LEDGER.md");
 for (const x of ["wordpress.com/support/subscribers/","ftc.gov/business-guidance/resources/can-spam-act","OFFER","NOT COMPUTABLE"]) assert.ok(s.includes(x),x);
});
