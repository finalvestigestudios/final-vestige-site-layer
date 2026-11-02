import {test} from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import {ATTRIBUTION_ENABLED,record,validateSynthetic,summarizeSynthetic} from './attribution.mjs';
const here=new URL('.',import.meta.url);const read=x=>fs.readFileSync(new URL(x,here),'utf8');
const A=read('presell-A-text.html'),B=read('presell-B-film.html'),core=read('guide-core.html'),article=read('investigation.html'),hub=read('mind-hub-candidate.html'),vtt=read('film-40s.vtt'),matrix=read('claims-permissions.csv'),sources=read('source-register.csv');
for(const [name,html] of [['A',A],['B',B]]){
 test(name+' exact guide',()=>assert.equal(html.split('<main class="guide" id="guide-core">')[1].split('</main>')[0],core));
 test(name+' native-off button',()=>assert.match(html,/<button[^>]*disabled[^>]*>/));
 test(name+' prospective near-CTA disclosure',()=>{const p=html.indexOf('Final Vestige may earn a commission'),b=html.indexOf('<button');assert(p>0&&b>p&&b-p<500)});
 test(name+' no active commerce and no scripts/forms',()=>{assert(!/<script\b|<form\b|<iframe\b|<video\b|autoplay|dataLayer|gtag\(|fbq\(/i.test(html));assert(!/<a[^>]+href=["']https?:\/\/(?:zen12|inspire3|affiliates\.inspire3)/i.test(html))});
}
test('article independently source-grounded no commerce',()=>{assert.match(article,/James Braid/);assert.match(article,/Puységur/);assert(!/Zen12|Inspire3|commission|checkout|purchase through/i.test(article));});
test('film variant has complete noJS transcript',()=>{assert(!A.includes('Read the complete 40-second film transcript'));assert(B.includes('<details>')&&B.includes('<summary>Read the complete 40-second film transcript</summary>'));assert(B.includes('Not proof')||B.includes('proof of a promised result'));});
test('six continuous caption windows 0-40s',()=>{const times=[...vtt.matchAll(/(\d\d:\d\d:\d\d\.\d{3}) --> (\d\d:\d\d:\d\d\.\d{3})/g)];assert.equal(times.length,6);assert.equal(times[0][1],'00:00:00.000');assert.equal(times.at(-1)[2],'00:00:40.000');for(let i=1;i<6;i++)assert.equal(times[i-1][2],times[i][1]);});
test('hub only published routes and canonical restraint',()=>{assert.match(hub,/PR #172/);assert(!/<form\b|<script\b|autoplay/i.test(hub));assert.match(hub,/finalvestige.com\/focus/);});
test('claim matrix covers approval and denial',()=>{assert(matrix.includes('Final Vestige Zen12 approval'));assert(matrix.includes('BLOCK'));assert(matrix.includes('Zen12 hour equivalence'));assert(matrix.split('\n').length>=45);});
test('source register has exact official and FTC sources',()=>{for(const x of ['https://zen12.com/hnp','https://inspire3.com/','ftc.gov','pubmed.ncbi.nlm.nih.gov/37205669'])assert(sources.includes(x));});
test('synthetic tracking fully disabled and PII rejected',()=>{assert.equal(ATTRIBUTION_ENABLED,false);assert.equal(record({topic:'braid',channel:'organic',variant:'A'}),false);assert(!validateSynthetic({topic:'braid',channel:'organic',variant:'A',email:'a@b.com'}));assert(!validateSynthetic({topic:'braid',channel:'organic',variant:'A',ip:'127.0.0.1'}));});
test('synthetic privacy n19 suppressed n20 aggregate',()=>{const row={topic:'braid',channel:'organic',variant:'B'};assert.deepEqual(summarizeSynthetic(Array.from({length:19},()=>({...row}))),[]);assert.equal(summarizeSynthetic(Array.from({length:20},()=>({...row})))[0].count,20);});
