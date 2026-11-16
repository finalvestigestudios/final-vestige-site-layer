// R414 isolated, no-dependency fail-closed source verifier.
// Usage: node mind/r414/verify.mjs (from repository root).
// Does NOT simulate WordPress, browser, real playback, merchant checkout or production QA.
import { readFileSync } from 'node:fs';
import { strict as assert } from 'node:assert';
const base = 'mind/r414/';
const read = (name) => readFileSync(base + name, 'utf8');
const a = read('ZEN12_A_TEXT.html');
const b = read('ZEN12_B_OPTIONAL_FILM.html');
const hub = read('MIND_HUB_WP_SOURCE_DRAFT.html');
const article = read('THE_RECORDING_IS_NOT_THE_EXPERIMENT.md');
const svg = read('ZEN12_42S_POSTER.svg');
const captions = read('ZEN12_42S_CAPTIONS.vtt');
const matrix = JSON.parse(read('CLAIM_SOURCE_PERMISSION_MATRIX.json'));
const dossier = read('CONVERSION_ACCEPTANCE_AND_CREATOR_FIT.md');
let checks=0;
function check(condition,reason){checks++;assert.ok(condition,reason);}
const guide = (s) => s.match(/<main class="wrap" id="buyer-guide">[\s\S]*?<\/main>/)?.[0] || '';
const badLink = /<a\b[^>]*href=["']https?:\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|affiliates\.inspire3\.com|hypnosislive\.com|brainwaveshots\.com)\b/i;
const badTracking = /<script\b|<iframe\b|<form\b|<input\b|\bonclick\s*=|\bonload\s*=|\bonerror\s*=|\bautoplay\s*(?:=|\s|>)/i;
function assertSafeHtml(s,which){
  check(/<!DOCTYPE html>/i.test(s),which+' requires doctype');
  check(/<html lang="en">/.test(s),which+' must declare language');
  check(/name="viewport"/.test(s),which+' must have viewport');
  check(/name="robots" content="noindex,nofollow"/.test(s),which+' must be unpublished preview');
  check(!badTracking.test(s),which+' prohibits scripts, forms, embeds, handlers, autoplay');
  check(!badLink.test(s),which+' no off-site merchant or affiliate clickable links');
  check(!/utm_source=|utm_content=|fbclid|gclid/i.test(s),which+' no production campaign tracking');
}
for (const [name,html] of [['A',a],['B',b],['hub',hub]]) assertSafeHtml(html,name);
check(guide(a).length>5500,'buyer guide A substantively complete');
check(guide(a)===guide(b),'A/B buyer copy byte-identical');
for (const [name,html] of [['A',a],['B',b]]) {
  const offer=html.match(/<section class="offer"[\s\S]*?<\/section>/)?.[0] || '';
  check(offer.includes('If you purchase through a future authorized link, Final Vestige may earn a commission at no additional cost to you.'),name+' nearby full FTC disclosure');
  check(/<button\b[^>]*\bdisabled\b/.test(offer),name+' genuinely disabled native button');
  check(offer.indexOf('may earn a commission')<offer.indexOf('<button'),name+' disclosure before button');
  check(offer.includes('named')===false || offer.includes('unverified'),name+' holds commercial CTA');
  check(html.includes('href="https://finalvestige.com/focus/"'),name+' free first-party resource present');
  check((html.match(/<button\b/g)||[]).length===1,name+' one commerce button');
  check(!/\$\s*\d+/.test(html),name+' no unverified advertised fixed price');
}
check(b.includes('Optional 42-second original film concept'),'B film clearly labelled concept');
check(b.includes('NOT a playable video'),'B does not claim playback');
check(b.includes('src="./ZEN12_42S_POSTER.svg"'),'B poster asset referenced');
check(b.includes('href="./ZEN12_42S_CAPTIONS.vtt"'),'B VTT linked');
check(b.includes('<details>')&&b.includes('<summary>'),'B transcript works without JS');
check(!a.includes('id="optional-film"'),'A truly text-only');
check(svg.includes('viewBox="0 0 960 540"'),'poster 16:9');
check(svg.includes('<title')&&svg.includes('<desc'),'poster accessibility description');
check(!/<(?:script|image|foreignObject)\b/i.test(svg),'poster has no external fetch/scripts');
check(captions.startsWith('WEBVTT'),'valid VTT header');
const cueTimes=[...captions.matchAll(/(\d\d):(\d\d):(\d\d)\.(\d{3}) --> (\d\d):(\d\d):(\d\d)\.(\d{3})/g)].map(m=>{
const p=(idx)=>+m[idx]*3600 + +m[idx+1]*60 + +m[idx+2] + +m[idx+3]/1000; return [p(1),p(5)];
});
check(cueTimes.length===6,'six timed caption cues');
check(cueTimes[0]?.[0]===0,'cue starts zero');
check(cueTimes.at(-1)?.[1]===42,'42 second film');
cueTimes.forEach(([s,e],i)=>{check(e>s,'cue positive length '+i);if(i)check(s===cueTimes[i-1][1],'no caption gaps '+i);});
check(hub.includes('Perception &amp; Attention')&&hub.includes('History of Suggestion')&&hub.includes('Practice &amp; Reflection')&&hub.includes('Tools Under Review'),'four streams present');
check(!hub.includes('href="https://zen12.com'),'no merchant hub link');
check(article.split(/\s+/).length>=1900,'substantive original article');
check(article.includes('168 met the review')&&article.includes('only **four**'),'accurate survey scope and caveat');
check(article.includes('not a finding that all other apps are ineffective'),'avoid reverse efficacy inference');
check(article.includes('not Zen12-specific')===false || article.includes('independent'),'research claim boundary');
check(article.includes('https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/'),'historical bridge');
check(article.includes('https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance'),'FTC source');
check(matrix.claims.length>=30,'30 classified claims');
check(matrix.release_gates.length>=26,'26 explicit gates');
check(matrix.release_gates.every(g=>g.status==='HOLD'),'all gates fail closed');
check(matrix.active_affiliate_link===false&&matrix.verified_fv_partner_approval===false,'no false permission');
check(matrix.verified_fv_owned_payable_mind_sku===false,'no fake owned SKU');
check(matrix.verified_affiliate_commission===false,'no fabricated commission');
check(matrix.release_approval===false,'no release');
check(matrix.claims.some(c=>c.id==='S016'&&c.status==='excluded'),'exclude 12m equals one hour');
check(matrix.claims.some(c=>c.id==='S025'&&c.status==='qualified_seller_statement'),'returns caveat visible');
check(matrix.sources.ftc_health.startsWith('https://www.ftc.gov/'),'FTC source pin');
check(dossier.includes('NOT COMPUTABLE'),'unknown revenue not zero');
check(dossier.includes('NOT VERIFIED'),'no fictional social IDs');
check(dossier.includes('Founder/Commerce'),'permission owner');
check(dossier.includes('Claude/Dispatch'),'newsletter owner');
// Adversarial safety controls: each single mutation MUST be caught by the appropriate gate.
const mutations=[
['activate native button',a.replace('class="disabled" disabled','class="disabled"'),s=>!/<button\b[^>]*\bdisabled\b/.test(s.match(/<section class="offer"[\s\S]*?<\/section>/)?.[0]||'')],
['inject merchant link',a.replace('View verified Zen12 checkout — unavailable','<a href="https://zen12.com/order">Buy now</a>'),s=>badLink.test(s)],
['inject new signup',a.replace('</body>','<form action="/subscribe"><input type="email"></form></body>'),s=>badTracking.test(s)],
['remove disclosure',a.replace('If you purchase through a future authorized link, Final Vestige may earn a commission at no additional cost to you.',''),s=>!(s.match(/<section class="offer"[\s\S]*?<\/section>/)?.[0]||'').includes('may earn a commission')],
['inject javascript',a.replace('</body>','<script src="https://example.com/t.js"></script></body>'),s=>badTracking.test(s)],
['inject autoplay',b.replace('</body>','<video autoplay controls></video></body>'),s=>badTracking.test(s)],
['insert fixed price',a.replace('Not a live offer.','Price $37. Not a live offer.'),s=>/\$\s*\d+/.test(s)],
['break A/B equality',b.replace('Twelve minutes','Eleven minutes'),s=>guide(s)!==guide(a)]
];
for(const [name,mut,detector] of mutations){check(detector(mut),'negative test caught '+name);}
console.log('R414 Node source-only verifier PASS '+checks+'/'+checks+' assertions, '+mutations.length+'/'+mutations.length+' unsafe mutations rejected. This is NOT browser, WordPress, playable media, Jetpack or merchant proof.');
