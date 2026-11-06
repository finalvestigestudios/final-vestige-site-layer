'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const {hardenFocusSource, EXPECTED_PDF}=require('./focus_gift_hardening.cjs');
const script=`<!-- wp:html -->
<script id="fvf-gift-v2">(function(){var g=document.getElementById('fvf-gift');if(!g){return;}
var bad=['invalid_email','error','blocked_email','opted_out','blocked'];
function show(){g.hidden=false;}
var q=null;try{q=new URLSearchParams(window.location.search).get('subscribe');}catch(e){}
if(q){if(bad.indexOf(q)<0){show();}}
var c=document.querySelector('.wp-block-jetpack-subscriptions__container');
function check(){if(c){if(/\\bis-subscriber\\b/.test(c.className)){show();}}}
check();if(c){if(window.MutationObserver){new MutationObserver(check).observe(c,{attributes:true,attributeFilter:['class']});}}})();</script>
<!-- /wp:html -->`;
const panel=`<div id="fvf-gift" class="fvf-gift" hidden role="status">
    <p class="fvf-gift-title">Your fieldbook is ready to download.</p>
    <a class="fvf-btn" href="${EXPECTED_PDF}" data-fv-event="focus_pdf_click" data-fv-location="after_signup">Download the Seven Day Focus Fieldbook</a>
    <p class="fvf-micro">Please confirm your email to join The Dispatch. The welcome email will include this same download link. Check Spam or Promotions if needed.</p>
  </div>`;
const subscription=`<!-- wp:jetpack/subscriptions {"showSubscribersTotal":false,"buttonOnNewLine":true,"submitButtonText":"Send me the fieldbook"} /-->`;
const source=['<main><h1>Focus</h1>',subscription,panel,script,'</main>'].join('\n');
const result=hardenFocusSource(source);
test('canonical observed source is supported',()=>assert.match(source,/fvf-gift-v2/));
test('canonical source replaces unsafe script',()=>assert.doesNotMatch(result.updated,/fvf-gift-v2"/));
test('public PDF remains accessible',()=>assert.ok(result.updated.includes(`href="${EXPECTED_PDF}"`)));
test('visible disclosure says download independent of subscription',()=>assert.match(result.updated,/Download(ing)? does not subscribe you/));
test('no fake success banner',()=>assert.doesNotMatch(result.updated,/Your fieldbook is ready to download/));
test('no hidden gift panel',()=>assert.doesNotMatch(result.updated,/id="fvf-gift"[^>]*hidden/));
test('accessible named region',()=>assert.match(result.updated,/role="region" aria-label="Free Focus Fieldbook download"/));
test('no client query or subscriber CSS used as confirmation',()=>{
 assert.doesNotMatch(result.updated,/get\('subscribe'\)|is-subscriber|MutationObserver/);
});
test('original Jetpack form unchanged',()=>assert.ok(result.updated.includes(subscription)));
test('one form and one gift panel',()=>{
 assert.equal((result.updated.match(/wp:jetpack\/subscriptions/g)||[]).length,1);
 assert.equal((result.updated.match(/id="fvf-gift"/g)||[]).length,1);
});
test('original PDF click event retained with truthful origin',()=>{
 assert.match(result.updated,/data-fv-event="focus_pdf_click" data-fv-location="public_fieldbook"/);
 assert.doesNotMatch(result.updated,/after_signup/);
});
test('no evidence of subscriber confirmation falsely claimed',()=>assert.equal(result.summary.confirmedSignupProof,'NONE_FROM_CLIENT'));
test('no WordPress write or send',()=>{
 assert.equal(result.summary.automaticEmailChanges,false);
 assert.equal(result.summary.subscriberListChanges,false);
});
for(const [name, mutated] of [
 ['missing script',source.replace(script,'')],
 ['duplicated script',source+script],
 ['missing panel',source.replace(panel,'')],
 ['duplicated panel',source+panel],
 ['missing form',source.replace(subscription,'')],
 ['duplicated form',source+subscription],
 ['wrong PDF',source.replace(EXPECTED_PDF,'https://example.com/other.pdf')],
 ['changed tracking',source.replace('after_signup','different')],
 ['script drift',source.replace("get('subscribe')","get('other')")],
 ['already patched',result.updated],
]) test('fail closed when '+name,()=>assert.throws(()=>hardenFocusSource(mutated),/Fail-closed/));
test('reject nonstring',()=>assert.throws(()=>hardenFocusSource(null),TypeError));
