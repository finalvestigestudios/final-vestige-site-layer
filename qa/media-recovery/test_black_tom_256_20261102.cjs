'use strict';
/** Native Node or isolated V8 regression replay; no network, CMS, or image bytes. */
function runCases(inspect,base){
 const errors=[];let passed=0;
 const clone=x=>JSON.parse(JSON.stringify(x));
 const ok=(label,fn,expected)=>{let a=clone(base);fn(a);let e=inspect(a);if(expected){if(e.some(x=>x.includes(expected)))passed++;else errors.push({label,wanted:expected,got:e});}
   else {if(e.length===0)passed++;else errors.push({label,wanted:'valid',got:e});}};
 ok('valid archival audit',()=>{},null);
 const mutations=[
  ['missing slot',a=>a.rows.pop(),'seven_rows_required'],
  ['reorder archival rows',a=>a.rows.reverse(),'row_frozen_identity_mismatch'],
  ['wrong published URL',a=>a.rows[0].stored_original_source_url='https://example.org/substitute.jpg','row_frozen_identity_mismatch'],
  ['alter ALT',a=>a.rows[1].stored_original_alt='different photograph','row_frozen_identity_mismatch'],
  ['invent origin HTTP 404',a=>a.rows[0].independent_source_retriever.origin_http_status=404,'invented_origin_http'],
  ['turn tool rejection into 200',a=>a.rows[0].independent_source_retriever.result='SUCCESS','invented_origin_http'],
  ['invent visitor HTTP 403',a=>a.rows[2].independent_source_retriever.visitor_http_status=403,'invented_origin_http'],
  ['invent screenshot/browser load',a=>a.rows[2].browser.visibly_broken=false,'invented_browser_measurement'],
  ['invent transferred bytes',a=>a.rows[3].browser.uncached_transfer_bytes=7000,'invented_browser_measurement'],
  ['invent final url',a=>a.rows[3].browser.final_url='https://example.com/final.jpg','invented_browser_measurement'],
  ['alter archive master dimensions',a=>a.rows[1].catalog.master_dimensions_from_catalog_px=[960,960],'invalid_archival_identity'],
  ['invent master binary verification',a=>a.rows[4].catalog.decoded_binary_identity_verified=true,'invalid_archival_identity'],
  ['pretend master binary downloaded',a=>a.rows[5].catalog.original_binary_downloaded=true,'invalid_archival_identity'],
  ['auto-upscale 800px to 960px',a=>a.rows[0].conditional_derivative.target_dimensions_px=[960,634],'invalid_derivative_geometry'],
  ['crop tall LOC map',a=>a.rows[1].conditional_derivative.target_dimensions_px=[960,960],'invalid_derivative_geometry'],
  ['false 960 wide on 412px portrait',a=>a.rows[5].conditional_derivative.target_dimensions_px=[960,1678],'invalid_derivative_geometry'],
  ['approve item rights',a=>a.rows[0].rights.assessment='APPROVED','rights_hold_violated'],
  ['approve local mirroring',a=>a.rows[4].rights.license_for_mirroring_approved=true,'rights_hold_violated'],
  ['approve WP rewrite',a=>a.rows[1].authorization.wordpress_post_rewrite_authorized=true,'unauthorized_wordpress_action'],
  ['approve media cache',a=>a.rights_and_release.first_party_cache_release=true,'unauthorized_release'],
  ['approve subscription spend',a=>a.rights_and_release.spend_allowed=true,'unauthorized_release'],
  ['falsely confirm 42 broken',a=>a.sitewide_context.reported_42_broken_guest_verified=true,'unsupported_sitewide_claim'],
  ['falsely measure 76 percent',a=>a.sitewide_context.claimed_76_percent_weight_savings_guest_measured=true,'unsupported_sitewide_claim'],
  ['assert 1 actually broken',a=>a.observation_limitations.verified_browser_broken_count=1,'unsupported_browser_or_redirect_claim'],
  ['wrong archived Git SHA',a=>a.source_inventory.part_git_blob_sha='0'.repeat(40),'frozen_source_not_pinned'],
  ['wrong archival record',a=>a.rows[4].catalog.primary_record_url=a.rows[1].catalog.primary_record_url,'invalid_archival_identity'],
  ['wrong canonical catalog',a=>a.rows[6].catalog.catalog_page_url='https://example.com','invalid_archival_identity'],
  ['duplicate slot',a=>a.rows[1].image_key=a.rows[0].image_key,'row_frozen_identity_mismatch'],
  ['fake catalog browser status',a=>a.observation_limitations.guest_browser_checks=7,'unsupported_browser_or_redirect_claim']
 ];
 for(const [label,fn,expected]of mutations)ok(label,fn,expected);
 return {passed,total:mutations.length+1,failed:errors};
}
module.exports={runCases};
if(require.main===module){
 const a=require('./black_tom_256_archive_20261102.json');
 const {inspect}=require('./validate_black_tom_256_20261102.cjs');
 const result=runCases(inspect,a);
 console.log(JSON.stringify(result,null,2));if(result.passed!==result.total)process.exitCode=1;
}
