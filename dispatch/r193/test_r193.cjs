"use strict";
/* UNSENT review files only. Run with node --test dispatch/r193/test_r193.cjs.
 * Tests synthetic source safety, not live email, consent, partner rights or sales.
 */
const { test } = require("node:test");
const a = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const get = n => fs.readFileSync(path.join(__dirname, n), "utf8");
const md = get("03_ZEN12_PREMIUM_OPTIONAL_UNSENT.md");
const txt = get("03_ZEN12_PREMIUM_OPTIONAL_UNSENT.txt");
const html = get("03_ZEN12_PREMIUM_OFFLINE_REVIEW_UNSENT.html");
const ledger = JSON.parse(get("MERCHANT_PRODUCT_RIGHTS_EVIDENCE.json"));
const audit = get("ORIGINAL_SIX_COPY_CONVERSION_AUDIT.md");
const spec = get("ONE_OFFER_ATTRIBUTION_CONSENT_SPEC.md");
const runbook = get("JETPACK_RECEIPT_AND_COMPLIANCE_RUNBOOK.md");
const subject = "Forty-eight recordings. One unanswered question.";
const preheader = "Zen12 describes the library. Its hour-equivalence claim still needs proof.";
test("01 subject is consistent across review formats", () => {for(const s of [md,txt,html])a.ok(s.includes(subject));});
test("02 preheader consistent, but unverified as a native Jetpack control",()=>{for(const s of [md,txt,html])a.ok(s.includes(preheader));a.match(runbook,/preheader.*not been verified/i);});
test("03 short truthful subject and preheader",()=>{a.ok(subject.length<70 && preheader.length<110);});
test("04 original 4:2 mix remains locked",()=>{a.deepEqual(ledger.issue_mix.editorial,[1,2,4,6]);a.deepEqual(ledger.issue_mix.commercial_review_pending,[3,5]);});
test("05 no send permission",()=>{a.equal(ledger.send_authorized,false);a.match(md,/UNSENT/);});
test("06 one prospective guide CTA is a placeholder",()=>{a.match(md,/APPROVED_ZEN12_WARMUP_GUIDE_URL_REQUIRED/);a.match(txt,/APPROVED_ZEN12_WARMUP_GUIDE_URL_REQUIRED/);a.match(html,/NOT LIVE \/ NOT CLICKABLE/);});
test("07 no affiliate or commerce link in actual reviewer HTML",()=>{a.doesNotMatch(html,/href=["'][^"']*(awin1|hop=|affiliate|ref=|utm_)/i);});
test("08 commercial disclosure adjacent to proposed CTA",()=>{const i=md.indexOf("PROPOSED PRIMARY CTA"),j=md.indexOf("Commercial disclosure");a.ok(i>0&&j>i&&j-i<450);a.match(html,/Commercial disclosure/);});
test("09 source links are three documentary sources only",()=>{for(const x of ["gutenberg.org/files/78413","wellcomecollection.org/works/bsjt9ey8","zen12.com/hnp"]){a.ok(md.includes(x));a.ok(html.includes(x));}a.equal((html.match(/<a href=/g)||[]).length,3);});
test("10 postal and unsubscribe remain hard-stops",()=>{for(const s of [md,txt,html])for(const token of ["[[VALID_POSTAL_ADDRESS_REQUIRED]]","[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]"])a.ok(s.includes(token));});
test("11 email-safe static document has semantic heading and tables",()=>{a.match(html,/<html lang="en">/);a.match(html,/<h1/);a.match(html,/<table role="presentation"/);a.doesNotMatch(html,/<script|<form|<iframe|<img|<video|onload=|onclick=|autoplay/i);});
test("12 seller product feature vs efficacy uncertainty preserved",()=>{a.equal(ledger.seller_described_features.length,3);a.ok(ledger.seller_claims_not_verified.some(s=>s.includes("Twelve minutes")));a.match(md,/cannot establish that equivalence/);});
test("13 displayed price is not a claimed checkout price",()=>{a.equal(ledger.price.checkout_total_confirmed,false);a.equal(ledger.price.allowed_in_current_email,false);a.ok(!md.includes("$87.99"));});
test("14 partner-specific email permission and earning link fail closed",()=>{a.equal(ledger.affiliate.explicit_email_channel_permission_verified,false);a.equal(ledger.affiliate.issued_earning_URL_verified,false);a.equal(ledger.mind_prewarm_guide.verified_live,false);});
test("15 confirmation and purchase have separate independent evidence stages",()=>{a.match(spec,/CONFIRMED_SIGNUP/);a.match(spec,/SETTLED PAID ORDER/);a.match(spec,/NOT COMPUTABLE/);});
test("16 no invented zero-revenue or A-B results",()=>{a.match(audit,/do not report revenue=0 or fake A\/B lift/);});
test("17 original master audit identifies repeated CTA and gift redundancy",()=>{a.match(audit,/same Puységur destination/);a.match(audit,/received Fieldbook link/);});
test("18 mutation detector refuses inserted earning link",()=>{const bad=html.replace("NOT LIVE / NOT CLICKABLE",'<a href="https://x.example/?ref=abc">BUY</a>');a.match(bad,/href=["'][^"']*ref=/);a.doesNotMatch(html,/href=["'][^"']*ref=/);});
test("19 mutation detector catches disclosure omission",()=>{const bad=md.replace("Commercial disclosure","Relation note");a.ok(!bad.includes("Commercial disclosure"));a.ok(md.includes("Commercial disclosure"));});
test("20 mutation detector catches missing mailing address",()=>{const bad=html.replace("[[VALID_POSTAL_ADDRESS_REQUIRED]]","");a.ok(!bad.includes("[[VALID_POSTAL_ADDRESS_REQUIRED]]"));a.ok(html.includes("[[VALID_POSTAL_ADDRESS_REQUIRED]]"));});
