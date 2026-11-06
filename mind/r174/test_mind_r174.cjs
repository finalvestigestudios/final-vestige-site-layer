/* Mind R174 — native Node 18+ source and deliberate unsafe-mutation guardrails.
   Run: node mind/r174/test_mind_r174.cjs
   Committed-source checks only. No browser, product approval, sale or actual conversion verified. */
'use strict';const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=process.env.MIND_R174_ROOT||process.cwd();
const paths={article:'mind/r174/what-hypnotizability-measures-INVESTIGATION-UNPUBLISHED.md',guide:'mind/r174/zen12-premium-independent-buyer-guide-UNPUBLISHED.md',offer:'mind/r174/zen12-premium-decision-UNPUBLISHED.html',hub:'mind/r174/mind-archive-conversion-integration-UNPUBLISHED.html',matrix:'mind/r174/product-evidence-claims-closed-gates.json',contract:'mind/r174/conversion-first-creator-to-paid-acceptance.md',r173a:'mind/r173/memory-confidence-is-not-accuracy-INVESTIGATION-UNPUBLISHED.md',r173g:'mind/r173/zen12-premium-independent-decision-guide-UNPUBLISHED.md',r173c:'mind/r173/creator-offer-conversion-attribution-and-acceptance.md'};
const read=()=>Object.fromEntries(Object.entries(paths).map(([k,p])=>[k,fs.readFileSync(path.join(root,p),'utf8')]));
let checks=0;function ok(x,msg){checks++;assert.ok(x,msg)}function reject(x,msg){ok(!x,msg)}
function audit(x){
ok(x.article.split(/\s+/).length>1700,'research must be substantive');
for(const s of ['pubmed.ncbi.nlm.nih.gov/2926631/','pubmed.ncbi.nlm.nih.gov/12470132/','pubmed.ncbi.nlm.nih.gov/39032268/','16 highly','16 less','Puységur','not a','not medical'])ok(x.article.toLowerCase().includes(s.toLowerCase()),'article science/limit: '+s);
reject(/<script\b/i.test(x.offer+x.hub),'script must not enter preview');
reject(/<form\b/i.test(x.offer+x.hub),'additional form');
reject(/<(?:iframe|video)\b/i.test(x.offer+x.hub),'do not falsely claim playable video or third-party embed');
reject(/\b(?:href|src)\s*=\s*["']https?:\/\/(?:zen12\.com|www\.zen12\.com|inspire3\.com|affiliates\.inspire3\.com|brainwaveshots\.com)/i.test(x.offer+x.hub),'merchant link activation');
ok(/<button[^>]*disabled[^>]*>Merchant purchase unavailable/i.test(x.offer),'button native disabled');
ok(/Potential affiliate disclosure:[\s\S]{0,400}<\/div>\s*<button[^>]*disabled/i.test(x.offer),'FTC disclosure adjacent to buying control');
ok(/No affiliate link is active here/i.test(x.offer),'disclosure no affiliate enabled');
ok(/<meta name="robots" content="noindex,nofollow"/i.test(x.offer),'draft noindex');
ok(/prefers-reduced-motion/i.test(x.offer+x.hub),'reduced-motion support');
ok(/<meta name="viewport"/i.test(x.offer+x.hub),'mobile responsive');
ok(/href="https:\/\/finalvestige\.com\/focus\/"/.test(x.offer+x.hub),'existing Focus route');
ok(/42-second|42 seconds/i.test(x.offer),'short video concept');
ok(/no playable video/i.test(x.offer),'unproduced video disclosure');
ok(/not a verified checkout|not independently verified checkout/i.test(x.guide),'checkout limitation');
ok(/no affiliate earning link or purchasing button is active/i.test(x.guide),'affiliate disabled guide');
ok(/links to the official seller above are \*\*editorial citations/i.test(x.guide.toLowerCase()),'guide citation links accurately distinguished');
ok(/a measured response|measured response/i.test(x.article),'distinct experiment claims');
ok(/refunds_not_already_in_receipts/i.test(x.contract),'avoid double deduction');
ok(/chargebacks_not_already_in_receipts/i.test(x.contract),'avoid double chargeback deduction');
ok(/NOT COMPUTABLE/.test(x.contract),'unknown KPI never zero');
ok(/negative stays negative/i.test(x.contract),'loss not hidden');
ok(/immutable asset_id/.test(x.contract),'creator provenance');
ok(/mini museum-first/i.test(x.contract.toLowerCase()),'preserve current Grok priority');
const m=JSON.parse(x.matrix);
ok(m.status==='UNPUBLISHED_HARD_HOLD','matrix release hold');
ok(m.sources.length>=14 && m.claims.length>=20 && m.gates.length>=20,'matrix depth');
ok(m.gates.every(g=>g.status==='CLOSED'),'fail-closed all gates');
ok(m.claims.some(c=>c.decision.includes('EXCLUDE_NO_EXACT_PRODUCT')),'unsupported product efficacy excluded');
ok(m.claims.some(c=>c.id==='C16'&&c.decision.includes('CLOSED')),'affiliate authorization unknown');
ok(/measured (memory|accuracy) improvement/i.test(x.r173a)||/accuracy/i.test(x.r173a),'R173 still scientific');
reject(/^# The Memory That Felt Sharper, but Wasn't/m.test(x.r173a),'categorical R173 title');
ok(/editorial citations for auditing/.test(x.r173g),'merchant citation distinction corrected');
ok(/refunds_not_already_in_receipts|refunds and chargebacks not already reflected/i.test(x.r173c),'R173 double-subtraction repaired');
ok(/commission_paid_and_cleared/i.test(x.r173c),'R173 transaction semantic retained');
ok(!/\$\d+.*guaranteed revenue|100% guaranteed results|this product cured/i.test(x.guide+x.offer+x.contract),'no unsupported income/health guarantees');
return checks;
}
const x=read();audit(x);const baseline=checks;
const mutations=[
['offer',s=>s.replace(' disabled aria-disabled',' aria-disabled')],
['offer',s=>s.replace('No affiliate link is active here.','Buy using our link now.')],
['offer',s=>s.replace('Potential affiliate disclosure:','Marketing information:')],
['offer',s=>s.replace('https://finalvestige.com/focus/','https://zen12.com/')],
['offer',s=>s.replace('<button type="button" disabled','<button type="button"')],
['offer',s=>s.replace('name="robots" content="noindex,nofollow"','name="robots" content="index,follow"')],
['offer',s=>s.replace('prefers-reduced-motion','no-motion-rule')],
['offer',s=>s.replace('42-second','15-second')],
['offer',s=>s.replace('no playable video','playable video')],
['offer',s=>s.replace('</main>','<script>fetch("/pixel")</script></main>')],
['offer',s=>s.replace('</main>','<form><input type="email"></form></main>')],
['offer',s=>s.replace('</main>','<iframe src="https://zen12.com"></iframe></main>')],
['guide',s=>s.replace('not independently verified checkout','verified checkout')],
['guide',s=>s.replace('No affiliate earning link or purchasing button is active','Our affiliate earning link is active')],
['guide',s=>s.replace('editorial citations for auditing','approved commissions for advertising')],
['matrix',s=>s.replace('"UNPUBLISHED_HARD_HOLD"','"LIVE"')],
['matrix',s=>s.replace('"status": "CLOSED"','"status": "OPEN"')],
['matrix',s=>s.replace('EXCLUDE_NO_EXACT_PRODUCT_SUBSTANTIATION','APPROVED')],
['contract',s=>s.replace('refunds_not_already_in_receipts','refunds')],
['contract',s=>s.replace('chargebacks_not_already_in_receipts','chargebacks')],
['contract',s=>s.replace('NOT COMPUTABLE','0.00')],
['contract',s=>s.replace('Negative stays negative','Negative is clamped to zero')],
['contract',s=>s.replace('immutable asset_id','fabricated asset_id')],
['r173a',s=>s.replace('The Memory That Felt More Certain Without Greater Accuracy','The Memory That Felt Sharper, but Wasn\'t')],
['r173g',s=>s.replace('editorial citations for auditing','commerce links for purchases')],
['r173c',s=>s.replace('refunds_not_already_in_receipts','refunds')]
];
let killed=0;for(const [key,f] of mutations){const y={...x,[key]:f(x[key])};if(y[key]===x[key])throw Error('Mutation failed to change '+key);try{audit(y)}catch(_){killed++;}}
assert.equal(killed,mutations.length,'all deliberately unsafe mutations must fail');
process.stdout.write('Mind R174: '+baseline+' baseline assertions PASS; '+killed+'/'+mutations.length+' unsafe mutations killed. SOURCE ONLY.\n');
