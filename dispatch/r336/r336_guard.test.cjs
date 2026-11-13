// Native offline QA: node --test dispatch/r336/r336_guard.test.cjs
"use strict";
const {test} = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const get = f => fs.readFileSync(path.join(__dirname,f),"utf8");
const md=get("issue05-total-focus-candidate.md");
const html=get("issue05-total-focus-candidate.html");
const txt=get("issue05-total-focus-candidate.txt");
const fact=get("MERCHANT_FACT_AND_CLAIM_LEDGER.md");
const funnel=get("OFFER_FUNNEL_RELEASE_DECISIONS.md");
const manifest=JSON.parse(get("../campaign-2026-mind/manifest.json"));
test("master mix stays six issues: four editorial, two commercial",()=>{
assert.equal(manifest.issues.length,6);
assert.equal(manifest.issues.filter(x=>x.kind==="editorial").length,4);
assert.equal(manifest.issues.filter(x=>x.kind.includes("commercial")).length,2);
});
test("optional replacement never adopted and unsent",()=>{
for(const s of [md,html,txt]) {assert.match(s,/NOT ADOPTED/); assert.match(s,/UNSENT/)}
});
test("reader subject not a guaranteed product claim",()=>{
assert.match(md,/Before you buy a focus hypnosis recording/);
assert.ok("Before you buy a focus hypnosis recording".length<60);
assert.doesNotMatch(md,/guaranteed focus|limitless powers|100% razor-sharp/i);
});
test("product-specific format is seller-attributed",()=>{
for(const s of [md,html,txt]) {assert.match(s,/Total Focus/);assert.match(s,/33.minute/);assert.match(s,/47 MB/);assert.match(s,/seller/i)}
});
test("vendor promise distinguished from independent science",()=>{
for(const s of [md,txt]){assert.match(s,/vendor advertisements/); assert.match(s,/does not|Neither establishes|not proof/i)}
});
test("FAQ five-session refund cap cannot be hidden",()=>{
for(const s of [md,html,txt,fact])assert.match(s,/five sessions per year/i)
});
test("no price, countdown, fake scarcity, or checkout prompt in recipient drafts",()=>{
for(const s of [md,html,txt]){assert.doesNotMatch(s,/\$\s?\d/); assert.doesNotMatch(s,/buy now|add to cart|last chance|only \d+ left/i)}
});
test("commercial disclosure appears in same email beside inactive guide",()=>{
for(const s of [md,html,txt]) {assert.match(s,/may earn a commission/);assert.match(s,/guide/)}
});
test("html contains no active affiliate or seller href",()=>{
assert.doesNotMatch(html,/<a\b[^>]*href\s*=\s*["'][^"']*(?:hypnosislive|inspire3)/i);
assert.doesNotMatch(html,/<a\b[^>]*href\s*=\s*["'][^"']*buyer/i);
});
test("real mailing footer and unsubscribe remain blocked",()=>{
assert.match(html,/physical postal address/);
assert.match(html,/NOT been evidenced/);
assert.match(txt,/LEGAL HOLD/);
assert.match(md,/NOT VERIFIED/);
});
test("email-safe static semantic HTML",()=>{
assert.match(html,/<html lang="en">/);
assert.match(html,/<h1/);
assert.match(html,/role="presentation"/);
assert.doesNotMatch(html,/<script|<form|onclick\s*=|<iframe/i);
});
test("exact merchant FAQ and independent research linked in docs",()=>{
for(const u of ["https://hypnosislive.com/faq","https://pubmed.ncbi.nlm.nih.gov/39032268/","https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business"])
assert.ok(fact.includes(u));
});
test("unknown revenue is not fabricated",()=>{
assert.match(funnel,/NOT COMPUTABLE/);
assert.match(funnel,/not a purchase/);
});
test("single authoritative confirmed signup is defined",()=>{
assert.match(funnel,/confirmed_signup/);
assert.match(funnel,/provider subscription transition/);
assert.match(funnel,/deduplicated/);
});
test("commercial slots remain held",()=>{
assert.match(funnel,/HOLD_MERCHANT/);
assert.match(funnel,/HOLD_UNSENT/);
});
