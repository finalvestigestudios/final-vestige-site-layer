import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname,join} from 'node:path';
import {ACTIVE,validateSyntheticEvent,collectRealEvent,synthesizeAggregate} from './privacy-attribution.mjs';
const root=dirname(fileURLToPath(import.meta.url));
const get=p=>readFileSync(join(root,p),'utf8');
const a=get('offer-a-text.blocks.html'),b=get('offer-b-film.blocks.html'),core=get('guide-core.html'),inv=get('investigation.md'),hub=get('mind-hub-noncanonical.blocks.html'),vtt=get('captions.vtt'),claims=JSON.parse(get('claims-and-release.json'));
function audit(html) {
  assert.match(html,/<button\s+type="button" disabled\b/);
  assert.match(html,/Final Vestige may earn a commission at no additional cost to you/);
  const disclosure=html.indexOf('Final Vestige may earn a commission');
  const button=html.indexOf('Visit the official Zen12 offer — not yet enabled');
  assert.ok(disclosure>=0 && button>=0 && Math.abs(disclosure-button)<450);
  assert.doesNotMatch(html,/<a\b[^>]*href="https?:\/\/(?:www\.)?(?:zen12\.com\/(?:hnp|getstarted)|affiliates\.inspire3\.com)/i);
  assert.doesNotMatch(html,/<(?:script|iframe|form|input|video|audio)\b/i);
  assert.doesNotMatch(html,/\b(?:autoplay|dataLayer|gtag\(|fbq\(|localStorage|sessionStorage)\b/i);
  assert.match(html,/@media\(max-width:780px\)/);
  assert.match(html, /@media\(prefers-reduced-motion:reduce\)/);
  assert.match(html, /@media\(forced-colors:active\)/);
  assert.match(html, /:focus-visible/);
  assert.match(html, /https:\/\/finalvestige\.com\/focus\//);
}
test('original independent article is substantive and appropriately separated',()=>{
  assert.ok(inv.split(/\s+/).length>1500);
  for(const p of ['Loftus','Palmer','Gabbert','Schincariol','2003','2024','Puységur'])assert.ok(inv.includes(p));
  assert.doesNotMatch(inv,/(Zen12|Inspire3|Hypnosis Live).{0,100}(buy|affiliate|recommend)/i);
  assert.match(inv,/The Glass That Wasn't There/);
});
test('text and film variants embed byte-identical named-product guide',()=>{
  assert.ok(core.length>8000);
  assert.equal(a.split(core).length,2);
  assert.equal(b.split(core).length,2);
  assert.ok(core.includes('zen12.com/hnp'));
  assert.ok(core.includes('zen12.com/getstarted'));
  audit(a);audit(b);
});
test('film is optional, described honestly and provides no-JS transcript',()=>{
  assert.match(b, /<svg[\s\S]*?role="img"/);
  assert.match(b, /Playback is <strong>not<\/strong> enabled/);
  assert.match(b, /id="r68-film-transcript"/);
  assert.match(b, /Skip directly to the film transcript/);
  assert.equal((b.match(/<time>/g)||[]).length,6);
  assert.doesNotMatch(a,/id="r68-film-transcript"/);
});
test('caption timeline continuous, exact 40 seconds',()=>{
  const all=[...vtt.matchAll(/(\d\d):(\d\d):(\d\d)\.\d{3} --> (\d\d):(\d\d):(\d\d)\.\d{3}/g)];
  assert.equal(all.length,6);
  const toSec=m=>Number(m[1])*3600+Number(m[2])*60+Number(m[3]);
  const toSec2=m=>Number(m[4])*3600+Number(m[5])*60+Number(m[6]);
  assert.equal(toSec(all[0]),0);assert.equal(toSec2(all.at(-1)),40);
  all.forEach((m,i)=>{assert.ok(toSec2(m)>toSec(m));if(i)assert.equal(toSec(m),toSec2(all[i-1]));});
});
test('claims release matrix fails closed and uses only actual source references',()=>{
 assert.equal(claims.affiliate_link,null);assert.equal(claims.release_status,'HARD_HOLD');
 assert.equal(claims.visitor_measurement_enabled,false);
 assert.ok(claims.decisions.length>=40);
 for(const r of claims.decisions){assert.ok(r.id&&r.decision&&r.claim);for(const s of r.sources){assert.match(s.url,/^https:\/\//);}}
 const necessary=['publisher_specific_permission_missing','unsupported_do_not_assert'];
 for(const x of necessary)assert.ok(claims.decisions.some(r=>r.decision===x));
});
test('hub preserves one existing Focus funnel; no new forms',()=>{
 assert.match(hub,/https:\/\/finalvestige\.com\/focus\//);
 assert.match(hub,/puysegurs-animal-magnetism-files/);
 assert.doesNotMatch(hub,/<(?:script|iframe|form|input)\b/);
 assert.doesNotMatch(hub,/href="https?:\/\/zen12\.com\/getstarted/);
 assert.match(hub,/PR #172/);
});
test('synthetic-only aggregate validation rejects PII',()=>{
 assert.equal(ACTIVE,false);
 assert.throws(()=>collectRealEvent());
 assert.throws(()=>validateSyntheticEvent({topic:'memory',channel:'tiktok',variant:'a',event:'offer_intent',email:'x@y.z'}));
 assert.throws(()=>validateSyntheticEvent({topic:'memory',channel:'tiktok',variant:'a',event:'offer_intent',referrer_url:'https://example.com'}));
 assert.throws(()=>validateSyntheticEvent({topic:'memory',channel:'tiktok',variant:'a',event:'offer_intent',id:'user1'}));
 const e={topic:'memory',channel:'tiktok',variant:'b',event:'offer_intent'};
 assert.deepEqual(synthesizeAggregate(Array.from({length:19},()=>e)),[]);
 assert.deepEqual(synthesizeAggregate(Array.from({length:20},()=>e)),[{cohort:'memory|tiktok|offer_intent|b',count:20}]);
});
