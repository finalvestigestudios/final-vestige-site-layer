// Node >=20: node --test mind/cocktail-party-zen12-r62/verify.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
const read=name=>readFileSync(new URL('./'+name,import.meta.url),'utf8');
const [article,core,a,b,hub,vtt,claims,sources,privacy]=['investigation.md','guide-core.html','offer-a-text-only.blocks.html','offer-b-video-concept.blocks.html','mind-hub-concept.blocks.html','film-captions.vtt','claim-approval-matrix.csv','source-register.csv','privacy-attribution.js'].map(read);
const noCommerce=page=>!/<a\b[^>]*href=["'][^"']*(zen12|inspire3|affiliates\.inspire3|hypnosislive|brainwaveshots)/i.test(page)&&!/<(?:script|iframe|form)\b/i.test(page)&&!/<video\b[^>]*autoplay/i.test(page);
const nativeDisabled=page=>/<button\b[^>]*\sdisabled(?:\s|=|>)[^>]*>Seller link withheld/.test(page);
const closeDisclosure=page=>{const d=page.indexOf('Affiliate disclosure:');const btn=page.indexOf('<button',d);return d>=0&&btn>d&&btn-d<900;};
const noPiiCode=text=>!/(document\.cookie|localStorage|sessionStorage|navigator\.sendBeacon|fetch\(|XMLHttpRequest|email\s*:|ip_address|userAgent)/i.test(text);
test('research article has primary citations and no seller naming',()=>{
 assert.match(article,/Cherry.*1953/);assert.match(article,/Moray.*1959/);assert.match(article,/1995/);assert.match(article,/2021/);assert.match(article,/34\.6%/);assert.match(article,/29%/);
 assert.doesNotMatch(article,/\bZen12\b|\bInspire3\b|affiliate|checkout/i);
 assert.ok(article.split(/\s+/).length>1700);
});
test('A/B substantive guide byte-for-byte identical',()=>{
 assert.ok(core.length>10000);
 assert.equal(a.split(core).length,2);assert.equal(b.split(core).length,2);
 assert.ok(a.indexOf(core)>=0&&b.indexOf(core)>=0);
});
test('independently useful seller-matched buyer guide',()=>{
 for(const s of ['twelve-minute','twelve levels','four listening styles','48 MP3','Seller','NCCIH','no-purchase','privacy','unverified']){}
 for(const s of ['twelve','levels','48 MP3','mobile','money-back','NCCIH','FTC','Seller'])assert.ok(core.includes(s),s);
 assert.match(core,/The most attractive claim is also the least established/);
 assert.match(core,/not identified independent/);
});
test('every variant has native disabled control and adjacent disclosure',()=>{
 for(const page of [a,b]){assert.ok(nativeDisabled(page));assert.ok(closeDisclosure(page));assert.match(page,/commission at no additional cost/i);}
});
test('no live affiliate merchant or leaking remote embeds',()=>{
 for(const page of [a,b,hub])assert.ok(noCommerce(page));
 for(const page of [a,b])assert.doesNotMatch(page,/rel=["'](?:sponsored|noopener)["']\s+href=/i);
});
test('no duplicated opt-in, scripts, iframe, autoplay, remote CSS/fonts',()=>{
 for(const page of [a,b,hub]){assert.doesNotMatch(page,/<form\b|<script\b|<iframe\b|autoplay|@import|https?:\/\/[^"'\s]*\.(?:js|woff)/i); }
});
test('B optional short has complete no-JS transcript and static art',()=>{
 assert.match(b,/<details open>/);assert.match(b,/<summary>/);assert.match(b,/<svg\b/);assert.match(b,/no hosted player/i);
 assert.doesNotMatch(b,/<video\b/);assert.ok(!a.includes('<svg'));
});
test('source-controlled caption cues contiguous at exactly 40 seconds',()=>{
 const lines=[...vtt.matchAll(/(\d\d:\d\d:\d\d\.\d\d\d) --> (\d\d:\d\d:\d\d\.\d\d\d)/g)];
 assert.equal(lines.length,6);
 assert.equal(lines[0][1],'00:00:00.000');assert.equal(lines.at(-1)[2],'00:00:40.000');
 for(let i=1;i<lines.length;i++)assert.equal(lines[i-1][2],lines[i][1]);
});
test('hub is noncanonical and only links to published first party',()=>{
 assert.match(hub,/PR #172/);assert.match(hub,/NOT PUBLISHED/);
 assert.match(hub,/https:\/\/finalvestige\.com\/focus\//);
 assert.doesNotMatch(hub,/<a[^>]+href=["'][^"']*\/mind\//i);
});
test('source register 22 data rows, decision matrix 56 rows',()=>{
 assert.equal(sources.trim().split('\n').length-1,22);
 assert.equal(claims.trim().split('\n').length-1,56);
 assert.match(claims,/NOT SUBSTANTIATED/);assert.match(claims,/NOT VERIFIED/);assert.match(claims,/PROHIBITED/);
});
test('privacy model is non-instrumenting and rejects unknown identifiers',async()=>{
 assert.ok(noPiiCode(privacy));const mod=await import('data:text/javascript,'+encodeURIComponent(privacy));
 assert.equal(mod.ACTIVE,false);
 assert.equal(mod.acceptSynthetic({variant:'text',topic:'attention',event:'outbound-intent'}),true);
 assert.equal(mod.acceptSynthetic({variant:'text',topic:'attention',event:'outbound-intent',email:'person@example.invalid'}),false);
 assert.equal(mod.acceptSynthetic({variant:'text',topic:'attention',event:'purchase'}),false);
 assert.equal(mod.aggregateSynthetic(Array(19).fill({variant:'text',topic:'attention',event:'outbound-intent'})).length,0);
 assert.equal(mod.aggregateSynthetic(Array(20).fill({variant:'text',topic:'attention',event:'outbound-intent'}))[0].count,20);
});
test('safety checker detects deliberate unsafe mutations',()=>{
 assert.equal(noCommerce(b.replace('</main>','<a href="https://zen12.com/hnp">Buy</a></main>')),false);
 assert.equal(noCommerce(a.replace('</main>','<script src="https://evil.invalid/t.js"></script></main>')),false);
 assert.equal(nativeDisabled(a.replace(' type="button" disabled',' type="button"')),false);
 assert.equal(closeDisclosure(a.replace('Affiliate disclosure:','Commercial info:')),false);
});
