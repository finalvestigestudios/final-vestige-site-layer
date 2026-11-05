/**
 * Real Chromium DOM and link-navigation regression for the seven ACTUAL
 * public Chapter Rail destinations. Synthetic fixture, not hosted WordPress.
 * FV_TEST_CHROMIUM=/usr/bin/chromium node --test test_real_seven_chapters_browser.mjs
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import {auditChapterNavigation,chapterNavigationPassed} from './live_public_focus_browser_gate.mjs';

const IDS=['fv-hf-title','fv-hf-chronicle','fv-hf-evidence',
  'fv-hf-inquiry','fv-hf-method-title','fv-hf-observer','fv-hf-mind-title'];
const WIDTHS=[320,390,768,1279,1280,1440,1920];
const launchOptions=process.env.FV_TEST_CHROMIUM
  ?{headless:true,executablePath:process.env.FV_TEST_CHROMIUM,args:['--no-sandbox']}
  :{headless:true};

function fixture(mutation=''){
  const navLinks=IDS.map((id,i)=>'<a href="#'+
    (mutation==='wrong-link'&&i===4?'fv-hf-apollo':id)+
    '">Chapter '+(i+1)+'</a>');
  if(mutation==='missing-link')navLinks.splice(6,1);
  if(mutation==='duplicate-link')navLinks.push(navLinks[2]);
  if(mutation==='reordered-link')[navLinks[1],navLinks[2]]=[navLinks[2],navLinks[1]];
  const sections=IDS.map((id,i)=>{
    if(mutation==='missing-target'&&i===6)return '';
    const isHeading=[0,4,6].includes(i);
    const headingId=isHeading?id:id+'-title';
    const label=mutation==='wrong-label'&&i===4?'not-a-heading':headingId;
    const hidden=mutation==='hidden-chapter'&&i===4?' hidden':'';
    const className=mutation==='css-hidden'&&i===4?' class="missing"':'';
    const heading=mutation==='empty-heading'&&i===4?'':'Verified chapter '+(i+1);
    const words=mutation==='short-copy'&&i===4?'Short.':
      ('This evidence chapter provides original archival records, limitations, and accessible context for the reader. ').repeat(4);
    const marker=isHeading?
      '<h2 id="'+id+'">'+heading+'</h2>':
      '<h2 id="'+headingId+'">'+heading+'</h2>';
    return '<section aria-labelledby="'+label+'"'+hidden+className+'>'+marker+
      '<p>'+words+'</p></section>';
  });
  if(mutation==='duplicate-target')sections.push('<div id="fv-hf-method-title">Duplicate</div>');
  return '<!doctype html><html lang="en"><meta charset="utf-8">'+
    '<style>body{margin:0;background:#0a0b0b;color:#f4efe6;font:17px/1.6 Georgia}'+
    '.fv-hf__chapter-nav{display:flex;overflow-x:auto;gap:10px;padding:12px;background:#132323;white-space:nowrap}'+
    '.fv-hf__chapter-nav a{color:#f7dba4;padding:12px;min-height:44px}'+
    'section{min-height:260px;padding:30px;border-bottom:1px solid #b8955e}'+
    '.missing{display:none}'+
    (mutation==='hidden-nav'?'.fv-hf__chapter-nav{display:none}':'')+
    '</style><main data-fv-home-flagship>'+
    '<nav class="fv-hf__chapter-nav" aria-label="Explore the chapters">'+
    navLinks.join('')+'</nav>'+sections.join('')+'</main></html>';
}
test('all seven real chapter destinations remain readable across seven widths and JS/no-JS',async()=>{
  const browser=await chromium.launch(launchOptions);
  try{
    for(const javaScriptEnabled of [true,false]){
      for(const width of WIDTHS){
        const page=await browser.newPage({viewport:{width,height:900},javaScriptEnabled});
        try{
          await page.setContent(fixture());
          const state=await auditChapterNavigation(page);
          assert.ok(chapterNavigationPassed(state),width+' js='+javaScriptEnabled+' '+JSON.stringify(state));
          assert.deepEqual(state.navTargets,IDS.map(id=>'#'+id));
          for(const id of IDS){
            await page.locator('.fv-hf__chapter-nav a[href="#'+id+'"]').click();
            assert.equal(new URL(page.url()).hash,'#'+id,'native chapter link navigation '+id);
          }
        }finally{await page.close();}
      }
    }
  }finally{await browser.close();}
});
test('missing/reordered chapter links and absent/hidden/unlabeled destinations fail closed',async()=>{
  const browser=await chromium.launch(launchOptions);
  try{
    const page=await browser.newPage({viewport:{width:390,height:900},javaScriptEnabled:false});
    try{
      for(const mutation of ['wrong-link','missing-link','duplicate-link',
        'reordered-link','missing-target','duplicate-target','hidden-chapter',
        'css-hidden','wrong-label','empty-heading','short-copy','hidden-nav']){
        await page.setContent(fixture(mutation));
        const state=await auditChapterNavigation(page);
        assert.equal(chapterNavigationPassed(state),false,
          mutation+' wrongly approved '+JSON.stringify(state));
      }
    }finally{await page.close();}
  }finally{await browser.close();}
});
