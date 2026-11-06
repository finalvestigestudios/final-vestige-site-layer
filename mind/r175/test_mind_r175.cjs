/* Mind R175 reproducible source and unsafe-mutation checks. Node >=18.
   Run: node mind/r175/test_mind_r175.cjs
   Static source assertions only; not a browser, seller approval, or verified sale. */
'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=process.env.MIND_R175_ROOT||process.cwd();
const paths={article:'the-pendulum-was-moving-INVESTIGATION-UNPUBLISHED.md',guide:'zen12-premium-independent-buyer-UNPUBLISHED.md',offer:'zen12-pendulum-buyer-PREVIEW-UNPUBLISHED.html',hub:'mind-archive-four-stream-PREVIEW-UNPUBLISHED.html',matrix:'product-claims-authorization-gates.json',plan:'offer-creator-to-paid-proof-and-experiment.md'};
const read=()=>Object.fromEntries(Object.entries(paths).map(([key,name])=>[key,fs.readFileSync(path.join(root,'mind/r175',name),'utf8')]));
let assertions=0;
function ck(condition,label){assertions++;assert.ok(condition,label)}
function audit(s){
ck(s.article.split(/\s+/).length>1700,'article must have depth');
for(const term of ['22377138','5858027','Puységur','ideomotor','fifty-seven percent','fifty-three percent','not a product'])ck(s.article.toLowerCase().includes(term.toLowerCase()),'primary evidence '+term);
ck(s.guide.includes('48 MP3')&&s.guide.includes('twelve sequential levels'),'seller features');
ck(s.offer.includes('42-second'),'optional 42-second storyboard');
ck(s.offer.includes('type="button" disabled aria-disabled="true"'),'native disabled merchant CTA');
ck(s.offer.includes('Potential affiliate disclosure')&&s.offer.includes('commission at no additional cost'),'FTC disclosure');
ck(s.offer.indexOf('Potential affiliate disclosure')>s.offer.indexOf('Merchant purchase unavailable'),'disclosure adjacent below button');
ck(s.offer.includes('https://finalvestige.com/focus/')&&s.hub.includes('https://finalvestige.com/focus/'),'existing Focus route');
for(const h of [s.offer,s.hub]){
ck(!/<script\b/i.test(h),'script introduced');
ck(!/<form\b/i.test(h),'extra form');
ck(!/<(?:iframe|video)\b/i.test(h),'third party/playable media falsely included');
ck(!/\b(?:href|src)\s*=\s*["']https?:\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|affiliates\.inspire3\.com|hypnosislive\.com|brainwaveshots\.com)/i.test(h),'merchant outbound link');
ck(!/www\.awin1\.com/i.test(h),'no unauthorized affiliate URL');
ck(h.includes('noindex,nofollow'),'unpublished preview indexing guard');
ck(h.includes('prefers-reduced-motion'),'motion accessibility');
}
const j=JSON.parse(s.matrix);
ck(j.activation===false&&j.affiliate_earning_url===null,'affiliate gate');
ck(j.realized_net_revenue_per_1000_qualified_human_sessions===null,'no invented revenue');
ck(j.release_gates.some(x=>x.status==='CLOSED'&&x.name.includes('Inspire3')),'partner hard hold');
ck(s.plan.includes('affiliate_click')&&s.plan.includes('affiliate_paid_commission'),'click not paid');
ck(s.plan.includes('qualified-human sessions')&&s.plan.includes('NOT COMPUTABLE'),'qualified denominator');
ck(s.plan.includes('not already deducted'),'double deduction avoidance');
}
const source=read();audit(source);const baseline=assertions;let caught=0;
const attacks=[
s=>s.offer=s.offer.replaceAll('type="button" disabled aria-disabled="true"','type="button"'),
s=>s.offer=s.offer.replaceAll('Potential affiliate disclosure','Some information'),
s=>s.offer=s.offer.replaceAll('at no additional cost','plus an extra fee'),
s=>s.offer=s.offer.replaceAll('https://finalvestige.com/focus/','/missing/'),
s=>s.hub=s.hub.replaceAll('https://finalvestige.com/focus/','/missing/'),
s=>s.offer=s.offer.replaceAll('</body>','<script src="https://ad.example/tracker.js"></script></body>'),
s=>s.hub=s.hub.replaceAll('</body>','<form><input type="email"></form></body>'),
s=>s.offer=s.offer.replaceAll('</body>','<a href="https://zen12.com/">Buy</a></body>'),
s=>s.offer=s.offer.replaceAll('</body>','<a href="https://www.awin1.com/x">Buy</a></body>'),
s=>s.offer=s.offer.replaceAll('noindex,nofollow','index,follow'),
s=>s.hub=s.hub.replaceAll('noindex,nofollow','index,follow'),
s=>s.offer=s.offer.replaceAll('prefers-reduced-motion','prefers-motion'),
s=>s.article=s.article.replaceAll('fifty-seven percent','one hundred percent'),
s=>s.article=s.article.replaceAll('fifty-three percent','zero percent'),
s=>s.article=s.article.replaceAll('22377138','false-link'),
s=>s.article=s.article.replaceAll('Puységur','not-present'),
s=>s.guide=s.guide.replaceAll('48 MP3','40 MP3'),
s=>s.matrix=s.matrix.replaceAll('"activation": false','"activation": true'),
s=>s.matrix=s.matrix.replaceAll('"affiliate_earning_url": null','"affiliate_earning_url": "https://unapproved.example/"'),
s=>s.matrix=s.matrix.replaceAll('"realized_net_revenue_per_1000_qualified_human_sessions": null','"realized_net_revenue_per_1000_qualified_human_sessions": 1200'),
s=>s.plan=s.plan.replaceAll('affiliate_paid_commission','click_only'),
s=>s.plan=s.plan.replaceAll('qualified-human sessions','unqualified_views'),
s=>s.plan=s.plan.replaceAll('not already deducted','always deducted twice'),
s=>s.offer=s.offer.replaceAll('42-second','65-second'),
s=>s.offer=s.offer.replaceAll('type="button" disabled aria-disabled="true"','type="submit" aria-disabled="true"'),
s=>s.hub=s.hub.replaceAll('</body>','<iframe src="https://example.com"></iframe></body>')
];
for(let i=0;i<attacks.length;i++){const altered={...source};attacks[i](altered);try{audit(altered)}catch(e){caught++;continue}throw Error('unsafe mutation survived '+i)}
assert.equal(caught,attacks.length);
console.log('R175 PASS: '+baseline+' baseline source checks; '+caught+'/'+attacks.length+' unsafe mutation probes detected. Browser/merchant/CI not tested.');