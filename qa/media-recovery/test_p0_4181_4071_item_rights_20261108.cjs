'use strict';
function runTests(validate,source){
 const copy=x=>JSON.parse(JSON.stringify(x)),out=[];
 const check=(name,change)=>{const a=copy(source);if(change)change(a);const r=validate(a);const expected=!change;if(r.ok!==expected)throw Error(name+': expected '+expected+' got '+JSON.stringify(r));out.push(name)};
 check('valid_untouched');
 const cases=[
 ['invented_42_count',a=>a.historical_42_broken='CONFIRMED'],
 ['fake_76_savings',a=>a.claimed_76pct_wire_reduction='MEASURED'],
 ['invented_guest_total',a=>a.verified_guest_broken_total=2],
 ['pretend_wp_write',a=>a.wordpress_writes=1],
 ['pretend_asset_cache',a=>a.assets_downloaded=1],
 ['falsify_original_url',a=>a.records[0].original_stored_src+='?changed'],
 ['falsify_post_binding',a=>a.records[0].post_id=407],
 ['invent_origin_403',a=>a.records[0].original_retrieval.is_origin_http=true],
 ['invent_browser_400',a=>a.records[1].original_retrieval.guest_http=400],
 ['lose_wrapper_provenance',a=>a.records[1].original_retrieval.is_guest_browser_http=true],
 ['reverse_uscg_scene',a=>a.records[0].item.catalog_identifies='Lighthouse wreckage'],
 ['false_uscg_binary',a=>a.records[0].candidate.binary_sha256='fakehash'],
 ['assume_uscg_size',a=>a.records[0].candidate.proposed_px=[960,540]],
 ['false_rehost',a=>a.records[1].candidate.cache_or_upload_authorized=true],
 ['upscale_policy',a=>a.records[0].candidate.no_upscale=false],
 ['wrong_usgs_thumbnail_path',a=>a.records[1].item.candidate_image_url+='?changed'],
 ['declare_native_geometry',a=>a.records[1].item.native_px_verified=true],
 ['unconditional_usgs_960',a=>a.records[1].candidate.proposed_px_is_conditional=false],
 ['unlicensed_usgs',a=>a.records[1].item.catalog_usage='All rights reserved'],
 ['remove_attribution',a=>a.records[0].rights.credit_required=''],
 ['misrepresent_wrapper',a=>a.records[1].original_retrieval.wrapper_http_code=404],
 ['duplicate_record',a=>a.records[1].image_key='418:1'],
 ['change_frozen_census',a=>a.prior_p0_ledger.git_blob_sha='deadbeef'],
 ['wrong_primary_name_policy',a=>a.records[0].item.name_variants.editorial_decision='CHANGE_ALT_TO_PETTIT'],
 ['invent_other_post_caption',a=>a.records[1].stored_alt='a different event'],
 ['unverified_release',a=>a.records[0].candidate.wordpress_action='REPLACE_NOW']
 ];
 for(const [n,f] of cases)check(n,f);
 return {ok:true,passed:out.length,test_names:out};
}
module.exports={runTests};
if(typeof require==='function'&&require.main===module){const {validate}=require('./validate_p0_4181_4071_item_rights_20261108.cjs');const fs=require('node:fs');const a=JSON.parse(fs.readFileSync(__dirname+'/p0_4181_4071_item_rights_20261108.json','utf8'));console.log(JSON.stringify(runTests(validate,a),null,2))}
