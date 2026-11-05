#!/usr/bin/env node
'use strict';
/**
 * Apollo R129 — offline, fail-closed proposal gate for one educator funnel.
 * Never activates checkout, publishes, records visits, or confirms merchant orders.
 * A completed manifest can reach HUMAN_REVIEW_REQUIRED, not LIVE/VERIFIED.
 * Usage: node r129_educator_offer_gate.cjs --manifest r129_offer_manifest.json \
 *        [--html landing-preview.html] [--output /tmp/apollo-r129.json]
 */
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const SHA = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const EXPECTED_SCHEMA = 'fv.apollo.educator-offer.v1';
const required = Object.freeze([
  ['merchant.seller_account_verified', 'MERCHANT_ACCOUNT_NOT_VERIFIED'],
  ['merchant.existing_sku_verified', 'EXISTING_SELLABLE_SKU_NOT_VERIFIED'],
  ['merchant.checkout_test_passed', 'CHECKOUT_UNVERIFIED'],
  ['merchant.delivery_test_passed', 'FULFILLMENT_UNVERIFIED'],
  ['merchant.refund_terms_reviewed', 'REFUND_TERMS_UNVERIFIED'],
  ['rights.original_instructional_content_reviewed', 'ORIGINAL_CONTENT_RIGHTS_UNVERIFIED'],
  ['rights.third_party_assets_cleared_or_excluded', 'THIRD_PARTY_RIGHTS_UNVERIFIED'],
  ['education.teacher_preview_approved', 'TEACHER_PREVIEW_UNREVIEWED'],
  ['education.accessibility_reviewed', 'PAID_PRODUCT_ACCESSIBILITY_UNREVIEWED'],
  ['measurement.real_campaign_asset_id_verified', 'GROK_ASSET_ID_UNVERIFIED'],
  ['measurement.session_to_order_attribution_verified', 'ORDER_ATTRIBUTION_UNVERIFIED'],
  ['governance.founder_commercial_terms_approved', 'COMMERCIAL_TERMS_NOT_APPROVED'],
  ['governance.founder_production_release_approved', 'PRODUCTION_RELEASE_NOT_APPROVED']
]);
function valueAt(obj, key){return key.split('.').reduce((a, k)=>a && Object.hasOwn(a,k)?a[k]:undefined,obj);}
function approvedEvidence(value){
  return !!(value && value.verified===true && typeof value.evidence_ref==='string' &&
    value.evidence_ref.trim().length>=8 && typeof value.reviewed_by==='string' &&
    value.reviewed_by.trim().length>=3 && /^\d{4}-\d{2}-\d{2}$/.test(value.reviewed_on||''));
}
function auditLanding(html){
  const errors=[];
  const primary=[...html.matchAll(/<a\b[^>]*\bdata-fv-primary-cta\b[^>]*>/g)];
  if(primary.length!==1 || !/href="#classroom-preview"/.test(primary[0]?.[0]||''))
    errors.push('FREE_CLASSROOM_ACTION_MISSING_OR_DUPLICATED');
  if(!/<section\b[^>]*id="classroom-preview"[^>]*>/.test(html) ||
    !/<article\b[^>]*data-fv-student-print/.test(html))
    errors.push('NO_JS_CLASSROOM_EXERCISE_MISSING');
  if(/<form\b/i.test(html)) errors.push('UNAPPROVED_LEAD_CAPTURE_FORM');
  if(/<a\b[^>]*href="https?:\/\/[^"]*(?:payhip\.com|gumroad\.com|checkout|buy-now)[^"]*"/i.test(html))
    errors.push('UNVERIFIED_COMMERCE_LINK_PRESENT');
  if(/<img\b|<picture\b|<iframe\b/i.test(html))
    errors.push('UNREVIEWED_MEDIA_EMBED');
  if(!/Apollo 204 Review Board/.test(html) || !/0\/6/.test(html))
    errors.push('PRIMARY_SOURCE_OR_REUSE_WARNING_MISSING');
  return errors;
}
function evaluate(manifest, html){
  const blockers=[];
  if(manifest?.schema!==EXPECTED_SCHEMA) blockers.push('MANIFEST_SCHEMA_MISMATCH');
  if(manifest?.offer_type!=='original_educator_casefile') blockers.push('OFFER_NOT_EDUCATOR_CASEFILE');
  if(manifest?.target_audience!=='secondary_history_educators') blockers.push('AUDIENCE_MISMATCH');
  const externalUrl=manifest?.merchant?.listing_url;
  if(externalUrl!=null){
    try { const u=new URL(externalUrl);
      if(u.protocol!=='https:'||u.hostname!=='payhip.com'||!/^\/b\/[^/]+\/?$/.test(u.pathname)||u.search||u.hash)
        blockers.push('LISTING_URL_NOT_DIRECT_PAYHIP_PRODUCT');
    } catch{ blockers.push('LISTING_URL_INVALID'); }
  }else blockers.push('PRODUCT_LISTING_URL_UNAVAILABLE');
  for(const [key,code] of required){if(!approvedEvidence(valueAt(manifest,key)))blockers.push(code);}
  const page_errors=typeof html==='string'?auditLanding(html):['ACTUAL_LANDING_NOT_INSPECTED'];
  const readiness=blockers.length===0&&page_errors.length===0?'HUMAN_REVIEW_REQUIRED':'STAGING_HOLD';
  return {schema:'fv.apollo.offer-readiness-report.v1',readiness,
    proposed_pathway:'Grok Apollo long-form → Apollo evidence landing → free student worksheet → optional verified paid teacher casefile',
    primary_action:'Free classroom evidence exercise; no signup',
    permitted_commerce_cta:'NONE_UNTIL_SEPARATE_RELEASE_AUTHORIZATION',
    verified_sku_in_this_report:false,merchant_settled_orders:'UNOBSERVABLE',
    source_code_sha256:typeof html==='string'?SHA(Buffer.from(html,'utf8')):null,
    blockers,page_errors,rights_status:'ITEM_SPECIFIC_COMMERCIAL_REVIEW_REQUIRED',
    actions:'Do not create a purchase link, lead form, paid-product claim or analytics event from this manifest.'};
}
function cohort(input){
  const unknown={status:'NOT_COMPUTABLE',net_revenue_per_1000_minor:null,
    paid_conversion_rate:null,realized_net_minor:null,reason:'MISSING_VERIFIED_AGGREGATE_AND_JOIN'};
  if(!input || !['7d','30d'].includes(input.window) ||
      input.qualified_human_sessions_verified!==true ||
      input.merchant_orders_reconciled!==true || input.asset_to_order_join_verified!==true)
    return unknown;
  const fields=['qualified_human_sessions','paid_orders','gross_minor','refunds_minor','fees_minor'];
  if(fields.some(k=>!Number.isSafeInteger(input[k]) || input[k]<0))return unknown;
  if(input.qualified_human_sessions===0)return {...unknown,reason:'ZERO_VERIFIED_QUALIFIED_SESSIONS'};
  if(input.refunds_minor>input.gross_minor)return {...unknown,reason:'REFUNDS_EXCEED_GROSS_REQUIRES_RECONCILIATION'};
  const net=input.gross_minor-input.refunds_minor-input.fees_minor;
  return {status:'AGGREGATE_COMPUTABLE_NOT_CAUSAL_PROOF',window:input.window,
    qualified_human_sessions:input.qualified_human_sessions,
    verified_paid_orders:input.paid_orders,
    realized_net_minor:net,
    net_revenue_per_1000_minor:Math.round(100000*net/input.qualified_human_sessions)/100,
    paid_conversion_rate:input.paid_orders/input.qualified_human_sessions,
    small_sample_warning:input.qualified_human_sessions<100||input.paid_orders<30,
    attribution_note:'Aggregate joins must be independently reconciled; do not infer sales from clicks.'};
}
function main(args){
  let manifestFile=null,htmlFile=path.join(__dirname,'landing-preview.html'),output=null;
  for(let i=0;i<args.length;i++){
    const a=args[i];
    if(a==='--manifest')manifestFile=args[++i];
    else if(a==='--html')htmlFile=args[++i];
    else if(a==='--output')output=args[++i];
    else throw new Error('Unknown option: '+a);
  }
  if(!manifestFile)throw new Error('--manifest required');
  const manifest=JSON.parse(fs.readFileSync(manifestFile,'utf8'));
  const html=fs.readFileSync(htmlFile,'utf8');
  const result=evaluate(manifest,html);
  const json=JSON.stringify(result,null,2)+'\n';
  if(output)fs.writeFileSync(output,json,'utf8');else process.stdout.write(json);
  process.exitCode=2; // Audit output is never a machine authorization for deployment.
}
module.exports={auditLanding,evaluate,cohort,approvedEvidence,required};
if(require.main===module){try{main(process.argv.slice(2));}catch(err){
  process.stderr.write('APOLLO_R129_GATE_BLOCKED: '+err.message+'\n');process.exitCode=2;}}
