'use strict';
const PINNED=[
  {
    "slot": "218:0",
    "url": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Glomar_Manganese_Nodule_Encased_in_Lucite.jpg?width=1280",
    "alt": "Manganese nodule recovered from the Pacific by the Glomar Explorer and preserved in Lucite by the CIA Museum.",
    "catalog": "https://commons.wikimedia.org/wiki/File:Glomar_Manganese_Nodule_Encased_in_Lucite.jpg",
    "primary": "https://www.cia.gov/legacy/museum/artifact/manganese-nodule-encased-in-lucite/",
    "pixels": [
      800,
      533
    ],
    "bytes": 9281
  },
  {
    "slot": "218:1",
    "url": "https://commons.wikimedia.org/wiki/Special:Redirect/file/USNS_Glomar_Explorer_(T-AG-193).jpg?width=1280",
    "alt": "Hughes Glomar Explorer at sea, the vessel secretly built for Project AZORIAN.",
    "catalog": "https://commons.wikimedia.org/wiki/File:USNS_Glomar_Explorer_(T-AG-193).jpg",
    "primary": "https://www.cia.gov/legacy/museum/exhibit/project-azorian/",
    "pixels": [
      1280,
      833
    ],
    "bytes": 563931
  },
  {
    "slot": "218:2",
    "url": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Glomar_Patch.jpg?width=1280",
    "alt": "Hughes Glomar Explorer crew patch bearing the Summa Corporation name used during Project AZORIAN.",
    "catalog": "https://commons.wikimedia.org/wiki/File:Glomar_Patch.jpg",
    "primary": "https://www.cia.gov/legacy/museum/artifact/glomar-explorer-crew-patch/",
    "pixels": [
      800,
      533
    ],
    "bytes": 26721
  },
  {
    "slot": "218:3",
    "url": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Model_of_the_sunken_and_deteriorated_K-129_submarine_was_created_by_the_CIA_during_the_AZORIAN_mission_that_has_never_been_displayed_before_at_the_CIA_Museum_in_2022.jpg?width=1280",
    "alt": "CIA model of the wrecked Soviet submarine K-129 created during Project AZORIAN.",
    "catalog": "https://commons.wikimedia.org/wiki/File:Model_of_the_sunken_and_deteriorated_K-129_submarine_was_created_by_the_CIA_during_the_AZORIAN_mission_that_has_never_been_displayed_before_at_the_CIA_Museum_in_2022.jpg",
    "primary": "https://www.cia.gov/legacy/museum/exhibit/project-azorian/",
    "pixels": [
      3598,
      2400
    ],
    "bytes": 5740268
  },
  {
    "slot": "218:4",
    "url": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Painting-of-AZORIAN-mission-approved.jpg?width=1280",
    "alt": "Project AZORIAN lead engineer Sherman Wetmore looking at a painting of Glomar Explorer raising K-129 during a 2022 CIA Museum visit.",
    "catalog": "https://commons.wikimedia.org/wiki/File:Painting-of-AZORIAN-mission-approved.jpg",
    "primary": "https://www.cia.gov/stories/story/honoring-the-mission-of-project-azorian/",
    "pixels": [
      800,
      709
    ],
    "bytes": 31376
  },
  {
    "slot": "218:5",
    "url": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Hughes_Glomar_Explorer_coveralls_and_ashtray_are_examples_of_the_depth_of_cover_that_CIA_and_Hughes_manufactured_for_the_expedition_and_these_artifacts_have_never_been_displayed_before_at_the_CIA_Museum_in_2022.jpg?width=1280",
    "alt": "Glomar Explorer coveralls and ashtray created as part of the Hughes and Summa Corporation cover identity for Project AZORIAN.",
    "catalog": "https://commons.wikimedia.org/wiki/File:Hughes_Glomar_Explorer_coveralls_and_ashtray_are_examples_of_the_depth_of_cover_that_CIA_and_Hughes_manufactured_for_the_expedition_and_these_artifacts_have_never_been_displayed_before_at_the_CIA_Museum_in_2022.jpg",
    "primary": "https://www.cia.gov/stories/story/honoring-the-mission-of-project-azorian/",
    "pixels": [
      2400,
      3598
    ],
    "bytes": 5171994
  }
];
function validate(a){
const e=[];
if(!a||a.schema!=="fv-media-azorian-six-v1")return ["schema mismatch"];
if(a.audit_date_utc!=="2026-11-09"||a.frozen_corpus_date!=="2026-10-30"||a.fixture?.blob_sha!=="0f3dfe398a76838049cebba7cb773d5c5a0c8c69")e.push("fixture/date mismatch");
if(a.post?.id!==218||a.post?.url!=="https://finalvestige.com/2026/08/18/the-rock-had-to-be-real/"||a.site_qa_owner_pr!==154||a.media_engineering_pr!==1703)e.push("post/PR ownership mismatch");
const c=a.census||{},s=a.retrieval_summary||{};
if(c.posts!==61||c.images!==355||c.external_slots!==288||c.reported_broken!==42||c.visitor_confirmed_broken!==0||c.transfer_76_pct_measured!==false||c.wp_oversized_originals!==15||c.wp_oversized_stored_original_bytes!==47096779)e.push("unverified performance claim");
if(s.exact_stored_urls_queried!==6||s.inaccessible_by_tool!==6||s.actual_browser_http_observations!==0)e.push("retriever claim mismatch");
if(!Array.isArray(a.rows)||a.rows.length!==6)return [...e,"row count"];
const seen=new Set();
for(let i=0;i<6;i++){
const r=a.rows[i],p=PINNED[i];if(!r||r.slot!==p.slot||r.post_id!==218||seen.has(r.slot)||r.original_url!==p.url||r.original_alt!==p.alt){e.push("frozen source mismatch "+i);continue}seen.add(r.slot);
const cat=r.catalog||{},t=r.retriever||{},v=r.visitor||{},st=r.stage||{},rel=r.release||{};
if(cat.url!==p.catalog||cat.source_primary_url!==p.primary||cat.html_catalog_verified!==true||JSON.stringify(cat.catalog_native_dimensions_px)!==JSON.stringify(p.pixels)||cat.catalog_original_bytes!==p.bytes||cat.license_observation!=="COMMONS_CLAIMS_US_GOVERNMENT_PD_NOT_FINAL_CLEARANCE"||cat.exact_published_binary_match_verified!==false)e.push("catalog changed "+i);
if(t.method!=="web.open_literal_source_redirect"||t.observation!=="TOOL_URL_NOT_ACCESSIBLE"||t.actual_origin_http!==null)e.push("fabricated origin result "+i);
for(const key of ["http_status","current_src","encoded_transfer_bytes","mime","natural_dimensions_px","cached","confirmed_broken"])if(v[key]!==null)e.push("fabricated browser evidence "+i+":"+key);
const w=Math.min(960,p.pixels[0]),h=Math.round(p.pixels[1]*w/p.pixels[0]);
if(st.max_width_px!==960||JSON.stringify(st.conditional_catalog_px)!==JSON.stringify([w,h])||st.no_upscale!==true||st.actual_derivative_created!==false||st.verified_binary_identity!==false||st.rights_cleared!==false)e.push("stage evidence/size invalid "+i);
for(const key of ["download","cache","upload_wp","rewrite_blocks","deploy"])if(rel[key]!==false)e.push("unapproved release "+i+":"+key);
if(typeof r.historic_visual_integrity!=="string"||r.historic_visual_integrity.length<25||typeof r.rights_review_required!=="string"||r.rights_review_required.length<25)e.push("lost rights/scene "+i);
}
return e;
}
module.exports={validate};
if(require.main===module){const data=require('./azorian_218_six_source_20261109.json');const result=validate(data);if(result.length){console.error(result);process.exitCode=1}else console.log('6/6 source rows PASS')}
