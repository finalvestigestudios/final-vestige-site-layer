'use strict';
/**
 * FV Mind R204 reproducible static-source regression checks.
 * Run from any cwd: node mind/r204/test_mind_r204.cjs
 * Requires only Node.js built-ins; NO network, no credentials, no WP or merchant writes.
 * This cannot prove browser accessibility, film playback, checkout or sales.
 */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const ROOT = path.resolve(__dirname, '..', '..');
function read(p){return fs.readFileSync(path.join(ROOT,p),'utf8')}
const article = read('mind/r204/when-the-hand-on-the-table-feels-like-yours-RUBBER-HAND-UNPUBLISHED.md');
const hub = read('mind/r204/mind-archive-FOUR-STREAM-STATIC-PREVIEW-UNPUBLISHED.html');
const plan = read('mind/r204/ONE-VERIFIED-OFFER-CREATOR-FIT-CONVERSION-AB-ACCEPTANCE.md');
const matrix = JSON.parse(read('mind/r204/RUBBER-HAND-ZEN12-CLAIM-SOURCE-COMMERCE-MATRIX.json'));
const r203 = read('mind/r203/the-decision-they-switched-choice-blindness-UNPUBLISHED.md');
const r203m = JSON.parse(read('mind/r203/CHOICE-BLINDNESS-ZEN12-SOURCE-CLAIM-AUTHORIZATION-MATRIX.json'));
const r202m = JSON.parse(read('mind/r202/CLAIMS-OFFER-CONVERSION-VERIFICATION.json'));
const a=read('mind/r203/zen12-decision-record-A-TEXT-UNPUBLISHED.html');
const b=read('mind/r203/zen12-decision-record-B-OPTIONAL-42S-UNPUBLISHED.html');
const vtt=read('mind/r203/zen12-optional-choice-film-42s-UNRENDERED.vtt');

let passed=0;const failures=[];
function check(name, condition){let ok=false;try{ok=typeof condition==='function'?Boolean(condition()):Boolean(condition)}catch(e){failures.push(name+': '+e.message);return}if(ok)passed++;else failures.push(name)}
check('article source-control-only',article.includes('UNPUBLISHED — RESEARCH DRAFT'));
check('article substantive length',article.split(/\s+/).length>2200);
check('article original 1998 reference',article.includes('10.1038/35784'));
check('article 2011 measurement dispute',article.includes('21738756'));
check('article 2020 demand critique',article.includes('10.1525/collabra.325'));
check('article 2022 rebuttal',article.includes('s41467-022-28177-z'));
check('article 2023 meta analytic qualifier',article.includes('0.35'));
check('article avoids branding as evidence',article.includes('not evidence for Zen12')||article.includes('not evidence for Zen12'));
check('article does not activate tracking',!/<script|utm_content=|aw(in1)?\.com\/cread/i.test(article));
check('article distinguishes research from affiliate',article.includes('no affiliate earning link'));
check('hub self-contained HTML',hub.startsWith('<!doctype html>'));
check('hub HTML language',/<html lang="en">/.test(hub));
check('hub responsive viewport',/name="viewport"/.test(hub));
check('hub source-only noindex',/name="robots" content="noindex,nofollow"/.test(hub));
check('hub has native skip navigation',/class="skip" href="#main"/.test(hub));
check('hub has matching main landmark',/id="main"/.test(hub));
check('hub has four streams', (hub.match(/class="stream"/g)||[]).length===4);
check('hub responsive at mobile width',/@media\(max-width:780px\)/.test(hub));
check('hub reduced-motion preference',/prefers-reduced-motion:reduce/.test(hub));
check('hub forced-colors treatment',/forced-colors:active/.test(hub));
check('hub keyboard focus styling',/:focus-visible/.test(hub));
check('hub single existing Focus route',hub.includes('https://finalvestige.com/focus/'));
check('hub published Change Blindness path',hub.includes('https://finalvestige.com/2026/11/02/change-blindness/'));
check('hub published Mesmerism route',hub.includes('https://finalvestige.com/2026/11/02/mesmerism/'));
check('hub historical source trail',hub.includes('puysegurs-animal-magnetism-files/'));
check('hub not linking unpublished rubber-hand route',!/<a[^>]+href="[^"]*rubber-hand/i.test(hub));
check('hub image has accessible title',/role="img" aria-labelledby="diag-title diag-desc"/.test(hub));
check('hub diagram explicitly not archival',hub.includes('not a photograph'));
check('hub full disclosure',hub.includes('may earn a commission if you purchase through it, at no additional cost to you'));
check('hub native disabled button',/<button type="button" disabled aria-disabled="true">Merchant offer unavailable/.test(hub));
check('hub disclosure appears before button',hub.indexOf('Prospective affiliate disclosure')<hub.indexOf('<button type="button" disabled'));
check('hub no affiliate earning link',!/(?:www\.)?awin1\.com\/cread|clickbank\.net|aff_id=|\?hop=/i.test(hub));
check('hub no active merchant anchor',!/<a[^>]+href="https?:\/\/(?:www\.)?zen12\.com/i.test(hub));
check('hub no new email form',!/<form\b|<input\b/i.test(hub));
check('hub no JavaScript',!/<script\b|on(?:click|load|submit)=/i.test(hub));
check('hub no external media/third-party tags',!/<iframe|<video|<audio|src="http|@import\b/i.test(hub));
check('hub link fragments resolve',()=>{const ids=new Set([...hub.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]));return [...hub.matchAll(/href="#([^"]+)"/g)].every(m=>ids.has(m[1]))});
check('hub IDs unique',()=>{const ids=[...hub.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]);return ids.length===new Set(ids).size});
check('matrix all sources count',matrix.sources.length===matrix.source_count && matrix.source_count>=12);
check('matrix all claims count',matrix.claims.length===matrix.claim_count && matrix.claim_count>=18);
check('matrix all release gates count',matrix.gates.length===matrix.open_gate_count && matrix.gates.length>=25);
check('matrix all gates open',matrix.gates.every(g=>g.status==='OPEN'&&g.pass_evidence===null));
check('matrix each cited source exists',()=>{const ids=new Set(matrix.sources.map(x=>x.id));return matrix.claims.every(c=>c.source_ids.length>0&&c.source_ids.every(id=>ids.has(id)))});
check('matrix unique claim IDs',new Set(matrix.claims.map(c=>c.id)).size===matrix.claims.length);
check('matrix source URLs absolute https',matrix.sources.every(s=>s.url.startsWith('https://')));
check('matrix pending affiliate URL null',matrix.offer_priority.affiliate_url===null);
check('matrix no invented commission',matrix.offer_priority.commission===null);
check('matrix pending sale null',matrix.offer_priority.merchant_settled_sales===null);
check('matrix pricing withheld',matrix.offer_priority.price_to_publish===null);
check('matrix no fabricated owned checkout',matrix.offer_priority.fallback_status.includes('NOT_AUTHENTICATED'));
check('matrix no deployed A/B traffic',matrix.experiment.traffic===false&&matrix.experiment.randomized===false);
check('matrix creator fits contain no invented asset ID',matrix.creator_to_offer_fits.every(x=>!x.asset_id));
check('matrix campaigns count',matrix.creator_to_offer_fits.length===3);
check('plan price caveat',plan.includes('not sufficient to quote a firm checkout price'));
check('plan 42 second not playable',plan.includes('NOT a rendered MP4'));
check('plan no active merchant',plan.includes('natively disabled purchase controls'));
check('plan explicit risk and objections',plan.includes('Objections, respectfully'));
check('plan disclosure near CTA',plan.includes('may earn a commission at no additional cost to you'));
check('plan primary revenue metric',plan.includes('realized net revenue × 1,000 / qualified-human landing sessions'));
check('plan distinguishes clicks and paid sale',plan.includes('**not** a sale')&&plan.includes('merchant_paid_conversion'));
check('plan 7 and 30-day cohorts',plan.includes('7/30-day cohort'));
check('plan privacy no duplicate scripts',plan.includes('do not install a new script'));
check('plan first party UTM with asset ID',plan.includes('utm_content=<immutable actual Grok asset_id>'));
check('plan A and B references existing guides',plan.includes('mind/r203/zen12-decision-record-A-TEXT-UNPUBLISHED.html')&&plan.includes('mind/r203/zen12-decision-record-B-OPTIONAL-42S-UNPUBLISHED.html'));
check('plan protects homepage',plan.includes('homepage PR #49'));
check('r203 pension study ordering clarified',r203.includes('similar substitutions first')&&r203.includes('stopping manipulation trials'));
check('r203 correct political fieldwork year',r203.includes("Sweden's 2010 election"));
check('r203 jam tasted tea smelled',r203.includes('**tasted jam**')&&r203.includes('**smelled tea**'));
check('r203 moral survey measure clarified',r203.includes('statement and a recorded rating'));
check('r203 matrix assumption in CB08',r203m.claims.find(c=>c.id==='CB08').limit.includes('upper estimates assumed'));
check('r202 matrix corrigendum S07',r202m.sources.find(c=>c.id==='S07').note.includes('programming confounds'));
check('r202 matrix precise C08',r202m.claims.find(c=>c.id==='C08').statement.includes('fake news on social media'));
check('inherited A button disabled',/\bdisabled\b/.test(a));
check('inherited B button disabled',/\bdisabled\b/.test(b));
check('inherited A near affiliate disclosure',/commission/i.test(a));
check('inherited B near affiliate disclosure',/commission/i.test(b));
check('inherited video captions unrendered VTT',vtt.startsWith('WEBVTT')&&vtt.includes('-->'));
check('no live production controls added',!/<form\b/i.test(a+b));
const mutationCases=[
['remove disabled',s=>s.replace('disabled aria-disabled','aria-disabled'),s=>/<button type="button" disabled aria-disabled="true">Merchant offer unavailable/.test(s)],
['remove commission disclaimer',s=>s.replace('may earn a commission if you purchase through it, at no additional cost to you','may get paid'),s=>s.includes('may earn a commission if you purchase through it, at no additional cost to you')],
['insert active seller link',s=>s.replace('</footer>','<a href="https://zen12.com/hnp">Buy</a></footer>'),s=>!/<a[^>]+href="https?:\/\/(?:www\.)?zen12\.com/i.test(s)],
['inject script',s=>s.replace('</body>','<script>alert(1)</script></body>'),s=>!/<script\b/i.test(s)],
['add duplicate form',s=>s.replace('</main>','<form><input type="email"></form></main>'),s=>!/<form\b|<input\b/i.test(s)],
['break skip target',s=>s.replace('id="main"','id="gone"'),s=>/id="main"/.test(s)],
['remove noindex',s=>s.replace('noindex,nofollow','index,follow'),s=>/noindex,nofollow/.test(s)],
['remove focus style',s=>s.replace('a:focus-visible,button:focus-visible','a:focus,button:focus'),s=>/:focus-visible/.test(s)],
['revoke reduced motion',s=>s.replace('prefers-reduced-motion:reduce','prefers-reduced-motion:no-preference'),s=>/prefers-reduced-motion:reduce/.test(s)],
['insert unauthorized affiliate URL',s=>s.replace('</footer>','<a href="https://www.awin1.com/cread?x=1">click</a></footer>'),s=>!/awin1\.com\/cread/i.test(s)]
];
let caught=0;const missed=[];for(const [name,mutate,safe] of mutationCases){const change=mutate(hub);if(change!==hub&&!safe(change))caught++;else missed.push(name)}
if(failures.length||missed.length){console.error('FAILED static assertions',failures,'MUTATIONS missed',missed);process.exit(1)}
console.log(JSON.stringify({milestone:'R204',static_assertions_passed:passed,deliberate_unsafe_mutations_detected:caught,total_mutations:mutationCases.length,scope:'source-level only; not browser/CI/merchant/live',result:'PASS'}));
