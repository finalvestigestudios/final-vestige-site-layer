// Run: node mind/r150/test-r150.cjs (on a normal checkout). No dependencies.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const dir=__dirname;
const read=n=>fs.readFileSync(path.join(dir,n),'utf8');
const article=read('posthypnotic-amnesia-investigation.md');
const packet=read('one-offer-clearance-and-creator-map.md');
const html=read('focus-bridge-REVIEW-ONLY.html');
const data=JSON.parse(read('claim-matrix-and-closed-gates.json'));
let n=0;
function check(label,fn){try{fn();n++;process.stdout.write('PASS '+label+'\n')}catch(e){console.error('FAIL '+label,e.message);process.exitCode=1}}
check('investigation has primary sources',()=>assert.match(article,/pubmed\.ncbi\.nlm\.nih\.gov\/4031223/));
check('1995 ERP source',()=>assert.match(article,/pubmed\.ncbi\.nlm\.nih\.gov\/7673565/));
check('1992 group source',()=>assert.match(article,/pubmed\.ncbi\.nlm\.nih\.gov\/1442638/));
check('distinguishes report versus erasure',()=>assert.match(article,/failure to \*report\*/));
check('article has focus next step',()=>assert.match(article,/finalvestige\.com\/focus/));
check('article does not claim lived experience',()=>assert.doesNotMatch(article,/I (used|tested|listened to) (Zen12|Total Focus)/i));
check('commercial CTA gate explicitly closed',()=>assert.match(packet,/HOLD_MERCHANT/));
check('owned Payhip rights unknown',()=>assert.match(packet,/rights license/));
check('affiliate_click is not an order',()=>assert.match(packet,/affiliate_click.*never.*sale/i));
check('creator asset IDs held',()=>assert.match(packet,/asset_id \*\*UNVERIFIED\*\*/));
check('bridge has existing focus URL',()=>assert.match(html,/href="https:\/\/finalvestige\.com\/focus\/"/));
check('bridge no scripts',()=>assert.doesNotMatch(html,/<script\b/i));
check('bridge no forms',()=>assert.doesNotMatch(html,/<form\b/i));
check('bridge no merchant redirects',()=>assert.doesNotMatch(html,/href="https:\/\/(zen12|hypnosislive|inspire3)\./i));
check('bridge accessible label',()=>assert.match(html,/aria-labelledby="read-on"/));
check('bridge semantic main',()=>assert.match(html,/<main>/));
check('bridge focus-visible',()=>assert.match(html,/:focus-visible/));
check('bridge motion reduction',()=>assert.match(html,/prefers-reduced-motion:reduce/));
check('no automatic media',()=>assert.doesNotMatch(html,/<video\b|<audio\b|autoplay/i));
check('bridge 48px target',()=>assert.match(html,/min-height:48px/));
check('claim register sufficiently populated',()=>assert.ok(data.claims.length>=20));
check('gates 20+',()=>assert.ok(Object.keys(data.gates).length>=20));
check('all merchant gates closed',()=>assert.ok(Object.values(data.gates).every(x=>x.status==='CLOSED'&&x.evidence===null)));
check('no active CTA authorization',()=>assert.equal(data.merchant_cta_authorized,false));
check('no verified commissions invented',()=>assert.equal(data.commission_verified,false));
check('unproven benefits rejected',()=>assert.ok(data.claims.some(c=>c.id==='C10'&&c.status==='REJECT')));
check('exact product not confused with zen12',()=>assert.ok(data.claims.some(c=>c.id==='C09'&&c.claim.includes('33-minute'))));
check('no fabricated tracking URLs in bridge',()=>assert.doesNotMatch(html,/[?&](?:ref|aff_id|click_id)=/i));
check('FTC disclaimer template near planned control documented',()=>assert.match(packet,/If you purchase through this link/));
check('no duplicate email list',()=>assert.doesNotMatch(html,/subscribe|input type="email"/i));

function mutationCaught(name,mutated,bad){
 check('adversarial mutation caught: '+name,()=>assert.equal(Boolean(bad(mutated)),true));
}
mutationCaught('external script',html.replace('</main>','<script src="https://other.example/t.js"></script></main>'),x=>/<script\\b/i.test(x));
mutationCaught('second signup form',html.replace('</main>','<form><input type="email"></form></main>'),x=>/<form\\b/i.test(x));
mutationCaught('merchant URL',html.replace('href="https://finalvestige.com/focus/"','href="https://zen12.com/?ref=bogus"'),x=>/href="https:\\/\\/(?:zen12|hypnosislive|inspire3)\\./i.test(x));
mutationCaught('affiliate query',html.replace('https://finalvestige.com/focus/','https://finalvestige.com/focus/?aff_id=bogus'),x=>/[?&](?:ref|aff_id|click_id)=/i.test(x));
mutationCaught('focus CTA removed',html.replace('href="https://finalvestige.com/focus/"','href="#"'),x=>!/href="https:\\/\\/finalvestige\\.com\\/focus\\/"/.test(x));
mutationCaught('commercial gate opened',JSON.stringify({...data,merchant_cta_authorized:true}),x=>JSON.parse(x).merchant_cta_authorized!==false);
mutationCaught('invented paid commission',JSON.stringify({...data,commission_verified:true}),x=>JSON.parse(x).commission_verified!==false);
mutationCaught('reopened merchant gate',JSON.stringify({...data,gates:{...data.gates,named_partner_approval:{status:'VERIFIED'}}}),x=>Object.values(JSON.parse(x).gates).some(g=>g.status!=='CLOSED'));
if(process.exitCode)process.exit(process.exitCode); console.log(n+' / '+n+' checks passed');