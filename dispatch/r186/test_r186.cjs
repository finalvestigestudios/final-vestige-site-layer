"use strict";
// Offline self-test; run with node --test. No network; never sends or activates.
const {test}=require("node:test"); const assert=require("node:assert/strict");
const fs=require("node:fs"); const path=require("node:path");
const p=f=>fs.readFileSync(path.join(__dirname,f),"utf8");
const md=()=>p("ISSUE03_ZEN12_OPTIONAL_DRAFT.md");
const txt=()=>p("ISSUE03_REVIEW_ONLY.txt");
const html=()=>p("ISSUE03_REVIEW_ONLY.html");
const gate=()=>JSON.parse(p("RELEASE_ATTESTATIONS.json"));
test("four editorial / two commercial original campaign unchanged",()=>{assert.deepEqual(gate().mix,{editorial:4,commercial_pending:2});assert.equal(gate().master_pr,175)});
test("one proposed CTA is inactive in all formats",()=>{for(const s of [md(),txt(),html()]){assert.ok(s.includes("[[APPROVED_LIVE_ZEN12_GUIDE_URL_REQUIRED]]"));assert.ok(!/href=["'][^"']*(?:awin1\.com|affiliates\.inspire3\.com\/(?:track|click|go)|[?&](?:aff_id|affiliate_id|clickid|subid)=)/i.test(s))}});
test("subject and preheader agree in all formats",()=>{for(const s of [md(),txt(),html()]){assert.ok(s.includes("Does twelve minutes buy an hour?"));assert.ok(s.includes("A short routine is easy to test."))}});
test("adjacent disclosure and placeholders in all formats",()=>{for(const s of [md(),txt(),html()]){assert.match(s,/may earn a commission/i);assert.ok(s.includes("[[VALID_FINAL_VESTIGE_PHYSICAL_POSTAL_ADDRESS_REQUIRED]]"));assert.ok(s.includes("[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]"))}});
test("specific offer claims framed as seller assertions",()=>{for(const s of [md(),txt(),html()]){assert.match(s,/seller/i);assert.match(s,/48/);assert.ok(!/clinically proven to reprogram|guaranteed income|cures anxiety/i.test(s))}});
test("HTML review-only is semantically accessible and email-conservative",()=>{const h=html();assert.match(h,/<html lang="en">/);assert.match(h,/<h1\b/);assert.match(h,/role="presentation"/);assert.ok(!/<script\b|<form\b|onclick\s*=|style\s*=\s*"[^"]*position:\s*fixed/i.test(h))});
test("source links and first-party historic bridge present",()=>{for(const s of [md(),txt(),html()]){assert.ok(s.includes("https://zen12.com/hnp"));assert.ok(s.includes("https://finalvestige.com/2026/11/02/mesmerism/"))}});
test("absolute release hard stop",()=>{const x=gate();assert.equal(x.status,"HOLD_UNSENT");assert.equal(x.approval.send_authorized,false);assert.equal(x.approval.publication_authorized,false);assert.equal(x.merchant.email_channel_permission,false);assert.equal(x.merchant.approved_affiliate_url,null);assert.equal(x.footer.native_email_preview_obtained,false);assert.equal(x.attribution.net_revenue_per_1000_human_sessions,null)});
test("no third-party tracking or buyer PII in reviewer HTML",()=>{const h=html();assert.ok(!/<img\b[^>]+src=["']https?:/i.test(h));assert.ok(!/\b(?:pixel|gtag|fbq)\(/.test(h));assert.ok(!/[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}/i.test(h))});
test("merchant guarantee and price not presented as independently established",()=>{for(const s of [md(),txt(),html()]){assert.ok(!/\$\d+(?:\.\d\d)?/.test(s));assert.ok(!/guaranteed to|cure|risk.free offer/i.test(s))}});
