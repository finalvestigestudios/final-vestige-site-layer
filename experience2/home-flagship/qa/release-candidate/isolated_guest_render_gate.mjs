/** Genuine anonymous-visitor rendering check for an EDITOR-SAVED candidate.
 * Only an ephemeral HTTP-loopback WordPress Playground can be modified. An
 * isolated published COPY is needed because anonymous visitors cannot see a
 * WP draft. Original Gutenberg draft and production content are untouched.
 */
import assert from 'node:assert/strict';
import {join} from 'node:path';

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
    for(const width of [360,390,768,1440,1920]) {
      const page=await context.newPage();
      try {
        await page.setViewportSize({width,height:900});
        await restrictVisitorNetwork(page,server.serverUrl,blocked);
        await page.goto(receipt.url,{waitUntil:'domcontentloaded',timeout:90000});
        await page.locator('[data-fv-home-flagship]').waitFor({timeout:30000});
        const state=await page.evaluate(()=>{
          const root=document.querySelector('[data-fv-home-flagship]');
          const cta=root?.querySelector('.fv-hf__mast-cta');
          const box=cta?.getBoundingClientRect();
          return {admin_bar:!!document.querySelector('#wpadminbar'),
            logged_in:document.body.classList.contains('logged-in'),
            chapters:root?.querySelectorAll('.fv-hf__chapter-nav a').length||0,
            margins:document.querySelectorAll('.fv-margin-strip__item').length,
            cta_href:cta?.getAttribute('href'),cta_visible:!!box&&box.width>0&&box.height>=44,
            cta_top:box?.top,cta_height:box?.height,
            horizontal_overflow:document.documentElement.scrollWidth>innerWidth+1};
        });
        await page.screenshot({path:join(outputDirectory,`assembler-guest-${width}.png`),
          animations:'disabled',fullPage:false,timeout:30000});
        if(state.admin_bar||state.logged_in||state.chapters!==7||state.margins!==72||
          state.cta_href!=='https://finalvestige.com/focus/'||!state.cta_visible||
          state.horizontal_overflow||state.cta_top>=900)throw new Error('Guest admission '+JSON.stringify(state));
        assert.ok(isCookieFreeGuest(await context.cookies()));
        await page.addScriptTag({path:axePath});
        const violations=await page.evaluate(async()=>{
          if(!window.axe)throw new Error('axe unavailable; fail closed');
          const r=await window.axe.run(document,{runOnly:{type:'tag',
            values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}});
          return r.violations.map(v=>({id:v.id,impact:v.impact,
            nodes:v.nodes.length,selectors:v.nodes.slice(0,2).map(n=>n.target)}));
        });
        checks.push({width,state,whole_document_axe_violations:violations});
        if(violations.length)failures.push({width,reason:'Full-document axe: '+JSON.stringify(violations)});
      } catch(e){failures.push({width,reason:String(e?.message||e).slice(0,1200)});}
      finally{await page.close();}
    }
    const noContext=await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:844}});
    try {
      const page=await noContext.newPage();
      await restrictVisitorNetwork(page,server.serverUrl,blocked);
      await page.goto(receipt.url,{waitUntil:'domcontentloaded',timeout:90000});
      const noJS=await page.evaluate(()=>({admin_bar:!!document.querySelector('#wpadminbar'),
        details:!!document.querySelector('#fv-hf-observer-answer summary'),
        evidence:document.querySelectorAll('.fv-hf__observer-context a').length,
        focus:!!document.querySelector('.fv-hf__observer-exit a[data-fv-destination="focus"]')}));
      await page.screenshot({path:join(outputDirectory,'assembler-guest-390-nojs.png'),
        animations:'disabled',fullPage:false,timeout:30000});
      if(noJS.admin_bar||!noJS.details||noJS.evidence<2||!noJS.focus)
        failures.push({width:'390-nojs',reason:'Anonymous no-JS disclosure or Focus missing'});
      checks.push({width:'390-nojs',state:noJS});
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
