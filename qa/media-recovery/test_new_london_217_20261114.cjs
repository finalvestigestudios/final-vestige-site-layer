'use strict';
const {validate}=require('./validate_new_london_217_20261114.cjs');
const base=require('./new_london_217_catalog_rights_20261114.json');
function runTests(){
 let passed=0;
 function check(b,m){if(!b)throw Error('FAILED '+m);passed++}
 const clone=()=>JSON.parse(JSON.stringify(base));
 check(validate(clone()).ok,'baseline');
 function neg(label,fn){const a=clone();fn(a);check(!validate(a).ok,label)}
 neg('invented broken',a=>a.browser_verified_broken_count=42);
 neg('invented wire saving',a=>a.visitor_weight_reduction_percent=76);
 neg('claim 42 verified',a=>a.reference_61_355.report_of_42_broken='confirmed');
 neg('claim 76 verified',a=>a.reference_61_355.report_of_76_percent='measured');
 neg('production mutation',a=>a.production_wordpress_write=true);
 neg('downloaded assets',a=>a.downloaded_media_binaries=true);
 neg('inaccurate oversized total',a=>a.reference_61_355.oversize_originals_stored_bytes++);
 neg('source collection drift',a=>a.frozen_source.blob='bogus');
 neg('missing image',a=>a.images.pop());
 for(let i=0;i<6;i++){
  neg('URL tamper '+i,a=>a.images[i].source_url+='&crop=1');
  neg('wrong catalog '+i,a=>a.images[i].catalog_url='https://commons.wikimedia.org/wiki/File:Unrelated.jpg');
  neg('fake 404 '+i,a=>a.images[i].guest_browser_http_status=404);
  neg('fake transfer '+i,a=>a.images[i].guest_network_transfer_bytes=200);
  neg('incorrect width '+i,a=>a.images[i].original_width_px++);
  neg('upscale '+i,a=>a.images[i].conditional_max_width_px=1280);
  neg('unlicensed cache '+i,a=>a.images[i].rights_clear_to_cache=true);
  neg('unlicensed rehost '+i,a=>a.images[i].rights_clear_to_rehost=true);
  neg('unsupported rights '+i,a=>a.images[i].commons_reported_rights='PUBLIC_DOMAIN_GUARANTEED');
  neg('WP write '+i,a=>a.images[i].production_wordpress_write_authorized=true);
  neg('unproven binary '+i,a=>a.images[i].exact_visual_crop_verified=true);
  neg('altered ALT '+i,a=>a.images[i].alt='');
 }
 neg('remove CC link',a=>a.images[5].license_url=null);
 neg('fake license in caption',a=>a.images[5].caption_has_license_link=true);
 neg('lost INP ancestry',a=>a.images[3].extracted_from_original=null);
 neg('lost timeline warning',a=>a.images[0].metadata_date_discrepancy=null);
 return {passed,failed:0};
}
module.exports={runTests};
if(require.main===module)console.log(JSON.stringify(runTests()));
