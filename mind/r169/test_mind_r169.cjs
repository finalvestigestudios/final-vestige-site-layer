/* Mind R169 – REPRODUCIBLE SOURCE-ONLY safety/claims/revenue guard.
 * Run from repository root: node mind/r169/test_mind_r169.cjs
 * Exact source QA only. NOT a browser, paid checkout, CI, affiliate acceptance or a released site.
 */
'use strict';
const fs=require('node:fs');
const path=require('node:path');
const files={
 article:'white-bear-thought-suppression-investigation-UNPUBLISHED.md',
 buyer:'zen12-white-bear-buyer-bridge-UNPUBLISHED.html',
 hub:'mind-archive-four-stream-conversion-hub-UNPUBLISHED.html',
 matrix:'zen12-exact-offer-claims-and-closed-release-gates.json',
 plan:'creator-offer-ab-test-and-net-revenue-acceptance.md'
};
let assertions=0,mutations=0;
const load=()=>Object.fromEntries(Object.entries(files).map(([k,f])=>[k,fs.readFileSync(path.join(__dirname,f),'utf8')]));
function check(condition,message){assertions++;if(!condition)throw Error('R169 compliance failure '+assertions+': '+message)}
function has(s,re,msg){check(re.test(s),msg)}
function lacks(s,re,msg){check(!re.test(s),msg)}
function validate(d){
 const m=JSON.parse(d.matrix), a=d.article, b=d.buyer, h=d.hub, p=d.plan;
 check(m.status==='DRAFT_ONLY_HARD_HOLD','commercial hard hold');
 check(m.sources.length===17&&m.claims.length===26&&m.gates.length===36,'fixed evidence inventory');
 check(m.gates.every(x=>x.status==='CLOSED'&&x.evidence===null),'all commercial/release gates closed');
 check(m.authorization.affiliate_approved===null,'no invented acceptance');
 check(m.authorization.affiliate_url===null,'no authorized URL yet');
 check(m.authorization.allowed_channels===null&&m.authorization.partner_terms===null,'permissions unknown');
 check(m.product.product_specific_efficacy_independently_verified===false,'no efficacy transfer');
 check(m.product.final_checkout_price_usd===null&&m.product.refund_fulfilled===null,'no invented checkout/refunds');
 check(m.owned_alternative.payhip_mind_sku===null&&m.owned_alternative.rights_verified===null,'no fake SKU');
 check(m.revenue.verified_affiliate_commissions_paid_usd===null,'no fabricated commission');
 check(m.revenue.verified_owned_product_orders===null&&m.revenue.qualified_human_sessions===null,'unknown numerator/denominator');
 check(m.revenue.net_revenue_per_1000_qualified_human_sessions===null,'KPI NOT COMPUTABLE');
 check(m.product.package_seller_describes.mp3_files===48&&m.product.package_seller_describes.levels===12,'seller exact package');
 check(m.claims.some(x=>x.id==='P07'&&x.status==='UNSUPPORTED_PRODUCT_EFFICACY'),'12min equals 1hr NOT adopted');
 check(m.claims.some(x=>x.id==='P24'&&x.status==='UNKNOWN'),'unknown Grok asset ids');
 check(m.sources.some(x=>x.url==='https://zen12.com/')&&m.sources.some(x=>x.url.includes('ftc.gov')),'source provenance');
 has(a,/Paradoxical Effects of Thought Suppression/,'primary research title');
 has(a,/pubmed\.ncbi\.nlm\.nih\.gov\/3612492/,'primary paper permanent record');
 has(a,/five-minute|5-min|five minutes/,'experiment duration');
 has(a,/distract|substitut/i,'distracter nuance');
 has(a,/Puységur|Puys[eé]gur/,'historical archive bridge');
 has(a,/not proof|does not prove|cannot establish|does not establish/i,'epistemic limits');
 has(a,/https:\/\/finalvestige\.com\/focus\//,'existing Focus route in article');
 lacks(a,/\<a\s+[^>]*href=["']https?:\/\/(?:zen12|inspire3|affiliates\.inspire3)/i,'no merchant in research article');
 has(b,/<meta name="robots" content="noindex,nofollow"/,'noindex draft buyer');
 has(h,/<meta name="robots" content="noindex,nofollow"/,'noindex draft hub');
 has(b,/<html lang="en">/,'document language');
 has(b,/href="#main"/,'skip to main');
 has(b,/<main id="main">/,'main landmark');
 has(b,/prefers-reduced-motion:reduce/,'reduce motion CSS');
 has(b,/a:focus-visible/,'focus indicators');
 has(b,/<button[^>]*\bdisabled\b[^>]*>Zen12 Premium purchase link/,'native disabled CTA');
 has(b,/Affiliate disclosure:[\s\S]{0,300}may earn a commission at no additional cost to you/,'near-link material connection disclosure');
 has(b,/https:\/\/finalvestige\.com\/focus\//,'one existing Focus CTA');
 has(b,/42-second/,'optional 42 second video concept');
 has(b,/00–08:[\s\S]*36–42:/,'timed 42s transcript');
 has(b,/not a playable video|No autoplay/i,'no produced/autoplay claims');
 has(b,/<svg[\s\S]*?aria-labelledby="arttitle artdesc"/,'accessible original illustration');
 lacks(b,/<video\b|<audio\b|<iframe\b|<script\b/i,'no media/network/scripts in draft');
 lacks(h,/<video\b|<audio\b|<iframe\b|<script\b/i,'no scripts/embeds in hub');
 lacks(b,/<form\b|<input\b/i,'no duplicated subscriber forms');
 lacks(h,/<form\b|<input\b/i,'no duplicated hub forms');
 lacks(b,/<a\b[^>]*href=["'](?:https?:)?\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|affiliates\.inspire3\.com)/i,'no seller/partner clickable URL');
 lacks(h,/<a\b[^>]*href=["'](?:https?:)?\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|affiliates\.inspire3\.com)/i,'no seller link on hub');
 lacks(b,/<a[^>]*href=[^>]*(?:awin1|clickbank|partner=|affiliate=|aff_id=)/i,'no injected earning link');
 lacks(b,/<button[^>]*>\s*(?:Buy|Purchase|Get Started)\b/i,'no enabled buy control');
 has(h,/Perception & Attention/,'hub stream 1');
 has(h,/History of Suggestion/,'hub stream 2');
 has(h,/Practice & Reflection/,'hub stream 3');
 has(h,/Tools Under Review/,'hub stream 4');
 has(h,/UNPUBLISHED PAGE CONCEPT/,'hub separate from PR172');
 has(h,/No second email form/,'single Jetpack path');
 check(h.includes('https://finalvestige.com/focus/'),'live focus route in hub');
 has(p,/NOT COMPUTABLE/,'no synthetic zero');
 has(p,/merchant \*retail order value\* never becomes FV affiliate revenue|Merchant \*retail order value\* never becomes FV affiliate revenue/,'affiliate revenue definition');
 has(p,/confirmed_signup[\s\S]*affiliate_outbound[\s\S]*merchant_confirmed_paid_order[\s\S]*affiliate_commission_settled/,'event hierarchy');
 has(p,/qualified human sessions/i,'correct denominator');
 has(p,/7\/30/,'two cohorts');
 has(p,/A \/ control:[\s\S]*B \/ treatment:/,'A-B controlled hypothesis');
 has(p,/TASK-008/,'Grok coordination');
 lacks(p,/source=internal_pii|collect.*email address.*analytics/i,'no PII directives');
 return assertions;
}
const original=load();validate(original);
const probes=[
 ['buyer','<button type="button" class="dead" disabled aria-disabled="true">','<button type="button" class="dead">'],
 ['buyer','Zen12 Premium purchase link — unavailable pending approval','Purchase Zen12 now'],
 ['buyer','Affiliate disclosure:','Commercial note:'],
 ['buyer','If this guide eventually contains an authorized purchasing link and you purchase through it, Final Vestige may earn a commission at no additional cost to you.','No commission disclosure required'],
 ['buyer','https://finalvestige.com/focus/','https://example.com/not-focus/'],
 ['buyer','<meta name="robots" content="noindex,nofollow">','<meta name="robots" content="index,follow">'],
 ['buyer','<html lang="en">','<html>'],
 ['buyer','<main id="main">','<div id="main">'],
 ['buyer','prefers-reduced-motion:reduce','motion-enabled:all'],
 ['buyer','a:focus-visible','a:visited'],
 ['buyer','42-second','38-second'],
 ['buyer','36–42:','36–46:'],
 ['buyer','<svg viewBox="0 0 560 390" role="img" aria-labelledby="arttitle artdesc">','<svg viewBox="0 0 560 390">'],
 ['hub','History of Suggestion','Miracle of Suggestion'],
 ['hub','No second email form','A new email form'],
 ['hub','UNPUBLISHED PAGE CONCEPT','A live launch'],
 ['hub','https://finalvestige.com/focus/','https://example.com/join/'],
 ['article','https://pubmed.ncbi.nlm.nih.gov/3612492/','https://example.com/bogus-source'],
 ['article','https://finalvestige.com/focus/','https://example.com/new-list'],
 ['plan','NOT COMPUTABLE','Revenue is zero'],
 ['plan','affiliate_commission_settled','affiliate_click_is_paid'],
 ['plan','TASK-008','TASK-010'],
 ['plan','A / control:','A / unrelated:'],
 ['plan','B / treatment:','B / unrelated:'],
 ['matrix','"affiliate_approved": null','"affiliate_approved": true'],
 ['matrix','"affiliate_url": null','"affiliate_url": "https://example.com/fake-affiliate"'],
 ['matrix','"mp3_files": 48','"mp3_files": 24'],
 ['matrix','"verified_affiliate_commissions_paid_usd": null','"verified_affiliate_commissions_paid_usd": 5000'],
 ['matrix','"qualified_human_sessions": null','"qualified_human_sessions": 5000'],
 ['matrix','"payhip_mind_sku": null','"payhip_mind_sku": "MADEUP1"'],
 ['matrix','"final_checkout_price_usd": null','"final_checkout_price_usd": 37'],
 ['matrix','"status": "CLOSED"','"status": "OPEN"']
];
for(const [key,find,replacement] of probes){
 if(!original[key].includes(find))throw Error('Bad R169 mutation setup '+key+': '+find);
 const changed={...original,[key]:original[key].replaceAll(find,replacement)};
 try{validate(changed);throw Error('UNDTECTED unsafe mutation '+key+': '+find)}
 catch(e){if(e.message.startsWith('UNDTECTED'))throw e;mutations++}
}
const injection=[
 ['buyer','<script src="https://example.com/pixel.js"></script>'],
 ['buyer','<iframe src="https://example.com/embed"></iframe>'],
 ['buyer','<form><input type="email"></form>'],
 ['buyer','<a href="https://zen12.com/">Buy here</a>'],
 ['buyer','<a href="https://affiliates.inspire3.com/">Join</a>'],
 ['buyer','<a href="https://inspire3.com/">Seller link</a>'],
 ['hub','<a href="https://zen12.com/">Click to buy</a>']
];
for(const [key,txt] of injection){
 const changed={...original,[key]:original[key].replace('</main>',txt+'</main>')};
 try{validate(changed);throw Error('UNDTECTED injected unsafe markup '+txt)}
 catch(e){if(e.message.startsWith('UNDTECTED'))throw e;mutations++}
}
console.log('R169 SOURCE-ONLY PASS: '+assertions+' aggregate assertions including '+mutations+' detected unsafe mutation/injection probes. Native browser, checkout, WP/Jetpack live, CI, video and sales remain UNTESTED.');
