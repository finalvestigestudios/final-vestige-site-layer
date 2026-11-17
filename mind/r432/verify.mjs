#!/usr/bin/env node
// R432 standalone, no-dependency source and commerce hold verifier.
// Run: node mind/r432/verify.mjs (repository checkout)
// This verifies static source invariants, NOT real-browser WCAG/CWV, video encoding, merchant rights or sales.
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
const dir = path.dirname(fileURLToPath(import.meta.url));
const filenames = ['THE_SECOND_NUMBER_ARRIVED.md','ZEN12_A_TEXT_BUYER_GUIDE.html','ZEN12_B_42S_FILM_CONCEPT.html','ZEN12_OPTIONAL_42S.vtt','ZEN12_OPTIONAL_POSTER.svg','MIND_ARCHIVE_WORDPRESS_SOURCE_ONLY.html','CLAIM_SOURCE_AND_RELEASE_MATRIX.json','CONVERSION_ACCEPTANCE_AND_GROK_CROSSWALK.md'];
const documents = Object.fromEntries(filenames.map(n=>[n,fs.readFileSync(path.join(dir,n),'utf8')]));
let count = 0;
function check(fn, title) { try { fn();count++; process.stdout.write('PASS '+title+'\n'); } catch(e) { console.error('FAIL '+title+': '+e.message); process.exitCode=1; } }
const a = documents['ZEN12_A_TEXT_BUYER_GUIDE.html'];
const b = documents['ZEN12_B_42S_FILM_CONCEPT.html'];
const hub = documents['MIND_ARCHIVE_WORDPRESS_SOURCE_ONLY.html'];
const article = documents['THE_SECOND_NUMBER_ARRIVED.md'];
const matrix = JSON.parse(documents['CLAIM_SOURCE_AND_RELEASE_MATRIX.json']);
const contract = documents['CONVERSION_ACCEPTANCE_AND_GROK_CROSSWALK.md'];
const poster = documents['ZEN12_OPTIONAL_POSTER.svg'];
const vtt = documents['ZEN12_OPTIONAL_42S.vtt'];
const core = s=>s.slice(s.indexOf('<section class="section" id="demo">'),s.indexOf('</main>'));
check(()=>assert.equal(core(a),core(b)),'buyer text A/B identical');
check(()=>assert.equal(matrix.release,'HARD_HOLD'),'matrix release HOLD');
check(()=>assert.equal(matrix.allow_earning_link,false),'affiliate activation false');
check(()=>assert.equal(matrix.allow_cms_write,false),'no CMS release');
check(()=>assert.equal(matrix.allow_tracking_deploy,false),'no tracking release');
check(()=>assert.equal(matrix.claim_count,matrix.claims.length),'claim count reconciled');
check(()=>assert.equal(matrix.source_count,matrix.sources.length),'source count reconciled');
check(()=>assert.equal(matrix.release_gates.length,28),'28 defined commercial gates');
check(()=>assert.ok(matrix.release_gates.every(x=>x.status==='HOLD'&&!x.evidence_id)),'all commercial gates on HOLD');
check(()=>assert.ok(matrix.claims.every(c=>c.source_ids.every(id=>matrix.sources.some(s=>s.id===id)))),'claim references resolve');
check(()=>assert.equal(new Set(matrix.sources.map(x=>x.id)).size,matrix.sources.length),'unique source ids');
check(()=>assert.equal(new Set(matrix.claims.map(x=>x.id)).size,matrix.claims.length),'unique claim ids');
for(const [label,html] of [['A',a],['B',b],['hub',hub]]){
 check(()=>assert.match(html,/<!doctype html>/i),label+' valid doctype');
 check(()=>assert.match(html,/<html lang="en">/),label+' english language');
 check(()=>assert.match(html,/<meta name="viewport"/),label+' viewport meta');
 check(()=>assert.match(html,/name="robots" content="noindex,nofollow"/),label+' noindex prototype');
 check(()=>assert.doesNotMatch(html,/<script\b|<iframe\b|<form\b|<input\b/i),label+' no scripts iframe or duplicate forms');
 check(()=>assert.doesNotMatch(html,/\bautoplay\s*(?:=|>|\/>)|onerror\s*=|onclick\s*=|javascript:/i),label+' no forced playback / inline handlers');
 check(()=>assert.doesNotMatch(html,/<a\b[^>]*href="https?:\/\/(?:zen12|affiliates\.inspire3|hypnosislive|brainwaveshots)\./i),label+' no merchant outbound links');
 check(()=>assert.match(html,/:focus-visible/),label+' keyboard visible focus');
 check(()=>assert.match(html,/@media\(max-width:/),label+' responsive CSS');
 check(()=>assert.match(html,/<main\b/),label+' meaningful main');
}
for(const [label,html] of [['A',a],['B',b]]){
 check(()=>assert.match(html,/If you purchase through a qualifying Final Vestige link, Final Vestige may earn a commission/),label+' clear nearby disclosure');
 check(()=>assert.match(html,/<button[^>]+disabled/),label+' affiliate CTA disabled');
 check(()=>assert.match(html,/no independently|not independently|does not validate|not a twelve-minute MP3/i),label+' product efficacy qualified');
 check(()=>assert.match(html,/https:\/\/finalvestige.com\/focus\//),label+' existing free route');
 check(()=>assert.match(html,/id="commercial-hold"/),label+' disabled CTA explanation');
 check(()=>assert.ok(html.indexOf('class="disclosure"') < html.indexOf('class="hold"')) ,label+' disclosure precedes CTA');
}
check(()=>assert.match(b,/id="optional-film"/),'B has optional media concept');
check(()=>assert.doesNotMatch(a,/id="optional-film"/),'A no film');
check(()=>assert.match(b,/Full 42-second narration|full 42-second narration/),'B has full narration');
check(()=>assert.match(b,/ZEN12_OPTIONAL_42S.vtt/),'B names VTT');
check(()=>assert.match(b,/ZEN12_OPTIONAL_POSTER.svg/),'B names poster');
check(()=>assert.match(poster,/<svg/),'poster is SVG');
check(()=>assert.match(poster,/<title id="title">/),'poster accessible title');
check(()=>assert.doesNotMatch(poster,/<script\b|<foreignObject\b|xlink:href\s*=|<image\b[^>]+href\s*=\s*['\"]https?:/i),'poster no script/remote assets');
check(()=>assert.match(vtt,/^WEBVTT/),'captions VTT header');
const cues=[...vtt.matchAll(/(\d\d:\d\d:\d\d\.\d{3}) --> (\d\d:\d\d:\d\d\.\d{3})/g)];
const ms=s=>{let [h,m,t]=s.split(':');return (+h)*3600000+(+m)*60000+Math.round(Number(t)*1000)};
check(()=>assert.equal(cues.length,6),'six caption cues');
check(()=>assert.equal(ms(cues[0][1]),0),'captions start at zero');
check(()=>assert.equal(ms(cues.at(-1)[2]),42000),'captions end 42 seconds');
check(()=>assert.ok(cues.every((x,i)=>ms(x[2])>ms(x[1])&&(i===0||ms(cues[i-1][2])===ms(x[1])))),'contiguous nonoverlap captions');
check(()=>assert.match(article,/1992/),'article original experiment dated');
check(()=>assert.match(article,/270-millisecond interval beginning 180 milliseconds/),'article precise task timing');
check(()=>assert.match(article,/17 practitioners and 23 novices/),'article group sizes');
check(()=>assert.match(article,/10–12 hours per day/),'article training intensity');
check(()=>assert.match(article,/NOT validate|does not license|does not validate|does not fill that gap/i),'article no product efficacy extrapolation');
check(()=>assert.match(article,/https:\/\/finalvestige.com\/free-resources\/puysegurs-animal-magnetism-files/),'historical bridge');
check(()=>assert.match(article,/https:\/\/finalvestige.com\/focus\//),'single Focus funnel');
check(()=>assert.ok(article.split(/\s+/).length>1900),'substantive original investigation');
check(()=>assert.match(contract,/UNMATCHED/),'real creator media unverified');
check(()=>assert.match(contract,/NOT COMPUTABLE/),'revenue undefined rather than invented');
check(()=>assert.match(contract,/affiliate_outbound/),'click distinct from sale');
check(()=>assert.match(contract,/7\/30/),'cohort requirements defined');
check(()=>assert.match(contract,/HOLD BOTH PAID CTA PATHS/),'payable-offer-first precedence');
console.log('R432:',count,'static assertions passed; native browser/WP/film/merchant checks not performed.');
if(process.exitCode)process.exit(1);
