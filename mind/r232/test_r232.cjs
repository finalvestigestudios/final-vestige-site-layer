"use strict";
/* R232 reproducible node-only source acceptance. Run: node mind/r232/test_r232.cjs
   Source-only: NOT a live WP/browser/merchant accessibility, checkout, or conversion test. */
const fs=require("node:fs"),path=require("node:path"),assert=require("node:assert/strict");
const dir=__dirname;
const names={a:"zen12-r232-A-TEXT-UNPUBLISHED.html",b:"zen12-r232-B-OPTIONAL-42S-STORYBOARD-UNRENDERED.html",hub:"mind-four-stream-WORDPRESS-SOURCE-PREVIEW-UNPUBLISHED.html",vtt:"zen12-r232-42s-proposed-captions.vtt",matrix:"SELLER-CLAIM-PROOF-AND-COMMERCE-GATES.json",article:"TWELVE-MINUTES-IS-NOT-AN-HOUR-UNPUBLISHED.md",plan:"CONVERSION-ELIGIBILITY-CREATOR-AB-ACCEPTANCE.md"};
const read=()=>Object.fromEntries(Object.entries(names).map(([k,v])=>[k,fs.readFileSync(path.join(dir,v),"utf8")]));
function guard(f){
 const issues=[],bad=(x)=>issues.push(x); let m;
 try{m=JSON.parse(f.matrix)}catch(e){bad("bad json");return issues}
 if(m.affiliate_activation!=="HARD_HOLD"||m.shop_authorization!=="UNVERIFIED")bad("affiliate authorization drift");
 const urls=m.sources.map(x=>x.url),sourceIds=m.sources.map(x=>x.id);
 if(new Set(sourceIds).size!==sourceIds.length||sourceIds.length<19||!sourceIds.includes("AFFPORTAL")||!sourceIds.includes("FTC_HEALTH"))bad("source set");
 if(m.claims.length!==30||new Set(m.claims.map(c=>c.id)).size!==30)bad("claim set");
 if(m.gates.length!==16||m.gates.some(g=>g.status!=="HARD_HOLD"))bad("release gates");
 for(const c of m.claims){if(!c.evidence?.length||c.evidence.some(id=>!sourceIds.includes(id)))bad("claim evidence "+c.id)}
 const expected={"C04":"unsupported_product_specific_equivalence_do_not_assert","C05":"unsupported_product_specific_claim_do_not_assert","C20":"false_public_registration_not_acceptance","C21":"not_verified_hold","C22":"false_requires_jetpack_evidence","C23":"false_requires_merchant_transaction","C24":"not_computable_missing_denominator_numerator"};
 for(const [id,status] of Object.entries(expected))if(m.claims.find(c=>c.id===id)?.status!==status)bad("critical claim "+id);
 for(const [name,html] of [["a",f.a],["b",f.b],["hub",f.hub]]){
  if(!/^<!doctype html>/i.test(html)||!/<html lang="en">/i.test(html)||!/<meta name="viewport"/.test(html)||!/<main\b/.test(html))bad(name+" basic HTML");
  if(/<\s*(?:script|iframe|form|object|embed|video|audio|plaintext|xmp|noembed|noscript)\b/i.test(html))bad(name+" forbidden active/opaque tag");
  if(/\son[a-z]+\s*=/i.test(html)||/javascript:|data:text\/html|srcdoc\s*=/i.test(html))bad(name+" active content");
  if(/<a\b[^>]*href=["'][^"']*(?:zen12\.com|inspire3\.com|brainwaveshots\.com|hypnosislive\.com|payhip\.com)/i.test(html))bad(name+" unapproved merchant click");
  if(/<form\b/i.test(html)||/googletagmanager|google-analytics|facebook\.com\/tr\?/.test(html))bad(name+" new tracking or signup");
  if(!/href="https:\/\/finalvestige\.com\/focus\/"/.test(html))bad(name+" missing single existing Focus route");
 }
 for(const name of ["a","b"]){
  const html=f[name];if(!/<button[^>]*\sdisabled\b[^>]*>Zen12 offer/.test(html))bad(name+" enabled offer");
  if(!/Affiliate disclosure: If a future approved purchase link/.test(html))bad(name+" adjacent disclosure");
  const start=html.indexOf("Affiliate disclosure:"),btn=html.indexOf("<button class=\"disabled\"");
  if(start<0||btn<0||btn-start>330||start>btn)bad(name+" disclosure placement");
  if(!/No affiliate link is active on this page/.test(html))bad(name+" pending state");
 }
 const main=(s)=>s.slice(s.indexOf('<main class="wrap" id="content">'),s.indexOf('<footer class="wrap">'));
 if(main(f.a)!==main(f.b))bad("A/B text differs");
 if(/id="optional-film"/.test(f.a)||!/id="optional-film"/.test(f.b))bad("film not B-only");
 if(!/<details>/.test(f.b)||!/<svg/.test(f.b)||!/<desc/.test(f.b)||!/<ol>/.test(f.b)||!/video not rendered/i.test(f.b))bad("B storyboard accessibility");
 if(!/^WEBVTT\s/.test(f.vtt)||[...f.vtt.matchAll(/--> /g)].length!==5||!/00:00:42\.000/.test(f.vtt))bad("captions");
 if(f.article.split(/\s+/).length<2000||!/JAMA|2025/.test(f.article)||!/Puys[eé]gur/.test(f.article))bad("investigation depth");
 if(!/net revenue/i.test(f.plan)||!/HARD HOLD/i.test(f.plan)||!/asset_id/.test(f.plan))bad("conversion plan");
 if(!m.sources.some(s=>s.id==="ZEN12"&&s.url==="https://zen12.com/hnp"))bad("actual seller offer");
 if(urls.some(x=>!/^https:\/\//.test(x)))bad("unqualified evidence URLs");
 return issues;
}
const files=read();assert.deepEqual(guard(files),[],"baseline unsafe");
let checks=0;
const mutate=(key,replacer,label)=>{const f={...files,[key]:replacer(files[key])};const issues=guard(f);assert(issues.length>0,"escaped guard: "+label);checks++};
mutate("a",s=>s.replace('class="disabled" disabled','class="disabled"'),"enabled A");
mutate("b",s=>s.replace('class="disabled" disabled','class="disabled"'),"enabled B");
mutate("a",s=>s.replace('Affiliate disclosure: If a future approved purchase link','Optional disclaimer: If a future approved purchase link'),"disclosure");
mutate("b",s=>s.replace('No affiliate link is active on this page.','Buy now, offer live.'),"false status");
mutate("hub",s=>s.replace('</main>','<form action="/new-list"></form></main>'),"new list");
mutate("hub",s=>s.replace('</main>','<script>alert(1)</script></main>'),"JS");
mutate("a",s=>s.replace('</main>','<a href="https://zen12.com/hnp">Shop</a></main>'),"merchant href");
mutate("b",s=>s.replace('</main>','<a onclick="alert(1)" href="/focus/">Click</a></main>'),"event handler");
mutate("b",s=>s.replace('<details>','<div>'),"storyboard");
mutate("b",s=>s.replace('id="optional-film"','id="optional-banner"'),"film B");
mutate("a",s=>s.replace('The enticing part of the promise','Buy it immediately'),"unequal offer");
mutate("vtt",s=>s.replace('00:00:42.000','00:00:30.000'),"timing");
mutate("matrix",s=>s.replace('"HARD_HOLD"','"AUTHORIZED"'),"release gate");
mutate("matrix",s=>s.replace('"not_verified_hold"','"verified_approved"'),"fabricated partner");
mutate("matrix",s=>s.replace('"false_requires_jetpack_evidence"','"confirmed_lead"'),"faked subscriber");
mutate("matrix",s=>s.replace('"false_requires_merchant_transaction"','"paid_sale"'),"faked sale");
mutate("matrix",s=>s.replace('"false_public_registration_not_acceptance"','"approved"'),"public portal confusion");
mutate("matrix",s=>s.replace('"not_computable_missing_denominator_numerator"','"zero_revenue"'),"missing attribution");
mutate("matrix",s=>s.replace('https://zen12.com/hnp','http://invalid.example'),"seller source");
mutate("article",s=>s.slice(0,200),"article depth");
mutate("plan",s=>s.replace('HARD HOLD','unblocked').replace(/net revenue/ig,'page views').replace(/asset_id/g,'unverified'),"revenue plan");
console.log("R232 SOURCE-ONLY PASS: baseline 0 violations; "+checks+"/"+checks+" adversarial test cases rejected. NOT native browser, WP, CI, checkout, or paid transactions.");
