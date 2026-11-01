'use strict';
/** Execute the local Gutenberg render hook in PHP; WordPress itself is not installed. */
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const cp = require('node:child_process');
const {BRIDGE} = require('./make_integrated_playground_bridge.cjs');

function runPhpContract() {
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'fv-jetpack-local-'));
  try {
    fs.mkdirSync(path.join(dir,'assets'));
    const flagship='<div data-fv-home-flagship>Reviewed Gutenberg content</div>';
    fs.writeFileSync(path.join(dir,'assets','wordpress-page-fragment.review-only.html'),flagship);
    const src=[
      '<?php',
      "$GLOBALS['front']=true;$GLOBALS['local']=true;$GLOBALS['ready']=true;",
      'function add_filter($name,$cb,$priority,$argc) {$GLOBALS["render_callback"]=$cb;}',
      'function is_front_page(){return $GLOBALS["front"];}', 
      'function fv_ex2_safe_stage(){return $GLOBALS["local"];}', 
      'function fv_ex2_ready(){return $GLOBALS["ready"];}', 
      "function do_shortcode($x){return 'RENDERED_FLAGSHIP';}",
      BRIDGE,
      "$c=$GLOBALS['render_callback'];",
      "$jetpack=['blockName'=>'jetpack/subscriptions'];",
      "$html=['blockName'=>'core/html'];",
      "$tests=[];",
      "$tests['local_jetpack']=$c('', $jetpack);",
      "$GLOBALS['local']=false;$tests['production_jetpack']=$c('ORIGINAL_JETPACK_FORM', $jetpack);",
      "$GLOBALS['local']=true;$GLOBALS['front']=false;$tests['other_page_jetpack']=$c('ORIGINAL_JETPACK_FORM', $jetpack);",
      "$GLOBALS['front']=true;$tests['other_block']=$c('OTHER_CONTENT', ['blockName'=>'core/paragraph']);",
      "$tests['flagship']=$c('"+flagship+"',$html);",
      "$tests['tampered']=$c('<div data-fv-home-flagship>Altered</div>',$html);",
      "$GLOBALS['ready']=false;$tests['unready']=$c('"+flagship+"',$html);",
      "echo json_encode($tests,JSON_THROW_ON_ERROR);"
    ].join('\n');
    const script=path.join(dir,'fixture.php');
    fs.writeFileSync(script,src);
    const lint=cp.spawnSync('php',['-l',script],{encoding:'utf8'});
    assert.equal(lint.status,0,lint.stderr||lint.stdout);
    const run=cp.spawnSync('php',[script],{encoding:'utf8'});
    assert.equal(run.status,0,run.stderr||run.stdout);
    return JSON.parse(run.stdout);
  } finally {fs.rmSync(dir,{recursive:true,force:true});}
}

const results=runPhpContract();
test('Local signup preview is explicit and labelled as nonfunctional',()=>{
  assert.match(results.local_jetpack,/data-fv-subscriptions-local-only="true"/);
  assert.match(results.local_jetpack,/hosted verification required/);
  assert.match(results.local_jetpack,/no email addresses are collected/);
});
test('Preview never presents a fake working signup control',()=>{
  assert.doesNotMatch(results.local_jetpack,/<(?:form|input|button)\b|action=|type="email"/i);
});
test('Preview cannot include tracking, scripts, external links or merchant redirection',()=>{
  assert.doesNotMatch(results.local_jetpack,/<(?:script|iframe|img|a)\b|https?:\/\//i);
});
test('Outside local stage the existing WordPress/Jetpack HTML is unchanged',()=>{
  assert.equal(results.production_jetpack,'ORIGINAL_JETPACK_FORM');
});
test('Non-home pages and unrelated Gutenberg blocks are unchanged',()=>{
  assert.equal(results.other_page_jetpack,'ORIGINAL_JETPACK_FORM');
  assert.equal(results.other_block,'OTHER_CONTENT');
});
test('Seven-chapter source hook still renders its independently guarded fragment',()=>{
  assert.equal(results.flagship,'RENDERED_FLAGSHIP');
});
test('Changed or unreadied archival fragment still fails closed',()=>{
  assert.match(results.tampered,/Local stage CLOSED/);
  assert.match(results.unready,/Local stage CLOSED/);
});
test('One render_block hook; no second callback ordering dependency',()=>{
  assert.equal((BRIDGE.match(/add_filter\('render_block'/g)||[]).length,1);
});