'use strict';
/** Offline, read-only source custody and release safety checker. No fetching or WordPress calls. */
const EXPECTED={
  "367:1": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Operation_Chrome_Dome_route.jpg?width=1280",
  "367:2": "https://commons.wikimedia.org/wiki/Special:Redirect/file/USS_Skill_(MSO-471)_operating_off_the_coast_of_Spain%2C_in_February_1966_(428-NPC-36556).jpg?width=1280",
  "367:3": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Zoeken_naar_H_bom_in_Spanje%2C_de_Alvin_wordt_te_water_gelaten%2C_Bestanddeelnr_918-8161.jpg?width=1280",
  "367:4": "https://navalunderseamuseum.org/wp-content/uploads/2016/03/CURV-I-H-Bomb-Recovery-300x243.jpg",
  "367:5": "https://commons.wikimedia.org/wiki/Special:Redirect/file/428-GX-_USN_118930_(26941557635).jpg?width=1280",
  "367:6": "https://commons.wikimedia.org/wiki/Special:Redirect/file/1966_Palomares_B-52_crash_-_recovered_H-bomb.jpg?width=1280",
  "367:7": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Palomares_barrels.jpg?width=1280",
  "367:8": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Recovered_Mk_28RI_bomb.JPG?width=1280"
};
const CATALOGS={
  "367:1": "https://commons.wikimedia.org/wiki/File:Operation_Chrome_Dome_route.jpg",
  "367:2": "https://commons.wikimedia.org/wiki/File:USS_Skill_(MSO-471)_operating_off_the_coast_of_Spain,_in_February_1966_(428-NPC-36556).jpg",
  "367:3": "https://commons.wikimedia.org/wiki/File:Zoeken_naar_H_bom_in_Spanje,_de_Alvin_wordt_te_water_gelaten,_Bestanddeelnr_918-8161.jpg",
  "367:4": "https://navalunderseamuseum.org/petrel-helmet/",
  "367:5": "https://commons.wikimedia.org/wiki/File:428-GX-_USN_118930_(26941557635).jpg",
  "367:6": "https://commons.wikimedia.org/wiki/File:1966_Palomares_B-52_crash_-_recovered_H-bomb.jpg",
  "367:7": "https://commons.wikimedia.org/wiki/File:Palomares_barrels.jpg",
  "367:8": "https://commons.wikimedia.org/wiki/File:Recovered_Mk_28RI_bomb.JPG"
};
const RIGHTS={
  "367:1": "CC_BY_SA_2_5",
  "367:2": "US_NAVY_PD_CLAIM_NARA_85011",
  "367:3": "CC0_1_0_ARCHIVES_NL_918_8161",
  "367:4": "RIGHTS_UNVERIFIED",
  "367:5": "US_NAVY_PD_CLAIM",
  "367:6": "US_NAVY_PD_CLAIM_WITH_CROP",
  "367:7": "US_AIR_FORCE_PD_CLAIM_THIRD_PARTY_ORIGIN",
  "367:8": "US_NAVY_PD_CLAIM"
};
const DIMENSIONS={
  "367:1": [
    1475,
    923
  ],
  "367:2": [
    1227,
    898
  ],
  "367:3": [
    3440,
    2453
  ],
  "367:4": null,
  "367:5": [
    1854,
    2464
  ],
  "367:6": [
    662,
    374
  ],
  "367:7": [
    500,
    252
  ],
  "367:8": [
    617,
    461
  ]
};
const isInt=x=>Number.isInteger(x)&&x>0;
function validate(a){
  const errors=[],bad=(v,label)=>{if(!v)errors.push(label)};
  bad(a?.schema==='fv-palomares-eight-source-recovery-v1','schema');
  bad(a?.source_custody?.post_id===367&&a?.source_custody?.image_tags===9&&a?.source_custody?.external_image_slots===8,'post custody');
  bad(a?.source_custody?.last_modified==='2026-10-29T17:34:27'&&a?.source_custody?.status==='publish'&&a?.source_custody?.live_exact_src_match_frozen===true,'readback');
  bad(a?.source_custody?.frozen_source_blob_sha==='48e1ebf07207e948ba5802e714eb39659d2e1c1d','frozen provenance');
  bad(a?.counts?.external_urls===8&&a?.counts?.tool_url_not_accessible===7&&a?.counts?.tool_rendered===1,'wrapper counts');
  bad(a?.counts?.visitor_broken_confirmed===null&&a?.counts?.observed_image_transfer_bytes===null&&a?.counts?.reported_42_broken_verified===false&&a?.counts?.claimed_76_percent_weight_saving_measured===false,'unsupported claim');
  bad(a?.counts?.wordPress_originals_over_1_5_decimal_mb===15&&a?.counts?.oversize_storage_bytes===47096779,'stored threshold');
  bad(a?.release?.all_on_hold===true&&a?.release?.external_binary_downloads===0&&a?.release?.cache_writes===0&&a?.release?.wordpress_writes===0&&a?.release?.homepage_changes===0&&a?.release?.spend_usd===0,'release');
  bad(typeof a?.cache_wp_plan==='string'&&a.cache_wp_plan.startsWith('HOLD:'),'cache plan');
  bad(Array.isArray(a?.rows)&&a.rows.length===8,'rows');
  const seen=new Set();
  for(const r of a?.rows||[]){
    if(!r||typeof r!=='object'){errors.push('row type');continue;}
    const k=r.slot;bad(!seen.has(k),'duplicate '+k);seen.add(k);
    bad(Object.hasOwn(EXPECTED,k),'unknown slot '+k);
    bad(r.post_id===367&&r.exact_live_wp_src===EXPECTED[k],'wrong live src '+k);
    bad(r.source_catalog===CATALOGS[k],'catalog identity '+k);
    bad(r.rights_classification===RIGHTS[k]&&typeof r.rights_observation==='string'&&r.rights_observation.length>25,'rights '+k);
    bad(r.source_identity_relation==='SAME_ARCHIVAL_FILE_TITLE_BUT_RENDERED_BINARY_UNVERIFIED','identity '+k);
    const expected=DIMENSIONS[k],actual=r.original_catalog_px,out=r.conditional_max_width_960_px;
    if(expected===null){bad(actual===null&&out===null,'unknown size '+k);}
    else {bad(Array.isArray(actual)&&JSON.stringify(actual)===JSON.stringify(expected),'native dims '+k);
      const w=Math.min(960,expected[0]),h=Math.round(expected[1]*w/expected[0]);
      bad(Array.isArray(out)&&out[0]===w&&out[1]===h,'proportional cap '+k);}
    bad(r.no_upscale===true&&r.binary_sha256===null&&r.rights_final_clearance===false&&r.editor_approved===false,'release proof '+k);
    bad(r.cache_authorized===false&&r.wp_media_authorized===false&&r.wp_post_authorized===false,'forbidden publication '+k);
    const p=r.retriever||{},outcome=k==='367:4'?'IMAGE_RENDERED':'URL_NOT_ACCESSIBLE_VIA_TOOL';
    bad(p.method==='web.open'&&p.outcome===outcome&&p.date_local==='2026-11-08','tool outcome '+k);
    for(const f of ['wrapper_http_status','origin_http_status','guest_browser_http_status','guest_current_src','guest_natural_px','guest_transfer_bytes','guest_broken'])bad(p[f]===null,'invented status '+k+':'+f);
  }
  bad(seen.size===8&&Object.keys(EXPECTED).every(x=>seen.has(x)),'source coverage');
  return {ok:errors.length===0,errors,rows:seen.size};
}
module.exports={validate};
