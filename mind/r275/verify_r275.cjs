/* Final Vestige Mind R275 - dependency-free source custody and commercial safety checks.
 * Run from repository root: node mind/r275/verify_r275.cjs
 * This verifies static source invariants, NOT browser WCAG, merchant approval, checkout, or paid sales.
 */
'use strict';
const REQUIRED_GATES=[
'named_inspire3_acceptance','issued_publisher_specific_earning_url','exact_zen12_offer_identity',
'current_authenticated_cart_total','refund_policy_scope_and_fulfillment','approved_web_promotion_channels',
'approved_email_promotion_channels','approved_creatives_or_swipe_terms','product_specific_claim_substantiation',
'affiliate_attribution_permissions','ftc_adjacent_disclosure_qa','signed_out_mobile_browser_qa',
'word_press_sanitization_qa','founder_commercial_release_approval','independent_settled_commission_report',
'verified_product_sales_and_refunds_reconciliation'];
function ensure(bool,message){ if(!bool) throw new Error(message); }
function validate(bundle){
 const {article,html,matrix,acceptance,variantA,variantB}=bundle;
 [article,html,acceptance,variantA,variantB].forEach((s,i)=>ensure(typeof s==='string'&&s.length>1600,'missing source '+i));
 const m=typeof matrix==='string'?JSON.parse(matrix):matrix;
 ensure(m.schema==='fv-mind-r275-offer-science-eligibility-v1','wrong schema');
 ensure(m.release==='HARD_HOLD','premature release');
 ensure(m.status==='UNPUBLISHED_SOURCE_CONTROLLED','publication mislabel');
 ensure(m.gates_count===16&&m.commercial_gates.length===16,'16 gates required');
 const got=m.commercial_gates.map(x=>x.id);
 ensure(new Set(got).size===16&&REQUIRED_GATES.every(x=>got.includes(x)),'gate identifiers changed');
 ensure(m.commercial_gates.every(g=>g.status==='HARD_HOLD'&&g.evidence==='NOT_VERIFIED'&&g.release_blocker===true),'authorization falsely cleared');
 ensure(m.sources.length===18&&m.sources_count===18,'source inventory drift');
 ensure(m.claims.length===28&&m.claims_count===28,'claim inventory drift');
 const urls=new Set(m.sources.map(x=>x.id));
 ensure(new Set(m.sources.map(x=>x.url)).size===m.sources.length,'duplicate source URL');
 ensure(m.claims.every(c=>c.source_ids.length>0&&c.source_ids.every(s=>urls.has(s))),'unsourced claim');
 const questionable=/unverified|seller|prohibited|not_supported|public_offer_variance|supported_conditionally|regulatory_guidance/;
 ensure(m.claims.some(c=>c.id==='C05'&&c.status==='not_supported'),'expectancy failure not acknowledged');
 ensure(m.claims.some(c=>c.id==='C08'&&c.status==='not_supported'),'unresolved academic dispute mislabeled');
 ensure(m.claims.some(c=>c.id==='C17'&&c.status==='unsupported_seller_efficacy'),'false efficacy certification');
 ensure(m.claims.some(c=>c.id==='C20'&&c.status==='not_supported'),'price drift hidden');
 ensure(m.claims.some(c=>c.id==='C28'&&c.status==='prohibited_attribution_error'),'affiliate click equated with sale');
 ensure(m.options.length===5&&m.options.find(x=>x.id==='zen12_standard')?.eligible_for_live_cta===false,'unauthorized offer');
 ensure(m.options.find(x=>x.id==='fv_paid_mind_fallback')?.authorized_sku===null,'fabricated SKU');
 ensure(m.options.filter(x=>x.issued_earning_link).length===0,'active earning link');
 ensure(Object.values(m.release_controls).every(x=>x===false),'unapproved release flag');
 ensure(m.measurement.kpi_net_revenue_per_1000_qualified_human_sessions===null,'fabricated KPI');
 ensure(m.measurement.event_outbound_is_sale===false,'outbound counted as paid sale');
 ensure(m.creator_topic_fit.find(x=>x.topic.startsWith('Puységur'))?.internal_grok_asset_id===null,'public YouTube ID claimed as internal asset');
 ensure(m.creator_topic_fit.find(x=>x.topic.startsWith('Rubber-hand'))?.public_article===null,'unpublished article fabricated live');
 ensure(article.includes('https://www.nature.com/articles/s41467-022-28177-z')&&article.includes('https://www.nature.com/articles/s41467-022-28178-y'),'two-sided evidence dispute missing');
 ensure(article.includes('https://doi.org/10.1038/35784')&&article.includes('https://finalvestige.com/focus/'),'primary source/free alternative missing');
 ensure(article.includes('UNPUBLISHED')&&article.includes('No commercial recommendation'),'investigation independence missing');
 ensure(html.includes('name="robots" content="noindex,nofollow"')&&html.includes('<main ')&&html.includes('<h1'),'preview metadata/accessibility structure missing');
 ensure(html.includes('https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/')&&html.includes('https://finalvestige.com/focus/'),'contextual source navigation missing');
 ensure(!/<(script|iframe|form|video|audio|source|link)[\s>]/i.test(html),'unapproved active media/form/script/stylesheet');
 ensure(!/on(?:load|error|click|mouseover)\s*=/i.test(html),'inline handler');
 ensure(!/url\s*\(|@import|fetch\s*\(|navigator\.sendBeacon|dataLayer\s*\./i.test(html),'CSS/JS network resource');
 ensure(!/autoplay\s*=|<img\b[^>]*src\s*=|<svg\b[^>]*href\s*=/i.test(html),'remote image or force-play media');
 const anchors=[...html.matchAll(/href="([^"]+)"/g)].map(x=>x[1]);
 ensure(anchors.every(x=>/^https:\/\/(?:www\.)?(?:finalvestige\.com|zen12\.com|nature\.com|doi\.org)\//.test(x)||
 /^https:\/\/www\.ftc\.gov\//.test(x)),'unknown external URL or affiliate redirect');
 ensure(!/(?:awin1\.com|clickbank|[?&]ref=|affiliate[_-]?id|hoplink|rel="sponsored"|utm_source=)/i.test(html),'unexpected earning link');
 const button=[...html.matchAll(/<button\b([^>]*)>([\s\S]*?)<\/button>/gi)];
 ensure(button.length===1&&/\bdisabled\b/i.test(button[0][1])&&!/\bhref\b|\bformaction\b/i.test(button[0][1]),'CTA not disabled');
 const disclosure=html.indexOf('id="disclose"'),cta=html.indexOf('<button');
 ensure(disclosure>cta&&disclosure-cta<900&&html.includes('may earn a commission'),'adjacent disclosure missing');
 ensure(!/guaranteed\s+\$37|clinically proven to rewire|cures\s+(?:anxiety|depression)|made\s+us\s+wealthy/i.test(html+acceptance),'prohibited seller conclusion');
 ensure(acceptance.includes('NOT COMPUTABLE')&&acceptance.includes('merchant-confirmed')&&acceptance.includes('PR #172'),'revenue distinction or governance missing');
 ensure(acceptance.includes('360, 390, 768 and 1440')&&acceptance.includes('consent'),'mobile QA/consent criteria missing');
 [variantA,variantB].forEach((v,i)=>{ensure(/<button\b[^>]*disabled/i.test(v),'inherited pilot '+i+' CTA enabled');ensure(/may earn a commission/i.test(v),'inherited disclosure lost');ensure(!/<form\b|<script\b/i.test(v),'inherited extra form/script');});
 ensure(variantB.includes('42-second')&&variantA.includes('Is twelve minutes'),'inherited A/B cohort missing');
 return {passed:true,sources:m.sources.length,claims:m.claims.length,gates:m.commercial_gates.length,hrefs:anchors.length};
}
function adversarial(bundle){
 const mutations=[
 ['clear_authorization',x=>{x.matrix.commercial_gates[0].status='APPROVED';}],
 ['delete_gate',x=>{x.matrix.commercial_gates.pop();}],
 ['rename_gate',x=>{x.matrix.commercial_gates[0].id='approved_merchant';}],
 ['invent_partner_url',x=>{x.matrix.options[0].issued_earning_link='https://seller.example/earn';}],
 ['enable_offer',x=>{x.matrix.options[0].eligible_for_live_cta=true;}],
 ['enable_publishing',x=>{x.matrix.release_controls.merge_approved=true;}],
 ['invent_product',x=>{x.matrix.options[4].authorized_sku='imaginary';}],
 ['invent_kpi',x=>{x.matrix.measurement.kpi_net_revenue_per_1000_qualified_human_sessions=999;}],
 ['count_click_sale',x=>{x.matrix.measurement.event_outbound_is_sale=true;}],
 ['invent_creator_id',x=>{x.matrix.creator_topic_fit[0].internal_grok_asset_id='SV9m07PFTYk';}],
 ['invent_live_article',x=>{x.matrix.creator_topic_fit[2].public_article='https://finalvestige.com/mind/rubber-hand/';}],
 ['erase_source',x=>{x.matrix.sources.shift();}],
 ['remove_claim_caveat',x=>{x.matrix.claims.find(c=>c.id==='C17').status='supported';}],
 ['hide_price_drift',x=>{x.matrix.claims.find(c=>c.id==='C20').status='supported';}],
 ['remove_disclosure',x=>{x.html=x.html.replace('may earn a commission','maybe a partner');}],
 ['activate_button',x=>{x.html=x.html.replace('type="button" disabled','type="button"');}],
 ['inject_form',x=>{x.html+='\n<form><input type="email"></form>';}],
 ['inject_script',x=>{x.html+='\n<script src="https://tracker.invalid/x.js"></script>';}],
 ['inject_css_resource',x=>{x.html=x.html.replace('</style>','body{background:url(https://tracker.invalid/pixel)}</style>');}],
 ['inject_merchant',x=>{x.html=x.html.replace('</main>','<a href="https://evil.example/affiliate">Buy</a></main>');}],
 ['inject_earning_link',x=>{x.html=x.html.replace('</main>','<a href="https://www.awin1.com/cread.php">Buy</a></main>');}],
 ['strip_free_path',x=>{x.html=x.html.replaceAll('https://finalvestige.com/focus/','/invalid');}],
 ['bad_scholarship',x=>{x.article=x.article.replaceAll('https://www.nature.com/articles/s41467-022-28177-z','unverified');}],
 ['delete_article_independence',x=>{x.article=x.article.replace('No commercial recommendation','Commercial recommendation');}],
 ['missing_campaign_consents',x=>{x.acceptance=x.acceptance.replaceAll('consent','no privacy rules');}],
 ['remove_inherited_disclosure',x=>{x.variantA=x.variantA.replaceAll('may earn a commission','may earn nothing');}],
 ['enable_inherited_offer',x=>{x.variantB=x.variantB.replace(/<button([^>]*)disabled/,'<button$1');}]
 ];
 let rejected=0,escaped=[];
 for(const [name,mutate] of mutations){
  const x={...bundle,matrix:JSON.parse(JSON.stringify(bundle.matrix))};mutate(x);
  try{validate(x);escaped.push(name);}catch(_){rejected++;}
 }
 if(escaped.length)throw new Error('unsafe mutations escaped: '+escaped.join(', '));
 return {rejected,total:mutations.length};
}
module.exports={validate,adversarial,REQUIRED_GATES};
if(typeof require!=='undefined'&&require.main===module){
 const fs=require('node:fs'),path=require('node:path');const cwd=process.cwd();function read(p){return fs.readFileSync(path.join(cwd,p),'utf8');}
 const b={
 article:read('mind/r275/THE-HAND-THAT-WASNT-YOURS-UNPUBLISHED.md'),
 html:read('mind/r275/MIND-BODY-OWNERSHIP-READING-MODULE-UNPUBLISHED.html'),
 matrix:JSON.parse(read('mind/r275/RUBBER-HAND-PRODUCT-CLAIM-AUTHORIZATION-MATRIX.json')),
 acceptance:read('mind/r275/OFFER-TO-NET-REVENUE-PILOT-AND-CREATOR-ACCEPTANCE.md'),
 variantA:read('mind/r268/ZEN12-A-TEXT-UNPUBLISHED.html'),
 variantB:read('mind/r268/ZEN12-B-OPTIONAL-FILM-UNPUBLISHED.html')
 };
 console.log(JSON.stringify({baseline:validate(b),adversarial:adversarial(b)},null,2));
}
