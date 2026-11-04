'use strict';
// R125: source contracts, not a substitute for full Chromium/axe execution.
// Usage: node --test experience2/apollo-creator-bridge/test_r125_actual_navigation_contract.cjs
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const root=__dirname;
const runner=fs.readFileSync(path.join(root,'qa_r113_print.py'),'utf8');
const html=fs.readFileSync(path.join(root,'landing-preview.html'),'utf8');
const count=(s,term)=>s.split(term).length-1;
test('Playwright browser opens the real HTTP document, never document.write',()=>{
  assert.equal(count(runner,'page.set_content('),0);
  assert.match(runner,/page\.goto\(url,wait_until='load',timeout=15000\)/);
});
test('Loopback server serves exact tracked HTML bytes, not reconstructed fixture',()=>{
  assert.match(runner,/payload=html\.read_bytes\(\)/);
  assert.match(runner,/ThreadingHTTPServer\(\('127\.0\.0\.1',0\),Handler\)/);
});
test('Local server rejects unrelated routes',()=>{
  assert.match(runner,/self\.path\.split\('\?',1\)\[0\]!='\/landing-preview\.html'/);
  assert.match(runner,/self\.send_error\(404\)/);
});
test('Server lifecycle is bound to browser run including failure',()=>{
  assert.match(runner,/with serve_canonical_landing\(html\) as target, sync_playwright\(\) as p:/);
  assert.match(runner,/server\.shutdown\(\)/);
  assert.match(runner,/server\.server_close\(\)/);
});
test('Browser response must be 200 with URL and navigation timing',()=>{
  assert.match(runner,/response\.status==200 and page\.url==url/);
  assert.match(runner,/performance\.getEntriesByType\('navigation'\)/);
});
test('Blocked network navigation cannot be silently replaced with a fixture',()=>{
  assert.match(runner,/NAVIGATION_BLOCKED/);
  assert.match(runner,/ACTUAL_NAVIGATION_FAILED/);
  assert.match(runner,/document\.write fallback prohibited/);
});
test('Source identity remains tied to git HEAD and canonical path',()=>{
  assert.match(runner,/EXACT_GIT_HEAD/);
  assert.match(runner,/HEAD_SOURCE_MISMATCH/);
  assert.match(runner,/NOT_CANONICAL_LANDING/);
});
test('Full matrix still exercises no JS and JavaScript at 320-1920 widths',()=>{
  assert.match(runner,/WIDTHS=\(320,360,390,768,1024,1440,1920\)/);
  assert.match(runner,/for js in \(False,True\):/);
});
test('LCP observer installs prior to navigation and requires a real entry',()=>{
  const start=runner.indexOf("page.add_init_script(script='('+PERF_INIT+')()')");
  const nav=runner.indexOf("navigate_actual_page(page,target,f'performance-");
  const obs=runner.indexOf("window.__fv_perf && window.__fv_perf.lcp !== null");
  assert.ok(start>=0&&nav>start&&obs>nav);
});
test('Performance evidence remains labeled laboratory, not field',()=>{
  assert.match(runner,/lab_only':True/);
  assert.match(runner,/lcp<=2500 and cls<=0\.1/);
});
test('axe requires an approved bundle and verifies axe.run actually exists',()=>{
  assert.match(runner,/AXE_BUNDLE_REQUIRED/);
  assert.match(runner,/typeof window\.axe\.run === 'function'/);
  assert.match(runner,/len\(record\['axe_scans'\]\)==4/);
});
test('Browser runner must require screenshots, teacher and worksheet PDFs',()=>{
  assert.match(runner,/len\(record\['screenshots'\]\)==2/);
  assert.match(runner,/record\['worksheet_pdf'\] is not None/);
});
test('Preview Escape handler listens on document instead of trapping focus',()=>{
  assert.match(html,/document\.addEventListener\('keydown',function\(event\)\{/);
  assert.match(html,/event\.key==='Escape'&&sheet\.classList\.contains\('fv-student-preview'\)/);
  assert.doesNotMatch(html,/sheet\.addEventListener\('keydown',function\(event\)/);
});
test('Actual-page test checks Escape after user focuses outside the worksheet',()=>{
  assert.match(runner,/global Escape failed after focus left preview/);
  assert.match(runner,/page\.locator\('\[data-fv-primary-cta\]'\)\.focus\(\)/);
});
test('The approved primary route remains free and without checkout or form',()=>{
  assert.equal(count(html,'data-fv-primary-cta'),1);
  assert.doesNotMatch(html,/<form\b|<iframe\b|<script\b[^>]*src=|sendBeacon\s*\(/i);
  assert.doesNotMatch(html,/<a\b[^>]*payhip/i);
});
test('NASA photographic source custody and uncertain catalog ID remain explicit',()=>{
  assert.equal((html.match(/data-fv-student-photo="0[1-6]"/g)||[]).length,6);
  assert.match(html,/S67-19766/);
  assert.match(html,/0\/6/);
});
test('Receipt includes exact git HEAD commit SHA and refuses missing SHA',()=>{
  assert.match(runner,/git_head_sha=git_head_sha\(\)/);
  assert.match(runner,/\['git','rev-parse','HEAD'\]/);
  assert.match(runner,/or not record\['git_head_sha'\]/);
});
