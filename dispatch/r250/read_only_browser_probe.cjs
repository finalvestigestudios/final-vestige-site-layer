#!/usr/bin/env node
"use strict";
/**
 * R250 non-submitting VISITOR-ONLY browser probe.
 * This script DOES NOT create accounts, type an email, submit forms or log subscriber identities.
 * Browser engine must ALREADY be installed; script never installs dependencies.
 * Run: node dispatch/r250/read_only_browser_probe.cjs
 * Optional FV_PROBE_OUTDIR=/path OUTSIDE tracked repo. Screenshots: anonymous public page only.
 */
const fs=require("node:fs");
const path=require("node:path");
const os=require("node:os");
const {evaluateMatrix}=require("./browser_evidence_gate.cjs");
let chromium;
try {({chromium}=require("playwright"));}catch{
 console.error("BLOCKED: playwright is not installed. Do not install a service or alter production; hand to existing Claude/Site QA environment.");
 process.exit(2);
}
const TARGETS=["https://finalvestige.com/focus/","https://finalvestige.com/dispatch/"];
const OUT=process.env.FV_PROBE_OUTDIR||path.join(os.tmpdir(),"fv-dispatch-browser-proof-r250");
async function visibleCount(locator){let n=0;for(let i=0;i<await locator.count();i++)if(await locator.nth(i).isVisible())n++;return n;}
async function labeledVisibleCount(locator){let n=0;for(let i=0;i<await locator.count();i++){let el=locator.nth(i);if(!await el.isVisible())continue;
 if(await el.evaluate(e=>Boolean(e.labels&&e.labels.length)||Boolean(e.getAttribute("aria-label"))||Boolean(e.getAttribute("aria-labelledby"))))n++;}return n;}
async function safeProbe(browser,url,width) {
 const context=await browser.newContext({viewport:{width,height:900},storageState:{cookies:[],origins:[]},serviceWorkers:"block",permissions:[]});
 const page=await context.newPage();
 let blockedCount=0,browserErrors=0,openers=0,selfNavigation=0;
 // Network fail-closed: blocking *any* non-read request prevents email signup submissions even if page scripts try.
 await context.route("**/*",route=>{
   const method=route.request().method().toUpperCase();
   if(method!=="GET"&&method!=="HEAD"){blockedCount++;return route.abort("blockedbyclient");}
   return route.continue();
 });
 page.on("pageerror",()=>{browserErrors++;});
 try {
  await page.goto(url,{waitUntil:"domcontentloaded",timeout:30000});
  await page.waitForTimeout(1500); // allow client-side Jetpack hydration; does not interact with subscriber data
  const block=page.locator(".wp-block-jetpack-subscriptions");
  let emails=block.locator('input[type="email"]');
  let shown=await visibleCount(emails);
  if(!shown){
    // Only click an OPENING anchor/button outside a form, never a submit control.
    const openersList=block.locator("a,button");
    for(let i=0;i<Math.min(await openersList.count(),8);i++){
      let el=openersList.nth(i);
      if(!await el.isVisible())continue;
      const safe=await el.evaluate(e=>{
        if(e.closest("form"))return false;
        if(e.tagName==="BUTTON"&&(e.type||"submit").toLowerCase()==="submit")return false;
        if(e.tagName==="A"){try{let u=new URL(e.href);return u.protocol==="https:"&&u.hostname==="finalvestige.com";}catch{return false;}}
        return true;
      });
      if(!safe)continue;
      const before=page.url();
      try{await el.click({timeout:3000});openers++;await page.waitForTimeout(1100);
        if(page.url()!==before&&new URL(page.url()).pathname===new URL(before).pathname)selfNavigation++;
      }catch{browserErrors++;}
      break; // one non-submitting opener maximum
    }
  }
  emails=page.locator('.wp-block-jetpack-subscriptions input[type="email"], [role="dialog"] input[type="email"]');
  shown=await visibleCount(emails);
  const accessible=await labeledVisibleCount(emails);
  // Some WordPress actions are buttons with implicit submit type. Only count alongside visible email fields.
  const visibleSubmit=shown>0?await visibleCount(page.locator('.wp-block-jetpack-subscriptions button, .wp-block-jetpack-subscriptions input[type="submit"], [role="dialog"] button, [role="dialog"] input[type="submit"]')):0;
  // Keyboard-only navigation check from start. Never activate a focused control or send any keystroke containing data.
  await page.keyboard.press("ControlOrMeta+Home");
  let reached=false;
  for(let i=0;i<300;i++){
    await page.keyboard.press("Tab");
    if(await page.evaluate(()=>Boolean(document.activeElement?.closest?.(".wp-block-jetpack-subscriptions,[role=dialog]")))){reached=true;break;}
  }
  // Filename contains no query strings, subscriber data, or tokens; context is always anonymous.
  const tag=new URL(url).pathname.replaceAll("/","")||"home";
  await page.screenshot({path:path.join(OUT,tag+"-"+width+".png"),fullPage:false,animations:"disabled"});
  return {record_source:"UNAUTHENTICATED_PLAYWRIGHT_BROWSER",url,viewport_width:width,observed_at_utc:new Date().toISOString(),
    unauthenticated_context:true,blocked_non_get_requests:true,blocked_attempt_count:blockedCount,
    user_data_typed:false,form_submitted:false,received_email_sent:false,
    visible_email_inputs:shown,accessible_visible_email_inputs:accessible,visible_submit_controls:visibleSubmit,
    safe_openers_clicked:openers,self_navigation_count:selfNavigation,browser_errors:browserErrors,
    keyboard_reached_subscribe:reached};
 } catch {
  return {record_source:"UNAUTHENTICATED_PLAYWRIGHT_BROWSER",url,viewport_width:width,observed_at_utc:new Date().toISOString(),
   unauthenticated_context:true,blocked_non_get_requests:true,user_data_typed:false,form_submitted:false,received_email_sent:false,
   visible_email_inputs:0,accessible_visible_email_inputs:0,visible_submit_controls:0,
   safe_openers_clicked:openers,self_navigation_count:selfNavigation,browser_errors:browserErrors+1,keyboard_reached_subscribe:false};
 } finally {await context.close();}
}
(async()=>{
  fs.mkdirSync(OUT,{recursive:true});
  const browser=await chromium.launch({headless:true});
  const observations=[];
  try{for(const url of TARGETS)for(const width of [390,1440])observations.push(await safeProbe(browser,url,width));}
  finally{await browser.close();}
  const summary=evaluateMatrix(observations);
  const payload={protocol:"R250_NO_SUBMISSION",observations,summary};
  fs.writeFileSync(path.join(OUT,"redacted-observations.json"),JSON.stringify(payload,null,2)+"\n",{mode:0o600});
  console.log(JSON.stringify({output_directory:OUT,status:summary.status,missing:summary.missing,
    classifications:summary.items.map(x=>({page:x.url?.split("/")[3],width:x.viewport_width,result:x.classification})),
    no_form_submitted:true,no_emails_sent:true,release_authorized:false},null,2));
  process.exitCode=summary.status==="VISUAL_ONLY_COMPLETE"?0:1;
})().catch(()=>{console.error("BLOCKED: browser probe could not complete; no sending or signup attempted.");process.exitCode=2;});
