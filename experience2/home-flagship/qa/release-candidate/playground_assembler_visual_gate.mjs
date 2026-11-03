#!/usr/bin/env node
/**
 * Real Assembler front-end qualification against an ephemeral, localhost-only
 * WordPress Playground draft with actual source-controlled seven chapters.
 * NOT a WordPress.com staging clone. No actual page-6 content, users or secrets.
 */
import assert from 'node:assert/strict';
import {createHash,randomBytes} from 'node:crypto';
import {readFile,mkdir,writeFile} from 'node:fs/promises';
import {dirname,resolve,join} from 'node:path';
import {fileURLToPath} from 'node:url';
const HERE=dirname(fileURLToPath(import.meta.url));
const hash=(data)=>createHash('sha256').update(data).digest('hex');
const hostAllowed=(url)=>{
  try {
    const u=new URL(url);
    return u.protocol==='http:' && ['127.0.0.1','localhost','[::1]'].includes(u.hostname) &&
      !!u.port && !u.username && !u.password;
  } catch{return false;}
};
function validateCandidate(source,manifest) {
  assert.equal(manifest.data_classification,'SYNTHETIC_TEST_FIXTURE_ONLY');
  assert.equal(manifest.page6_live_content_included,false);
  assert.equal(manifest.release,'HOLD');
  assert.equal(hash(source),manifest.candidate_sha256);
  assert.equal(source.byteLength,manifest.candidate_bytes);
  const html=source.toString('utf8');
  assert.equal((html.match(/<span class="fv-margin-strip__item" style="--i:\d+">/g)||[]).length,72);
  assert.equal((html.match(/jetpack\/subscriptions/g)||[]).length,1);
  assert.equal((html.match(/FV EX2 SOURCE-CONTROLLED FULL FLAGSHIP/g)||[]).length,1);
  assert.equal((html.match(/data-fv-home-flagship/g)||[]).length,1);
  assert.ok(!html.includes('NYPL believes this item is in the public domain'));
  assert.ok(!html.includes('https://finalvestige.com/wp-json/'));
  for(const id of ['fv-hf-title','fv-hf-chronicle','fv-hf-evidence','fv-hf-inquiry',
    'fv-hf-method-title','fv-hf-observer','fv-hf-mind-title']) {
    assert.equal(html.split('id="'+id+'"').length-1,1,'Missing chapter '+id);
  }
}
const getArg=(key)=>{const i=process.argv.indexOf(key);return i<0?null:process.argv[i+1];};
function selfTest() {
  let cases=0;
  for(const u of ['http://localhost:9473','http://127.0.0.1:9400','http://[::1]:9473']) {
    assert.equal(hostAllowed(u),true);cases++;
  }
  for(const u of ['https://localhost:9473','http://finalvestige.com:9473',
    'http://localhost:9473@evil.com/','http://localhost/',
    'file:///tmp/page','http://user@localhost:9473']) {
    assert.equal(hostAllowed(u),false);cases++;
  }
  const sample=Buffer.from('irrelevant');
  assert.throws(()=>validateCandidate(sample,{}));cases++;
  assert.throws(()=>validateCandidate(sample,{release:'APPROVED'}));cases++;
  console.log(JSON.stringify({self_test:'PASS',cases,network:false,release:'HOLD'}));
}
if(process.argv.includes('--self-test')) {selfTest();}
else {
  const srcFile=getArg('--candidate'), manifestFile=getArg('--manifest'),
    zipFile=getArg('--theme-zip'), outDir=getArg('--out');
  assert.ok(srcFile&&manifestFile&&zipFile&&outDir,'Required four file/directory flags');
  for(const p of [srcFile,manifestFile,zipFile]) assert.notEqual(resolve(p),resolve(outDir));
  const candidate=await readFile(resolve(srcFile)),manifest=JSON.parse(await readFile(resolve(manifestFile),'utf8'));
  validateCandidate(candidate,manifest);
  const zip=await readFile(resolve(zipFile));
  assert.ok(zip.length>10000&&zip.length<10000000&&zip[0]===0x50&&zip[1]===0x4b,'Invalid theme ZIP');
  const [{runCLI},{chromium},axe]=await Promise.all([
    import('@wp-playground/cli'),import('playwright'),import('axe-core')
  ]);
  const axeSource=axe.default?.source||axe.source;
  assert.ok(typeof axeSource==='string' && axeSource.length>10000,'axe unavailable; FAIL CLOSED');
  const token=randomBytes(32).toString('hex');
  let server, browser, context, draft=false, failure=null, results=[];
  const receipts={candidate_sha256:hash(candidate),theme_zip_sha256:hash(zip),
    theme_version:'UNKNOWN',source_controlled_files:Object.keys(manifest.source_sha256||{}).length,
    release:'HOLD',stage_environment:'EPHEMERAL_LOCAL_PLAYGROUND_NOT_WORDPRESS_COM'};
  try {
    server=await runCLI({command:'server',wp:'6.8',php:'8.3',port:9473,login:false});
    assert.ok(hostAllowed(server.serverUrl),'Refusing non-loopback Playground');
    const write=(name,value)=>server.playground.writeFile('/wordpress/'+name,value);
    await write('wp-content/fv-ex2-synthetic-only.marker','SYNTHETIC_TEST_FIXTURE_ONLY\n');
    await write('wp-content/fv-ex2-editor-token',token+'\n');
    await write('wp-content/fv-ex2-synthetic-candidate.html',candidate);
    await write('wp-content/fv-ex2-assembler.zip',zip);
    await write('fv_ex2_editor_qa_once.php',await readFile(join(HERE,'playground_gutenberg_editor_gate.php')));
    await write('fv_ex2_assembler_qa_once.php',await readFile(join(HERE,'playground_assembler_theme_gate.php')));
    browser=await chromium.launch({headless:true});
    context=await browser.newContext({viewport:{width:1440,height:900}});
    const act=async (action,theme=false)=>{
      const file=theme?'fv_ex2_assembler_qa_once.php':'fv_ex2_editor_qa_once.php';
      const u=new URL('/'+file+'?action='+action,server.serverUrl);
      assert.ok(hostAllowed(u.origin));
      const request=(v)=>context.request.post(v.toString(),{
        headers:{'X-FV-EX2-EDITOR-TOKEN':token},maxRedirects:0,failOnStatusCode:false,timeout:90000
      });
      let res=await request(u);
      if([301,302,303,307,308].includes(res.status())) {
        const location=new URL(res.headers().location||'',u);
        assert.ok(hostAllowed(location.origin)&&location.port===u.port&&location.pathname===u.pathname
          && (location.search===u.search || location.search===''),'Unsafe local redirect');
        res=await request(new URL(u.pathname+u.search,location.origin));
      }
      assert.ok((res.headers()['content-type']||'').includes('application/json'),'No JSON response');
      const body=await res.json();
      assert.equal(res.status(),200,JSON.stringify({action,status:res.status(),reason:body.reason}));
      return body;
    };
    const created=await act('create');
    assert.equal(created.result,'CREATED');
    assert.equal(created.source_sha256,hash(candidate));
    assert.ok(Number.isSafeInteger(created.draft_id)&&created.draft_id>0);
    draft=true;
    const staged=await act('install',true);
    assert.equal(staged.result,'ASSEMBLER_ACTIVE');
    assert.equal(staged.theme,'assembler');
    receipts.theme_version=staged.version;
    const login=await act('login');assert.equal(login.result,'LOGIN_SET');
    // Save through the actual Gutenberg data-store before checking front-end render.
    const editorPage=await context.newPage();
    const editorUrl=new URL('/wp-admin/post.php',server.serverUrl);
    editorUrl.searchParams.set('post',String(created.draft_id));
    editorUrl.searchParams.set('action','edit');
    await editorPage.goto(editorUrl.toString(),{waitUntil:'domcontentloaded',timeout:90000});
    await editorPage.waitForFunction(id=>{
      const s=window.wp?.data?.select('core/editor');
      return s?.getCurrentPostId?.()===id && !s?.isSavingPost?.();
    },created.draft_id,{timeout:90000});
    const editorSaved=await editorPage.evaluate(async()=>{
      const select=window.wp.data.select('core/editor');
      const dispatch=window.wp.data.dispatch('core/editor');
      if(!dispatch?.savePost)throw new Error('Gutenberg editor store absent');
      dispatch.editPost({title:'FV EX2 SYNTHETIC EDITOR SAVED'});
      await dispatch.savePost();
      return {success:select.didPostSaveRequestSucceed(),
        failed:select.didPostSaveRequestFail(),
        draft:select.getEditedPostAttribute('status')==='draft'};
    });
    assert.deepEqual(editorSaved,{success:true,failed:false,draft:true});
    await editorPage.close();
    const preflight=await act('verify');
    assert.equal(preflight.result,'PASS');
    assert.equal(preflight.stored_sha256,hash(candidate));
    const render=async(width,{javascript=true,reducedMotion=false,tag='regular'}={})=>{
      const c=await browser.newContext({viewport:{width,height:900},javaScriptEnabled:javascript,
        reducedMotion:reducedMotion?'reduce':'no-preference'});
      try {
        // Use only the synthetic preview, never a WordPress.com URL.
        await c.addCookies(await context.cookies(server.serverUrl));
        const page=await c.newPage();
        const images=[];
        page.on('response',resp=>{
          if(resp.request().resourceType()==='image') images.push(resp);
        });
        const preview=new URL('/?page_id='+created.draft_id+'&preview=true',server.serverUrl);
        assert.ok(hostAllowed(preview.origin));
        const resp=await page.goto(preview.toString(),{waitUntil:'domcontentloaded',timeout:90000});
        assert.equal(resp?.status(),200,'Preview HTTP status not 200');
        await page.waitForSelector('[data-fv-home-flagship]',{timeout:45000});
        await page.waitForTimeout(1800);
        const metrics=await page.evaluate(()=>{
          const root=document.querySelector('[data-fv-home-flagship]');
          const nav=document.querySelector('.fv-hf__chapter-nav');
          const img=[...root.querySelectorAll('img')];
          return {title:document.title,theme:document.body.className,
            chapterLinks:[...nav?.querySelectorAll('a[href^="#"]')||[]].map(e=>e.getAttribute('href')),
            chapters:[...nav?.querySelectorAll('a[href^="#"]')||[]].every(e=>document.getElementById(e.hash.slice(1))),
            margins:document.querySelectorAll('.fv-margin-strip__item').length,
            focus:document.body.innerText.includes('Focus Fieldbook'),
            navPresent:!!nav,rootCount:document.querySelectorAll('[data-fv-home-flagship]').length,
            width:document.documentElement.scrollWidth, viewport:window.innerWidth,
            images:img.map(i=>({loaded:i.complete&&i.naturalWidth>0, width:i.naturalWidth}))
          };
        });
        assert.equal(metrics.rootCount,1);
        assert.equal(metrics.chapterLinks.length,7);
        assert.equal(metrics.chapters,true);
        assert.equal(metrics.margins,72);
        assert.equal(metrics.focus,true);
        assert.equal(metrics.navPresent,true);
        assert.ok(metrics.width<=metrics.viewport+1,'Horizontal overflow');
        assert.ok(metrics.images.length>=1,'No archival image in document');
        assert.ok(metrics.images.every(i=>i.loaded),'At least one archival image did not load');
        // Network response bytes—not media metadata and not DOM naturalWidth.
        const imageTransfers=await Promise.all(images.map(async r=>{
          let bytes=0;
          try{bytes=(await r.body()).length;}catch{}
          return {host:new URL(r.url()).hostname,status:r.status(),bytes,
            type:(r.headers()['content-type']||'').split(';')[0]};
        }));
        assert.ok(imageTransfers.some(x=>x.status===200&&x.bytes>0&&x.type.startsWith('image/')),
          'No verified image response body bytes');
        // axe must actually execute in this exact rendered WordPress DOM.
        await page.addScriptTag({content:axeSource});
        const accessibility=await page.evaluate(async()=>{
          if(!window.axe) throw new Error('axe missing');
          const r=await window.axe.run(document,{runOnly:{type:'tag',
            values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}});
          return {violations:r.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.length})),
            passes:r.passes.length,incomplete:r.incomplete.length};
        });
        assert.equal(accessibility.violations.length,0,'axe WCAG violations in rendered WordPress preview');
        await mkdir(resolve(outDir),{recursive:true});
        const screenshot='assembler_'+width+'_'+tag+'.png';
        await page.screenshot({path:join(resolve(outDir),screenshot),fullPage:false,animations:'disabled'});
        return {width,javascript,reducedMotion,tag,metrics,imageTransfers,accessibility,screenshot};
      } finally{await c.close();}
    };
    for(const width of [320,390,768,1440,1920]) results.push(await render(width));
    results.push(await render(390,{javascript:false,reducedMotion:true,tag:'nojs_reduced'}));
    const verified=await act('verify');
    assert.equal(verified.result,'PASS');
    assert.equal(verified.stored_sha256,hash(candidate));
    receipts.render_cases=results;
    receipts.editor_raw_hash_verified=true;
  } catch(e){failure=e;}
  finally {
    let cleaned=!draft;
    if(draft&&server&&context) {
      try {
        const u=new URL('/fv_ex2_editor_qa_once.php?action=cleanup',server.serverUrl);
        const res=await context.request.post(u.toString(),{headers:{'X-FV-EX2-EDITOR-TOKEN':token},
          maxRedirects:0,failOnStatusCode:false,timeout:30000});
        if(res.status()===200){const b=await res.json();cleaned=b.result==='DELETED'&&b.verified_absent===true;}
      } catch{}
    }
    if(!cleaned)failure=new Error('FAIL CLOSED: draft deletion not verified');
    receipts.draft_removed=cleaned;
    if(browser)await browser.close();
    if(server)await server[Symbol.asyncDispose]();
  }
  if(failure) {
    console.error(JSON.stringify({result:'HOLD',error:failure.message,
      completed_cases:results.map(r=>({width:r.width,tag:r.tag}))}));
    process.exitCode=1;
  } else {
    receipts.result='PASS';
    const receiptFile=join(resolve(outDir),'assembler_visual_manifest.json');
    await writeFile(receiptFile,JSON.stringify(receipts,null,2)+'\n');
    console.log(JSON.stringify({result:'PASS',candidate_sha256:receipts.candidate_sha256,
      theme_version:receipts.theme_version,cases:results.length,draft_removed:true,
      image_bytes:results.map(x=>x.imageTransfers.map(i=>i.bytes)),release:'HOLD'}));
  }
}
