#!/usr/bin/env node
/* Isolated review artifact only. Never calls WordPress, GitHub, Jetpack or network.
   Usage: node prepare_focus_nojs_fallback.cjs exported-public-page.json proposed-page-content.html
   Input: {id:1579, modified:'2026-11-05T17:44:02', status:'publish', content:'<serialized Gutenberg source>'}.
   Output is an independent LOCAL file requiring code/editor review and explicit release approval.
*/
'use strict';
const fs=require('node:fs');
const path=require('node:path');
const assert=require('node:assert/strict');
const CURRENT_MODIFIED='2026-11-05T17:44:02';
const PDF='https://finalvestige.com/wp-content/uploads/2026/10/Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf';
const BEGIN='<!-- wp:jetpack/subscriptions ';
const FOCUS_FALLBACK='<!-- REVIEW ONLY. Proposed after existing Jetpack subscriptions block on /focus/; never replace Jetpack. -->';
function once(s,needle){return s.split(needle).length===2;}
function prepare(page,block){
  assert.equal(page.id,1579,'wrong page');
  assert.equal(page.status,'publish','unexpected publication state');
  assert.equal(page.modified,CURRENT_MODIFIED,'WordPress revision changed: retrieve and independently review');
  const source=page.content;
  assert.equal(typeof source,'string','missing raw editor source');
  assert.ok(source.length>5000,'unexpectedly short page source');
  assert.ok(source.includes('class="wp-block-group alignfull fv-focus"'),'not the Focus page');
  assert.ok(once(source,BEGIN),'Jetpack subscription anchor not unique');
  assert.ok(once(source,PDF),'post-signup PDF asset missing or duplicated');
  assert.ok(source.includes('id="fvf-gift"') && source.includes(' hidden '),'post-signup gift not gated as expected');
  assert.ok(!source.includes(FOCUS_FALLBACK) && !source.includes('<noscript>'),'fallback already present; manual review required');
  assert.ok(!source.includes('<!-- wp:jetpack/subscriptions {"showSubscribersTotal":true'),'subscription configuration unexpected');
  assert.ok(block.includes(FOCUS_FALLBACK),'wrong review block');
  assert.ok(once(block,PDF) && once(block,'<noscript>'),'missing genuine PDF fallback');
  assert.ok(!/<form\b|<script\b|data-fv-event=/i.test(block),'fallback cannot submit a form or track a conversion');
  const start=source.indexOf(BEGIN),end=source.indexOf(' /-->',start);
  assert.ok(end>start && end-start<1500,'subscription block boundary changed');
  const insertion=end+6;
  const output=source.slice(0,insertion)+'\n\n'+block.trim()+'\n'+source.slice(insertion);
  assert.ok(output.split(BEGIN).length===2,'subscription block was lost');
  assert.ok(output.includes('<!-- wp:jetpack/subscriptions') && output.includes('id="fvf-gift"'));
  assert.ok(output.includes(FOCUS_FALLBACK));
  return output;
}
if(require.main===module){
  if(process.argv.length!==4){console.error('Usage: node prepare_focus_nojs_fallback.cjs source-page-1579.json proposed-local-content.html');process.exit(2)}
  try{
    const file=path.resolve(process.argv[2]);const out=path.resolve(process.argv[3]);
    assert.notEqual(file,out,'cannot overwrite source export');
    const page=JSON.parse(fs.readFileSync(file,'utf8'));
    const block=fs.readFileSync(path.join(__dirname,'focus_nojs_fallback_block.html'),'utf8');
    const result=prepare(page,block);
    fs.writeFileSync(out,result,{flag:'wx'});
    console.log(JSON.stringify({status:'CREATED_LOCAL_REVIEW_ONLY',output:out,page:1579,sourceModified:CURRENT_MODIFIED,jetpackPreserved:true,pdfDirectFallback:true,productionChanged:false}));
  }catch(e){console.error('HOLD:',e.message);process.exit(2)}
}
module.exports={prepare,CURRENT_MODIFIED,PDF};
