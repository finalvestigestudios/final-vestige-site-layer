import test from 'node:test';
import assert from 'node:assert/strict';
import {VIEWPORTS,CHAPTERS,ARCHIVE_FILES,imageAssetName,auditedArchives,validateFocusGeometry,pathOnly}
  from './live_public_focus_browser_gate.mjs';

const valid=(mode='strip')=>({
  visible:true,hit:true,mode,
  box:{x:10,y:95,width:155,height:48},
  href:'/focus/'
});
test('at least seven viewport admissions include the 1279/1280 CTA switch',()=>{
  assert.deepEqual(VIEWPORTS,[320,390,768,1279,1280,1440,1920]);
});
test('exact published seven chapter ids retained',()=>{
  assert.equal(CHAPTERS.length,7);
  assert.equal(new Set(CHAPTERS).size,7);
  assert.ok(CHAPTERS.includes('fv-hf-franklin'));
});
test('one unobstructed 44px visible above-fold CTA accepted',()=>{
  assert.equal(validateFocusGeometry([valid()],390,900).hitCount,1);
});
test('hidden CTA never counts',()=>{
  assert.equal(validateFocusGeometry([{...valid(),visible:false}],390,900).hitCount,0);
});
test('occluded CTA never counts',()=>{
  assert.equal(validateFocusGeometry([{...valid(),hit:false}],390,900).hitCount,0);
});
test('CTA below first viewport never counts',()=>{
  assert.equal(validateFocusGeometry([{
    ...valid(),box:{x:10,y:899,width:155,height:48}}],390,900).hitCount,0);
});
test('offscreen and clipped CTA never counts',()=>{
  assert.equal(validateFocusGeometry([{
    ...valid(),box:{x:-1,y:95,width:155,height:48}}],390,900).hitCount,0);
});
test('visual but sub-44px CTA never counts as usable target',()=>{
  assert.equal(validateFocusGeometry([{
    ...valid(),box:{x:10,y:95,width:120,height:39}}],390,900).hitCount,0);
});
test('mobile strip and desktop navigation are distinct modes',()=>{
  assert.deepEqual(validateFocusGeometry([valid('strip')],390,900).modes,['strip']);
  assert.deepEqual(validateFocusGeometry([valid('nav')],1440,900).modes,['nav']);
});
test('sanitize URLs, never report query/fragment/foreign hostname',()=>{
  assert.equal(pathOnly('https://finalvestige.com/focus/?asset_id=private#x'),'/focus/');
  assert.equal(pathOnly('https://notfinalvestige.com/focus/'),'external-host');
  assert.equal(pathOnly('http://[bad'),'invalid-url');
});

const liveArchiveDom=ARCHIVE_FILES.map(asset=>({
  srcHost:'i0.wp.com',srcPath:'/finalvestige.com/wp-content/uploads/2026/08/'+asset,
  complete:true,naturalWidth:960,naturalHeight:700
}));
const liveArchiveTransfers=ARCHIVE_FILES.map(asset=>({
  asset,http:200,bytes:12000,firstParty:false
}));
test('exact published Apollo/Franklin/NYPL archive assets are required',()=>{
  assert.deepEqual(ARCHIVE_FILES,[
    's67-19766.webp','franklinexpeditionnote.jpg',
    'edit-017-v02-nypl-5003296-original.jpg']);
  assert.ok(auditedArchives(liveArchiveDom,liveArchiveTransfers)
    .every(r=>r.dom&&r.decoded&&r.transfer));
});
test('zero archive images cannot yield a browser PASS',()=>{
  assert.ok(auditedArchives([],[]).every(r=>!r.dom&&!r.decoded&&!r.transfer));
});
test('one missing archive fails even when other images load',()=>{
  assert.equal(auditedArchives(liveArchiveDom.slice(1),liveArchiveTransfers)[0].dom,false);
});
test('decoded pixels and metadata alone do not establish HTTP image bytes',()=>{
  assert.ok(auditedArchives(liveArchiveDom,
    liveArchiveTransfers.map(x=>({...x,bytes:0}))).every(r=>!r.transfer));
});
test('403 HTTP, missing decode, or zero dimension fail closed',()=>{
  assert.equal(auditedArchives(liveArchiveDom,
    liveArchiveTransfers.map(x=>({...x,http:403})))[0].transfer,false);
  assert.equal(auditedArchives(liveArchiveDom.map(x=>({...x,naturalWidth:0})),
    liveArchiveTransfers)[0].decoded,false);
});
test('trust only real FV uploads or the exact i0.wp.com WP CDN path',()=>{
  assert.equal(imageAssetName('https://finalvestige.com/wp-content/uploads/2026/08/s67-19766.webp'),'s67-19766.webp');
  assert.equal(imageAssetName('https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/Franklinexpeditionnote.jpg?fit=644%2C1024'),'franklinexpeditionnote.jpg');
  assert.equal(imageAssetName('https://evil.example/wp-content/uploads/2026/08/s67-19766.webp'),null);
  assert.equal(imageAssetName('https://i0.wp.com/not-finalvestige.com/wp-content/uploads/2026/08/s67-19766.webp'),null);
  assert.equal(imageAssetName('invalid://['),null);
});
