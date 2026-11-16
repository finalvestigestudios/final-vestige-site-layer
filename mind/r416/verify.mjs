// R416 source-gate verifier. Run: node mind/r416/verify.mjs
// Static checks only: NOT a substitute for browser WCAG, merchant approval or paid-order confirmation.
import {readFileSync} from 'node:fs';
import {join,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import assert from 'node:assert/strict';
const dir=dirname(fileURLToPath(import.meta.url));
const read=n=>readFileSync(join(dir,n),'utf8');
const files={a:read('ZEN12_A_TEXT.html'),b:read('ZEN12_B_OPTIONAL_FILM_CONCEPT.html'),hub:read('MIND_HUB_SOURCE_ONLY.html'),article:read('THE_FREQUENCY_THAT_WAS_SUPPOSED_TO_BECOME_FOCUS.md'),decision:read('CONVERSION_CHECKOUT_AND_CREATOR_ACCEPTANCE.md')};
const matrix=JSON.parse(read('CLAIM_PROOF_AND_PERMISSION_MATRIX.json'));
let tested=0;
const check=(name,fn)=>{fn();tested++;console.log('PASS '+String(tested).padStart(2,'0')+' '+name);};
const buyText=s=>s.replace(/<details class="film" id="optional-film">[\s\S]*?<\/details>/,'').replace(/<title>Zen12 independent guide — (?:B optional film concept|A text only) \| Final Vestige<\/title>/,'<title>Zen12 independent guide</title>');
const anchors=s=>[...s.matchAll(/<a\b[^>]*\bhref=["']([^"']+)["']/gi)].map(m=>m[1]);
const reject=s=>{
 assert(!/<script\b|<iframe\b|<form\b|<input\b|<object\b|<embed\b|<video\b/i.test(s),'active or input HTML element');
 assert(!/\bon\w+\s*=|\bautoplay(?:\\s|=|>)+|document\.cookie|localStorage|sessionStorage/i.test(s),'JS/auto tracking');
 assert(/<button\b[^>]*\bdisabled\b[^>]*>/i.test(s),'native disabled commerce control');
 assert(/Affiliate disclosure next to proposed offer:/.test(s),'adjacent affiliate disclosure');
 assert(/No such link is currently active/.test(s),'fail-closed language');
 assert(/If Final Vestige later offers an approved purchasing link/.test(s),'conditional relationship');
 assert(!anchors(s).some(h=>/^(https?:)?\/\/([^\/]*\.)?(?:zen12\.com|inspire3\.com|hypnosislive\.com|brainwaveshots\.com|affiliates\.inspire3\.com)(?:\/|$)/i.test(h)),'seller-linked merchant anchor');
 assert(!/\$(?:17|24|37|87)[\.,\d]*/i.test(s),'fixed offer price');
 assert(!/clinically proven.*Zen12|guaranteed.*concentration|instant cure/i.test(s),'unsubstantiated guarantee');
};
for(const k of ['a','b']){
 check(k+' document and noindex',()=>{assert(/<!doctype html>/i.test(files[k]));assert(/lang="en"/.test(files[k]));assert(/name="viewport"/.test(files[k]));assert(/noindex,nofollow/.test(files[k]));});
 check(k+' fail-closed commerce',()=>reject(files[k]));
 check(k+' free route and merchant descriptions',()=>{assert(files[k].includes('https://finalvestige.com/focus/'));assert(files[k].includes('https://zen12.com/about'));assert(files[k].includes('48 MP3s'));});
 check(k+' keyboard/mobile/reduced-motion',()=>{assert(/focus-visible/.test(files[k]));assert(/max-width:800px/.test(files[k]));assert(/prefers-reduced-motion/.test(files[k]));assert(/Skip to main content/.test(files[k]));});
 check(k+' external research and FTC',()=>{assert(files[k].includes('PMC10198548'));assert(files[k].includes('health-products-compliance-guidance'));});
}
check('A/B copy exactly identical apart from optional film and variant title',()=>assert.equal(buyText(files.a),buyText(files.b)));
check('B optional, no-JS, rights-original and transcript',()=>{assert(/<details class="film" id="optional-film">/.test(files.b));assert(/role="img"/.test(files.b));assert(/<title id="poster-title">/.test(files.b));assert(/Full accessible narration transcript/.test(files.b));assert(/no encoded video is supplied here/i.test(files.b));assert(!files.a.includes('optional-film'));});
check('B six caption ranges cover complete 42 sec',()=>{for(let [s,e] of [[0,7],[7,14],[14,21],[21,28],[28,35],[35,42]]) assert(files.b.includes(`00:${String(s).padStart(2,'0')}–00:${String(e).padStart(2,'0')}`));});
check('hub four streams and safe assets',()=>{['Perception and attention','history of suggestion','Practice and reflection','Tools under review'].forEach(t=>assert(files.hub.toLowerCase().includes(t.toLowerCase())));assert(files.hub.includes('noindex,nofollow'));assert(!/<form\b|<script\b|<iframe\b/i.test(files.hub));});
check('hub live-article and free link destinations',()=>{['/change-blindness/','/mesmerism/','/puysegurs-animal-magnetism-files/','https://finalvestige.com/focus/'].forEach(u=>assert(files.hub.includes(u)));});
check('substantive sourced investigation',()=>{assert(files.article.split(/\s+/).length>=1700);['Ingendoh','Smallwood','Chee','Puységur','FTC','2023','2024'].forEach(s=>assert(files.article.includes(s)));});
check('article seller and research independent citations',()=>{for(const u of ['https://pmc.ncbi.nlm.nih.gov/articles/PMC10198548/','https://pubmed.ncbi.nlm.nih.gov/38458383/','https://zen12.com/about','https://brainwaveshots.com/focus-shot','https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance'])assert(files.article.includes(u));});
check('matrix claims',()=>assert(matrix.claims.length>=30));
check('matrix sources',()=>assert(Object.keys(matrix.source_urls).length>=18));
check('all gates held closed',()=>{assert(matrix.release_gates.length>=25);assert(matrix.release_gates.every(g=>g.status==='HARD_HOLD'));});
check('no approved paid offer',()=>assert.deepEqual(matrix.approved_paid_offers,[]));
check('no revenue fabrication',()=>{assert.equal(matrix.kpi_net_revenue_per_1000_qualified_sessions,null);assert.equal(matrix.verified_paid_orders,null);});
check('decision map and 7/30 cohorts',()=>{['Change Blindness','Puységur','Mesmer','7/30-day','merchant_settled_commission','qualified_human_session'].forEach(s=>assert(files.decision.includes(s)));});
check('checkout friction language caution',()=>{assert(files.decision.includes('does not prove every field is mandatory'));assert(files.decision.includes('price/coupon'));});
check('no active script or subscription in prototype',()=>{for(const k of ['a','b','hub']) assert(!/<form\b|<script\b|<video\b[^>]*\bautoplay(?:\\s|=|>)/i.test(files[k]));});
const mutations=[
 s=>s.replace('<button type="button" disabled aria-disabled="true">','<button type="button">'),
 s=>s.replace('Affiliate disclosure next to proposed offer:','No further disclosure:'),
 s=>s.replace('No such link is currently active.','Get it today!'),
 s=>s.replace('</body>','<script>window.x=1</script></body>'),
 s=>s.replace('</body>','<a href="https://zen12.com/order">Pay now</a></body>'),
 s=>s.replace('</body>','<form><input name="email"></form></body>'),
 s=>s.replace('</body>','<video autoplay></video></body>'),
 s=>s.replace('No such link is currently active.','No such link is currently active. Price $37.'),
];
check('8 adversarial media/offer/PII mutations rejected',()=>{for(const change of mutations){let failed=false;try{reject(change(files.a));}catch{failed=true;}assert(failed,'unsafe mutation was accepted');}});
check('gate opening mutation rejected',()=>{const corrupted=JSON.parse(JSON.stringify(matrix));corrupted.release_gates[0].status='OPEN';assert(!corrupted.release_gates.every(g=>g.status==='HARD_HOLD'));});
console.log('R416: '+tested+' static assertions passed. Native Node source tests only; no browser or merchant verification.');
