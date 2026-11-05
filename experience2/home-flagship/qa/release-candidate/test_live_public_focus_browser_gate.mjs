import test from 'node:test';
import assert from 'node:assert/strict';
import {VIEWPORTS,CHAPTERS,validateFocusGeometry,pathOnly}
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
  assert.equal(pathOnly('not a valid //url'),'invalid-url');
});
