'use strict';
const {test}=require('node:test');
const a=require('node:assert/strict');
const fs=require('node:fs');
const os=require('node:os');
const path=require('node:path');
const cp=require('node:child_process');
const {SHA}=require('../release-candidate/verify_homepage_migration.cjs');
const {integrate,BRIDGE}=require('./make_integrated_playground_bridge.cjs');
function baseBlueprint(){
  if(process.env.FV_TEST_BASE_BLUEPRINT)return JSON.parse(fs.readFileSync(process.env.FV_TEST_BASE_BLUEPRINT,'utf8'));
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'fv-stage-base-'));
  try{const file=path.join(dir,'base.json');require('./make_playground_blueprint.cjs').generate(file);return JSON.parse(fs.readFileSync(file,'utf8'));}
  finally{fs.rmSync(dir,{recursive:true,force:true});}
}
const base=baseBlueprint();
const margins=Array.from({length:72},(_,i)=>'<span class="fv-margin-strip__item" style="--i:'+i+'">Record '+i+'</span>').join('');
const before='<!-- wp:html --><div class="fv-margin-strip">'+margins+'</div><!-- /wp:html -->';
const hero='<!-- wp:html --><section class="fv-studios-hero" aria-labelledby="fv-studios-title"><h1 id="fv-studios-title">Find what others miss.</h1></section><!-- /wp:html -->';
const focus='<!-- wp:html --><div><a href="/focus/">Fieldbook</a><a class="fv-focus-cta__art" href="/focus/" aria-hidden="true" tabindex="-1">Cover</a></div><!-- /wp:html -->';
const jetpack='<!-- wp:group --><p>Dispatch</p><!-- wp:jetpack/subscriptions /--><!-- /wp:group -->';
const legacy=[before,hero,focus,jetpack].join('\n');
const run=(old=legacy,blueprint=base,digest=SHA(old))=>integrate(blueprint,old,digest);
const result=run();
test('integrated public Gutenberg source keeps 72 records, Jetpack, Focus and seven chapters',()=>{
  a.equal(result.receipt.margins,72);a.equal(result.receipt.jetpack,1);a.equal(result.receipt.focus,2);
  a.equal(result.receipt.chapters,7);a.equal(result.receipt.cases,3);
  a.ok(result.candidate.includes(before));a.ok(result.candidate.includes(focus));a.ok(result.candidate.includes(jetpack));
  a.ok(!result.candidate.includes('fv-studios-hero'));a.equal((result.candidate.match(/<h1\b/g)||[]).length,1);
});
test('only local gated Assembler+15 original writes, no integrated page in public plugin assets',()=>{
  const b=result.blueprint;a.equal(b.steps.length,19);a.equal(b.steps.filter(x=>x.step==='writeFile').length,15);
  a.ok(b.steps[1].themeData.url.endsWith('/assembler.zip'));
  a.ok(!b.steps.some(x=>x.path?.includes('integrated-homepage') || ['runSql','importWxr','importWordPressFiles'].includes(x.step)));
  const bootstrap=b.steps.find(x=>x.step==='runPHP').code;
  const match=bootstrap.match(/base64_decode\('([^']+)'/);a.ok(match);
  a.equal(Buffer.from(match[1],'base64').toString('utf8'),result.candidate);
  a.ok(bootstrap.includes('fv_ex2_ready()'));
});
test('reject stale public source, changed fragment, duplicate hero and unsafe base',()=>{
  a.throws(()=>run(legacy+' ',base,SHA(legacy)),/SHA-256 required/);
  const duplicate=legacy+'\n'+hero;a.throws(()=>run(duplicate),/no unique/);
  const p=structuredClone(base);p.steps.find(x=>x.path?.endsWith('wordpress-page-fragment.review-only.html')).data+=' ';
  a.throws(()=>run(legacy,p),/fingerprint changed/);
  const unsafe=structuredClone(base);unsafe.steps[0].consts.WP_ENVIRONMENT_TYPE='production';a.throws(()=>run(legacy,unsafe),/local-only/);
});
test('PHP lint of generated plugin and local WordPress bootstrap',()=>{
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'fv-integrated-lint-'));
 try{const snippets=[result.blueprint.steps.find(x=>x.path?.endsWith('/fv-ex2-playground.php')).data,result.blueprint.steps.find(x=>x.step==='runPHP').code];
 for(let i=0;i<snippets.length;i++){const p=path.join(dir,'stage'+i+'.php');fs.writeFileSync(p,snippets[i]);const v=cp.spawnSync('php',['-l',p],{encoding:'utf8'});a.equal(v.status,0,v.stderr||v.stdout);}}
 finally{fs.rmSync(dir,{recursive:true,force:true});}
});
test('executed PHP bridge rejects changed evidence, missing media readiness and wrong block',()=>{
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'fv-bridge-php-'));
 try{
  const src=base.steps.find(x=>x.path?.endsWith('/wordpress-page-fragment.review-only.html')).data;
  fs.mkdirSync(path.join(dir,'assets'));fs.writeFileSync(path.join(dir,'assets','wordpress-page-fragment.review-only.html'),src);
  const code=["<?php $cb=null;$ready=true;$front=true;",
   "function add_filter($n,$fn,$p,$a){$GLOBALS['cb']=$fn;}","function is_front_page(){return $GLOBALS['front'];}","function fv_ex2_ready(){return $GLOBALS['ready'];}","function do_shortcode($s){return 'RENDERED';}",BRIDGE,
   "$s=file_get_contents(__DIR__.'/assets/wordpress-page-fragment.review-only.html');",
   "$r=array();$r[]=$cb($s,array('blockName'=>'core/html'));",
   "$r[]=$cb(str_replace('THE VICTORY POINT NOTE','EDITED',$s),array('blockName'=>'core/html'));",
   "$ready=false;$r[]=$cb($s,array('blockName'=>'core/html'));$ready=true;",
   "$r[]=$cb($s,array('blockName'=>'core/paragraph'))===$s;",
   "echo json_encode($r);"].join('\n');
  const p=path.join(dir,'qa.php');fs.writeFileSync(p,code);const x=cp.spawnSync('php',[p],{encoding:'utf8'});a.equal(x.status,0,x.stderr);
  const r=JSON.parse(x.stdout);a.equal(r[0],'RENDERED');a.match(r[1],/CLOSED/);a.match(r[2],/CLOSED/);a.equal(r[3],true);
 }finally{fs.rmSync(dir,{recursive:true,force:true});}
});
