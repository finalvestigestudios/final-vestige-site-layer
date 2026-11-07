'use strict';
// Pure offline validator: no HTTP, media download, WP writes, or release action.
function inspect(a) {
 const errors=[];const check=(v,msg)=>{if(!v)errors.push(msg)};
 const ids=[39,40,41,42,43,293,382,388,389,405,482,1257,1258],slots=['34:0','35:0','36:0','37:0','38:0','621:0','621:1'];
 const sum=x=>x.reduce((n,v)=>n+v.original_bytes,0),pixelPair=d=>Array.isArray(d)&&d.length===2&&d.every(v=>Number.isInteger(v)&&v>0);
 if(!a||typeof a!=='object')return{ok:false,errors:['audit_required']};
 check(a.schema==='fv-media-oversize-raw-inline-crosswalk-v1','schema');
 check(a.source_ref==='f69a12cd9241ea0f39cfcb74c669bb6f7fb10357','snapshot_ref');
 check(a.cohort?.posts===61&&a.cohort?.inline_images===355&&a.cohort?.offsite_raw_refs===288,'cohort');
 check(a.cohort?.browser_verified_broken_count===null&&a.cohort?.reported_42_broken_images==='UNVERIFIED'&&a.cohort?.claimed_76pct_wire_savings==='UNMEASURED','unsupported_claim');
 check(a.live_browser_bytes_total===null&&a.measured_page_image_weight_reduction_pct===null,'unmeasured_wire');
 check(a.wordpress_writes===0&&a.third_party_downloads===0&&a.files_generated_or_copied===0,'production_hold');
 check(a.oversize_threshold_bytes===1572864,'threshold');
 const source=a.source_blob_shas||{};
 check(Object.keys(source).length===10&&Object.entries(source).every(([f,sha])=>f.startsWith('qa/media-recovery/')&&/^[a-f0-9]{40}$/.test(sha)),'source_provenance');
 if(!Array.isArray(a.rows)||a.rows.length!==13)return{ok:false,errors:[...errors,'13_rows_required']};
 const seen=new Set(),refs=new Set();
 for(const x of a.rows){
  check(Number.isInteger(x.media_id)&&!seen.has(x.media_id),'media_id');seen.add(x.media_id);
  check(typeof x.original_src==='string'&&x.original_src.startsWith('https://finalvestige.com/wp-content/uploads/')&&!/[?#]/.test(x.original_src),'source_url');
  check(Number.isInteger(x.original_bytes)&&x.original_bytes>a.oversize_threshold_bytes,'original_byte_count');
  const d=x.original_pixels,t=x.conditional_preview_pixels;
  check(pixelPair(d)&&pixelPair(t),'dimensions');
  if(pixelPair(d)&&pixelPair(t))check(t[0]===Math.min(960,d[0])&&t[1]===Math.round(d[1]*t[0]/d[0])&&t[0]<=d[0]&&t[1]<=d[1],'no_upscale_geometry');
  check(x.web_browser_http_status===null&&x.web_browser_current_src===null&&x.web_browser_image_encoded_bytes===null&&x.web_browser_decode_ok===null,'no_invented_browser');
  check(x.rights_clearance==='HOLD'&&x.allow_rehosting===false&&x.allow_wordpress_write===false&&x.live_asset_changed===false,'rights_hold');
  check(x.existing_proxy_variant===null||(typeof x.existing_proxy_variant==='string'&&x.existing_proxy_variant.startsWith('https://i0.wp.com/finalvestige.com/wp-content/uploads/')),'proxy_url');
  check(x.proxy_variant_visitor_verified===false,'proxy_unverified');
  check(Array.isArray(x.inline_source_matches)&&x.inline_source_matches.length<=1,'inline_refs');
  if(Array.isArray(x.inline_source_matches)){
   const used=x.inline_source_matches.length>0;
   check(x.inline_source_status===(used?'INLINE_SRC_PRESENT_IN_61_POST_COHORT':'NOT_FOUND_IN_61_POST_INLINE_SRC_COHORT'),'source_status');
   check(x.triage===(used?(x.existing_proxy_variant?'P1_CAPTURE_BROWSER_VARIANT_FIRST':'P1_CAPTURE_BROWSER_ORIGINAL_AND_SRCSET_FIRST'):'INVENTORY_ONLY_NOT_INLINE_PRIORITIZE_VISITOR_EVIDENCE'),'priority');
   for(const m of x.inline_source_matches){
    check(typeof m.slot==='string'&&!refs.has(m.slot)&&/^\d+:\d+$/.test(m.slot),'slot_id');refs.add(m.slot);
    check(typeof m.post_url==='string'&&m.post_url.startsWith('https://finalvestige.com/')&&typeof m.post_title==='string'&&m.post_title.length>0&&typeof m.stored_alt==='string','post_evidence');
   }
  }
 }
 check(ids.every(id=>seen.has(id))&&seen.size===ids.length,'expected_media_set');
 const yes=a.rows.filter(x=>x.inline_source_matches.length),no=a.rows.filter(x=>!x.inline_source_matches.length);
 check(a.oversize_original_count===13&&a.oversize_stored_original_bytes===sum(a.rows)&&sum(a.rows)===43522829,'storage_original_sum');
 check(a.raw_inline_match_originals===yes.length&&yes.length===7&&a.raw_inline_match_original_bytes===sum(yes)&&sum(yes)===23619602,'matched_original_sum');
 check(a.not_in_inline_originals===no.length&&no.length===6&&a.not_in_inline_original_bytes===sum(no)&&sum(no)===19903227,'unmatched_original_sum');
 check(slots.every(s=>refs.has(s))&&refs.size===slots.length&&JSON.stringify((a.exact_inline_slots||[]).slice().sort())===JSON.stringify(slots),'slot_set');
 return{ok:errors.length===0,errors,metrics:{originals:13,raw_inline_matched:yes.length,no_raw_inline_match:no.length,original_storage_bytes:sum(a.rows),raw_inline_original_storage_bytes:sum(yes),unmatched_original_storage_bytes:sum(no),actual_browser_bytes:null,measured_reduction_pct:null}};
}
module.exports={inspect};
if(require.main===module){const fs=require('node:fs');const file=process.argv[2]||__dirname+'/oversize_inline_61x355_20261107.json';const out=inspect(JSON.parse(fs.readFileSync(file,'utf8')));console.log(JSON.stringify(out,null,2));if(!out.ok)process.exitCode=1;}
