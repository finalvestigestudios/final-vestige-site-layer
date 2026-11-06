'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const {inspect,attrs,decodeEntities}=require('./verify_focus_nojs_funnel.cjs');
const base='<div class="wp-block-jetpack-subscriptions"><h2 id="subscribe-blog">Subscribe</h2>'+
'<a href="https://finalvestige.com/?post_type=page&#038;p=1579">Send me the fieldbook</a></div>'+
'<h1>The 52-page Fieldbook</h1>';
test('entity decoding preserves query parameters',()=>assert.equal(decodeEntities('a&#038;b&amp;c&#x26;d'),'a&b&c&d'));
test('attributes recognize link target',()=>assert.equal(attrs('<a href="/focus/" rel="nofollow">').href,'/focus/'));
test('real Jetpack-shaped self-link is not mistaken for a confirmed signup',()=>{const r=inspect(base);assert.equal(r.self_link_subscription_controls,1);assert.equal(r.form_count,0);assert.equal(r.qualified_for_release,false);assert.ok(r.flags.includes('SELF_LINKING_SUBSCRIBE_CONTROL_HAS_NO_NOJS_FALLBACK_IN_CONTENT'));});
test('hidden PDF link does not count as a fallback',()=>{const r=inspect(base+'<div hidden><a href="/downloads/fieldbook.pdf">Get PDF</a></div>');assert.equal(r.no_js_pdf_fallback,false);});
test('noscript fallback is visible without JS but does not certify conversions',()=>{const r=inspect(base+'<noscript><a href="/downloads/fieldbook.pdf">Read the fieldbook without JS</a></noscript>');assert.equal(r.no_js_pdf_fallback,true);assert.equal(r.flags.length,0);assert.equal(r.qualified_for_release,false);});
test('native HTML form avoids self-link dead-end but still requires a browser test',()=>{const r=inspect(base+'<form action="/subscribe" method="post"><input name="email" type="email"><button>Subscribe</button></form>');assert.equal(r.flags.length,0);assert.equal(r.qualified_for_release,false);});
test('missing signup block fails',()=>{const r=inspect('<h1>52-page Fieldbook</h1>');assert.ok(r.flags.includes('NO_JETPACK_SUBSCRIPTION_BLOCK_IN_RENDERED_CONTENT'));});
test('missing 52 page promise fails',()=>{const r=inspect(base.replace('52-page','Seven Day'));assert.ok(r.flags.includes('FIELDBOOK_52_PAGE_PROMISE_NOT_FOUND'));});
test('no-JS PDF fallback must not be inside a JS-dependent hidden container',()=>{const r=inspect(base+'<div hidden><noscript><a href="/downloads/a.pdf">PDF</a></noscript></div>');assert.equal(r.no_js_pdf_fallback,false);});
