'use strict';
/* FV Mind R287: source-only integrity suite (native: node mind/r287/verify_r287.cjs).
 Runs offline, reads only repository files; does not activate offers or change CMS.
 It is NOT an HTML5/browser/parser security audit nor merchant/payment acceptance. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const files={
 a:'../r284/ZEN12-BUYER-GUIDE-A-TEXT-ONLY-UNPUBLISHED.html',
 b:'../r284/ZEN12-BUYER-GUIDE-B-FILM-STORYBOARD-UNPUBLISHED.html',
 hub:'MIND-MCGURK-ARCHIVE-INSERT-WP-HTML-UNPUBLISHED.html',
 article:'THE-WORD-YOUR-EYES-PUT-INTO-SOMEONE-ELSES-MOUTH-UNPUBLISHED.md',
 matrix:'MCGURK-REFUND-SOURCE-COMMERCIAL-MATRIX.json',
 plan:'CONVERSION-TRUTH-SECURITY-AND-RELEASE-ACCEPTANCE.md'
};
const sourceMap=Object.fromEntries([
 ['mcgurk_1976','https://www.nature.com/articles/264746a0'],
 ['mcgurk_2018','https://pubmed.ncbi.nlm.nih.gov/30418995/'],
 ['mcgurk_model','https://pubmed.ncbi.nlm.nih.gov/25245268/'],
 ['mcgurk_stability','https://pubmed.ncbi.nlm.nih.gov/25802068/'],
 ['mcgurk_bias','https://pubmed.ncbi.nlm.nih.gov/30231054/'],
 ['mcgurk_review','https://doi.org/10.1163/22134808-00002565'],
 ['acute_2026','https://link.springer.com/article/10.1007/s11065-026-09714-9'],
 ['eeg_2023','https://pubmed.ncbi.nlm.nih.gov/37205669/'],
 ['inspire3','https://inspire3.com/'],
 ['zen12','https://zen12.com/hnp'],
 ['zen12_promo','https://zen12.com/secret/'],
 ['zen12_free','https://zen12.com/freeaudio'],
 ['hl_focus','https://hypnosislive.com/mental-skills/total-focus'],
 ['hl_faq','https://hypnosislive.com/faq'],
 ['bw_focus','https://brainwaveshots.com/focus-shot'],
 ['bw_faq','https://brainwaveshots.com/faq'],
 ['partner','https://affiliates.inspire3.com/'],
 ['ftc_endorse','https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking'],
 ['ftc_health','https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance'],
 ['fv_focus','https://finalvestige.com/focus/'],
 ['fv_change','https://finalvestige.com/2026/11/02/change-blindness/'],
 ['fv_mesmer','https://finalvestige.com/2026/11/02/mesmerism/'],
 ['fv_puy','https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/'],
 ['fv_collection','https://finalvestige.com/collection/']
]);
const gates='merchant_account_acceptance merchant_identity_matches_fv affiliate_terms_current permitted_traffic_channels approved_presell_placement issued_earning_url test_tracking_accepted offer_route_exact checkout_price_and_charges returns_eligibility_restrictions seller_creative_rights original_video_media_rights product_specific_claims_review adjacent_disclosure_qa browser_mobile_accessibility conversion_reporting_access founder_live_release_approval founder_commercial_activation_approval'.split(' ');
const urlAllow=new Set([
 '#main','https://finalvestige.com/focus/',
 'https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/',
 'https://finalvestige.com/affiliate-disclosure/',
 'https://finalvestige.com/editorial-standards/',
 'https://finalvestige.com/2026/11/02/change-blindness/',
 'https://pubmed.ncbi.nlm.nih.gov/37205669/',
 'https://pubmed.ncbi.nlm.nih.gov/38215647/',
 'https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking',
 'https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance',
 'https://www.nature.com/articles/264746a0'
]);
const tags=new Set('html head body meta title style header nav main footer section article aside div p h1 h2 h3 h4 strong small span br ol ul li time details summary table thead tbody tr th td a button'.split(' '));
const attributes=new Set('lang charset name content class id href aria-label aria-labelledby aria-describedby role type disabled scope'.split(' '));
const decodeEnt=s=>s.replace(/&#(x[0-9a-f]+|[0-9]+);?/gi,(m,n)=>{try{let cp=n[0].toLowerCase()==='x'?parseInt(n.slice(1),16):parseInt(n,10);return cp>0&&cp<=0x10ffff?String.fromCodePoint(cp):m;}catch{return m;}}).replace(/&(amp|quot|apos|colon|sol|tab|newline|lt|gt);?/gi,(m,n)=>({amp:'&',quot:'"',apos:"'",colon:':',sol:'/',tab:'\t',newline:'\n',lt:'<',gt:'>'})[n.toLowerCase()]||m);
function checkHtml(s,label){
 assert.ok(s.length>4000,label+' empty HTML');
 assert.ok(!/<\s*\/?(?:script|iframe|form|input|video|audio|object|embed|link|base|svg|img)\b/i.test(s),label+' unsafe element');
 assert.ok(!/\b(?:@import|@font-face|expression\s*\(|url\s*\()/i.test(s),label+' external CSS');
 assert.ok(!/<meta[^>]+http-equiv/i.test(s),label+' meta redirect');
 const extracted=s.replace(/<!--[\s\S]*?-->/g,'');
 let count=0,anchors=0,buttons=0;
 for(const m of extracted.matchAll(/<([a-z][\w-]*)\b([^<>]*?)>/gi)){
   count++;const tag=m[1].toLowerCase();let tail=m[2].trim();
   if(!tags.has(tag))throw Error(label+' tag '+tag);
   const attr={};const allowForTag=tag==='section'&&label==='hub'&&m[0].includes('id="fv-mind-r287"');
   while(tail){
     const q=tail.match(/^([a-z][a-z0-9:-]*)(?:\s*=\s*("[^"]*"|'[^']*'))?\s*/i);
     assert.ok(q,label+' malformed/unquoted attribute near '+tail.slice(0,40));
     const key=q[1].toLowerCase(),val=q[2]?q[2].slice(1,-1):null;
     assert.ok(!Object.prototype.hasOwnProperty.call(attr,key),label+' duplicate attr '+key);
     assert.ok(attributes.has(key)||(key==='style'&&allowForTag),label+' forbidden attr '+key);
     if(key==='disabled') assert.equal(val,null,label+' bad disabled');
     else assert.ok(val!==null,label+' attr value missing '+key);
     attr[key]=val;tail=tail.slice(q[0].length);
   }
   if(tag==='a'){
     anchors++;
     assert.equal(typeof attr.href,'string',label+' anchor lacks href');
     const value=attr.href;
     assert.equal(decodeEnt(value),value,label+' encoded URL');
     assert.ok(!/%[0-9a-f]{2}/i.test(value),label+' percent-encoded URL');
     assert.ok(urlAllow.has(value),label+' unapproved anchor '+value);
     assert.ok(!value.startsWith('//'),label+' protocol relative');
   }else assert.ok(!('href' in attr),label+' unexpected href attr');
   if(tag==='button'){
     buttons++;
     assert.ok('disabled' in attr,label+' enabled button');
     assert.equal(attr.type,'button',label+' button type');
     assert.equal(attr['aria-describedby'],label==='hub'?'m287-disclosure':'prospective-disclosure',label+' wrong disclosure reference');
   }
   if(label!=='hub') assert.ok(!('style' in attr),label+' inline style added');
 }
 assert.ok(count>20 && anchors>=4,label+' incomplete HTML');
 assert.equal(buttons,1,label+' noncanonical button count');
 const d=label==='hub'?'id="m287-disclosure"':'id="prospective-disclosure"';
 const pos=s.indexOf(d),b=s.indexOf('<button');
 assert.ok(pos>=0&&b>pos&&b-pos<1800,label+' disclosure not adjacent');
 assert.ok(s.slice(Math.max(0,pos-60),b).includes('affiliate disclosure:'),label+' no explicit prospective relationship');
 assert.ok(s.includes('https://finalvestige.com/focus/'),label+' free route missing');
 assert.ok(!/(?:googletagmanager\.com|google-analytics\.com|doubleclick\.net|facebook\.com\/tr)/i.test(s),label+' injected tracking endpoint');
}
function parity(a,b){
 const bText=b.replace(/<aside class="film"[\s\S]*?<\/aside>\s*/,'').replace('Variant B / optional film concept','Variant A / text only');
 assert.equal(bText.replace(/\s+/g,' ').trim(),a.replace(/\s+/g,' ').trim(),'A/B reader and buyer copy drift');
 assert.ok(b.includes('Static dark-gradient text poster')&&b.includes('Storyboard only — no playable video yet'),'B untruthful film claim');
 for(let i=0;i<7;i++) assert.ok(b.includes('00:'+String(i*6).padStart(2,'0')+'–00:'+String((i+1)*6).padStart(2,'0')),'B time missing '+i);
}
function check(s){
 const m=JSON.parse(s.matrix);
 assert.equal(m.version,'R287');assert.equal(m.publication,'UNPUBLISHED');assert.equal(m.commercial,'HARD_HOLD');
 assert.equal(m.parent_sha,'8078e6dac34723c47c190d1d63c373f373e5ad6f');
 assert.deepEqual(Object.fromEntries(m.sources.map(x=>[x.id,x.url])),sourceMap,'exact source ID / URL mapping drift');
 assert.equal(m.sources.length,Object.keys(sourceMap).length,'source count');
 assert.equal(m.claims.length,22,'claim coverage');
 const requiredDecisions={C05:'EXCLUDE_AS_FACT',C07:'EXCLUDE_AS_FACT',C08:'EXCLUDE_AS_FACT',C09:'DISCLOSE_SEPARATE_CONSENT',C11:'EXCLUDE_AS_FACT',C13:'EXCLUDE_AS_FACT',C14:'ATTRIBUTE_MERCHANT_WARNING',C15:'EXCLUDE_AS_FACT',C18:'REQUIRE_ADJACENT_DISCLOSURE',C19:'REQUIRE_PRODUCT_SPECIFIC_PROOF',C20:'EXCLUDE_AS_FACT',C21:'EXCLUDE_AS_FACT',C22:'EXCLUDE_AS_FACT'};
 for(const c of m.claims){assert.ok(sourceMap[c.source_id],c.id+' unsupported source');assert.ok(c.statement&&c.limit&&c.decision,c.id+' incomplete');if(requiredDecisions[c.id])assert.equal(c.decision,requiredDecisions[c.id],c.id+' unacceptable decision');}
 assert.deepEqual(m.commercial_gates.map(x=>x.id),gates,'exact named authorization gates');
 for(const g of m.commercial_gates){assert.equal(g.state,'HARD_HOLD',g.id);assert.equal(g.proof,null,g.id);assert.equal(g.approval_reference,null,g.id);}
 for(const o of m.offers){assert.equal(o.approved_earning_url,null,o.id+' activated');assert.ok(o.commercial_state==='HARD_HOLD'||o.commercial_state==='FREE_NOT_PAID'||o.commercial_state==='NOT_AUTHENTICATED',o.id+' commercial state');}
 assert.equal(m.offers[0].verified_paid_orders,null);
 for(const k of ['asset_id','qualified_human_sessions','affiliate_clicks','verified_paid_orders','settled_commission','realized_net_revenue','net_revenue_per_1000_qualified_human_sessions'])assert.equal(m.measurement[k],null,'fake metric '+k);
 assert.equal(m.measurement.missing_rule,'NULL_NOT_COMPUTABLE_NOT_ZERO');
 assert.deepEqual(m.measurement.cohorts_days,[7,30]);
 for(const [k,v]of Object.entries(m.release_controls))assert.equal(v,false,'release control '+k);
 assert.equal(m.creator_routes.length,3);
 for(const r of m.creator_routes)assert.equal(r.grok_asset_id,null,'fake creator ID');
 for(const k of ['a','b','hub'])checkHtml(s[k],k);
 parity(s.a,s.b);
 for(const [label,html] of [['A',s.a],['B',s.b]]){
   for(const phrase of [
     'one refund within any six-month period',
     'orders exceeding ten items, refund eligibility also requires that fewer than half of the ordered items have been downloaded',
     'no more than five refunded sessions','epilepsy',
     'at no additional cost to you','Zen12 purchase link unavailable'
   ])assert.ok(html.includes(phrase),label+' missing buyer truth '+phrase);
   assert.ok(!html.includes('adds restrictions for orders exceeding ten items'),'old omission remains');
 }
 for(const phrase of ['Harry McGurk','1976','2018','Puységur','no evidence','twelve-minute','r = 0.91'])assert.ok(s.article.toLowerCase().includes(phrase.toLowerCase()),'missing editorial evidence '+phrase);
 for(const id of ['mcgurk_1976','mcgurk_2018','mcgurk_model','mcgurk_stability','mcgurk_bias','mcgurk_review'])assert.ok(s.article.includes(sourceMap[id]),'article missing primary evidence '+id);
 assert.ok(!/\]\(https:\/\/(?:www\.)?(?:zen12|inspire3|hypnosislive|brainwaveshots)\.com/i.test(s.article),'active merchant link in article');
 for(const id of Object.keys(sourceMap))assert.ok(s.matrix.includes(sourceMap[id]),'matrix source removed '+id);
 assert.ok(s.plan.includes('fewer than half')&&s.plan.includes('NOT COMPUTABLE'),'acceptance plan incomplete');
 return true;
}
function load(){return Object.fromEntries(Object.entries(files).map(([k,file])=>[k,fs.readFileSync(path.join(__dirname,file),'utf8')]));}
function mutationTests(base){
 const mutations=[];
 for(let i=0;i<gates.length;i++)mutations.push(['gate-'+i,s=>{let m=JSON.parse(s.matrix);m.commercial_gates[i].state='APPROVED';s.matrix=JSON.stringify(m)}]);
 mutations.push(
 ['source substituted',s=>{let m=JSON.parse(s.matrix);m.sources[0].url='https://fake.example/test';s.matrix=JSON.stringify(m)}],
 ['source ID shuffled',s=>{let m=JSON.parse(s.matrix);m.sources[0].id='renamed';s.matrix=JSON.stringify(m)}],
 ['fake revenue',s=>{let m=JSON.parse(s.matrix);m.measurement.realized_net_revenue=123;s.matrix=JSON.stringify(m)}],
 ['fake qualified session',s=>{let m=JSON.parse(s.matrix);m.measurement.qualified_human_sessions=42;s.matrix=JSON.stringify(m)}],
 ['fake grok ID',s=>{let m=JSON.parse(s.matrix);m.creator_routes[0].grok_asset_id='guess123';s.matrix=JSON.stringify(m)}],
 ['affiliate link in offer',s=>{let m=JSON.parse(s.matrix);m.offers[0].approved_earning_url='https://zen12.com/?a=fake';s.matrix=JSON.stringify(m)}],
 ['commission authorization',s=>{let m=JSON.parse(s.matrix);m.release_controls.merchant_links_active=true;s.matrix=JSON.stringify(m)}],
 ['no refund download condition A',s=>{s.a=s.a.replace('fewer than half of the ordered items have been downloaded','further restrictions apply')}],
 ['no refund download condition B',s=>{s.b=s.b.replace('fewer than half of the ordered items have been downloaded','further restrictions apply')}],
 ['only B parity drift',s=>{s.b=s.b.replace('12 levels','13 levels')}],
 ['both versions lose refund cap',s=>{s.a=s.a.replace('no more than five refunded sessions','unlimited refunds');s.b=s.b.replace('no more than five refunded sessions','unlimited refunds')}],
 ['missing adjacent disclosure',s=>{s.a=s.a.replace('id="prospective-disclosure"','id="gone"')}],
 ['second enabled control',s=>{s.b=s.b.replace('</main>','<button type="button">Buy now</button></main>')}],
 ['form injected',s=>{s.hub+=' <form action="https://zen12.com/"><input type="email"></form>'}],
 ['merchant direct link',s=>{s.a=s.a.replace('href="https://finalvestige.com/focus/"','href="https://zen12.com/hnp"')}],
 ['encoded merchant link',s=>{s.a=s.a.replace('href="https://finalvestige.com/focus/"','href="&#104;ttps://zen12.com/hnp"')}],
 ['protocol relative merchant',s=>{s.a=s.a.replace('href="https://finalvestige.com/focus/"','href="//zen12.com/hnp"')}],
 ['percent encoded URL',s=>{s.b=s.b.replace('href="https://finalvestige.com/focus/"','href="https%3A%2F%2Fzen12.com%2Fhnp"')}],
 ['single quote unapproved href',s=>{s.b=s.b.replace('href="https://finalvestige.com/focus/"',"href='https://zen12.com/hnp'")}],
 ['merchant iframe',s=>{s.hub+='<iframe src="https://zen12.com/hnp"></iframe>'}],
 ['image pixel',s=>{s.hub+='<img src="https://tracker.example/a.gif">'}],
 ['resource image',s=>{s.a=s.a.replace('</main>','<picture><source srcset="//zen12.com/a"></picture></main>')}],
 ['onmouseover event',s=>{s.b=s.b.replace('<nav ', '<nav onmouseover="alert(1)" ')}],
 ['formaction',s=>{s.hub=s.hub.replace('<button type="button"','<button formaction="https://zen12.com" type="button"')}],
 ['CSS remote resource',s=>{s.a=s.a.replace('</style>','@import url(https://host.example/font);</style>')}],
 ['unlisted tag',s=>{s.hub+='<custom-element>Hi</custom-element>'}],
 ['unsupported claim',s=>{let m=JSON.parse(s.matrix);m.claims.find(x=>x.id==='C07').decision='ALLOW';s.matrix=JSON.stringify(m)}],
 ['disabled removed from sole purchase button',s=>{s.a=s.a.replace('type="button" disabled','type="button"')}],
 ['existing free funnel dropped',s=>{s.hub=s.hub.replaceAll('https://finalvestige.com/focus/','https://zen12.com/hnp')}],
 ['article hidden merchant anchor',s=>{s.article+=' [a](https://zen12.com/hnp)'}],
 ['unverified source count',s=>{let m=JSON.parse(s.matrix);m.sources.pop();s.matrix=JSON.stringify(m)}]
 );
 let passed=0;
 for(const [name,mutate] of mutations){
   const s={...base};mutate(s);
   let rejected=false;try{check(s)}catch(e){rejected=true;}
   assert.ok(rejected,'UNDETECTED MUTATION: '+name);
   passed++;
 }
 return passed;
}
function run(){const s=load();check(s);const rejected=mutationTests(s);console.log('R287 SOURCE BASELINE PASS; '+rejected+'/'+rejected+' intentionally unsafe mutations REJECTED; 18/18 authorization gates HARD_HOLD; HTML attribute/URL policy and A/B parity PASS; NO LIVE VALIDATION.');}
run();