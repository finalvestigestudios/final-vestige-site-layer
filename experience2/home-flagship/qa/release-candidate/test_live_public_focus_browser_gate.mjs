import test from 'node:test';
import assert from 'node:assert/strict';
import {VIEWPORTS,CHAPTERS,ARCHIVE_FILES,imageAssetName,imageKey,auditedArchives,validateFocusGeometry,pathOnly}
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

const cdn=a=>'https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/'+a+'?fit=768%2C600&ssl=1';
const archives=ARCHIVE_FILES.map(asset=>({
  srcHost:'i0.wp.com',srcPath:'/finalvestige.com/wp-content/uploads/2026/08/'+asset,
  sourceKey:imageKey(cdn(asset)),isArchive:true,alt:'Evidence caption',
  complete:true,naturalWidth:960,naturalHeight:700
}));
const network=ARCHIVE_FILES.map((asset,i)=>({
  asset,sourceKey:archives[i].sourceKey,http:200,bytes:12000
}));
const ok=(dom=archives,tx=network)=>auditedArchives(dom,tx)
  .every(r=>r.dom&&r.described&&r.decoded&&r.transfer);
test('all three exact archival exhibits require decoded positive HTTP bytes',()=>{
  assert.equal(ARCHIVE_FILES.length,3);
  assert.equal(ok(),true);
});
test('empty DOM, missing exhibit, duplicate or unmarked decoy fail',()=>{
  assert.equal(ok([],[]),false);
  assert.equal(ok(archives.slice(1)),false);
  assert.equal(ok([...archives,archives[0]]),false);
  assert.equal(ok(archives.map((d,i)=>i===0?{...d,isArchive:false}:d)),false);
});
test('same filename other responsive derivative is not a matching transfer',()=>{
  const alter=network.map((t,i)=>i===0?{...t,
    sourceKey:imageKey(cdn(ARCHIVE_FILES[0]).replace('768%2C600','300%2C233'))}:t);
  assert.equal(ok(archives,alter),false);
});
test('same filename other allowed origin is not a matching transfer',()=>{
  const alter=network.map((t,i)=>i===0?{...t,
    sourceKey:imageKey('https://finalvestige.com/wp-content/uploads/2026/08/'+ARCHIVE_FILES[0])}:t);
  assert.equal(ok(archives,alter),false);
});
test('no description, missing decode, failed status, zero bytes all fail closed',()=>{
  assert.equal(ok(archives.map((d,i)=>i===1?{...d,alt:'   '}:d)),false);
  assert.equal(ok(archives.map((d,i)=>i===1?{...d,naturalWidth:0}:d)),false);
  assert.equal(ok(archives,network.map((d,i)=>i===1?{...d,http:403}:d)),false);
  assert.equal(ok(archives,network.map((d,i)=>i===1?{...d,bytes:0}:d)),false);
});
test('non-HTTPS, bad CDN path, userinfo, foreign host blocked',()=>{
  for(const s of [
    'http://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/s67-19766.webp',
    'https://bad.example/wp-content/uploads/2026/08/s67-19766.webp',
    'https://i0.wp.com/not-finalvestige.com/wp-content/uploads/2026/08/s67-19766.webp',
    'https://user:pass@i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/s67-19766.webp'
  ])assert.equal(imageAssetName(s),null);
});
test('fingerprint distinguishes responsive src and is SHA-256 format',()=>{
  const x=imageKey(cdn(ARCHIVE_FILES[0]));
  const y=imageKey(cdn(ARCHIVE_FILES[0]).replace('768%2C600','300%2C233'));
  assert.match(x,/^[a-f0-9]{64}$/);
  assert.notEqual(x,y);
});
test('72 Margins are admission requirements for both JS/no-JS',async()=>{
  const {readFile}=await import('node:fs/promises');
  const {dirname,join}=await import('node:path');
  const {fileURLToPath}=await import('node:url');
  const s=await readFile(join(dirname(fileURLToPath(import.meta.url)),
    'live_public_focus_browser_gate.mjs'),'utf8');
  assert.match(s,/state\.marginCount===72&&state\.marginSequential&&state\.marginNonempty/);
  assert.match(s,/isArchive:el\.hasAttribute\('data-fv-archive-img'\)/);
});
