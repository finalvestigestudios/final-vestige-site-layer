// R265 strengthened source-level release gate, repaired in R266. Native Node: node mind/r265/test_r265.cjs
'use strict';
const fs=require('node:fs'), path=require('node:path'), assert=require('node:assert/strict');
const read=n=>fs.readFileSync(path.join(__dirname,n),'utf8');
const files={article:read('THE-MACHINE-YOU-THOUGHT-YOU-UNDERSTOOD-UNPUBLISHED.md'),A:read('ZEN12-A-SOURCED-UNPUBLISHED.html'),B:read('ZEN12-B-OPTIONAL-FILM-UNPUBLISHED.html'),hub:read('MIND-ARCHIVE-UNPUBLISHED.html'),matrix:JSON.parse(read('CLAIMS-AND-COMMERCE-HARDHOLD.json')),plan:read('OFFER-TO-REVENUE-ACCEPTANCE.md')};
const EXACT_GATES=['named_partner_acceptance','written_product_permission','approved_social_channels','approved_email_channel','issued_tracking_url','affiliate_terms','approved_creatives_rights','exact_active_offer','cart_total_verified','returns_terms_verified','fulfillment_verified','product_specific_claim_substantiation','independent_disclosure_qa','first_party_attribution_review','verified_paid_merchant_reporting','founder_release_approval'];
const CLAIM_STATES={C01:'SUPPORTED_FOR_STUDY_NOT_PRODUCT',C02:'SUPPORTED_WITH_BOUNDARIES',C03:'SUPPORTED_WITH_BOUNDARIES',C04:'SELLER_DESCRIPTION_ONLY',C05:'SELLER_DESCRIBED_DELIVERY_UNVERIFIED',C06:'NOT_SUBSTANTIATED_FOR_PRODUCT;OMIT',C07:'NOT_SUBSTANTIATED;OMIT',C08:'HISTORICAL_DISPLAY_ONLY;NO_CURRENT_PRICE',C09:'UNVERIFIED_FULFILLMENT;DO_NOT_ASSERT',C10:'NOT_VERIFIED',C11:'NOT_VERIFIED',C12:'FALSE;PROHIBITED',C13:'FALSE;PROHIBITED',C14:'SUPPORTED',C15:'SUPPORTED'};
const COMMERCE_NULL=['affiliate_link','approved_publisher','commission_rate','price','paid_orders','refunds','net_revenue_per_1000_qualified_humans'];
const CONSTRAINTS=['no_live_cms','no_deploy','no_merge','no_new_jetpack_list','no_tracking_script','no_media_autoplay'];
function checkHtml(label,s){
  assert(/<html lang="en">/i.test(s)&&/<meta name="viewport"/i.test(s)&&/<main>/i.test(s),label+' basic semantics');
  assert(/<meta name="robots" content="noindex,nofollow">/.test(s),label+' preview noindex');
  assert(!/<(script|form|iframe|video|audio|object|embed|svg|link)\b/i.test(s),label+' forbidden active/embed element');
  assert(!/\b(onclick|onload|onerror|onmouseover|autoplay|srcdoc|contenteditable|formaction)\s*=/i.test(s),label+' forbidden executable attribute');
  assert(!/\b(src|action)\s*=/i.test(s),label+' forbidden load/action attribute');
  assert(!/@import\b|url\s*\(\s*['"]?https?:/i.test(s),label+' remote style import');
  assert(!/<meta[^>]+http-equiv\s*=\s*["']?refresh/i.test(s),label+' redirect');
  const links=[...s.matchAll(/<a\b[^>]*\bhref\s*=\s*(["'])(.*?)\1/gi)].map(x=>x[2].replace(/&amp;/g,'&'));
  for(const href of links){
    assert(!/javascript:|data:|&#|%0[ad]/i.test(href),label+' unsafe URL');
    if(href.startsWith('#'))continue;
    const u=new URL(href);
    assert(u.protocol==='https:',label+' non HTTPS');
    assert(['finalvestige.com','www.ftc.gov','pubmed.ncbi.nlm.nih.gov'].includes(u.hostname),label+' unapproved outbound '+u.hostname);
  }
  assert(links.some(x=>x.includes('finalvestige.com/focus/')),label+' preserve Focus');
  const box=s.match(/<div class="commercial"[^>]*>([\s\S]*?)<\/div>/i);
  assert(box,label+' commercial box');
  const content=box[1],p=content.match(/<p class="disclose">[\s\S]*?<\/p>/i),btn=content.match(/<button\b[^>]*>[\s\S]*?<\/button>/i);
  assert(p&&btn,label+' separate disclosure / CTA');
  assert(/may earn a commission/i.test(p[0]),label+' clear material connection');
  assert(/no (?:earning|partner) link is (?:currently )?active/i.test(content),label+' hold copy');
  const pIdx=content.indexOf(p[0]), bIdx=content.indexOf(btn[0]);
  assert(pIdx>=0&&bIdx>pIdx&&bIdx-(pIdx+p[0].length)<140,label+' near-CTA disclosure precedes CTA');
  assert(/\bdisabled(?:\s|>|=)/i.test(btn[0]),label+' CTA must be disabled');
  assert(!/href\s*=|formaction\s*=|onclick\s*=/i.test(btn[0]),label+' CTA cannot route externally');
  assert.equal((s.match(/<button\b/gi)||[]).length,1,label+' no second enabled CTA');
  return true;
}
function verify(f){
  assert(f.article.includes('Rozenblit')&&f.article.includes('Fernbach')&&f.article.includes('https://pubmed.ncbi.nlm.nih.gov/21442007/'),'historical article citations');
  assert(/No affiliate recommendation/i.test(f.article),'investigation separated from commerce');
  const m=f.matrix;assert.equal(m.status,'UNPUBLISHED_HARD_HOLD');assert.equal(m.gates.length,16);
  assert.deepEqual(m.gates.map(g=>g.id).sort(),[...EXACT_GATES].sort(),'gate identity and uniqueness');
  for(const g of m.gates)assert(g.status==='HARD_HOLD'&&g.evidence===null,'every approval gate held');
  assert.equal(m.claims.length,15);assert.deepEqual(m.claims.map(c=>c.id).sort(),Object.keys(CLAIM_STATES).sort());
  assert.equal(new Set(m.sources.map(s=>s.id)).size,m.sources.length,'unique source IDs');
  assert(m.sources.some(s=>s.url==='https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance'),'FTC source retained');
  for(const s of m.sources)assert(/^https:\/\//.test(s.url),'source URL');
  for(const c of m.claims){
    assert.equal(c.status,CLAIM_STATES[c.id],'exact claim classification');
    for(const id of c.source.split(';'))assert(m.sources.some(s=>s.id===id),'claim cited source exists');
  }
  assert.deepEqual(Object.keys(m.commerce).sort(),[...COMMERCE_NULL].sort(),'unverified commerce fields');
  for(const k of COMMERCE_NULL)assert.equal(m.commerce[k],null,'unknown '+k+' must stay unknown');
  for(const k of CONSTRAINTS)assert.equal(m.constraints[k],true,'release boundary '+k);
  for(const k of ['A','B','hub'])checkHtml(k,f[k]);
  assert(!f.A.includes('Optional original 42-second film'),'A is text-only');
  assert(f.B.includes('Optional original 42-second film'),'B optional-film concept');
  assert(/<details>[\s\S]*?<summary>Read complete 42-second caption\/transcript concept<\/summary>/.test(f.B),'B transcript visible on opt in');
  assert(f.B.includes('aria-label="Dark illustrated poster reading: Twelve minutes. Three different questions."'),'poster alt matches actual pixels');
  assert.equal((f.B.match(/<li data-start=/g)||[]).length,7,'seven timed segments');
  const segments=[...f.B.matchAll(/<li data-start="(\d+)" data-end="(\d+)">/g)];
  assert.equal(segments.length,7);
  segments.forEach((match,i)=>{assert.equal(Number(match[1]),i*6);assert.equal(Number(match[2]),(i+1)*6)});
  const removeFilm=s=>s.replace(/<section class="film"[\s\S]*?<\/section>/,'');
  const body=s=>removeFilm(s).replace(/<title>[\s\S]*?<\/title>/,'').replace(/Draft [AB] —/g,'Draft X —');
  assert.equal(body(f.A),body(f.B),'purchase content parity');
  for(const term of ['merchant_confirmed_order','affiliate_outbound','NOT COMPUTABLE','Focus'])assert(f.plan.includes(term),'conversion contract '+term);
  assert(!/affiliate revenue is confirmed|confirmed subscriber from gift UI|commission rate: [1-9]/i.test(f.plan));
  return true;
}
verify(files);
const neg=[
 ['gate identity changed',f=>f.matrix.gates[0].id='counterfeit_gate'],
 ['duplicate gate',f=>f.matrix.gates[1].id=f.matrix.gates[0].id],
 ['gate removed',f=>f.matrix.gates.pop()],
 ['false partner approval',f=>f.matrix.gates[0].status='APPROVED'],
 ['fake gate evidence',f=>f.matrix.gates[1].evidence='verified'],
 ['false paid orders',f=>f.matrix.commerce.paid_orders=4],
 ['false publisher',f=>f.matrix.commerce.approved_publisher=true],
 ['fake commission',f=>f.matrix.commerce.commission_rate=0.5],
 ['false price',f=>f.matrix.commerce.price=87.99],
 ['fake refunded orders',f=>f.matrix.commerce.refunds=0],
 ['invented affiliate URL',f=>f.matrix.commerce.affiliate_link='https://fake.invalid'],
 ['invented revenue',f=>f.matrix.commerce.net_revenue_per_1000_qualified_humans=600],
 ['allow live CMS',f=>f.matrix.constraints.no_live_cms=false],
 ['allow deploy',f=>f.matrix.constraints.no_deploy=false],
 ['allow merge',f=>f.matrix.constraints.no_merge=false],
 ['duplicate signup permission',f=>f.matrix.constraints.no_new_jetpack_list=false],
 ['new analytics permission',f=>f.matrix.constraints.no_tracking_script=false],
 ['autoplay permission',f=>f.matrix.constraints.no_media_autoplay=false],
 ['unsupported efficacy status',f=>f.matrix.claims[5].status='SUPPORTED'],
 ['incorrect publisher claim',f=>f.matrix.claims[9].status='SUPPORTED'],
 ['false source ID',f=>f.matrix.claims[0].source='S999'],
 ['duplicate claim ID',f=>f.matrix.claims[1].id='C01'],
 ['invented source',f=>f.matrix.sources[0].url='javascript:alert(1)'],
 ['seller link A',f=>f.A=f.A.replace('https://finalvestige.com/focus/','https://zen12.com/secret/')],
 ['seller link B',f=>f.B=f.B.replace('https://finalvestige.com/focus/','https://zen12.com/hnp')],
 ['merchant link HUB',f=>f.hub=f.hub.replace('https://finalvestige.com/focus/','https://affiliates.inspire3.com/track')],
 ['masked merchant URL',f=>f.B=f.B.replace('https://finalvestige.com/focus/','https://zen12.com/secret/?utm_x=y')],
 ['removed disclosure A',f=>f.A=f.A.replace('may earn a commission','could be nice')],
 ['disclosure moved away from CTA',f=>{f.B=f.B.replace(/<p class="disclose">([\s\S]*?)<\/p>(<button[\s\S]*?<\/button>)/,'$2<p class="disclose">$1</p>')}],
 ['enabled CTA A',f=>f.A=f.A.replace('button type="button" disabled','button type="button"')],
 ['enabled CTA B',f=>f.B=f.B.replace('button type="button" disabled','button type="button"')],
 ['enabled CTA HUB',f=>f.hub=f.hub.replace('button type="button" disabled','button type="button"')],
 ['injected form B',f=>f.B+='<form action="/subscribe"><input></form>'],
 ['injected tracking A',f=>f.A+='<script src="/pixel.js"></script>'],
 ['silent external pixel',f=>f.hub+='<img src="https://spy.invalid/pixel">'],
 ['inline click handler',f=>f.B=f.B.replace('disabled aria-describedby','disabled onclick="buy()" aria-describedby')],
 ['meta redirect',f=>f.A=f.A.replace('<head>','<head><meta http-equiv="refresh" content="0;url=https://seller.invalid">')],
 ['autoplay JS',f=>f.B+='<video autoplay></video>'],
 ['film unlabeled',f=>f.B=f.B.replace('Dark illustrated poster reading: Twelve minutes. Three different questions.','Illustrated concept: a timer, seven evidence cards, and the words Claim, Source, Limit')],
 ['film captions missing',f=>f.B=f.B.replace('36–42s: Examine','36–42s text omitted: Examine')],
 ['film timing corrupt',f=>f.B=f.B.replace('data-start="36" data-end="42"','data-start="33" data-end="42"')],
 ['A B divergent purchase text',f=>f.B=f.B.replace('a free timer already does that','a free timer cannot do that')],
 ['unapproved new second CTA',f=>f.hub+='<button>BUY NOW</button>'],
 ['invented source',f=>f.article=f.article.replace('https://pubmed.ncbi.nlm.nih.gov/21442007/','https://invalid.example/')],
 ['fabricated paid metrics',f=>f.plan+='\nAffiliate revenue is confirmed'],
 ['fake Focus lead',f=>f.plan+='\nconfirmed subscriber from gift UI']
];
let rejected=0;
for(const [name,mutate] of neg){
  const f=JSON.parse(JSON.stringify(files)), before=JSON.stringify(f);
  mutate(f);
  assert.notEqual(JSON.stringify(f),before,'negative mutation must actually change input: '+name);
  try{verify(f)}catch(e){rejected++;continue}
  throw new Error('TEST FAILED TO REJECT: '+name);
}
console.log('R265 repaired baseline PASS; '+rejected+'/'+neg.length+' effective adversarial modifications rejected; source-only suite; native browser/CMS/merchant QA still required.');
