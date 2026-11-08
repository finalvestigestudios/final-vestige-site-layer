'use strict';
/**
 * R205 offline static-source guardrails. Run: node mind/r205/test_mind_r205.cjs
 * Node built-ins only. Does NOT contact WP, merchant, subscriber APIs or external sources.
 * Source-only: no assurance of actual WCAG 2.2 compliance, playback, page speed or paid sales.
 */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const article=read('mind/r205/the-pendulum-that-answered-ideomotor-science-UNPUBLISHED.md');
const hub=read('mind/r205/mind-archive-four-stream-IDEOMOTOR-WP-PREVIEW-UNPUBLISHED.html');
const A=read('mind/r205/zen12-evidence-A-TEXT-UNPUBLISHED.html');
const B=read('mind/r205/zen12-evidence-B-OPTIONAL-42S-UNPUBLISHED.html');
const vtt=read('mind/r205/zen12-ideomotor-optional-42s-UNRENDERED.vtt');
const plan=read('mind/r205/OFFER-FIRST-CREATOR-FIT-NET-REVENUE-RELEASE-GATE.md');
const M=JSON.parse(read('mind/r205/IDEOMOTOR-SOURCE-CLAIMS-OFFER-AUTHORIZATION.json'));
const oldArticle=read('mind/r204/when-the-hand-on-the-table-feels-like-yours-RUBBER-HAND-UNPUBLISHED.md');
const oldM=JSON.parse(read('mind/r204/RUBBER-HAND-ZEN12-CLAIM-SOURCE-COMMERCE-MATRIX.json'));
const oldChoice=JSON.parse(read('mind/r203/CHOICE-BLINDNESS-ZEN12-SOURCE-CLAIM-AUTHORIZATION-MATRIX.json'));
let passed=0;const failed=[];function check(name,test){let okay=false;try{okay=typeof test==='function'?!!test():!!test}catch(e){failed.push(name+':'+e.message);return}if(okay)passed++;else failed.push(name)}
function idsUnique(s){const ids=[...s.matchAll(/\bid="([^"]+)"/g)].map(x=>x[1]);return ids.length===new Set(ids).size}
function fragmentsResolve(s){const ids=new Set([...s.matchAll(/\bid="([^"]+)"/g)].map(x=>x[1]));return [...s.matchAll(/href="#([^"]+)"/g)].every(x=>ids.has(x[1]))}
function noRisk(s){return !/<script\b|<iframe\b|<form\b|<input\b|on(?:click|load|submit)\s*=|@import\b|src="https?:/i.test(s)&&!/(?:www\.)?awin1\.com\/cread|clickbank\.net|[?&]hop=|[?&]aff_id=/i.test(s)}
function noSellerAnchor(s){return !/<a\b[^>]*href="https?:\/\/(?:www\.)?(?:zen12\.com|hypnosislive\.com)[^"]*"[^>]*>/i.test(s)}
function safeCommerce(s){const dis=s.indexOf('id="affiliate-disclosure"');const btn=s.indexOf('Merchant purchase link withheld');return dis>0&&btn>dis&&/<button class="btn" type="button" disabled\b/.test(s)&&s.includes('we may earn a commission at no additional cost to you')&&noRisk(s)&&noSellerAnchor(s)}
function stripFilm(s){return s.replace(/<section id="film"[\s\S]*?<\/section>/,'').replace('optional-film · Unpublished','text · Unpublished').replace('Variant B: identical core text plus optional unrendered short-film concept','Variant A: text only')}
check('article release banner',article.includes('UNPUBLISHED / no WordPress write'));
check('article > 2700 words',article.split(/\s+/).length>2700);
check('article primary pendulum',article.includes('10.1080/00221309.1976.9710871'));
check('article Ouija 2012 original',article.includes('22377138'));
check('article 2022 nonreplication primary',article.includes('2021.2010641'));
check('article 2017 bias not accuracy claim',article.includes('**57% verbally**')&&article.includes('**53% with the pendulum**'));
check('article 2018 online 2019 issue difference',article.includes('**2018**')&&article.includes('**2019 journal issue**'));
check('article no brand effectiveness inference',article.includes('They do not test Zen12, Hypnosis Live'));
check('article seller independent',article.includes('No pendulum'));
check('article historical source link',article.includes('puysegurs-animal-magnetism-files'));
check('article original free exercise',article.includes('three columns'));
check('article has historical and scientific limits',article.includes('historical review, not'));
check('article scientific sources at least 8', (article.match(/^\d+\. /gm)||[]).length>=9);
check('article no affiliate link',!/(?:www\.)?awin1\.com|hop=|affiliate earning URL/.test(article));
check('A doctype language',A.startsWith('<!doctype html>')&&A.includes('<html lang="en">'));
check('B doctype language',B.startsWith('<!doctype html>')&&B.includes('<html lang="en">'));
check('hub doctype language',hub.startsWith('<!doctype html>')&&hub.includes('<html lang="en">'));
for(const [name,s] of [['A',A],['B',B],['hub',hub]]){
check(name+' responsive viewport',s.includes('name="viewport"'));
check(name+' noindex',s.includes('noindex,nofollow'));
check(name+' keyboard focus',s.includes(':focus-visible'));
check(name+' reduced motion',s.includes('prefers-reduced-motion:reduce'));
check(name+' forced colors',s.includes('forced-colors:active'));
check(name+' named main',s.includes('id="main"'));
check(name+' skip link',s.includes('href="#main"'));
check(name+' unique IDs',()=>idsUnique(s));
check(name+' internal fragments resolve',()=>fragmentsResolve(s));
check(name+' no active remote assets/forms/scripts',()=>noRisk(s));
check(name+' no merchant active anchor',()=>noSellerAnchor(s));
check(name+' no invented live ideomotor route',!/<a[^>]*href="[^"]*ideomotor-effect/i.test(s));
}
check('hub four stream structure',(hub.match(/class="stream"/g)||[]).length===4);
check('hub diagram accessible',hub.includes('role="img" aria-labelledby="pend-title pend-desc"'));
check('hub image not archival',hub.includes('not an archival photograph'));
check('hub published change blindness',hub.includes('finalvestige.com/2026/11/02/change-blindness/'));
check('hub historical Mesmerism',hub.includes('finalvestige.com/2026/11/02/mesmerism/'));
check('hub Puységur route',hub.includes('finalvestige.com/free-resources/puysegurs-animal-magnetism-files/'));
check('hub existing Focus only',hub.includes('finalvestige.com/focus/')&&!/<form\b/.test(hub));
check('hub prospective disclosure adjacent',hub.includes('may earn a commission at no additional cost to you')&&hub.indexOf('id="close-disclosure"')<hub.indexOf('Commercial offer not active'));
check('hub purchase disabled',/<button type="button" disabled/.test(hub));
check('A commercial-safe',()=>safeCommerce(A));
check('B commercial-safe',()=>safeCommerce(B));
check('A/B core EXACT text unchanged',stripFilm(B)===A);
check('B only film block', B.includes('<section id="film"')&&!A.includes('<section id="film"'));
check('film is conceptual/no playable element',B.includes('Not produced or playable')&&!/<video\b|<audio\b/.test(B));
check('film original accessible static SVG',B.includes('role="img" aria-labelledby="pendulum-title pendulum-desc"'));
check('film transcript native details',B.includes('<details>')&&B.includes('00:38–00:42'));
check('caption file WEBVTT',vtt.startsWith('WEBVTT'));
check('caption timestamp 42',vtt.includes('00:00:38.000 --> 00:00:42.000'));
check('caption no phantom synced player',!B.includes('<track'));
check('both guides seller inventory accurate',A.includes('48 MP3 recordings')&&B.includes('48 MP3 recordings'));
check('guides price conflict explicit',A.includes('$87.99')&&A.includes('$87')&&A.includes('neither'));
check('guides non-medical',A.includes('not clinically tested Zen12 Premium')===false && A.includes('has not purchased, used or clinically tested Zen12 Premium'));
check('guides free existing Focus without new opt-in form',A.includes('finalvestige.com/focus/')&&!/<form\b/.test(A));
check('matrix source count',M.source_count===M.sources.length&&M.source_count>=20);
check('matrix claims count',M.claim_count===M.claims.length&&M.claim_count>=30);
check('matrix gates count',M.gate_count===M.gates.length&&M.gate_count>=30);
check('matrix unique source ids',new Set(M.sources.map(s=>s.id)).size===M.sources.length);
check('matrix unique claim ids',new Set(M.claims.map(c=>c.id)).size===M.claims.length);
check('matrix all claims source resolved',()=>{const ids=new Set(M.sources.map(x=>x.id));return M.claims.every(c=>c.source_ids.length&&c.source_ids.every(id=>ids.has(id)))});
check('matrix all sources HTTPS',M.sources.every(x=>x.url.startsWith('https://')));
check('matrix all gates open',M.gates.every(x=>x.status==='OPEN'&&x.evidence===null));
check('matrix publisher acceptance null',M.lead_offer.specific_partner_acceptance===null);
check('matrix earning URL null',M.lead_offer.issued_affiliate_url===null);
check('matrix personalized commission null',M.lead_offer.personal_commission_terms===null);
check('matrix checkout price null',M.lead_offer.final_checkout_price===null);
check('matrix paid orders null',M.lead_offer.merchant_confirmed_orders===null);
check('matrix net revenue null',M.lead_offer.net_revenue===null);
check('matrix CTA disabled',M.lead_offer.paid_purchase_cta==='DISABLED');
check('matrix owned product not authenticated',M.lead_offer.fallback_owned_mind_product==='NOT AUTHENTICATED');
check('matrix creator actual IDs missing',M.creator_to_offer_fits.length===3&&M.creator_to_offer_fits.every(x=>x.asset_id===null));
check('matrix A/B unrendered',M.experiment.traffic===false&&M.experiment.status.includes('UNRENDERED'));
check('matrix disputed seller price noted',M.offer_discrepancy.includes('$87.99')&&M.offer_discrepancy.includes('$87 Premium'));
check('matrix privacy contract avoids PII',M.event_contract.storage.includes('no IP'));
check('plan actual offer and fit',plan.includes('**Zen12 Premium**')&&plan.includes('Three creator'));
check('plan noncomparable price caution',plan.includes('**$87.99**')&&plan.includes('**$87**'));
check('plan 7 and 30 day cohorts',plan.includes('**7-day and 30-day cohorts**'));
check('plan formula net revenue',plan.includes('realized net revenue per 1,000 qualified human landing sessions'));
check('plan explicit click not sale',plan.includes('NOT a sale'));
check('plan verified merchant event',plan.includes('merchant_paid_conversion'));
check('plan actual Grok asset IDs',plan.includes('immutable real Grok asset_id'));
check('plan no new analytics',plan.includes('No duplicate script'));
check('plan hold publisher',plan.includes('HOLD affiliate activation'));
check('plan protects homepage',plan.includes('homepage PR #49'));
check('prior 2020 Collabra separate from n353',oldArticle.includes('different 2020 study must be kept distinct'));
check('prior same n353 reanalysis',oldArticle.includes('**same 353-participant data**'));
check('prior S1-S3 composite',oldArticle.includes('**referred touch and ownership**'));
check('prior rho and p',oldArticle.includes('**−0.066**')&&oldArticle.includes('**.219**'));
check('prior author reply and DOI',oldArticle.includes('s41467-022-28178-y'));
check('prior matrix source total coherent',oldM.source_count===oldM.sources.length);
check('prior matrix all source references coherent',()=>{const ids=new Set(oldM.sources.map(x=>x.id));return oldM.claims.every(c=>c.source_ids.every(id=>ids.has(id)))});
check('prior matrix RH08 separate samples',oldM.claims.find(c=>c.id==='RH08').decision==='REJECT');
check('prior matrix RH06 includes nature study',oldM.claims.find(c=>c.id==='RH06').source_ids.includes('S16'));
check('prior R203 CB08 count corrected',oldChoice.claims.find(c=>c.id==='CB08').limit.includes('98 participants with usable'));
const mutations=[
['A purchase enabled',A,s=>s.replace('type="button" disabled','type="button"'),safeCommerce],
['A disclosure suppressed',A,s=>s.replace('we may earn a commission at no additional cost to you','our partners support us'),safeCommerce],
['A added merchant link',A,s=>s.replace('</footer>','<a href="https://zen12.com/hnp">BUY</a></footer>'),safeCommerce],
['A injected JS',A,s=>s.replace('</body>','<script src="https://example.com/t.js"></script></body>'),safeCommerce],
['B added form',B,s=>s.replace('</main>','<form><input type="email"></form></main>'),noRisk],
['B iframe embed',B,s=>s.replace('</body>','<iframe src="https://videos.test"></iframe></body>'),noRisk],
['B tracking link',B,s=>s.replace('</footer>','<a href="https://www.awin1.com/cread?tag=1">x</a></footer>'),safeCommerce],
['A on-click',A,s=>s.replace('<main id="main">','<main id="main" onclick="bad()">'),noRisk],
['hub paid embed',hub,s=>s.replace('</body>','<iframe src="https://www.example.com"></iframe></body>'),noRisk],
['A new font remote',A,s=>s.replace('</style>','@import url(https://example.com/font.css);</style>'),noRisk],
['B forced merchant anchor',B,s=>s.replace('</main>','<a href="https://hypnosislive.com/shop">Buy</a></main>'),noSellerAnchor],
['A direct affiliate URL',A,s=>s.replace('</main>','<a href="https://clickbank.net/?hop=x">Buy</a></main>'),noRisk],
];let caught=0,missed=[];for(const [name,orig,mutate,predicate] of mutations){const changed=mutate(orig);if(changed!==orig&&!predicate(changed))caught++;else missed.push(name)}
if(failed.length||missed.length){console.error(JSON.stringify({passed,failed,mutations_caught:caught,missed}));process.exit(1)}
console.log(JSON.stringify({milestone:'R205',assertions_passed:passed,mutations_caught:caught,total_mutations:mutations.length,scope:'offline static-source only; NOT browser/CI/merchant/revenue',result:'PASS'}));
