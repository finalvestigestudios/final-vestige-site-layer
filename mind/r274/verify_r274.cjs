'use strict';
/**
 * FV Mind R274 — pure static/source audit. Zero dependencies.
 * Usage at repository root: node mind/r274/verify_r274.cjs
 * Source assertions are NOT browser QA, checkout QA, WCAG certification, or paid conversion tests.
 */
const fs = require('node:fs');
const path = require('node:path');
const ROOT = path.resolve(__dirname, '../..');
const dir = 'mind/r274/';
const requiredGateIds = [
'named_inspire3_acceptance','issued_publisher_specific_earning_url','exact_zen12_offer_identity',
'current_authenticated_cart_total','refund_policy_scope_and_fulfillment','approved_web_promotion_channels',
'approved_email_promotion_channels','approved_creatives_or_swipe_terms','product_specific_claim_substantiation',
'affiliate_attribution_permissions','ftc_adjacent_disclosure_qa','signed_out_mobile_browser_qa',
'word_press_sanitization_qa','founder_commercial_release_approval',
'independent_settled_commission_report','verified_product_sales_and_refunds_reconciliation'
];
function filesFromDisk() {
 const read = name => fs.readFileSync(path.join(ROOT,dir,name),'utf8');
 return {article:read('THE-EXPERIMENT-THAT-MADE-DISTRACTION-DISAPPEAR-UNPUBLISHED.md'),
   hub:read('MIND-ARCHIVE-RESEARCH-MODULE-UNPUBLISHED.html'),
   matrix:read('PRODUCT-CLAIM-SOURCE-REVENUE-GATES.json'),
   plan:read('ONE-OFFER-CONVERSION-AB-ATTRIBUTION-ACCEPTANCE.md')};
}
function audit(input) {
 let a={};try{a=JSON.parse(input.matrix)}catch(e){return ['INVALID_JSON: '+e.message]}
 const errors=[];
 const check=(predicate,code)=>{if(!predicate)errors.push(code)};
 check(a.schema==='fv-mind-r274-evidence-commerce-gates-v1','MATRIX_SCHEMA');
 check(a.status==='UNPUBLISHED_SOURCE_CONTROLLED' && a.release==='HARD_HOLD','MATRIX_RELEASE');
 check(a.release_controls?.affiliate_links_active===false && a.release_controls?.WordPress_live_edits===false &&
 a.release_controls?.merge_approved===false && a.release_controls?.newsletter_edits===false,'RELEASE_CONTROLS');
 check(Array.isArray(a.sources) && a.sources.length>=20 && a.sources.every(x=>/^https:\/\//.test(x.url)),'PROVENANCE_SOURCES');
 check(new Set((a.sources||[]).map(x=>x.id)).size===(a.sources||[]).length,'SOURCE_DUPLICATES');
 check(Array.isArray(a.claims) && a.claims.length>=24,'CLAIMS_INVENTORY');
 check((a.claims||[]).every(x=>x.source_ids.every(id=>(a.sources||[]).some(s=>s.id===id))),'CLAIM_SOURCE_INTEGRITY');
 check((a.claims||[]).find(x=>x.id==='C19')?.status==='NOT_VERIFIED' &&
 (a.claims||[]).find(x=>x.id==='C20')?.status==='NOT_VERIFIED' &&
 (a.claims||[]).find(x=>x.id==='C25')?.status==='NOT_COMPUTABLE','COMMERCIAL_RESULT_TRUTH');
 check((a.claims||[]).find(x=>x.id==='C08')?.status==='unsupported_extrapolation','LOAD_CONCLUSION_LIMITS');
 check((a.claims||[]).find(x=>x.id==='C12')?.status==='unsupported_seller_efficacy_withhold','SELLER_CLAIM_BOUNDARY');
 check(Array.isArray(a.commercial_gates) && a.commercial_gates.length===16 &&
 requiredGateIds.every(id=>a.commercial_gates.some(g=>g.id===id)) &&
 a.commercial_gates.every(g=>g.status==='HARD_HOLD' && g.release_blocker===true && g.evidence==='NOT_VERIFIED'),'SIXTEEN_GATES_HARD_HOLD');
 check(new Set((a.commercial_gates||[]).map(g=>g.id)).size===16,'GATE_UNIQUENESS');
 const offer=(a.products||[]).find(p=>p.id==='zen12_premium_standard');
 check(!!offer && offer.page==='https://zen12.com/hnp' && offer.separate_offer==='https://zen12.com/secret/' && offer.account_issued_affiliate_link===null && offer.checkout_total===null && offer.eligible_for_live_earning_cta===false,'ZEN12_APPROVAL_HOLD');
 const owned=(a.products||[]).find(p=>p.id==='fv_owned_paid_mind');
 check(!!owned && owned.sku===null && owned.active_checkout===null && owned.paid_orders===null,'OWNED_PAID_PRODUCT_HOLD');
 check(a.measurement?.implement_new_scripts===false && a.measurement?.no_fingerprinting===true &&
 a.measurement?.no_personal_data===true && a.measurement?.kpi_status==='NOT_COMPUTABLE' &&
 a.measurement?.cohorts_days?.join(',')==='7,30','PRIVACY_AND_KPI_HOLD');
 check(Array.isArray(a.creator_topic_fit) && a.creator_topic_fit.length===3 &&
 a.creator_topic_fit.every(t=>t.media_id===null && t.media_url===null),'NO_FABRICATED_GROK_ASSETS');
 check(a.creator_topic_fit?.[2]?.public_article===null,'NO_FAKE_UNPUBLISHED_ARTICLE_URL');
 check(input.article.includes('The Experiment That Made Distraction Disappear') && input.article.includes('2025') &&
 input.article.includes('Eltiti') && input.article.includes('Puységur') &&
 input.article.includes('replicat'),'ARTICLE_EVIDENCE');
 check(!/\\[(?:buy|purchase|checkout|order|get started|claim)[^\\]]*\\]\\(https?:\\/\\/(?:zen12\\.com|hypnosislive\\.com|brainwaveshots\\.com|affiliates\\.inspire3\\.com)/i.test(input.article),'ARTICLE_NO_SALES_CTA');
 check(input.article.includes('does not demonstrate') && input.article.includes('failure to replicate') &&
 input.article.includes('It will not reproduce a laboratory effect'),'ARTICLE_LIMITATIONS');
 check(input.hub.includes('UNPUBLISHED') && input.hub.includes('noindex,nofollow') &&
 input.hub.includes('<main>') && input.hub.includes('lang="en"') &&
 input.hub.includes('prefers-reduced-motion'),'HUB_STRUCTURE');
 check(/<button\b[^>]*\bdisabled\b[^>]*>/.test(input.hub),'DISABLED_CTA');
 const ctaIdx=input.hub.indexOf('Merchant offer unavailable pending verification');
 const discloseIdx=input.hub.indexOf('If a future approved purchase link');
 check(ctaIdx>=0 && discloseIdx>ctaIdx && discloseIdx-ctaIdx<600,'NEAR_CTA_FTC_DISCLOSURE');
 check(input.hub.includes('There is no active merchant or affiliate link') &&
 input.hub.includes('no additional cost to you'),'FTC_CLARITY');
 check(!/<(?:script|iframe|form|video|audio)\b/i.test(input.hub) &&
 !/\bonclick\s*=|\bonerror\s*=|autoplay|<meta[^>]+http-equiv/i.test(input.hub),'HUB_NO_SCRIPTS_FORMS_MEDIA');
 check(!/url\s*\(\s*['"]?\s*(?:https?:|\/\/|data:)/i.test(input.hub) &&
 !/<use\b/i.test(input.hub) && !/<svg\b[^>]+(?:href|xlink:href)/i.test(input.hub),'HUB_NO_HIDDEN_RESOURCES');
 const hrefs=[...input.hub.matchAll(/\bhref\s*=\s*["']([^"']+)["']/g)].map(x=>x[1]);
 check(hrefs.length>=4 && hrefs.every(h=>/^https:\/\/finalvestige\.com\//.test(h)),'HUB_ONLY_FIRST_PARTY_LINKS');
 check(input.hub.includes('aria-describedby="commercial-disclosure commercial-hold"') &&
 input.hub.includes('id="commercial-disclosure"'),'BUTTON_ACCESSIBILITY');
 check(input.hub.includes('@media(max-width:760px)') &&
 input.hub.includes(':focus-visible'),'RESPONSIVE_KEYBOARD');
 check(input.plan.includes('**B is not a playable video') &&
 input.plan.includes('A/B is NOT LIVE') && input.plan.includes('HARD HOLD'),'AB_EXPERIMENT_STATUS');
 check(input.plan.includes('qualified_human_session') || input.plan.includes('qualified-human session'),'HUMAN_DENOMINATOR');
 check(input.plan.includes('7-day') && input.plan.includes('30-day') &&
 input.plan.includes('NOT_COMPUTABLE'),'COHORT_TRUTH');
 check(input.plan.includes('affiliate_outbound_click') &&
 input.plan.includes('merchant-confirmed paid order'),'EVENT_DISTINCTION');
 check(input.plan.includes('R268') && input.plan.includes('R273') &&
 input.plan.includes('PR #172'),'CANONICAL_PROTECTION');
 return errors;
}
function mutateAndCheck(original) {
 const clone=o=>JSON.parse(JSON.stringify(o));
 const changes=[
 ['clear approval gate',v=>{let m=JSON.parse(v.matrix);m.commercial_gates[0].status='CLEARED';v.matrix=JSON.stringify(m)}],
 ['remove one gate',v=>{let m=JSON.parse(v.matrix);m.commercial_gates.pop();v.matrix=JSON.stringify(m)}],
 ['duplicate gate',v=>{let m=JSON.parse(v.matrix);m.commercial_gates[0].id=m.commercial_gates[1].id;v.matrix=JSON.stringify(m)}],
 ['inject earning URL',v=>{let m=JSON.parse(v.matrix);m.products[0].account_issued_affiliate_link='https://example.com/affiliate';v.matrix=JSON.stringify(m)}],
 ['activate eligible offer',v=>{let m=JSON.parse(v.matrix);m.products[0].eligible_for_live_earning_cta=true;v.matrix=JSON.stringify(m)}],
 ['fabricate checkout total',v=>{let m=JSON.parse(v.matrix);m.products[0].checkout_total=87.99;v.matrix=JSON.stringify(m)}],
 ['fabricate owned SKU',v=>{let m=JSON.parse(v.matrix);m.products[3].sku='product-001';v.matrix=JSON.stringify(m)}],
 ['fabricate publisher acceptance',v=>{let m=JSON.parse(v.matrix);m.claims.find(x=>x.id==='C19').status='APPROVED';v.matrix=JSON.stringify(m)}],
 ['fabricate net revenue',v=>{let m=JSON.parse(v.matrix);m.measurement.kpi_status='ZERO';v.matrix=JSON.stringify(m)}],
 ['leak person info',v=>{let m=JSON.parse(v.matrix);m.measurement.no_personal_data=false;v.matrix=JSON.stringify(m)}],
 ['fake creator id',v=>{let m=JSON.parse(v.matrix);m.creator_topic_fit[0].media_id='FAKE123';v.matrix=JSON.stringify(m)}],
 ['invent article URL',v=>{let m=JSON.parse(v.matrix);m.creator_topic_fit[2].public_article='https://finalvestige.com/mind/article/';v.matrix=JSON.stringify(m)}],
 ['erase seller claim warning',v=>{let m=JSON.parse(v.matrix);m.claims.find(x=>x.id==='C12').status='clinically_proven';v.matrix=JSON.stringify(m)}],
 ['remove cited source',v=>{let m=JSON.parse(v.matrix);m.sources=m.sources.filter(s=>s.id!=='S08');v.matrix=JSON.stringify(m)}],
 ['enable CTA',v=>{v.hub=v.hub.replace(' type="button" disabled',' type="button"')}],
 ['remove disclosure',v=>{v.hub=v.hub.replace('If a future approved purchase link','This is a curated product link')}],
 ['add merchant href',v=>{v.hub=v.hub.replace('</main><footer>', '<a href="https://zen12.com/hnp">Buy</a></main><footer>')}],
 ['add script',v=>{v.hub=v.hub.replace('</body>','<script>location.href="https://seller.example"</script></body>')}],
 ['add signup form',v=>{v.hub=v.hub.replace('</body>','<form><input type=email></form></body>')}],
 ['external background',v=>{v.hub=v.hub.replace(':root{color-scheme:dark}',':root{color-scheme:dark;background:url(https://tracking.example/pixel)}')}],
 ['svg external use',v=>{v.hub=v.hub.replace('</body>','<svg><use href="https://tracking.example/svg#x"/></svg></body>')}],
 ['remove a11y labels',v=>{v.hub=v.hub.replace('aria-describedby="commercial-disclosure commercial-hold"','')}],
 ['remove article replication',v=>{v.article=v.article.replaceAll('2025','1900')}],
 ['alter A/B truth',v=>{v.plan=v.plan.replace('**B is not a playable video','**B is a playable video')}],
 ['fake A/B status',v=>{v.plan=v.plan.replace('A/B is NOT LIVE','A/B is LIVE')}],
 ['mislabel earnings',v=>{v.plan=v.plan.replace('NOT_COMPUTABLE','0.00')}],
 ['alter authorizing policy',v=>{let m=JSON.parse(v.matrix);m.release_controls.merge_approved=true;v.matrix=JSON.stringify(m)}]
 ];
 return changes.map(([name,change])=>{const v=clone(original);change(v);return {name,rejected:audit(v).length>0,errors:audit(v)}})
}
if (require.main===module) {
 const data=filesFromDisk();const errs=audit(data);
 const mutations=mutateAndCheck(data);
 const escaped=mutations.filter(m=>!m.rejected);
 console.log(JSON.stringify({baseline:errs.length===0?'PASS':'FAIL',errors:errs,
 adversarial_total:mutations.length,adversarial_rejected:mutations.length-escaped.length,
 escaped},null,2));
 if(errs.length||escaped.length)process.exitCode=1;
}
module.exports={audit,mutateAndCheck,filesFromDisk};
