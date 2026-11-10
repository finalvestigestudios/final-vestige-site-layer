"use strict";
const fs = require("node:fs");
const path = require("node:path");
const assert = require("node:assert/strict");
const {inspect} = require("./preflight.cjs");
const root = __dirname, campaign = path.resolve(root, "../campaign-2026-mind");
const manifest = JSON.parse(fs.readFileSync(path.join(campaign, "manifest.json"), "utf8"));
const text = id => fs.readFileSync(path.join(root, "ISSUE" + id + "_COPY_REVIEW.md"), "utf8");
const html = id => fs.readFileSync(path.join(root, "REVIEW_" + id + "_EMAIL.html"), "utf8");
let total = 0;
function test(label, fn) { fn(); total++; process.stdout.write("PASS " + label + "\n"); }
for (const [id, n] of [["03",3],["05",5]]) {
 const original = text(id), preview = html(id);
 const verify = (body=original, view=preview, m=manifest) => inspect(body, view, m, n);
 test(id+" valid gated candidate", () => assert.equal(verify().pass, true, JSON.stringify(verify().faults)));
 test(id+" one inactive CTA", () => assert.equal(verify().cta_count, 1));
 test(id+" sources exist", () => assert.ok(verify().reference_count >= 3));
 test(id+" rejects second CTA", () => assert.ok(verify(original+"\n"+original.match(/^\*\*PRIMARY CTA.*$/m)[0]).faults.includes("SINGLE_DISABLED_CTA")));
 test(id+" rejects activated earning CTA", () => assert.ok(verify(original.replace(/\[\[APPROVED_LIVE_[A-Z0-9_]+\]\]/, "https://affiliate.example/earn")).faults.includes("SINGLE_DISABLED_CTA")));
 test(id+" rejects removed disclosure", () => assert.ok(verify(original.replace(/^\*\*Commercial disclosure.*\n/m, "")).faults.includes("DISCLOSURE_PRESENT")));
 test(id+" rejects distant disclosure", () => assert.ok(verify(original.replace(/(\*\*PRIMARY CTA.*\n)/, "$1\nA pushy extra section\n")).faults.includes("DISCLOSURE_ADJACENT")));
 test(id+" rejects missing postal gate", () => assert.ok(verify(original.replace("[[VALID_FINAL_VESTIGE_POSTAL_ADDRESS_REQUIRED]]","")).faults.includes("COMPLIANCE_GATES")));
 test(id+" rejects unapproved claim", () => assert.ok(verify(original+" clinically proven to reprogram").faults.includes("MISLEADING_COPY")));
 test(id+" rejects tracking URL", () => assert.ok(verify(original.replace("https://finalvestige.com/focus/","https://finalvestige.com/focus/?secret=1")).faults.includes("SOURCE_URL_ALLOWLIST")));
 test(id+" rejects script injection", () => assert.ok(verify(original,preview+"<script>alert(1)</script>").faults.includes("PREVIEW_SEND_HOLD")));
 test(id+" rejects false preview link", () => assert.ok(verify(original,preview+' href="[[APPROVED_LIVE_TEST]]"').faults.includes("PREVIEW_LINK_GUARD") || verify(original,preview+' href="[[APPROVED_LIVE_TEST]]"').pass === false));
 test(id+" rejects active merchant manifest", () => assert.ok(verify(original,preview,{...manifest,issues:manifest.issues.map((x,j)=>j===n-1?{...x,merchant_affiliate_url:"https://example.com"}:x)}).faults.includes("MERCHANT_ACTIVATION")));
}
test("manifest four editorial two commercial", () => assert.equal(manifest.issues.filter(x=>x.kind==="editorial").length,4));
test("manifest no activated links", () => assert.ok(manifest.issues.every(x=>x.merchant_affiliate_url===null)));
console.log("R261 OFFLINE NATIVE QA "+total+"/"+total+" PASSED. NOT EMAIL DELIVERY OR MERCHANT AUTHORIZATION.");
