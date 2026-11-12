"use strict";
const fs=require("node:fs"),path=require("node:path"),assert=require("node:assert/strict");
const rd=n=>fs.readFileSync(path.join(__dirname,n),"utf8");
const A=rd("ZEN12-A-TEXT-REVIEW.html"),B=rd("ZEN12-B-OPTIONAL-FILM-REVIEW.html"),H=rd("MIND-HUB-WP-REVIEW.html"),V=rd("ORIGINAL-42S-CAPTIONS.vtt"),M=JSON.parse(rd("CLAIM-SOURCE-COMMERCE-GATES.json"));
let n=0;
function pass(label,fn){fn();console.log("PASS",label);n++;}
function secure(html){assert(!/<script\b|<iframe\b|<form\b|on(?:click|load|error)\s*=/i.test(html));assert(html.includes('type="button" disabled'));assert(html.includes('id="affiliate-disclosure"'));assert(html.includes("https://finalvestige.com/focus/"));assert(html.includes("noindex,nofollow"));assert(html.includes("prefers-reduced-motion"))}
pass("A inactive and safe",()=>secure(A));pass("B inactive and safe",()=>secure(B));
pass("exact buyer text equivalent",()=>assert.equal(A,B.replace(/<aside class="film"[\s\S]*?<\/aside>/,"")));
pass("caption length, six segments",()=>{assert(V.startsWith("WEBVTT"));assert.equal((V.match(/-->/g)||[]).length,6);assert(V.includes("00:00:42.000"))});
pass("B illustration and transcript, no video",()=>{assert(B.includes('role="img"'));assert(B.includes("<details>"));assert(!/<video\b|<audio\b/i.test(B))});
pass("all claim references grounded",()=>{const ids=new Set(M.sources.map(s=>s.id));M.claims.forEach(c=>assert(ids.has(c.source)))});
pass("18 commercial gates held",()=>{assert.equal(M.authorization.length,18);assert(M.authorization.every(g=>g.status==="HARD_HOLD"))});
pass("hub four streams",()=>["Perception &amp; Attention","History of Suggestion","Practice &amp; Reflection","Tools Under Review"].forEach(s=>assert(H.includes(s))));
for(const [label,modified] of [["script",A+"<script>x</script>"],["extra form",A+"<form></form>"],["enabled CTA",A.replace('type="button" disabled','type="button"')],["missing disclosure",A.replace('id="affiliate-disclosure"','id="hidden"')],["wrong free destination",A.replace('https://finalvestige.com/focus/','https://example.invalid/focus/')]]){assert.throws(()=>secure(modified));n++;console.log("PASS reject",label)}
console.log(n+" isolated source checks passed; native Node execution only if actually invoked.");
