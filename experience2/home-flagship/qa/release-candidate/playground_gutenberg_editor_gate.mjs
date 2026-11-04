#!/usr/bin/env node
/**
 * FV EX2 REAL Gutenberg editor data-store save, ephemeral Playground ONLY.
 * Refuses production and non-synthetic inputs. Never logs cookies/tokens/content.
 * This is NOT WordPress.com/Assembler/Jetpack parity or permission to publish.
 *
 * Optional dependency (CI only): @wp-playground/cli@3.1.56, playwright@1.56.1
 * Self-checks run without npm/network: node this-file.mjs --self-test
 */
import assert from 'node:assert/strict';
import { createHash, randomBytes } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const sha = (bytes) => createHash('sha256').update(bytes).digest('hex');
const loopback = (url) => {
  try {
    const u = new URL(url);
    return u.protocol === 'http:' &&
      ['127.0.0.1', 'localhost', '[::1]'].includes(u.hostname) &&
      u.username === '' && u.password === '' && !!u.port;
  } catch { return false; }
};
// The disposable environment marker is SYNTHETIC_TEST_FIXTURE_ONLY, but the
// page payload now contains the 72 actual publicly published Margins texts.
// Never confuse an environment safety marker with data provenance.
const DATA_CLASS='PUBLIC_PAGE6_MARGINS_WITH_SYNTHETIC_JETPACK_FIXTURE';
const SOURCE_FILES=[
  'index.html','flagship.css','chronicle.css','chronicle-lens.css',
  'inquiry.css','observer-lab.css','reading-trail.css',
  'flagship.js','observer-lab.js','chronicle-lens.js','reading-trail.js'
].sort();
const CHAPTER_IDS=[
  'fv-hf-title','fv-hf-chronicle','fv-hf-evidence','fv-hf-inquiry',
  'fv-hf-method-title','fv-hf-observer','fv-hf-mind-title'
];
function checkManifest(manifest,candidate,fixtureBytes) {
  assert.equal(manifest.data_classification,DATA_CLASS,
    'Public-Margins payload misclassified as synthetic-only');
  assert.equal(manifest.page6_live_content_included,false);
  assert.equal(manifest.public_page6_margins_texts_included,true);
  assert.equal(manifest.other_page6_content_included,false);
  assert.equal(manifest.real_source_controlled_flagship,true);
  assert.equal(manifest.production_source_or_subscribers,'ONLY_PUBLIC_MARGINS_NO_PRIVATE_DATA');
  assert.equal(manifest.accessibility_performance_approval,'NOT_GRANTED');
  assert.equal(manifest.release,'HOLD');
  assert.equal(manifest.candidate_sha256,sha(candidate));
  assert.equal(manifest.candidate_bytes,candidate.byteLength);
  assert.equal(manifest.margin_items,72);
  assert.equal(manifest.gutenberg_custom_html_blocks,2);
  assert.equal(manifest.jetpack_block_comments,1);
  assert.equal(manifest.nypl_record_links,2);
  assert.equal(manifest.style_source_count,6);
  assert.equal(manifest.script_source_count,4);
  assert.equal(manifest.wordpress_main_landmark_adapted,true);
  assert.deepEqual(manifest.chapter_targets,CHAPTER_IDS);
  assert.deepEqual(Object.keys(manifest.source_sha256||{}).sort(),SOURCE_FILES);
  for(const digest of Object.values(manifest.source_sha256))
    assert.match(digest,/^[a-f0-9]{64}$/,'Invalid flagship source fingerprint');
  assert.match(manifest.assembler_saved_stage_css_sha256,/^[a-f0-9]{64}$/);
  assert.equal(manifest.public_fragment_fixture_sha256,sha(fixtureBytes),
    'Published public Margins fixture hash drift');
  const fixture=JSON.parse(fixtureBytes.toString('utf8'));
  assert.equal(fixture.source_site_id,256784396);
  assert.equal(fixture.source_page_id,6);
  assert.equal(fixture.source_url,'https://finalvestige.com/');
  assert.equal(fixture.status,'ISOLATED_WORDPRESS_PLAYGROUND_ONLY');
  assert.equal(fixture.fragment_count,72);
  assert.equal(fixture.source_modified,manifest.published_margins_source_modified);
  assert.ok(Array.isArray(fixture.items) && fixture.items.length===72);
  const source=candidate.toString('utf8');
  const records=new Set();
  for(let i=0;i<72;i++){
    const item=fixture.items[i];
    assert.equal(item.index,i,'Published Margins index drift');
    assert.ok(typeof item.text==='string' && item.text.length>0);
    assert.ok(!records.has(item.text),'Published Margins source duplicate');
    records.add(item.text);
    const escaped=item.text.replace(/&/g,'&amp;');
    assert.ok(source.includes('<span class="fv-margin-strip__item" style="--i:'+
      i+'">'+escaped+'</span>'),'Candidate is not the published Margins at index '+i);
  }
  assert.equal((source.match(/<span class="fv-margin-strip__item" style="--i:\d+">/g)||[]).length,72);
  assert.equal((source.match(/jetpack\/subscriptions/g)||[]).length,1);
  assert.equal((source.match(/<script data-fv-source=/g)||[]).length,4);
  assert.equal((source.match(/<style data-fv-stage-only=/g)||[]).length,2);
  assert.equal((source.match(/<!-- wp:html -->/g)||[]).length,2);
  assert.equal((source.match(/<!-- \/wp:html -->/g)||[]).length,2);
  assert.equal((source.match(/data-fv-embedded-main="wordpress-assembler"/g)||[]).length,1);
  assert.equal((source.match(/FV-EX2 PAGE6 REVIEW-ONLY/g)||[]).length,1);
  assert.ok(source.includes('Focus Fieldbook') && source.includes('fv-hf__chapter-nav'));
  assert.ok(!source.includes('https://finalvestige.com/wp-json/'));
}
function checkEditorReceipt(receipt, digest) {
  assert.equal(receipt.result, 'PASS');
  assert.equal(receipt.release, 'HOLD');
  assert.equal(receipt.test_type, 'REAL_GUTENBERG_EDITOR_SAVE_SYNTHETIC_PLAYGROUND_ONLY');
  assert.equal(receipt.data_class,DATA_CLASS);
  // Data class reports public Margins; synthetic-only is the loopback marker, not content.
  assert.equal(receipt.source_sha256, digest);
  assert.equal(receipt.stored_sha256, digest);
  assert.equal(receipt.source_bytes, receipt.stored_bytes);
  assert.equal(Object.keys(receipt.checks || {}).length, 9);
  for (const v of Object.values(receipt.checks)) assert.equal(v, true);
}
/** On a successful PHP create response, validate the whole creation receipt.
 * IMPORTANT: mark draftCreated BEFORE calling this function so that even a
 * malformed receipt results in verified disposable-draft cleanup. */
function checkCreatedReceipt(created,digest) {
  assert.equal(created.status,200,'Disposable WordPress create HTTP status');
  const body=created.body;
  assert.equal(body?.result,'CREATED');
  assert.equal(body?.release,'HOLD');
  assert.equal(body?.data_class,DATA_CLASS);
  assert.equal(body?.source_sha256,digest);
  assert.ok(Number.isSafeInteger(body?.draft_id) && body.draft_id>0,
    'Disposable WordPress draft ID invalid');
  return body.draft_id;
}
/** Shared fail-closed disposable HTTP transport, including final cleanup. */
async function postLocalAction(context,serverUrl,action,token) {
      const u = new URL('/fv_ex2_editor_qa_once.php?action='+action,serverUrl);
      assert.ok(loopback(u.origin), 'Refusing a non-loopback WordPress POST target');
      const request = (url) => context.request.post(url.toString(), {
        headers:{'X-FV-EX2-EDITOR-TOKEN':token}, timeout:90000,
        maxRedirects:0, failOnStatusCode:false
      });
      let res = await request(u);
      // Playground may canonicalize 127.0.0.1 ↔ localhost. Permit exactly
      // one same-PHP-route/same-port loopback-host correction. Never follow
      // redirects to login, external sites or a different action.
      if ([301,302,303,307,308].includes(res.status())) {
        const location = res.headers()['location'] || '';
        let target;
        try { target = new URL(location,u); } catch { target = null; }
        const safe = target && loopback(target.origin) &&
          target.pathname === u.pathname && target.port === u.port &&
          (target.search === u.search || target.search === '') &&
          !target.username && !target.password;
        if (!safe) {
          throw new Error('Blocked unsafe local WordPress redirect ' + res.status() +
            ' destination path ' + (target?.pathname || '[invalid]'));
        }
        const canonical = new URL(u.pathname + u.search, target.origin);
        res = await request(canonical);
      }
      const status = res.status();
      if ([301,302,303,307,308].includes(status)) {
        const location = res.headers()['location'] || '';
        let next;
        try { next = new URL(location,u); } catch { next=null; }
        throw new Error('Refusing second consecutive PHP route redirect ' + status +
          ' path ' + (next?.pathname || '[invalid]') +
          ' loopback=' + Boolean(next && loopback(next.origin)) +
          ' same_action=' + Boolean(next && next.search === u.search));
      }
      const contentType = res.headers()['content-type'] || '';
      if (!contentType.includes('application/json')) {
        throw new Error('Playground PHP route returned non-JSON HTTP ' + status +
          ' content-type=' + contentType.split(';')[0]);
      }
      const body = await res.json();
      return {status,body};
}

async function selfTest() {
  // Real public text fixture, synthetic candidate layout: no production CMS reads.
  const fixtureBytes=await readFile(join(HERE,'public_page6_margins_20261102.json'));
  const fixture=JSON.parse(fixtureBytes.toString('utf8'));
  const rows=fixture.items.map(({index,text})=>
    '<span class="fv-margin-strip__item" style="--i:'+index+'">'+
    text.replace(/&/g,'&amp;')+'</span>').join('');
  const candidate=Buffer.from(
    '<!-- wp:html -->FV-EX2 PAGE6 REVIEW-ONLY'+rows+'<!-- /wp:html -->'+
    '<!-- wp:html --><div data-fv-embedded-main="wordpress-assembler">'+
    'fv-hf__chapter-nav Focus Fieldbook <style data-fv-stage-only="a"></style>'+
    '<style data-fv-stage-only="b"></style>'+
    '<script data-fv-source="a"></script><script data-fv-source="b"></script>'+
    '<script data-fv-source="c"></script><script data-fv-source="d"></script>'+
    '<!-- /wp:html --><!-- wp:jetpack/subscriptions /-->');
  const checks=Object.fromEntries(Array.from({length:9},(_,i)=>['check'+i,true]));
  const manifest={
    data_classification:DATA_CLASS,page6_live_content_included:false,
    public_page6_margins_texts_included:true,other_page6_content_included:false,
    real_source_controlled_flagship:true,production_source_or_subscribers:'ONLY_PUBLIC_MARGINS_NO_PRIVATE_DATA',
    accessibility_performance_approval:'NOT_GRANTED',release:'HOLD',
    candidate_sha256:sha(candidate),candidate_bytes:candidate.length,margin_items:72,
    gutenberg_custom_html_blocks:2,jetpack_block_comments:1,nypl_record_links:2,
    style_source_count:6,script_source_count:4,wordpress_main_landmark_adapted:true,
    chapter_targets:CHAPTER_IDS,source_sha256:Object.fromEntries(SOURCE_FILES.map(x=>[x,'a'.repeat(64)])),
    assembler_saved_stage_css_sha256:'b'.repeat(64),
    public_fragment_fixture_sha256:sha(fixtureBytes),
    published_margins_source_modified:fixture.source_modified
  };
  let total=0;
  checkManifest(manifest,candidate,fixtureBytes);total++;
  const mutate=[
    ['data_classification','SYNTHETIC_TEST_FIXTURE_ONLY'],
    ['public_page6_margins_texts_included',false],
    ['other_page6_content_included',true],
    ['release','APPROVED'],
    ['candidate_sha256','0'.repeat(64)],
    ['public_fragment_fixture_sha256','0'.repeat(64)],
    ['published_margins_source_modified','2020-01-01T00:00:00'],
    ['script_source_count',0],
    ['production_source_or_subscribers','PRODUCTION_DB_INCLUDED']
  ];
  for(const [key,value] of mutate){
    assert.throws(()=>checkManifest({...manifest,[key]:value},candidate,fixtureBytes));
    total++;
  }
  assert.throws(()=>checkManifest({...manifest,source_sha256:{}},candidate,fixtureBytes));total++;
  assert.throws(()=>checkManifest(manifest,Buffer.from(
    candidate.toString().replace('FV-EX2 PAGE6 REVIEW-ONLY','altered')),fixtureBytes));total++;
  for(const u of ['http://127.0.0.1:9473/','http://localhost:1234/','http://[::1]:9473/']){
    assert.ok(loopback(u));total++;
  }
  for(const u of ['https://finalvestige.com/','http://localhost/','http://localhost:9473@evil.test/',
    'http://user@127.0.0.1:9473/','http://127.0.0.2:9473/']){
    assert.ok(!loopback(u));total++;
  }
  const pass={
    result:'PASS',release:'HOLD',test_type:'REAL_GUTENBERG_EDITOR_SAVE_SYNTHETIC_PLAYGROUND_ONLY',
    data_class:DATA_CLASS,source_sha256:'a',stored_sha256:'a',source_bytes:5,stored_bytes:5,checks
  };

  // Real create() receipt contract, including regression for the old
  // SYNTHETIC_TEST_FIXTURE_ONLY mismatch that aborted before cleanup.
  const goodCreate={status:200,body:{result:'CREATED',release:'HOLD',
    data_class:DATA_CLASS,source_sha256:'a',draft_id:42}};
  assert.equal(checkCreatedReceipt(goodCreate,'a'),42);total++;
  const badCreates=[
    {...goodCreate,body:{...goodCreate.body,data_class:'SYNTHETIC_TEST_FIXTURE_ONLY'}},
    {...goodCreate,body:{...goodCreate.body,release:'LIVE'}},
    {...goodCreate,body:{...goodCreate.body,source_sha256:'tampered'}},
    {...goodCreate,body:{...goodCreate.body,draft_id:0}},
    {...goodCreate,body:{...goodCreate.body,draft_id:'42'}},
    {...goodCreate,body:{...goodCreate.body,result:'FAIL'}},
    {...goodCreate,status:422},
    {...goodCreate,body:null}
  ];
  for(const bad of badCreates){assert.throws(()=>checkCreatedReceipt(bad,'a'));total++;}
  checkEditorReceipt(pass,'a');total++;
  for(const invalid of [
    {...pass,data_class:'SYNTHETIC_TEST_FIXTURE_ONLY'},
    {...pass,stored_sha256:'b'}, {...pass,checks:{...checks,check4:false}},
    {...pass,release:'LIVE'}, {...pass,result:'FAIL'}, {...pass,source_bytes:6},
    {...pass,checks:{}}
  ]) {assert.throws(()=>checkEditorReceipt(invalid,'a'));total++;}

  // Asynchronous transport simulations: no network/WordPress required.
  const fake=(responses,hits=[])=>({request:{post:async(url,opts)=>{
    hits.push({url,opts});
    if(!responses.length)throw Error('Unexpected request');
    const r=responses.shift();
    return {status:()=>r.status,headers:()=>({'location':r.location||'',
      'content-type':r.contentType||'application/json'}),json:async()=>r.body};
  }}});
  const testToken='a'.repeat(64),deletedBody={result:'DELETED',verified_absent:true,release:'HOLD'};
  const directHits=[];
  const direct=await postLocalAction(fake([{status:200,body:deletedBody}],directHits),
    'http://127.0.0.1:9473/','cleanup',testToken);
  assert.equal(direct.body.verified_absent,true);
  assert.equal(directHits.length,1);
  assert.equal(directHits[0].opts.maxRedirects,0);total++;
  const canonicalHits=[];
  const canonical=await postLocalAction(fake([
    {status:301,location:'http://localhost:9473/fv_ex2_editor_qa_once.php'},
    {status:200,body:deletedBody}
  ],canonicalHits),'http://127.0.0.1:9473/','cleanup',testToken);
  assert.equal(canonical.body.result,'DELETED');
  assert.equal(canonicalHits.length,2);
  assert.ok(canonicalHits[1].url.includes('localhost:9473/fv_ex2_editor_qa_once.php?action=cleanup'));total++;
  for(const location of [
    'https://finalvestige.com/fv_ex2_editor_qa_once.php?action=cleanup',
    'http://evil.example:9473/fv_ex2_editor_qa_once.php?action=cleanup',
    'http://localhost:9474/fv_ex2_editor_qa_once.php?action=cleanup',
    'http://localhost:9473/wp-admin/',
    'http://localhost:9473/fv_ex2_editor_qa_once.php?action=create',
    'http://user@localhost:9473/fv_ex2_editor_qa_once.php?action=cleanup'
  ]){
    await assert.rejects(()=>postLocalAction(fake([{status:302,location}]),
      'http://127.0.0.1:9473/','cleanup',testToken),/unsafe local WordPress redirect/);total++;
  }
  await assert.rejects(()=>postLocalAction(fake([
    {status:301,location:'http://localhost:9473/fv_ex2_editor_qa_once.php'},
    {status:302,location:'http://127.0.0.1:9473/fv_ex2_editor_qa_once.php'}
  ]),'http://127.0.0.1:9473/','cleanup',testToken),/second consecutive/);total++;
  await assert.rejects(()=>postLocalAction(fake([
    {status:200,contentType:'text/html',body:deletedBody}
  ]),'http://127.0.0.1:9473/','cleanup',testToken),/non-JSON/);total++;
  console.log(JSON.stringify({self_test:'PASS',cases:total,fixture_sha256:sha(fixtureBytes),
    data_class:DATA_CLASS,network_used:false,release:'HOLD'}));
}
if (process.argv.includes('--self-test')) {
  await selfTest();
} else {
  const idx = process.argv.indexOf('--candidate');
  const midx = process.argv.indexOf('--manifest');
  assert.ok(idx > -1 && midx > -1 && process.argv[idx+1] && process.argv[midx+1]);
  const candidatePath = resolve(process.argv[idx+1]);
  const manifestPath = resolve(process.argv[midx+1]);
  assert.notEqual(candidatePath, manifestPath);
  const candidate = await readFile(candidatePath);
  const manifest = JSON.parse(await readFile(manifestPath, 'utf8'));
  const fixtureBytes=await readFile(join(HERE,'public_page6_margins_20261102.json'));
  checkManifest(manifest,candidate,fixtureBytes);
  const digest = sha(candidate);
  // No imported Playground or Chromium package until source/manifest is admitted.
  const [{runCLI},{chromium}] = await Promise.all([
    import('@wp-playground/cli'), import('playwright')
  ]);
  const token = randomBytes(32).toString('hex');
  const probe = await readFile(join(HERE,'playground_gutenberg_editor_gate.php'));
  let server, browser, context, draftCreated = false, act;
  let failure = null;
  let proof = null;
  try {
    server = await runCLI({
      command:'server', wp:'6.8', php:'8.3', port:9473, login:false
    });
    assert.ok(loopback(server.serverUrl), 'Playground server must be HTTP loopback with explicit port');
    await server.playground.writeFile('/wordpress/wp-content/fv-ex2-synthetic-only.marker',
      'SYNTHETIC_TEST_FIXTURE_ONLY\n');
    await server.playground.writeFile('/wordpress/wp-content/fv-ex2-synthetic-candidate.html',candidate);
    await server.playground.writeFile('/wordpress/wp-content/fv-ex2-editor-token',token+'\n');
    await server.playground.writeFile('/wordpress/fv_ex2_editor_qa_once.php',probe);
    const makeUrl = (action) => new URL('/fv_ex2_editor_qa_once.php?action='+action,server.serverUrl);
    browser = await chromium.launch({headless:true});
    context = await browser.newContext({viewport:{width:1440,height:900}});
    act = (action) => postLocalAction(context,server.serverUrl,action,token);
    const created = await act('create');
    // A CREATED response means a temporary draft may exist. Arm cleanup
    // BEFORE validating the receipt: corrupted data-class or digest must
    // never leave a test draft orphaned.
    draftCreated = created.status===200 && created.body?.result==='CREATED';
    const draftId = checkCreatedReceipt(created,digest);
    const login = await act('login');
    assert.equal(login.status,200);
    assert.equal(login.body.result,'LOGIN_SET');
    const page = await context.newPage();
    const editorUrl = new URL('/wp-admin/post.php',server.serverUrl);
    editorUrl.searchParams.set('post',String(draftId));
    editorUrl.searchParams.set('action','edit');
    await page.goto(editorUrl.toString(),{waitUntil:'domcontentloaded',timeout:90000});
    await page.waitForFunction((id) => {
      const s = window.wp?.data?.select('core/editor');
      return s?.getCurrentPostId?.() === id && !s?.isSavingPost?.();
    },draftId,{timeout:90000});
    const editor = await page.evaluate(async () => {
      const sel=window.wp.data.select('core/editor');
      const dispatch=window.wp.data.dispatch('core/editor');
      if(!sel || !dispatch || typeof dispatch.savePost !== 'function') throw new Error('No Gutenberg editor data-store');
      dispatch.editPost({title:'FV EX2 SYNTHETIC EDITOR SAVED'});
      await dispatch.savePost();
      return {
        saved:sel.didPostSaveRequestSucceed(),
        failed:sel.didPostSaveRequestFail(),
        draft:sel.getEditedPostAttribute('status') === 'draft'
      };
    });
    assert.deepEqual(editor,{saved:true,failed:false,draft:true},
      'Gutenberg editor Save did not complete cleanly');
    const checked = await act('verify');
    assert.equal(checked.status,200,'Stored editor content was not admitted');
    checkEditorReceipt(checked.body,digest);
    // Optional additional REAL front-end browser gate; still disposable and
    // staged. A failure here must trigger the original mandatory draft cleanup.
    let assemblerEvidence = null;
    const assemblerIdx=process.argv.indexOf('--assembler-dir');
    if(assemblerIdx !== -1){
      const evidenceIdx=process.argv.indexOf('--evidence-dir');
      assert.ok(process.argv[assemblerIdx+1] && evidenceIdx>0 &&
        process.argv[evidenceIdx+1], 'Assembler rendering requires theme and evidence dirs');
      const mod=await import('./playground_assembler_render_gate.mjs');
      assemblerEvidence=await mod.runAssemblerPreview({
        server,browser,context,draftId,
        themeDirectory:resolve(process.argv[assemblerIdx+1]),
        outputDirectory:resolve(process.argv[evidenceIdx+1])
      });
    }
    proof = {result:'PASS',draft_removed:false,release:'HOLD',
      assembler_render:assemblerEvidence,
      type:checked.body.test_type,sha256:digest,checks:checked.body.checks,
      candidate_bytes:checked.body.source_bytes};
  } catch(e) {
    failure = e;
  } finally {
    let cleaned = !draftCreated;
    if(draftCreated && server && context && act) {
      try {
        // Reuse the same guarded POST and canonicalization policy as create.
        const deleted=await act('cleanup');
        cleaned=deleted.status===200 && deleted.body.result==='DELETED' &&
          deleted.body.verified_absent===true && deleted.body.release==='HOLD';
      } catch {cleaned=false; }
    }
    if(!cleaned) failure = new Error('FAIL CLOSED: disposable Gutenberg draft deletion unverified');
    if(browser) await browser.close();
    if(server) await server[Symbol.asyncDispose]();
    if(proof && !failure) {
      proof.draft_removed = true;
      console.log(JSON.stringify(proof,null,2));
    }
  }
  if(failure) throw failure;
}
