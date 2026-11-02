#!/usr/bin/env node
/** Genuine Lighthouse run on WordPress Playground's already admitted, authenticated
 * seven-chapter shortcode renderer. Chrome + cookies + private iframe URL stay local.
 * NEVER emit Lighthouse's raw LHR, URL, nonce, cookie, trace, browser profile or log.
 */
import { readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { execFileSync } from 'node:child_process';
import * as chromeLauncher from 'chrome-launcher';
import lighthouse from 'lighthouse';
import { chromium } from 'playwright-core';
import { sanitizedSample, buildReceipt } from './lighthouse_receipt.mjs';

const BASE='http://127.0.0.1:9400/';
const REVIEW=BASE+'?pagename=fv-ex2-playground-review';
const FRAME_TITLE='Final Vestige Experience 2.0, unpublished editorial preview';
const get=(flag)=>{const pos=process.argv.indexOf(flag);return pos>0?process.argv[pos+1]:null;};
let chrome, browser;
async function main() {
  const repo=get('--repo'), sha=get('--expected-head'), statePath=get('--storage-state'), out=get('--out');
  if (!repo||!sha||!statePath||!out||!/^[0-9a-f]{40}$/.test(sha)) throw Error('ARGS_INVALID');
  const actual=execFileSync('git',['-C',repo,'rev-parse','HEAD'],{encoding:'utf8',stdio:['ignore','pipe','ignore']}).trim();
  if (actual!==sha) throw Error('SOURCE_HEAD_CHANGED');
  const state=JSON.parse(readFileSync(statePath,'utf8'));
  if (!Array.isArray(state.cookies)||!state.cookies.some(c=>c.name.startsWith('wordpress_logged_in'))) {
    throw Error('PRIVATE_WORDPRESS_LOGIN_MISSING');
  }
  for(const cookie of state.cookies) {
    if(cookie.domain!=='127.0.0.1') throw Error('NON_LOOPBACK_COOKIE_REFUSED');
  }
  chrome=await chromeLauncher.launch({
    chromePath: chromium.executablePath(),
    chromeFlags: ['--headless=new','--no-sandbox','--disable-dev-shm-usage',
      '--disable-background-networking','--disable-extensions']
  });
  browser=await chromium.connectOverCDP('http://127.0.0.1:'+chrome.port);
  const context=browser.contexts()[0];
  if(!context) throw Error('CHROME_DEFAULT_CONTEXT_MISSING');
  await context.addCookies(state.cookies);
  const probe=await context.newPage();
  try {
    await probe.goto(REVIEW,{waitUntil:'domcontentloaded',timeout:45000});
    const frame=probe.locator('iframe[title="'+FRAME_TITLE+'"]');
    await frame.waitFor({state:'attached',timeout:20000});
    if ((await frame.getAttribute('sandbox')||'').split(/\s+/).sort().join(' ')!==
        ['allow-popups','allow-scripts'].sort().join(' ')) throw Error('PREVIEW_SANDBOX_CHANGED');
    const src=await frame.getAttribute('src');
    if (!src) throw Error('PRIVATE_RENDERER_MISSING');
    const u=new URL(src,REVIEW);
    if (u.protocol!=='http:'||u.hostname!=='127.0.0.1'||u.port!=='9400'||
        u.username||u.password) throw Error('NON_LOOPBACK_RENDERER_REFUSED');
    // Verify the renderer itself before Lighthouse: not a WordPress login page
    // or preview-shell iframe score masquerading as the seven-chapter experience.
    const direct=await context.newPage();
    try {
      const response=await direct.goto(u.href,{waitUntil:'domcontentloaded',timeout:45000});
      if (response?.status()!==200 ||
          await direct.locator('[data-fv-home-flagship]').count()!==1) {
        throw Error('CANONICAL_RENDERER_NOT_READY');
      }
    } finally { await direct.close(); }
    const results=[];
    const boundedProfiles=[];
    const profiles=[
      { name:'mobile_390', formFactor:'mobile',
        screenEmulation:{mobile:true,width:390,height:844,deviceScaleFactor:1,disabled:false}},
      { name:'desktop_1440',formFactor:'desktop',
        screenEmulation:{mobile:false,width:1440,height:900,deviceScaleFactor:1,disabled:false}}
    ];
    for(const p of profiles) {
      // Lighthouse owns browser navigation, but shares the same authenticated
      // default Chrome cookie jar. Disabling storage reset prevents login loss.
      const run=await lighthouse(u.href,{
        port:chrome.port,logLevel:'silent',output:'json',
        onlyCategories:['performance','accessibility','best-practices'],
        disableStorageReset:true,
        // Lighthouse's official desktop preset adjusts scoring calibration AND
        // simulated CPU/network. formFactor alone does not.
        preset:p.name==='desktop_1440'?'desktop':undefined,
        formFactor:p.formFactor,screenEmulation:p.screenEmulation,
        throttlingMethod:'simulate'
      });
      const lhr=run?.lhr;
      if (!lhr || lhr.finalUrl!==u.href) throw Error('LIGHTHOUSE_DID_NOT_AUDIT_PRIVATE_RENDERER');
      // Publish ONLY bounded emulation values to diagnose a profile-label
      // mismatch; never raw Lighthouse JSON, URLs, body, cookie or debug trace.
      const cfg=lhr.configSettings||{};
      const e=cfg.screenEmulation||{},t=cfg.throttling||{};
      const bounded=(value)=>typeof value==='number'&&Number.isFinite(value)&&value>=0&&value<=10000?value:null;
      boundedProfiles.push({
        profile:p.name,
        form_factor:['mobile','desktop'].includes(cfg.formFactor)?cfg.formFactor:'OTHER',
        effective_width_px:bounded(e.width),effective_height_px:bounded(e.height),
        effective_mobile:typeof e.mobile==='boolean'?e.mobile:null,
        cpu_multiplier:bounded(t.cpuSlowdownMultiplier),
      });
      writeFileSync(resolve(out,'LIGHTHOUSE_PROFILE_DIAGNOSTIC.json'),
        JSON.stringify({status:'DIAGNOSTIC_ONLY_RELEASE_HOLD',
          exact_source_commit:sha,profiles:boundedProfiles},null,2)+'\n',{mode:0o600});
      results.push(sanitizedSample(lhr,p.name));
    }
    const rec=buildReceipt(results,sha);
    // This file is the only Lighthouse artifact. NEVER persist raw LHR, devtools
    // trace, private URL, browser cookies, redirects or diagnosis stack.
    writeFileSync(resolve(out,'LIGHTHOUSE_PRIVATE_LAB.json'),JSON.stringify(rec,null,2)+'\n',{mode:0o600});
    process.stdout.write('LIGHTHOUSE_PRIVATE_LAB_RECEIPT_WRITTEN\n');
  } finally {await probe.close();}
}
try {await main();}
catch(e) {
  // Never forward arbitrary Lighthouse errors, which can contain nonce URLs.
  const safeCodes=new Set([
    'LIGHTHOUSE_EFFECTIVE_PROFILE_MISMATCH','LIGHTHOUSE_DID_NOT_AUDIT_PRIVATE_RENDERER',
    'CANONICAL_RENDERER_NOT_READY','LIGHTHOUSE_RUNTIME_FAILURE',
    'CATEGORY_SCORE_MISSING','AUDIT_METRIC_MISSING','PRIVATE_WORDPRESS_LOGIN_MISSING',
    'LIGHTHOUSE_VERSION_MISSING','SOURCE_HEAD_CHANGED','NON_LOOPBACK_COOKIE_REFUSED'
  ]);
  const classification=safeCodes.has(e?.message)?e.message:'OTHER_LIGHTHOUSE_PRIVATE_GATE_FAILURE';
  try {
    const output=get('--out');
    if (output) writeFileSync(resolve(output,'LIGHTHOUSE_FAILURE_CLASS.json'),
      JSON.stringify({status:'RELEASE_HOLD',code:classification},null,2)+'\n',{mode:0o600});
  } catch {}
  process.stderr.write('LIGHTHOUSE_PRIVATE_GATE_HOLD\n');
  process.exitCode=2;
} finally {
  try{await browser?.close();}catch{}
  try{await chrome?.kill();}catch{}
}
