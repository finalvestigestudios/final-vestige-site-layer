/** Reproducible offline verification: node --test verify.test.mjs
 * Must run after: node build.mjs. All tests use local source, synthetic events, and no network.
 * Browser/WCAG and WordPress staging require separate independent review.
 */
import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';
import {ATTRIBUTION_ENABLED,REPORT_MIN_COUNT,recordLiveEvent,validateSyntheticEvent,aggregateSyntheticRows} from './privacy-attribution.mjs';
const here=dirname(fileURLToPath(import.meta.url));
const read=n=>readFileSync(join(here,n),'utf8');
const A=read('zen12-a-wordpress-draft.html');
const B=read('zen12-b-wordpress-draft.html');
const offline=read('offline-b-with-real-video.html');
const article=read('investigation-wordpress-draft.html');
const core=read('zen12-guide-core.html');
const css=read('pilot.css');
const poster=read('film-poster.svg');
const vtt=read('film-captions.vtt');
const matrix=read('claims-permissions-matrix.csv');
const stripFilm=h=>h.replace(/<figure class="fv51-film" data-variant-element="optional-film"[\s\S]*?<\/figure>/,'');
const normalizeVariant=h=>stripFilm(h).replace('data-variant="B"','data-variant="A"').replace(/<!-- UNPUBLISHED .*? -->/,'');
function assertSafeBuyerPage(html){
  assert.match(html,/disabled\s+aria-describedby="fv51-commission-disclosure fv51-offer-state"/);
  assert.match(html,/If you purchase through a future approved link/);
  assert.match(html,/<p class="fv51-disclosure" id="fv51-commission-disclosure">/);
  const posD=html.indexOf('id="fv51-commission-disclosure"'),posB=html.indexOf('<button type="button" disabled');
  assert.ok(posB>posD && posB-posD<800,'near-offer disclosure');
  assert.doesNotMatch(html,/<a\b[^>]*href=["'][^"']*(?:zen12\.com|inspire3\.com)/i,'no activated merchant links');
  assert.doesNotMatch(html,/<(?:script|iframe|form)\b/i,'no tracker/embed/duplicate opt-in');
  assert.doesNotMatch(html,/autoplay\b/i,'no forced video');
  assert.doesNotMatch(html,/data:application\/javascript|javascript:/i,'no JS URLs');
}
test('build variants have one and same substantive seller-matched core',()=>{
  assert.ok(A.includes(core),'A must contain exact shared guide core');
  assert.equal(normalizeVariant(B),normalizeVariant(A),'B text same as A except optional educational film');
  assert.equal(normalizeVariant(offline),normalizeVariant(A),'offline player text same as A');
});
test('both WordPress drafts have zero active commerce or subscriber implementation',()=>{
  for(const x of [A,B]) assertSafeBuyerPage(x);
});
test('unsafe mutations caught: active merchant URL, script, forced playback, absent disabled CTA',()=>{
  const mutations=[
    B.replace('disabled aria-describedby','aria-describedby'),
    B.replace('</section>\n</section>','<a href="https://zen12.com/getstarted">Buy</a></section>\n</section>'),
    B.replace('<!-- UNPUBLISHED','<script>fetch("https://example.com")</script><!-- UNPUBLISHED'),
    B.replace('data-variant="B"','autoplay data-variant="B"'),
    B.replace('If you purchase through a future approved link','Commission disclosure redacted')
  ];
  for(const [i,m] of mutations.entries()){
    assert.throws(()=>assertSafeBuyerPage(m),'mutant '+i+' was not caught');
  }
});
test('film version is an honest offline/noninteractive concept on WordPress',()=>{
  assert.match(B,/data-variant-element="optional-film"/);
  assert.match(B,/no play button/);
  assert.doesNotMatch(B,/<video\b/i);
  assert.match(B,/<details><summary>Read the complete film transcript/);
  assert.match(offline,/<video controls playsinline preload="none"/);
  assert.match(offline,/<track src="film-captions.vtt"/);
  assert.doesNotMatch(offline,/autoplay\b/i);
});
test('captions are timed through exact 40-second end and poster has accessible description',()=>{
  assert.ok(vtt.startsWith('WEBVTT'));
  assert.equal((vtt.match(/-->/g)||[]).length,6);
  assert.match(vtt,/00:00:32\.000 --> 00:00:40\.000/);
  assert.match(poster,/<title id="ttl">/);
  assert.match(poster,/<desc id="desc">/);
  assert.doesNotMatch(poster,/<script|xlink:href="http|<foreignObject/i);
});
test('specific science and product safeguards in article and guide',()=>{
  assert.match(article,/Raymond, Shapiro and Karen Arnell|Jane Raymond, Kimron Shapiro/);
  assert.match(article,/three months of intensive/i);
  assert.doesNotMatch(article,/zen12|inspire3/i);
  assert.match(core,/Final Vestige does not adopt those efficacy claims/i);
  assert.match(core,/We have not purchased, downloaded or audited/i);
  assert.match(core,/free Seven Day Focus Fieldbook/i);
  assert.match(core,/first 6 levels|First 6/);
  assert.match(core,/48 MP3s|<td>48<\/td>/);
  assert.ok((matrix.match(/\n"P\d{3}",/g)||[]).length>=40,'matrix must have at least 40 audit decisions');
});
test('CSS scopes and progressive enhancement affordances are present',()=>{
  assert.match(css,/\.fv51-pilot/);
  assert.match(css,/:focus-visible/);
  assert.match(css,/max-width:480px/);
  assert.match(css,/prefers-reduced-motion:reduce/);
  assert.match(css,/min-height:44px/);
  assert.match(A,/href="#fv51-guide-title"/);
});
test('telemetry is hard-OFF and rejects identifying/unknown fields',()=>{
  assert.equal(ATTRIBUTION_ENABLED,false);
  assert.equal(recordLiveEvent({ip:'203.0.113.5',email:'x@example.org'}).recorded,false);
  const good={event:'guide_view',channel:'tiktok',variant:'B',topic:'zen12'};
  assert.equal(validateSyntheticEvent(good).ok,true);
  for(const key of ['email','ip','referrer','url','userId','timestamp','utm_source']){
    assert.equal(validateSyntheticEvent({...good,[key]:'private'}).ok,false,key);
  }
  assert.equal(validateSyntheticEvent({...good,channel:'bob'}).ok,false);
  assert.equal(validateSyntheticEvent({}).ok,false);
});
test('synthetic reports suppress all small cells under 20',()=>{
  const e={event:'guide_view',channel:'tiktok',variant:'B',topic:'zen12'};
  assert.equal(REPORT_MIN_COUNT,20);
  assert.deepEqual(aggregateSyntheticRows(Array.from({length:19},()=>e)),[]);
  assert.deepEqual(aggregateSyntheticRows(Array.from({length:20},()=>e)),[{cell:'guide_view|tiktok|B|zen12',count:20}]);
  assert.throws(()=>aggregateSyntheticRows([{...e,email:'x@example.com'}]));
});
