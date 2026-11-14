// Offline source-only regression tests; run with: node mind/r376/verify.mjs
// No network, no paid tools, no CMS or affiliate interaction.
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
const root=path.dirname(fileURLToPath(import.meta.url));
const read=(name)=>fs.readFileSync(path.join(root,name),'utf8');
const article=read('THE_MACHINE_YOU_THOUGHT_YOU_UNDERSTOOD.md');
const a=read('ZEN12_A_BUYER_GUIDE.html');
const b=read('ZEN12_B_OPTIONAL_FILM_GUIDE.html');
const hub=read('MIND_HUB_WORDPRESS_REVIEW_ONLY.html');
const vtt=read('ORIGINAL_42S_CAPTIONS.vtt');
const memo=read('CONVERSION_ACCEPTANCE_AND_CREATOR_HANDOFF.md');
const matrix=JSON.parse(read('CLAIM_SOURCE_AUTHORIZATION_MATRIX.json'));
let pass=0;
function check(name,condition){assert.ok(condition,name);pass++;}
const filmRe=/<figure aria-labelledby="film-title">[\s\S]*?<\/figure>/;
const extractBlock=(html)=>html.match(/<section class="panel" id="offer">[\s\S]*?<\/section>/)?.[0]??'';
const safe=(html)=>!/<script\b|<iframe\b|<form\b|<video\b|<audio\b|<link\b[^>]*rel=["']?preload|autoplay(?:=|\s|>)/i.test(html)
   && !/href=["']https?:\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|affiliates\.inspire3\.com|hypnosislive\.com|brainwaveshots\.com)/i.test(html)
   && /<button class="cta" type="button" disabled\b/.test(html)
   && /class="disclosure"/.test(html)
   && /noindex,nofollow,noarchive/.test(html);
check('article substantial',article.trim().split(/\s+/).length>=1800);
for(const [k,v] of [['2002 source', '10.1207/s15516709cog2605_1'],['2013 source','10.1177/0956797612464058'],['Puységur route','puysegurs-animal-magnetism-files'],['Focus existing route','finalvestige.com/focus/'],['commercial distinction','not an endorsement'],['uncertainty','not a universal'],['free exercise','Minutes 0–2']])check('article '+k,article.toLowerCase().includes(v.toLowerCase()));
for(const [label,html] of [['A',a],['B',b],['Hub',hub]]){
 check(label+' HTML',html.startsWith('<!doctype html>'));
 check(label+' lang',html.includes('lang="en"'));
 check(label+' UTF8',html.includes('charset="utf-8"'));
 check(label+' viewport',html.includes('name="viewport"'));
 check(label+' robots',html.includes('noindex,nofollow,noarchive'));
 check(label+' no script',!/<script\b/i.test(html));
 check(label+' no form',!/<form\b/i.test(html));
 check(label+' no iframe',!/<iframe\b/i.test(html));
 check(label+' no active merchant links',!/href=["']https?:\/\/(?:www\.)?(?:zen12|inspire3|affiliates\.inspire3|hypnosislive|brainwaveshots)\./i.test(html));
}
for(const [label,html] of [['A',a],['B',b]]){
 check(label+' inactive offer',safe(html));
 check(label+' adjacent disclosure',extractBlock(html).includes('class="disclosure"')&&extractBlock(html).indexOf('class="disclosure"')<extractBlock(html).indexOf('<button class="cta"'));
 check(label+' Focus only existing funnel',html.includes('https://finalvestige.com/focus/'));
 check(label+' no seller purchase link',!/<a[^>]+href=["'][^"']*(?:zen12|inspire3)/i.test(html));
 check(label+' no product testimonial',!/(i (?:personally|used|tested|tried) zen12)/i.test(html));
 check(label+' no playback/autoplay',!/<(?:video|audio)[\s>]/i.test(html));
 check(label+' meaningful product format',html.includes('48 MP3 recordings')&&html.includes('twelve levels'));
}
check('B optional illustration',filmRe.test(b)&&b.includes('role="img"'));
check('B transcript',b.includes('Read the full 42-second narration transcript'));
check('B unchanged substantive buyer body',b.replace(filmRe,'')===a);
check('VTT starts WEBVTT',vtt.startsWith('WEBVTT'));
check('VTT cue count', (vtt.match(/-->/g)||[]).length===6);
check('VTT exact end',vtt.includes('00:00:42.000'));
check('VTT no markup tags', !/<script|<iframe|<img/i.test(vtt));
check('hub four streams', ['Perception &amp; Attention','History of Suggestion','Practice &amp; Reflection','Tools Under Review'].every(x=>hub.includes(x)));
check('hub existing single funnel',hub.includes('existing single Dispatch subscription'));
check('hub source-only',hub.includes('source prototype')||hub.includes('SOURCE PROTOTYPE'));
check('matrix claims',matrix.claims.length===32);
check('matrix release gates',matrix.gates.length===32);
check('matrix HOLD gates',matrix.gates.every(x=>x.status==='HOLD'&&x.verified_pass===false));
check('matrix distinct IDs',new Set(matrix.claims.map(x=>x.id)).size===32);
check('matrix exact status',matrix.commerce.issued_earning_url==='NOT VERIFIED');
check('matrix seller price conflict',matrix.commerce.seller_display_price.includes('CONFLICT'));
check('matrix named sources',Object.keys(matrix.sources).length===15);
check('memo source tags',memo.includes('utm_medium=organic_social'));
check('memo actual post gate',memo.includes('immutable asset_id'));
check('memo paid vs click',memo.includes('affiliate_outbound'));
check('memo revenue 7/30 day',memo.includes('7- and 30-day'));
check('memo net formula',memo.includes('net_revenue_per_1000'));
check('memo preserve owners',memo.includes('PR #49')&&memo.includes('PR #172'));
const mutants=[
 ['enabled native button',a.replace('type="button" disabled','type="button"')],
 ['aria-disabled fake',a.replace('type="button" disabled','type="button" aria-disabled="true"')],
 ['no disclosure',a.replace('class="disclosure"','class="advertising-note"')],
 ['direct seller href',a.replace('<button class="cta"','<a href="https://zen12.com/">Buy now</a><button class="cta"')],
 ['affiliate seller href',a.replace('<button class="cta"','<a href="https://affiliates.inspire3.com/xyz">Earn</a><button class="cta"')],
 ['added signup form',a.replace('</main>','<form action="/capture" method="get"><input name="email"></form></main>')],
 ['added script',a.replace('</main>','<script src="https://tracker.example/test.js"></script></main>')],
 ['added autoplay film',a.replace('</main>','<video autoplay src="file.mp4"></video></main>')],
 ['public indexable draft',a.replace('noindex,nofollow,noarchive','index,follow')],
 ['third-party iframe',a.replace('</main>','<iframe src="https://widgets.example/"></iframe></main>')]
];
function isHardHold(html){return safe(html)&&!/<form\b|<script\b|<iframe\b|<video\b/i.test(html)&&html.includes('noindex,nofollow,noarchive')&&extractBlock(html).includes('class="disclosure"')}
for(const [description,mutant] of mutants)check('reject mutant: '+description,!isHardHold(mutant));
console.log('PASS '+pass+' offline source and safety assertions; all '+mutants.length+' injected unsafe mutations rejected. NOT native browser/WP/merchant/CI QA.');
