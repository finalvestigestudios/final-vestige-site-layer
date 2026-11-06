/* Final Vestige Studios Mind R173 — executable source & mutation test.
   Node 18+: node mind/r173/test_mind_r173.cjs
   Source only: NOT live browser, affiliate acceptance, merchant checkout or paid-sale proof. */
'use strict';
const fs=require('node:fs'),path=require('node:path'),root=process.env.MIND_R173_ROOT||process.cwd();
const paths={
article:'mind/r173/memory-confidence-is-not-accuracy-INVESTIGATION-UNPUBLISHED.md',
guide:'mind/r173/zen12-premium-independent-decision-guide-UNPUBLISHED.md',
offer:'mind/r173/zen12-memory-confidence-PRESELL-UNPUBLISHED.html',
hub:'mind/r173/mind-four-stream-ARCHIVE-UNPUBLISHED.html',
matrix:'mind/r173/zen12-evidence-claim-permission-net-gates.json',
plan:'mind/r173/creator-offer-conversion-attribution-and-acceptance.md',
r172article:'mind/r172/the-skill-that-attention-training-did-not-measure-INVESTIGATION-UNPUBLISHED.md',
r172plan:'mind/r172/one-real-offer-creator-fit-ab-and-reconciled-net-contract.md'
};
const src=Object.fromEntries(Object.entries(paths).map(([k,v])=>[k,fs.readFileSync(path.join(root,v),'utf8')]));
function ensure(ok,message){if(!ok)throw Error(message);}
function contrast(c1,c2){const channel=c=>{c=parseInt(c,16)/255;return c<=.04045?c/12.92:Math.pow((c+.055)/1.055,2.4)};const L=s=>{s=s.replace('#','');return .2126*channel(s.slice(0,2))+.7152*channel(s.slice(2,4))+.0722*channel(s.slice(4,6))};const a=L(c1),b=L(c2);return (Math.max(a,b)+.05)/(Math.min(a,b)+.05)}
function verify(d, verbose=false){
 let n=0;const ok=(p,msg)=>{ensure(p,msg);n++};
 const {article,guide,offer,hub,plan,r172article,r172plan}=d;
 const matrix=JSON.parse(d.matrix);
 ok(article.trim().split(/\s+/).length>=1900,'article is not deeply written');
 ok(article.includes('24 highly suggestible participants'),'research sample omitted');
 ok(article.includes('134 milliseconds'),'reaction time omitted');
 ok(article.includes('AUC 0.961')&&article.includes('0.956'),'accuracy result omitted');
 ok(article.includes('not statistically significant'),'accuracy caveat missing');
 ok(article.includes('49 people with acquired brain injury'),'distinct RCT context missing');
 ok(article.replace(/\*/g,'').includes('not a hypnosis intervention'),'free demo disclaimer missing');
 ok(article.includes('Puységur'),'archive bridge missing');
 ok(article.includes('38569321'),'primary research PMID missing');
 ok(article.includes('health'),'medical claim boundary missing');
 ok(!/we (used|tested|purchased) Zen12/i.test(article),'invented direct-use evidence');
 ok(guide.includes('48 downloadable MP3')&&guide.includes('twelve levels'),'exact SKU feature loss');
 ok(guide.includes('one-year money-back guarantee')||guide.includes('one-year money-back'),'seller guarantee absent');
 ok(guide.includes('not an authenticated checkout')||guide.includes('not a verified final checkout')||guide.includes('not an authenticated checkout quote'),'pricing qualifier absent');
 ok(guide.includes('no checkout link here'),'guide not explicitly commercial hold');
 ok(guide.includes('may earn a commission'),'conditional disclosure absent');
 ok(guide.includes('free Seven Day Focus Fieldbook'),'free alternative absent');
 ok(guide.includes('no product trial')||guide.includes('No purchase or product trial'),'no fake personal product testing');
 ok(offer.includes('<meta name="robots" content="noindex,nofollow">'),'draft index shield absent');
 ok(offer.includes('<meta name="viewport"'),'mobile viewport missing');
 ok(/<a class="skip" href="#main">/i.test(offer),'skip link missing');
 ok(offer.includes('id="main"'),'main skip target missing');
 ok(offer.includes(':focus-visible'),'keyboard focus styling missing');
 ok(offer.includes('prefers-reduced-motion'),'reduced motion missing');
 ok(offer.includes('max-width:800px'),'mobile layout CSS absent');
 ok(/<button[^>]*class="buy"[^>]*\bdisabled\b/i.test(offer),'purchase control not natively disabled');
 ok(!/href\s*=\s*["']https?:\/\/(?:www\.)?(?:zen12|inspire3|affiliates\.inspire3)\.com/i.test(offer),'active merchant or affiliate URL');
 ok(!/<script\b|<iframe\b|<form\b|<video\b|<audio\b/i.test(offer),'new script/embed/form/media introduced');
 ok(!/autoplay\s*(?:=|>)/i.test(offer),'autoplay attr introduced');
 const i=offer.indexOf('<p class="disclosure">'),j=offer.indexOf('<button type="button" class="buy"');
 ok(i>=0&&j>i&&j-i<750,'FTC disclosure not proximate to disabled purchase');
 ok(offer.includes('at no additional cost to you'),'material connection not plainly described');
 ok(offer.includes('No earning link is active now'),'missing nonactivation statement');
 ok(offer.includes('2026')&&offer.includes('$87.99'),'dated price fact absent');
 ok(offer.includes('final checkout quote'),'no checkout disclaimer missing');
 ok(offer.includes('without a measured')||offer.includes('not significantly improve'),'accurate research boundary missing');
 ok(offer.includes('42-second')&&offer.includes('Open storyboard')&&offer.includes('timeline'),'optional storyboard absent');
 ok(offer.includes('No video exists')||offer.includes('no video exists'),'video must not be represented as produced');
 ok(offer.includes('https://finalvestige.com/focus/'),'existing Focus CTA missing');
 ok(contrast('#e5dfd2','#0a0c0c')>=4.5,'body contrast under 4.5');
 ok(contrast('#e3bd7c','#0a0c0c')>=4.5,'link contrast under 4.5');
 ok(hub.includes('The Mind & Perception Archive'),'hub title removed');
 for(const stream of ['Perception & Attention','History of Suggestion','Practice & Reflection','Tools Under Review'])ok(hub.includes(stream),'hub stream missing: '+stream);
 ok(hub.includes('https://finalvestige.com/focus/'),'hub loses Focus');
 ok(hub.includes("canonical Mind hub PR #172")||hub.includes("Canonical Mind hub PR #172"),'canonical PR ownership dropped');
 ok(!/<script\b|<iframe\b|<form\b|<video\b/i.test(hub),'hub gained script/embed/form');
 ok(!/href\s*=\s*["']https?:\/\/(?:www\.)?(?:zen12|inspire3)\.com/i.test(hub),'hub activated merchant route');
 ok(matrix.source_register.length>=13,'insufficient source provenance');
 ok(matrix.claim_decisions.length>=26,'claim matrix shortened');
 ok(matrix.release_gates.length>=36,'release gate matrix shortened');
 ok(matrix.release_gates.every(x=>x.status==='CLOSED'),'commercial/release gate opened');
 ok(matrix.affiliate_url===null&&matrix.authorized_channels===null,'invented affiliate destination or channel rights');
 ok(matrix.approval_evidence_status==='UNKNOWN','approval falsely established');
 ok(matrix.verified_publisher_approval===false,'unverified approval asserted');
 ok(matrix.revenue_status.net_per_thousand===null,'net revenue fabricated');
 ok(matrix.owned_product_fallback.eligible_payhip_mind_sku===null,'owned product invented');
 const accuracy=matrix.claim_decisions.find(x=>x.id==='C11');
 ok(accuracy&&accuracy.decision==='REJECT','accuracy misrepresentation accepted');
 const clinical=matrix.claim_decisions.find(x=>x.id==='C09');
 ok(clinical&&clinical.decision==='DO_NOT_ADOPT_AS_FACT','unverified health efficacy adopted');
 ok(plan.includes('NOT COMPUTABLE')&&plan.includes('Keep negative net negative'),'revenue treatment could hide loss');
 ok(!/Math\.max\(0|MAX\(0/i.test(plan),'negative net being clamped');
 ok(plan.includes('commission_paid_and_cleared')&&plan.includes('affiliate_outbound'),'click/paid conversion conflated');
 ok(plan.includes('confirmed_signup')&&plan.includes('provider acceptance'),'lead confirmation contract absent');
 ok(plan.includes('7- and 30-day cohorts'),'cohort definition lost');
 ok(plan.includes('Grok')&&plan.includes('Praxxis'),'creator owner omitted');
 ok(plan.includes('TASK-008'),'creator handoff omitted');
 ok(plan.includes('site QA')||plan.includes('Site QA'),'browser QA owner omitted');
 ok(plan.includes('360/390/768/1440/1920'),'viewport acceptance missing');
 ok(plan.includes('No-go release verdict'),'explicit HOLD missing');
 ok(r172article.includes('sufficiently gradually')&&r172article.includes('arbitrary abrupt'),'inherited R172 gradual-change correction missing');
 ok(r172plan.includes('socioemotional and sociocognitive modules'),'inherited R172 module correction missing');
 if(verbose)console.log('R173 source PASS: '+n+' baseline assertions');
 return n;
}
const baselines=verify(src,true);
const mutations=[
 ['affiliate link injection','offer',s=>s.replace('href="https://finalvestige.com/focus/"','href="https://zen12.com/"')],
 ['native purchase enabled','offer',s=>s.replace('class="buy" disabled','class="buy"')],
 ['missing near disclosure','offer',s=>s.replace('<p class="disclosure">','<p class="quiet">')],
 ['commission disclosure removed','offer',s=>s.replace('may earn a commission','may recommend options')],
 ['false activation','offer',s=>s.replace('No earning link is active now','An earning link is live now')],
 ['third-party tracking','offer',s=>s.replace('</body>','<script src="https://tracking.example/analytics.js"></script></body>')],
 ['email form duplication','offer',s=>s.replace('</body>','<form><input type="email"></form></body>')],
 ['forced autoplay','offer',s=>s.replace('</body>','<video autoplay></video></body>')],
 ['missing no-index flag','offer',s=>s.replace('noindex,nofollow','index,follow')],
 ['reduced-motion deleted','offer',s=>s.replace('@media(prefers-reduced-motion:reduce)','@media(prefers-reduced-motion:none)')],
 ['lost skip navigation','offer',s=>s.replace('class="skip" href="#main"','class="skip" href="#lost"')],
 ['invalid source date','offer',s=>s.replace('$87.99','$19.99')],
 ['false video produced','offer',s=>s.replace('No video exists','A playable video exists')],
 ['free Focus link missing','offer',s=>s.replaceAll('https://finalvestige.com/focus/','https://example.invalid/focus/')],
 ['altered research sample','article',s=>s.replace('24 highly suggestible participants','240 unselected people')],
 ['accuracy conflation','article',s=>s.replace('AUC 0.961','AUC 1.000')],
 ['absent significance caveat','article',s=>s.replace('not statistically significant','statistically significant')],
 ['missing FTC near guide','guide',s=>s.replace('may earn a commission','will receive nothing')],
 ['invented checkout','guide',s=>s.replace('not an authenticated checkout quote','a verified final checkout quote')],
 ['opened 1 gate','matrix',s=>s.replace('"status": "CLOSED"','"status": "OPEN"')],
 ['invented affiliate URL','matrix',s=>s.replace('"affiliate_url": null','"affiliate_url": "https://unverified.example/link"')],
 ['fabricated money','matrix',s=>s.replace('"net_per_thousand": null','"net_per_thousand": 250')],
 ['fabricated Payhip SKU','matrix',s=>s.replace('"eligible_payhip_mind_sku": null','"eligible_payhip_mind_sku": "PRODUCT-999"')],
 ['health benefit approved','matrix',s=>s.replace('"id": "C09",\n      "text":','"id": "C09",\n      "text":').replace('"decision": "DO_NOT_ADOPT_AS_FACT"','"decision": "ALLOW_AS_FACT"')],
 ['losses clamped','plan',s=>s.replace('Keep negative net negative','Make negative net zero')],
 ['lost paid commission event','plan',s=>s.replace('commission_paid_and_cleared','affiliate_clicked')],
 ['unverified signup declaration','plan',s=>s.replace('provider acceptance/confirmation','client form submission')],
 ['inherited study correction reversed','r172article',s=>s.replace('sufficiently gradually','instantly')],
 ['inherited training module correction reversed','r172plan',s=>s.replace('socioemotional and sociocognitive modules','attention-only training')]
];
let caught=0;const failing=[];
for(const [label,key,fn] of mutations){const newValue=fn(src[key]);ensure(newValue!==src[key],'mutation not applied: '+label);try{verify({...src,[key]:newValue});failing.push(label);}catch(_err){caught++;}}
ensure(failing.length===0,'unsafe mutations not caught: '+failing.join(', '));
console.log('R173 mutation PASS: '+caught+'/'+mutations.length+' unsafe changes rejected');
console.log('SOURCE-LEVEL ONLY: browser/mobile/WCAG/CI/merchant/email/video/settlement checks not executed.');
