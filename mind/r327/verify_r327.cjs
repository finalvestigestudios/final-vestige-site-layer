#!/usr/bin/env node
"use strict";
/* Offline source-level checks only; not native WP / browser / merchant certification. */
const fs=require("node:fs"),path=require("node:path"),assert=require("node:assert/strict");
const F={article:"THE-CHOICE-YOU-NEVER-MADE-UNPUBLISHED.md",a:"ZEN12-A-TEXT-REVIEW-ONLY.html",b:"ZEN12-B-OPTIONAL-42S-REVIEW-ONLY.html",hub:"MIND-FOUR-STREAM-UNPUBLISHED-HUB-REVIEW.html",vtt:"ORIGINAL-42S-CAPTIONS.vtt",matrix:"PRODUCT-CLAIM-SOURCE-AUTHORIZATION-MATRIX.json",dossier:"OFFER-FUNNEL-QA-ATTRIBUTION-RELEASE-DOSSIER.md"};
const load=()=>Object.fromEntries(Object.entries(F).map(([k,f])=>[k,fs.readFileSync(path.join(__dirname,f),"utf8")]));
const film=/<section id="optional-42s-film"[\s\S]*?<\/section>/;
function check(f){let errs=[],m;let test=(v,n)=>{if(!v)errs.push(n)};
try{m=JSON.parse(f.matrix)}catch(e){return ["matrix-json"]}
const sources=new Set(m.sources.map(x=>x.id));
test(m.release_state==="UNPUBLISHED_HARD_HOLD","held");
test(m.sources.length>=20&&m.sources.every(x=>/^https:\/\//.test(x.url)),"sources");
test(m.claims.length>=35&&m.claims.every(x=>x.source_ids.length&&x.source_ids.every(id=>sources.has(id))),"claims");
test(m.authorization_gates.length===18&&m.authorization_gates.every(x=>x.status==="HARD_HOLD"&&x.activation===false),"gates");
test(m.offers[0].publisher_eligible===null&&m.offers[0].affiliate_url===null,"partner-unknown");
test(m.creator_topic_to_product_fit.length===3&&m.creator_topic_to_product_fit.every(x=>x.asset_id===null&&x.media_url===null),"creator-ids-not-invented");
test(m.measurement.value===null&&m.measurement.zero_equals_unknown===false,"net-unknown");
test(f.article.includes("135 of 206")&&f.article.includes("65.5%")&&f.article.includes("computerized"),"covert-denominator");
test(/2014/.test(f.article)&&/2005/.test(f.article)&&/2025/.test(f.article),"research");
for(const key of ["a","b"]){let h=f[key];
test(/<html lang="en">/.test(h)&&/href="#main"/.test(h),"accessible-shell-"+key);
test((h.match(/<h1>/g)||[]).length===1,"h1-"+key);
test(/<button[^>]*disabled aria-disabled="true"/.test(h),"inert-commerce-"+key);
test(/Prospective affiliate disclosure:/.test(h)&&h.indexOf("Prospective affiliate disclosure:")>h.indexOf('disabled aria-disabled="true"')&&h.indexOf("Prospective affiliate disclosure:")-h.indexOf('disabled aria-disabled="true"')<310,"proximate-disclosure-"+key);
test(!/<a[^>]+href=["'][^"']*(zen12\.com|inspire3\.com|brainwaveshots\.com|hypnosislive\.com)/i.test(h),"no-merchant-anchor-"+key);
test(!/<script\b|<iframe\b|<form\b|<video\b|\sautoplay(?:\s|=|>)|\son\w+\s*=/i.test(h),"no-tracking-autoplay-form-"+key);
test((h.match(/href="https:\/\/finalvestige.com\/focus\/"/g)||[]).length===1,"single-focus-"+key);
}
test(f.b.replace(film,"")===f.a&&film.test(f.b)&&!film.test(f.a),"ab-content-parity");
test(/<details>/.test(f.b)&&/aria-labelledby="p-title p-desc"/.test(f.b),"optional-art-transcript");
test((f.vtt.match(/-->/g)||[]).length===6&&/00:00:42\.000/.test(f.vtt),"caption-42s");
test(["perception","history","practice","tools"].every(id=>f.hub.includes('id="'+id+'"')),"four-streams");
test(!/<script\b|<form\b|<iframe\b/.test(f.hub),"hub-no-new-stack");
test(/NOT COMPUTABLE/.test(f.dossier)&&/refund/.test(f.dossier),"revenue-evidence");
return errs;
}
let files=load(),errs=check(files);assert.deepEqual(errs,[],"Unsafe baseline: "+errs.join(", "));
let mutants=[
["enable",f=>f.a=f.a.replace('disabled aria-disabled="true"',"")],
["no-disclosure-a",f=>f.a=f.a.replace("Prospective affiliate disclosure:","")],
["no-disclosure-b",f=>f.b=f.b.replace("Prospective affiliate disclosure:","")],
["merchant-link-a",f=>f.a=f.a.replace("</main>",'<a href="https://zen12.com/getstarted">Buy</a></main>')],
["merchant-link-b",f=>f.b=f.b.replace("</main>",'<a href="https://inspire3.com/">Buy</a></main>')],
["script",f=>f.a=f.a.replace("</body>","<script>bad()</script></body>")],
["iframe",f=>f.b=f.b.replace("</body>","<iframe></iframe></body>")],
["form",f=>f.a=f.a.replace("</body>","<form></form></body>")],
["autoplay",f=>f.b=f.b.replace("</body>","<video autoplay></video></body>")],
["onerror",f=>f.a=f.a.replace("<main",'<img onerror="bad()"><main')],
["focus-duplicate",f=>f.a=f.a.replace("</main>",'<a href="https://finalvestige.com/focus/">again</a></main>')],
["skip",f=>f.a=f.a.replace('href="#main"','href="#else"')],
["lang",f=>f.b=f.b.replace('lang="en"','lang=""')],
["h1",f=>f.b=f.b.replace("<h1>","<h2>")],
["remove-film",f=>f.b=f.b.replace(film,"")],
["alter-buyer-copy",f=>f.b=f.b.replace("Its refund guarantee is seller-advertised","Its refund guarantee is absolutely proven")],
["remove-last-caption",f=>f.vtt=f.vtt.replace(/00:00:35\.000 --> 00:00:42\.000[\s\S]*/,"")],
["caption-end",f=>f.vtt=f.vtt.replace("00:00:42.000","00:00:49.000")],
["denominator",f=>f.article=f.article.replace("135 of 206","135 of 300")],
["year",f=>f.article=f.article.replace(/2025/g,"unknown")],
["source-http",f=>{let j=JSON.parse(f.matrix);j.sources[0].url="http://example.com";f.matrix=JSON.stringify(j)}],
["claim-orphan",f=>{let j=JSON.parse(f.matrix);j.claims[0].source_ids=["UNKNOWN"];f.matrix=JSON.stringify(j)}],
["open-gate",f=>{let j=JSON.parse(f.matrix);j.authorization_gates[0].activation=true;f.matrix=JSON.stringify(j)}],
["fewer-gates",f=>{let j=JSON.parse(f.matrix);j.authorization_gates.pop();f.matrix=JSON.stringify(j)}],
["fake-asset",f=>{let j=JSON.parse(f.matrix);j.creator_topic_to_product_fit[0].asset_id="FAKE";f.matrix=JSON.stringify(j)}],
["affiliate-url",f=>{let j=JSON.parse(f.matrix);j.offers[0].affiliate_url="https://example.com";f.matrix=JSON.stringify(j)}],
["assumed-approval",f=>{let j=JSON.parse(f.matrix);j.offers[0].publisher_eligible=true;f.matrix=JSON.stringify(j)}],
["net-zero",f=>{let j=JSON.parse(f.matrix);j.measurement.value=0;f.matrix=JSON.stringify(j)}],
["remove-hub-stream",f=>f.hub=f.hub.replace('id="history"','id="missing"')],
["hub-form",f=>f.hub=f.hub.replace("</main>","<form></form></main>")]
];
for(const [name,modify] of mutants){let copy={...files};modify(copy);assert(check(copy).length,"Unsafe change accepted: "+name)}
console.log(JSON.stringify({status:"PASS",baseline:"source-level",unsafe_mutations_rejected:mutants.length,files:Object.keys(F),limit:"Not WCAG/browser/WordPress/merchant proof"}));
module.exports={check};
