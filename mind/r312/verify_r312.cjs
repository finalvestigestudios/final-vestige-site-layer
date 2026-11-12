#!/usr/bin/env node
"use strict";
// R312 reproducible, deliberately scoped SOURCE guard. Not browser, WP or payment certification.
const fs = require("node:fs");
const path = require("node:path");
const dir = __dirname;
const fn = {
 article:"THE-LETTER-THAT-ARRIVED-WHILE-ATTENTION-WAS-BUSY-UNPUBLISHED.md",
 A:"ZEN12-A-TEXT-BUYER-PILOT-REVIEW-ONLY.html",
 B:"ZEN12-B-OPTIONAL-42S-FILM-PILOT-REVIEW-ONLY.html",
 hub:"MIND-ARCHIVE-FOUR-STREAM-WP-HTML-REVIEW-ONLY.html",
 captions:"ORIGINAL-42-SECOND-STORYBOARD-CAPTIONS.vtt",
 matrix:"ATTENTIONAL-BLINK-ZEN12-SOURCE-CLAIM-AUTHORIZATION.json",
 plan:"ONE-OFFER-REAL-REVENUE-EXPERIMENT-AND-RELEASE-GATES.md"
};
const original=Object.fromEntries(Object.entries(fn).map(([k,v])=>[k,fs.readFileSync(path.join(dir,v),"utf8")]));
function assert(ok,message){if(!ok)throw Error(message)}
function test(v){
 const m=JSON.parse(v.matrix);
 assert(m.sources.length===18,"sources count");
 assert(m.claims.length===30,"claims count");
 assert(m.gates.length===18 && m.gates.every(g=>g.status==="HARD_HOLD"),"all commercial holds");
 assert(m.creator_to_offer.length===3 && m.creator_to_offer.every(c=>c.existing_creator_asset_id===null),"creator assets unverified");
 assert(m.measurement.current_kpi_state==="NOT_COMPUTABLE","KPI cannot be fabricated");
 assert(m.published_state.cms_write===false && m.published_state.merchant_url_active===false &&
  m.published_state.merge===false && m.published_state.additional_jetpack_form===false,"release inactive");
 for(const k of ["A","B","hub"]){
  const s=v[k];
  assert(/^<!doctype html>/i.test(s),"HTML doctype "+k);
  assert(/<html lang="en"/i.test(s),"document language "+k);
  assert((s.match(/<h1\b/gi)||[]).length===1,"one h1 "+k);
  assert(/<meta name="viewport"/i.test(s),"responsive viewport "+k);
  assert(/@media\(max-width:430px\)/i.test(s),"mobile CSS "+k);
  assert(/prefers-reduced-motion/i.test(s),"reduced motion "+k);
  assert(/focus-visible/i.test(s),"keyboard focus "+k);
  assert(/<button type="button" disabled\b/i.test(s),"native disabled button "+k);
  assert(!/<script\b|<iframe\b|<form\b|<input\b|<video\b|<audio\b/i.test(s),"no new active widget/scripts/forms "+k);
  assert(!/\bautoplay(?=\s|>|=)|document\.cookie|localStorage|fetch\s*\(|gtag\s*\(|fbq\s*\(/i.test(s),"no autostart or tracking "+k);
  assert(!/href=["']https?:\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|hypnosislive\.com|brainwaveshots\.com|affiliates\.inspire3\.com)\b/i.test(s),"no active merchant link "+k);
  assert(!/href=["'](?:javascript:|data:)/i.test(s),"unsafe URL "+k);
  assert(/commission at no additional cost/i.test(s),"proximate commission disclosure "+k);
  assert(/not (?:yet )?verified|not yet verified|not active|approval pending|outstanding/i.test(s),"commercial limits "+k);
  assert(!/guaranteed (?:focus|concentration|health|result)|proven to (?:cure|fix|treat)|\$[1-9][\d,]*/i.test(s),"unsupported efficacy / price "+k);
  const pos=s.indexOf("<button type=\"button\" disabled");
  const disclosure=s.indexOf("commission at no additional cost",pos);
  assert(pos>=0 && disclosure>pos && disclosure-pos<900,"near button FTC disclosure "+k);
 }
 assert(!/<section aria-labelledby="film-heading" class="panel film">/i.test(v.A),"A text only");
 assert(/<section aria-labelledby="film-heading" class="panel film">/i.test(v.B),"B original film");
 function normalize(s){return s.replace(/<section aria-labelledby="film-heading" class="panel film">[\s\S]*?<\/section>/,"").replace(/Variant [AB]/g,"Variant X")}
 assert(normalize(v.A)===normalize(v.B),"A/B equivalent exact buyer copy aside from optional film");
 assert(/00:00:00\.000 --> 00:00:07\.000/.test(v.captions) &&
 /00:00:33\.000 --> 00:00:42\.000/.test(v.captions),"full 42s WebVTT timing");
 assert(/WEBVTT/.test(v.captions),"caption format");
 assert(/Ninety-eight/.test(v.article) && /twenty-nine/i.test(v.article)===false && /leaving \*\*29\*\*/.test(v.article),"original participant denominators");
 assert(/0\.75 in the control condition versus 0\.33/.test(v.article),"experiment 1 correct lag2");
 assert(/0\.77 versus 0\.28/.test(v.article),"experiment 2 correct lag2");
 assert(/1992 paper's indexed abstract/.test(v.article),"reading depth");
 assert(/does not prove about meditation audio/i.test(v.article),"science/commerce boundary");
 assert(/NOT COMPUTABLE/.test(v.plan),"unknown revenue denominator");
 assert(/affiliate_click/.test(v.plan) && /merchant_confirmed_paid_order/.test(v.plan),"distinct merchant/outbound events");
 assert(/Grok.*Praxxis/.test(v.plan),"creator ownership");
 return true;
}
test(original);
const cases=[
 ["A disabled control removed",s=>s.A=s.A.replace('<button type="button" disabled','<button type="button"')],
 ["B disabled control removed",s=>s.B=s.B.replace('<button type="button" disabled','<button type="button"')],
 ["Hub disabled control removed",s=>s.hub=s.hub.replace('<button type="button" disabled','<button type="button"')],
 ["ARIA-only disabled fake",s=>s.A=s.A.replace('<button type="button" disabled','<button type="button" aria-disabled="true"')],
 ["Merchant checkout A",s=>s.A=s.A.replace('</body>','<a href="https://zen12.com/getstarted">buy</a></body>')],
 ["Merchant checkout B",s=>s.B=s.B.replace('</body>','<a href="https://affiliates.inspire3.com/">buy</a></body>')],
 ["Merchant link hub",s=>s.hub=s.hub.replace('</body>','<a href="https://hypnosislive.com/mental-skills/total-focus">buy</a></body>')],
 ["Active form A",s=>s.A=s.A.replace('</body>','<form></form></body>')],
 ["Tracking script B",s=>s.B=s.B.replace('</body>','<script src="https://analytics.example"></script></body>')],
 ["Embedded iframe",s=>s.B=s.B.replace('</body>','<iframe src="https://player.example"></iframe></body>')],
 ["Autoplay film",s=>s.B=s.B.replace('</body>','<video autoplay></video></body>')],
 ["JavaScript URL",s=>s.A=s.A.replace('</body>',"<a href='javascript:alert(1)'>open</a></body>")],
 ["Guaranteed focus",s=>s.A=s.A.replace('</body>','guaranteed focus</body>')],
 ["Fake discounted price",s=>s.B=s.B.replace('</body>','Buy for $87.99</body>')],
 ["Remove A disclosure",s=>s.A=s.A.replace('commission at no additional cost','income')],
 ["Remove B disclosure",s=>s.B=s.B.replace('commission at no additional cost','income')],
 ["Move hub disclosure far",s=>s.hub=s.hub.replace('commission at no additional cost','income')],
 ["Modify one buyer variant",s=>s.A=s.A.replace('twelve-minute routine','nine-minute routine')],
 ["Remove film treatment",s=>s.B=s.B.replace('class="panel film"','class="panel box"')],
 ["Erase VTT finish",s=>s.captions=s.captions.replace('00:00:33.000 --> 00:00:42.000','00:00:33.000 --> 00:00:40.000')],
 ["Corrupt VTT",s=>s.captions=s.captions.replace("WEBVTT","CAPTION")],
 ["Forged affiliate acceptance",s=>s.matrix=s.matrix.replace('"status": "HARD_HOLD"','"status": "APPROVED"')],
 ["Forged all asset IDs",s=>s.matrix=s.matrix.replace('"existing_creator_asset_id": null','"existing_creator_asset_id": "fake_123"')],
 ["False computable KPI",s=>s.matrix=s.matrix.replace('"current_kpi_state": "NOT_COMPUTABLE"','"current_kpi_state": "REVENUE_VERIFIED"')],
 ["False merchant activation",s=>s.matrix=s.matrix.replace('"merchant_url_active": false','"merchant_url_active": true')],
 ["Unjustified source count",s=>s.matrix=JSON.stringify({...JSON.parse(s.matrix),sources:JSON.parse(s.matrix).sources.slice(1)})],
 ["New subscription form claimed",s=>s.matrix=s.matrix.replace('"additional_jetpack_form": false','"additional_jetpack_form": true')],
 ["Wrong experimental denominator",s=>s.article=s.article.replace('**29**','**30**')],
 ["Wrong condition number",s=>s.article=s.article.replace('0.75 in the control condition versus 0.33','0.95 in the control condition versus 0.33')],
 ["False original paper inspection",s=>s.article=s.article.replace("1992 paper's indexed abstract","1992 paper fully personally inspected")],
 ["Delete science/commerce boundary",s=>s.article=s.article.replace('What this does not prove about meditation audio','What the experiment proves about Zen12')],
 ["Erase net metric caveat",s=>s.plan=s.plan.replace('NOT COMPUTABLE','REVENUE VERIFIED')],
 ["Lose commission event taxonomy",s=>s.plan=s.plan.replace('merchant_confirmed_paid_order','affiliate_click')],
 ["Lose mobile support",s=>s.hub=s.hub.replace('@media(max-width:430px)','@media(max-width:500px)')],
 ["Lose keyboard indication",s=>s.B=s.B.replaceAll('focus-visible','no-focus')],
 ["Lose reduced motion",s=>s.A=s.A.replaceAll('prefers-reduced-motion','prefers-full-motion')]
];
let pass=0,fail=[];for(const [name,mutation] of cases){const copy={...original};mutation(copy);try{test(copy);fail.push(name)}catch{pass++}}
if(fail.length){console.error("FAILED to reject",fail);process.exitCode=1}
console.log(JSON.stringify({baseline:"PASS",negative_mutations_rejected:pass,total_negative_mutations:cases.length,escaped:fail,scope:"native Node source guard only; no browser/CMS/merchant claims"}));
