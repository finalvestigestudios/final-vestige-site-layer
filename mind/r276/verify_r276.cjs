/* FV Mind R276. UNPUBLISHED static safety gate.
 * Native run: node mind/r276/verify_r276.cjs (from repository root).
 * Also exports validate/selfTest for isolated source-bound JS execution.
 * Static checks do NOT establish WCAG, WP sanitization, paid sales or merchant authorization.
 */
'use strict';
const assert=(condition,msg)=>{if(!condition)throw new Error(msg)};
const GATES=[
'named_inspire3_acceptance','issued_publisher_specific_earning_url','exact_zen12_offer_identity',
'current_authenticated_cart_total','refund_policy_scope_and_fulfillment','approved_web_promotion_channels',
'approved_email_promotion_channels','approved_creatives_or_swipe_terms','product_specific_claim_substantiation',
'affiliate_attribution_permissions','ftc_adjacent_disclosure_qa','signed_out_mobile_browser_qa',
'word_press_sanitization_qa','founder_commercial_release_approval',
'independent_settled_commission_report','verified_product_sales_and_refunds_reconciliation'];
const OFFER_IDS=['zen12_standard','zen12_distinct_promo','hypnosis_live_total_focus','brainwave_shots_focus','fv_paid_mind_owned'];
const RELEASE_KEYS=['cms_writes','publishing','social_posts','email_sends','merchant_links','new_tracking','new_forms','paid_services','merge_approved'];
const FORBIDDEN_RESOURCES=/<(?:script|iframe|form|video|audio|canvas|object|embed)\b|<link\s+[^>]*rel\s*=\s*["']?(?:preload|stylesheet|prefetch)|(?:src|srcset|action|poster|data|ping|formaction)\s*=\s*["']\s*(?:https?:|\/\/)/i;
const HELD=/commercial(?:_gates)?|release_controls/;
function linksFromHtml(html) {
 const out=[];
 const tags=html.match(/<a\b[^>]*>/gi)||[];
 for(const tag of tags){
   const found=tag.match(/\bhref\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))/i);
   if(found)out.push(found[1]||found[2]||found[3]);
 } return out;
}
function validate(b){
 ['guide','html','matrix','article275','module275','matrix275','variantA','variantB'].forEach(k=>assert(b[k]!==undefined,'missing '+k));
 const m=typeof b.matrix==='string'?JSON.parse(b.matrix):b.matrix;
 const older=typeof b.matrix275==='string'?JSON.parse(b.matrix275):b.matrix275;
 assert(m.schema==='fv-mind-r276-zen12-evidence-commercial-hold-v1','wrong schema');
 assert(m.release==='DRAFT_HARD_HOLD'&&m.public_activation===false,'premature activation');
 assert(m.exact_offer==='Zen12 Premium STANDARD only, not /secret promo','offer identity conflated');
 assert(m.sources.length===15&&m.claims.length===23,'source or claim count drift');
 const sid=new Set(m.sources.map(x=>x.id));assert(sid.size===15,'duplicate source ID');
 assert(new Set(m.sources.map(x=>x.url)).size===15,'duplicate source link');
 assert(m.sources.every(x=>/^https:\/\//.test(x.url)),'untrusted source URL');
 assert(m.claims.every(c=>c.id&&c.claim&&c.status&&c.limitation&&c.source_ids.length>0&&c.source_ids.every(id=>sid.has(id))),'unsourced claims');
 const statuses=new Map(m.claims.map(c=>[c.id,c.status]));
 assert(statuses.get('C06')==='unsupported_seller_efficacy'&&statuses.get('C07')==='unsupported_seller_health_performance','zen12 efficacy reclassified');
 assert(statuses.get('C10')==='not_supported'&&statuses.get('C15')==='unverified_partner_authorization','mechanism or approval false claim');
 assert(statuses.get('C19')==='not_supported_duplicate_topic_hold'&&statuses.get('C21')==='prohibited_revenue_inference','duplicate/sales false claim');
 assert(m.commercial_gates.length===16,'gate count');
 const gateSet=new Set(m.commercial_gates.map(g=>g.id));assert(gateSet.size===16&&GATES.every(id=>gateSet.has(id)),'gate identities');
 assert(m.commercial_gates.every(g=>g.status==='HARD_HOLD'&&g.evidence==='NOT_VERIFIED'&&g.release_blocker===true),'cleared commercial gate');
 assert(m.products.length===5&&OFFER_IDS.every(id=>m.products.find(x=>x.id===id))&&new Set(m.products.map(p=>p.id)).size===5,'offer list integrity');
 assert(m.products.every(p=>p.eligible_for_earning_cta===false),'merchant improperly enabled');
 for(const p of m.products) {assert(!p.issued_earning_url,'affiliate URL improperly inserted');}
 assert(m.products.find(p=>p.id==='fv_paid_mind_owned').sku===null,'unauthenticated owned SKU');
 assert(m.release_controls&&Object.keys(m.release_controls).length===RELEASE_KEYS.length&&RELEASE_KEYS.every(k=>m.release_controls[k]===false),'release flag key set or activation');
 assert(m.AB.hosted_video_playback===false&&m.AB.study_started===false&&m.AB.qualified_sample===false,'invented A/B results');
 assert(m.attribution.net_revenue_per_1000_qualified_human_sessions===null,'fabricated revenue KPI');
 assert(m.attribution.affiliate_click==='NEVER_A_SALE'&&m.attribution.settled_commission==='PARTNER_REPORTED_REQUIRED','click-sale conflation');
 assert(m.creative_matching.length===3&&m.creative_matching.every(v=>v.asset_id===null&&v.verified_clickable_path===false),'fabricated Grok creator asset identity');
 assert(m.canonical_overlap.r275_rubber_hand==='DUPLICATE_TOPIC_HOLD_R204_R218_R251'&&m.canonical_overlap.new_public_url_allowed===false,'canonical hold removed');
 assert(older.editorial_canonical_status.includes('R204_R218_R251'),'R275 hold absent');
 assert(older.release==='HARD_HOLD'&&older.commercial_gates.length===16&&older.commercial_gates.every(g=>g.status==='HARD_HOLD'),'R275 commercial hold weakened');
 assert(b.article275.includes('DUPLICATE HOLD')&&b.article275.includes('353')&&b.article275.includes('five participants')&&b.article275.includes('nineteen'),'R275 methodological corrections missing');
 assert(b.module275.includes('duplicate topic')&&b.module275.includes('s41467-022-28178-y'),'R275 reading module lacks hold/reply');
 assert(b.guide.length>11000&&b.guide.includes('A Twelve-Minute Soundtrack')&&b.guide.includes('No such earning link is active'),'guide not present');
 assert(b.guide.includes('Ingendoh')&&b.guide.includes('Chee'),'review studies absent');
 assert(b.guide.includes('fourth proposition')&&b.guide.includes('The comparison that matters'),'insufficient evidence trail');
 assert(b.html.startsWith('<!doctype html>')&&b.html.includes('<html lang="en"'),'missing semantic doc');
 for(const need of ['<main','<h1','<h2','<details','<summary','<ol','<button','type="button"','aria-disabled="true"','disabled','prefers-reduced-motion','focus-visible','@media(max-width:390px)','<meta name="viewport"','noindex,nofollow','https://finalvestige.com/focus/','If you purchase through a future authorized link'])assert(b.html.includes(need),'missing HTML requirement '+need);
 assert(!FORBIDDEN_RESOURCES.test(b.html),'external asset, form, script or forced media');
 assert(!/<input\b/i.test(b.html),'extra input');
 assert((b.html.match(/<button\b/gi)||[]).length===1,'multiple buyer controls');
 assert(/<button\b[^>]*\bdisabled\b[^>]*>/i.test(b.html),'purchase control enabled');
 const near=b.html.slice(b.html.indexOf('<button'),b.html.indexOf('<button')+900);
 assert(near.includes('If you purchase through a future authorized link')&&near.includes('there is no active')===false,'near CTA disclosure absent');
 const links=linksFromHtml(b.html);
 assert(links.length>=12,'expected source links missing');
 assert(links.every(x=>x.startsWith('#')||x.startsWith('https://')),'invalid link');
 const earningDomains=['zen12.com','hypnosislive.com','brainwaveshots.com','affiliates.inspire3.com'];
 assert(new Set(links.filter(x=>earningDomains.some(d=>(x.match(/^https?:\/\/([^/]+)/i)||[])[1]===d))).size<=2,'extra distinct merchant destinations');
 assert(links.filter(x=>/zen12\.com/.test(x)).every(x=>x==='https://zen12.com/hnp'||x==='https://zen12.com/secret/'),'unapproved merchant URL');
 assert(!/(?:awin1\.com|clickbank|hop=|affid=|affiliate_id=|ref=|utm_|fbclid=|gclid=|pixel)/i.test(b.html),'unauthorized tracking or affiliate token');
 const allowed=['finalvestige.com','zen12.com','inspire3.com','doi.org','ftc.gov'];
 assert(links.filter(x=>/^https:\/\//.test(x)).every(x=>allowed.includes((x.match(/^https:\/\/([^/]+)/i)||[])[1].replace(/^www\./,''))),'unreviewed outbound URL');
 assert(b.html.includes('Evidence before expectation'),'poster concept deleted');
 assert(b.variantA.includes('disabled')&&b.variantB.includes('disabled'),'inherited A/B purchase controls changed');
 assert(b.variantA.includes('If you purchase')&&b.variantB.includes('If you purchase'),'inherited A/B disclosure absent');
 return {source_count:m.sources.length,claims:m.claims.length,held_gates:m.commercial_gates.length,source_links:links.length,merchant_source_only:true,public_activation:false};
}
function selfTest(b) {
 const baseline=validate(b);
 const mutations=[
 ['activate',x=>{x.matrix.public_activation=true}],['gate',x=>{x.matrix.commercial_gates[0].status='APPROVED'}],['gateMissing',x=>{x.matrix.commercial_gates.pop()}],
 ['gateForged',x=>{x.matrix.commercial_gates[0].id='forged'}],['fakePaid',x=>{x.matrix.attribution.net_revenue_per_1000_qualified_human_sessions=50}],
 ['saleClicks',x=>{x.matrix.attribution.affiliate_click='COMMISSION'}],['sellerClaim',x=>{x.matrix.claims[5].status='proven'}],['approvalClaim',x=>{x.matrix.claims[14].status='approved'}],
 ['ownedSku',x=>{x.matrix.products[4].sku='invented-sku'}],['merchantEnabled',x=>{x.matrix.products[0].eligible_for_earning_cta=true}],
 ['earningURL',x=>{x.matrix.products[0].issued_earning_url='https://example.com/earn'}],['creatorAsset',x=>{x.matrix.creative_matching[1].asset_id='invented'}],
 ['releaseFlag',x=>{x.matrix.release_controls.merchant_links=true}],['deleteReleaseFlag',x=>{delete x.matrix.release_controls.new_tracking}],
 ['fakeAB',x=>{x.matrix.AB.study_started=true}],['hosting',x=>{x.matrix.AB.hosted_video_playback=true}],
 ['sourceZero',x=>{x.matrix.sources=[]}],['fakeSource',x=>{x.matrix.claims[0].source_ids=['S99']}],
 ['duplicateOK',x=>{x.matrix.canonical_overlap.new_public_url_allowed=true}],['removeR275',x=>{x.article275=x.article275.replace('DUPLICATE HOLD','PUBLISHABLE')}],
 ['removeReply',x=>{x.module275=x.module275.replace('s41467-022-28178-y','missing')}],['unholdR275',x=>{x.matrix275.commercial_gates[0].status='OK'}],
 ['removeViewport',x=>{x.html=x.html.replace('name="viewport"','name="viewp0rt"')}],['badLanguage',x=>{x.html=x.html.replace('<html lang="en"','<html lang="fr"')}],
 ['newForm',x=>{x.html+='\n<form></form>'}],['script',x=>{x.html+='\n<script src="https://example.com/a.js"></script>'}],
 ['iframe',x=>{x.html+='\n<iframe src="https://example.com"></iframe>'}],['pixel',x=>{x.html+='\n<img src="https://example.com/1x1.png">'}],
 ['autoload',x=>{x.html+='\n<video autoplay></video>'}],['merchantButton',x=>{x.html=x.html.replace('disabled aria-disabled="true"','aria-disabled="false"')}],
 ['secondButton',x=>{x.html+='\n<button>Buy now</button>'}],['removeDisclosure',x=>{x.html=x.html.replace('If you purchase through a future authorized link','N/A')}],
 ['injectClickbank',x=>{x.html+='\n<a href="https://zen12.com/?hop=fake">Buy</a>'}],['newSeller',x=>{x.html+='\n<a href="https://merchant.example/c">Buy</a>'}],
 ['removeFocus',x=>{x.html=x.html.replace('https://finalvestige.com/focus/','https://example.org/')}],['newInput',x=>{x.html+='\n<input type=email>'}],
 ['removeMediaCSS',x=>{x.html=x.html.replace('@media(max-width:390px)','/* noop */')}],['removePoster',x=>{x.html=x.html.replace('Evidence before expectation','no')}],
 ['removeA',x=>{x.variantA=x.variantA.replace('disabled','required')}],['removeB',x=>{x.variantB=x.variantB.replace('If you purchase','No disclosure')}]
 ];
 let rejected=0,ineffective=[];
 for(const [name,fn] of mutations){const copy=JSON.parse(JSON.stringify(b));fn(copy);let didFail=false;try{validate(copy);}catch(_){didFail=true;}if(didFail)rejected++;else ineffective.push(name)}
 assert(ineffective.length===0,'unsafe mutation escaped: '+ineffective.join(', '));
 return {baseline,mutations_rejected:rejected,mutations_total:mutations.length};
}
module.exports={validate,selfTest,GATES,linksFromHtml};
if(require.main===module){
 const fs=require('fs'),path=require('path'),root=path.resolve(__dirname,'../..');
 const read=p=>fs.readFileSync(path.join(root,p),'utf8');
 const payload={guide:read('mind/r276/ZEN12-IS-A-STRUCTURED-LIBRARY-NOT-A-CLINICAL-PROMISE-UNPUBLISHED.md'),html:read('mind/r276/ZEN12-PURCHASE-EVIDENCE-ROOM-UNPUBLISHED.html'),matrix:JSON.parse(read('mind/r276/EXACT-OFFER-CLAIM-AND-CONVERSION-GATES.json')),article275:read('mind/r275/THE-HAND-THAT-WASNT-YOURS-UNPUBLISHED.md'),module275:read('mind/r275/MIND-BODY-OWNERSHIP-READING-MODULE-UNPUBLISHED.html'),matrix275:JSON.parse(read('mind/r275/RUBBER-HAND-PRODUCT-CLAIM-AUTHORIZATION-MATRIX.json')),variantA:read('mind/r268/ZEN12-A-TEXT-UNPUBLISHED.html'),variantB:read('mind/r268/ZEN12-B-OPTIONAL-FILM-UNPUBLISHED.html')};
 console.log(JSON.stringify(selfTest(payload),null,2));
}
