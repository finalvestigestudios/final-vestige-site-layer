#!/usr/bin/env node
/**
 * FV Experience 2.0 — real Assembler-theme FRONT-END render admission.
 * Disposable local WordPress Playground only; source-controlled flagship + SYNTHETIC
 * Margins/Jetpack fixtures. No WordPress.com writes, subscriber data or production DB.
 * Not hosted parity, a Lighthouse audit, or production release authorization.
 */
import assert from 'node:assert/strict';
import {createHash, randomBytes} from 'node:crypto';
import {readFile, writeFile, mkdir} from 'node:fs/promises';
import {join, resolve, dirname} from 'node:path';
import {fileURLToPath} from 'node:url';

const HERE=dirname(fileURLToPath(import.meta.url));
const ASSEMBLER_ZIP='https://public-api.wordpress.com/rest/v1/themes/download/assembler.zip';
const WIDTHS=[320,390,768,1440,1920];
const sha = bytes => createHash('sha256').update(bytes).digest('hex');
const local = value => {
  try {
    const u=new URL(value);
    return u.protocol==='http:' && ['127.0.0.1','localhost','[::1]'].includes(u.hostname)
      && !!u.port && !u.username && !u.password;
  } catch { return false; }
};
function admission(manifest, source) {
  assert.equal(manifest.release,'HOLD');
  assert.equal(manifest.data_classification,'SYNTHETIC_TEST_FIXTURE_ONLY');
  assert.equal(manifest.page6_live_content_included,false);
  assert.equal(manifest.real_source_controlled_flagship,true);
  assert.equal(manifest.candidate_sha256,sha(source));
  assert.equal(manifest.candidate_bytes,source.length);
  assert.equal(manifest.margin_items,72);
  assert.equal(manifest.nypl_record_links,2);
  assert.equal(manifest.script_source_count,4);
  assert.equal(manifest.style_source_count,6);
  const text=source.toString('utf8');
  assert.equal((text.match(/<span class="fv-margin-strip__item" style="--i:\d+">/g)||[]).length,72);
  assert.equal((text.match(/jetpack\/subscriptions/g)||[]).length,1);
  assert.equal((text.match(/<script data-fv-source=/g)||[]).length,4);
  assert.ok(text.includes('FV EX2 SOURCE-CONTROLLED FULL FLAGSHIP'));
  assert.ok(text.includes('fv-hf__chapter-nav'));
  assert.ok(!text.includes('NYPL believes this item is in the public domain'));
}
function assertPreview(url,origin) {
  assert.ok(local(url),'Not a disposable HTTP loopback preview');
  assert.equal(new URL(url).port,new URL(origin).port,'Preview escaped the Playground port');
}
function receiptCheck(body,digest) {
  assert.equal(body.result,'PASS');
  assert.equal(body.release,'HOLD');
  assert.equal(body.source_sha256,digest);
  assert.equal(body.stored_sha256,digest);
  assert.equal(body.source_bytes,body.stored_bytes);
  assert.equal(Object.keys(body.checks||{}).length,9);
  assert.ok(Object.values(body.checks).every(v=>v===true));
}
function selfTest(){
  let checks=0;
  for(const s of ['http://localhost:9479/','http://127.0.0.1:9479/','http://[::1]:9479/']){assert.ok(local(s));checks++;}
  for(const s of ['https://finalvestige.com/','http://finalvestige.com:9479/','http://localhost/',
    'http://localhost:9479@finalvestige.com/','http://127.0.0.2:9479/','file:///a',
    'http://finalvestige.com.evil:9479/']){
    assert.ok(!local(s));checks++;
  }
  assert.deepEqual(WIDTHS,[320,390,768,1440,1920]);checks++;
  assert.throws(()=>assertPreview('https://finalvestige.com','http://localhost:9479'));checks++;
  assert.throws(()=>assertPreview('http://localhost:9478','http://localhost:9479'));checks++;
  const fixture=Buffer.from('x');
  assert.throws(()=>admission({release:'HOLD'},fixture));checks++;
  assert.throws(()=>receiptCheck({result:'PASS',checks:{}},'x'));checks++;
  console.log(JSON.stringify({self_tests:'PASS',checks,network:false,production_writes:false}));
}
if(process.argv.includes('--self-test')) selfTest();
else {
  const arg = name => {
    const i=process.argv.indexOf(name);
    assert.ok(i>0 && process.argv[i+1] && !process.argv[i+1].startsWith('--'),'Missing '+name);
    return resolve(process.argv[i+1]);
  };
  const candidate=await readFile(arg('--candidate'));
  const manifest=JSON.parse(await readFile(arg('--manifest'),'utf8'));
  const out=arg('--out');
  admission(manifest,candidate);
  await mkdir(out,{recursive:true});
  // Runtime dependencies are imported only AFTER the fail-closed synthetic-source check.
  const [{runCLI},{chromium},{default:AxeBuilder}]=await Promise.all([
    import('@wp-playground/cli'),import('playwright'),import('@axe-core/playwright')
  ]);
  const token=randomBytes(32).toString('hex');
  const php=await readFile(join(HERE,'playground_gutenberg_editor_gate.php'));
  const digest=sha(candidate);
  let server, browser, context, draft=false, outcome=null, fault=null;
  const summary={result:'HOLD',test:'REAL_ASSEMBLER_FRONTEND_SYNTHETIC_PLAYGROUND',
    source_sha256:digest,source_bytes:candidate.length,wp_personal_parity:false,
    widths:[],no_js:null,media:[],axe:[],release:'HOLD',cleaned:false};
  try {
    server=await runCLI({
      command:'server',wp:'6.8',php:'8.3',port:9479,login:false,
      blueprint:{steps:[{step:'installTheme',themeData:{resource:'url',url:ASSEMBLER_ZIP},
        options:{activate:true}}]}
    });
    assert.ok(local(server.serverUrl),'Refusing a non-loopback WordPress instance');
    await server.playground.writeFile('/wordpress/wp-content/fv-ex2-synthetic-only.marker',
      'SYNTHETIC_TEST_FIXTURE_ONLY\n');
    await server.playground.writeFile('/wordpress/wp-content/fv-ex2-synthetic-candidate.html',candidate);
    await server.playground.writeFile('/wordpress/wp-content/fv-ex2-editor-token',token+'\n');
    await server.playground.writeFile('/wordpress/fv_ex2_editor_qa_once.php',php);
    browser=await chromium.launch({headless:true});
    context=await browser.newContext({viewport:{width:1440,height:900}});
    const act=async action=>{
      let target=new URL('/fv_ex2_editor_qa_once.php?action='+action,server.serverUrl);
      assertPreview(target.toString(),server.serverUrl);
      const request = url => context.request.post(url.toString(),{
        headers:{'X-FV-EX2-EDITOR-TOKEN':token},timeout:90000,maxRedirects:0,
        failOnStatusCode:false
      });
      let response=await request(target);
      if([301,302,303,307,308].includes(response.status())){
        const target2=new URL(response.headers().location||'',target);
        assertPreview(target2.toString(),server.serverUrl);
        assert.equal(target2.pathname,target.pathname);
        assert.ok(target2.search===target.search||target2.search==='');
        response=await request(new URL(target.pathname+target.search,target2.origin));
      }
      assert.equal(response.status(),200,'Local WordPress '+action+' returned '+response.status());
      assert.ok((response.headers()['content-type']||'').includes('application/json'));
      return response.json();
    };
    const created=await act('create');
    assert.equal(created.result,'CREATED');
    assert.equal(created.source_sha256,digest);
    const id=created.draft_id;
    assert.ok(Number.isSafeInteger(id)&&id>0);
    draft=true;
    assert.equal((await act('login')).result,'LOGIN_SET');
    const editor=await context.newPage();
    const editorUrl=new URL('/wp-admin/post.php',server.serverUrl);
    editorUrl.searchParams.set('post',String(id));
    editorUrl.searchParams.set('action','edit');
    await editor.goto(editorUrl.toString(),{waitUntil:'domcontentloaded',timeout:90000});
    await editor.waitForFunction(n=>window.wp?.data?.select('core/editor')?.getCurrentPostId?.()===n,
      id,{timeout:90000});
    const save=await editor.evaluate(async()=>{
      const select=window.wp.data.select('core/editor');
      const dispatch=window.wp.data.dispatch('core/editor');
      dispatch.editPost({title:'FV EX2 SYNTHETIC EDITOR SAVED'});
      await dispatch.savePost();
      return {ok:select.didPostSaveRequestSucceed(),failed:select.didPostSaveRequestFail()};
    });
    assert.deepEqual(save,{ok:true,failed:false});
    receiptCheck(await act('verify'),digest);
    await editor.close();
    const preview=new URL('/',server.serverUrl);
    preview.searchParams.set('page_id',String(id));
    preview.searchParams.set('preview','true');
    assertPreview(preview.toString(),server.serverUrl);
    const imgStats=new Map();
    for(const width of WIDTHS){
      const page=await context.newPage();
      await page.setViewportSize({width,height:900});
      page.on('response', async response=>{
        const url=response.url();
        if(!url.startsWith('https://finalvestige.com/wp-content/uploads/'))return;
        const item={path:new URL(url).pathname,status:response.status(),bytes:0};
        try { if(response.ok())item.bytes=(await response.body()).length; } catch {item.bytes=0;}
        imgStats.set(item.path,item);
      });
      await page.goto(preview.toString(),{waitUntil:'domcontentloaded',timeout:90000});
      assertPreview(page.url(),server.serverUrl);
      await page.locator('[data-fv-home-flagship]').waitFor({timeout:30000});
      await page.evaluate(()=>document.fonts?.ready);
      const state=await page.evaluate(()=>{
        const root=document.querySelector('[data-fv-home-flagship]');
        const nav=[...root.querySelectorAll('.fv-hf__chapter-nav a[href^="#"]')];
        const ids=nav.map(a=>a.getAttribute('href').slice(1));
        const ok=ids.every(id=>document.getElementById(id));
        const doc=document.documentElement;
        return {assembler:document.body.classList.contains('wp-theme-assembler-wpcom') &&
            [...document.querySelectorAll('link[rel="stylesheet"]')].some(l=>{
              try { return new URL(l.href).pathname==='/wp-content/themes/assembler-wpcom/style.css'; }
              catch { return false; }
            }),
          theme_body_classes:[...document.body.classList].filter(x=>x.startsWith('wp-theme-')),
          theme_css_paths:[...document.querySelectorAll('link[rel="stylesheet"]')].map(x=>x.getAttribute('href')||'').filter(x=>x.includes('/themes/')).map(x=>new URL(x,location.href).pathname).slice(0,6),
          chapter_links:nav.length,targets_resolve:ok,
          margins:document.querySelectorAll('.fv-margin-strip__item').length,
          document_width:doc.scrollWidth,viewport_width:innerWidth,
          source_styles:document.querySelectorAll('style[data-fv-stage-only="source-css"]').length,
          scripts:document.querySelectorAll('script[data-fv-source]').length,
          case_panels:root.querySelectorAll('[data-fv-case]').length,
          displayed_text:root.innerText.length};
      });
      assert.equal(state.assembler,true,'Actual Assembler theme did not render. CSS='+JSON.stringify(state.theme_css_paths)+' classes='+JSON.stringify(state.theme_body_classes));
      assert.equal(state.chapter_links,7);
      assert.equal(state.targets_resolve,true);
      assert.equal(state.margins,72);
      assert.equal(state.source_styles,1);
      assert.equal(state.scripts,4);
      assert.equal(state.case_panels,3);
      assert.ok(state.displayed_text>1000);
      assert.ok(state.document_width<=state.viewport_width+1,
        'Horizontal overflow at '+width);
      const shot=join(out,'assembler-'+width+'.png');
      await page.screenshot({path:shot,fullPage:width===320||width===1440,
        animations:'disabled'});
      if(width===390||width===1440){
        const axe=await new AxeBuilder({page}).withTags([
          'wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa'
        ]).analyze();
        const violations=axe.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.length}));
        summary.axe.push({width,violation_count:violations.length,violations});
      }
      if(width===390){
        const caseButton=page.locator('[data-fv-case-button="franklin"]');
        await caseButton.click({timeout:30000});
        assert.equal(await caseButton.getAttribute('aria-pressed'),'true');
        assert.equal(await page.locator('[data-fv-case="franklin"]').isVisible(),true);
      }
      summary.widths.push({width,...state,screenshot:'assembler-'+width+'.png'});
      await writeFile(join(out,'manifest.partial.json'),JSON.stringify(summary,null,2));
      await page.close();
    }
    const nojs=await browser.newContext({viewport:{width:390,height:844},
      javaScriptEnabled:false});
    await nojs.addCookies(await context.cookies());
    const plain=await nojs.newPage();
    await plain.goto(preview.toString(),{waitUntil:'domcontentloaded',timeout:90000});
    assertPreview(plain.url(),server.serverUrl);
    const basic=await plain.evaluate(()=>{
      const root=document.querySelector('[data-fv-home-flagship]');
      return {present:!!root,all_case_panels_visible:!!root &&
        [...root.querySelectorAll('[data-fv-case]')].every(el=>!el.hidden),
        links:root?.querySelectorAll('.fv-hf__chapter-nav a[href^="#"]').length,
        margins:document.querySelectorAll('.fv-margin-strip__item').length};
    });
    assert.deepEqual(basic,{present:true,all_case_panels_visible:true,links:7,margins:72});
    summary.no_js=basic;
    await plain.screenshot({path:join(out,'assembler-390-nojs.png'),animations:'disabled'});
    await nojs.close();
    summary.media=[...imgStats.values()].sort((a,b)=>a.path.localeCompare(b.path));
    assert.ok(summary.media.some(m=>m.status===200&&m.bytes>0),
      'No real first-party archival image body bytes verified');
    assert.ok(summary.axe.every(x=>x.violation_count===0),
      'Axe identified WCAG-tagged violations — see preserved manifest');
    outcome=true;
  }catch(e){fault=e;summary.error=e?.message||String(e);}
  finally{
    if(draft&&server&&context){
      try{
        const u=new URL('/fv_ex2_editor_qa_once.php?action=cleanup',server.serverUrl);
        assertPreview(u.toString(),server.serverUrl);
        const response=await context.request.post(u.toString(),{
          headers:{'X-FV-EX2-EDITOR-TOKEN':token},timeout:30000,
          maxRedirects:0,failOnStatusCode:false});
        const body=await response.json();
        summary.cleaned=response.status()===200&&body.result==='DELETED'&&body.verified_absent===true;
      }catch{summary.cleaned=false;}
    }
    if(!summary.cleaned) fault=new Error('FAIL CLOSED: disposable draft cleanup unverified');
    if(browser)await browser.close();
    if(server)await server[Symbol.asyncDispose]();
    summary.result=outcome&&!fault?'PASS':'FAIL';
    await writeFile(join(out,'assembler-results.json'),JSON.stringify(summary,null,2));
    console.log(JSON.stringify({result:summary.result,release:'HOLD',
      candidate_sha256:digest,widths:summary.widths.map(x=>x.width),
      no_js:summary.no_js,axe:summary.axe,media:summary.media,
      cleaned:summary.cleaned,error:summary.error||null},null,2));
  }
  if(fault)throw fault;
}