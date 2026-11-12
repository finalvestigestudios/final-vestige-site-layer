'use strict';
/* Frozen 61-post integrity audit: strictly offline, no browser requests or WordPress writes. */
const fs=require('node:fs'),path=require('node:path');
const INPUTS=[
'live_part01_8posts_52_images_20261112.json',
'live_part02_8posts_59_images_20261112.json',
'live_part03_8posts_49_images_20261112.json',
'live_part04_8posts_56_images_20261112.json',
'live_part05_8posts_54_commons_20261112.json',
'live_part06_8posts_49_images_20261112.json',
'live_parts07_08_13posts_36_images_20261112.json'
];
function norm(s){return String(s??'').replace(/&amp;/g,'&').replace(/&quot;/g,'"').replace(/&#(?:0*39|x0*27);/gi,"'");}
function validate(a,registry,sources){
  const errors=[],fail=s=>errors.push(s);
  if(a?.schema!=='fv-media-complete-historical-61-355-live-src-alt-20261112-v1')return {ok:false,errors:['schema_changed']};
  if(!registry||!Array.isArray(registry.rows)||!Array.isArray(sources)||sources.length!==7)
    return {ok:false,errors:['source_files_missing']};
  const registryMap=new Map(registry.rows.map(x=>[x.slot,x]));
  const rawMap=new Map(),posts=new Set();
  sources.forEach((obj,i)=>{
    const records=obj?.rows||obj?.records||[];
    if(!Array.isArray(records)||!Array.isArray(obj.posts))fail('malformed_segment:'+i);
    for(const p of (obj.posts||[]))posts.add(p.post_id||p.id);
    for(const x of records){
      if(rawMap.has(x.slot))fail('duplicate_input_slot:'+x.slot);
      rawMap.set(x.slot,{source:x,segment:INPUTS[i]});
    }
  });
  if(rawMap.size!==355||posts.size!==61)fail('historical_input_cohort_incomplete');
  const stats={frozen_posts:posts.size,verified_image_positions:0,source_equal:0,alt_equal:0,historical_offsite_positions:0,historical_first_party_positions:0,missing_both_html_dimensions:0,both_html_dimensions:0,partial_html_dimension_pairs:0,literal_html_srcset:0,archive_candidates_mapped:0,conditional_960px_leads:0,real_guest_origin_http_statuses_measured:0,confirmed_broken_guest_images:null,percent_network_bytes_saved:null,production_repairs:0};
  const seen=new Set();
  if(!Array.isArray(a.rows))fail('rows_missing');
  for(const x of (a.rows||[])){
    stats.verified_image_positions++;
    if(seen.has(x.slot))fail('duplicate_rollup_slot:'+x.slot);
    seen.add(x.slot);
    if(!posts.has(x.post_id)||!x.slot.startsWith(String(x.post_id)+':'))fail('foreign_post_slot:'+x.slot);
    const ref=rawMap.get(x.slot);
    if(!ref){fail('unrecognized_slot:'+x.slot);continue;}
    const raw=ref.source;
    if(x.source_segment!=='qa/media-recovery/'+ref.segment)fail('segment_cross_reference_changed:'+x.slot);
    const published=norm(raw.live_src??raw.live_source_url??raw.source_url);
    const frozen=norm(raw.frozen_src??raw.frozen_source_url??raw.source_url);
    if(published!==frozen||published!==x.source_url||x.source_equal!==true)fail('published_original_drift:'+x.slot);
    else stats.source_equal++;
    const alt=norm(raw.live_alt),oldAlt=norm(raw.frozen_alt??raw.baseline_alt??raw.original_alt??raw.live_alt);
    if(alt!==oldAlt||x.alt!==alt||x.alt_equal!==true||raw.alt_equal===false)fail('alt_integrity_drift:'+x.slot);
    else stats.alt_equal++;
    const ow=raw.html_width_px??raw.html_width??null,oh=raw.html_height_px??raw.html_height??null;
    if(x.html_width_px!==ow||x.html_height_px!==oh)fail('geometry_source_drift:'+x.slot);
    const w=x.html_width_px,h=x.html_height_px;
    if(w===null&&h===null)stats.missing_both_html_dimensions++;
    else if(Number.isSafeInteger(w)&&w>0&&Number.isSafeInteger(h)&&h>0)stats.both_html_dimensions++;
    else{stats.partial_html_dimension_pairs++;fail('incomplete_or_invalid_dimensions:'+x.slot);}
    if(x.html_srcset_present!==false){stats.literal_html_srcset++;fail('unverified_srcset:'+x.slot);}
    const original=registryMap.get(x.slot);
    if(original){
      stats.historical_offsite_positions++;
      if(original.stored_url!==x.source_url||x.offsite_historical_registry!==true)fail('external_registry_original_mismatch:'+x.slot);
      if(!Array.isArray(x.candidates)||x.candidates.length!==(original.candidate_sources||[]).length)fail('archival_candidate_mapping_changed:'+x.slot);
    }else{
      stats.historical_first_party_positions++;
      if(x.offsite_historical_registry!==false||!/^https:\/\/(finalvestige\.com|i[0-9]\.wp\.com\/finalvestige\.com)\//.test(x.source_url))fail('unmapped_third_party:'+x.slot);
    }
    if(x.candidates?.length)stats.archive_candidates_mapped++;
    if(x.candidates?.some(c=>Array.isArray(c.conditional_960px)))stats.conditional_960px_leads++;
    for(const c of x.candidates||[]){
      if(c.item_rights_cleared!==false||c.exact_image_match_verified!==false)fail('candidate_rights_overclaim:'+x.slot);
      if(c.conditional_960px!==null){
        const d=c.conditional_960px;
        if(!Array.isArray(d)||d.length!==2||!d.every(n=>Number.isSafeInteger(n)&&n>0)||d[0]>960)fail('unsafe_960_width:'+x.slot);
      }
    }
    if(x.guest_http_status!==null||x.guest_natural_pixels!==null||x.guest_current_src!==null||x.guest_transferred_bytes!==null||x.guest_failure_confirmed!==null||x.measured_cls!==null)fail('fabricated_guest_telemetry:'+x.slot);
    if(x.rights_cleared!==false||x.exact_image_match_verified!==false||x.rehost_authorized!==false||x.wordpress_write_authorized!==false)fail('unauthorized_release:'+x.slot);
  }
  if(stats.verified_image_positions!==355||seen.size!==355||stats.historical_offsite_positions!==288||stats.historical_first_party_positions!==67||stats.missing_both_html_dimensions!==305||stats.both_html_dimensions!==50)fail('historical_census_invariant');
  if(!Array.isArray(a.input_audits)||a.input_audits.length!==7||a.input_audits.some((x,i)=>x.path!=='qa/media-recovery/'+INPUTS[i]))fail('segment_manifest_invariant');
  for(const [k,v] of Object.entries(stats))if(a.counts?.[k]!==v)fail('aggregate_count_mismatch:'+k);
  if(a.policy?.visitor_browser_confirmed_42_broken!==false||a.policy?.claimed_76_percent_network_byte_reduction_verified!==false||a.policy?.site_qa_original_collector_pr!==154||a.policy?.production_writes!==false||a.policy?.automatic_rehosting!==false||a.policy?.external_media_downloads!==false||a.policy?.homepage_design_changes!==false)fail('no_release_policy_changed');
  return {ok:errors.length===0,errors,counts:stats};
}
if(require.main===module){
 const rollup=JSON.parse(fs.readFileSync(process.argv[2]||path.join(__dirname,'live_61post_355image_integrity_consolidated_20261112.json')));
 const registry=JSON.parse(fs.readFileSync(path.join(__dirname,'coverage_288_exact_pr1703_20261110.json')));
 const sources=INPUTS.map(s=>JSON.parse(fs.readFileSync(path.join(__dirname,s))));
 const result=validate(rollup,registry,sources);console.log(JSON.stringify(result,null,2));if(!result.ok)process.exitCode=1;
}
module.exports={validate,INPUTS};
