#!/usr/bin/env node
/** EX2 isolated real Assembler frontend gate. Only call after verified Gutenberg
 * editor Save inside disposable loopback WordPress Playground. RELEASE HOLD.
 * Not WordPress.com hosting, real Jetpack, live page6, field CWV or manual WCAG.
 */
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile, readdir, mkdir} from 'node:fs/promises';
import {join, relative, resolve, sep, basename} from 'node:path';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const sha=b=>createHash('sha256').update(b).digest('hex');
const loopback=(raw)=>{
  try {const u=new URL(raw);return u.protocol==='http:'&&['localhost','127.0.0.1','[::1]'].includes(u.hostname)&&Boolean(u.port)&&!u.username&&!u.password;}catch{return false;}
};
const mediaHost=(raw)=>{
  try {const u=new URL(raw);return u.protocol==='https:'&&['finalvestige.com','i0.wp.com'].includes(u.hostname)&&!u.username&&!u.password&&/\.(webp|png|jpe?g|svg)$/i.test(u.pathname);}catch{return false;}
};
const widths=[320,390,768,1440,1920];
async function walk(base,dir=base){
  const out=[];
  for(const d of await readdir(dir,{withFileTypes:true})){
    if(d.isSymbolicLink())throw new Error('Theme symlink denied');
    const f=join(dir,d.name);
    if(d.isDirectory())out.push(...await walk(base,f));
    else if(d.isFile())out.push(f);
    else throw new Error('Nonregular theme entry denied');
  }
  return out;
}
function themeVersion(css){
  const name=css.match(/^Theme Name:\s*(.+)$/mi)?.[1]?.trim();
  const version=css.match(/^Version:\s*(.+)$/mi)?.[1]?.trim();
  if(name!=='Assembler'||!version||!/^\d+\.\d+\.\d+$/.test(version))throw new Error('Invalid Assembler metadata');
  return version;
}
async function activateTheme(server,themeDirectory){
  const base=resolve(themeDirectory);
  const themeSlug=basename(base);
  assert.ok(['assembler','assembler-wpcom'].includes(themeSlug),'Unrecognized official Assembler ZIP root');
  const version=themeVersion(await readFile(join(base,'style.css'),'utf8'));
  const files=await walk(base);
  assert.ok(files.length>5&&files.length<900,'Unexpected theme file inventory');
  const root='/wordpress/wp-content/themes/'+themeSlug,dirs=new Set([root]);
  let bytes=0;
  for(const f of files){
    const parts=relative(base,f).split(sep);
    if(parts.some(x=>x==='..'||x==='.'||!x))throw new Error('Theme traversal denied');
    for(let i=1;i<parts.length;i++)dirs.add(root+'/'+parts.slice(0,i).join('/'));
    bytes+=(await readFile(f)).length;
  }
  assert.ok(bytes>1000&&bytes<30_000_000,'Unexpected theme bytes');
  for(const dir of [...dirs].sort((a,b)=>a.length-b.length))await server.playground.mkdir(dir);
  for(const f of files)await server.playground.writeFile(root+'/'+relative(base,f).split(sep).join('/'),await readFile(f));
  const php=`<?php require '/wordpress/wp-load.php'; switch_theme('${themeSlug}'); $t=wp_get_theme(); echo wp_json_encode(array('stylesheet'=>get_stylesheet(),'template'=>get_template(),'version'=>$t->get('Version'),'home'=>home_url('/')));`;
  const result=await server.playground.run({code:php});
  let obj;
  try {obj=JSON.parse(result.text);}catch{throw new Error('WordPress theme activation receipt invalid');}
  assert.equal(obj.stylesheet,themeSlug);
  assert.equal(obj.template,themeSlug);
  assert.equal(obj.version,version);
  assert.ok(loopback(obj.home));
  return {version,theme_slug:themeSlug,files:files.length,bytes,provenance:'WordPress.com free official Assembler download (not version-pinned)'};
}
function restrictNetwork(page,blocked){
  return page.route('**/*',route=>{
    const u=route.request().url();
    if(loopback(u)||mediaHost(u))return route.continue();
    try {blocked.add(new URL(u).hostname);}catch{blocked.add('[invalid]');}
    return route.abort();
  });
}
async function imageBodies(page){
  const urls=await page.locator('img').evaluateAll(els=>[...new Set(els.map(x=>x.currentSrc||x.src).filter(Boolean))]);
  const rows=[];
  for(const url of urls){
    if(!mediaHost(url))continue;
    const res=await page.request.get(url,{maxRedirects:2,timeout:30000,failOnStatusCode:false});
    const body=await res.body(),mime=(res.headers()['content-type']||'').split(';')[0];
    const pass=res.status()===200&&mime.startsWith('image/')&&body.byteLength>100;
    rows.push({host:new URL(url).hostname,status:res.status(),mime,bytes:body.byteLength,sha256:sha(body),pass});
    if(!pass)throw new Error('First-party archival media body unreadable');
  }
  if(rows.length<2)throw new Error('No complete two-source archival image body evidence');
  return rows;
}
async function checkView(page,width,axePath){
  await page.setViewportSize({width,height:900});
  await page.goto(page.stageUrl,{waitUntil:'domcontentloaded',timeout:90000});
  await page.locator('[data-fv-home-flagship]').waitFor({timeout:30000});
  await page.evaluate(()=>document.fonts?.ready);
  const state=await page.evaluate(()=>{
    const root=document.querySelector('[data-fv-home-flagship]');
    const links=[...root.querySelectorAll('.fv-hf__chapter-nav a[href^="#"]')];
    return {chapter_links:links.length,chapter_targets:links.filter(a=>document.getElementById(a.getAttribute('href').slice(1))).length,
      margins:document.querySelectorAll('.fv-margin-strip__item').length,
      focus:(document.body.innerText.match(/Focus Fieldbook/g)||[]).length,
      overflow:document.documentElement.scrollWidth>innerWidth+1,
      main:!!root.querySelector('main'),h1:!!root.querySelector('h1'),
      inline_scripts:root.querySelectorAll('script[data-fv-source]').length,
      document_scripts:document.querySelectorAll('script[data-fv-source]').length,
      source_script_names:[...document.querySelectorAll('script[data-fv-source]')].map(x=>x.dataset.fvSource).sort(),
      interactive_enhanced:root.classList.contains('fv-hf--enhanced'),
      root_styles:root.querySelectorAll('style[data-fv-stage-only]').length,
      document_styles:document.querySelectorAll('style[data-fv-stage-only]').length,
      post_content_nodes:document.querySelectorAll('.wp-block-post-content').length};
  });
  assert.equal(state.chapter_links,7);
  assert.equal(state.chapter_targets,7);
  assert.equal(state.margins,72);
  assert.ok(state.focus>=1);
  assert.equal(state.overflow,false,`Horizontal overflow at ${width}`);
  assert.equal(state.main,true);assert.equal(state.h1,true);
  // WordPress serializes script tags in the stored Custom HTML, then the HTML
  // browser parser can relocate them outside .fv-hf. Verify exact executable
  // script identities in the rendered DOCUMENT, not an invented DOM hierarchy.
  assert.deepEqual(state.source_script_names,
    ['chronicle-lens.js','flagship.js','observer-lab.js','reading-trail.js'],
    'Gutenberg script custody mismatch in actual rendered document');
  assert.equal(state.interactive_enhanced,true,
    'Flagship enhancement did not initialize in Assembler WordPress render');
  await page.addScriptTag({path:axePath});
  const violations=await page.evaluate(async()=>{
    if(!window.axe)throw new Error('axe unavailable: fail closed');
    const r=await window.axe.run(document.querySelector('[data-fv-home-flagship]'),
      {runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}});
    return r.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.length,
      targets:v.nodes.slice(0,4).map(n=>n.target.slice(0,3)),
      contrast:v.nodes.slice(0,2).flatMap(n=>n.any.filter(c=>c.id==='color-contrast').map(c=>({
        foreground:c.data?.fgColor,background:c.data?.bgColor,
        measured:c.data?.contrastRatio,required:c.data?.expectedContrastRatio
      })))}));
  });
  if(violations.length)throw new Error(`Automated axe findings at ${width}: ${JSON.stringify(violations)}`);
  return {width,state,axe_violations:0,media:await imageBodies(page)};
}
export async function runAssemblerPreview({server,browser,context,draftId,themeDirectory,outputDirectory}){
  assert.ok(Number.isInteger(draftId)&&draftId>0);
  assert.ok(loopback(server.serverUrl));
  const theme=await activateTheme(server,themeDirectory);
  await mkdir(outputDirectory,{recursive:true});
  const blocked=new Set(),page=await context.newPage();
  page.stageUrl=new URL(`/?page_id=${draftId}&preview=true`,server.serverUrl).href;
  if(!loopback(page.stageUrl))throw new Error('Unsafe preview URL');
  await restrictNetwork(page,blocked);
  const axePath=require.resolve('axe-core/axe.min.js'),responsive=[];
  for(const width of widths){
    const item=await checkView(page,width,axePath);
    if([390,1440].includes(width))await page.screenshot({path:join(outputDirectory,`assembler-${width}.png`),animations:'disabled'});
    responsive.push(item);
  }
  await page.setViewportSize({width:720,height:450});
  await page.goto(page.stageUrl,{waitUntil:'domcontentloaded',timeout:90000});
  const reflow=await page.evaluate(()=>({overflow:document.documentElement.scrollWidth>innerWidth+1,
    chapters:document.querySelectorAll('.fv-hf__chapter-nav a').length}));
  assert.equal(reflow.overflow,false,'200% desktop CSS viewport equivalent overflow');
  assert.equal(reflow.chapters,7);
  await page.close();
  const noContext=await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:844}});
  await noContext.addCookies(await context.cookies());
  const noPage=await noContext.newPage();
  await restrictNetwork(noPage,blocked);
  await noPage.goto(new URL(`/?page_id=${draftId}&preview=true`,server.serverUrl).href,
    {waitUntil:'domcontentloaded',timeout:90000});
  const noJS=await noPage.evaluate(()=>({chapters:document.querySelectorAll('.fv-hf__chapter-nav a').length,
    margins:document.querySelectorAll('.fv-margin-strip__item').length,
    h1:document.querySelectorAll('[data-fv-home-flagship] h1').length}));
  assert.deepEqual(noJS,{chapters:7,margins:72,h1:1});
  await noContext.close();
  return {type:'ISOLATED_WP_ASSEMBLER_RENDER_SYNTHETIC_ONLY',release:'HOLD',theme,
    responsive,zoom_200_percent_equivalent:reflow,no_js:noJS,blocked_hosts:[...blocked].sort(),
    limits:['not WP.com Atomic parity','not real Jetpack','not real hosted page6 content','not physical browser zoom','not manual WCAG 2.2 AA','not field Core Web Vitals']};
}
function selfTest(){
  for(const u of ['http://localhost:3211/','http://127.0.0.1:9473/'])assert.ok(loopback(u));
  for(const u of ['https://finalvestige.com/','http://localhost/','http://localhost:3211@evil.com/'])assert.ok(!loopback(u));
  assert.ok(mediaHost('https://finalvestige.com/wp-content/uploads/f.jpg'));
  assert.ok(mediaHost('https://i0.wp.com/finalvestige.com/test.webp?fit=300'));
  for(const u of ['http://finalvestige.com/foo.jpg','https://evil.example/test.png','https://finalvestige.com/wp-admin/'])assert.ok(!mediaHost(u));
  assert.equal(themeVersion('Theme Name: Assembler\nVersion: 0.0.126\n'),'0.0.126');
  assert.throws(()=>themeVersion('Theme Name: Other\nVersion: 1.0.0\n'));
  console.log(JSON.stringify({self_test:'PASS',checks:12,network_used:false,release:'HOLD'}));
}
if(process.argv.includes('--self-test'))selfTest();
