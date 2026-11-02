// Reproducible native Node 22 suite: node --test mind/attentional-blink-meditation-r63/verify.test.mjs
// Also requires ffprobe for the separately rendered offline preview; media is NOT hosted.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {ACTIVE,acceptSynthetic,aggregateSynthetic,emitLiveEvent} from './privacy-attribution.mjs';
const f=n=>readFileSync(new URL(n,import.meta.url),'utf8');
const article=f('./investigation.md'), core=f('./guide-core.html'), a=f('./offer-a-text.blocks.html'), b=f('./offer-b-video.blocks.html'),hub=f('./mind-hub-noncanonical.blocks.html'),vtt=f('./film-captions.vtt'),src=f('./source-register.csv'),claims=f('./claim-permission-matrix.csv'),renderer=f('./render_film.py');
const merchantAnchor=/<a\b[^>]*\bhref\s*=\s*["'][^"']*(?:zen12\.com|inspire3\.com|affiliates\.inspire3\.com|hypnosislive\.com|brainwaveshots\.com)[^"']*["']/i;
const nativeDisabled=page=>/<button\b(?=[^>]*\sdisabled(?:\s|=|>))[^>]*>Seller link withheld — approval pending<\/button>/.test(page);
const nearDisclosure=page=>{const x=page.indexOf('Affiliate disclosure:'),y=page.indexOf('<button',x);return x>=0&&y>x&&y-x<600};
const safePage=page=>!merchantAnchor.test(page)&&!/<script\b|<iframe\b|<form\b|autoplay\b|<video\b/i.test(page);
const captionMatches=()=>[...vtt.matchAll(/(\d\d:\d\d:\d\d\.\d{3}) --> (\d\d:\d\d:\d\d\.\d{3})/g)];
test('original investigation substantive, sourced, no commerce',()=>{
 assert.ok(article.split(/\s+/).length>2000);
 for(const term of ['Raymond','Shapiro','Arnell','Chun','Potter','Hommel','Akyürek','Slagter','17 participants','23 novices','336 milliseconds','672 milliseconds','Whitfield','Puységur'])assert.ok(article.includes(term),term);
 assert.doesNotMatch(article,/Zen12|Inspire3|affiliate|checkout/i);
 assert.doesNotMatch(article,/Zainal, N\. H\./);
});
test('source-based guide has seller-versus-evidence and consumer boundary',()=>{
 assert.ok(core.length>10000);
 for(const term of ['twelve-minute','twelve','forty-eight','48 MP3','Slagter','mobile','SMS','refund','FTC','NCCIH','not a test of Zen12','no live purchasing link'])assert.ok(core.toLowerCase().includes(term.toLowerCase()),term);
});
test('A and B contain identical substantive guide once',()=>{
 assert.equal(a.split(core).length,2);assert.equal(b.split(core).length,2);
 assert.ok(b.indexOf('<h1')<b.indexOf('<aside class="fv63-film"'));
});
test('near-CTA conspicuous disclosure and native disabled control',()=>{
 for(const x of [a,b]){assert.ok(nativeDisabled(x),'native disabled');assert.ok(nearDisclosure(x),'adjacent disclosure');assert.match(x,/may earn a commission at no additional cost/i);}
});
test('all page candidates forbid seller links, tracking and duplicate signup',()=>{
 for(const x of [a,b,hub])assert.ok(safePage(x),'unapproved external destination or active mechanism');
 for(const x of [a,b,hub])assert.doesNotMatch(x,/@import|fonts\.googleapis|localStorage|sessionStorage|document\.cookie|fetch\(|XMLHttpRequest|sendBeacon/i);
});
test('B provides static visual and transcript; no false player',()=>{
 assert.match(b,/<svg viewBox=/);assert.match(b,/<details open>/);assert.match(b,/<summary>/);
 assert.match(b,/The image is a static poster/);assert.doesNotMatch(b,/<video\b|preload=/);
 assert.doesNotMatch(a,/<svg viewBox=/);
});
test('VTT cues contiguous with exactly 40s timeline',()=>{
 const m=captionMatches();assert.equal(m.length,6);
 assert.equal(m[0][1],'00:00:00.000');assert.equal(m.at(-1)[2],'00:00:40.000');
 for(let i=1;i<m.length;i++)assert.equal(m[i-1][2],m[i][1]);
});
test('film source is original and frame-count governed',()=>{
 assert.match(renderer,/nb_frames=480/);assert.match(renderer,/duration=40.000000/);
 assert.match(renderer,/480/);assert.match(renderer,/def wave/);assert.match(renderer,/not a validated RSVP experiment/i);
});
test('source register and permission matrix sufficiently granular',()=>{
 assert.equal(src.trim().split('\n').length-1,21);
 assert.equal(claims.trim().split('\n').length-1,50);
 for(const s of ['NOT SUBSTANTIATED','NOT VERIFIED','PROHIBITED','FALSE','SELLER DESCRIBED'])assert.ok(claims.includes(s),s);
 for(const s of ['zen12.com/hnp','zen12.com/getstarted','inspire3.com/privacy','ftc.gov','pubmed.ncbi.nlm.nih.gov/34350544'])assert.ok(src.includes(s),s);
});
test('new hub not canonical and keeps published Focus only',()=>{
 assert.match(hub,/PR #172/);assert.match(hub,/NOT PUBLISHED/);
 assert.match(hub,/https:\/\/finalvestige.com\/focus\//);
 assert.match(hub,/https:\/\/finalvestige.com\/free-resources\/puysegurs-animal-magnetism-files\//);
 assert.doesNotMatch(hub,/<a[^>]+href=["'][^"']*\/mind\//i);
});
test('offline privacy rejects PII and small aggregates',()=>{
 assert.equal(ACTIVE,false);assert.equal(emitLiveEvent({}),false);
 const good={variant:'video',topic:'zen12-guide',event:'outbound-intent',source:'tiktok'};
 assert.equal(acceptSynthetic(good),true);
 for(const bad of [{...good,email:'example@invalid.test'}, {...good,ip:'127.0.0.1'}, {...good,referrer:'/secret?email=x'}, {...good,event:'purchase'}, {...good,source:'unique-user'},null,[]])assert.equal(acceptSynthetic(bad),false);
 assert.equal(aggregateSynthetic(Array(19).fill(good)).length,0);
 assert.equal(aggregateSynthetic(Array(20).fill(good))[0].count,20);
});
test('unsafe transformations fail their dedicated safety check',()=>{
 const candidates=[
 a.replace(' disabled>','>'),
 a.replace('Affiliate disclosure:','Disclosure removed:'),
 a.replace('Seller link withheld — approval pending','<a href="https://zen12.com/getstarted">BUY</a>'),
 a.replace('</section>','<form action="/capture"><input type="email"></form></section>'),
 b.replace('</section>','<script src="https://example.com/track.js"></script></section>'),
 b.replace('<details open>','<details hidden>'),
 a.replace(core,'REDACTED'),
 b.replace(core,'REDACTED')
 ];
 assert.equal(nativeDisabled(candidates[0]),false);
 assert.equal(nearDisclosure(candidates[1]),false);
 assert.equal(safePage(candidates[2]),false);
 assert.equal(safePage(candidates[3]),false);
 assert.equal(safePage(candidates[4]),false);
 assert.doesNotMatch(candidates[5],/<details open>/);
 assert.equal(candidates[6].includes(core),false);
 assert.equal(candidates[7].includes(core),false);
});
