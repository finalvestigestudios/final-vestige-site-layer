/**
 * Offline, representative real-Chromium browser regression for published Page 6
 * archive case interactions; NOT live WordPress, Jetpack or source-equivalent staging.
 * Run with: node --test test_active_archive_browser_gate.mjs
 * Requires playwright + its Chromium; set FV_TEST_CHROMIUM to a system Chromium path.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import {activateArchiveCase} from './live_public_focus_browser_gate.mjs';

const CASES=['apollo','franklin','malbone'];
const WIDTHS=[320,390,768,1279,1280,1440,1920];
const svg='data:image/svg+xml,'+encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="180" height="130"><rect width="180" height="130" fill="#b8955e"/></svg>');
function fixture(enhanced=true){
  const buttons=CASES.map((id,i)=>`<button type="button" data-fv-case-button="${id}" aria-pressed="${i===0}">Open ${id}</button>`).join('');
  const panels=CASES.map((id,i)=>`<article data-fv-case="${id}" ${i?'hidden':''}><h2>${id}</h2><img alt="Synthetic ${id} illustration" loading="lazy" data-fv-archive-img src="${svg}"></article>`).join('');
  const script=enhanced?`<script>document.querySelectorAll('[data-fv-case-button]').forEach(b=>b.addEventListener('click',()=>{const id=b.dataset.fvCaseButton;document.querySelectorAll('[data-fv-case]').forEach(p=>p.hidden=p.dataset.fvCase!==id);document.querySelectorAll('[data-fv-case-button]').forEach(btn=>btn.setAttribute('aria-pressed',String(btn.dataset.fvCaseButton===id)));}));</script>`:'';
  return `<!doctype html><html lang="en"><meta charset="utf-8"><style>body{font:18px Georgia;background:#0a0a09;color:#f4efe6}button{min-height:44px;padding:12px;background:#183436;color:#fff}article{padding:12px}img{width:180px;height:130px}</style><main><div data-fv-case-buttons>${buttons}</div><div data-fv-case-stage>${panels}</div></main>${script}</html>`;
}
const opts=process.env.FV_TEST_CHROMIUM?{headless:true,executablePath:process.env.FV_TEST_CHROMIUM,args:['--no-sandbox']}:{headless:true};

test('hidden cases need actual selection before lazy archival image inspection at all seven widths',async()=>{
  const browser=await chromium.launch(opts);
  try{
    for(const width of WIDTHS){
      const page=await browser.newPage({viewport:{width,height:900},reducedMotion:'reduce'});
      try{
        await page.setContent(fixture());
        await assert.rejects(page.locator('[data-fv-case="franklin"] img').scrollIntoViewIfNeeded({timeout:250}),/Timeout|visible|hidden/i);
        for(const id of CASES){
          const result=await activateArchiveCase(page,id);
          assert.deepEqual(result.selected,[id]);
          const img=page.locator(`[data-fv-case="${id}"] img`);
          await img.scrollIntoViewIfNeeded({timeout:2000});
          await img.evaluate(el=>el.decode());
          assert.ok(await img.evaluate(el=>el.naturalWidth>0));
        }
        const key=page.locator('[data-fv-case-button="apollo"]');
        await key.focus();await key.press('Enter');
        assert.deepEqual(await page.locator('[data-fv-case]:not([hidden])').getAttribute('data-fv-case'),'apollo');
      }finally{await page.close();}
    }
  }finally{await browser.close();}
});

test('invalid case, missing controls and nonfunctional controls fail closed',async()=>{
  const browser=await chromium.launch(opts);
  try{
    const page=await browser.newPage();
    await page.setContent(fixture());
    await assert.rejects(activateArchiveCase(page,'other'),/Unexpected archive case/);
    await page.locator('[data-fv-case-button="franklin"]').evaluate(el=>el.remove());
    await assert.rejects(activateArchiveCase(page,'franklin'),/missing or duplicated/);
    await page.setContent(fixture(false));
    await assert.rejects(activateArchiveCase(page,'malbone'),/did not reveal/);
    await page.close();
  }finally{await browser.close();}
});
