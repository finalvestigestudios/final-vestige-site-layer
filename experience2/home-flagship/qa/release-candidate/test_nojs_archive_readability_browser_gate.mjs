/**
 * JS-disabled, representative browser fixture. It exercises the exact exported
 * auditNoJsArchives helper against actual Chromium DOM/CSS observations.
 * NOT a WordPress Playground test, nor a production WCAG assertion.
 *
 * Run: FV_TEST_CHROMIUM=/usr/bin/chromium node --test test_nojs_archive_readability_browser_gate.mjs
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import {auditNoJsArchives} from './live_public_focus_browser_gate.mjs';

const CASES=['apollo','franklin','malbone'];
const WIDTHS=[320,390,768,1279,1280,1440,1920];
function fixture(breakType=''){
  let panels=CASES.map(id=>{
    const title=breakType==='broken-label'&&id==='franklin'?'wrong-title':('fv-hf-'+id+'-title');
    const text=breakType==='short'&&id==='franklin'?'Short.':
      ('This independent archival case provides readable evidence and historic context. ').repeat(5);
    const source=breakType==='no-source'&&id==='franklin'
      ?'<a href="https://finalvestige.com/focus/">Only internal</a>'
      :'<a href="https://www.nasa.gov/source-'+id+'">Primary source</a>';
    const hidden=breakType==='hidden-panel'&&id==='franklin'?' hidden':'';
    return '<article data-fv-case="'+id+'" aria-labelledby="fv-hf-'+id+'-title"'+hidden+'>'+
      '<h3 id="'+title+'">Verified '+id+' record</h3><p>'+text+'</p>'+source+'</article>';
  }).join('');
  if(breakType==='duplicate')panels+='<article data-fv-case="apollo">Duplicate</article>';
  const chooserHidden=breakType==='visible-chooser'?'':' hidden';
  const stylesheet=breakType==='css-invisible'
    ?'article[data-fv-case="franklin"]{display:none}':'';
  return '<!doctype html><html lang="en"><meta charset="utf-8">'+
    '<style>body{font:18px Georgia}article{padding:24px;margin:12px}'+stylesheet+'</style>'+
    '<main data-fv-home-flagship><div data-fv-case-buttons'+chooserHidden+'>'+
    '<button type="button">Enhancement-only selector</button></div>'+panels+'</main></html>';
}
function passes(r){
  return r.controlsHidden&&r.panelCount===3&&r.cases.length===3&&
    r.cases.every(c=>c.unique&&c.exposed&&c.titled&&c.readable&&c.sourceLinked);
}
const launchOpts=process.env.FV_TEST_CHROMIUM
  ?{headless:true,executablePath:process.env.FV_TEST_CHROMIUM,args:['--no-sandbox']}
  :{headless:true};

test('no-JS all three sourceful records visible at seven widths',async()=>{
  const browser=await chromium.launch(launchOpts);
  try{
    for(const width of WIDTHS){
      const page=await browser.newPage({viewport:{width,height:900},javaScriptEnabled:false});
      try{
        await page.setContent(fixture());
        const result=await auditNoJsArchives(page);
        assert.ok(passes(result),width+' '+JSON.stringify(result));
        assert.deepEqual(result.cases.map(c=>c.id),CASES);
      }finally{await page.close();}
    }
  }finally{await browser.close();}
});
test('hidden, unsourced, unlabeled, unreadable, duplicated and visible chooser reject',async()=>{
  const browser=await chromium.launch(launchOpts);
  try{
    const page=await browser.newPage({javaScriptEnabled:false});
    try{
      for(const mutation of [
        'hidden-panel','no-source','broken-label','short',
        'duplicate','visible-chooser','css-invisible'
      ]){
        await page.setContent(fixture(mutation));
        const result=await auditNoJsArchives(page);
        assert.equal(passes(result),false,mutation+' erroneously passed');
      }
    }finally{await page.close();}
  }finally{await browser.close();}
});
