'use strict';
const {test} = require('node:test');
const assert = require('node:assert/strict');
const {censusFromParts,validate} = require('./validate_duplicate_source_20261101.cjs');
const clone=x=>structuredClone(x);
function fixture() {
  const origin='https://research.fs.usda.gov/images/';
  const rows=[];
  for(let i=0;i<7;i++) rows.push({key:'213:'+i,post_id:213,post_title:'The Fire He Lit Himself',post_url:'https://finalvestige.com/213',slot:i,source_url:origin+(i===6?'map2.jpg':'map'+i+'.jpg'),source_kind:'external',alt:'USFS archival image '+i,width_px:i===0?1024:null,height_px:i===0?622:null});
  for(const i of [2,5])rows.push({key:'291:'+i,post_id:291,post_title:'One Bulldozer Never Came Back',post_url:'https://finalvestige.com/291',slot:i,source_url:'https://archive.example.org/teton.jpg',source_kind:'external',alt:'Dam visual '+i,width_px:null,height_px:null});
  const part={posts:[{id:213},{id:291}],images:rows};
  const counted=censusFromParts([part]);
  const groups=counted.duplicates.map(a=>({post_id:a[0].post_id,exact_stored_url:a[0].source_url,confirmed_live_cms_duplicate:true,image_binary_identity_verified:false,visitor_browser_http_status:null,visitor_network_transfer_bytes:null,confirmed_broken_slots:null,rights_status:'HOLD',publication_authorized:false,distinct_alt_count:new Set(a.map(r=>r.alt)).size,source_references:a.map(r=>({image_key:r.key,slot:r.slot,exact_alt:r.alt})),candidate_primary_record_url:'https://www.nwcg.gov/'}));
  const report={schema_version:1,audit_kind:'EXACT_STORED_URL_DUPLICATES_NOT_NETWORK_RESPONSES',inventory:counted.counts,duplicate_groups:groups,network_and_performance_proof:{actual_guest_browser_response_statuses:null,actual_browser_decoded_image_statuses:null,broken_image_slots_count:null,broken_distinct_source_count:null,claimed_42_broken_confirmed:false,measured_76_percent_weight_reduction:null},safety:{no_cms_writes:true,no_media_downloads:true,no_licensed_asset_copy:true,no_homepage_design_edits:true,no_new_spend:true}};
  const images=rows.filter(r=>r.post_id===213).map(r=>({key:r.key,slot:r.slot,exact_stored_url:r.source_url,exact_stored_alt:r.alt,source_kind:r.source_kind,known_stored_width_px:r.width_px,known_stored_height_px:r.height_px,catalog_or_primary_context_url:'https://research.fs.usda.gov/',rights_status:'HOLD',binary_sha256:null,actual_visitor_http_status:null,actual_visitor_decoded_width_px:null,actual_visitor_transfer_bytes:null,wordpress_upload_authorized:false,wordpress_post_update_authorized:false,max_allowed_output_width_px:960,no_upscaling:true,preserve_aspect_ratio:true,verified_catalog_width_px:r.slot===3?1457:null,verified_catalog_height_px:r.slot===3?972:null,conditional_resize_dimensions_px:r.slot===0?{width:960,height:583}:r.slot===3?{width:960,height:640}:null,copyright_and_credit_note:r.slot===5?'Courtesy New York Times: HOLD':'USFS rights held'}));
  const mann={schema_version:1,post_id:213,images,staging_plan:{wordpress_production_write_authorized:false,per_item_rights_approval_required:true},browser_weight_reduction_percent:null,broken_image_count:null};
  return {parts:[part],report,mann};
}
const good=fixture();
test('full synthetic inventory and Mann Gulch ledger pass',()=>assert.equal(validate(...[good.report,good.mann,good.parts]).mann_slots,7));
test('count same image in two slots but as one network-source URL',()=>{const c=censusFromParts(good.parts).counts;assert.equal(c.stored_image_references,9);assert.equal(c.exact_distinct_urls,7);assert.equal(c.intrapost_repeated_url_groups,2);assert.equal(c.intrapost_redundant_image_references,2);});
const mutations=[
 ['invented visitor 404',f=>f.mann.images[0].actual_visitor_http_status=404],
 ['invented visitor 200',f=>f.mann.images[0].actual_visitor_http_status=200],
 ['invented failed-image total',f=>f.report.network_and_performance_proof.broken_image_slots_count=42],
 ['invented 76 percent saving',f=>f.report.network_and_performance_proof.measured_76_percent_weight_reduction=76],
 ['claim 42 failures confirmed',f=>f.report.network_and_performance_proof.claimed_42_broken_confirmed=true],
 ['invented transfer bytes',f=>f.mann.images[2].actual_visitor_transfer_bytes=100],
 ['duplicated URL changed',f=>f.report.duplicate_groups[0].exact_stored_url+='?new=true'],
 ['duplicate ALT mismatch',f=>f.report.duplicate_groups[1].source_references[0].exact_alt='Wrong event'],
 ['source slot spoof',f=>f.report.duplicate_groups[0].source_references[0].image_key='213:6'],
 ['mask a duplicated slot',f=>f.report.duplicate_groups.pop()],
 ['count inflated',f=>f.report.inventory.offsite_references++],
 ['Mann source drift',f=>f.mann.images[3].exact_stored_url='https://other.example.org/image.jpg'],
 ['Mann ALT drift',f=>f.mann.images[2].exact_stored_alt='Unverified claim'],
 ['unauthorized media upload',f=>f.mann.images[1].wordpress_upload_authorized=true],
 ['unauthorized WordPress update',f=>f.mann.images[1].wordpress_post_update_authorized=true],
 ['rights wrongly cleared',f=>f.mann.images[3].rights_status='CLEAR'],
 ['rights gate on report ignored',f=>f.report.duplicate_groups[1].publication_authorized=true],
 ['upscaled width',f=>f.mann.images[0].conditional_resize_dimensions_px.width=1200],
 ['distorted crop',f=>f.mann.images[0].conditional_resize_dimensions_px.height=800],
 ['dimension invention',f=>f.mann.images[1].conditional_resize_dimensions_px={width:960,height:600}],
 ['New York Times rights erased',f=>f.mann.images[5].copyright_and_credit_note='USFS only'],
 ['fake on-site network status',f=>f.report.duplicate_groups[0].visitor_browser_http_status=503],
 ['image data SHA fabricated',f=>f.mann.images[1].binary_sha256='deadbeef'],
 ['staging WP permission opened',f=>f.mann.staging_plan.wordpress_production_write_authorized=true],
 ['malicious source URL scheme',f=>f.parts[0].images[0].source_url='javascript:alert(1)'],
 ['duplicate image key in corpus',f=>f.parts[0].images[1].key='213:0'],
 ['unsafe primary URL credential',f=>f.report.duplicate_groups[0].candidate_primary_record_url='https://someone:password@example.org/a'],
 ['invented failed asset count',f=>f.report.network_and_performance_proof.broken_distinct_source_count=7]
];
for(const [name,mutate] of mutations)test('fail closed: '+name,()=>{const f=clone(good);mutate(f);assert.throws(()=>validate(f.report,f.mann,f.parts));});
