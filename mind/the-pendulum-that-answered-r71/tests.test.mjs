import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {join,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {ENABLED,normalizeSyntheticEvent,previewAggregatesForOfflineReview} from './attribution.mjs';
const here=dirname(fileURLToPath(import.meta.url));
const load=p=>readFileSync(join(here,p),'utf8');
const a=load('zen12-a-text.blocks.html');
const b=load('zen12-b-film.blocks.html');
const core=load('zen12-guide-core.html');
const article=load('investigation.md');
const matrix=JSON.parse(load('claim-matrix.json'));
const vtt=load('captions.vtt');
for(const [name,page] of [['A',a],['B',b]]){
  test(name+' contains unmodified independent core',()=>assert.ok(page.includes(core)));
  test(name+' genuine disabled button and near-CTA disclosure',()=> {
    assert.match(page,/<button[^>]*type="button"[^>]*disabled[^>]*>/);
    const disclosure=page.lastIndexOf('Final Vestige may earn a commission');
    const button=page.lastIndexOf('<button type="button" disabled');
    assert.ok(disclosure>=0 && button>disclosure && button-disclosure<400);
  });
  test(name+' no active merchant conversion links',()=>assert.doesNotMatch(page,/<a\b[^>]*href="https:\/\/(?:zen12|inspire3|hypnosislive|brainwaveshots)\.com/i));
  test(name+' no script/forms/iframes/media embeds',()=>assert.doesNotMatch(page,/<(?:script|form|iframe|video|audio)\b/i));
  test(name+' no autoplay attribute',()=>assert.doesNotMatch(page,/<[^>]+\sautoplay(?:\s|>|=)/i));
  test(name+' preserves only one existing Focus destination',()=>assert.match(page,/https:\/\/finalvestige\.com\/focus\//));
}
test('B has transcript without JS',()=>{assert.match(b,/<details>/);assert.match(b,/35–40 s/)});
test('B explicitly refuses unhosted playback',()=>assert.match(b,/Playback disabled in this unpublished candidate/));
test('A is text only without optional film block',()=>assert.doesNotMatch(a,/data-optional-video/));
test('B has film placeholder',()=>assert.match(b,/data-optional-video="awaiting-first-party-host"/));
test('investigation is free of seller purchase links',()=>assert.doesNotMatch(article,/https:\/\/(?:zen12|inspire3|hypnosislive|brainwaveshots)\.com/i));
test('investigation cites actual scholarly work',()=>{for(const doi of ['10.1080/00221309.1976.9710871','10.1093/nc/nix014','10.1080/00029157.2021.2010641'])assert.ok(article.includes(doi))});
test('film caption file spans exact 40 seconds',()=>{assert.match(vtt,/^WEBVTT/);assert.match(vtt,/00:00:35\.000 --> 00:00:40\.000/)});
test('all claims have linked source IDs',()=>{const ids=new Set(matrix.sources.map(s=>s.id));for(const c of matrix.claims){assert.ok(c.source_ids.length>0,c.id);for(const id of c.source_ids)assert.ok(ids.has(id),id)}});
test('partner activation is hard-held',()=>{assert.equal(matrix.activation.enabled,false);assert.equal(matrix.activation.approved_affiliate_url,null);assert.equal(matrix.activation.founder_release_approval,false)});
test('attribution disabled',()=>{assert.equal(ENABLED,false);assert.equal(normalizeSyntheticEvent({page:'zen12-guide',variant:'B',channel:'tiktok',event:'cta-intent'}),null)});
test('aggregation rejects unexpected PII fields',()=>{const good={page:'zen12-guide',variant:'A',channel:'direct',event:'view'};const events=Array(19).fill(good);assert.equal(previewAggregatesForOfflineReview(events).length,0);assert.equal(previewAggregatesForOfflineReview([...events,good]).length,1);assert.equal(previewAggregatesForOfflineReview([...events,{...good,email:'example@example.com'}]).length,0)});
test('no live links from A/B use unverified earning destinations',()=>{assert.doesNotMatch(a+b,/data-affiliate-activation="active"/);assert.match(a+b,/hard-hold/)});
