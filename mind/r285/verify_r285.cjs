'use strict';
/* FV Mind R285: strict, dependency-free source-only audit. Run: node mind/r285/verify_r285.cjs.
 NOT a substitute for browser/WordPress/merchant verification. Does not write or access network. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const files={
 article:'THE-THOUGHT-THAT-RETURNED-BECAUSE-YOU-FORBADE-IT-UNPUBLISHED.md',
 matrix:'CLAIM-PROOF-CREATOR-AND-COMMERCIAL-HARDHOLD.json',
 newHub:'MIND-WHITE-BEAR-READING-ROOM-WP-CUSTOM-HTML-UNPUBLISHED.html',
 a:'../r284/ZEN12-BUYER-GUIDE-A-TEXT-ONLY-UNPUBLISHED.html',
 b:'../r284/ZEN12-BUYER-GUIDE-B-FILM-STORYBOARD-UNPUBLISHED.html',
 hub:'../r284/MIND-CANONICAL-HUB-INSERT-CANDIDATE-UNPUBLISHED.html'
};
function read(){return Object.fromEntries(Object.entries(files).map(([k,v])=>[k,fs.readFileSync(path.join(__dirname,v),'utf8')]));}
const links=new Set('#main https://finalvestige.com/focus/ https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ https://finalvestige.com/affiliate-disclosure/ https://finalvestige.com/editorial-standards/ https://finalvestige.com/2026/11/02/change-blindness/ https://finalvestige.com/2026/11/02/mesmerism/ https://pubmed.ncbi.nlm.nih.gov/37205669/ https://pubmed.ncbi.nlm.nih.gov/38215647/ https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance'.split(' '));
const tags=new Set('html head body meta title style header nav main footer section article aside div p h1 h2 h3 h4 strong small span br ol ul li time details summary table thead tbody tr th td a button'.split(' '));
const attributes=new Set('lang charset name content class id href aria-label aria-labelledby aria-describedby role type disabled scope'.split(' '));
const sources='whitebear_1987 ironic_1997 meta_2020 mood_1993 meditation_adverse eeg_2023 inspire3 zen12 zen12_newsletter total_focus hypnosis_refund focus_shot brainwave_refund ftc_endorsement ftc_health fv_puy fv_focus fv_change fv_mesmer yt_mesmer'.split(' ');
const gates='merchant_account_acceptance merchant_identity_matches_fv affiliate_terms_current permitted_traffic_channels approved_presell_placement issued_earning_url test_tracking_accepted offer_route_exact checkout_price_and_charges returns_eligibility_restrictions seller_creative_rights product_specific_claims_review adjacent_disclosure_qa browser_mobile_accessibility conversion_reporting_access founder_live_release_approval'.split(' ');
const offers='zen12_premium zen12_promo hypnosis_live_total_focus brainwave_focus_shot fv_free_focus fv_paid_mind_sku'.split(' ');
function decode(s){return s.replace(/&(#x[0-9a-f]+|#[0-9]+|amp|quot|apos|colon|Tab|NewLine|sol|period);?/gi,(all,e)=>{let v=e.toLowerCase();if(v[0]==='#'){let n=v[1]==='x'?parseInt(v.slice(2),16):parseInt(v.slice(1),10);return n>0&&n<=0x10ffff?String.fromCodePoint(n):all;}return ({amp:'&',quot:'"',apos:"'",colon:':',tab:'\t',newline:'\n',sol:'/',period:'.'})[v]||all;});}
function auditMarkup(html,key){
 assert.ok(html.length>=1800,key+' length');
 const style=[...html.matchAll(/<style\b[^>]*>([\s\S]*?)<\/style\s*>/gi)];
 for(const s of style)assert.ok(!/@import\b|url\s*\(|expression\s*\(|(?:^|[;{])\s*behavior\s*:|-moz-binding|data\s*:/i.test(s[1]),key+' resource-loading CSS');
 const work=html.replace(/<!--[\s\S]*?-->/g,'').replace(/<style\b[^>]*>[\s\S]*?<\/style\s*>/gi,'<style></style>').replace(/<!doctype\s+html\s*>/gi,'');
 const fragments=[...work.matchAll(/<([^<>]*)>/g)];
 assert.ok(!/[<>]/.test(work.replace(/<[^<>]*>/g,'')),key+' malformed markup');
 let buttons=0,disclosures=0,focus=0,anchors=0;
 for(const x of fragments){
  const token=x[1].trim();
  if(token[0]==='/'){
    assert.ok(/^\/\s*[a-z][\w:-]*\s*$/i.test(token),key+' bad close');
    assert.ok(tags.has(token.slice(1).trim().toLowerCase()),key+' forbidden close');
    continue;
  }
  const tag=/^([a-z][\w:-]*)([\s\S]*)$/i.exec(token);
  assert.ok(tag,key+' invalid tag');
  const name=tag[1].toLowerCase();
  assert.ok(tags.has(name),key+' forbidden tag '+name);
  let rest=tag[2],pos=0,attrs={};
  const rule=/\s*([a-z_:][\w:.-]*)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'=<>\x60]+)))?/iy;
  while(pos<rest.length){
   if(/^\s*$/.test(rest.slice(pos)))break;
   rule.lastIndex=pos;
   let a=rule.exec(rest);
   assert.ok(a,key+' malformed attribute');
   pos=rule.lastIndex;
   let n=a[1].toLowerCase(),v=decode(a[2]??a[3]??a[4]??'');
   assert.ok(attributes.has(n),key+' forbidden attr '+n);
   assert.ok(!Object.prototype.hasOwnProperty.call(attrs,n),key+' duplicate attr '+n);
   assert.ok(!/&(?:#|colon|tab|newline|sol);?/i.test(v),key+' unresolved attr entity');
   attrs[n]=v;
  }
  if(name==='a'){
    anchors++;
    assert.ok(Object.prototype.hasOwnProperty.call(attrs,'href'),key+' anchor needs href');
    assert.ok(links.has(attrs.href),key+' unapproved URL '+attrs.href);
    if(attrs.href==='https://finalvestige.com/focus/')focus++;
  }else assert.ok(!('href' in attrs),key+' href forbidden outside anchor');
  if(name==='button'){
   buttons++;
   assert.equal(attrs.type,'button');
   assert.ok('disabled' in attrs,key+' paid button must be disabled');
   assert.ok('aria-describedby' in attrs,key+' disclosure reference');
  }else assert.ok(!('disabled' in attrs));
  if(attrs.id==='prospective-disclosure'||attrs.id==='r285-disclosure')disclosures++;
  if(name==='meta')assert.ok((attrs.charset==='utf-8'&&Object.keys(attrs).length===1)||(attrs.name==='viewport'&&attrs.content==='width=device-width, initial-scale=1')||(attrs.name==='robots'&&attrs.content==='noindex,nofollow'),key+' unexpected meta');
 }
 assert.ok(anchors>=2&&focus>=1,key+' preserve real published/free routes');
 if(['a','b','newHub'].includes(key)){
  assert.equal(buttons,1,key+' exactly one disabled paid button');
  assert.equal(disclosures,1,key+' exactly one prospective disclosure');
  assert.ok(/may earn a commission at no additional cost to you/i.test(html),key+' truthful FTC language');
  assert.ok(/authorization pending|unavailable pending authorization/i.test(html),key+' offer held');
 }else assert.equal(buttons,0,key+' no new clickable controls');
 if(key==='b')assert.ok(html.includes('Storyboard only — no playable video yet'));
}
function check(d){
 const m=JSON.parse(d.matrix);
 assert.equal(m.revision,'r285');
 assert.equal(m.status,'DRAFT_UNPUBLISHED_COMMERCIAL_HARD_HOLD');
 assert.equal(m.approval_status,'NOT_AUTHENTICATED');
 assert.equal(m.verified_account_permission,false);
 assert.equal(m.external_affiliate_urls_active,false);
 assert.equal(m.unapproved_merchant_hrefs_allowed,false);
 assert.deepEqual(m.source_register.map(x=>x.id),sources);
 assert.deepEqual(m.source_register.map(x=>x.url),["https://pubmed.ncbi.nlm.nih.gov/3612492/","https://www.psychologicalscience.org/journals/psychological-science/j.1467-9280.1997.tb00399.x/","https://pubmed.ncbi.nlm.nih.gov/32286932/","https://pubmed.ncbi.nlm.nih.gov/8295117/","https://doi.org/10.1111/acps.13225","https://pubmed.ncbi.nlm.nih.gov/37205669/","https://inspire3.com/","https://zen12.com/hnp","https://zen12.com/freeaudio","https://hypnosislive.com/mental-skills/total-focus","https://hypnosislive.com/faq","https://brainwaveshots.com/focus-shot","https://brainwaveshots.com/faq","https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking","https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance","https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/","https://finalvestige.com/focus/","https://finalvestige.com/2026/11/02/change-blindness/","https://finalvestige.com/2026/11/02/mesmerism/","https://www.youtube.com/watch?v=SV9m07PFTYk"],'exact source URLs; no substituted evidence');
 assert.equal(new Set(m.source_register.map(x=>x.url)).size,20);
 assert.ok(m.source_register.every(x=>/^https:\/\/\S+$/.test(x.url)));
 assert.deepEqual(m.commercial_gates.map(x=>x.id),gates);
 assert.ok(m.commercial_gates.every(x=>x.state==='HARD_HOLD'&&x.proof===null));
 assert.deepEqual(m.offer_candidates.map(x=>x.id),offers);
 for(const o of m.offer_candidates){
  assert.equal(o.commercial_state,o.id==='fv_free_focus'?'FREE_LEAD_NOT_SALE':'HARD_HOLD');
  assert.equal(o.approved_partner_link,null);
  assert.equal(o.verified_checkout_total,null);
  assert.equal(o.verified_paid_orders,null);
 }
 assert.equal(m.offer_candidates[4].free_url,'https://finalvestige.com/focus/');
 assert.equal(m.claims.length,24);
 assert.equal(new Set(m.claims.map(x=>x.id)).size,24);
 assert.ok(m.claims.every(x=>sources.includes(x.source_id)&&x.decision&&x.kind));
 for(const [id,state] of [['C10','EXCLUDE_AS_FACT'],['C11','EXCLUDE_AS_FACT'],['C12','MUST_SEPARATE_FROM_FV'],['C15','MUST_DISCLOSE_IF_COMPARING'],['C18','MUST_DISCLOSE_IF_COMPARING'],['C19','MUST_DISCLOSE'],['C20','EXCLUDE_AS_FACT'],['C21','REQUIRE_NEAR_CTA'],['C22','REQUIRE_PRODUCT_SPECIFIC'],['C24','EXCLUDE_AS_FACT']])
  assert.equal(m.claims.find(x=>x.id===id)?.decision,state,id);
 assert.equal(m.creator_routes.length,3);
 assert.ok(m.creator_routes.every(x=>x.grok_asset_id===null));
 assert.equal(m.creator_routes[1].proof_state,'PUBLIC_TOPIC_WITNESS_NOT_INTERNAL_ID');
 assert.equal(m.experiment.not_live,true);
 assert.ok(m.experiment.variant_b.includes('nonplayable'));
 assert.ok(m.measurement.affiliate_click.includes('not a paid sale'));
 assert.ok(m.measurement.net_revenue_per_1000.startsWith('NULL'));
 assert.deepEqual(m.measurement.cohorts_days,[7,30]);
 assert.equal(m.release_gate,'HARD_HOLD');
 assert.ok(d.article.split(/\s+/).length>=2100);
 for(const s of ['31 studies','1987','2020','rebound','cognitive load','https://pubmed.ncbi.nlm.nih.gov/3612492/','https://pubmed.ncbi.nlm.nih.gov/32286932/','https://zen12.com/hnp','no earning links','not a clinical trial','https://finalvestige.com/focus/'])
  assert.ok(d.article.toLowerCase().includes(s.toLowerCase()),'article grounding '+s);
 for(const k of ['a','b','hub','newHub'])auditMarkup(d[k],k);
 for(const k of ['a','b'])for(const term of ['five refunded sessions in a year','one refund within any six-month period','with epilepsy','seller FAQ'])assert.ok(d[k].includes(term),'merchant-specific policy shown in buyer '+k+': '+term);
 assert.ok(!d.a.includes('class="film"'));
 assert.ok(d.b.includes('class="film"'));
 assert.ok(d.newHub.includes('unpublished design candidate'));
 assert.ok(d.newHub.includes('PR #172'));
 assert.ok(d.newHub.includes('not playable media'));
 function normalize(h){return h.replace(/<aside class="film"[\s\S]*?<\/aside>/,'').replace(/Variant B \/ optional film concept/g,'Variant A / text only');}
 assert.equal(normalize(d.b),normalize(d.a),'A/B body parity');
}
const fixture=read();check(fixture);
const attempts=[];
const payloads=[
 '<script src="https://t.invalid/x.js"></script>',
 '<img src="https://t.invalid/pixel.gif">',
 '<iframe src="https://zen12.com/hnp"></iframe>',
 '<form action="/newlist"><input></form>',
 '<video autoplay src="https://t.invalid/a.mp4"></video>',
 '<a href=https://zen12.com/hnp>Pay</a>',
 '<a href="https://&#x7a;en12.com/hnp">Pay</a>',
 '<a href="&#104;ttps://zen12.com/hnp">Pay</a>',
 '<a href="javascript&#58;alert(1)">Pay</a>',
 '<a href="data:text/html,foo">Pay</a>',
 '<a href="https://finalvestige.com/focus/" onclick="buy()">Pay</a>',
 '<a href="https://finalvestige.com/focus/" onfocus=buy()>Pay</a>',
 '<meta http-equiv="refresh" content="0;url=https://zen12.com/hnp">',
 '<link rel="preload" href="https://t.invalid/a">',
 '<svg><a xlink:href="https://zen12.com/hnp">Pay</a></svg>',
 '<div style="background:url(https://t.invalid/pixel)">Pixel</div>',
 '<style>@import "https://t.invalid/track.css";</style>',
 '<a href="https://finalvestige.com/focus/" href="https://zen12.com/hnp">Dbl</a>',
 '<a href="https://finalvestige.com/focus/" ping="https://t.invalid/hit">Track</a>',
 '<button type="button" aria-describedby="r285-disclosure">ACTIVE</button>',
 '<a href="#new-buyer-list">New form</a>'
];
for(const k of ['a','b','hub','newHub'])for(const p of payloads)attempts.push([k,s=>s+'</div>'+p]);
for(const change of [
 m=>m.verified_account_permission=true,
 m=>m.external_affiliate_urls_active=true,
 m=>m.approval_status='VERIFIED',
 m=>m.unapproved_merchant_hrefs_allowed=true,
 m=>m.commercial_gates[0].state='APPROVED',
 m=>m.commercial_gates[0].proof=true,
 m=>m.commercial_gates.splice(1,1),
 m=>m.offer_candidates[0].commercial_state='ACTIVE',
 m=>m.offer_candidates[0].approved_partner_link='https://zen12.com/x?id=123',
 m=>m.offer_candidates[4].free_url='https://zen12.com/gift',
 m=>m.offer_candidates.splice(5,1),
 m=>m.creator_routes[1].grok_asset_id='invented',
 m=>m.creator_routes[1].proof_state='VERIFIED',
 m=>m.claims[9].decision='ALLOW_AS_FACT',
 m=>m.claims[20].decision='OPTIONAL',
 m=>m.measurement.net_revenue_per_1000='0 estimated',
 m=>m.experiment.not_live=false,
 m=>m.release_gate='APPROVED',
 m=>m.source_register[0].url='https://false.invalid/',
 m=>m.claims[0].source_id='missing_source'
])attempts.push(['matrix',s=>{let m=JSON.parse(s);change(m);return JSON.stringify(m); }]);
for(const term of ['five refunded sessions in a year','one refund within any six-month period','with epilepsy'])attempts.push(['both',s=>s.replaceAll(term,'withheld merchant policy')]);
attempts.push(['article',s=>s.replaceAll('31 studies','3 studies')]);
attempts.push(['article',s=>s.replace('https://pubmed.ncbi.nlm.nih.gov/3612492/','https://false.invalid/')]);
attempts.push(['both',s=>s+'<a href="https://zen12.com/hnp">Pay</a>']);
let rejected=0;
for(const [key,mutate] of attempts){
 const t={...fixture};
 if(key==='both'){t.a=mutate(t.a);t.b=mutate(t.b);}else t[key]=mutate(t[key]);
 assert.notDeepEqual(t,fixture,'mutation must change input');
 let failed=false;try{check(t);}catch(e){failed=true;}
 assert.ok(failed,'unsafe mutation escaped: '+key);
 rejected++;
}
console.log('R285 BASELINE PASS; '+rejected+'/'+attempts.length+' unsafe changes rejected; 16/16 commercial gates HARD_HOLD; canonical A/B parity; source-only, not browser or transaction proof.');
