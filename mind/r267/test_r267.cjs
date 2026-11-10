// Final Vestige Mind R267 — reproducible source-only QA; Node: node mind/r267/test_r267.cjs
// Deliberately no network, tracking, commercial API calls, video playback or CMS mutations.
'use strict';
const fs = require('node:fs'), path = require('node:path');
const root = path.resolve(__dirname, '../..');
const read = p => fs.readFileSync(path.join(root, p), 'utf8');
const SOURCE_PATHS = {
  original: 'mind/r267/THE-WHITE-BEAR-IN-THE-ROOM-UNPUBLISHED.md',
  correction: 'mind/r266/THE-VOICE-THAT-COULD-NOT-TAKE-CONTROL-UNPUBLISHED.md',
  matrix266: 'mind/r266/SELF-HYPNOSIS-CLAIMS-PRODUCT-PARTNER-REVENUE-HOLD.json',
  evidence: 'mind/r267/WHITE-BEAR-OFFER-CLAIM-SOURCE-RELEASE-HOLD.json',
  buyerA: 'mind/r265/ZEN12-A-SOURCED-UNPUBLISHED.html',
  buyerB: 'mind/r265/ZEN12-B-OPTIONAL-FILM-UNPUBLISHED.html',
  hub: 'mind/r267/MIND-HUB-MODULAR-INTEGRATION-UNPUBLISHED.html',
  plan: 'mind/r267/CANONICAL-CONVERSION-REPAIR-EXPERIMENT-OWNER-PLAN.md'
};
const GATES=['named_partner_acceptance','written_product_permission','approved_social_channels','approved_email_channel','issued_tracking_url','affiliate_terms','approved_creatives_rights','exact_active_offer','cart_total_verified','returns_terms_verified','fulfillment_verified','product_specific_claim_substantiation','independent_disclosure_qa','first_party_attribution_review','verified_paid_merchant_reporting','founder_release_approval'];
function ok(x,msg){if(!x)throw new Error('R267 FAIL: '+msg)}
function eq(a,b,msg){ok(a===b,msg+' expected '+JSON.stringify(b)+' observed '+JSON.stringify(a))}
const visible = html => html.replace(/<style\b[^>]*>[\s\S]*?<\/style>/gi,'').replace(/<[^>]*>/g,' ').replace(/\s+/g,' ').trim();
function tags(html) {
  let result=[], m;
  const tagsRe=/<([a-z][\w:-]*)\b([^<>]*?)>/gi;
  while ((m=tagsRe.exec(html))) {
    let attrs={}, a, source=m[2];
    const re=/(?:^|\s)([^\s=/>]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'=<>\x60]+)))?/g;
    while ((a=re.exec(source))) attrs[a[1].toLowerCase()]={value:a[2]??a[3]??a[4]??'',quoted:a[4]===undefined,boolean:a[2]===undefined&&a[3]===undefined&&a[4]===undefined};
    result.push({name:m[1].toLowerCase(),attrs,raw:m[0],index:m.index});
  }
  return result;
}
function checkMarkup(html, commercialRequired) {
  const found=tags(html), disallowed=['script','iframe','form','video','audio','source','track','object','embed'];
  for(const t of found){
    ok(!disallowed.includes(t.name),'prohibited element '+t.name);
    if(t.attrs.autoplay)throw Error('R267 FAIL: autoplay attr');
    if(t.name==='a'){
      const h=t.attrs.href;ok(h&&h.quoted,'unquoted/absent href');
      ok(/^https:\/\/(?:finalvestige\.com|pubmed\.ncbi\.nlm\.nih\.gov|www\.ftc\.gov)\/.+/i.test(h.value),'unapproved or merchant URL '+h.value);
      ok(!/javascript:|data:/i.test(h.value),'unsafe URL protocol');
    }
    if(t.name==='button')ok(t.attrs.disabled&&t.attrs.type&&t.attrs.type.value==='button','all CTA controls disabled');
    if(t.name==='input')throw Error('R267 FAIL: additional input');
    if(t.name==='a'&&/zen12|inspire3|hypnosislive|brainwaveshots/i.test(t.raw))throw Error('R267 FAIL: merchant link');
  }
  ok(!/https?:\/\/(?:www\.)?(?:zen12|inspire3|hypnosislive|brainwaveshots)\.com/i.test(html),'merchant text URL in markup');
  if(commercialRequired){
    const i=html.indexOf('Potential earning-link disclosure:');
    const b=html.indexOf('<button',i);
    ok(i>=0&&b>i&&b-i<600,'prospective FTC disclosure immediately before CTA');
    ok(html.includes('Final Vestige may earn a commission'),'plain commission disclosure');
    const buttons=found.filter(t=>t.name==='button');eq(buttons.length,1,'exactly one held purchase CTA');
    ok(html.includes('https://finalvestige.com/focus/'),'existing Focus alternative');
  }
}
function verify(F){
  const a=F.original,c=F.correction,e=JSON.parse(F.evidence),m=JSON.parse(F.matrix266),p=F.plan;
  const ar=a.trim().split(/\s+/);ok(ar.length>=2000,'distinct substantial source-led investigation');
  for (const term of ['1987','white bear','1994','2009','five-minute','distracter','not itself a clinical','Puységur','no affiliate recommendation']) ok(a.toLowerCase().includes(term.toLowerCase()),'original missing '+term);
  for(const id of ['3612492','8121959','8295117','29040891'])ok(a.includes(id),'original missing primary source '+id);
  ok(!/https?:\/\/(?:zen12|inspire3|hypnosislive|brainwaveshots)\.com/i.test(a),'no seller endorsement link in article');
  ok(c.includes('The old story begins with an artillery officer'),'historical correction retained');
  ok(!c.includes('The old story begins with a physician'),'false historical identification');
  for(const term of ['53.4%','40.9%','P* = .04','P* = .06','partial η² = .02','205 of 250','191 at week twelve','time-matched','R254','R247'])ok(c.includes(term),'trial/canonical correction '+term);
  ok(!/a specific self-administered audio protocol outperformed its comparison on the reported measures/.test(c),'remove overbroad superiority');
  const c05=m.claims.find(q=>q.id==='C05');
  ok(c05&&c05.claim.includes('P=.06')&&c05.claim.includes('P=.04')&&c05.status==='INDEPENDENT_TRIAL_NOT_PRODUCT','C05 distinct endpoint evidence preserved');
  eq(e.status,'BUILT_SOURCE_CONTROLLED_UNPUBLISHED_COMMERCE_HARD_HOLD','hard-hold status');
  eq(e.sources.length,19,'source matrix size');
  eq(e.claims.length,20,'claim matrix size');
  const idset=new Set(e.sources.map(x=>x.id));eq(idset.size,e.sources.length,'no duplicate source ID');
  for(const s of e.sources)ok(/^https:\/\//.test(s.url),'verified source URL schema');
  for(const cl of e.claims){ok(cl.source_ids.length>0,'claims mapped');for(const id of cl.source_ids)ok(idset.has(id),'mapped claim source '+id)}
  for(const id of ['C12','C13','C14'])ok(e.claims.find(c=>c.id===id)?.status==='UNSUBSTANTIATED_SELLER_CLAIM_OMIT','unsupported efficacy omitted '+id);
  eq(e.gates.length,GATES.length,'commercial gate count');
  eq(new Set(e.gates.map(x=>x.id)).size,GATES.length,'unique commercial gates');
  for(const id of GATES){const g=e.gates.find(x=>x.id===id);ok(g&&g.status==='HARD_HOLD'&&g.evidence===null,'held authorization '+id)}
  ok(e.offer.issued_earning_url===null&&!e.offer.merchant_link_active&&!e.release.live&&!e.release.affiliate_active,'affiliate and release dormant');
  for(const key of ['gross_revenue','net_revenue','qualified_human_sessions','net_revenue_per_1000_qualified_human_sessions'])ok(e.privacy_measurement[key]===null,'unknown revenue remains null '+key);
  eq(e.creator_fit.length,3,'creator mapping count');
  for(const item of e.creator_fit)ok(item.media_asset_id===null,'never invent media asset ID');
  checkMarkup(F.buyerA,true);checkMarkup(F.buyerB,true);checkMarkup(F.hub,false);
  const faq=html=>{const x=html.match(/<p class="buyer-faq">([\s\S]*?)<\/p>/);ok(x,'seller-specific buyer FAQ exists');return visible(x[1])};
  eq(faq(F.buyerA),faq(F.buyerB),'A/B exact-Premium seller copy parity');
  for(const html of [F.buyerA,F.buyerB])for(const phrase of ['forty-eight-MP3','one-hour training call','one-year refund','no authenticated Final Vestige checkout'])ok(html.includes(phrase),'seller/terms copy '+phrase);
  ok(/Optional original 42-second film/i.test(F.buyerB),'video variant labeled optional');
  ok(!/Optional original 42-second film/i.test(F.buyerA),'text variant remains text only');
  ok(F.hub.includes('aria-labelledby')&&F.hub.includes('disabled aria-describedby')&&F.hub.includes('focus-visible'),'modular hub accessibility');
  for(const term of ['NOT TESTED','HARD HOLD','A/B','R254','R247','P=.06','Grok','Praxxis','Claude','Dispatch','Founder','issue #820','refunds'])ok(p.includes(term),'conversion owner/release plan '+term);
  return {source_count:e.sources.length,claim_count:e.claims.length,gate_count:e.gates.length,article_words:ar.length};
}
function run(f){
  const baseline=verify(f);
  const bad=[], inject=(name,mut)=>bad.push([name,mut]);
  for(const id of GATES)inject('falsify gate '+id,F=>{const m=JSON.parse(F.evidence);m.gates.find(x=>x.id===id).status='CLEARED';F.evidence=JSON.stringify(m)});
  inject('omit gate',F=>{const m=JSON.parse(F.evidence);m.gates.pop();F.evidence=JSON.stringify(m)});
  inject('invent paid revenue',F=>{const m=JSON.parse(F.evidence);m.privacy_measurement.net_revenue=300;F.evidence=JSON.stringify(m)});
  inject('invent media asset',F=>{const m=JSON.parse(F.evidence);m.creator_fit[0].media_asset_id='madeup';F.evidence=JSON.stringify(m)});
  inject('break citation map',F=>{const m=JSON.parse(F.evidence);m.claims[0].source_ids=['NO_SOURCE'];F.evidence=JSON.stringify(m)});
  inject('remove P06 historical source',F=>{F.original=F.original.replace('8121959','missing')});
  inject('reintroduce physician error',F=>{F.correction=F.correction.replace('begins with an artillery officer','begins with a physician')});
  inject('hide P=.06 caveat',F=>{F.correction=F.correction.replaceAll('P* = .06','P* = .05')});
  inject('promote unverified efficacy',F=>{F.evidence=F.evidence.replace('UNSUBSTANTIATED_SELLER_CLAIM_OMIT','PROVEN_PRODUCT_OUTCOME')});
  inject('put seller link A',F=>{F.buyerA=F.buyerA.replace('</main>','<a href="https://zen12.com/secret/">Buy</a></main>')});
  inject('put unquoted merchant link B',F=>{F.buyerB=F.buyerB.replace('</main>','<a href=https://zen12.com/hnp>Buy</a></main>')});
  inject('unsafe JS URL A',F=>{F.buyerA=F.buyerA.replace('</main>','<a href=javascript:alert(1)>go</a></main>')});
  inject('unsafe data URL B',F=>{F.buyerB=F.buyerB.replace('</main>','<a href="data:text/html,test">go</a></main>')});
  inject('activate commercial button A',F=>{F.buyerA=F.buyerA.replace('type="button" disabled','type="button"')});
  inject('remove adjacent disclosure B',F=>{F.buyerB=F.buyerB.replace('Potential earning-link disclosure:', 'Undisclosed:')});
  inject('force autoplay',F=>{F.buyerB=F.buyerB.replace('</main>','<video autoplay></video></main>')});
  inject('inject an extra signup form',F=>{F.hub=F.hub.replace('</section>','<form><input></form></section>')});
  inject('inject tracking script',F=>{F.buyerA=F.buyerA.replace('</main>','<script src="https://tracker.example/t.js"></script></main>')});
  inject('make A/B package mismatch',F=>{F.buyerB=F.buyerB.replace('one-year refund guarantee','three-day refund guarantee')});
  inject('remove existing Focus navigation',F=>{F.hub=F.hub.replaceAll('https://finalvestige.com/focus/','https://zen12.com/hnp')});
  inject('detach source receipt',F=>{const m=JSON.parse(F.evidence);m.sources.pop();F.evidence=JSON.stringify(m)});
  inject('assert sale from click',F=>{const m=JSON.parse(F.evidence);m.offer.merchant_link_active=true;F.evidence=JSON.stringify(m)});
  inject('remove duplicate-publication note',F=>{F.correction=F.correction.replace('R254','OTHER')});
  let rejected=0,passed=[];
  for(const [name,fn] of bad){const candidate={...f};fn(candidate);let threw=false;try{verify(candidate)}catch(_){threw=true}if(!threw)passed.push(name);else rejected++;}
  ok(passed.length===0,'unsafe mutations not rejected: '+passed.join(','));
  return {...baseline,adversarial_cases:bad.length,adversarial_rejected:rejected};
}
function loadAll(){const f={};for(const [key,p] of Object.entries(SOURCE_PATHS))f[key]=read(p);return f}
if(require.main===module){const r=run(loadAll());console.log('R267 BASELINE PASS; '+r.adversarial_rejected+'/'+r.adversarial_cases+' unsafe mutations rejected. Sources='+r.source_count+', claims='+r.claim_count+', gates='+r.gate_count+'.');}
module.exports={verify,run,loadAll,SOURCE_PATHS};
