'use strict';
// R126: source contracts and mutation tests, not proof of full browser acceptance.
// Run: node --test experience2/apollo-creator-bridge/test_r126_campaign_privacy_contract.cjs
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const html=fs.readFileSync(path.join(__dirname,'landing-preview.html'),'utf8');
const runner=fs.readFileSync(path.join(__dirname,'qa_r113_print.py'),'utf8');
const anchors=(source)=>[...source.matchAll(/<a\b[^>]*>/gi)].map(m=>m[0]);
const nasa=(source)=>anchors(source).filter(a=>/href="https:\/\/(?:www|sma)\.nasa\.gov\//i.test(a));
function validNasaLinks(source){
  const links=nasa(source);
  return links.length===22 && links.every(a=>/\brel="noreferrer noopener"/i.test(a));
}
function safeExternalHosts(source){
  return anchors(source).filter(a=>/\bhref="https:\/\//i.test(a)).every(a=>{
    const m=a.match(/href="([^"]+)"/i);
    const url=new URL(m[1]);
    return url.protocol==='https:' && ['www.nasa.gov','sma.nasa.gov','finalvestige.com'].includes(url.hostname);
  });
}
test('all 22 NASA source exits prevent campaign referrer leakage',()=>{
  assert.equal(nasa(html).length,22);
  assert.ok(validNasaLinks(html));
});
test('source privacy check fails if one NASA noreferrer is removed',()=>{
  const damaged=html.replace(' rel="noreferrer noopener"','');
  assert.equal(validNasaLinks(damaged),false);
});
test('no source link points to an unreviewed external host',()=>{
  assert.ok(safeExternalHosts(html));
  assert.equal(safeExternalHosts(html.replace('https://www.nasa.gov/image-detail/','https://clicktracker.example/image-detail/')),false);
});
test('one free classroom CTA retains explicit hash route without JavaScript',()=>{
  const ctas=anchors(html).filter(a=>a.includes('data-fv-primary-cta'));
  assert.equal(ctas.length,1);
  assert.match(ctas[0],/href="#classroom-preview"/);
  assert.match(html,/<section id="classroom-preview" tabindex="-1"/);
  assert.match(html,/without signup/i);
});
test('no visitor beacon, storage, checkout or remote script inserted',()=>{
  assert.doesNotMatch(html,/<form\b|<iframe\b|<script\b[^>]*src=|navigator\.sendBeacon|\bXMLHttpRequest\b|\blocalStorage\b|\bdocument\.cookie\b/i);
  assert.doesNotMatch(html,/<a\b[^>]*href="https:\/\/(?:www\.)?payhip\./i);
});
test('canonical real-document navigation is still required',()=>{
  assert.match(runner,/page\.goto\(url,wait_until='load',timeout=15000\)/);
  assert.doesNotMatch(runner,/page\.set_content\(/);
  assert.match(runner,/EXACT_GIT_HEAD/);
});
test('synthetic source ID, standard organic UTMs and their survival are tested',()=>{
  assert.match(runner,/utm_source=youtube&utm_medium=organic_social&utm_campaign=history_pilot_2026_11&utm_content=apollo1_youtube_lf_qa001/);
  assert.match(runner,/page\.evaluate\('location\.search'\)=='\?'\+campaign/);
  assert.match(runner,/page\.url==destination\+'#classroom-preview'/);
});
test('read-only browser request and storage checks are fail-closed',()=>{
  assert.match(runner,/page\.on\('request',lambda req: requests\.append\(req\.url\)\)/);
  assert.match(runner,/automatic_third_party_requests':0/);
  assert.match(runner,/document\.cookie===/);
  assert.match(runner,/localStorage\.length===0 && sessionStorage\.length===0/);
  assert.match(runner,/unexpected network request during landing/);
});
test('campaign replay occurs in two mobile/desktop real browser contexts',()=>{
  assert.match(runner,/for width in \(390,1440\):/);
  assert.match(runner,/audit_campaign_boundary\(browser,target,record\)/);
  assert.match(runner,/len\(record\['campaign_boundary'\]\)==2/);
});
test('NASA photo custody remains provisional and reproductions absent',()=>{
  assert.match(html,/S67-19766/);
  assert.match(html,/0\/6/);
  assert.equal((html.match(/data-fv-student-photo="0[1-6]"/g)||[]).length,6);
  assert.doesNotMatch(html,/<img\b|<picture\b/i);
});
test('future merchant acceptance cannot be inferred from this staging page',()=>{
  assert.match(html,/product hypothesis/i);
  assert.match(runner,/synthetic_browser_smoke_not_a_conversion/);
  assert.doesNotMatch(html,/<a\b[^>]*href="[^"]*checkout/i);
});
