/** R50 offline source-contract tests. Run: node --test commerce-contract.test.mjs */
import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
const read = p => readFileSync(new URL(p,import.meta.url),"utf8");
const a=read("./presell-A-text-only.html"), b=read("./presell-B-optional-film.html");
const core=read("./guide-core.html"), hub=read("./mind-hub-alternative-unpublished.html");
const investigation=read("./investigation.md"), claims=read("./claims-matrix.csv");
const linkToMerchant=/(?:href|src)\s*=\s*["']\s*https?:\/\/(?:[^/"']+\.)?(?:zen12\.com|inspire3\.com)(?:\/|["'])/i;
const realDisabled=/<button\b[^>]*\sdisabled(?:\s|=|>)/i;
function respectsContract(html){
 const disclosure=html.indexOf("If you purchase through a future earning link, Final Vestige may earn a commission");
 const button=html.indexOf('<button type="button" disabled');
 return /data-commerce="HOLD"/.test(html)
 && realDisabled.test(html) && /aria-disabled="true"/.test(html)
 && disclosure >= 0 && button > disclosure && button-disclosure < 700
 && !linkToMerchant.test(html) && !/<(?:script|iframe|form|video)\b/i.test(html)
 && !/\bonclick\s*=/i.test(html) && !/<a\b[^>]+\bhref=["'](?:javascript:|data:)/i.test(html);
}
test("both variants preserve exact substantive buyer guide",()=>{
 assert.ok(a.includes(core));assert.ok(b.includes(core));assert.equal(a.split(core).length,2);assert.equal(b.split(core).length,2);
});
for(const [label,h] of [["A",a],["B",b]])test("source and commerce hold "+label,()=>{
 assert.ok(respectsContract(h));assert.match(h,/<h1\b[^>]*id="fv-zen12-title"/);
 assert.match(h,/prefers-reduced-motion/);assert.match(h,/@media\(max-width:390px\)/);
 assert.match(h,/https:\/\/finalvestige\.com\/focus\//);
});
test("B optional film has no broken playable control",()=>{
 assert.match(b,/<details>/);assert.match(b,/<summary>/);assert.match(b,/static poster—not a play button/);
 assert.doesNotMatch(a,/<details>/);
});
test("investigation independent of commercial recommendation",()=>{
 assert.match(investigation,/The Sound the Mouth Invented/);
 assert.match(investigation,/https:\/\/doi\.org\/10\.1038\/264746a0/);
 assert.doesNotMatch(investigation,/(?:zen12\.com|inspire3\.com|affiliate discount|buy now)/i);
});
test("matrix and canonical hub are present",()=>{
 assert.ok(claims.trim().split("\n").length >= 55);
 assert.match(hub,/PR #172/);assert.doesNotMatch(hub,/<form\b/i);
});
test("mutations cannot silently arm offer",()=>{
 assert.equal(respectsContract(a.replace(/\sdisabled aria-disabled=/," aria-disabled=")),false);
 assert.equal(respectsContract(b.replace("may earn a commission","may have a connection")),false);
 assert.equal(respectsContract(b.replace("Seller visit unavailable — approval pending","<a href='https://zen12.com/getstarted'>Shop</a>")),false);
 assert.equal(respectsContract(a.replace('data-commerce="HOLD"','data-commerce="ON"')),false);
 assert.equal(respectsContract(b.replace("<!-- never here -->","<script src='https://example.com/t.js'></script>").replace("<aside class=\"fv-offer\"","<script src='https://example.com/t.js'></script><aside class=\"fv-offer\"")),false);
});
test("no claims presented as independently tested product",()=>{
 assert.match(core,/We have not independently tested Zen12/);
 assert.match(core,/not product-specific validation/i);
 assert.match(core,/not independently established here/);
});
