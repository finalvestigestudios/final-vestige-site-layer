import fs from "node:fs"; import assert from "node:assert/strict";
const file=n=>fs.readFileSync(new URL(n,import.meta.url),"utf8");
const A=file("ZEN12_A_TEXT_GUIDE.html"), B=file("ZEN12_B_OPTIONAL_FILM_CONCEPT.html"), H=file("MIND_HUB_SOURCE_ONLY.html"), R=file("THE_CHOICE_YOU_DID_NOT_MAKE.md"), C=JSON.parse(file("CLAIM_SOURCE_PERMISSION_MATRIX.json")), V=file("ZEN12_FILM_42S.vtt");
let count=0;function ok(x,m){assert.ok(x,m);count++}
const canon=s=>s.split("<!-- COPY-START -->")[1]?.split("<!-- COPY-END -->")[0];
ok(canon(A) && canon(A)===canon(B),"A/B substantive buyer content identical");
for(const [n,s] of [["A",A],["B",B],["Hub",H]]){ok(s.includes('name="viewport"'),n+" responsive");ok(s.includes('name="robots" content="noindex,nofollow"'),n+" noindex");ok(!/<script\b/i.test(s),n+" no script");ok(!/<iframe\b/i.test(s),n+" no iframe");ok(!/<video\b/i.test(s),n+" no forced video");ok(!/\bautoplay\s*(?:=|>)/i.test(s),n+" no autoplay attribute");ok(!/<form\b/i.test(s),n+" no duplicate signup");}
for(const [n,s] of [["A",A],["B",B]]){ok(s.includes('disabled type="button" aria-disabled="true"'),n+" button");ok(s.includes("Prospective affiliate disclosure"),n+" disclosure");ok(s.indexOf("Prospective affiliate disclosure")<s.indexOf("Offer unavailable"),n+" adjacent disclosure");ok(!/href="https?:\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|hypnosislive\.com|brainwaveshots\.com)/i.test(s),n+" no merchant egress");ok(s.includes("https://finalvestige.com/focus/"),n+" existing Focus only");}
ok(B.includes("<details>")&&B.includes("<summary>"),"optional film only");
ok(B.includes('role="img"')&&B.includes('aria-labelledby="filmt fdesc"'),"poster named");
ok(!A.includes("<details>"),"text variant no film");
ok((V.match(/-->/g)||[]).length===6 && V.includes("00:00:42.000"),"42s 6-cue draft");
ok(R.split(/\s+/).length>=1700,"substantive manuscript");
for(const s of ["10.1126/science.1111709","10.1016/j.cognition.2010.06.010","10.1371/journal.pone.0045457","Puységur","not a validated","HARD HOLD"]){ok(R.toLowerCase().includes(s.toLowerCase()),"source/limit "+s)}
ok(C.sources.length>=16&&C.claims.length>=25,"matrix scope");
ok(C.gates.length===28&&C.gates.every(g=>g.status==="HOLD"),"all 28 gates HOLD");
ok(C.claims.filter(x=>x.status.includes("DO NOT ADOPT")).length>=4,"seller efficacy not adopted");
console.log("PASS "+count+" static-source assertions; browser, CMS, real film, settlement NOT tested");