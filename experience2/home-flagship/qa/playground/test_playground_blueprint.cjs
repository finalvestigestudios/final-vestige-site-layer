'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const os=require('node:os');
const path=require('node:path');
const crypto=require('node:crypto');
const {execFileSync}=require('node:child_process');
const {generate,IMAGES,THEME_URL}=require('./make_playground_blueprint.cjs');
const {ASSETS,makeBundle}=require('../release-candidate/build_release_review.cjs');
function withStage(fn){
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'fv-stage-tests-'));
 try{return fn(path.join(dir,'blueprint.json'))}finally{fs.rmSync(dir,{recursive:true,force:true})}
}
function blueprint(output){
 const receipt=generate(output);
 const data=JSON.parse(fs.readFileSync(output,'utf8'));
 return {receipt,data};
}
test('same exact source: all 11 review files inline with SHA-256 attestations',()=>withStage(out=>{
 const {data,receipt}=blueprint(out);
 assert.equal(receipt.sourceGitBlob,'70ebe0d8e122048343c99a3c6adc6f7ac498ed7f');
 assert.equal(data.steps.length,19);
 const assets=data.steps.filter(s=>s.step==='writeFile'&&typeof s.data==='string'&&s.path.includes('/assets/'));
 assert.equal(assets.length,11);
 const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'fv-rebuild-'));
 try{
 const manifest=makeBundle(path.resolve(__dirname,'../..'),path.join(tmp,'release'));
 for(const step of assets) {
   const name=path.basename(step.path);
   const digest=crypto.createHash('sha256').update(step.data).digest('hex');
   assert.equal(digest,manifest.files[name].sha256,name);
 }
 }finally{fs.rmSync(tmp,{recursive:true,force:true})}
}));
test('real official Assembler theme and three public, exact media originals only',()=>withStage(out=>{
 const {data}=blueprint(out);
 const theme=data.steps.find(x=>x.step==='installTheme');
 assert.equal(theme.themeData.url,THEME_URL);
 assert.equal(theme.options.activate,true);
 const images=data.steps.filter(x=>x.step==='writeFile'&&typeof x.data==='object'&&x.path.includes('/media/'));
 assert.equal(images.length,3);
 assert.deepEqual(images.map(x=>x.data.url),IMAGES.map(x=>x[1]));
 assert(images.every(x=>x.data.resource==='url'));
}));
test('private-stage guard and WordPress-native shortcode are hard prerequisites',()=>withStage(out=>{
 const {data}=blueprint(out);
 const constants=data.steps.find(x=>x.step==='defineWpConfigConsts');
 assert.deepEqual(constants.consts,{WP_ENVIRONMENT_TYPE:'local',FV_EX2_ALLOW_LOCAL_REVIEW:true});
 const plugin=data.steps.find(x=>x.path?.endsWith('/fv-ex2-playground.php')).data;
 for(const marker of ['fv_ex2_safe_stage()',"wp_get_environment_type() === 'local'",'fv_ex2_integrity()',"add_shortcode('fv_ex2_stage_home'",'getimagesize','plugins_url','preg_replace_callback']) {
   assert(plugin.includes(marker),marker);
 }
 const run=data.steps.at(-1);
 assert.equal(run.step,'runPHP');
 assert(run.code.includes("get_stylesheet() !== 'assembler'"));
 assert(run.code.includes('wp_insert_post'));
 assert(run.code.includes("update_option('page_on_front'"));
}));
test('no production-data import, external services, newsletter payload, or injected merchant scripts',()=>withStage(out=>{
 const {data}=blueprint(out);
 assert(!data.steps.some(x=>['importWxr','importWordPressFiles','runSql','installPlugin'].includes(x.step)));
 const j=JSON.stringify(data);
 assert(!j.includes('inspire3.com'));
 assert(!j.includes('jetpack/subscriptions'));
 assert(!j.includes('mailchimp.com'));
 assert(!j.includes('contact@example.com'));
}));
test('fails closed when blueprint path already exists',()=>withStage(out=>{
 generate(out);
 assert.throws(()=>generate(out),/refusing overwrite/);
}));
test('generated WordPress renderer parses as PHP 8+',()=>withStage(out=>{
 const {data}=blueprint(out);
 const plugin=data.steps.find(x=>x.path?.endsWith('/fv-ex2-playground.php')).data;
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'fv-stage-php-'));
 try{
  const p=path.join(dir,'review.php');
  fs.writeFileSync(p,plugin);
  const res=execFileSync('php',['-l',p],{encoding:'utf8'});
  assert(res.includes('No syntax errors detected'));
 } finally{fs.rmSync(dir,{recursive:true,force:true})}
}));
