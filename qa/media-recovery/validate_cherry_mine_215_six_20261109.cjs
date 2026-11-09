'use strict';
// Offline, read-only, fail-closed archival evidence validator. No HTTP, WordPress, CDN or file mutation.
const fs = require('node:fs');
const EXPECTED = Object.freeze([
  ['215:0','https://commons.wikimedia.org/wiki/Special:Redirect/file/Cherry_Mine_disaster,_crowd_at_mouth_of_shaft.jpg?width=1280','LC-DIG-ggbain-04371',[4811,3367],[960,672],1909],
  ['215:1','https://commons.wikimedia.org/wiki/Special:Redirect/file/Cherry_Mine_fan_house_and_escape_shaft_postcard.jpg?width=1280',null,[600,374],[600,374],1910],
  ['215:2','https://commons.wikimedia.org/wiki/Special:Redirect/file/A_miner%27s_family_at_dinner_-_DPLA_-_5f57daf0a0ca864c0d59173171a22547.jpg?width=1280','DPLA:5f57daf0a0ca864c0d59173171a22547',[1536,1024],[960,640],1910],
  ['215:3','https://commons.wikimedia.org/wiki/Special:Redirect/file/The_Appalling_Mine_Disaster_at_Cherry,_III._(1).png?width=1280',null,null,null,null],
  ['215:4','https://commons.wikimedia.org/wiki/Special:Redirect/file/Cherry_Mine_disaster,_mourners_and_coffins_LCCN2014684364.jpg?width=1280','LCCN2014684364 / LC-DIG-ggbain-04370',[1024,747],[960,700],null],
  ['215:5','https://commons.wikimedia.org/wiki/Special:Redirect/file/Group_made_orphans_by_Cherry_Mine_disaster_where_400_men_were_entombed,_Nov._13,_1909,_Cherry,_Ill._-_Washington_Photo_Co._LCCN2011661524.jpg?width=1280','LCCN2011661524 / LC-DIG-ds-01289',[8194,5544],[960,650],1909]
]);
const FALSE_RELEASE = ['rights_cleared','full_resolution_inspection_passed','byte_identity_verified','download_authorized','cache_authorized','wordpress_upload_authorized','post_block_rewrite_authorized'];
const NULL_VISITOR = ['actual_http_status','final_url','mime','natural_width_px','natural_height_px','wire_bytes','was_cached','confirmed_broken'];
function validate(a) {
 const errors=[]; const fail=(s)=>errors.push(s);
 if(!a||typeof a!=='object'||Array.isArray(a)) return {ok:false,errors:['invalid_root']};
 if(a.schema!=='fv-media-cherry-215-catalog-custody-v1'||a.audit_date_utc!=='2026-11-09') fail('schema_or_date');
 if(a.scope?.includes('No actual visitor')!==true) fail('scope_must_disclaim_guest_status');
 const corpus=a.source_corpus||{};
 if(corpus.posts!==61||corpus.inline_images!==355||corpus.external_origin_slots!==288||corpus.as_of!=='2026-10-30'||corpus.post_id!==215||
 corpus.frozen_part!=='qa/media-recovery/parts/06.json'||corpus.frozen_blob_sha!=='0f3dfe398a76838049cebba7cb773d5c5a0c8c69') fail('historical_census_or_fixture');
 if(corpus.post_url!=='https://finalvestige.com/2026/08/18/a-wall-in-the-dark/'||corpus.modified_at_source!=='2026-10-29T15:59:59') fail('post_source_identity');
 if(a.method?.browser_guest_status!=='UNMEASURED'||a.method?.image_transfer_bytes!=='UNMEASURED'||a.method?.percent_76_savings!=='UNMEASURED') fail('unsupported_measurement');
 if(a.performance_context?.historical_reported_broken_42_browser_verified!==false||a.performance_context?.claimed_76_percent_transfer_saving_verified!==false||
 a.performance_context?.wp_originals_over_1500000_bytes!==15||a.performance_context?.stored_bytes_for_15!==47096779||
 a.performance_context?.stored_bytes_not_wire_bytes!==true) fail('performance_claim_or_unit');
 if(JSON.stringify(a.site_qa_owned_guest_queue)!==JSON.stringify(['285:5','285:2','287:5','418:1','418:2','407:1'])) fail('site_qa_p0_queue');
 if(!Array.isArray(a.rows)||a.rows.length!==6) return {ok:false,errors:[...errors,'must_have_six_rows']};
 const unique=new Set(); const urlUnique=new Set();
 for(let i=0;i<6;i++){
  const r=a.rows[i]||{}, exp=EXPECTED[i], cat=r.catalog||{}, vis=r.visitor||{}, rel=r.release||{}, ret=r.retriever||{};
  const id=exp[0];if(r.slot!==id||r.post_id!==215||r.post_url!==corpus.post_url) fail(id+':slot_post_binding');
  if(r.stored_url!==exp[1]) fail(id+':original_stored_url_changed');
  if(unique.has(r.slot)||urlUnique.has(r.stored_url)) fail(id+':duplicate_source'); unique.add(r.slot);urlUnique.add(r.stored_url);
  if(typeof r.original_alt!=='string'||r.original_alt.length<40||r.source_inventory_blob_sha!==corpus.frozen_blob_sha) fail(id+':alt_or_fixture_provenance');
  if(r.requested_redirect_width_px!==1280) fail(id+':requested_width');
  if(ret.tool!=='web.open'||ret.checked_utc_date!=='2026-11-09'||ret.result!=='TOOL_URL_NOT_ACCESSIBLE'||ret.actual_http_status!==null) fail(id+':retriever_is_not_guest_http');
  for(const key of NULL_VISITOR){if(!Object.hasOwn(vis,key)||vis[key]!==null) fail(id+':fabricated_visitor_'+key);}
  if(cat.accession!==exp[2]||cat.catalog_date_year!==exp[5]) fail(id+':catalog_accession_or_date');
  if(!cat.url?.startsWith('https://commons.wikimedia.org/wiki/File:')||typeof cat.authority!=='string'||!cat.authority) fail(id+':catalog_title_or_authority');
  if(typeof cat.rights_observation!=='string'||cat.rights_observation.length<32||typeof cat.scene_and_caption_gate!=='string'||cat.scene_and_caption_gate.length<40)fail(id+':rights_or_scene_disclaimer');
  if(cat.binary_exact_match_verified!==false||cat.html_verified!==(i!==3)) fail(id+':catalog_evidence_overclaim');
  for(const [field,target] of [['native_master_catalog_px',exp[3]],['conditional_max960_catalog_px',exp[4]]]){
    if(JSON.stringify(cat[field])!==JSON.stringify(target))fail(id+':'+field);
  }
  if(exp[3]!==null){
   const [mw,mh]=exp[3],[rw,rh]=exp[4];
   if(!Number.isInteger(mw)||!Number.isInteger(mh)||rw>960||rw>mw||rh>mh||Math.abs(rh-rw*mh/mw)>1.25)fail(id+':invalid_no_upscale_aspect');
  }else if(cat.primary_catalog_url!==null||cat.creator_credit!==null)fail(id+':unknown_image_cannot_gain_catalog_evidence');
  for(const key of FALSE_RELEASE){if(rel[key]!==false)fail(id+':unsafe_release_'+key);}
 }
 if(!a.rows[1].catalog.scene_and_caption_gate.includes('1910')||!a.rows[1].catalog.scene_and_caption_gate.includes('upscale'))fail('postcard_1910_no_upscale');
 if(!a.rows[2].catalog.scene_and_caption_gate.includes('1910'))fail('family_photo_1910_not_1909');
 if(!a.rows[5].catalog.scene_and_caption_gate.includes('not verified death count'))fail('archival_400_entombed_not_death_count');
 if(a.rows[3].catalog.native_master_catalog_px!==null||a.rows[3].catalog.conditional_max960_catalog_px!==null)fail('unverified_illustration_geometry');
 return {ok:errors.length===0,errors};
}
module.exports={validate,EXPECTED};
if(require.main===module){
 const path=process.argv[2]||'qa/media-recovery/cherry_mine_215_six_20261109.json';
 try{const result=validate(JSON.parse(fs.readFileSync(path,'utf8')));process.stdout.write(JSON.stringify(result)+'\n');if(!result.ok)process.exitCode=1;}catch(e){process.stderr.write('read_or_parse_failure: '+e.message+'\n');process.exitCode=1;}
}
