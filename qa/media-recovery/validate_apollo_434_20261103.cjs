'use strict';
const fs = require('node:fs');
const path = require('node:path');
const IDs = [null,'S67-15717','S66-58038','KSC-20170124-PH_KLS01_0164','S67-21294','KSC-20170124-PH_KLS01_0090'];
function validate(a, frozen) {
  const e=[]; const fail=s=>e.push(s);
  if(a?.schema!=='fv-apollo-434-live-nasa-dependency-v1')fail('schema');
  if(a?.wordpress?.post_id!==434||a?.wordpress?.status!=='publish'||a?.wordpress?.read_only!==true||a?.wordpress?.source_reconciled_6_of_6!==true)fail('wp source');
  if(a?.archive?.inventory_file!=='qa/media-recovery/parts/01.json'||! /^[a-f0-9]{40}$/.test(a?.archive?.git_blob_sha||''))fail('archive pin');
  const archive=(frozen?.images||[]).filter(x=>x.post_id===434);
  if(archive.length!==6||!Array.isArray(a?.images)||a.images.length!==6)return [...e,'six slot census'];
  for(let i=0;i<6;i++){
    const x=a.images[i],z=archive[i];
    if(x.key!==`434:${i}`||x.source_url!==z.source_url||x.stored_alt!==z.alt||JSON.stringify(x.stored_dimensions_px)!==JSON.stringify([z.width_px,z.height_px]))fail(`source identity ${i}`);
    if(i===0){if(x.source_kind!=='first_party'||x.nasa_identifier!==null)fail('first party');}
    else if(x.source_kind!=='external_nasa'||x.nasa_identifier!==IDs[i]||x.catalog_id_match!==true||
      !x.source_url.startsWith(`https://images-assets.nasa.gov/image/${IDs[i]}/${IDs[i]}~large.jpg`)||
      !/^https:\/\/(?:www\.nasa\.gov|commons\.wikimedia\.org)\//.test(x.canonical_catalog_url||''))fail(`NASA identity ${i}`);
    if(!['not_tested','displayed','inaccessible_no_origin_status'].includes(x.original_url_observation?.result))fail(`wrapper result ${i}`);
    for(const f of ['origin_http_status','guest_http_status','guest_current_src','guest_decode_ok','guest_natural_width_px','guest_wire_bytes'])if(x.original_url_observation?.[f]!==null)fail(`unmeasured guest/origin ${i} ${f}`);
    const d=x.conditional_derivative_px,p=x.catalog_pixel_dimensions_px??x.stored_dimensions_px;
    if(!Array.isArray(d)||d.length!==2||d[0]!==Math.min(960,p[0])||d[1]!==Math.round(p[1]*d[0]/p[0])||
       d[0]>p[0]||d[0]>960||x.derivative_max_width_px!==960||x.upscale_prohibited!==true)fail(`derivative ${i}`);
    if(x.rights?.status!=='ITEM_REVIEW_REQUIRED'||x.rights?.reuse_authorized!==false||x.wordpress_upload_authorized!==false||x.wordpress_post_edit_authorized!==false)fail(`rights ${i}`);
  }
  if(!a.images[3].historical_caption_conflict?.includes('mockup')||!a.images[3].stored_alt.includes('three-part')||!a.images[3].proposed_alt_review_only?.includes('mockup'))fail('historical discrepancy');
  if(a.scoped_totals?.inline_images!==6||a.scoped_totals?.external_nasa!==5||a.scoped_totals?.exact_source_displayed_by_independent_retriever!==1||a.scoped_totals?.retriever_inaccessible_without_origin_status!==4||a.scoped_totals?.guest_browser_confirmed_broken!==0||a.scoped_totals?.production_replacements!==0)fail('honest totals');
  if(a.sitewide_context?.claimed_wire_reduction_76_percent_measured!==false||a.sitewide_context?.alleged_broken_42_guest_confirmed!==false||a.status!=='EVIDENCE_ONLY_HOLD'||a.permissions?.wordpress_write!==false||a.permissions?.republish!==false)fail('claims or publish');
  return e;
}
module.exports={validate};
if(require.main===module){
 const a=JSON.parse(fs.readFileSync(path.join(__dirname,'apollo_434_nasa_sources_20261103.json'),'utf8'));
 const f=JSON.parse(fs.readFileSync(path.join(__dirname,'parts/01.json'),'utf8'));
 const errors=validate(a,f);console.log(errors.length?errors:'Apollo 434 source/rights validator PASS');
 process.exitCode=errors.length?1:0;
}
