'use strict';
/**
 * Simulates WordPress' documented wp_insert_post -> wp_unslash behavior.
 * The actual integrate() source is used with only the release-candidate
 * assembler/hasher replaced by synthetic fixtures. Does not run WordPress.
 */
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const os=require('node:os');
const path=require('node:path');
const cp=require('node:child_process');
const Module=require('node:module');
const crypto=require('node:crypto');
const hash=x=>crypto.createHash('sha256').update(x,'utf8').digest('hex');
const REVIEWED='a868423c033a179d1821bb9eb1cf7b5c6c07106097e18cce6afe58b79f908cc1';
const FRAGMENT='/wordpress/wp-content/plugins/fv-ex2-playground/assets/wordpress-page-fragment.review-only.html';
const PLUGIN='/wordpress/wp-content/plugins/fv-ex2-playground/fv-ex2-playground.php';
const preserved='<!-- wp:html --><div data-fv-home-flagship="true" data-example="\\u0026">'+ '--i:'.repeat(72) + '<p>C:\\history\\evidence</p></div><!-- /wp:html -->\n<!-- wp:jetpack/subscriptions /-->';
const receipt={preserved_margin_items:72,original_jetpack_blocks:1,original_focus_links:2,chapter_anchors:7,evidence_cases:3};
const origLoad=Module._load;
Module._load=function(id,parent,isMain){
 if(id.endsWith('/release-candidate/assemble_homepage_migration.cjs')) return {assemble:()=>({candidate:preserved,receipt})};
 if(id.endsWith('/release-candidate/verify_homepage_migration.cjs')) return {SHA:s=>s==='trusted_fragment'?REVIEWED:hash(s)};
 return origLoad.apply(this,arguments);
};
let integrate;
try {({integrate}=require('./make_integrated_playground_bridge.cjs'));}finally{Module._load=origLoad;}
const page='<p>PUBLIC PAGE 6</p>'.repeat(100);
function base(){
 const steps=[{step:'defineWpConfigConsts',consts:{WP_ENVIRONMENT_TYPE:'local',FV_EX2_ALLOW_LOCAL_REVIEW:true}},
 {step:'installTheme',themeData:{url:'/private/assembler.zip'}}];
 steps.push({step:'writeFile',path:FRAGMENT,data:'trusted_fragment'});
 steps.push({step:'writeFile',path:PLUGIN,data:'function fv_ex2_integrity(){} function fv_ex2_ready(){}'});
 for(let i=0;i<13;i++)steps.push({step:'writeFile',path:'/private/local-'+i,data:'x'});
 steps.push({step:'runPHP',code:"<?php if (!fv_ex2_ready()) throw new Exception('missing stage gate');"});
 steps.push({step:'setSiteOptions',options:{show_on_front:'page'}});
 assert.equal(steps.length,19);return {steps};
}
const rawPhp=integrate(base(),page,hash(page)).blueprint.steps.find(x=>x.step==='runPHP').code;
const phpBody=rawPhp.replace(/^<\?php require_once '\/wordpress\/wp-load\.php';/, '');
function phpRun(body,{tamper=false}={}){
 const work=fs.mkdtempSync(path.join(os.tmpdir(),'fv-wp-post-save-'));
 const lines=[
 '<?php',
 "function fv_ex2_ready(){return true;}",
 "function get_stylesheet(){return 'assembler';}",
 "function wp_get_environment_type(){return 'local';}",
 "function wp_slash($s){return addslashes($s);}",
 "function is_wp_error($x){return false;}",
 "function parse_blocks($s){return array(array('blockName'=>'core/html','innerHTML'=>'data-fv-home-flagship'));}",
 "function wp_insert_post($p,$strict=false){",
 " $stored=stripslashes($p['post_content']);",
 tamper?" $stored=str_replace('data-fv-home-flagship','tampered',$stored);":"",
 " $GLOBALS['saved']=$stored;return 84;}",
 "function get_post_field($key,$id,$context){return $GLOBALS['saved'];}",
 "function update_option($key,$value){return true;}",
 body,
 "if ($GLOBALS['saved']!==$raw) {echo 'UNDETECTED_CORRUPTION';} else {echo 'INTEGRITY_OK';}"
 ];
 const file=path.join(work,'probe.php'); fs.writeFileSync(file,lines.join('\n'));
 try{
  const lint=cp.spawnSync('php',['-l',file],{encoding:'utf8'});assert.equal(lint.status,0,lint.stderr||lint.stdout);
  return cp.spawnSync('php',[file],{encoding:'utf8'});
 }finally{fs.rmSync(work,{recursive:true,force:true})}
}
test('bootstrap slashes Gutenberg input and verifies exact persisted SHA-256',()=>{
 assert.match(rawPhp,/wp_slash\(\$raw\)/);
 assert.match(rawPhp,/get_post_field\('post_content',\$id,'raw'\)/);
 assert.match(rawPhp,/hash_equals\('[0-9a-f]{64}',hash\('sha256',\$fv_stored\)\)/);
});
test('PHP 8.4 WordPress-like insert preserves slashes with wp_slash',()=>{
 const p=phpRun(phpBody);assert.equal(p.status,0,p.stderr);assert.match(p.stdout,/INTEGRITY_OK/);
});
test('missing wp_slash causes a WordPress-like unslash to fail closed',()=>{
 const p=phpRun(phpBody.replace("wp_slash($raw)","$raw"));
 assert.notEqual(p.status,0);assert.match(p.stderr,/Gutenberg content changed during WordPress save/);
});
test('server-side post-content mutation independently fails closed',()=>{
 const p=phpRun(phpBody,{tamper:true});assert.notEqual(p.status,0);
 assert.match(p.stderr,/Gutenberg content changed during WordPress save/);
});
test('RED: old bootstrap would silently accept altered stored Gutenberg',()=>{
 const prior=phpBody.replace('wp_slash($raw)','$raw')
 .replace(/^.*\$fv_stored=get_post_field.*\n/m,'')
 .replace(/^.*Gutenberg content changed during WordPress save.*\n/m,'');
 const p=phpRun(prior);assert.equal(p.status,0,p.stderr);
 assert.match(p.stdout,/UNDETECTED_CORRUPTION/);
});
