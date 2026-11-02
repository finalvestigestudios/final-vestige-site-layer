import test from "node:test";import assert from "node:assert/strict";import fs from "node:fs";import path from "node:path";
const root=path.dirname(new URL(import.meta.url).pathname);
const load=(n)=>fs.readFileSync(path.join(root,n),"utf8");
const A=load("zen12-a-text.blocks.html"),B=load("zen12-b-film.blocks.html"),core=load("guide-core.html"),C=JSON.parse(load("claim-matrix.json"));
for(const [n,s] of [["A",A],["B",B]]){
 test(n+" true disabled offer CTA",()=>assert.match(s,/<button[^>]*\sdisabled(?:\s|>)/));
 test(n+" near link disclosure",()=>assert.ok(s.indexOf("Affiliate disclosure:")>0&&s.indexOf("Affiliate disclosure:")<s.indexOf("<button")));
 test(n+" no active merchant URL",()=>assert.doesNotMatch(s,/<a\s[^>]*href=["']https?:\/\/(?:www\.)?(zen12|inspire3|hypnosislive)\.com/i));
 test(n+" no executable embeds",()=>assert.doesNotMatch(s,/<(script|iframe|form|video|audio)\b/i));
 test(n+" no autoplay",()=>assert.doesNotMatch(s,/<\w+[^>]*\sautoplay(?:[\s=>])/i));
 test(n+" accessible guide heading",()=>assert.match(s,/<h1 id="fv-r72-title">/));
 test(n+" checkout no real price",()=>assert.doesNotMatch(s,/\$\s*\d/));
 test(n+" one existing focus path",()=>assert.match(s,/https:\/\/finalvestige\.com\/focus\//));
 test(n+" seller evidence boundaries",()=>assert.match(s,/not independently substantiated/i));
}
test("A and B exact substantive guide",()=>assert.ok(A.includes(core)&&B.includes(core)));
test("film accessible transcript without JS",()=>assert.ok(B.includes("<details>")&&B.includes("00:35–00:40")&&B.includes("No video is hosted")));
test("A contains no promotional film",()=>assert.ok(!A.includes("fv-r72-film")));
test("caption cues 6",()=>assert.equal((load("captions.vtt").match(/\d\d:\d\d:\d\d\.\d\d\d -->/g)||[]).length,6));
test("matrix 25+ decisions",()=>assert.ok(C.decisions.length>=25));
test("matrix exact seller URL",()=>assert.ok(C.sources.some(x=>x.url==="https://zen12.com/hnp")));
test("matrix rejected hour-equivalence",()=>assert.ok(C.decisions.some(x=>/same benefits as one hour/.test(x.claim)&&x.status.startsWith("REJECT"))));
test("attribution hard-off",()=>assert.match(load("attribution.mjs"),/export const ENABLED = false/));
test("no new email lists",()=>assert.ok(!A.includes("<form")&&!B.includes("<form")));
test("separate investigation",()=>assert.ok(!load("investigation.md").includes("If you purchase through this link")));
test("B no remote video player",()=>assert.doesNotMatch(B,/player\.vimeo|youtube\.com\/embed/i));
