'use strict';
/** Camp Century 290: read-only historical-image provenance validator.
 * No HTTP, file writes, image downloads, WordPress edits, or publication controls.
 */
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const EXPECTED_PART_SHA='49183f66f880f7c4dfd363acca906876877f2e5e';
const OBS=['RETRIEVER_IMAGE_DISPLAYED','RETRIEVER_IMAGE_DISPLAYED','RETRIEVER_IMAGE_DISPLAYED','RETRIEVER_TIMEOUT_NO_ORIGIN_STATUS','RETRIEVER_IMAGE_DISPLAYED','RETRIEVER_DISABLED_NO_ORIGIN_STATUS'];
const isHttps=x=>typeof x==='string'&&/^https:\/\/[^\s/]+\//.test(x);
const hash=b=>crypto.createHash('sha1').update('blob '+b.length+'\\0').update(b).digest('hex');
function load(root=__dirname){
 const raw=fs.readFileSync(path.join(root,'parts/03.json'));
 const ledger=JSON.parse(fs.readFileSync(path.join(root,'camp_century_290_primary_visual_20261102.json'),'utf8'));
 return {ledger,raw,source:JSON.parse(raw)};
}
function validateLedger(ledger,source,raw){
 const errors=[];
 if(!ledger||ledger.schema_version!==1||ledger.as_of!=='2026-11-02')errors.push('wrong_schema');
 if(raw&&hash(raw)!==EXPECTED_PART_SHA)errors.push('source_part_sha_mismatch');
 const original=source?.images?.filter(x=>x.post_id===290)||[];
 const p=source?.posts?.find(x=>x.id===290);
 if(!p||p.url!==ledger?.source_attestation?.permalink||p.modified!==ledger?.source_attestation?.modified||original.length!==6||
    ledger?.source_attestation?.status!=='publish'||ledger.source_attestation.source_part_git_blob_sha!==EXPECTED_PART_SHA||
    ledger.source_attestation.exact_source_and_alt_matches_frozen!==6)errors.push('frozen_post_source_mismatch');
 if(!Array.isArray(ledger?.rows)||ledger.rows.length!==6)return [...new Set([...errors,'six_rows_required'])];
 let displayed=0,timeout=0,disabled=0;
 const seen=new Set();
 for(let i=0;i<6;i++){
  const row=ledger.rows[i],o=original[i];
  if(!o||row?.image_key!==o.key||row.post_id!==290||seen.has(row.image_key)||
     row.exact_published_source_url!==o.source_url||row.exact_published_alt!==o.alt||
     !isHttps(row.exact_published_source_url))errors.push('source_identity:'+i);
  if(row?.image_key)seen.add(row.image_key);
  const obs=row?.independent_retriever;
  if(obs?.method!=='web.open rendered binary or failed independent retriever; NOT logged-out Chrome'||
    obs?.observation!==OBS[i]||obs?.origin_http_status!==null||obs?.visitor_http_status!==null)
    errors.push('fabricated_retriever_status:'+i);
  if(obs?.observation==='RETRIEVER_IMAGE_DISPLAYED')displayed++;
  if(obs?.observation==='RETRIEVER_TIMEOUT_NO_ORIGIN_STATUS')timeout++;
  if(obs?.observation==='RETRIEVER_DISABLED_NO_ORIGIN_STATUS')disabled++;
  const v=row?.actual_visitor_browser;
  if(!v||Object.values(v).some(x=>x!==null))errors.push('unmeasured_browser_fields:'+i);
  const a=row?.authoritative_recovery_candidate,d=row?.dimensions,g=row?.release_gates;
  if(!a||!isHttps(a.url)||a.exact_binary_sha256_verified!==false||
    a.item_specific_rights_review!=='HOLD'||a.wordPress_media_upload_authorized!==false)
    errors.push('rights_or_identity_unverified:'+i);
  if(!d||d.max_width_px!==960||d.never_upscale!==true||d.preserve_full_image_no_crop!==true||
     d.requires_binary_decode_before_derivative!==true)errors.push('dimension_safety:'+i);
  if(d?.catalog_original_px){
   const {width,height}=d.catalog_original_px,actual=d.conditional_derivative_px;
   if(!Number.isSafeInteger(width)||!Number.isSafeInteger(height)||width<1||height<1||
      actual?.width!==Math.min(960,width)||actual?.height!==Math.round(height*Math.min(960,width)/width))
     errors.push('dimension_geometry:'+i);
  }else if(d?.conditional_derivative_px!==null)errors.push('invented_dimensions:'+i);
  if(!g||Object.values(g).some(x=>x!==false))errors.push('premature_publication_gate:'+i);
  if(i!==4&&row.proposed_alt_review!==null)errors.push('unapproved_alt_other:'+i);
 }
 if(displayed!==4||timeout!==1||disabled!==1||ledger?.counts?.displayed_through_independent_retriever!==4||
    ledger.counts.source_timed_out_no_http!==1||ledger.counts.source_disabled_no_http!==1||
    ledger.counts.actual_guest_browser_confirmed_broken!==0||ledger.counts.visitor_browser_verified_any!==0||
    ledger.counts.published_edits!==0||ledger.counts.reported_42_browser_broken_proven!==false||
    ledger.counts.claimed_76_percent_transfer_reduction_measured!==false)
    errors.push('fabricated_summary');
 const target=ledger.rows[2].dimensions;
 if(target?.catalog_original_px?.width!==1573||target?.catalog_original_px?.height!==1132||
    target?.conditional_derivative_px?.width!==960||target?.conditional_derivative_px?.height!==691)
    errors.push('army_trench_cross_section_dimensions');
 const mismatch=ledger.rows[4].proposed_alt_review;
 if(mismatch?.status!=='EDITORIAL_ONLY_NOT_PUBLISHED'||!mismatch.suggested?.includes('thermal drill')||
    !mismatch.reason?.includes('NOT workers')||!ledger.rows[4].exact_published_alt.includes('ice core material'))
    errors.push('thermal_drill_alt_evidence_missing');
 if(ledger.rows[5].authoritative_recovery_candidate.kind!=='published_researchgate_journal_figure_not_verified_identical_to_cc0_dataset'||
    !ledger.rows[5].authoritative_recovery_candidate.rights.includes('separately unverified'))
    errors.push('geus_dataset_license_not_transferrable');
 const ctx=ledger.sitewide_context;
 if(ctx?.published_posts!==61||ctx.stored_inline_refs!==355||ctx.stored_offsite_refs!==288||
    ctx.wordpress_originals_above_1_5_mib!==13||ctx.alleged_broken_verified!==false||
    ctx.claimed_reduction_measured!==false||ctx.production_repairs!==0)
    errors.push('unverified_sitewide_claim');
 return [...new Set(errors)];
}
if(require.main===module){
 try{const {ledger,raw,source}=load(),errors=validateLedger(ledger,source,raw);
 console.log(JSON.stringify({ok:!errors.length,errors,post_id:290,images:ledger.rows.length}));
 if(errors.length)process.exitCode=1;}catch(e){console.error(String(e));process.exitCode=1}
}
module.exports={load,validateLedger,EXPECTED_PART_SHA};
