import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {dirname} from 'node:path';
import {ATTRIBUTION_ENABLED, validateSyntheticEvent, recordLiveEvent, aggregateSyntheticEvents} from './privacy-attribution.mjs';

const dir=dirname(fileURLToPath(import.meta.url));
const read=f=>readFileSync(join(dir,f),'utf8');
const core=read('zen12-guide-core.html');
const a=read('zen12-a-wordpress-draft.html');
const b=read('zen12-b-wordpress-draft.html');
const article=read('investigation-wordpress-draft.html');
const hub=read('mind-hub-alternative-draft.html');
const csv=read('claims-permissions-matrix.csv');
const vtt=read('film-captions.vtt');
const vtxt=read('film-script.md');
const all=[a,b];
const good={event:'guide_view',topic:'zen12_guide',variant:'text',channel:'direct'};

test('A/B preserve full byte-identical editorial guide and differentiated optional film',()=>{
  assert.ok(core.length>12000);
  assert.equal(a.split(core).length,2);
  assert.equal(b.split(core).length,2);
  assert.equal((a.match(/class="fv-m52-guidecore"/g)||[]).length,1);
  assert.equal((b.match(/class="fv-m52-guidecore"/g)||[]).length,1);
  assert.ok(!a.includes('fv-m52-video'));
  assert.ok(b.includes('fv-m52-video') && b.includes('m52-poster-caption'));
  assert.ok(b.includes('Read the complete 40-second transcript'));
});

test('inert affiliate controls with adjacent material-connection disclosures',()=>{
  for (const page of all){
    assert.match(page, /<button type="button" disabled aria-disabled="true">/);
    assert.match(page,/may earn a commission at no additional cost to you/i);
    assert.match(page,/No earning link is active here/i);
    const block=page.match(/<div class="fv-m52-cta"[\s\S]*?<\/div>/)?.[0];
    assert.ok(block && block.indexOf('may earn a commission')<block.indexOf('<button'));
    assert.ok(block.indexOf('may earn a commission')>=0);
  }
});

test('none of the consumer candidates enable merchant links or tracking',()=>{
  for (const page of [...all,hub,article]){
    assert.doesNotMatch(page,/<a\b[^>]*href=['"][^'"]*(?:zen12\.com|affiliates\.inspire3|hypnosislive\.com)/i);
    assert.doesNotMatch(page,/<script\b|<form\b|<iframe\b|\bautoplay\b\s*=|\bonclick\s*=/i);
    assert.doesNotMatch(page,/www\.googletagmanager\.com|google-analytics\.com|facebook\.com\/tr/i);
    assert.doesNotMatch(page,/UNPUBLISHED-REVIEW-ASSET-NOT-HOSTED/);
  }
});

test('article is scientifically sourced and commercially independent',()=>{
  assert.match(article, /10\.3758\/BF03208840/);
  assert.match(article, /10\.1111\/j\.1467-9280\.1997\.tb00427\.x/);
  assert.match(article,/only about half/i);
  assert.match(article,/social.group/i);
  assert.doesNotMatch(article, /Zen12|Inspire3|affiliate|purchase\s+now/i);
  assert.match(article,/not a validated replication/i);
});

test('seller claims are not passed off as product proof',()=>{
  for(const page of all){
    assert.match(page,/have not bought, downloaded, listened to, clinically tested/i);
    assert.match(page,/not independently substantiated|not substantiated/i);
    assert.match(page,/did not test Zen12/i);
    assert.match(page,/cannot attest/i);
    assert.match(page,/twelve-minute sound-format|twelve-minute format|twelve-minute listening/i);
  }
});

test('original film is optional, captions cover exactly 40 seconds and no unsupported experiment claim',()=>{
  const cues=[...vtt.matchAll(/(\d\d:\d\d:\d\d\.\d\d\d) --> (\d\d:\d\d:\d\d\.\d\d\d)/g)];
  assert.equal(cues.length,6);
  assert.equal(cues[0][1],'00:00:00.000');
  assert.equal(cues.at(-1)[2],'00:00:40.000');
  assert.match(vtxt,/not a reenactment/i);
  assert.doesNotMatch(b,/<video\b[^>]*autoplay/i);
  assert.match(b,/Static review poster|static HTML-only diagram|static HTML diagram/i);
});

test('responsive no-JS, mobile accessibility and one existing Focus link',()=>{
  for(const page of [a,b,hub]){
    assert.match(page,/<h1\b/i);
    assert.match(page,/:focus-visible/);
    assert.match(page,/@media\(prefers-reduced-motion:reduce\)/);
    assert.doesNotMatch(page,/<input\b|type=["']email["']/i);
    assert.ok(page.includes('https://finalvestige.com/focus/'));
  }
  assert.match(a,/overflow-x:auto/);
  assert.match(b,/<summary>Read the complete 40-second transcript<\/summary>/);
});

test('claims source matrix records explicit authorization gaps',()=>{
  const lines=csv.trim().split('\n');
  assert.ok(lines.length>=50);
  assert.match(csv,/NOT_VERIFIED/);
  assert.match(csv,/UNSUBSTANTIATED_HEALTH/);
  assert.match(csv,/FALSE_INFERENCE/);
  assert.match(csv,/HARD_HOLD/);
  assert.match(csv,/Written|written|Channel permission|Channel/);
});

test('privacy fails closed and rejects personal fields with no telemetry emitter',()=>{
  assert.equal(ATTRIBUTION_ENABLED,false);
  assert.equal(recordLiveEvent(good).recorded,false);
  assert.deepEqual(validateSyntheticEvent(good),good);
  for(const x of [
    {...good,ip:'203.0.113.1'}, {...good,email:'reader@example.test'},
    {...good,full_referrer:'https://example.test/?token=private'},
    {...good,session:'abc'}, {...good,channel:'search?campaign=abc'},
    {...good,topic:'zen12_guide&email=person'}, {}, null, []]){
    assert.throws(()=>validateSyntheticEvent(x));
  }
  assert.deepEqual(aggregateSyntheticEvents(Array.from({length:19},()=>good)),[]);
  assert.deepEqual(aggregateSyntheticEvents(Array.from({length:20},()=>good)),[{group:'guide_view|zen12_guide|text|direct',count:20}]);
  assert.throws(()=>aggregateSyntheticEvents([good],19));
});

test('adversarial unsafe edits would be detected by base guards',()=>{
  const unsafe=(x)=>/<a\b[^>]*href=['"][^'"]*(?:zen12\.com|affiliates\.inspire3|hypnosislive\.com)/i.test(x)
                    || /<script\b|<form\b|<iframe\b|\bautoplay\b\s*=|\bonclick\s*=/i.test(x)
                    || !/<button type="button" disabled aria-disabled="true">/.test(x)
                    || !/may earn a commission at no additional cost to you/i.test(x);
  assert.equal(unsafe(a),false);
  for(const altered of [
    a.replace('disabled aria-disabled="true"',''),
    a.replace('may earn a commission at no additional cost to you',''),
    a+'<a href="https://zen12.com/hnp">merchant checkout</a>',
    a+'<script>fetch("/track")</script>',
    a+'<form action="/join"></form>',
    a+'<iframe src="https://example.org/embed"></iframe>',
    a+'<img autoplay="autoplay">'
  ]) assert.equal(unsafe(altered),true);
});
