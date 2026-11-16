#!/usr/bin/env node
// R419 source-only audit. Node builtin modules, no external dependency or network.
"use strict";
const fs=require("node:fs"),path=require("node:path"),assert=require("node:assert/strict");
const root=__dirname;
const read=n=>fs.readFileSync(path.join(root,n),"utf8");
const A=read("ZEN12_A_TEXT_ONLY.html"),B=read("ZEN12_B_OPTIONAL_FILM_CONCEPT.html");
const H=read("MIND_ARCHIVE_WP_SOURCE_DRAFT.html"),T=read("THE_BEAT_IS_NOT_THE_BENEFIT.md"),V=read("ZEN12_FILM_STORYBOARD.vtt");
const M=JSON.parse(read("CLAIM_SOURCE_PERMISSION_MATRIX.json"));
let pass=0;
function check(label,fn){try{fn();pass++;process.stdout.write("PASS "+label+"\n")}catch(e){process.stderr.write("FAIL "+label+": "+e.message+"\n");process.exitCode=1}}
const buyerBody=s=>{const x=s.match(/<main\s+class="shell"\s+id="main">[\s\S]*?<\/main>/);assert(x,"main absent");return x[0]};
const merchantLink=/<a\b[^>]*\bhref\s*=\s*["']https?:\/\/(?:www\.)?(?:zen12|inspire3|hypnosislive|brainwaveshots)\.com/i;
const safe=s=>{assert(!merchantLink.test(s),"merchant checkout anchor");assert(!/<script\b/i.test(s),"script");assert(!/<iframe\b/i.test(s),"iframe");assert(!/<form\b/i.test(s),"additional signup");assert(!/<input\b/i.test(s),"PII control");assert(!/<video\b/i.test(s),"unproduced media player");assert(!/\bautoplay\s*(?:=|>)/i.test(s),"autoplay");assert(!/\$\s*\d/.test(s),"unverified price");assert(/<button\s+disabled\s+type="button"/.test(s),"merchant CTA enabled");assert(s.indexOf("Potential affiliate disclosure:")>0&&s.indexOf("Potential affiliate disclosure:")<s.indexOf("Official offer link unavailable"),"proximate disclosure");};
check("buyer main content parity",()=>assert.equal(buyerBody(A),buyerBody(B)));
check("A no film",()=>assert(!A.includes("<svg")));
check("B original poster SVG",()=>assert(B.includes("<svg")&&B.includes("original concept")));
for(const [n,s] of [["A",A],["B",B],["Hub",H]]){
check(n+" no external script",()=>assert(!/<script\b/i.test(s)));
check(n+" no additional form",()=>assert(!/<form\b/i.test(s)));
check(n+" no active merchant links",()=>assert(!merchantLink.test(s)));
check(n+" responsive viewport",()=>assert(s.includes('name="viewport"')));
check(n+" noindex review",()=>assert(s.includes('name="robots" content="noindex,nofollow"')));
}
for(const [n,s] of [["A",A],["B",B]]){
check(n+" release fails closed",()=>safe(s));
check(n+" independent study URLs",()=>assert(s.includes("PMC10198548")&&s.includes("PMC11799511")));
check(n+" editorial link remains free",()=>assert(s.includes("https://finalvestige.com/focus/")));
check(n+" product efficacy explicitly denied",()=>assert(/seller assertions, not findings/i.test(s)));
check(n+" focus button hard disabled",()=>assert(/<button disabled type="button"/.test(s)));
}
check("hub 4 editorial streams",()=>assert.equal((H.match(/class="tile"/g)||[]).length,4));
check("hub genuine published routes",()=>assert(H.includes("/blog/")&&H.includes("/mesmerism/")&&H.includes("/change-blindness/")));
check("matrix 28 items",()=>assert.equal(M.claims.length,28));
check("matrix 19 cited source URLs",()=>assert.equal(Object.keys(M.sources).length,19));
check("matrix source ID integrity",()=>M.claims.forEach(x=>assert(M.sources[x.source_id],"source missing "+x.id)));
check("matrix 28 closed gates",()=>assert.equal(M.release_gates.filter(x=>x.status==="HOLD").length,28));
check("matrix revenue absent not invented",()=>assert.equal(M.reported_net_revenue_per_1000_qualified_sessions,null));
check("matrix purchase URL null",()=>assert.equal(M.merchant_cta,null));
check("investigation cites 2023 + 2025 research",()=>assert(T.includes("PMC10198548")&&T.includes("PMC11799511")));
check("film cues exactly 6",()=>assert.equal((V.match(/\d\d:\d\d\.000 --> \d\d:\d\d\.000/g)||[]).length,6));
check("film cue timeline contiguous 42 seconds",()=>{let m=[...V.matchAll(/(\d\d):(\d\d)\.000 --> (\d\d):(\d\d)\.000/g)];assert.equal(m.length,6);let prev=0;m.forEach(x=>{let start=+x[1]*60 + +x[2],end=+x[3]*60 + +x[4];assert.equal(start,prev);assert(end>start);prev=end});assert.equal(prev,42)});
const unsafe=[["new merchant anchor",s=>s+'<a href="https://zen12.com/order">buy</a>'],["new signup",s=>s+"<form action='x'></form>"],["JS injection",s=>s+"<script>alert(1)</script>"],["foreign video player",s=>s+"<iframe></iframe>"],["fake price",s=>s+"<p>$19</p>"],["remove disclosure",s=>s.replace("Potential affiliate disclosure:","Missing label")],["enable button",s=>s.replace('<button disabled type="button"','<button type="button"')],["autoplay",s=>s+"<video autoplay></video>"]];
for(const [n,mutate] of unsafe)check("negative mutation caught: "+n,()=>assert.throws(()=>safe(mutate(A))));
process.stdout.write(pass+" source assertions completed. This is NOT browser, CI, media, WordPress, merchant, or live funnel QA.\n");
if(process.exitCode)process.exit(process.exitCode);
