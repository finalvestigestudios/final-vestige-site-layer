#!/usr/bin/env node
// Mind R397 offline source gates. npm-free, Node >=18. Run: node mind/r397/verify.mjs
// Static assertions are NOT browser accessibility, WordPress sanitizer, hosted CI,
// seller checkout, Jetpack delivery, or verified affiliate/revenue tests.
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import assert from 'node:assert/strict';

const root = dirname(fileURLToPath(import.meta.url));
const read = (file) => readFileSync(join(root, file), 'utf8');
const a = read('ZEN12_A_TEXT_ONLY.html');
const b = read('ZEN12_B_OPTIONAL_FILM.html');
const hub = read('MIND_HUB_WORDPRESS_REVIEW_SOURCE.html');
const article = read('THE_FACE_THAT_LOOKED_NORMAL_UPSIDE_DOWN.md');
const vtt = read('THATCHER_42S.vtt');
const matrix = JSON.parse(read('CLAIMS_SOURCES_AUTHORIZATION_MATRIX.json'));
const acceptance = read('CONVERSION_ACCEPTANCE_AND_GROK_HANDOFF.md');
let checks = 0;
function ok(x, message) { assert.ok(x, message); checks++; }
function eq(x, y, message) { assert.equal(x, y, message); checks++; }
const core = (s) => s.split('<section aria-labelledby="why">')[1]?.split('</main>')[0];
function sourceSafety(s) {
  return !/<(?:script|iframe|form|video|audio)\b/i.test(s)
    && !/\bautoplay\b\s*(?:=|>)/i.test(s)
    && !/<a\b[^>]*href\s*=\s*["']https?:\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|affiliates\.inspire3\.com|hypnosislive\.com|brainwaveshots\.com)/i.test(s)
    && /<button\b[^>]*\bdisabled\b/i.test(s)
    && !/<(?:a|button)\b[^>]*\bonclick\s*=/i.test(s)
    && /If Final Vestige receives approval/.test(s)
    && /may earn a commission/.test(s)
    && !/we tested Zen12|we used Zen12|proven to cure|guaranteed to cure/i.test(s);
}
ok(sourceSafety(a),'A must not activate unsafe commerce or media');
ok(sourceSafety(b),'B must not activate unsafe commerce or media');
eq(core(a),core(b),'identical substantive buyer copy in A/B');
ok(core(a).length > 4500,'substantive buyer evidence, not thin affiliate paragraph');
ok(!a.includes('class="film-note"') && b.includes('class="film-note"'),'only B contains optional video concept');
ok(b.includes('role="img"') && b.includes('aria-labelledby="post-title post-desc"'),'poster accessible');
ok(b.includes('SCHEMATIC ONLY') && b.includes('NOT A TEST'),'diagram not presented as experiment');
ok(b.includes('No playable media file exists'),'no fictitious encoded movie');
ok(!b.includes('preload="auto"'),'no media loading by default');
ok(!/<script\b|<iframe\b/i.test(hub),'hub no script or external embed');
ok(!/<form\b/i.test(hub),'hub no duplicate sign-up');
ok(!/href=["'][^"']*\/mind\/[^"']+/.test(hub),'hub contains no unpublished Mind article route');
ok(hub.includes('DRAFT ONLY') && hub.includes('UNPUBLISHED'),'clear published vs draft');
ok(hub.includes('https://finalvestige.com/focus/'),'existing Fieldbook route intact');
ok(article.length > 13000,'deep original investigation');
for(const id of ['LOBMAIER2007','WONG2010','PSALTA2014','FTC_ENDORSE','FTC_HEALTH','WP_PUY','WP_FOCUS','ZEN_ORDER','ZEN_PROMO']){
  ok(matrix.source_urls.some(s=>s.id===id && s.url.startsWith('https://')), 'source present: '+id);
}
eq(matrix.inventory.posts,66,'published posts inventory');
eq(matrix.inventory.pages,92,'published pages inventory');
eq(matrix.inventory.mind_live_page,false,'Mind is not live');
ok(matrix.claims.length>=25,'evidence matrix breadth');
ok(matrix.gates.length>=16 && matrix.gates.every(g=>g.status==='HOLD' && g.proof===null),'every release gate closed');
ok(matrix.claims.filter(c=>c.kind==='partner_authorization').every(c=>c.status==='NOT_VERIFIED'),'no fabricated approval');
ok(matrix.claims.some(c=>c.kind==='seller_efficacy' && c.status.includes('UNSUBSTANTIATED')),'unverified seller promises classified');
ok(acceptance.includes('partner_paid_conversion') && acceptance.includes('affiliate_click'),'different conversion events');
ok(acceptance.includes('NOT COMPUTABLE') && acceptance.includes('qualified-human sessions'),'no phantom revenue');
ok(acceptance.includes('2026/11/02/change-blindness/') && acceptance.includes('/mesmerism/') && acceptance.includes('puysegurs-animal-magnetism-files'),'three real published topic routes');
ok(acceptance.includes('No creator assignment is made'),'creator lane preserved');
const cueRegex=/^(\d\d:\d\d:\d\d\.\d{3}) --> (\d\d:\d\d:\d\d\.\d{3})$/gm;
const cues=[...vtt.matchAll(cueRegex)];
eq(cues.length,6,'six VTT cues');
eq(cues[0][1],'00:00:00.000','caption starts at zero');
eq(cues.at(-1)[2],'00:00:42.000','caption ends at 42s');
const sec = t=> {const [h,m,rest]=t.split(':');return (+h*3600)+(+m*60)+Number(rest)};
for(let i=0;i<cues.length;i++){
  ok(sec(cues[i][2])>sec(cues[i][1]),'positive cue duration '+i);
  if(i) eq(cues[i-1][2],cues[i][1],'continuous cue timing '+i);
}
const lines = vtt.split('\n');
const captionText = lines.filter(s=>s.trim() && !/WEBVTT|-->/.test(s)).join(' ').replace(/\s+/g,' ').trim();
const transcript = b.match(/<p id="film-transcript">([\s\S]*?)<\/p>/)?.[1].replace(/<[^>]*>/g,'').replace(/\s+/g,' ').trim();
eq(captionText,transcript,'caption wording exactly equals transcript');
const mutantCases={
  'active seller link': a.replace('<button type="button" disabled','<a href="https://zen12.com/getstarted">BUY</a><button type="button" disabled'),
  'lost approval notice': a.replace('If Final Vestige receives approval','After you purchase'),
  'lost commission word': a.replace('may earn a commission','may share our thoughts'),
  'new form': a.replace('</main>','<form action="/new-lead"></form></main>'),
  'script injection': a.replace('</main>','<script>alert(1)</script></main>'),
  'autoplay movie': a.replace('</main>','<video autoplay></video></main>'),
  'unproven cure': a.replace('</main>','<p>proven to cure insomnia</p></main>'),
  'video player': a.replace('</main>','<iframe src="https://video.example"></iframe></main>')
};
for(const [label,unsafe] of Object.entries(mutantCases))ok(!sourceSafety(unsafe),'unsafe alteration rejected: '+label);
console.log('Mind R397 STATIC source tests: '+checks+' PASS; unsafe fixtures '+Object.keys(mutantCases).length+' rejected.');
console.log('NOT tested: real browser/WCAG, video playback, installed WordPress, merchant authorization/transactions, Jetpack, tracking/paid revenue.');
