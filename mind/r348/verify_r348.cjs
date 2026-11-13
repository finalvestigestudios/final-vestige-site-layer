// R348 read-only deterministic tests. Run: node mind/r348/verify_r348.cjs
'use strict';
const fs=require('node:fs'), path=require('node:path'), assert=require('node:assert/strict');
const here=__dirname;
function load(f){return fs.readFileSync(path.join(here,f),'utf8')}
function gate(files){
 const a=files.A,b=files.B,l=JSON.parse(files.ledger),c=files.captions, hub=files.hub;
 const getCore=s=>s.split('<!-- BUYER_CORE_START -->')[1]?.split('<!-- BUYER_CORE_END -->')[0];
 assert.ok(getCore(a)&&getCore(b),'Both variants require buyer core');
 assert.equal(getCore(a),getCore(b),'A/B must share exact buyer copy');
 for(const s of [a,b,hub]){
  assert.match(s,/<html lang="en">/);
  assert.match(s,/<meta name="robots" content="noindex,nofollow">/);
  assert.match(s,/<main\b/);
  assert.match(s,/:focus-visible/);
  assert.match(s,/@media\(prefers-reduced-motion:reduce\)/);
  assert.doesNotMatch(s,/<\s*(script|iframe|form|input)\b/i);
  assert.doesNotMatch(s, /\bonclick\s*=|\bonload\s*=|autoplay|<\s*video\b/i);
 }
 for(const s of [a,b]){
   assert.match(s,/<button[^>]*\bdisabled\b[^>]*>/);
   assert.match(s,/Prospective affiliate disclosure: If an authorized purchasing link/);
   assert.match(s,/Final Vestige may earn a commission/);
   assert.ok(s.indexOf('Prospective affiliate disclosure')<s.indexOf('Zen12 purchase link unavailable'));
   assert.ok(s.indexOf('Zen12 purchase link unavailable')-s.indexOf('Prospective affiliate disclosure')<700);
   assert.match(s,/href="https:\/\/finalvestige.com\/focus\/"/);
   assert.doesNotMatch(s,/href=["'][^"']*(zen12|inspire3|hypnosislive|brainwaveshots|payhip|affiliates)/i);
   assert.doesNotMatch(s,/guaranteed results|cures anxiety|fixes ADHD|verified sale|buy now|order now|checkout now/i);
 }
 assert.match(b,/Original short-film treatment/);
 assert.match(b,/not a playable or hosted video/i);
 assert.match(b,/<details>/);
 assert.match(b,/role="img"/);
 assert.equal((c.match(/ --> /g)||[]).length,6,'exactly six captions');
 assert.match(c,/00:00:35\.000 --> 00:00:42\.000/);
 assert.ok(l.claims.length>=25);
 assert.ok(Object.keys(l.release_gates).length>=25);
 assert.ok(Object.values(l.release_gates).every(x=>x==='HOLD_UNVERIFIED'));
 assert.equal(l.commercial_status.issued_earning_link,null);
 assert.equal(l.commercial_status.realized_net_revenue_per_1000_qualified_human_sessions,null);
 assert.equal(l.commercial_status.active_fv_owned_mind_product,null);
 assert.doesNotMatch(files.hub,/href=["']\/mind\//i);
 assert.match(files.dossier,/NOT COMPUTABLE/);
 assert.match(files.dossier,/affiliate_outbound_click/);
 assert.match(files.dossier,/settled_affiliate_commission/);
 return true;
}
const files={A:load('ZEN12_A_TEXT_REVIEW.html'),B:load('ZEN12_B_OPTIONAL_FILM_REVIEW.html'),ledger:load('PRODUCT_CLAIMS_AND_RELEASE_GATES.json'),captions:load('ORIGINAL_42S_CAPTIONS.vtt'),hub:load('MIND_HUB_WORDPRESS_REVIEW_ONLY.html'),dossier:load('CONVERSION_ACCEPTANCE.md')};
gate(files);
const mutations=[
 x=>({...x,A:x.A.replace(/ disabled aria-describedby/,' aria-describedby')}),
 x=>({...x,B:x.B.replace('Prospective affiliate disclosure:','Opaque marketing label:')}),
 x=>({...x,A:x.A.replace('href="https://finalvestige.com/focus/"','href="https://zen12.com/buy"')}),
 x=>({...x,B:x.B.replace('<!-- BUYER_CORE_END -->','<script>track()</script><!-- BUYER_CORE_END -->')}),
 x=>({...x,hub:x.hub.replace('<main id="main"','<form action="https://evil.example"><main id="main"')}),
 x=>({...x,B:x.B.replace('role="img"','role="presentation"')}),
 x=>({...x,B:x.B.replace('not a playable or hosted video','currently autoplaying seller ad')}),
 x=>({...x,captions:x.captions.replace(/00:00:35\.000 --> 00:00:42\.000[\s\S]*/,'')}),
 x=>({...x,ledger:x.ledger.replace('"HOLD_UNVERIFIED"','"VERIFIED"')}),
 x=>({...x,A:x.A.replace('Prospective affiliate disclosure: If an authorized purchasing link','Prospective affiliate disclosure: If an affiliate link')}),
 x=>({...x,A:x.A.replace('The merchant advertises equivalence','Guaranteed results: The merchant advertises equivalence')}),
 x=>({...x,dossier:x.dossier.replace('NOT COMPUTABLE','0')})
];
let killed=0;
for(const m of mutations){try{gate(m(files))}catch(e){killed++;continue}throw new Error('Unsafe mutation escaped test: '+killed)}
assert.equal(killed,mutations.length);
console.log('PASS R348 read-only source gates; '+mutations.length+' negative mutations rejected. Not a substitute for browser, WP, merchant or CI validation.');
