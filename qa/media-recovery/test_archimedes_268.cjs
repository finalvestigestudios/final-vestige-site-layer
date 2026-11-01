'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const {validate}=require('./validate_archimedes_268.cjs');
const copy=x=>structuredClone(x);
function sample(){
 const originals=[[665,448],[10880,8160],[2040,2720],[8160,10880],[8160,10880],[6600,9500]];
 const commonsSlots=[0,2,3,5,6,9];
 const rows=Array.from({length:10},(_,i)=>{
  const n=commonsSlots.indexOf(i),known=n>=0,w=known?originals[n][0]:null,h=known?originals[n][1]:null;
  const tw=known?Math.min(960,w):null, th=known?Math.round(h*tw/w):null;
  const sourceUrl=known?`https://commons.wikimedia.org/wiki/Special:Redirect/file/slot%20${i}.jpg?width=960`:`https://archimedespalimpsest.org/a/${i}.jpg`;
  return {image_key:`268:${i}`,slot:i,post_id:268,article_url:'https://finalvestige.com/p/',exact_stored_url:sourceUrl,source_kind:known?'wikimedia_redirect':'external',alt_text:`alt ${i}`,
    source_viewer:{method:'independent_web_retriever_2026_11_01',result:[1,7].includes(i)?'RENDERED':i===4?'APEX_REDIRECT_TARGET_UNAVAILABLE':i===8?'UNAVAILABLE':'UNAVAILABLE_OR_REDIRECT_NOT_FOLLOWED',http_status:null,decoded_dimensions_px:null,is_guest_browser_proof:false},
    catalog:{source_record_url:known?`https://commons.wikimedia.org/wiki/File:slot_${i}.jpg`:null,record_type:known?'exact_commons_filename_record':'publisher_site_jpeg_no_individual_catalog_record_confirmed',original_width_px:w,original_height_px:h,dimensions_origin:known?'commons_file_page_original_master_metadata':'unverified',original_sha256:null},
    rights:{recorded_claim:known?(i===0?'commons_us_public_domain_claim_unevaluated':'commons_cc_by_2_0_vs_project_data_cc_by_3_0'):'no_item_specific_reuse_permission_verified_for_project_website_presentation_photo',credit_to_preserve:'needs credit',license_decision:'HOLD',item_permission_verified:false,rights_review_done:false},
    optimization:{maximum_width_px:960,proposed_width_px:tw,proposed_height_px:th,no_upscale:true,preserve_aspect_ratio:true,source_material_not_downloaded:true,local_cached_media_id:null,original_master_hash_verified:false,derivative_quality_qa_complete:false},
    visitor_browser:{http_status:null,final_image_url:null,decoded_width_px:null,encoded_transfer_bytes:null,broken:null,measured_savings_percent:null},wordpress_media_upload_authorized:false,wordpress_post_edit_authorized:false};
 });
 return {doc:{schema_version:1,cms:{post_id:268,status:'publish',url:'https://finalvestige.com/p/',live_exact_source_url_matches:10,live_exact_alt_matches:10},summary:{image_slots:10,commons_file_records:6,publisher_hosted_jpegs:4,web_retriever_rendered:2,web_retriever_inconclusive:8,visitor_broken_confirmed:null,measured_weight_reduction_percent:null,production_replacements:0},publisher_license_scope_warning:'Project dataset CC BY 3.0 is not necessarily site photo license.',rows},census:{images:rows.map(x=>({post_id:268,slot:x.slot,source_url:x.exact_stored_url,alt:x.alt_text,post_url:x.article_url}))}};
}
test('valid bounded rights-closed synthetic custody fixture',()=>{const {doc,census}=sample();assert.deepEqual(validate(doc,census),{ok:true,errors:[]})});
const mutations=[
 ['wrong original image', d=>d.rows[0].exact_stored_url='https://different.org/img.jpg'],
 ['different historical alt',d=>d.rows[3].alt_text='unrelated'],
 ['duplicate image key',d=>d.rows[1].image_key='268:0'],
 ['fake loaded HTTP 200',d=>d.rows[1].visitor_browser.http_status=200],
 ['fake 403',d=>d.rows[8].visitor_browser.http_status=403],
 ['invented transfer bytes',d=>d.rows[2].visitor_browser.encoded_transfer_bytes=4218],
 ['fake broken count',d=>d.summary.visitor_broken_confirmed=2],
 ['fake 76 percent',d=>d.summary.measured_weight_reduction_percent=76],
 ['downscale overshoot',d=>d.rows[0].optimization.proposed_width_px=960],
 ['aspect corruption',d=>d.rows[9].optimization.proposed_height_px=1200],
 ['invented website-image width',d=>d.rows[4].catalog.original_width_px=600],
 ['invented website-image derivative',d=>d.rows[7].optimization.proposed_width_px=960],
 ['unsupported project license on presentation photo',d=>d.rows[1].rights.recorded_claim='commons_cc_by_2_0_vs_project_data_cc_by_3_0'],
 ['unresolved commons license switched to approved',d=>d.rows[2].rights.license_decision='APPROVED'],
 ['wordpress media write mistakenly enabled',d=>d.rows[2].wordpress_media_upload_authorized=true],
 ['wordpress block rewrite mistakenly enabled',d=>d.rows[5].wordpress_post_edit_authorized=true],
 ['claim retriever is visitor Chrome',d=>d.rows[1].source_viewer.is_guest_browser_proof=true],
 ['pretend web viewer returned status',d=>d.rows[8].source_viewer.http_status=404],
 ['claim 4 rendered photos',d=>d.summary.web_retriever_rendered=4],
 ['asset binary hash invented',d=>d.rows[6].catalog.original_sha256='0000000'],
 ['claim source file copied',d=>d.rows[3].optimization.source_material_not_downloaded=false],
 ['missing source slot',d=>d.rows.pop()],
 ['wrong source classification',d=>d.rows[3].source_kind='external'],
 ['duplicate media target',d=>d.rows[1].optimization.local_cached_media_id=123],
 ['missing source credit',d=>d.rows[2].rights.credit_to_preserve=''],
 ['unverified browser successful decode',d=>d.rows[5].visitor_browser.decoded_width_px=960],
 ['wrong Commons file catalog',d=>d.rows[2].catalog.source_record_url='https://commons.wikimedia.org/wiki/File:unrelated.jpg'],
 ['missing required catalog record',d=>d.rows[3].catalog=null],
 ['missing rights object',d=>d.rows[6].rights=null],
 ['null image slot',d=>d.rows[1]=null]
];
for(const [name,mutate] of mutations){test('reject '+name,()=>{const {doc,census}=sample();mutate(doc);assert.equal(validate(doc,census).ok,false)})}
