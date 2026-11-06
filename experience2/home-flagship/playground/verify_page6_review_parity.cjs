#!/usr/bin/env node
/* Offline public-content-only structural release-admission check.
   Usage: node verify_page6_review_parity.cjs <Page6-EDITOR.html> <PlaygroundBlueprint.json> [Page6-RENDERED.html]
   Caller must supply files locally; no network, no WordPress writes, no visitor records. */
'use strict';
const fs=require('node:fs');
const crypto=require('node:crypto');
const {inspect}=require('node:util');
const ids=['fv-hf-title','fv-hf-chronicle','fv-hf-evidence','fv-hf-inquiry','fv-hf-method-title','fv-hf-observer','fv-hf-mind-title'];
const pattern=/<span class="fv-margin-strip__item"[^>]*>[\s\S]*?<\/span>/g;
const norm=s=>s.replace(/\s+/g,' ').trim();
const count=(s,re)=>(s.match(re)||[]).length;
function check(live,blueprint,rendered){
  const errors=[];
  function requireTrue(condition, code){if(!condition)errors.push(code);}
  requireTrue(blueprint&&Array.isArray(blueprint.steps)&&blueprint.steps.length===5,'BLUEPRINT_STEPS');
  const steps=blueprint?.steps||[];
  requireTrue(steps[0]?.step==='installTheme' && steps[0]?.options?.targetFolderName==='assembler','THEME_FOLDER');
  const source=steps[2]?.data||'';
  requireTrue(steps[2]?.step==='writeFile' && /\/mu-plugins\//.test(steps[2]?.path||''),'ISOLATED_MU_PLUGIN');
  requireTrue(source.includes("if (!is_page('fv-ex2-review'))"),'PREVIEW_ONLY_GUARD');
  const delimiter="return <<<'FVPG_HTML_END'\n";
  const start=source.indexOf(delimiter);
  const end=start>=0?source.indexOf('\nFVPG_HTML_END',start+delimiter.length):-1;
  requireTrue(start>=0 && end>=0,'PREVIEW_HTML_SOURCE');
  const preview=start>=0&&end>=0?source.slice(start+delimiter.length,end):'';
  const records=(s)=>[...s.matchAll(pattern)].map(m=>norm(m[0]));
  const current=records(live),proposed=records(preview);
  requireTrue(current.length===72 && proposed.length===72,'MARGINS_COUNT');
  requireTrue(current.length===72&&proposed.length===72&&current.every((v,i)=>v===proposed[i]),'MARGINS_EXACT_PUBLIC_TEXT');
  ids.forEach(id=>requireTrue(live.includes('id="'+id+'"')&&preview.includes('id="'+id+'"'),'CHAPTER_'+id));
  requireTrue(count(preview,/<img\s/g)===2,'PREVIEW_TWO_EDITORIAL_IMAGES');
  requireTrue(preview.includes('Franklinexpeditionnote.jpg')&&preview.includes('s67-19766.webp'),'PREVIEW_CORRECT_ARCHIVES');
  requireTrue(!preview.includes('edit-017-v02-nypl-5003296-original.jpg'),'NYPL_EXCLUDED_UNTIL_RIGHTS_CLEARED');
  requireTrue(!preview.includes('jetpack/subscriptions'),'NO_JETPACK_CLONE');
  requireTrue(preview.includes('href="https://finalvestige.com/focus/"'),'FOCUS_OFFER_TARGET');
  requireTrue(preview.includes('Explore the free 52-page Focus Fieldbook'),'FOCUS_REVIEW_EXPERIMENT');
  requireTrue(live.includes('href="https://finalvestige.com/blog/">Read the investigations'),'LIVE_BASELINE_HERO_ACTION');
  requireTrue(preview.includes('Enter the evidence room'),'PRIMARY_EVIDENCE_CTA');
  requireTrue(source.includes('Reviewed reduced-motion remedy from draft PR #1062'),'REDUCED_MOTION_REVIEW_REMEDY');
  const result={version:1,qualified:false,wordPressRuntimeTested:false,rawSourceTested:true,
    editorHash:crypto.createHash('sha256').update(live).digest('hex'),
    blueprintHash:crypto.createHash('sha256').update(JSON.stringify(blueprint)).digest('hex'),
    liveMargins:current.length,previewMargins:proposed.length,
    liveImages:count(live,/<img\s/g),previewImages:count(preview,/<img\s/g),
    previewFocusRefs:count(preview,/https:\/\/finalvestige\.com\/focus\//g),
    renderedEvidence:rendered!==undefined?{
       wpApiRenderedSourceRead:true, marginItems:count(rendered,/class="fv-margin-strip__item"/g),
       nativeJetpackContent:rendered.includes('jetpack')||rendered.includes('wp-block-jetpack-subscriptions'),
       chapterIds:ids.filter(id=>rendered.includes('id="'+id+'"')).length
    }:null,
    errors};
  if(rendered!==undefined){requireTrue(count(rendered,/class="fv-margin-strip__item"/g)===72,'RENDERED_MARGINS');ids.forEach(id=>requireTrue(rendered.includes('id="'+id+'"'),'RENDERED_CHAPTER_'+id));}
  result.errors=errors;result.sourceParityPass=errors.length===0;
  return result;
}
module.exports={check};
if(require.main===module){
  try{if(process.argv.length<4)throw Error('Usage: <public Page6 editor file> <review Blueprint JSON> [rendered WordPress response]');
  const [raw,blue,view]=process.argv.slice(2);
  const out=check(fs.readFileSync(raw,'utf8'),JSON.parse(fs.readFileSync(blue,'utf8')),view?fs.readFileSync(view,'utf8'):undefined);
  process.stdout.write(JSON.stringify(out,null,2)+'\n');process.exitCode=out.sourceParityPass?0:2;
  }catch(e){console.error('GATE CLOSED: '+e.message);process.exitCode=2;}
}
