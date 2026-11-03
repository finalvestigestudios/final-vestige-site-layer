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
function checkManifest(manifest, candidate) {
  assert.equal(manifest.data_classification, 'SYNTHETIC_TEST_FIXTURE_ONLY');
  assert.equal(manifest.page6_live_content_included, false);
  assert.equal(manifest.release, 'HOLD');
  assert.equal(manifest.candidate_sha256, sha(candidate));
  assert.equal(manifest.candidate_bytes, candidate.byteLength);
  assert.equal(manifest.margin_items, 72);
  assert.ok(manifest.gutenberg_custom_html_blocks >= 2);
  assert.equal(manifest.jetpack_block_comments, 1);
  assert.equal(manifest.nypl_record_links, 2);
  const source = candidate.toString('utf8');
  assert.equal((source.match(/<span class="fv-margin-strip__item" style="--i:\d+">/g) || []).length, 72);
  assert.equal((source.match(/jetpack\/subscriptions/g) || []).length, 1);
  assert.equal((source.match(/FV-EX2 PAGE6 REVIEW-ONLY/g) || []).length, 1);
  assert.ok(source.includes('Focus Fieldbook') && source.includes('fv-hf__chapter-nav'));
  assert.ok(!source.includes('https://finalvestige.com/wp-json/'));
}
function checkEditorReceipt(receipt, digest) {
  assert.equal(receipt.result, 'PASS');
  assert.equal(receipt.release, 'HOLD');
  assert.equal(receipt.test_type, 'REAL_GUTENBERG_EDITOR_SAVE_SYNTHETIC_PLAYGROUND_ONLY');
  assert.equal(receipt.data_class, 'SYNTHETIC_TEST_FIXTURE_ONLY');
  assert.equal(receipt.source_sha256, digest);
  assert.equal(receipt.stored_sha256, digest);
  assert.equal(receipt.source_bytes, receipt.stored_bytes);
  assert.equal(Object.keys(receipt.checks || {}).length, 9);
  for (const v of Object.values(receipt.checks)) assert.equal(v, true);
}
function selfTest() {
  let total = 0;
  const accept = (u) => { assert.equal(loopback(u), true); total++; };
  const deny = (u) => { assert.equal(loopback(u), false); total++; };
  accept('http://127.0.0.1:9473/');
  accept('http://localhost:1234/');
  accept('http://[::1]:9473/');
  for (const u of [
    'https://finalvestige.com/', 'http://finalvestige.com:9473/',
    'https://localhost:9473/', 'http://localhost/',
    'http://localhost:9473@finalvestige.com/', 'http://user@127.0.0.1:9473/',
    'http://127.0.0.2:9473/', 'file:///tmp/site',
    'http://finalvestige.com.evil:9473/', 'not-a-url'
  ]) deny(u);
  const candidate = Buffer.from('mock material');
  const manifest = {data_classification:'SYNTHETIC_TEST_FIXTURE_ONLY',page6_live_content_included:false,
    release:'HOLD',candidate_sha256:sha(candidate),candidate_bytes:candidate.length,
    margin_items:72,gutenberg_custom_html_blocks:2,jetpack_block_comments:1,nypl_record_links:2};
  assert.throws(() => checkManifest(manifest,candidate)); total++; // no synthetic markup
  assert.throws(() => checkManifest({...manifest,release:'APPROVED'},candidate)); total++;
  const checks = Object.fromEntries(Array.from({length:9},(_,i)=>['check'+i,true]));
  const pass = {result:'PASS',release:'HOLD',test_type:'REAL_GUTENBERG_EDITOR_SAVE_SYNTHETIC_PLAYGROUND_ONLY',
    data_class:'SYNTHETIC_TEST_FIXTURE_ONLY',source_sha256:'a',stored_sha256:'a',
    source_bytes:5,stored_bytes:5,checks};
  checkEditorReceipt(pass,'a');total++;
  for(const invalid of [
    {...pass,stored_sha256:'b'}, {...pass,checks:{...checks,check4:false}},
    {...pass,release:'LIVE'}, {...pass,result:'FAIL'},
    {...pass,source_bytes:6}, {...pass,checks:{}}
  ]) { assert.throws(()=>checkEditorReceipt(invalid,'a')); total++; }
  console.log(JSON.stringify({self_test:'PASS',cases:total,network_used:false,release:'HOLD'}));
}
if (process.argv.includes('--self-test')) {
  selfTest();
} else {
  const idx = process.argv.indexOf('--candidate');
  const midx = process.argv.indexOf('--manifest');
  assert.ok(idx > -1 && midx > -1 && process.argv[idx+1] && process.argv[midx+1]);
  const candidatePath = resolve(process.argv[idx+1]);
  const manifestPath = resolve(process.argv[midx+1]);
  assert.notEqual(candidatePath, manifestPath);
  const candidate = await readFile(candidatePath);
  const manifest = JSON.parse(await readFile(manifestPath, 'utf8'));
  checkManifest(manifest,candidate);
  const digest = sha(candidate);
  // No imported Playground or Chromium package until source/manifest is admitted.
  const [{runCLI},{chromium}] = await Promise.all([
    import('@wp-playground/cli'), import('playwright')
  ]);
  const token = randomBytes(32).toString('hex');
  const probe = await readFile(join(HERE,'playground_gutenberg_editor_gate.php'));
  let server, browser, context, draftCreated = false;
  let failure = null;
  let proof = null;
  try {
    server = await runCLI({
      command:'server', wp:'6.8', php:'8.3', port:9473, login:true
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
    const act = async (action) => {
      const u = makeUrl(action);
      assert.ok(loopback(u.origin), 'Refusing a non-loopback WordPress POST target');
      const res = await context.request.post(u.toString(),{
        headers:{'X-FV-EX2-EDITOR-TOKEN':token}, timeout:90000,
        maxRedirects:0, failOnStatusCode:false
      });
      const body = await res.json();
      return {status:res.status(),body};
    };
    const created = await act('create');
    assert.equal(created.status,200);
    assert.equal(created.body.result,'CREATED');
    assert.equal(created.body.data_class,'SYNTHETIC_TEST_FIXTURE_ONLY');
    assert.equal(created.body.source_sha256,digest);
    const draftId = created.body.draft_id;
    assert.ok(Number.isSafeInteger(draftId) && draftId>0);
    draftCreated = true;
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
    proof = {result:'PASS',draft_removed:false,release:'HOLD',
      type:checked.body.test_type,sha256:digest,checks:checked.body.checks,
      candidate_bytes:checked.body.source_bytes};
  } catch(e) {
    failure = e;
  } finally {
    let cleaned = !draftCreated;
    if(draftCreated && server && context) {
      try {
        const u = new URL('/fv_ex2_editor_qa_once.php?action=cleanup',server.serverUrl);
        const res = await context.request.post(u.toString(),{
          headers:{'X-FV-EX2-EDITOR-TOKEN':token},
          timeout:30000,maxRedirects:0,failOnStatusCode:false
        });
        const b = await res.json();
        cleaned = res.status()===200 && b.result==='DELETED' && b.verified_absent===true;
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
