'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const {normalizedPath, visibleAnchors, inspect} = require('./published_page_route_guard.cjs');
const origin = 'https://finalvestige.com';
const page=(content, url='https://finalvestige.com/focus/')=>({id:1579,link:url,status:'publish',content});
const post={id:42,link:'https://finalvestige.com/2026/10/30/a-story/',status:'publish'};
const snap=(content,more={})=>({site_origin:origin,pages:[page(content)],posts:[post],...more});
test('canonical published page and post links pass as source links',()=>{
 const r=inspect(snap('<a href="/focus/">Book</a><a href="/2026/10/30/a-story/">Read</a>'));
 assert.equal(r.status,'CLEAN_SOURCE'); assert.equal(r.first_party_links_inspected,2);
});
test('unlisted site route becomes review, not a claimed 404',()=>{
 const r=inspect(snap('<a href="/not-published/">Find</a>'));
 assert.equal(r.status,'REVIEW_SOURCE'); assert.equal(r.http_verified,false);
 assert.deepEqual(r.orphan_route_candidates[0].normalized_path,'/not-published/');
});
test('retired 72-hours URL anywhere in saved markup gets review',()=>{
 const r=inspect(snap('<!-- wp:html --><a href="/72-hours-without-the-tap/">Guide</a>'));
 assert.equal(r.retired_campaign_references.length,1);
});
test('old water manual filename gets review without being published',()=>{
 assert.equal(inspect(snap('Old file: Final_Vestige_Water_Manual.pdf')).status,'REVIEW_SOURCE');
});
test('first-party absolute, relative and querystring paths normalize',()=>{
 assert.equal(normalizedPath('https://finalvestige.com/focus?x=1#y'),'/focus/');
 assert.equal(normalizedPath('/focus/?a=1&amp;b=2'),'/focus/');
 assert.equal(normalizedPath('focus/', origin),'/focus/');
});
test('offsite lookalikes and protocol-relative impostors are excluded',()=>{
 assert.equal(normalizedPath('https://finalvestige.com.evil.example/focus/'),null);
 assert.equal(normalizedPath('//attacker.example/login'),null);
});
test('fragment, query-only, mail and tel are not route defects',()=>{
 for(const h of ['#subscribe-blog','?subscribe=success','mailto:a@example.com','tel:+12065550123']) assert.equal(normalizedPath(h),null);
});
test('plugin, wp-login and media routes are explicitly non-verifiable',()=>{
 const r=inspect(snap('<a href="/portal/?fcom_action=auth">Join</a><a href="/wp-content/uploads/x.pdf">Download</a><a href="/wp-login.php">Login</a>'));
 assert.equal(r.status,'CLEAN_SOURCE');assert.equal(r.skipped_dynamic_routes,3);
});
test('script and CSS strings do not create rendered anchor candidates',()=>{
 const h='<script>const s=`<a href="/fake/">`;</script><style>i:after{content:"<a href=\'/bad/\'>"}</style><a href="/focus/">OK</a>';
 assert.deepEqual(visibleAnchors(h),['/focus/']);
});
test('Gutenberg comments with raw href do not count as visible links',()=>{
 assert.deepEqual(visibleAnchors('<!-- wp:html {"href":"/nope/"} --><a href="/focus/">Open</a>'),['/focus/']);
});
test('published page inventory requires saved source, never silent pass',()=>{
 assert.equal(inspect({pages:[{id:1,link:'/'}],posts:[]}).status,'INVALID_INPUT');
 assert.equal(inspect({pages:[],posts:[]}).status,'INVALID_INPUT');
});
test('draft in input fails closed rather than treating as live route',()=>{
 assert.equal(inspect(snap('ok',{pages:[{...page('ok'),status:'draft'}]})).status,'INVALID_INPUT');
});
test('no writes or mutations to input structures',()=>{
 const s=snap('<a href="/focus/">OK</a>');const before=JSON.stringify(s);inspect(s);assert.equal(JSON.stringify(s),before);
});
test('missing registry article path generates review',()=>{
 const r=inspect(snap('<a href="/2026/10/30/unknown-post/">Read</a>'));
 assert.equal(r.orphan_route_candidates[0].normalized_path,'/2026/10/30/unknown-post/');
});
test('https external references do not count as internal routes',()=>{
 const r=inspect(snap('<a href="https://example.org/evidence">Official record</a>'));
 assert.equal(r.status,'CLEAN_SOURCE');assert.equal(r.first_party_links_inspected,0);
});
