'use strict';
// Read-only, offline, evidence-quality validator. Does not fetch, modify, upload, or publish media.
const EXPECTED=[
  {
    "key": "418:0",
    "url": "https://www.history.uscg.mil/Portals/6/2_%20new%20and%20old%20lighthouses%2019849609_web1_1_-Scotch-Cap-lighthouse-1200x984.jpg",
    "alt": "The old and new Scotch Cap lighthouses on Unimak Island before the concrete lighthouse was destroyed by the April 1, 1946 tsunami.",
    "record": "https://www.history.uscg.mil/Research/THE-LONG-BLUE-LINE/Article/2866442/the-long-blue-line-standing-a-deadly-watch-75-years-agofinal-hours-of-scotch-ca/",
    "id": "not established",
    "result": "RETRIEVER_INACCESSIBLE_NO_STATUS",
    "error": null
  },
  {
    "key": "418:1",
    "url": "https://media.defense.gov/2021/Mar/30/2002610812/1920/1080/0/210330-G-DE713-0002.JPG",
    "alt": "Chief Boatswain’s Mate Anthony L. Petit, officer in charge of Scotch Cap Lighthouse when the 1946 tsunami killed its five-man crew.",
    "record": "https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/",
    "id": "210330-G-DE713-0002.JPG",
    "result": "RETRIEVER_403",
    "error": 403
  },
  {
    "key": "418:2",
    "url": "https://www.history.uscg.mil/Portals/6/5_%20Scotch_Cap_debris2_1946.jpg",
    "alt": "Broken concrete and debris where Scotch Cap Lighthouse stood after the April 1, 1946 tsunami.",
    "record": "https://www.history.uscg.mil/Research/THE-LONG-BLUE-LINE/Article/2866442/the-long-blue-line-standing-a-deadly-watch-75-years-agofinal-hours-of-scotch-ca/",
    "id": "not established",
    "result": "RETRIEVER_403",
    "error": 403
  },
  {
    "key": "418:3",
    "url": "https://www.history.uscg.mil/Portals/6/6_%20Scotch%20Cap%20remains.jpg",
    "alt": "Aerial photograph of the destroyed Scotch Cap light station on Unimak Island after the 1946 tsunami.",
    "record": "https://www.history.uscg.mil/Research/THE-LONG-BLUE-LINE/Article/2866442/the-long-blue-line-standing-a-deadly-watch-75-years-agofinal-hours-of-scotch-ca/",
    "id": "not established",
    "result": "RETRIEVER_INACCESSIBLE_NO_STATUS",
    "error": null
  },
  {
    "key": "418:4",
    "url": "https://www.hawaiimagazine.com/wp-content/uploads/2020/12/Tsunami1946NOAA2.jpg",
    "alt": "Tsunami water inundating the Hilo waterfront in April 1946, with a person visible near the advancing water.",
    "record": "https://prod-01-alb-www-noaa.woc.noaa.gov/noaa-collections/photo-library/pl23theb2705jpg",
    "id": "pl23_theb2705.jpg",
    "result": "RETRIEVER_RENDERED",
    "error": null
  },
  {
    "key": "418:5",
    "url": "https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/styles/full_width/public/media/images/19460401_UNKNOWN_37-012_copy.jpg?itok=ASMRCahz",
    "alt": "Debris covering a Hilo street and partly burying a vehicle after the April 1, 1946 tsunami.",
    "record": "https://www.usgs.gov/media/images/damage-hilo-tsunami-struck-april-fools-day-1946",
    "id": "19460401_UNKNOWN_37-012_copy.jpg",
    "result": "RETRIEVER_RENDERED",
    "error": null
  }
];
function demand(condition,message){if(!condition)throw new Error(message);}
function validateTsunami418(d){
 demand(d?.schema_version===1 && d.post_id===418,'schema/post mismatch');
 demand(d?.source_inventory_verified_current_cms===true && d.wp_modified==='2026-08-28T03:11:08','unverified current WordPress source');
 demand(d.source_count===6 && d.offsite_source_count===6 && Array.isArray(d.rows) && d.rows.length===6,'six offsite slots required');
 demand(d.sitewide_post_count===61 && d.sitewide_reference_count===355 && d.sitewide_external_reference_count===288 && d.oversized_originals_above_1_5MiB===13,'frozen sitewide baseline mutated');
 demand(d.claimed_broken_42_verified===false && d.claimed_76pct_weight_reduction_measured===false && d.verified_sitewide_browser_broken_count===null && d.measured_before_image_bytes===null && d.measured_after_image_bytes===null,'fabricated sitewide failure or image-weight evidence');
 demand(d.production_images_repaired===0,'unapproved production repair asserted');
 demand(typeof d.frozen_source_blob_sha==='string' && /^[a-f0-9]{40}$/.test(d.frozen_source_blob_sha),'missing frozen source custody hash');
 const keys=new Set();
 for(let i=0;i<EXPECTED.length;i++){
  const row=d.rows[i], expected=EXPECTED[i];
  demand(row?.key===expected.key && row.post_id===418 && row.slot===i && !keys.has(row.key),'duplicate or changed slot');keys.add(row.key);
  demand(row.original_source_url===expected.url && row.original_alt===expected.alt,'published URL or ALT altered');
  demand(row.source_html_width_px===null && row.source_html_height_px===null,'unsupported HTML dimensions');
  const v=row.viewer,b=row.browser,c=row.candidate;
  demand(v?.method==='web.run.open exact published source URL on 2026-11-01; not a guest browser','retriever methodology lost');
  demand(v.result===expected.result && v.retriever_error_code===expected.error,'retriever observation altered');
  demand(v.origin_http_status===null && v.final_image_http_status===null && v.encoded_transfer_bytes===null && v.decoded_natural_width_px===null,'retriever misreported as visitor Image response');
  demand(b?.logged_out_verified===false && b.current_src===null && b.status===null && b.content_type===null && b.natural_width_px===null && b.natural_height_px===null && b.encoded_transfer_bytes===null && b.failed_visible_screenshot===null,'fabricated logged-out browser proof');
  demand(c?.record===expected.record && c.identifier===expected.id && typeof c.authority==='string' && c.authority.length>10,'archive record mismatch');
  demand(typeof c.relationship==='string' && c.relationship.length>30 && typeof c.credit==='string' && c.credit.length>5 && typeof c.rights_note==='string' && c.rights_note.length>30,'weak archival provenance or copyright note');
  demand(c.rights_review==='HOLD' && c.wordpress_upload_authorized===false && c.wordpress_post_edit_authorized===false && c.visual_QA_complete===false,'premature publication clearance');
  demand(c.binary_identity_verified===false && c.master_sha256===null,'invented exact-image custody');
  demand(c.candidate_width_cap_px===960 && c.no_upscale===true && c.preserve_aspect_ratio===true,'resize safeguards changed');
  demand(c.source_width_px===null && c.source_height_px===null && c.conditional_max_dimensions===null,'unverified master geometry and derivative');
  if(i===0)demand(c.filename_geometry_hint?.width_px===1200 && c.filename_geometry_hint.height_px===984 && c.filename_geometry_hint.unverified===true,'1200x984 is only an unverified filename hint');
  else demand(c.filename_geometry_hint===null,'invented filename geometry');
  if(i===1)demand(c.identifier==='210330-G-DE713-0002.JPG' && decodeURI(row.original_source_url).includes('210330-G-DE713-0002.JPG'),'missing exact Coast Guard identifier');
  if(i===4)demand(c.relationship.includes('NOT proven') && !c.relationship.includes('binary match'),'NOAA candidate falsely identified as exact photograph');
  if(i===5)demand(row.original_source_url.includes('19460401_UNKNOWN_37-012_copy.jpg') && c.identifier==='19460401_UNKNOWN_37-012_copy.jpg','USGS image filename mismatch');
 }
 return {ok:true,validated_slots:6,web_retriever_not_browser:true,production_writes_allowed:0};
}
module.exports={validateTsunami418,EXPECTED};
if(require.main===module){const fs=require('node:fs'),path=require('node:path'); const file=process.argv[2]||path.join(__dirname,'tsunami_418_uscg_noaa_usgs_20261101.json');process.stdout.write(JSON.stringify(validateTsunami418(JSON.parse(fs.readFileSync(file,'utf8'))))+'\\n');}
