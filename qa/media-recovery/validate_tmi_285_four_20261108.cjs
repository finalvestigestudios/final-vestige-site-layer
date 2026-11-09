'use strict';
/** Offline, fail-closed verification of frozen TMI non-P0 source audit. No network or WP calls. */
const EXPECTED = Object.freeze({
 "285:0": "https://live.staticflickr.com/7278/7447166686_5d24dff6db_b.jpg",
 "285:1": "https://i0.wp.com/www.squawkpoint.com/wp-content/uploads/2019/02/Three-Mile-Island-Control-Centre.jpg?ssl=1",
 "285:3": "https://i.insider.com/5d5eb5f754c75f23dc72ed4c?auto=webp&format=jpeg&width=800",
 "285:4": "https://images.pixels.com/images-medium-large-5/three-mile-island-damaged-reactor-core-nuclear-regulatory-commissionscience-photo-library.jpg"
});
const FIELDS = Object.freeze(["slot","published_src","alt","web_retriever","archival_candidate","visual_caution","release"]);
const OBS = Object.freeze({"285:0":"TOOL_403_FORBIDDEN","285:1":"RENDERED_VIA_WEB_RETRIEVER","285:3":"RENDERED_VIA_WEB_RETRIEVER","285:4":"RENDERED_VIA_WEB_RETRIEVER"});
const CAUTION = Object.freeze({"285:0":"1979_CREW_SCENE_NOT_AUTHENTICATED","285:1":"JETPACK_THIRD_PARTY_PROXY_NOT_FIRST_PARTY","285:3":"PUBLIC_FIGURES_PICTURED_SCENE_DATE_TO_VERIFY","285:4":"ILLUSTRATION_LABELS_REQUIRE_AT_LEAST_AS_READABLE_AS_ORIGINAL"});
const ALT = Object.freeze({"285:0":"Operators and technical staff inside the Three Mile Island Unit 2 control room during the 1979 accident.","285:1":"Wide view of the densely instrumented Three Mile Island Unit 2 control room.","285:3":"Technical personnel gathered inside the Three Mile Island control room during the 1979 accident response.","285:4":"Reconstruction of the severely damaged Three Mile Island Unit 2 reactor core after the partial meltdown."});
function failIf(condition, why){if(condition) throw Error(why);}
function exactKeys(obj, names, label){
 failIf(!obj||typeof obj!=="object"||Array.isArray(obj),label+":bad_object");
 const got=Object.keys(obj).sort().join("|"), want=[...names].sort().join("|");
 failIf(got!==want,label+":unexpected_keys");
}
function validate(a){
 const errors=[];
 try{
  exactKeys(a,["schema","observed_date_utc","cms","web_method","source_references","rows","aggregate","rights_and_release"],"root");
  failIf(a.schema!=="fv-tmi-285-non-p0-primary-map-20261108-v1","schema");
  failIf(a.observed_date_utc!=="2026-11-09","date");
  exactKeys(a.cms,["method","post_id","title","status","modified","url","total_inline_images","scope"],"cms");
  failIf(a.cms.method!=="wordpress_posts_get_context_edit_read_only"||a.cms.post_id!==285||a.cms.status!=="publish"||a.cms.modified!=="2026-11-02T21:39:59"||a.cms.total_inline_images!==6||a.cms.scope!=="ONLY_SLOTS_0_1_3_4_P0_2_5_SEPARATE","cms");
  failIf(a.cms.url!=="https://finalvestige.com/2026/08/19/the-light-said-closed-three-mile-island/","cms_url");
  failIf(a.cms.title!=="The Light Said Closed","title");
  failIf(a.web_method!=="web.open exact published image URL; tool wrapper/render outcome, not origin HTTP or guest Chrome","method");
  failIf(!Array.isArray(a.source_references)||a.source_references.length!==4||new Set(a.source_references).size!==4||a.source_references.some(u=>typeof u!=="string"||!u.startsWith("https://")),"source_references");
  failIf(!Array.isArray(a.rows)||a.rows.length!==4,"rows_count");
  const visited=new Set();
  for(const r of a.rows){
   exactKeys(r,FIELDS,"row");
   failIf(!Object.hasOwn(EXPECTED,r.slot)||visited.has(r.slot),"slot");
   visited.add(r.slot);
   failIf(r.published_src!==EXPECTED[r.slot]||r.alt!==ALT[r.slot],"source_or_alt");
   failIf(r.release!=="HOLD"||r.visual_caution!==CAUTION[r.slot],"release_or_visual");
   exactKeys(r.web_retriever,["tool","observation","origin_http","guest_http","guest_natural_width","guest_natural_height","guest_wire_bytes"],"retriever");
   failIf(r.web_retriever.tool!=="web.open"||r.web_retriever.observation!==OBS[r.slot],"observation");
   failIf(["origin_http","guest_http","guest_natural_width","guest_natural_height","guest_wire_bytes"].some(k=>r.web_retriever[k]!==null),"fabricated_network_or_browser_evidence");
   const c=r.archival_candidate;
   if(r.slot==="285:4"){
    exactKeys(c,["official_catalog_url","commons_catalog_url","relationship","rights","native_dimensions","conditional_max_width_960"],"nrc_candidate");
    failIf(c.official_catalog_url!=="https://www.nrc.gov/education-regulatory-research/research/state-of-the-art-reactor-consequence-analyses-soarca/frequently-asked-questions"||c.commons_catalog_url!=="https://commons.wikimedia.org/wiki/File:Graphic_TMI-2_Core_End-State_Configuration.png","catalog_identity");
    failIf(c.relationship!=="SAME_NRC_SCIENTIFIC_FIGURE_BINARY_CROP_AND_TEXT_NOT_VERIFIED"||c.rights!=="CATALOG_ASSERTS_PD_USGOV_NRC_DERIVATIVE_REVIEW","rights_identity");
    failIf(JSON.stringify(c.native_dimensions)!==JSON.stringify([1772,2623])||JSON.stringify(c.conditional_max_width_960)!==JSON.stringify([960,1421]),"native_or_960_geometry");
   }else{
    exactKeys(c,["official_catalog_url","relationship","rights","native_dimensions","conditional_max_width_960"],"unmapped_candidate");
    failIf(c.official_catalog_url!==null||c.relationship!=="NO_VERIFIED_SAME_IMAGE_PRIMARY_CATALOG"||c.rights!=="UNKNOWN"||c.native_dimensions!==null||c.conditional_max_width_960!==null,"invented_replacement");
   }
  }
  failIf(visited.size!==4,"coverage");
  exactKeys(a.aggregate,["source_slots","rendered_by_web_retriever","tool_forbidden","confirmed_visitor_broken","confirmed_wire_bytes","sitewide_76_percent_savings_verified","reported_42_broken_verified"],"aggregate");
  failIf(a.aggregate.source_slots!==4||a.aggregate.rendered_by_web_retriever!==3||a.aggregate.tool_forbidden!==1||a.aggregate.confirmed_visitor_broken!==null||a.aggregate.confirmed_wire_bytes!==null||a.aggregate.sitewide_76_percent_savings_verified!==false||a.aggregate.reported_42_broken_verified!==false,"fabricated_aggregate");
  exactKeys(a.rights_and_release,["all_replacements_hold","third_party_binary_downloads","word_press_writes","home_edits","spend_usd","no_scraping"],"release");
  failIf(a.rights_and_release.all_replacements_hold!==true||a.rights_and_release.third_party_binary_downloads!==0||a.rights_and_release.word_press_writes!==0||a.rights_and_release.home_edits!==0||a.rights_and_release.spend_usd!==0||a.rights_and_release.no_scraping!==true,"unauthorized_release");
 }catch(e){errors.push(String(e.message||e))}
 return {valid:errors.length===0,errors};
}
module.exports={validate};
if(require.main===module){
 const fs=require("node:fs");
 const r=validate(JSON.parse(fs.readFileSync(process.argv[2],"utf8")));
 console.log(JSON.stringify(r)); if(!r.valid) process.exitCode=1;
}
