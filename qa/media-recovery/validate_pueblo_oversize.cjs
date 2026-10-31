'use strict';
// Fail-closed offline custody crosswalk: no HTTP, no WordPress writes.
const fs=require('node:fs'),path=require('node:path');
const loadJSON=f=>JSON.parse(fs.readFileSync(path.join(__dirname,f),'utf8'));
function load(){return{
 p:loadJSON('pueblo_nhhc_20261030.json'),b:loadJSON('oversize_960_plan_20261030.json'),
 ims:Array.from({length:8},(_,i)=>loadJSON('parts/'+String(i+1).padStart(2,'0')+'.json')).flatMap(x=>x.images),
 originals:loadJSON('oversize_originals_20261030.json')};}
function validate(p,b,ims,originals){
 const errs=[],sources=new Map(ims.map(x=>[x.key,x])),base=new Map(originals.map(x=>[x.media_id,x]));
 const catalog={'280:0':'428-GX-USN-1129207','280:1':'NH 75559','280:2':'NH 75561','280:3':'K-64683','280:4':null,'280:5':'K-64728'};
 if(ims.length!==355||p?.rows?.length!==6||p.post_id!==280||!Array.isArray(b?.rows)||b.rows.length!==13||p.snapshot_parent_head!==b.snapshot_parent_head||!/^[0-9a-f]{40}$/.test(p.snapshot_parent_head||''))errs.push('census_or_schema');
 if(new Set(p.rows.map(x=>x.image_key)).size!==6||new Set(b.rows.map(x=>x.media_id)).size!==13)errs.push('duplicate_id');
 for(let i=0;i<6;i++){let x=p.rows[i],s=sources.get(x.image_key);
  if(x.image_key!==('280:'+i)||!s||s.source_url!==x.stored_source_url||s.alt!==x.stored_alt||x.post_id!==280)errs.push('image_snapshot:'+i);
  if(x.official_catalog_id!==catalog[x.image_key]||!x.official_catalog_url.startsWith('https://www.history.navy.mil/'))errs.push('catalog_identity:'+i);
  if(i===4&&(x.match_evidence!=='official_article_embedded_image_uncataloged'||!x.unverified_subject_alternative_url?.includes('NH-68703')))errs.push('banner_not_verified_exact');
  if(i===3&&!x.editorial_alt_proposal?.includes('A released USS Pueblo crewman'))errs.push('one_crewman_correction');
  if(x.rights_item_level_cleared!==false||x.source_binary_match_verified!==false||x.original_image_binary_sha256!==null||x.wp_media_item_id!==null||x.wp_upload_approved!==false||x.post_rewrite_approved!==false||x.production_write_made!==false)errs.push('rights_or_cms:'+i);
  if(x.browser_http_status!==null||x.browser_natural_width_px!==null||x.browser_transfer_bytes!==null||x.source_intrinsic_width_px!==null||x.source_intrinsic_height_px!==null)errs.push('fabricated_status:'+i);
  if(x.target_max_width_px!==960||x.no_upscale!==true||x.preserve_aspect_ratio!==true)errs.push('unsafe_960:'+i);
 }
 if(p.claim_42_broken_verified!==false)errs.push('unsupported_broken_count');
 let sum=0,group=[0,0,0];
 for(const x of b.rows){const o=base.get(x.media_id);sum+=x.original_storage_bytes;
  if(!o||x.original_url!==o.url||x.original_storage_bytes!==o.original_bytes||x.original_width_px!==o.original_width_px||x.original_height_px!==o.original_height_px||JSON.stringify(x.inline_image_keys)!==JSON.stringify(o.referenced_inline_positions)||x.known_1024_variant_url!==o.existing_wp_1024_variant)errs.push('oversize_snapshot:'+x.media_id);
  const w=Math.min(960,x.original_width_px),h=Math.round(w*x.original_height_px/x.original_width_px);
  if(x.target_width_px!==w||x.target_height_px!==h||x.no_upscale!==true||x.preserve_aspect_ratio!==true||x.target_width_px>960)errs.push('unsafe_dimensions:'+x.media_id);
  const pri=x.inline_image_keys.length?(x.known_1024_variant_url?'P2_inline_variant_known_unverified':'P1_inline_no_variant_recorded'):'P3_not_inline_in_61_posts';
  if(x.priority!==pri)errs.push('priority:'+x.media_id);
  group[pri.startsWith('P1')?0:pri.startsWith('P2')?1:2]++;
  for(const key of x.inline_image_keys)if(sources.get(key)?.source_url!==x.original_url)errs.push('source_slot:'+key);
  if(x.original_sha256!==null||x.variant_http_status!==null||x.measured_browser_transfer_bytes!==null||x.predicted_or_measured_savings_percent!==null||x.rights_cleared_for_derivative!==false||x.production_write_made!==false||x.approved_for_recompression!==false||x.wp_media_upload_approved!==false)errs.push('invented_bytes_or_approval:'+x.media_id);
 }
 if(group.join()!=='5,2,6'||sum!==b.original_storage_bytes_total||b.count!==13)errs.push('large_census');
 if(b.before_image_wire_bytes!==null||b.after_image_wire_bytes!==null||b.claimed_76pct_measured!==false||b.claim_42_broken_verified!==false)errs.push('unsupported_savings_claim');
 return{ok:!errs.length,errors:errs,pueblo_images:p.rows.length,oversize_originals:b.rows.length,distribution:group,storage_bytes:sum};
}
if(require.main===module){const z=load(),v=validate(z.p,z.b,z.ims,z.originals);console.log(JSON.stringify(v,null,2));if(!v.ok)process.exitCode=1;}
module.exports={load,validate};
