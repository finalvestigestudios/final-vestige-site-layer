'use strict';
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs=require('node:fs');
const os=require('node:os');
const path=require('node:path');
const cp=require('node:child_process');
const {verifyTemplate,stageTemplate,FRONT_WIDTH,LOCAL_WIDTH,SHA}=require('./stage_page_template_parity.cjs');
const sample='<!-- wp:template-part {"slug":"header","theme":"assembler"} /-->\n'+
'<!-- wp:group {"tagName":"main"} -->\n<main class="wp-block-group">\n'+
'<!-- wp:post-content {"className":"fv-post-content","layout":{"type":"constrained","contentSize":"760px","wideSize":"1440px"}} /-->\n'+
'<!-- wp:html --><style> :root{--fv-gold:#c7a66c;} '+FRONT_WIDTH+' </style><!-- /wp:html -->\n'+
'</main><!-- /wp:group -->\n<!-- wp:template-part {"slug":"footer","theme":"assembler"} /-->\n'+
'<!-- Public template presentation tokens only. -->\n'.repeat(30);
const digest=SHA(sample);
function blueprint(){const s=Array.from({length:19},()=>({step:'writeFile',path:'/dummy',data:'local'}));s[0]={step:'defineWpConfigConsts',consts:{WP_ENVIRONMENT_TYPE:'local',FV_EX2_ALLOW_LOCAL_REVIEW:true}};s[1]={step:'installTheme',themeData:{url:'/private/assembler.zip'}};s[18]={step:'setSiteOptions',options:{blogname:'local'}};s[2]={step:'runPHP',code:"<?php require_once '/wordpress/wp-load.php';\nif (!fv_ex2_ready() || get_stylesheet() !== 'assembler' || wp_get_environment_type() !== 'local') throw new Exception('closed');\n$id=wp_insert_post(array('post_title'=>'FV LOCAL Integrated Homepage Review','post_status'=>'publish','post_type'=>'page','post_content'=>$raw));"};return {steps:s}}
function phpProbe(code,termFailure=false){const dir=fs.mkdtempSync(path.join(os.tmpdir(),'fv-template-'));try{
const snippet=code.slice(code.indexOf('// FV LOCAL TEMPLATE PARITY:'),code.indexOf("$id=wp_insert_post(array('post_title'=>'FV LOCAL Integrated Homepage Review'"));
const src=[
'<?php',
"function get_stylesheet(){return \'assembler\';}",
"function wp_get_environment_type(){return \'local\';}",
'function fv_ex2_safe_stage(){return true;}',
'function wp_slash($s){return $s;}',
'function is_wp_error($x){return false;}',
"function wp_insert_post($x,$strict){$GLOBALS['insert']=$x;return 123;}",
"function wp_set_object_terms($id,$term,$taxonomy){return "+(termFailure?'array()':'array(17)')+';}',
"function wp_get_block_template($slug,$type){return (object)array('content'=>$GLOBALS['insert']['post_content']);}",
snippet,
"echo json_encode(array('post_type'=>$GLOBALS['insert']['post_type'],'post_name'=>$GLOBALS['insert']['post_name'],'tagged'=>strpos($GLOBALS['insert']['post_content'],'body.home')!==false));"
].join('\n');
const f=path.join(dir,'test.php');fs.writeFileSync(f,src);const lint=cp.spawnSync('php',['-l',f],{encoding:'utf8'});assert.equal(lint.status,0,lint.stderr||lint.stdout);const run=cp.spawnSync('php',[f],{encoding:'utf8'});return {status:run.status,stdout:run.stdout,stderr:run.stderr};
}finally{fs.rmSync(dir,{recursive:true,force:true})}}

test('accept authentic page-template structural contract and adapt only local front selector',()=>{const q=verifyTemplate(sample,digest);assert.ok(q.localTemplate.includes(LOCAL_WIDTH));assert.ok(!q.localTemplate.includes(FRONT_WIDTH));assert.equal(q.original_sha256,digest)});
test('reject stale/missing template SHA-256',()=>{assert.throws(()=>verifyTemplate(sample,'0'.repeat(64)),/SHA-256/);assert.throws(()=>verifyTemplate(sample,''),/SHA-256/)});
test('reject a source without the exact production full-width override',()=>{assert.throws(()=>verifyTemplate(sample.replace(FRONT_WIDTH,'.page-id-6 .fv-post-content>*{max-width:760px}'),SHA(sample.replace(FRONT_WIDTH,'.page-id-6 .fv-post-content>*{max-width:760px}'))),/full-bleed/)});
test('reject layout drift to stock/other constrained widths',()=>{const s=sample.replace('"contentSize":"760px"','"contentSize":"620px"');assert.throws(()=>verifyTemplate(s,SHA(s)),/760\/1440/)});
test('reject active form/script/user markup in a purported public template',()=>{for (const injected of ['<script>alert(1)</script>','<form action="/submit"></form>','<!-- wp:jetpack/subscriptions /-->']){const s=sample+injected;assert.throws(()=>verifyTemplate(s,SHA(s)),/forbidden/)}});
test('exact local Blueprint shape and step/file counts unchanged',()=>{const q=stageTemplate(blueprint(),sample,digest);assert.equal(q.blueprint.steps.length,19);assert.equal(q.blueprint.steps.filter(s=>s.step==='writeFile').length,15);assert.equal(q.receipt.actual_wordpress_rendered,false);assert.ok(q.blueprint.steps[2].code.includes('FV LOCAL TEMPLATE PARITY'))});
test('requires staged local approval, Assembler ZIP and bootstrap',()=>{for(const [step,change] of [[0,z=>z.consts.WP_ENVIRONMENT_TYPE='production'],[1,z=>z.themeData.url='/other.zip'],[2,z=>z.code='<?php echo 42;']]){const b=blueprint();change(b.steps[step]);assert.throws(()=>stageTemplate(b,sample,digest),/HOLD/)}});
test('refuses duplicate template import or additional database/WXR import',()=>{const a=stageTemplate(blueprint(),sample,digest);assert.throws(()=>stageTemplate(a.blueprint,sample,digest),/already added/);const b=blueprint();b.steps[3]={step:'runSql',sql:'x'};assert.throws(()=>stageTemplate(b,sample,digest),/database\/user import/)});
test('real PHP 8.4 accepts generated local wp_template insertion and verifies binding',()=>{const p=phpProbe(stageTemplate(blueprint(),sample,digest).blueprint.steps[2].code);assert.equal(p.status,0,p.stderr);const r=JSON.parse(p.stdout);assert.equal(r.post_type,'wp_template');assert.equal(r.post_name,'page');assert.equal(r.tagged,true)});
test('PHP runtime fails closed if template theme binding fails',()=>{const p=phpProbe(stageTemplate(blueprint(),sample,digest).blueprint.steps[2].code,true);assert.notEqual(p.status,0);assert.match(p.stderr,/theme binding/)});
