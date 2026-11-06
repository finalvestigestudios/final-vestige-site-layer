/* Mind R155 independent source/safety contract, run: node mind/r155/test_mind_r155.cjs
   Offline. Does not post, deploy, pay, send email or execute analytics. */
'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const read=f=>fs.readFileSync(path.join(__dirname,f),'utf8');
const originals={article:read('thatcher-face-inversion-investigation.md'),guide:read('total-focus-exact-offer-buyer-guide.md'),html:read('mind-thatcher-focus-bridge-REVIEW-ONLY.html'),matrix:read('claim-source-authorization-matrix.json'),plan:read('revenue-creator-and-ab-acceptance.md')};
const audit=(d)=>{
 let errors=[],m;const ck=(v,label)=>{if(!v)errors.push(label)};
 try{m=JSON.parse(d.matrix)}catch{return ['unparseable claims matrix']}
 const btn=d.html.match(/<button\b[^>]*>/i);
 ck(Boolean(btn&&/\sdisabled(?:\s|>|=)/i.test(btn[0])),'physical disabled button');
 ck(/data-commercial-approved="false"/.test(d.html),'partner false');
 ck(/data-release="HARD_HOLD"/.test(d.html),'release hold');
 ck(d.html.indexOf('class="disclosure"')>=0 && d.html.indexOf('class="disclosure"')<d.html.indexOf('<button'),'disclosure before CTA');
 ck(/If you purchase through a future authorized link, Final Vestige may earn a commission/.test(d.html),'plain earning disclosure');
 ck(/href="https:\/\/finalvestige\.com\/focus\/"/.test(d.html),'existing Focus CTA');
 ck(!/<form\b|<script\b|<iframe\b/i.test(d.html),'no forms/scripts/iframes');
 ck(!/<video\b[^>]*autoplay/i.test(d.html),'no autoplay');
 ck(!/href="[^"]*(?:affiliates\.inspire3|affiliate_id|\/track\?|\/click\?)/i.test(d.html),'no affiliate earning URL');
 ck(!/<a[^>]*(?:buy|checkout|purchase)[^>]*href=/i.test(d.html),'no active buy anchor');
 ck(/:focus-visible/.test(d.html)&&/prefers-reduced-motion/.test(d.html),'accessibility CSS');
 ck(/max-width:690px/.test(d.html),'responsive breakpoint');
 ck(/data-video-status="STORYBOARD_ONLY"/.test(d.html),'video not playable');
 ck(d.article.split(/\s+/).length>=1800,'article original depth');
 ck(d.article.includes('https://doi.org/10.1068/p090483'),'1980 original');
 ck(d.article.includes('https://doi.org/10.1068/p3174'),'angle study');
 ck(d.article.includes('https://doi.org/10.1080/02724980244000774'),'four experiments');
 ck(d.article.includes('https://doi.org/10.1068/p7755'),'expressions study');
 ck(d.article.includes('no affiliate earning link'),'separate editorial boundary');
 ck(d.guide.includes('33 minutes')&&d.guide.includes('47 MB'),'exact SKU');
 ck(d.guide.includes('not a checkout-verified final price'),'price limitation');
 ck(d.guide.includes('HARD HOLD'),'authorization hold in guide');
 ck(d.plan.includes('merchant_confirmed_purchase')&&d.plan.includes('affiliate_commission_settled'),'events distinct');
 ck(d.plan.includes('REAL_GROK_ASSET_ID'),'no fake IDs');
 ck(d.plan.includes('NOT COMPUTABLE'),'missing denominator clear');
 ck(d.plan.includes('360/390/768/1440/1920'),'device QA');
 ck(d.plan.includes('text-only source guide (A)'),'AB preserved');
 ck(m.claims.length>=25&&m.claims.every(x=>/^https:\/\//.test(x.source)),'claims cited');
 ck(m.release_gates.length>=30&&m.release_gates.every(x=>x.status==='CLOSED'),'all release gates closed');
 ck(m.eligible_for_publication===false&&m.eligible_for_affiliate_activation===false,'release boolean false');
 ck(m.net_revenue_per_1000_qualified_sessions===null&&m.paid_attributable_orders===null,'unverified revenue null');
 ck(m.claims.some(x=>x.disposition==='REJECT_SELLER_CLAIM'),'seller promotion rejected');
 ck(m.claims.some(x=>x.disposition==='UNKNOWN_HARD_HOLD'),'account approval not claimed');
 return errors;
};
assert.deepEqual(audit(originals),[],'committed exact-source audit');
const trials=[
["enable merchant",x=>x.html=x.html.replace(/<button type="button" disabled/,'<button type="button"')],
["approve merchant",x=>x.html=x.html.replace('data-commercial-approved="false"','data-commercial-approved="true"')],
["mark release live",x=>x.html=x.html.replace('data-release="HARD_HOLD"','data-release="LIVE"')],
["erase disclosure",x=>x.html=x.html.replace('class="disclosure"','class="omitted"')],
["remove disclosure meaning",x=>x.html=x.html.replace('If you purchase through a future authorized link, Final Vestige may earn a commission','This is a product.')],
["inject tracker",x=>x.html+=' <script src="https://somewhere.test/tracker.js"></script>'],
["inject form",x=>x.html+=' <form><input type="email"></form>'],
["activate earning URL",x=>x.html+=' <a href="https://affiliates.inspire3.com/track?affiliate_id=FAKE">buy</a>'],
["drop Focus",x=>x.html=x.html.replace('href="https://finalvestige.com/focus/"','href="#"')],
["delete source",x=>x.article=x.article.replace('https://doi.org/10.1068/p090483','no-source')],
["delete price caution",x=>x.guide=x.guide.replace('not a checkout-verified final price','guaranteed final price')],
["invent paid order",x=>{let q=JSON.parse(x.matrix);q.paid_attributable_orders=1;x.matrix=JSON.stringify(q)}],
["open rights gates",x=>{let q=JSON.parse(x.matrix);q.release_gates[0].status='OPEN';x.matrix=JSON.stringify(q)}],
["claim activation",x=>{let q=JSON.parse(x.matrix);q.eligible_for_affiliate_activation=true;x.matrix=JSON.stringify(q)}],
["fake media ID",x=>x.plan=x.plan.replace('REAL_GROK_ASSET_ID','NOT_A_REAL_ID')],
["remove settled commission",x=>x.plan=x.plan.replace('affiliate_commission_settled','click')],
["erase mobile breakpoint",x=>x.html=x.html.replace('max-width:690px','max-width:250px')],
["erase motion",x=>x.html=x.html.replace('prefers-reduced-motion','prefers-default-motion')]
];
let caught=0;for(const [name,mutate] of trials){let x={...originals};mutate(x);let errs=audit(x);assert(errs.length>0,'mutation missed: '+name);caught++;}
console.log('PASS: exact-source compliance contract; '+caught+'/'+trials.length+' adversarial mutations rejected; '+Object.keys(originals).length+' source files; '+JSON.parse(originals.matrix).claims.length+' sourced decisions; '+JSON.parse(originals.matrix).release_gates.length+' closed gates');
