/* R176 source-level reproducible safety and methodology gates.
 * Node >= 18: node mind/r176/test_mind_r176.cjs
 * No mocked paid results. These checks are NOT real-browser WCAG, a merchant login, CI, or paid conversion.
 */
'use strict';
const fs=require('node:fs');
const path=require('node:path');
const assert=require('node:assert/strict');
const root=process.env.MIND_R176_ROOT||process.cwd();
const dir=path.join(root,'mind/r176');
const fileNames={
 article:'when-the-pendulum-did-not-know-INVESTIGATION-UNPUBLISHED.md',
 previous:'../r175/the-pendulum-was-moving-INVESTIGATION-UNPUBLISHED.md',
 guide:'zen12-twelve-minute-buyer-decision-UNPUBLISHED.md',
 offer:'zen12-12-minute-offer-VIDEO-HYPOTHESIS-UNPUBLISHED.html',
 hub:'mind-archive-integrated-four-stream-UNPUBLISHED.html',
 matrix:'offer-provenance-claims-and-gates.json',
 plan:'creator-to-verified-paid-acceptance.md'
};
const read=()=>Object.fromEntries(Object.entries(fileNames).map(([k,p])=>[k,fs.readFileSync(path.join(dir,p),'utf8')]));
let count=0;
const ck=(a,msg)=>{count++;assert.ok(a,msg)};
function audit(s){
 ck(s.article.trim().split(/\s+/).length>=1900,'R176 original investigation length');
 for(const x of ['2012','2017','2022','Gauchou','Moga','Dienes','Olson','sixty-three','thirty-four','twenty-one','twenty-seven','65%','50%','Puységur','not an exact reproduction'])
   ck(s.article.includes(x),'R176 research distinction missing: '+x);
 for(const x of ['twenty-one','sixty-three','thirty-four','Moga and Zoltan Dienes','2022'])
   ck(s.previous.includes(x),'R175 QA correction missing: '+x);
 for(const x of ['48 downloadable MP3','twelve','$87.99','one-year','we have not','free','Prospective affiliate disclosure','NOT ACTIVE'])
   ck(s.guide.toLowerCase().includes(x.toLowerCase()),'exact-offer guide '+x);
 for(const html of [s.offer,s.hub]){
   ck(/<html lang="en">/.test(html),'html language');
   ck(/name="viewport"/.test(html),'mobile viewport');
   ck(/noindex,nofollow/.test(html),'draft indexing guard');
   ck(/prefers-reduced-motion:reduce/.test(html),'reduced motion support');
   ck(/:focus-visible/.test(html),'keyboard focus style');
   ck(/class="skip"/.test(html),'skip navigation');
   ck(!/<script\b/i.test(html),'scripts forbidden');
   ck(!/<form\b/i.test(html),'duplicate email capture forbidden');
   ck(!/<(?:iframe|video)\b/i.test(html),'no third-party embedded or falsely produced video');
   ck(!/href\s*=\s*["']https?:\/\/(?:www\.)?(?:zen12\.com|affiliates\.inspire3\.com|inspire3\.com|www\.awin1\.com)/i.test(html),'unauthorized merchant links');
   ck(html.includes('https://finalvestige.com/focus/'),'preserve one Focus CTA');
 }
 ck(s.offer.includes('type="button" disabled aria-disabled="true"'),'native disabled purchase control');
 ck(s.offer.includes('Merchant purchase unavailable — approval pending'),'disabled label');
 ck(s.offer.includes('Potential affiliate disclosure:'),'adjacent affiliate notice');
 ck(s.offer.indexOf('Potential affiliate disclosure:')>s.offer.indexOf('Merchant purchase unavailable — approval pending'),'disclosure after purchase control');
 ck(s.offer.indexOf('Potential affiliate disclosure:')-s.offer.indexOf('Merchant purchase unavailable — approval pending')<500,'disclosure reasonably near button');
 ck(s.offer.includes('42-second') && s.offer.includes('00–08s:') && s.offer.includes('29–42s:'),'42-second original transcript');
 ck(s.offer.includes('poster') && s.offer.includes('no autoplay'),'static optional video concept');
 ck(s.offer.includes('rel="noopener noreferrer"'),'source links safe');
 ck(s.hub.includes('four streams') && s.hub.includes('Tools Under Review'),'four-stream archive');
 ck(s.hub.includes('canonical /mind/') && s.hub.includes('PR #172'),'canonical hub protection');
 const j=JSON.parse(s.matrix);
 ck(j.activation===false && j.affiliate_earning_url===null,'partner not activated');
 ck(j.verified_affiliate_approval===false,'no fake partner acceptance');
 ck(j.verified_payhip_mind_sku===null,'no fabricated owned SKU');
 ck(j.realized_net_revenue_per_1000_qualified_human_sessions===null,'no invented revenue KPI');
 ck(j.claims.length>=30 && j.sources.length>=12,'material source claims matrix');
 ck(j.release_gates.some(x=>x.id==='partner_approval' && x.state==='CLOSED'),'partner gate closed');
 ck(j.release_gates.some(x=>x.id==='founder_release' && x.state==='CLOSED'),'release gate closed');
 ck(s.plan.includes('affiliate_click') && s.plan.includes('merchant_confirmed_purchase') && s.plan.includes('affiliate_commission_paid'),'differentiate clicks from paid');
 ck(s.plan.includes('NOT COMPUTABLE') && s.plan.includes('not already deducted'),'no invented or duplicate-deducted money');
 ck(s.plan.includes('actual immutable Grok asset_id') && s.plan.includes('No CMS'),'creator approval boundaries');
}
const original=read();audit(original);const baseline=count;
const mutations=[
s=>s.offer=s.offer.replace('type="button" disabled aria-disabled="true"','type="button" aria-disabled="true"'),
s=>s.offer=s.offer.replace('Merchant purchase unavailable — approval pending','Buy now'),
s=>s.offer=s.offer.replace('Potential affiliate disclosure:','Disclaimer:'),
s=>s.offer=s.offer.replace('at no additional cost to you','with a fee'),
s=>s.offer=s.offer.replace('https://finalvestige.com/focus/','/fake-focus'),
s=>s.hub=s.hub.replace('https://finalvestige.com/focus/','/fake-focus'),
s=>s.offer=s.offer.replace('</body>','<a href="https://zen12.com/">Buy</a></body>'),
s=>s.offer=s.offer.replace('</body>','<a href="https://affiliates.inspire3.com/">Earn</a></body>'),
s=>s.offer=s.offer.replace('</body>','<script src="https://ads.example/pixel.js"></script></body>'),
s=>s.hub=s.hub.replace('</body>','<form><input type="email"></form></body>'),
s=>s.offer=s.offer.replace('noindex,nofollow','index,follow'),
s=>s.hub=s.hub.replace('prefers-reduced-motion:reduce','prefers-full-motion'),
s=>s.offer=s.offer.replace('42-second','90-second'),
s=>s.offer=s.offer.replace('00–08s:','00–50s:'),
s=>s.article=s.article.replace('sixty-three','eighty'),
s=>s.article=s.article.replace('thirty-four','forty'),
s=>s.article=s.article.replace('twenty-one','twenty-seven'),
s=>s.article=s.article.replace('Moga','Fake'),
s=>s.previous=s.previous.replace('Moga and Zoltan Dienes','Unknown study'),
s=>s.previous=s.previous.replace('sixty-three','eighty analyzed'),
s=>s.matrix=s.matrix.replace('"activation": false','"activation": true'),
s=>s.matrix=s.matrix.replace('"affiliate_earning_url": null','"affiliate_earning_url": "https://unapproved.example"'),
s=>s.matrix=s.matrix.replace('"verified_payhip_mind_sku": null','"verified_payhip_mind_sku": "fake"'),
s=>s.matrix=s.matrix.replace('"realized_net_revenue_per_1000_qualified_human_sessions": null','"realized_net_revenue_per_1000_qualified_human_sessions": 999'),
s=>s.plan=s.plan.replace('affiliate_commission_paid','affiliate_click'),
s=>s.plan=s.plan.replace('not already deducted','always deducted twice'),
s=>s.hub=s.hub.replace('PR #172','PR #9999'),
s=>s.offer=s.offer.replace('rel="noopener noreferrer"','rel="sponsored"'),
s=>s.offer=s.offer.replace('</body>','<iframe src="https://player.example"></iframe></body>'),
s=>s.guide=s.guide.replace('48 downloadable MP3','32 MP3')
];
let caught=0;
for(let i=0;i<mutations.length;i++){
 const test={...original};mutations[i](test);
 assert.notDeepEqual(test,original,'mutation must change actual text '+i);
 try{audit(test)}catch(e){caught++;continue}
 throw Error('unsafe mutation survived '+i);
}
assert.equal(caught,mutations.length);
console.log('R176 SOURCE TEST PASS: '+baseline+' baseline assertions, '+caught+'/'+mutations.length+' deliberate unsafe changes detected. No browser/merchant/CI/checkout test.');
