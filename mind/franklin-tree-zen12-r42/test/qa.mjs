import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {classify,syntheticReport,ENABLED,canCollect} from '../attribution.mjs';
const root=new URL('../',import.meta.url);
const read=name=>readFileSync(new URL(name,root),'utf8');
const a=read('zen12-text-only.wp.html'),b=read('zen12-film.wp.html'),article=read('franklin-commission.wp.html'),hub=read('mind-hub-alt.wp.html'),matrix=read('claim-matrix.csv');
const pages=[a,b,article,hub];
let passes=0;
function check(condition,label){assert.ok(condition,label);passes++;}
const anchorPattern=/<a\b[^>]*href=['"][^'"]*(?:zen12\.com|inspire3\.com|affiliates\.inspire3\.com)/i;
const unsafeTagPattern=/<(?:script|form|iframe)\b/i;
const autoplayTag=/<video\b[^>]*\bautoplay\b/i;
const disabled=/\bdisabled\s+aria-disabled="true"/;
const hasDisclosure=x=>x.includes('Affiliate disclosure:')&&x.includes('may earn a commission')&&x.includes('at no additional cost to you');
const guideCore=x=>x.slice(x.indexOf('<h1>'),x.indexOf('<aside class="offer"'));
check(pages.every(x=>x.includes('prefers-reduced-motion:reduce')),'reduced-motion CSS all');
check(pages.every(x=>x.includes('focus-visible')),'keyboard focus CSS all');
check(pages.every(x=>x.includes('@media(max-width:')),'responsive styles all');
check(a.includes('class="fvm-r42"')&&b.includes('class="fvm-r42"'),'buyer scoped styles');
check(article.includes('class="fv-r42"'),'science scoped styles');
check(hub.includes('class="fvm-archive-r42"'),'hub scoped styles');
check((a.match(/<h1>/g)||[]).length===1&&(b.match(/<h1>/g)||[]).length===1,'buyer H1 exactly one');
check(guideCore(a)===guideCore(b),'A/B substantive buyer guide identical bytes');
check(!pages.some(x=>unsafeTagPattern.test(x)),'no scripts, forms, iframes');
check(!pages.some(x=>autoplayTag.test(x)),'no autoplay video');
check(!pages.some(x=>anchorPattern.test(x)),'no unauthorized merchant link');
check(!pages.some(x=>/href=['"][^'"]*\butm_/i.test(x)),'no query tracking links');
check(hasDisclosure(a)&&hasDisclosure(b),'both prospective near-CTA disclosures');
check(disabled.test(a)&&disabled.test(b),'commercial CTA disabled both');
check(!hasDisclosure(article)&&!article.includes('class="offer"'),'history is not presell');
check(b.includes('not hosted on the website'),'honest video offline state');
check(b.includes('Read the complete 40-second film transcript'),'accessible transcript fallback');
check(b.includes('<svg role="img"'),'first party SVG media poster');
check(b.includes('no-JavaScript fallback'),'no JS fallback explanation');
check(!a.includes('<svg role="img"'),'A remains text-only');
check(hub.includes('canonical Mind hub remains draft PR #172'),'canonical hub preserved');
check(hub.includes('/focus/')&&article.includes('/focus/')&&a.includes('/focus/'),'only existing Focus route');
check(matrix.split('\n').filter(Boolean).length>=60,'substantive claims matrix');
check(matrix.includes('HARD HOLD')&&matrix.includes('UNSUBSTANTIATED'),'claims gated');
check(a.indexOf('Affiliate disclosure:')>a.indexOf('<aside class="offer"'),'near CTA disclosure A');
check(b.indexOf('Affiliate disclosure:')>b.indexOf('<aside class="offer"'),'near CTA disclosure B');
check(ENABLED===false && !canCollect(),'synthetic attribution always off');
const record={topic:'meditation',asset:'zen12_guide',variant:'text',slot:'context',destination:'seller_unavailable'};
check(classify(record)?.topic==='meditation','allowlisted categorical event');
for (const mut of [{...record,email:'a@example.com'},{...record,ip:'1.2.3.4'},{...record,referrer:'https://example.com'},{...record,utm_source:'tiktok'},{...record,user_agent:'Mozilla'},{...record,topic:'medical'},{...record,variant:'<script>'},null,{},[],42]){
 check(classify(mut)===null,'reject unexpected data');
}
check(syntheticReport(Array(9).fill(record)).length===0,'suppress cells under ten');
check(syntheticReport(Array(10).fill(record)).length===1,'report eligible synthetic 10 count');
check(syntheticReport([record],9).length===0,'forbid unsafe threshold override');
check(syntheticReport([{...record,email:'person@example.com'}]).length===0,'reject identifiable fake event');
// Mutation suite: inject unsafe HTML and assert the gate catches each.
function safeBuyer(x){return hasDisclosure(x)&&disabled.test(x)&&!anchorPattern.test(x)&&!unsafeTagPattern.test(x)&&!autoplayTag.test(x);}
for (const injected of [
 a.replace('Affiliate disclosure:','Disclosure removed:'),
 a.replace('disabled aria-disabled="true"',''),
 a+'<a href="https://zen12.com/getstarted">Buy</a>',
 a+'<a href="https://inspire3.com/">Shop</a>',
 b+'<form><input name="email"></form>',
 b+'<iframe src="https://example.com/track"></iframe>',
 b+'<video autoplay src="film.mp4"></video>',
 b+'<script>alert(1)</script>'
])check(!safeBuyer(injected),'unsafe mutation rejected');
check(read('film.vtt').includes('00:00:40.000'),'timed VTT ends at 40 seconds');
console.log('R42 SOURCE/PRIVACY MUTATION CHECKS PASSED:',passes);
