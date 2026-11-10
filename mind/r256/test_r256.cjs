/* FV Mind R256: reproducible fail-closed source checks.
 * Run native: node mind/r256/test_r256.cjs .  No network, no accounts, no user data.
 * The test reads only the five authored R256 artifacts, never production pages.
 * Browser/WP/commerce behavior MUST be checked separately.
 */
"use strict";
const BASE="mind/r256/";
const FILENAMES={
 article:"THE-WORD-YOUR-EYES-PUT-IN-YOUR-EARS-UNPUBLISHED.md",
 A:"zen12-price-integrity-A-text-HOLD.html",
 B:"zen12-price-integrity-B-42s-concept-HOLD.html",
 hub:"MIND-ARCHIVE-WORDPRESS-SOURCE-UNPUBLISHED.html",
 matrix:"CLAIM-PROOF-OFFER-DIVERGENCE-AUTHORIZATION.json",
 plan:"OFFER-TO-REVENUE-RELEASE-PLAN.md"
};
const reject=(ok,why)=>{if(!ok)throw Error(why)};
function validate(files){
 const article=files.article,A=files.A,B=files.B,hub=files.hub,raw=files.matrix,plan=files.plan;
 for (const [k,v] of Object.entries(files))reject(typeof v==="string"&&v.length>200,"missing/short "+k);
 const m=JSON.parse(raw);
 reject(m.sources.length>=18&&m.claims.length>=25&&m.gates.length===16,"source/claim/gate register incomplete");
 reject(new Set(m.sources.map(s=>s.id)).size===m.sources.length,"duplicate source IDs");
 reject(new Set(m.claims.map(s=>s.id)).size===m.claims.length,"duplicate claim IDs");
 reject(m.gates.every(g=>g.status==="HARD_HOLD"&&g.evidence===null),"commerce authorization spoofed");
 reject(m.commercial_state.merchant_link_enabled===false&&m.commercial_state.authenticated_partner_approval===false,"merchant link activated");
 reject(m.commercial_state.verified_paid_orders===null&&m.commercial_state.verified_affiliate_commissions===null&&m.commercial_state.net_revenue_per_1000_qualified_human_sessions===null,"invented revenue");
 reject(m.exact_standard_page==="https://zen12.com/hnp"&&m.alternative_page_warning.includes("/secret/"),"price context erased");
 reject(m.claims.some(c=>c.id==="C07"&&c.status==="seller_displays_promo"),"second price context misclassified");
 for(const c of m.claims)reject(m.sources.some(s=>s.id===c.source),"broken citation "+c.id);
 for(const key of ["A","B","hub"]){
  const h=files[key];
  reject(/<!doctype html>/i.test(h)&&/<html lang="en">/.test(h)&&/<meta name="viewport"/.test(h),"html accessibility skeleton "+key);
  reject(!/<script\b|<iframe\b|<form\b|<video\b|<audio\b|<link[^>]*rel=["']stylesheet["']|@import\b|on(?:click|load|error|mouseover|focus)=/i.test(h),"script/form/remote media/event handler found "+key);
  reject(!/<a[^>]*href=["'](?:https?:\/\/)?(?:www\.)?(?:zen12|inspire3|hypnosis-live|brainwaveshots|payhip)[^"']*["']/i.test(h),"merchant anchor enabled "+key);
  reject(/finalvestige\.com\/focus\//.test(h),"existing free Focus route missing "+key);
  reject(!/subscribe now|new mailing list|new newsletter form|mailchimp|convertkit|emailjs|pixel\.facebook|gtag\(/i.test(h),"duplicate email or tracking introduced "+key);
  reject(/prefers-reduced-motion:reduce/.test(h),"reduced motion support missing "+key);
  reject(/a:focus-visible/.test(h),"keyboard outline missing "+key);
 }
 for(const key of ["A","B"]){
  const h=files[key];
  reject(/<button[^>]*\bdisabled\b[^>]*>/.test(h),"commercial control enabled "+key);
  reject((h.match(/<button\b/g)||[]).length===1,"multiple commercial buttons "+key);
  reject(/class="notice"[\s\S]{50,500}<button[^>]*\bdisabled\b/.test(h),"adjacent disclosure missing "+key);
  reject(/may earn a commission/.test(h),"material connection language missing "+key);
  reject(/\$87\.99/.test(h)&&/\$37/.test(h)&&/different sales-page contexts/.test(h),"divergent seller promotion warning missing "+key);
  reject(/noindex,nofollow/.test(h),"unpublished search-index control missing "+key);
  reject(/finalvestige\.com\/focus\//.test(h),"Focus route missing "+key);
  reject(/unverified|not independently/i.test(h),"uncertainty missing "+key);
 }
 const buyerCopy=(h)=>h.slice(h.indexOf('<section class="intro"'),h.lastIndexOf("</main>"));
 reject(buyerCopy(A)===buyerCopy(B),"A/B comparison has non-video content drift");
 reject(!/<details\b/.test(A)&&/<details\b/.test(B),"video concept not isolated in B");
 reject(/Storyboard and captions only/.test(B)&&/NO video has been rendered/.test(B),"film falsely claimed rendered");
 reject(/<svg[^>]*role="img"/.test(B)&&/<title id="poster-title"/.test(B)&&/<desc id="poster-description"/.test(B),"SVG accessible text missing");
 const segments=[...B.matchAll(/<time>(\d{2}):(\d{2})–(\d{2}):(\d{2})<\/time>/g)].map(z=>[Number(z[1])*60+Number(z[2]),Number(z[3])*60+Number(z[4])]);
 reject(segments.length===7&&segments[0][0]===0&&segments.at(-1)[1]===42,"film 7 caption segments/42s timing invalid");
 for(let i=0;i<segments.length;i++)reject(segments[i][1]>segments[i][0]&&(i===0||segments[i][0]===segments[i-1][1]),"caption discontinuity "+i);
 reject(/source-controlled|Source-controlled/i.test(hub)&&/Puységur direct archive destination awaits/.test(hub),"hub archive verification hold removed");
 reject(/<button disabled type="button"/.test(hub)&&/Potential earning-link disclosure/.test(hub),"hub merchant disclosure/control missing");
 reject((article.match(/\b[\w'-]+\b/g)||[]).length>1600,"scientific investigation below substantive threshold");
 reject(/McGurk/.test(article)&&/MacDonald/.test(article)&&/doi\.org\/10\.1038\/264746a0/.test(article),"original paper source missing");
 reject(/Puységur/.test(article)&&/https:\/\/finalvestige\.com\/focus\//.test(article),"history/real funnel bridge missing");
 reject(article.includes("It does **not** demonstrate that binaural beats entrain an individual"),"specific science-to-product inference limit missing");
 reject(/Offer → funnel → blocker → change/.test(plan)&&/NOT_COMPUTABLE/.test(plan)&&/asset_id/.test(plan),"conversion plan incomplete");
 reject(/HARD HOLD/.test(plan)&&/browser/.test(plan)&&/WordPress/.test(plan),"release QA boundary missing");
 return {status:"PASS",sources:m.sources.length,claims:m.claims.length,gates:m.gates.length,film_segments:segments.length,film_seconds:segments.at(-1)[1]};
}
function runMutations(files){
 const cases=[
 ["enabled A button",f=>f.A=f.A.replace('type="button" disabled','type="button"')],
 ["enabled B button",f=>f.B=f.B.replace('type="button" disabled','type="button"')],
 ["remove A disclosure",f=>f.A=f.A.replace('may earn a commission','may get something')],
 ["remove B disclosure",f=>f.B=f.B.replace('may earn a commission','may get something')],
 ["merchant link A",f=>f.A=f.A.replace('<main>','<main><a href="https://zen12.com/hnp">Order</a>')],
 ["merchant link B",f=>f.B=f.B.replace('<main>','<main><a href="https://inspire3.com/offer">Get</a>')],
 ["email form A",f=>f.A=f.A.replace('<main>','<main><form action="/subscribe">')],
 ["tracker B",f=>f.B=f.B.replace('<main>','<main><script src="https://example.com/x.js"></script>')],
 ["inline event hub",f=>f.hub=f.hub.replace('<main>','<main onclick="track()">')],
 ["external video B",f=>f.B=f.B.replace('<main>','<main><iframe src="https://video.example/test"></iframe>')],
 ["alter A body",f=>f.A=f.A.replace('an organized audio library','a premium audio library')],
 ["alter B price",f=>f.B=f.B.replace('$87.99','$97.99')],
 ["erase price warning",f=>f.A=f.A.replace('different sales-page contexts','same guaranteed offer')],
 ["cut B caption",f=>f.B=f.B.replace('<time>00:36–00:42</time>','<time>00:36–00:40</time>')],
 ["shift film time",f=>f.B=f.B.replace('<time>00:06–00:12</time>','<time>00:07–00:12</time>')],
 ["remove B transcript",f=>f.B=f.B.replace(/<ol class="timed">[\s\S]*?<\/ol>/,'')],
 ["remove B SVG description",f=>f.B=f.B.replace(/<desc id="poster-description">[\s\S]*?<\/desc>/,'')],
 ["missing focus hub",f=>f.hub=f.hub.replaceAll('https://finalvestige.com/focus/','https://somewhere.invalid/focus/')],
 ["remove hub Puységur uncertainty",f=>f.hub=f.hub.replace('Puységur direct archive destination awaits','Archive link ready')],
 ["enable hub commerce",f=>f.hub=f.hub.replace('<button disabled','<button')],
 ["matrix approval spoof",f=>{const m=JSON.parse(f.matrix);m.gates[0].status="PASS";f.matrix=JSON.stringify(m)}],
 ["fake paid commissions",f=>{const m=JSON.parse(f.matrix);m.commercial_state.verified_affiliate_commissions=5;f.matrix=JSON.stringify(m)}],
 ["fake paid order",f=>{const m=JSON.parse(f.matrix);m.commercial_state.verified_paid_orders=1;f.matrix=JSON.stringify(m)}],
 ["fake net revenue",f=>{const m=JSON.parse(f.matrix);m.commercial_state.net_revenue_per_1000_qualified_human_sessions=100;f.matrix=JSON.stringify(m)}],
 ["erase alternate offer",f=>{const m=JSON.parse(f.matrix);m.alternative_page_warning="";f.matrix=JSON.stringify(m)}],
 ["demote price classification",f=>{const m=JSON.parse(f.matrix);m.claims.find(c=>c.id==="C07").status="verified_checkout";f.matrix=JSON.stringify(m)}],
 ["remove article source",f=>f.article=f.article.replace('doi.org/10.1038/264746a0','doi.org/unsourced')],
 ["remove article product limit",f=>f.article=f.article.replace('does **not** demonstrate','directly demonstrates')],
 ["remove no-JS A accessible outline",f=>f.A=f.A.replace('a:focus-visible','a:hover')],
 ["remove no-JS hub motion",f=>f.hub=f.hub.replace('prefers-reduced-motion:reduce','prefers-reduced-motion:no-preference')],
 ["remove plan revenue field",f=>f.plan=f.plan.replaceAll('NOT_COMPUTABLE','UNKNOWN')]
 ];
 let rejected=0,ineffective=[];
 for(const [label,mutation] of cases){const f={...files};mutation(f);try{validate(f);ineffective.push(label)}catch(_){rejected++}}
 return {rejected,total:cases.length,ineffective};
}
if(typeof module!=="undefined")module.exports={validate,runMutations,FILENAMES};
if(typeof require!=="undefined"&&require.main===module){
 const fs=require("node:fs"),path=require("node:path"),assert=require("node:assert/strict");
 const dir=__dirname,files={};
 for(const [key,name] of Object.entries(FILENAMES))files[key]=fs.readFileSync(path.join(dir,name),"utf8");
 const ok=validate(files),bad=runMutations(files);
 assert.equal(bad.rejected,bad.total,"Every deliberately unsafe mutation must be rejected: "+bad.ineffective.join(", "));
 console.log(JSON.stringify({baseline:ok,mutation_suite:bad,native_node:true},null,2));
}