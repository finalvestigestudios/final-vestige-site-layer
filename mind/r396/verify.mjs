// R396 no-dependency, fail-closed source verifier. Run: node mind/r396/verify.mjs
import {readFileSync} from "node:fs";
import {fileURLToPath} from "node:url";
import {dirname,join} from "node:path";
const dir=dirname(fileURLToPath(import.meta.url));
const load=f=>readFileSync(join(dir,f),"utf8");
const A=load("ZEN12_A.html"),B=load("ZEN12_B_OPTIONAL_FILM.html"),M=JSON.parse(load("CLAIM_RIGHTS_MATRIX.json")),V=load("GORILLA_42S.vtt"),H=load("MIND_HUB_SOURCE.html"),R=load("THE_GORILLA_IN_THE_READING_ROOM.md");
let count=0;function check(cond,msg){count++;if(!cond)throw Error("FAIL "+msg);}
for(const [label,h] of [["A",A],["B",B]]){
 check(h.includes('lang="en"'),label+" lang");
 check(h.includes('name="viewport"'),label+" responsive");
 check(h.includes('href="#main"'),label+" skip link");
 check(h.includes('prefers-reduced-motion'),label+" motion");
 check(h.includes('focus-visible'),label+" keyboard focus");
 check(h.includes('disabled aria-disabled="true"'),label+" disabled purchase");
 check(h.includes("may earn a commission at no additional cost to you"),label+" disclosure");
 check(h.indexOf("may earn a commission")<h.indexOf('class="disabled"'),label+" disclosure before CTA");
 check(!/href=["']https?:\\/\\/(?:www\\.)?(?:zen12\\.com|inspire3\\.com|affiliates\\.inspire3\\.com|hypnosislive\\.com|brainwaveshots\\.com)/i.test(h),label+" merchant href prohibited");
 check(!/autoplay|<script|<form|<iframe/i.test(h),label+" no autoplay/script/form/iframe");
 check(h.includes("https://finalvestige.com/focus/"),label+" one existing free funnel");
}
const normalize=s=>s.replace(/<section class="panel" aria-labelledby="film-title">[\\s\\S]*?<\\/section>/,"");
check(normalize(A)===normalize(B),"A/B exact nonvideo copy");
check(!A.includes("film-title")&&B.includes("film-title"),"film only B");
check((V.match(/ --> /g)||[]).length===6,"six subtitle cues");
check(V.includes("00:00:42.000"),"42-second end");
check(M.release_gates.every(x=>x.state==="HOLD"),"all gates closed");
check(M.claims.find(x=>x.id==="C13")?.classification==="unverified","publisher approval unknown");
check(M.claims.find(x=>x.id==="C22")?.classification==="unverified","paid revenue unknown");
check(M.sources.some(x=>x.url.includes("ftc.gov")),"FTC sources");
check(!/<script|<form|autoplay/i.test(H),"hub static");
check(R.includes("10.1068/p281059")&&R.includes("10.1177/0956797613479386"),"primary DOI");
check(R.includes("not a documented archival incident"),"constructed story labeling");
console.log("PASS "+count+" local static assertions; no browser, native WP, merchant or lead tests implied.");