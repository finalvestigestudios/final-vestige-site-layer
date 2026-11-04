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
function ex2_guest_refuse($s){ echo wp_json_encode(array('error'=>$s,'release'=>'HOLD')); exit; }
$u=wp_parse_url(home_url('/'));
if (!is_array($u)||($u['scheme']??'')!=='http'||
 !in_array($u['host']??'',array('localhost','127.0.0.1','::1'),true)||
 empty($u['port'])||is_multisite()||get_stylesheet()!=='assembler')
 ex2_guest_refuse('Not isolated local Assembler');
$marker='/tmp/fv-ex2-synthetic-only.marker';
$token_path='/tmp/fv-ex2-editor-token';
$copy_path='/tmp/fv-ex2-guest-copy-id';
if (!is_file($marker)||
 trim((string)file_get_contents($marker))!=='SYNTHETIC_TEST_FIXTURE_ONLY'||
 !is_file($token_path)||is_file($copy_path))
 ex2_guest_refuse('Missing private fixture or an outstanding guest copy');
$token=trim((string)file_get_contents($token_path));
if (strlen($token)!==64||!ctype_xdigit($token))
 ex2_guest_refuse('Invalid private fixture token');
$id=${draftId};
$draft=get_post($id);
if (!$draft||$draft->post_type!=='page'||$draft->post_status!=='draft'||
 $draft->post_title!=='FV EX2 SYNTHETIC EDITOR SAVED')
 ex2_guest_refuse('Not a verified Gutenberg candidate draft');
$owner=get_post_meta($id,'_fv_ex2_editor_qa_owner',true);
if (!is_string($owner)||!hash_equals(hash_hmac('sha256',(string)$id,$token),$owner))
 ex2_guest_refuse('Guest copy source is not HMAC-owned by this fixture');
$content=$draft->post_content;
if (!is_string($content)||
 substr_count($content,'data-fv-home-flagship')<1||
 substr_count($content,'72 published historical fragments in isolated review')<1||
 substr_count($content,'data-fv-source=')!==4||
 substr_count($content,'jetpack/subscriptions')!==1)
 ex2_guest_refuse('Missing public-Margins/synthetic-Jetpack fixture custody markers');
// WordPress can strip <script>/<style> on an anonymous wp_insert_post.
// Bind ONLY this validated local fixture to its one disposable administrator.
$admins=get_users(array('role'=>'administrator','number'=>1,'fields'=>'all'));
if (count($admins)!==1||!isset($admins[0]->ID))
 ex2_guest_refuse('Disposable administrator unavailable');
wp_set_current_user((int)$admins[0]->ID);
if (!current_user_can('unfiltered_html'))
 ex2_guest_refuse('Isolated Gutenberg editor cannot retain original HTML');
$source_sha=hash('sha256',$content);
$copy=wp_insert_post(array('post_type'=>'page','post_status'=>'publish',
 'post_name'=>'fv-ex2-anonymous-review-'.wp_generate_password(12,false,false),
 'post_title'=>'EX2 ANONYMOUS LOCAL REVIEW — NOT A PUBLIC WEBSITE',
 'post_content'=>wp_slash($content),'ping_status'=>'closed','comment_status'=>'closed',
 'to_ping'=>'','pinged'=>''),true);
if (is_wp_error($copy)||!is_int($copy)||$copy<1)
 ex2_guest_refuse('Local copy creation failed');
$created=get_post($copy);
if (!$created||hash('sha256',$created->post_content)!==$source_sha||
 $created->post_status!=='publish'){
 wp_delete_post($copy,true);
 ex2_guest_refuse('Local copy custody mismatch');
}
$copy_owner=hash_hmac('sha256','guest:'.(string)$copy,$token);
if (!add_post_meta($copy,'_fv_ex2_guest_copy_owner',$copy_owner,true)){
 wp_delete_post($copy,true);
 ex2_guest_refuse('Could not establish guest copy ownership');
}
if (file_put_contents($copy_path,(string)$copy,LOCK_EX)===false){
 wp_delete_post($copy,true);
 ex2_guest_refuse('Could not track the disposable guest copy');
}
echo wp_json_encode(array('type'=>'EPHEMERAL_LOOPBACK_ANONYMOUS_COPY',
 'copy_id'=>$copy,'source_draft_id'=>$id,'source_sha256'=>$source_sha,
 'copy_sha256'=>hash('sha256',$created->post_content),
 'url'=>get_permalink($copy),'release'=>'HOLD'));`;
}
export function phpGuestDelete(copyId=null) {
  assert.ok(copyId===null||(Number.isSafeInteger(copyId)&&copyId>0));
  const expected = copyId===null?'null':String(copyId);
  return `<?php
require '/wordpress/wp-load.php';
function ex2_guest_cleanup_reply($data){echo wp_json_encode($data);exit;}
$u=wp_parse_url(home_url('/'));
if (!is_array($u)||($u['scheme']??'')!=='http'||
 !in_array($u['host']??'',array('localhost','127.0.0.1','::1'),true)||
 empty($u['port'])||is_multisite()||get_stylesheet()!=='assembler')
 ex2_guest_cleanup_reply(array('error'=>'Not isolated local Assembler'));
$marker='/tmp/fv-ex2-synthetic-only.marker';
$token_path='/tmp/fv-ex2-editor-token';
$copy_path='/tmp/fv-ex2-guest-copy-id';
if (!is_file($marker)||
 trim((string)file_get_contents($marker))!=='SYNTHETIC_TEST_FIXTURE_ONLY'||
 !is_file($token_path)||!is_file($copy_path))
 ex2_guest_cleanup_reply(array('error'=>'No verified private guest copy tracker'));
$token=trim((string)file_get_contents($token_path));
if (strlen($token)!==64||!ctype_xdigit($token))
 ex2_guest_cleanup_reply(array('error'=>'Invalid private guest copy token'));
$id_str=trim((string)file_get_contents($copy_path));
if (!preg_match('/^[1-9]\\d*$/D',$id_str))
 ex2_guest_cleanup_reply(array('error'=>'Invalid private guest copy ID'));
$id=(int)$id_str;
if (${expected} !== null && $id !== ${expected})
 ex2_guest_cleanup_reply(array('error'=>'Guest receipt/tracker identity mismatch'));
$p=get_post($id);
$owner=get_post_meta($id,'_fv_ex2_guest_copy_owner',true);
$proof=hash_hmac('sha256','guest:'.(string)$id,$token);
if (!$p||$p->post_type!=='page'||
 !str_starts_with($p->post_title,'EX2 ANONYMOUS LOCAL REVIEW')||
 !is_string($owner)||!hash_equals($proof,$owner))
 ex2_guest_cleanup_reply(array('error'=>'Refusing deletion of an unowned guest copy'));
$deleted=wp_delete_post($id,true);
clean_post_cache($id);
if (!$deleted||get_post($id)!==null)
 ex2_guest_cleanup_reply(array('error'=>'Guest copy deletion was not verified'));
if (!@unlink($copy_path)||is_file($copy_path))
 ex2_guest_cleanup_reply(array('error'=>'Guest page removed but private tracker cleanup failed'));
ex2_guest_cleanup_reply(array('deleted'=>true,'verified_absent'=>true,'id'=>$id,'release'=>'HOLD'));`;
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
  // Arm cleanup before the PHP create call. A damaged/lost receipt must not
  // bypass removal of a copy already created inside the disposable Playground.
  let copyAttempted=false,copyId=null,context=null,receipt;
  const blocked=new Set(),checks=[],failures=[];
  try {
    copyAttempted=true;
    const raw=await server.playground.run({code:phpGuestCopy(draftId)});
    try {receipt=JSON.parse(raw.text);}catch{throw new Error('Invalid local guest-copy receipt');}
    copyId=Number.isSafeInteger(receipt?.copy_id)&&receipt.copy_id>0?receipt.copy_id:null;
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
        const readability=items.map(el=>{
          const rect=el.getBoundingClientRect();
          let ancestorHidden=false,cur=el;
          while(cur&&cur.nodeType===1) {
            const cs=getComputedStyle(cur);
            if(cs.display==='none'||cs.visibility!=='visible'||Number(cs.opacity)<0.5||
               cur.hidden||cur.inert||cur.getAttribute('aria-hidden')==='true')
              ancestorHidden=true;
            cur=cur.parentElement;
          }
          const css=getComputedStyle(el);
          return {display:css.display,visibility:css.visibility,opacity:css.opacity,
            position:css.position,width:rect.width,height:rect.height,
            ancestor_hidden:ancestorHidden};
        });
        return {admin_bar:!!document.querySelector('#wpadminbar'),
          logged_in:document.body.classList.contains('logged-in'),
          details:!!summary,summary_visible:visible(summary),
          evidence:document.querySelectorAll('.fv-hf__observer-context a').length,
          focus:!!focus,focus_visible:visible(focus),
          margins:items.length,margin_texts:items.map(el=>el.textContent),
          margin_position:first?getComputedStyle(first).position:null,
          margin_opacity:first?getComputedStyle(first).opacity:null,
          margin_readability:readability,
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
      const {margin_texts:publicMarginalText,
        margin_readability:privateRenderDetail,...noJSSummary}=noJS;
      checks.push({width:'390-nojs',state:noJSSummary});
    } finally {await noContext.close();}
  } finally {
    if(context)await context.close();
    if(copyAttempted) {
      let deleted=false;
      try {
        // PHP reads a PRIVATE tracker if the create receipt never arrived.
        // A mismatched ID or missing HMAC ownership fails closed.
        const r=await server.playground.run({code:phpGuestDelete(copyId)});
        const c=JSON.parse(r.text);
        deleted=c.deleted===true&&c.verified_absent===true&&
          c.release==='HOLD'&&Number.isSafeInteger(c.id)&&c.id>0&&
          (copyId===null||copyId===c.id);
      } catch {deleted=false;}
      if(!deleted)throw new Error('FAIL CLOSED: owned temporary guest page cleanup unverified');
    }
  }
  if(failures.length)throw new Error('ANONYMOUS_VISITOR_RELEASE_HOLD '+JSON.stringify(failures));
  return {release:'HOLD',scope:'ANONYMOUS_LOOPBACK_ASSEMBLER_NOT_HOSTED_WPCOM',
    saved_copy_sha256:receipt.copy_sha256,checks,blocked_hosts:[...blocked].sort(),
    cleanup:'VERIFIED',limitation:'WordPress Playground is not WordPress.com Atomic or Jetpack'};
}
