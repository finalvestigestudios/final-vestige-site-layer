#!/usr/bin/env node
/* Final Vestige Dispatch R160 — signed-out first-click evidence capture.
 * READ-ONLY: no email entries, POST/PUT/PATCH/DELETE network requests are aborted.
 * Must be explicitly run by site QA with an already-installed Playwright; no installation/spend.
 * Never a complete opt-in / welcome / email-delivery test. */
"use strict";
const fs=require("node:fs");
const path=require("node:path");
const targets=[
  {label:"dispatch",id:523,url:"https://finalvestige.com/dispatch/"},
  {label:"focus",id:1579,url:"https://finalvestige.com/focus/"}
];
const viewports=[320,390,768,1440];
function isSafeCandidate(href,target){
  try{
    const u=new URL(href,target.url);
    if(u.origin!=="https://finalvestige.com"||u.hash) return false;
    if(u.pathname!=="/")return false;
    if([...u.searchParams.keys()].sort().join(",")!=="p,post_type")return false;
    return u.searchParams.get("post_type")==="page"&&u.searchParams.get("p")===String(target.id);
  }catch(_){return false;}
}
function redactOnly(d){
  // Do not serialize DOM, cookies, form values, referrers, response bodies, or email addresses.
  return {page:d.page,viewport:d.viewport,url_before:d.url_before,url_after:d.url_after,
    inputs_before:d.inputs_before,inputs_after:d.inputs_after,visible_inputs_before:d.visible_inputs_before,
    visible_inputs_after:d.visible_inputs_after,subscribe_links:d.subscribe_links,
    safe_link_clicked:d.safe_link_clicked,blocked_non_get:d.blocked_non_get,console_error_count:d.console_error_count,
    status:d.status,screen_file:d.screen_file};
}
async function probePage(browser,target,width,outdir){
  const context=await browser.newContext({viewport:{width,height:900},storageState:{cookies:[],origins:[]},serviceWorkers:"block"});
  const page=await context.newPage();let blocked=0,consoleErr=0;
  await context.route("**/*",async route=>{
    if(route.request().method().toUpperCase()!=="GET"){blocked++;await route.abort("blockedbyclient");}
    else await route.continue();
  });
  page.on("console",m=>{if(m.type()==="error")consoleErr++});
  page.on("pageerror",()=>{consoleErr++});
  const x={page:target.label,viewport:width,url_before:target.url,url_after:null,inputs_before:0,inputs_after:0,
    visible_inputs_before:0,visible_inputs_after:0,subscribe_links:0,safe_link_clicked:false,
    blocked_non_get:0,console_error_count:0,status:"UNOBSERVED",screen_file:null};
  try{
    const res=await page.goto(target.url,{waitUntil:"domcontentloaded",timeout:25000});
    await page.waitForTimeout(1000);
    const input=page.locator('input[type="email"]');
    x.inputs_before=await input.count();
    for(let i=0;i<x.inputs_before;i++)if(await input.nth(i).isVisible())x.visible_inputs_before++;
    const links=page.locator("a");const n=Math.min(await links.count(),250);let candidate=null;
    for(let i=0;i<n;i++){
      const a=links.nth(i);const text=(await a.innerText().catch(()=>"")).trim();
      const href=await a.getAttribute("href");
      if(/subscribe/i.test(text)&&href){x.subscribe_links++;if(!candidate&&isSafeCandidate(href,target)) candidate=a;}
    }
    // Only follow the known, read-only WP content-API self-page GET anchor.
    // Never touch buttons, form submitters, subscription endpoints, or offsite links.
    if(x.visible_inputs_before===0&&candidate&&await candidate.isVisible()){
      await candidate.click({timeout:3000}).catch(()=>{});
      x.safe_link_clicked=true;await page.waitForTimeout(1000);
    }
    x.inputs_after=await input.count().catch(()=>0);
    for(let i=0;i<x.inputs_after;i++)if(await input.nth(i).isVisible().catch(()=>false))x.visible_inputs_after++;
    x.url_after=new URL(page.url()).origin+new URL(page.url()).pathname;
    x.blocked_non_get=blocked;
    x.console_error_count=consoleErr;
    x.status=x.visible_inputs_after>0?"VISIBLE_EMAIL_INPUT_NO_SUBMISSION":
      "NO_VISIBLE_EMAIL_INPUT_BROWSER_REVIEW_REQUIRED";
    if(blocked>0)x.status="UNKNOWN_NON_GET_NETWORK_BLOCKED_DURING_READONLY_TEST";
    if(res&&res.status()>=400)x.status="UNKNOWN_HTTP_ERROR_"+res.status();
    x.screen_file=target.label+"-"+width+".png";
    await page.screenshot({path:path.join(outdir,x.screen_file),animations:"disabled",fullPage:false});
  }catch(e){x.status="UNKNOWN_NAVIGATION_OR_BROWSER_ERROR";x.blocked_non_get=blocked;
    // Intentionally do not emit raw error text, which may contain credentials or query strings.
  }finally{await context.close();}
  return redactOnly(x);
}
async function main(){
  if(!process.argv.includes("--run")){
    process.stdout.write("R160 read-only browser diagnostic. To run: node guest_firstclick_readonly.cjs --run --out=/tmp/fv-r160\nNo forms are submitted; all non-GET requests are blocked. Requires preinstalled Playwright and Chromium.\n");
    return;
  }
  const outArg=process.argv.find(x=>x.startsWith("--out="));
  const outdir=path.resolve(outArg?outArg.slice(6):"./r160-guest-capture");
  fs.mkdirSync(outdir,{recursive:true});
  let chromium;
  try{chromium=require("playwright").chromium;}catch(e){
    process.stderr.write("PLAYWRIGHT_NOT_INSTALLED; no browser tests executed. Do not install paid tools.\n");process.exitCode=2;return;
  }
  const browser=await chromium.launch({headless:true});
  try{
    const results=[];
    for(const t of targets)for(const w of viewports)results.push(await probePage(browser,t,w,outdir));
    const report={title:"FV R160 guest first-click only",read_only:true,email_submissions:0,
      confirmed_signups:null,delivered_welcomes:null,eligible_subscribers:null,merchant_orders:null,
      results,interpretation:"NO email input in a screenshot/API is not sufficient to declare a broken form; manual accessible interactive review remains required."};
    fs.writeFileSync(path.join(outdir,"sanitized-firstclick.json"),JSON.stringify(report,null,2)+"\n");
    process.stdout.write(JSON.stringify({captures:results.length,report:path.join(outdir,"sanitized-firstclick.json"),
      status:"OBSERVATION_ONLY_NO_SIGNUPS"})+"\n");
  }finally{await browser.close();}
}
if(require.main===module)main().catch(()=>{process.stderr.write("READONLY_BROWSER_QA_FAILED; no signup action taken\n");process.exitCode=2});
module.exports={isSafeCandidate,redactOnly};
