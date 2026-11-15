"use strict";
const PINNED = [
  [
    "214:0",
    "https://cdn.loc.gov/service/pnp/ggbain/19600/19622v.jpg",
    "https://www.loc.gov/pictures/item/2014699553/marc/"
  ],
  [
    "214:1",
    "https://commons.wikimedia.org/wiki/Special:Redirect/file/Wreck_of_the_Eastland,_Chicago,_1915.jpg",
    "https://hdl.loc.gov/loc.pnp/pan.6a04191"
  ],
  [
    "214:2",
    "https://commons.wikimedia.org/wiki/Special:Redirect/file/EastlandKenosha.jpg",
    "https://commons.wikimedia.org/wiki/File:EastlandKenosha.jpg"
  ],
  [
    "214:3",
    "https://commons.wikimedia.org/wiki/Special:Redirect/file/Helen_Repa_Eastland_Disaster_photo.png?width=1280",
    "https://commons.wikimedia.org/wiki/File:Helen_Repa_Eastland_Disaster_photo.png"
  ],
  [
    "214:4",
    "https://cdn.loc.gov/service/pnp/ggbain/19600/19623v.jpg",
    "https://www.loc.gov/pictures/item/2014699554/"
  ],
  [
    "214:5",
    "https://commons.wikimedia.org/wiki/Special:Redirect/file/Photograph_of_The_Eastland_(upside_down)_on_Chicago_River,_Chicago._-_NARA_-_281841.jpg?width=1280",
    "https://www.archives.gov/chicago/highlights/eastland"
  ]
];
function validate(input) {
 const errors=[];
 const err=(name)=>errors.push(name);
 if(!input||typeof input!=="object")return ["invalid_document"];
 if(input.schema!=="fv-eastland-214-primary-custody-v1")err("schema");
 if(input.article?.post_id!==214||input.article?.url!=="https://finalvestige.com/2026/08/18/the-lifeboats-never-left-the-deck/")err("article");
 const b=input.baseline||{};
 if(b.historical_posts!==61||b.historical_images!==355||b.reported_broken!==42||b.guest_confirmed_broken!==null||b.claimed_transfer_savings_percent!==76||b.measured_transfer_savings_percent!==null||b.wp_originals_above_1500000_bytes!==16||b.wp_original_stored_bytes!==49107665)err("unsubstantiated_sitewide_claim");
 if(input.release!=="HOLD"||input.site_qa_154_collector_unchanged!==true||input.homepage_untouched!==true)err("release_scope");
 if(!Array.isArray(input.items)||input.items.length!==6)return [...errors,"six_slots_required"];
 const seen=new Set();
 for(let i=0;i<6;i++){
  const im=input.items[i],p=PINNED[i];
  if(!im||typeof im!=="object"){err("missing_item_"+i);continue}
  if(im.slot!==p[0]||im.source_url!==p[1]||im.record_url!==p[2]||seen.has(im.slot))err("source_custody_"+i);
  seen.add(im.slot);
  if(im.source_reader!=="web_open_inaccessible_binary_or_redirect"||im.origin_http_status!==null||im.guest_http_status!==null||im.guest_natural_width!==null||im.encoded_transfer_bytes!==null)err("fabricated_wire_evidence_"+i);
  if(im.exact_binary_identity_verified!==false||im.rights_cleared_for_wp!==false||im.cache_allowed!==false||im.wp_write_allowed!==false||im.disposition!=="HOLD")err("unauthorized_reuse_"+i);
  if(typeof im.rights_evidence!=="string"||im.rights_evidence.length<55||typeof im.visual_review!=="string"||im.visual_review.length<30)err("missing_provenance_"+i);
  const original=im.candidate_original_px||{},out=im.proposed_non_upscale_px||{};
  const w=original.width,h=original.height;
  if(!Number.isInteger(w)||!Number.isInteger(h)||w<=0||h<=0||im.proposed_max_width_px!==960){err("candidate_geometry_"+i);continue}
  const expectW=Math.min(w,960), expectH=Math.round(h*expectW/w);
  if(out.width!==expectW||out.height!==expectH||out.width>w||out.height>h)err("geometry_or_upscale_"+i);
  if(typeof im.archive_candidate!=="string"||!im.archive_candidate.startsWith("https://"))err("catalog_candidate_"+i);
 }
 // Catalog-specific rights and legibility controls:
 if(input.items[1]?.proposed_non_upscale_px?.height!==257)err("panorama_geometry_loss");
 if(input.items[2]?.proposed_non_upscale_px?.width!==475)err("small_original_no_upscale");
 if(!/not proof federal authorship/i.test(input.items[5]?.rights_evidence||""))err("nara_authorship_caveat");
 if(!/1910 date/.test(input.items[4]?.rights_evidence||""))err("loc_date_conflict");
 return errors;
}
module.exports={validate,PINNED};
if(require.main===module){
 const fs=require("node:fs"),path=require("node:path");
 const input=JSON.parse(fs.readFileSync(path.join(__dirname,"eastland_214_primary_crosswalk_20261114.json"),"utf8"));
 const failures=validate(input);
 console.log(JSON.stringify({result:failures.length?"HOLD_INVALID":"HOLD_VALIDATED",slot_count:input.items?.length,errors:failures},null,2));
 process.exitCode=failures.length?1:0;
}
