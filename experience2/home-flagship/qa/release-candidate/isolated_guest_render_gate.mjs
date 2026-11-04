/** Genuine anonymous-visitor rendering check for an EDITOR-SAVED candidate.
 * Only an ephemeral HTTP-loopback WordPress Playground can be modified. An
 * isolated published COPY is needed because anonymous visitors cannot see a
 * WP draft. Original Gutenberg draft and production content are untouched.
 */
import assert from 'node:assert/strict';
import {join} from 'node:path';
import {readFile} from 'node:fs/promises';
import {validatePublishedMarginsFixture} from './playground_assembler_render_gate.mjs';
import {GUEST_VIEWPORTS,assertPublishedMarginParity,assertAnonymousNoJSState}
  from './guest_render_source_contract.mjs';

export function safeLocalUrl(raw, serverUrl) {
  try {
    const u=new URL(raw), base=new URL(serverUrl);
    const approved=h=>['localhost','127.0.0.1','[::1]'].includes(h);
    return u.protocol==='http:'&&base.protocol==='http:'&&
      approved(u.hostname)&&approved(base.hostname)&&
      !!u.port&&u.port===base.port&&
      !u.username&&!u.password&&!base.username&&!base.password;
  } catch{return false;}
}
export function isCookieFreeGuest(cookies) {
  return Array.isArray(cookies)&&!cookies.some(c=>
    /^(wordpress_logged_in_|wordpress_sec_|wp-settings-)/.test(c.name));
}
export function phpGuestCopy(draftId) {
  assert.ok(Number.isSafeInteger(draftId)&&draftId>0);
  return `<?php
require '/wordpress/wp-load.php';
function ex2_guest_refuse($s){ echo wp_json_encode(array('error'=>$s)); exit; }
$u=wp_parse_url(home_url('/'));
if (!is_array($u)||($u['scheme']??'')!=='http'||
 !in_array($u['host']??'',array('localhost','127.0.0.1','::1'),true)||
 empty($u['port'])||is_multisite()||get_stylesheet()!=='assembler')
 ex2_guest_refuse('Not isolated local Assembler');
$id=${draftId};
$draft=get_post($id);
if (!$draft||$draft->post_type!=='page'||$draft->post_status!=='draft'||
 $draft->post_title!=='FV EX2 SYNTHETIC EDITOR SAVED')
 ex2_guest_refuse('Not a verified Gutenberg candidate draft');
$content=$draft->post_content;
if (!is_string($content)||
 substr_count($content,'data-fv-home-flagship')<1||
 substr_count($content,'72 published historical fragments in isolated review')<1||
 substr_count($content,'data-fv-source=')!==4||
 substr_count($content,'jetpack/subscriptions')!==1)
 ex2_guest_refuse('Missing synthetic fixture custody markers');
$source_sha=hash('sha256',$content);
$copy=wp_insert_post(array('post_type'=>'page','post_status'=>'publish',
 'post_name'=>'fv-ex2-anonymous-review-'.wp_generate_password(12,false,false),
 'post_title'=>'EX2 ANONYMOUS LOCAL REVIEW — NOT A PUBLIC WEBSITE',
 'post_content'=>$content,'ping_status'=>'closed','comment_status'=>'closed',
 'to_ping'=>'','pinged'=>''),true);
if (is_wp_error($copy)||!$copy)ex2_guest_refuse('Local copy creation failed');
$created=get_post($copy);
if (!$created||hash('sha256',$created->post_content)!==$source_sha||
 $created->post_status!=='publish'){
 wp_delete_post($copy,true);
 ex2_guest_refuse('Local copy custody mismatch');
}
echo wp_json_encode(array('type'=>'EPHEMERAL_LOOPBACK_ANONYMOUS_COPY',
 'copy_id'=>$copy,'source_draft_id'=>$id,'source_sha256'=>$source_sha,
 'copy_sha256'=>hash('sha256',$created->post_content),
 'url'=>get_permalink($copy),'release'=>'HOLD'));`;
}
export function phpGuestDelete(copyId) {
  assert.ok(Number.isSafeInteger(copyId)&&copyId>0);
  return `<?php
require '/wordpress/wp-load.php';
$u=wp_parse_url(home_url('/'));
if (!is_array($u)||($u['scheme']??'')!=='http'||
 !in_array($u['host']??'',array('localhost','127.0.0.1','::1'),true)||
 empty($u['port'])||is_multisite()||get_stylesheet()!=='assembler'){
 echo wp_json_encode(array('error'=>'Not local Playground'));exit;
}
$id=${copyId};$p=get_post($id);
if (!$p||$p->post_type!=='page'||$p->post_status!=='publish'||
 !str_starts_with($p->post_title,'EX2 ANONYMOUS LOCAL REVIEW')){
 echo wp_json_encode(array('error'=>'Not a generated review copy'));exit;
}
wp_delete_post($id,true);
echo wp_json_encode(array('deleted'=>get_post($id)===null,'id'=>$id));`;
}
export function validateGuestReceipt(receipt,draftId,serverUrl) {
  assert.equal(receipt?.type,'EPHEMERAL_LOOPBACK_ANONYMOUS_COPY');
  assert.equal(receipt?.source_draft_id,draftId);
  assert.ok(Number.isSafeInteger(receipt?.copy_id)&&receipt.copy_id>0);
  assert.match(receipt?.source_sha256||'',/^[a-f0-9]{64}$/);
  assert.equal(receipt?.copy_sha256,receipt?.source_sha256);
  assert.ok(safeLocalUrl(receipt?.url,serverUrl),'Refusing nonlocal published copy URL');
  assert.equal(receipt?.release,'HOLD');
  return receipt;
}
async function restrictVisitorNetwork(page,base,blocked) {
  await page.route('**/*',route=>{
    const raw=route.request().url();
    if(safeLocalUrl(raw,base))return route.continue();
    // Keep archival imagery in the render: same two HTTPS first-party media
    // origins used by the existing Assembler admission harness.
    let u;
    try{u=new URL(raw);}catch {blocked.add('[invalid]');return route.abort();}
    if(u.protocol==='https:'&&['finalvestige.com','i0.wp.com'].includes(u.hostname)&&
       /\.(webp|png|jpe?g|svg)$/i.test(u.pathname)&&!u.username&&!u.password)
      return route.continue();
    blocked.add(u.hostname);return route.abort();
  });
}
export async function runIsolatedGuestRender({server,browser,draftId,axePath,outputDirectory}) {
  assert.ok(safeLocalUrl(server?.serverUrl,server?.serverUrl),'Local Playground only');
  assert.ok(typeof axePath==='string'&&axePath.endsWith('.js'));
  // Fail before any local copy/write if the PUBLIC source fixture drifts.
  const fixture=JSON.parse(await readFile(
    new URL('./public_page6_margins_20261102.json',import.meta.url),'utf8'));
  const publishedMargins=validatePublishedMarginsFixture(fixture);
  const raw=await server.playground.run({code:phpGuestCopy(draftId)});
  let receipt;
  try {receipt=JSON.parse(raw.text);}catch{throw new Error('Invalid local guest-copy receipt');}
  // A malformed response with a copy ID still must be deleted in the finally.
  const copyId=Number.isSafeInteger(receipt?.copy_id)?receipt.copy_id:null;
  let context=null;
  const blocked=new Set(),checks=[],failures=[];
  try {
    validateGuestReceipt(receipt,draftId,server.serverUrl);
    context=await browser.newContext({viewport:{width:390,height:844},reducedMotion:'reduce'});
    assert.ok(isCookieFreeGuest(await context.cookies()));
    for(const {width,height,kind} of GUEST_VIEWPORTS) {
      const page=await context.newPage();
      try {
        await page.setViewportSize({width,height});
        await restrictVisitorNetwork(page,server.serverUrl,blocked);
        await page.goto(receipt.url,{waitUntil:'domcontentloaded',timeout:90000});
        await page.locator('[data-fv-home-flagship]').waitFor({timeout:30000});
        // A DOMContentLoaded screenshot alone can record a broken folio.
        // Decode first-viewport archival images and resolve fonts before capture.
        // Still save the screenshot if decoding fails for review evidence.
        let paintFailure=null;
        try {
          await page.evaluate(async()=>{
            if(document.fonts?.ready)await document.fonts.ready;
            const visible=[...document.querySelectorAll('[data-fv-home-flagship] img')]
              .filter(el=>{const r=el.getBoundingClientRect();
                return r.width>0&&r.height>0&&r.bottom>0&&r.top<innerHeight;});
            await Promise.all(visible.map(async el=>{
              let timer;
              try {
                await Promise.race([el.decode(),new Promise((_,reject)=>{
                  timer=setTimeout(()=>reject(new Error('Visible image decode timeout')),15000);
                })]);
                if(!el.complete||!el.naturalWidth||!el.naturalHeight)
                  throw new Error('Visible image has no decoded pixels');
              } finally {clearTimeout(timer);}
            }));
          });
        } catch(e){paintFailure=String(e?.message||e).slice(0,250);}
        const state=await page.evaluate(()=>{
          const root=document.querySelector('[data-fv-home-flagship]');
          const cta=root?.querySelector('.fv-hf__mast-cta');
          const box=cta?.getBoundingClientRect();
          const cx=box?(box.left+box.right)/2:0;
          const cy=box?(box.top+box.bottom)/2:0;
          const pointed=(cx>=0&&cx<innerWidth&&cy>=0&&cy<innerHeight)?
            document.elementFromPoint(cx,cy):null;
          const css=cta?getComputedStyle(cta):null;
          return {admin_bar:!!document.querySelector('#wpadminbar'),
            logged_in:document.body.classList.contains('logged-in'),
            chapters:root?.querySelectorAll('.fv-hf__chapter-nav a').length||0,
            margins:document.querySelectorAll('.fv-margin-strip__item').length,
            cta_href:cta?.getAttribute('href'),
            cta_visible:!!box&&box.width>=44&&box.height>=44&&box.top>=0&&
              box.bottom<=innerHeight&&css?.visibility==='visible'&&
              Number(css?.opacity)>0&&!!pointed&&cta.contains(pointed),
            cta_top:box?.top,cta_height:box?.height,cta_width:box?.width,
            horizontal_overflow:document.documentElement.scrollWidth>innerWidth+1};
        });
        await page.screenshot({path:join(outputDirectory,`assembler-guest-${width}.png`),
          animations:'disabled',fullPage:false,timeout:30000});
        assertPublishedMarginParity(
          await page.locator('.fv-margin-strip__item').allTextContents(),publishedMargins);
        if(paintFailure)throw new Error('Guest first-screen media incomplete: '+paintFailure);
        if(state.admin_bar||state.logged_in||state.chapters!==7||state.margins!==72||
          state.cta_href!=='https://finalvestige.com/focus/'||!state.cta_visible||
          state.horizontal_overflow)throw new Error('Guest admission '+JSON.stringify(state));
        assert.ok(isCookieFreeGuest(await context.cookies()));
        // Test the real focus order, not merely the href or CSS rectangle.
        const mastCTA=page.locator('.fv-hf__mast-cta');
        await mastCTA.focus();
        assert.equal(await page.evaluate(()=>document.activeElement?.classList.contains('fv-hf__mast-cta')),true,
          'Guest Focus CTA cannot receive keyboard focus');
        await page.keyboard.press('Tab');
        assert.equal(await page.evaluate(()=>document.activeElement?.getAttribute('href')), '#fv-hf-title',
          'Guest Focus CTA must lead into seven-chapter keyboard navigation');
        await page.addScriptTag({path:axePath});
        const violations=await page.evaluate(async()=>{
          if(!window.axe)throw new Error('axe unavailable; fail closed');
          const r=await window.axe.run(document,{runOnly:{type:'tag',
            values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}});
          return r.violations.map(v=>({id:v.id,impact:v.impact,
            nodes:v.nodes.length,selectors:v.nodes.slice(0,2).map(n=>n.target)}));
        });
        checks.push({width,kind,state,whole_document_axe_violations:violations});
        if(violations.length)failures.push({width,reason:'Full-document axe: '+JSON.stringify(violations)});
      } catch(e){failures.push({width,reason:String(e?.message||e).slice(0,1200)});}
      finally{await page.close();}
    }
    const noContext=await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:844}});
    try {
      const page=await noContext.newPage();
      await restrictVisitorNetwork(page,server.serverUrl,blocked);
      await page.goto(receipt.url,{waitUntil:'domcontentloaded',timeout:90000});
      const noJS=await page.evaluate(()=>{
        const summary=document.querySelector('#fv-hf-observer-answer summary');
        const focus=document.querySelector('.fv-hf__observer-exit a[data-fv-destination="focus"]');
        const visible=el=>{if(!el||!el.getClientRects().length)return false;
          const c=getComputedStyle(el);
          return c.display!=='none'&&c.visibility==='visible'&&Number(c.opacity)>0;};
        const region=document.querySelector('.fv-margin-strip__window');
        const items=[...document.querySelectorAll('.fv-margin-strip__item')];
        const first=items[0];
        return {admin_bar:!!document.querySelector('#wpadminbar'),
          logged_in:document.body.classList.contains('logged-in'),
          details:!!summary,summary_visible:visible(summary),
          evidence:document.querySelectorAll('.fv-hf__observer-context a').length,
          focus:!!focus,focus_visible:visible(focus),
          margins:items.length,margin_texts:items.map(el=>el.textContent),
          margin_position:first?getComputedStyle(first).position:null,
          margin_opacity:first?getComputedStyle(first).opacity:null,
          window_overflow:region?getComputedStyle(region).overflowY:null,
          horizontal_overflow:document.documentElement.scrollWidth>innerWidth+1};
      });
      await page.screenshot({path:join(outputDirectory,'assembler-guest-390-nojs.png'),
        animations:'disabled',fullPage:false,timeout:30000});
      try {
        assertPublishedMarginParity(noJS.margin_texts,publishedMargins);
        assertAnonymousNoJSState(noJS);
      } catch(e) {
        failures.push({width:'390-nojs',reason:String(e?.message||e).slice(0,700)});
      }
      const {margin_texts:publicMarginalText,...noJSSummary}=noJS;
      checks.push({width:'390-nojs',state:noJSSummary});
    } finally {await noContext.close();}
  } finally {
    if(context)await context.close();
    if(copyId) {
      let deleted;
      try{const r=await server.playground.run({code:phpGuestDelete(copyId)});deleted=JSON.parse(r.text).deleted===true;}
      catch{deleted=false;}
      if(!deleted)throw new Error('FAIL CLOSED: temporary guest page cleanup unverified');
    }
  }
  if(failures.length)throw new Error('ANONYMOUS_VISITOR_RELEASE_HOLD '+JSON.stringify(failures));
  return {release:'HOLD',scope:'ANONYMOUS_LOOPBACK_ASSEMBLER_NOT_HOSTED_WPCOM',
    saved_copy_sha256:receipt.copy_sha256,checks,blocked_hosts:[...blocked].sort(),
    cleanup:'VERIFIED',limitation:'WordPress Playground is not WordPress.com Atomic or Jetpack'};
}
