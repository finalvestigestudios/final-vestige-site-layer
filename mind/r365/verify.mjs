/**
 * Mind R365 source-only regression tests.
 * Run: node mind/r365/verify.mjs
 * Designed for a checkout of this draft branch. Does not connect to live WP or merchant.
 */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const dir = path.dirname(fileURLToPath(import.meta.url));
const read = f => fs.readFileSync(path.join(dir, f), 'utf8');
const A = read('ZEN12_A_BUYER_GUIDE.html');
const B = read('ZEN12_B_OPTIONAL_FILM_GUIDE.html');
const article = read('THE_WORD_THAT_WOULDNT_LET_GO.md');
const hub = read('MIND_ARCHIVE_WORDPRESS_REVIEW_ONLY.html');
const vtt = read('ORIGINAL_42S_CAPTIONS.vtt');
const matrix = JSON.parse(read('CLAIMS_SOURCES_RIGHTS_RELEASE_MATRIX.json'));
const acceptance = read('CONVERSION_FIRST_ACCEPTANCE_AND_HANDOFF.md');
let checks = 0;
const ok = (condition, message) => { checks++; assert.ok(condition, message); };
const impossibleMerchantLink = s => /<a\b[^>]*href\s*=\s*["']https?:\/\/(?:www\.)?(?:zen12|inspire3|hypnosislive|brainwaveshots)\./i.test(s);
const unsafeMarkup = s => /<script\b|<iframe\b|<form\b|<input\b|<video\b|\sonclick\s*=|\sonsubmit\s*=|\sautoplay\s*=|dataLayer|gtag\s*\(/i.test(s);
const hasDisabled = s => /<button\b[^>]*\bdisabled\b[^>]*>/i.test(s);
const disclosed = s => /Affiliate disclosure:[\s\S]*?Final Vestige may earn a commission at no additional cost to you/.test(s);
const safe = s => hasDisabled(s)&&disclosed(s)&&!impossibleMerchantLink(s)&&!unsafeMarkup(s);
const core = s => s.replace(/<section class="film"[\s\S]*?<\/section>/,'').replace(/Version [AB]/g,'Version X').replace(/>\s+</g,'><').trim();
ok(article.split(/\s+/).length >= 1900, 'deep original research threshold');
ok(article.includes('status: SOURCE_CONTROL_ONLY_NOT_PUBLISHED'), 'not published editorial status');
for(const p of ['https://pubmed.ncbi.nlm.nih.gov/12470132/','https://pubmed.ncbi.nlm.nih.gov/15994228/','https://doi.org/10.1080/00207144.2024.2356856','https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/','https://www.nccih.nih.gov/health/hypnosis']) ok(article.includes(p), 'article lacks source '+p);
for(const claim of ['16 highly suggestible and 16 less','not evidence that a consumer','historical analogy','not a product']) ok(article.toLowerCase().includes(claim.toLowerCase()), 'article boundary: '+claim);
ok(core(A)===core(B), 'A/B must contain identical substantive text');
for(const [v,s] of [['A',A],['B',B]]) {
  ok(s.includes('noindex,nofollow'),v+' must be noindex');
  ok(s.includes('name="viewport"'),v+' must be mobile-first');
  ok(s.includes('lang="en"'),v+' language');
  ok(s.includes('Skip to guide'),v+' skip link');
  ok(s.includes('prefers-reduced-motion'),v+' reduced motion');
  ok(s.includes('https://finalvestige.com/focus/'),v+' preserves fieldbook');
  ok(s.includes('subscribed')===false,v+' no invented subscriptions');
  ok(safe(s),v+' compliance-gated');
  ok(!/rel\s*=\s*["']sponsored/.test(s),v+' no fake active earning link');
  ok(!/merch.*approved for FV/i.test(s),v+' no merchant approval claim');
  ok(s.includes('seller')&&s.includes('refund'),v+' buyer limits');
  ok(!/https?:\/\/(clicks\.aweber|wow\.inspire3)/.test(s),v+' no leaked marketing URLs');
}
ok(!A.includes('class="film"'), 'A text only');
ok(B.includes('class="film"'), 'B optional film concept');
ok(B.includes('role="img"'), 'B described original poster');
ok(B.includes('film-desc'), 'B detailed SVG description');
ok(B.includes('<details>'), 'B full offline transcript');
ok(B.includes('not a playable')||B.includes('No encoded movie'), 'B must not claim hosted video');
ok(vtt.startsWith('WEBVTT'), 'VTT format');
const cues = [...vtt.matchAll(/(\d{2}):(\d{2}):(\d{2})\.(\d{3}) --> (\d{2}):(\d{2}):(\d{2})\.(\d{3})/g)];
ok(cues.length===6, '6 cues');
const ms=(h,m,s,f)=>(+h*3600 + +m*60 + +s)*1000 + +f;
const times=cues.map(c=>[ms(...c.slice(1,5)),ms(...c.slice(5,9))]);
ok(times[0][0]===0, '0s first cue');
ok(times[times.length-1][1]===42000, '42s endpoint');
ok(times.every(([start,end],i)=>end>start && (i===0||start===times[i-1][1])), 'sequential nonoverlapping captions');
ok((hub.match(/class="stream"/g)||[]).length===4, 'four distinct Mind streams');
ok(!unsafeMarkup(hub),'hub no scripts forms or iframe');
ok(!impossibleMerchantLink(hub),'hub no merchant links');
ok(hub.includes('noindex,nofollow'),'hub noindex');
ok(hub.includes('https://finalvestige.com/2026/11/02/change-blindness/'),'only verified live editorial route');
ok(hub.includes('https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/'),'source archive route');
ok(matrix.claims.length>=40,'claim ledger');
ok(Object.keys(matrix.sources).length>=15,'diverse official sources');
ok(matrix.release_gates.length===32,'commercial safety gate count');
ok(matrix.release_gates.every(g=>g.state==='HOLD'),'every release gate closed');
for(const prop of ['accepted_publisher','issued_link','allowed_channels','owned_mind_payhip_sku']) ok(matrix.commerce_authorization[prop]==='not_authenticated','must not invent '+prop);
ok(matrix.commerce_authorization.buyer_cta==='DISABLED','cannot activate');
ok(matrix.revenue.net_revenue_per_1000_qualified_human_sessions==='NOT_COMPUTABLE','net metric cannot be zero or fabricated');
ok(acceptance.includes('NOT COMPUTABLE')||acceptance.includes('NOT_COMPUTABLE'),'revenue boundary');
ok(acceptance.includes('seven')||acceptance.includes('7-day'),'cohort analysis');
ok(acceptance.includes('Grok')&&acceptance.includes('Praxxis')&&acceptance.includes('Claude'),'ownership');
ok(acceptance.includes('utm_content')&&acceptance.includes('asset_id'),'proper attribution contract');
const mutations=[
  s=>s.replace('button type="button" disabled','button type="button"'),
  s=>s.replace('Affiliate disclosure:', 'Discontinued promotion:'),
  s=>s.replace('Final Vestige may earn a commission at no additional cost to you','The audio will change your brain'),
  s=>s+'<a href="https://zen12.com/affiliate?unverified=true">Buy now</a>',
  s=>s+'<script>alert("track")</script>',
  s=>s+'<iframe src="https://example.com/tracker"></iframe>',
  s=>s+'<form><input type="email"></form>',
  s=>s+'<video autoplay src="/original.mp4"></video>'
];
for(const [i, mutate] of mutations.entries()) ok(!safe(mutate(A)),'unsafe mutation was not rejected #'+(i+1));
console.log('R365 exact-source Node static compliance: '+checks+'/'+checks+' PASS; 8/8 deliberate unsafe mutations rejected; native browser, WordPress, real media, merchant and CI are NOT covered.');
