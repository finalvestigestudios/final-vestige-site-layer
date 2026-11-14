import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname,join} from 'node:path';
import assert from 'node:assert/strict';

const dir=dirname(fileURLToPath(import.meta.url));
const read=n=>readFileSync(join(dir,n),'utf8');
const A=read('ZEN12_A_TEXT_ONLY.html');
const B=read('ZEN12_B_OPTIONAL_FILM.html');
const H=read('MIND_ARCHIVE_SOURCE_REVIEW_ONLY.html');
const E=read('THE_GORILLA_THE_EXPERTS_MISSED.md');
const V=read('R384_FILM_CAPTIONS.vtt');
const P=read('R384_SEARCH_POSTER.svg');
const D=read('CONVERSION_ACCEPTANCE_AND_HANDOFF.md');
const M=JSON.parse(read('CLAIMS_RIGHTS_AND_RELEASE_MATRIX.json'));

let pass=0;
function check(ok,label){assert.ok(ok,label);pass++}
function nativeDisabled(s){return /<button\b[^>]*\sdisabled(?=\s|>|=)/i.test(s)}
function noMerchantHref(s){return !/<a\b[^>]*href\s*=\s*["'][^"']*(?:zen12\.com|inspire3\.com|hypnosislive\.com|brainwaveshots\.com|affiliates\.inspire3)/i.test(s)}
function safeHTML(s){return !/<script\b|<iframe\b|<form\b|<video\b|\son\w+\s*=|\sautoplay(?=\s|>|=)|<meta[^>]*http-equiv=["']refresh/i.test(s)}
function hasAdjacentDisclosure(s){
 const disc=s.indexOf('<div class="disclosure">'),btn=s.indexOf('<button class="cta-disabled"');
 return disc>=0&&btn>disc&&btn-disc<750&&s.slice(disc,btn).includes('may earn a commission');
}
function sourceBody(s){return s.slice(s.indexOf('<div class="hero">'),s.indexOf('<footer>'))}
function stripFilm(s){return s.replace(/<section class="film"[\s\S]*?<\/section>/,'')}
function caseChecks(label,s){
 check(s.startsWith('<!doctype html>'),label+' doctype');
 check(s.includes('<html lang="en">'),label+' language');
 check(s.includes('<meta name="viewport"'),label+' viewport');
 check(s.includes('name="robots" content="noindex,nofollow"'),label+' noindex');
 check(s.includes('name="referrer"'),label+' referrer');
 check(s.includes('prefers-reduced-motion:reduce'),label+' reduced motion');
 check(s.includes('@media(max-width:720px)'),label+' responsive');
 check(nativeDisabled(s),label+' genuine disabled button');
 check(hasAdjacentDisclosure(s),label+' visible near-CTA disclosure');
 check(noMerchantHref(s),label+' no merchant link');
 check(safeHTML(s),label+' no third party scripts/forms/iframes');
 check(s.includes('https://finalvestige.com/focus/'),label+' existing Focus route');
 check(s.includes('https://finalvestige.com/affiliate-disclosure/'),label+' affiliate policy');
 check(s.includes('We have not checked an authorized referred checkout'),label+' price caveat');
 check(s.includes('not automatically an independently demonstrated treatment'),label+' editorial limit');
 check(!/guaranteed focus|cures anxiety|boosts IQ/i.test(s),label+' no banned efficacy slogans');
 check(s.includes('twelve-minute')||s.includes('twelve minutes'),label+' practice context');
}
caseChecks('A',A);caseChecks('B',B);
check(!A.includes('<section class="film"'),'A no treatment');
check(B.includes('<section class="film"'),'B treatment exists');
check(stripFilm(sourceBody(B))===sourceBody(A),'exact buyer-body A/B parity');
check(B.includes('R384_SEARCH_POSTER.svg'),'local poster');
check(B.includes('non-playable film concept'),'no false playback');
check(B.includes('full 42-second narration transcript'),'accessible transcript');
check(V.startsWith('WEBVTT'),'WebVTT header');
check((V.match(/-->/g)||[]).length===6,'six cues');
check(V.includes('00:00:42.000'),'42-second final timestamp');
check(P.includes('aria-labelledby="svgtitle svgdesc"'),'SVG accessible description');
check(P.includes('not research stimuli'),'SVG rights limit');
check(!/<script\b|<foreignObject\b|<image\b/i.test(P),'SVG safe self contained');
check(E.split(/\s+/).length>2500,'substantive 2500+ word investigation');
for(const u of ['https://doi.org/10.1068/p281059','https://doi.org/10.1068/i0386','https://pmc.ncbi.nlm.nih.gov/articles/PMC3964612/','https://doi.org/10.1177/17470218211064903'])check(E.includes(u),'research source '+u);
check(E.includes('not a medical-error rate')||E.includes('not a medical miss-rate'),'no clinical generalization');
check(H.includes('Four editorial streams'),'hub four streams');
check(H.includes('noindex,nofollow'),'hub draft noindex');
check(safeHTML(H),'hub no forbidden controls');
check(H.includes('https://finalvestige.com/focus/'),'hub existing Focus');
check(M.claims.length>=30,'30+ provenance claims');
check(M.releaseGates.length>=30,'30+ release gates');
check(M.releaseGates.every(g=>g.status==='HOLD'),'no gate falsely cleared');
check(M.claims.filter(c=>c.status.startsWith('REJECT')).length>=8,'unsupported claims withheld');
check(D.includes('net_revenue_per_1000_qualified_human_sessions'),'actual net KPI');
check(D.includes('merchant_confirmed_paid_purchase'),'paid event');
check(D.includes('provider_confirmed_lead'),'confirmed lead');
check(D.includes('affiliate_outbound'),'affiliate click separate');
check(D.includes('NOT COMPUTABLE'),'missing outcome disclosed');
check(D.includes('NOT VERIFIED'),'unknown media IDs disclosed');
check(D.includes('Issue #150'),'other work preserved');
check(D.includes('independently verified'), 'honest outcomes');

const mutations=[
 ['merchant hyperlink',()=>A.replace('</main>','<a href="https://zen12.com?aff=fake">Buy</a></main>'),s=>noMerchantHref(s)],
 ['native disabled substitution',()=>A.replace('disabled aria-describedby','aria-disabled="true" aria-describedby'),s=>nativeDisabled(s)],
 ['missing disclosure',()=>A.replace('<div class="disclosure">','<div class="notice">'),s=>hasAdjacentDisclosure(s)],
 ['script insertion',()=>B.replace('</body>','<script src="//tracker.test/x.js"></script></body>'),s=>safeHTML(s)],
 ['form insertion',()=>B.replace('</body>','<form><input></form></body>'),s=>safeHTML(s)],
 ['iframe injection',()=>B.replace('</body>','<iframe src="https://zen12.com"></iframe></body>'),s=>safeHTML(s)],
 ['autoplay video',()=>B.replace('</body>','<video autoplay controls></video></body>'),s=>safeHTML(s)],
 ['onload event',()=>A.replace('</body>','<img src="x" onerror="hack()"></body>'),s=>safeHTML(s)],
 ['new merchant in anchor',()=>B.replace('</body>','<a href="https://affiliates.inspire3.com/abcd">Now</a></body>'),s=>noMerchantHref(s)],
 ['noindex removal',()=>A.replace('name="robots" content="noindex,nofollow"','name="robots" content="index,follow"'),s=>s.includes('name="robots" content="noindex,nofollow"')],
 ['buyer parity removal',()=>B.replace('A short listening routine is a format, not a promise.','A short listening routine is a miraculous cure.'),s=>stripFilm(sourceBody(s))===sourceBody(A)]
];
let rejected=0;
for(const [name,mutate,guard] of mutations){check(!guard(mutate()),'unsafe mutation rejected: '+name);rejected++}
console.log(JSON.stringify({status:'PASS',assertions:pass,mutationsRejected:rejected,files:9,release:'HARD HOLD'}));
