'use strict';
/** Source-only layout reservation census. Never infer real CLS, LCP or a broken image.
 * Read-only, pinned to 61-post/355-image audit on Media Recovery #1703.
 * Does not change Site QA #154 browser collection, fetch images or modify WP.
 */
const fs=require('node:fs');
const crypto=require('node:crypto');
const SOURCE_GIT_BLOB='a9706c72ad6f17a68113aa87fc063f70d0ca0c34';
const SOURCE_SCHEMA='fv-media-complete-historical-61-355-live-src-alt-20261112-v1';
const P0=Object.freeze(['285:5','285:2','287:5','418:1','418:2','407:1']);
const hold=reason=>({status:'HOLD',reason,claimed_browser_broken_images:null,measured_cls:null,measured_wire_reduction_percent:null,production_change_allowed:false});
const gitBlob=data=>crypto.createHash('sha1').update('blob '+data.byteLength+'\0').update(data).digest('hex');
function reportHtmlImageGeometry(input,{testOnlyAllowUnpinned=false}={}) {
 try {
  if(!Buffer.isBuffer(input)||input.length>4*1024*1024)return hold('RAW_FROZEN_AUDIT_BUFFER_REQUIRED');
  const sha=gitBlob(input);
  if(!testOnlyAllowUnpinned&&sha!==SOURCE_GIT_BLOB)return hold('FROZEN_AUDIT_GIT_BLOB_MISMATCH');
  const audit=JSON.parse(input.toString('utf8'));
  if(!audit||audit.schema!==SOURCE_SCHEMA||!Array.isArray(audit.rows))return hold('AUDIT_SCHEMA_INVALID');
  const groups=new Map(),p0=new Map(),slots=new Set();
  const totals={inline_image_slots:0,offsite_slots:0,missing_both_html_dimensions:0,offsite_missing_both_dimensions:0,first_party_missing_both_dimensions:0,with_both_dimensions:0,partial_dimensions:0,html_srcset_present:0};
  for(const r of audit.rows){
   if(!r||!Number.isSafeInteger(r.post_id)||r.post_id<=0||
     r.slot?.split(':')[0]!==String(r.post_id)||!/^\d+:\d+$/.test(r.slot)||slots.has(r.slot)||
     typeof r.source_url!=='string'||!r.source_url.startsWith('https://')||
     typeof r.post_url!=='string'||!r.post_url.startsWith('https://finalvestige.com/')||
     typeof r.alt!=='string'||r.source_equal!==true||r.alt_equal!==true||
     typeof r.offsite_historical_registry!=='boolean'||typeof r.html_srcset_present!=='boolean')
    return hold('INVALID_FROZEN_IMAGE_ROW_OR_IDENTITY');
   slots.add(r.slot);
   const w=r.html_width_px,h=r.html_height_px;
   const oneMissing=(w==null)!==(h==null);
   if(oneMissing||(w!=null&&(!Number.isSafeInteger(w)||w<=0||!Number.isSafeInteger(h)||h<=0)))
    return hold('PARTIAL_OR_INVALID_STORED_HTML_GEOMETRY');
   const missing=w==null;
   let g=groups.get(r.post_id);
   if(!g){g={post_id:r.post_id,post_url:r.post_url,inline_images:0,offsite_images:0,missing_both_html_dimensions:0,offsite_missing_html_dimensions:0,first_party_missing_html_dimensions:0,html_srcset_images:0,missing_slots:[]};groups.set(r.post_id,g)}
   if(g.post_url!==r.post_url)return hold('POST_URL_CONFLICT');
   g.inline_images++;totals.inline_image_slots++;
   if(r.offsite_historical_registry){g.offsite_images++;totals.offsite_slots++}
   if(r.html_srcset_present){g.html_srcset_images++;totals.html_srcset_present++}
   if(missing){
    totals.missing_both_html_dimensions++;g.missing_both_html_dimensions++;g.missing_slots.push(r.slot);
    if(r.offsite_historical_registry){totals.offsite_missing_both_dimensions++;g.offsite_missing_html_dimensions++}
    else {totals.first_party_missing_both_dimensions++;g.first_party_missing_html_dimensions++}
   } else totals.with_both_dimensions++;
   if(P0.includes(r.slot))p0.set(r.slot,{slot:r.slot,post_id:r.post_id,post_url:r.post_url,
      exact_published_original_url:r.source_url,alt:r.alt,html_width_px:w??null,
      html_height_px:h??null,html_srcset_present:r.html_srcset_present,
      guest_response_status:null,guest_decode_status:null,measured_layout_shift:null,
      explicit_html_dimension_reservation:!missing,
      css_aspect_ratio_or_container_reservation_verified:false,
      decision:'SOURCE_EXPOSURE_ONLY_VERIFY_IN_SITE_QA_154_BROWSER'});
  }
  if(totals.missing_both_html_dimensions+totals.with_both_dimensions!==totals.inline_image_slots)
   return hold('IMPOSSIBLE_GEOMETRY_TOTALS');
  if(!testOnlyAllowUnpinned){
   if(groups.size!==61||totals.inline_image_slots!==355||totals.offsite_slots!==288||
      totals.missing_both_html_dimensions!==305||totals.with_both_dimensions!==50||
      totals.html_srcset_present!==0||p0.size!==6||
      audit.counts?.frozen_posts!==61||audit.counts?.verified_image_positions!==355||
      audit.counts?.missing_both_html_dimensions!==305||
      audit.counts?.historical_offsite_positions!==288)
      return hold('FROZEN_COUNTS_OR_P0_COVERAGE_CHANGED');
  }
  return {
   schema:'fv-media-61post-geometry-reservation-exposure-20261112-v1',
   status:'VERIFIED_SOURCE_ONLY_LAYOUT_GEOMETRY_EXPOSURE',
   audit_git_blob_sha:sha,
   source_scope:'61 frozen historical posts / 355 stored inline images; NOT current 66-post cohort',
   inference_limit:'Missing HTML width and height is an exposure, not proof of a layout shift. CSS aspect-ratio, containers and browser heuristics may reserve space. No guest image failure or CLS has been measured.',
   counts:{posts:groups.size,...totals,p0_source_slots_without_both_html_dimensions:P0.filter(x=>p0.get(x)&&p0.get(x).html_width_px===null).length},
   p0_qa_sequence:P0.filter(s=>p0.has(s)).map(s=>p0.get(s)),
   top_source_exposures:[...groups.values()].sort((a,b)=>b.missing_both_html_dimensions-a.missing_both_html_dimensions||b.offsite_missing_html_dimensions-a.offsite_missing_html_dimensions||a.post_id-b.post_id).slice(0,12),
   per_post:[...groups.values()].sort((a,b)=>a.post_id-b.post_id),
   browser_validation_request:'Site QA #154 existing cold guest collector: capture source/currentSrc and actual response+decode, then BEFORE-image layout reservation (CSS aspect-ratio, intrinsic ratio, box height), AFTER box dimensions and PerformanceObserver layout-shift entries excluding recent user input; compare same viewport/DPR with screenshots. Do not assume no HTML width/height caused CLS.',
   production_change_allowed:false,third_party_download_or_mirror_allowed:false,
   wordpress_post_rewrite_allowed:false,guest_broken_images_confirmed:null,
   measured_cls:null,measured_image_wire_reduction_percent:null,
   output_width_constraint:'At most 960px AND never upscale; require rights clearance, decoded native pixels, image identity and target DPR before staging.'
  };
 }catch(e){return hold('AUDIT_PARSE_OR_VALIDATION_ERROR:'+e.message)}
}
if(require.main===module){
 const name=process.argv[2];if(!name){console.error('usage: node audit_html_image_geometry_20261112.cjs FROZEN_LEDGER.json');process.exitCode=2}
 else {const out=reportHtmlImageGeometry(fs.readFileSync(name));process.stdout.write(JSON.stringify(out,null,2)+'\n');if(out.status==='HOLD')process.exitCode=2;}
}
module.exports={reportHtmlImageGeometry,SOURCE_GIT_BLOB,P0};
