'use strict';
/**
 * R136: independent editorial-to-product evidence gate.
 * Pure, offline, deterministic. This function never records a visitor, queries
 * a merchant, approves commercial reuse or authorizes publishing.
 * It is deliberately distinct from production analytics (#820) and Grok TASK-008.
 */
const {inspectCreatorUrl,inspectMerchantUrl}=require('./r137_destination_integrity.cjs');
const {inspectBoundCampaign,STATUS:BOUND_CANDIDATE}=require('./r138_creator_landing_custody.cjs');
const SCHEMA='fv.apollo.r136.conversion-evidence.v1';
const REQUIRED_SOURCES=Object.freeze([
 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/',
 'https://www.nasa.gov/image-detail/apollo-1-crew-honored/',
 'https://www.nasa.gov/image-detail/amf-s67-15717/',
 'https://www.nasa.gov/image-detail/amf-s66-58038/',
 'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/',
 'https://www.nasa.gov/image-detail/amf-s67-21294/',
 'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/'
]);
const FREE_FRAGMENT='#classroom-preview';
const ENTITY='Apollo 1: Fourteen Seconds, More Than One Failure';
function isPlainObject(v){return v!==null&&typeof v==='object'&&!Array.isArray(v);}
function cleanCampaign(c,independentlyReviewedLandingUrl=null){
 const errors=[];
 if(c===null||c===undefined)return {status:'NOT_SUBMITTED',errors:[],utm:null};
 if(!isPlainObject(c))return {status:'INVALID',errors:['CAMPAIGN_NOT_OBJECT'],utm:null};
 // Only confirmed Grok assets can be part of a proposed campaign; placeholders
 // are forbidden. This is a syntax check, never publication verification.
 if(c.source!=='youtube')errors.push('EXPECTED_GROK_YOUTUBE_LONG_FORM');
 if(!/^[a-z0-9][a-z0-9_-]{5,79}$/.test(c.asset_id||'') ||
    /placeholder|example|sample|pending|unknown|tbd|test/i.test(c.asset_id||''))
    errors.push('ASSET_ID_NOT_CONCRETE');
 if(c.owner!=='Grok'||c.publication_verified!==true||
    inspectCreatorUrl(c.public_url).status!=='SYNTAX_ONLY_NOT_PUBLICATION_PROOF')
    errors.push('PUBLICATION_NOT_INDEPENDENTLY_ATTESTED');
 if(c.destination_reviewed!==true||c.destination_fragment!==FREE_FRAGMENT)
    errors.push('DESTINATION_NOT_REVIEWED');
 // R138: claimed approval and a plausible video URL do not bind a Grok asset
 // to the actual reviewed WordPress route. This is still only an offline preflight.
 if(inspectBoundCampaign(c,independentlyReviewedLandingUrl).status!==BOUND_CANDIDATE)
    errors.push('GROK_VIDEO_TO_APOLLO_LANDING_NOT_BOUND');
 return {status:errors.length?'INVALID':'CANDIDATE_REQUIRES_INDEPENDENT_PLATFORM_CHECK',
  errors,utm:errors.length?null:{
   utm_source:'youtube',utm_medium:'organic_social',
   utm_campaign:'history_pilot_2026_11',utm_content:c.asset_id
  }};
}
function cleanOffer(o){
 const errors=[];
 if(o===null||o===undefined)return {status:'NOT_SUBMITTED',errors:[],candidate:null};
 if(!isPlainObject(o))return {status:'INVALID',errors:['OFFER_NOT_OBJECT'],candidate:null};
 if(!/^[a-z0-9][a-z0-9_-]{2,79}$/.test(o.sku||''))errors.push('SKU_MISSING');
 if(o.audience!=='educators_grades_6_9')errors.push('AUDIENCE_MISMATCH');
 if(o.topic!=='apollo1_source_analysis')errors.push('UNRELATED_OFFER');
 if(o.rights_review!=='SIGNED_OFF_BY_REVIEWER' ||
    !/^[0-9a-f]{64}$/.test(o.original_materials_sha256||''))
    errors.push('ORIGINAL_CONTENT_RIGHTS_UNVERIFIED');
 if(o.fulfillment_receipt!=='MERCHANT_TEST_DELIVERY_VERIFIED')
    errors.push('DELIVERY_NOT_TESTED');
 if(o.refund_policy_reviewed!==true)errors.push('REFUNDS_NOT_REVIEWED');
 if(o.founder_approval!==true)errors.push('FOUNDER_NOT_APPROVED');
 if(o.nasa_media_embedded!==false)errors.push('NASA_MEDIA_REUSE_SCOPE_UNCLEARED');
 // R137: exact Payhip product origin only. Still not proof of an actual listing.
 const checked=inspectMerchantUrl(o.merchant_url);
 const href=checked.status==='DOCUMENT_ONLY_NOT_MERCHANT_PROOF'?checked.product_url:null;
 if(!href)errors.push('MERCHANT_URL_UNVERIFIED');
 return {status:errors.length?'BLOCKED':'DOCUMENT_ONLY_NOT_MERCHANT_ATTESTATION',
   errors,candidate:errors.length?null:{sku:o.sku,merchant_url:href,topic:o.topic}};
}
function assess({landingHtml,routeAudit,mediaAudit,researchAudit,offer=null,campaign=null,
 browserReceipt=null,merchantReceipts=null,reviewedLandingUrl=null}={}){
 const blockers=[];
 if(typeof landingHtml!=='string'||!landingHtml.includes('data-fv-primary-cta')||
    !landingHtml.includes('href="'+FREE_FRAGMENT+'"')||
    !landingHtml.includes('id="classroom-preview"')||
    !landingHtml.includes('Free source-analysis exercise'))blockers.push('FREE_WORKSHEET_PATH_UNPROVEN');
 if(REQUIRED_SOURCES.some(u=>!landingHtml.includes('href="'+u+'"')))
    blockers.push('TECHNICAL_OR_PHOTO_PROVENANCE_MISSING');
 if(!isPlainObject(routeAudit)||routeAudit.status!=='PASS'||
    routeAudit.primary_cta_count!==1)blockers.push('ROUTE_SOURCE_GATE_NOT_PASS');
 if(!isPlainObject(mediaAudit)||mediaAudit.status!=='PASS_SOURCE_CUSTODY_ONLY'||
    mediaAudit.commercially_cleared_count!==0||mediaAudit.record_count!==6)
    blockers.push('NASA_MEDIA_CUSTODY_NOT_SOURCE_ONLY');
 if(!isPlainObject(researchAudit)||researchAudit.status!=='PASS')
    blockers.push('RESEARCH_DESK_EDITORIAL_GATE_NOT_PASS');
 const campaignCandidate=cleanCampaign(campaign,reviewedLandingUrl),offerCandidate=cleanOffer(offer);
 if(campaignCandidate.status!=='CANDIDATE_REQUIRES_INDEPENDENT_PLATFORM_CHECK')
    blockers.push('NO_VERIFIED_GROK_CAMPAIGN_ROUTE');
 if(offerCandidate.status!=='DOCUMENT_ONLY_NOT_MERCHANT_ATTESTATION')
    blockers.push('NO_VALID_PAID_EDUCATOR_OFFER_DOSSIER');
 // Never infer merchant settlement from values supplied to an offline QA script:
 // use separately reconciled paid-order, refund and fee receipts under issue #820.
 if(!Array.isArray(merchantReceipts)||merchantReceipts.length===0)
    blockers.push('NO_MERCHANT_SETTLEMENT_EVIDENCE');
 else blockers.push('MERCHANT_SETTLEMENT_NOT_INDEPENDENTLY_RECONCILED');
 if(!browserReceipt||browserReceipt.browser_acceptance!=='TESTED_LOCAL_ONLY'||
    (browserReceipt.errors||[]).length!==0)
    blockers.push('REAL_BROWSER_ACCEPTANCE_MISSING');
 else blockers.push('WORDPRESS_INTEGRATION_AND_FOUNDER_RELEASE_UNVERIFIED');
 blockers.push('SIX_PHOTO_SPECIFIC_RIGHTS_REVIEWS_OPEN');
 blockers.push('PRODUCTION_RELEASE_APPROVAL_NOT_GIVEN');
 return {
  schema:SCHEMA,case:ENTITY,scope:'STAGING_SOURCE_REVIEW_ONLY',
  primary_audience:'educators_grades_6_9',
  recommended_next_action:{href:FREE_FRAGMENT,label:'Review the free classroom evidence exercise',
   no_js_required:true,one_primary_cta:true},
  source_role:'NASA Review Board technical authority; photographs visual-only, no embedded media',
  editorial_custody:!blockers.some(x=>['FREE_WORKSHEET_PATH_UNPROVEN',
   'TECHNICAL_OR_PHOTO_PROVENANCE_MISSING','ROUTE_SOURCE_GATE_NOT_PASS',
   'NASA_MEDIA_CUSTODY_NOT_SOURCE_ONLY','RESEARCH_DESK_EDITORIAL_GATE_NOT_PASS'].includes(x))
    ? 'SOURCE_GATE_PASS_ONLY' : 'SOURCE_GATE_FAIL',
  campaign:candidateRedaction(campaignCandidate),
  proposed_offer:candidateRedaction(offerCandidate),
  conversion_hypothesis:'A free, primary-source classroom exercise may qualify educator demand for an original teacher-ready casefile; purchase intent and profit are unproven.',
  measurement:{qualified_human_sessions:'UNOBSERVABLE',cta_clicks:'UNOBSERVABLE',
    confirmed_leads:'UNOBSERVABLE',merchant_confirmed_orders:'UNOBSERVABLE',
    refunds_fees:'UNOBSERVABLE',net_revenue:'UNOBSERVABLE',
    net_revenue_per_1000_qualified_sessions:'NOT_COMPUTABLE',
    cohorts_7d_30d:'NOT_MEASURED'},
  qa:{browser:browserReceipt&&browserReceipt.browser_acceptance==='TESTED_LOCAL_ONLY'
    ? 'LOCAL_TEST_ONLY_NOT_LIVE':'NOT_ESTABLISHED',axe:'NOT_INDEPENDENTLY_VERIFIED',
    lcp_cls_p75:'NOT_MEASURED',wordpress:'NOT_TESTED'},
  blockers:[...new Set(blockers)],
  release:'STAGING_HOLD',live:false,approved_to_publish:false,
  paid_cta_insertion_authorized:false,
  note:'Offline candidate fields and source tests are not merchant, Grok, rights, founder, or paid-order attestations.'
 };
}
function candidateRedaction(result){
 return {status:result.status,errors:result.errors,candidate:result.candidate||null,
   utm:result.utm||null,independently_verified:false};
}
module.exports={assess,cleanCampaign,cleanOffer,REQUIRED_SOURCES,SCHEMA};
