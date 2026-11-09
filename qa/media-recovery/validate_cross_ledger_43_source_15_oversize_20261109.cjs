'use strict';
// Offline read-only evidence normalization gate; no HTTP, no image downloads, no WP writes.
const EXPECTED={
  "counts": {
    "source_rows": 43,
    "p0": 6,
    "oversize": 15,
    "stored_bytes": 47096779,
    "matched": 11,
    "inline_bytes": 38480915
  },
  "group_blobs": {
    "p0": "04df35ce25f99626c7b754c1d7eed0f3f006e3f4",
    "florida": "c0ec93d75ff6c7d1b655ea1ea1b42bc9c429106f",
    "navy": "0fe22f816dce9776d447b3ddfc7d7aeeb75ccad0",
    "palomares": "cb9f50e2410a8773bf282732e12cac5fe77251cf",
    "archimedes": "f3c9a13c290c15d3b21f8a75656ed807dab058cc",
    "tmi": "3b24bedaca914217c02e4d152d4f0822bbeb90ec"
  },
  "urls": {
    "285:5": "https://images.saymedia-content.com/.image/ar_16:9,c_fill,cs_srgb,fl_progressive,q_auto:eco,w_1200/MTg5ODU1MTM1NjYzNDAwNjM2/the-china-syndrome-blockbuster-movie-becomes-eerie-prophecy.jpg",
    "285:2": "https://blog.ucsusa.org/wp-content/uploads/2022/10/DBD-42-Figure-4-tmi-panel.jpg",
    "287:5": "https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg",
    "418:1": "https://media.defense.gov/2021/Mar/30/2002610812/1920/1080/0/210330-G-DE713-0002.JPG",
    "418:2": "https://www.history.uscg.mil/Portals/6/5_%20Scotch_Cap_debris2_1946.jpg",
    "407:1": "https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/img7535.jpg",
    "432:0": "https://www.floridamemory.com/fpc/prints/pr04493.jpg",
    "432:1": "https://www.floridamemory.com/fpc/reference/rc17068.jpg",
    "432:2": "https://www.floridamemory.com/fpc/reference/rc10673.jpg",
    "432:3": "https://www.floridamemory.com/fpc/general/n031889.jpg",
    "432:4": "https://www.floridamemory.com/fpc/reference/rc04344.jpg",
    "432:5": "https://www.floridamemory.com/fpc/reference/rc07668.jpg",
    "432:6": "https://www.floridamemory.com/fpc/msf/MSF-PB11548-001.jpg",
    "280:0": "https://www.history.navy.mil/content/history/museums/nmusn/explore/photography/ships-us/ships-usn-p/uss-pueblo-ager-2/428-gx-usn-1129207/_jcr_content/mediaitem/image.img.jpg/1504112093611.jpg",
    "280:1": "https://www.history.navy.mil/content/history/nhhc/research/histories/ship-histories/danfs/p/pueblo-iii/_jcr_content/body/media_asset_1086930325/image.img.jpg/1514467381634.jpg",
    "280:2": "https://www.history.navy.mil/bin/imageDownload?image=%2Fcontent%2Fdam%2Fnhhc%2Four-collections%2Fphotography%2Fimages%2FNH+75000%2FNH+75561&rendition=cq5dam.web.1280.1280.jpeg",
    "280:3": "https://www.history.navy.mil/content/history/nhhc/our-collections/photography/numerical-list-of-images/nara-series/80-g-k/80-G-K-60000/K-64683/_jcr_content/mediaitem/image.img.jpg/1459314791691.jpg",
    "280:4": "https://www.history.navy.mil/content/history/nhhc/research/histories/ship-histories/danfs/b/banner-ii/_jcr_content/body/media_asset/image.img.jpg",
    "280:5": "https://www.history.navy.mil/content/history/nhhc/our-collections/photography/numerical-list-of-images/nara-series/80-g-k/80-G-K-60000/K-64728/_jcr_content/mediaitem/image.img.jpg/1424360116159.jpg",
    "288:0": "https://www.history.navy.mil/content/history/nhhc/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-69000/NH-69586/_jcr_content/mediaitem/image.img.jpg/1438378291110.jpg",
    "288:2": "https://www.history.navy.mil/content/history/nhhc/our-collections/photography/technology/communications/radio/ug-21--us-naval-california-radio-station-collection/mare-island-naval-radio-station/ug-21-01-02-mare-island-naval-radio/jcr%3Acontent/mediaitem/image.img.jpg/1564510769845.jpg",
    "367:1": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Operation_Chrome_Dome_route.jpg?width=1280",
    "367:2": "https://commons.wikimedia.org/wiki/Special:Redirect/file/USS_Skill_(MSO-471)_operating_off_the_coast_of_Spain%2C_in_February_1966_(428-NPC-36556).jpg?width=1280",
    "367:3": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Zoeken_naar_H_bom_in_Spanje%2C_de_Alvin_wordt_te_water_gelaten%2C_Bestanddeelnr_918-8161.jpg?width=1280",
    "367:4": "https://navalunderseamuseum.org/wp-content/uploads/2016/03/CURV-I-H-Bomb-Recovery-300x243.jpg",
    "367:5": "https://commons.wikimedia.org/wiki/Special:Redirect/file/428-GX-_USN_118930_(26941557635).jpg?width=1280",
    "367:6": "https://commons.wikimedia.org/wiki/Special:Redirect/file/1966_Palomares_B-52_crash_-_recovered_H-bomb.jpg?width=1280",
    "367:7": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Palomares_barrels.jpg?width=1280",
    "367:8": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Recovered_Mk_28RI_bomb.JPG?width=1280",
    "268:0": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Archimedes%20Palimpsest.jpg?width=1280",
    "268:1": "https://archimedespalimpsest.org/assets/img/imaging_x8.jpg",
    "268:2": "https://commons.wikimedia.org/wiki/Special:Redirect/file/002r-001v%20Arch13r%20Sinar%20uvblue%20norm8%20Euchologion%20up%20%289737603804%29.jpg?width=960",
    "268:3": "https://commons.wikimedia.org/wiki/Special:Redirect/file/017r-016v%20Heiberg-UV-blue%20%289737623542%29.jpg?width=960",
    "268:4": "https://www.archimedespalimpsest.org/assets/img/imagecapture-capture2b.jpg",
    "268:5": "https://commons.wikimedia.org/wiki/Special:Redirect/file/017r-016v%20Arch07r%20Sinar%20pseudo%20no-veil%20%289734386225%29.jpg?width=960",
    "268:6": "https://commons.wikimedia.org/wiki/Special:Redirect/file/028v-021r%20Arch08r%20XRF%20FeFront%20registered%20%289734104759%29.jpg?width=1280",
    "268:7": "https://archimedespalimpsest.org/assets/img/imaging_x12.jpg",
    "268:8": "https://archimedespalimpsest.org/assets/img/imaging_x9.jpg",
    "268:9": "https://commons.wikimedia.org/wiki/Special:Redirect/file/176r-173v%20Hype03r%20Sinar%20LED445-735%20pseudo%20%289734660151%29.jpg?width=960",
    "285:0": "https://live.staticflickr.com/7278/7447166686_5d24dff6db_b.jpg",
    "285:1": "https://i0.wp.com/www.squawkpoint.com/wp-content/uploads/2019/02/Three-Mile-Island-Control-Centre.jpg?ssl=1",
    "285:3": "https://i.insider.com/5d5eb5f754c75f23dc72ed4c?auto=webp&format=jpeg&width=800",
    "285:4": "https://images.pixels.com/images-medium-large-5/three-mile-island-damaged-reactor-core-nuclear-regulatory-commissionscience-photo-library.jpg"
  },
  "candidates": {
    "285:5": "https://commons.wikimedia.org/wiki/File:Three_mile_island_062010.jpg",
    "285:2": "https://blog.ucs.org/wp-content/uploads/2022/10/DBD-42-Figure-4-tmi-panel.jpg",
    "287:5": "https://media.stpetecatalyst.com/uploads/2020/04/Skyway-Bridge-documentary.jpg",
    "418:1": "https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/",
    "418:2": "https://www.lighthousefriends.com/Scotch_Cap_debris2_1946.jpg",
    "407:1": "https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/thumbnails/image/img7535.jpg",
    "432:0": "https://floridamemory.com/items/show/4144",
    "432:1": "https://floridamemory.com/items/show/38362",
    "432:2": "https://floridamemory.com/items/show/33289",
    "432:3": "https://floridamemory.com/items/show/141398",
    "432:4": "https://floridamemory.com/items/show/27848",
    "432:5": "https://floridamemory.com/items/show/30741",
    "432:6": "https://floridamemory.com/items/show/340182",
    "280:0": "https://www.history.navy.mil/content/history/museums/nmusn/explore/photography/ships-us/ships-usn-p/uss-pueblo-ager-2/428-gx-usn-1129207.html",
    "280:1": "https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-75000/NH-75559.html",
    "280:2": "https://www.history.navy.mil/content/history/nhhc/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-75000/NH-75561.html",
    "280:3": "https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nara-series/80-g-k/80-G-K-60000/K-64683.html",
    "280:4": null,
    "280:5": "https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nara-series/80-g-k/80-G-K-60000/K-64728.html",
    "288:0": "https://www.history.navy.mil/content/history/nhhc/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-69000/NH-69586.html",
    "288:2": null,
    "367:1": "https://commons.wikimedia.org/wiki/File:Operation_Chrome_Dome_route.jpg",
    "367:2": "https://commons.wikimedia.org/wiki/File:USS_Skill_(MSO-471)_operating_off_the_coast_of_Spain,_in_February_1966_(428-NPC-36556).jpg",
    "367:3": "https://commons.wikimedia.org/wiki/File:Zoeken_naar_H_bom_in_Spanje,_de_Alvin_wordt_te_water_gelaten,_Bestanddeelnr_918-8161.jpg",
    "367:4": "https://navalunderseamuseum.org/petrel-helmet/",
    "367:5": "https://commons.wikimedia.org/wiki/File:428-GX-_USN_118930_(26941557635).jpg",
    "367:6": "https://commons.wikimedia.org/wiki/File:1966_Palomares_B-52_crash_-_recovered_H-bomb.jpg",
    "367:7": "https://commons.wikimedia.org/wiki/File:Palomares_barrels.jpg",
    "367:8": "https://commons.wikimedia.org/wiki/File:Recovered_Mk_28RI_bomb.JPG",
    "268:0": "https://commons.wikimedia.org/wiki/File:Archimedes_Palimpsest.jpg",
    "268:1": "https://www.archimedespalimpsest.org/about/imaging/capture.php",
    "268:2": "https://commons.wikimedia.org/wiki/File:002r-001v_Arch13r_Sinar_uvblue_norm8_Euchologion_up_(9737603804).jpg",
    "268:3": "https://commons.wikimedia.org/wiki/File:017r-016v_Heiberg-UV-blue_(9737623542).jpg",
    "268:4": "https://www.archimedespalimpsest.org/about/imaging/capture.php",
    "268:5": "https://commons.wikimedia.org/wiki/File:017r-016v_Arch07r_Sinar_pseudo_no-veil_(9734386225).jpg",
    "268:6": "https://commons.wikimedia.org/wiki/File:028v-021r_Arch08r_XRF_FeFront_registered_(9734104759).jpg",
    "268:7": "https://www.archimedespalimpsest.org/about/imaging/capture.php",
    "268:8": "https://www.archimedespalimpsest.org/about/imaging/capture.php",
    "268:9": "https://commons.wikimedia.org/wiki/File:176r-173v_Hype03r_Sinar_LED445-735_pseudo_(9734660151).jpg",
    "285:0": null,
    "285:1": null,
    "285:3": null,
    "285:4": "https://www.nrc.gov/education-regulatory-research/research/state-of-the-art-reactor-consequence-analyses-soarca/frequently-asked-questions"
  },
  "wrap": {
    "285:5": [
      "NOT_FOUND",
      404
    ],
    "285:2": [
      "REDIRECT_TARGET_INACCESSIBLE",
      500
    ],
    "287:5": [
      "NOT_FOUND",
      404
    ],
    "418:1": [
      "FORBIDDEN",
      403
    ],
    "418:2": [
      "FORBIDDEN",
      403
    ],
    "407:1": [
      "UNSUPPORTED_OCTET_STREAM",
      400
    ],
    "432:0": [
      "REDIRECT_TARGET_INACCESSIBLE",
      500
    ],
    "432:1": [
      "REDIRECT_TARGET_INACCESSIBLE",
      500
    ],
    "432:2": [
      "REDIRECT_TARGET_INACCESSIBLE",
      500
    ],
    "432:3": [
      "REDIRECT_TARGET_INACCESSIBLE",
      500
    ],
    "432:4": [
      "REDIRECT_TARGET_INACCESSIBLE",
      500
    ],
    "432:5": [
      "REDIRECT_TARGET_INACCESSIBLE",
      500
    ],
    "432:6": [
      "REDIRECT_TARGET_INACCESSIBLE",
      500
    ],
    "280:0": [
      "TIMEOUT_FETCHING",
      400
    ],
    "280:1": [
      "TIMEOUT_FETCHING",
      400
    ],
    "280:2": [
      "TIMEOUT_FETCHING",
      400
    ],
    "280:3": [
      "TIMEOUT_FETCHING",
      400
    ],
    "280:4": [
      "NOT_ACCESSIBLE_IN_TOOL",
      null
    ],
    "280:5": [
      "TIMEOUT_FETCHING",
      400
    ],
    "288:0": [
      "BAD_GATEWAY",
      502
    ],
    "288:2": [
      "BAD_GATEWAY",
      502
    ],
    "367:1": [
      "URL_NOT_ACCESSIBLE_VIA_TOOL",
      null
    ],
    "367:2": [
      "URL_NOT_ACCESSIBLE_VIA_TOOL",
      null
    ],
    "367:3": [
      "URL_NOT_ACCESSIBLE_VIA_TOOL",
      null
    ],
    "367:4": [
      "IMAGE_RENDERED",
      null
    ],
    "367:5": [
      "URL_NOT_ACCESSIBLE_VIA_TOOL",
      null
    ],
    "367:6": [
      "URL_NOT_ACCESSIBLE_VIA_TOOL",
      null
    ],
    "367:7": [
      "URL_NOT_ACCESSIBLE_VIA_TOOL",
      null
    ],
    "367:8": [
      "URL_NOT_ACCESSIBLE_VIA_TOOL",
      null
    ],
    "268:0": [
      "TOOL_INACCESSIBLE",
      null
    ],
    "268:1": [
      "WRAPPER_403",
      null
    ],
    "268:2": [
      "TOOL_INACCESSIBLE",
      null
    ],
    "268:3": [
      "TOOL_INACCESSIBLE",
      null
    ],
    "268:4": [
      "WRAPPER_403",
      null
    ],
    "268:5": [
      "TOOL_INACCESSIBLE",
      null
    ],
    "268:6": [
      "TOOL_INACCESSIBLE",
      null
    ],
    "268:7": [
      "WRAPPER_403",
      null
    ],
    "268:8": [
      "TOOL_INACCESSIBLE",
      null
    ],
    "268:9": [
      "TOOL_INACCESSIBLE",
      null
    ],
    "285:0": [
      "TOOL_403_FORBIDDEN",
      null
    ],
    "285:1": [
      "RENDERED_VIA_WEB_RETRIEVER",
      null
    ],
    "285:3": [
      "RENDERED_VIA_WEB_RETRIEVER",
      null
    ],
    "285:4": [
      "RENDERED_VIA_WEB_RETRIEVER",
      null
    ]
  },
  "oversize_urls": {
    "39": "https://finalvestige.com/wp-content/uploads/2026/08/bceca0bd-a16f-44f7-be08-16376fbf08ca.png",
    "40": "https://finalvestige.com/wp-content/uploads/2026/08/377e08da-e121-4f57-9174-1548343402b3.png",
    "41": "https://finalvestige.com/wp-content/uploads/2026/08/a44f673d-a8a8-4c83-9f29-7e24dd55156b.png",
    "42": "https://finalvestige.com/wp-content/uploads/2026/08/c1237ffd-4a47-4988-8254-e3b021069e72.png",
    "43": "https://finalvestige.com/wp-content/uploads/2026/08/01340c2e-1165-4ca0-aa96-87398a83d13a.png",
    "293": "https://finalvestige.com/wp-content/uploads/2026/08/ne.png",
    "382": "https://finalvestige.com/wp-content/uploads/2026/08/vasa-med-gamla-och-nya-stottor_vasa-with-old-and-new-supports.jpg",
    "388": "https://finalvestige.com/wp-content/uploads/2026/08/vasa-modell-2020.jpg",
    "389": "https://finalvestige.com/wp-content/uploads/2026/08/vasa-01-2020.jpg",
    "405": "https://finalvestige.com/wp-content/uploads/2026/08/The20Water20Resilience20Field20Manual.png",
    "482": "https://finalvestige.com/wp-content/uploads/2026/08/050e21e0-7b54-4f9a-ba0b-7f594657af05.png",
    "1257": "https://finalvestige.com/wp-content/uploads/2026/08/edit-017-v01-malbone-tunnel-generalpunger-original.jpg",
    "1258": "https://finalvestige.com/wp-content/uploads/2026/08/edit-017-v02-nypl-5003296-original.jpg",
    "1714": "https://finalvestige.com/wp-content/uploads/2026/10/halifax-explosion-map.png",
    "2148": "https://finalvestige.com/wp-content/uploads/2026/11/1927-caernarvon-levee-explosion-noaa-archive.jpg"
  }
};
function validate(doc,expect){
 const errors=[]; const bad=(message)=>errors.push(message);
 if(!doc||typeof doc!=="object"||Array.isArray(doc))return {pass:false,errors:["bad_document"]};
 const keys=Object.keys(doc).sort().join(",");
 if(keys!==["schema","assembled_utc_date","scope","source_groups","historical_inventory","expanded_inventory","counts","statistics","source_rows","oversized_media_rows","browser_handoff","policy"].sort().join(","))bad("root_keys");
 if(doc.schema!=="fv-cross-ledger-image-triage-v1")bad("schema");
 if(!Array.isArray(doc.source_groups)||doc.source_groups.length!==6)bad("source_groups");
 else {
  for(const g of doc.source_groups) if(expect.group_blobs[g.batch]!==g.source_blob_sha || !/^[0-9a-f]{40}$/.test(g.source_blob_sha))bad("source_ledger_sha:"+g.batch);
 }
 if(!Array.isArray(doc.source_rows)||doc.source_rows.length!==expect.counts.source_rows)bad("source_rows_count");
 else {
 const slots=new Set(); let p0=0; 
 for(const r of doc.source_rows){
  if(!r||typeof r!=="object"){bad("invalid_row");continue;}
  if(Object.keys(r).sort().join(",")!==["slot","post_id","batch","priority","stored_source_url","source_scope","retriever","candidate","release","source_ledger"].sort().join(","))bad("row_keys:"+r.slot);
  if(!/^\d+:\d+$/.test(r.slot)||slots.has(r.slot))bad("duplicate_or_invalid_slot:"+r.slot);
  slots.add(r.slot);
  if(expect.urls[r.slot]!==r.stored_source_url|| !/^https:\/\//.test(r.stored_source_url))bad("original_url:"+r.slot);
  if(parseInt(r.slot,10)!==r.post_id)bad("post_mismatch:"+r.slot);
  if(expect.group_blobs[r.batch]!==r.source_ledger?.blob_sha || !r.source_ledger?.path?.startsWith("qa/media-recovery/"))bad("blob_provenance:"+r.slot);
  if(r.priority!==(r.batch==="p0"?"P0":"P1"))bad("priority:"+r.slot);
  if(r.priority==="P0")p0++;
  const ret=r.retriever;
  if(!ret||ret.method!=="EXTERNAL_WEB_RETRIEVER_NOT_GUEST"||[ret.origin_http,ret.guest_http,ret.guest_decoded_px,ret.guest_wire_bytes,ret.visitor_broken].some(x=>x!==null))bad("fabricated_browser_status:"+r.slot);
  if(JSON.stringify([ret.result,ret.wrapper_code])!==JSON.stringify(expect.wrap[r.slot]))bad("wrapper_provenance:"+r.slot);
  const c=r.candidate;
  if(!c||c.catalog_url!==expect.candidates[r.slot]||c.exact_binary_match!==false||c.item_rights_cleared!==false||c.visual_signoff!==false)bad("candidate_approval:"+r.slot);
  if(c?.conditional_960px!==null){
   const a=c.conditional_960px;
   if(!Array.isArray(a)||a.length!==2|| !a.every(x=>Number.isInteger(x)&&x>0)||a[0]>960)bad("960px:"+r.slot);
   const native=c.native_px;
   if(native && Array.isArray(native)&&native.length===2){
    if(a[0]>native[0] || a[1]>native[1] || Math.abs(a[0]/a[1]-native[0]/native[1])>0.005)bad("no_upscale_or_crop:"+r.slot);
   }
  }
  if(!r.release || Object.values(r.release).some(v=>v!==false)||Object.keys(r.release).length!==5)bad("unauthorized_release:"+r.slot);
 }
 if(slots.size!==expect.counts.source_rows||p0!==expect.counts.p0)bad("unique_source_coverage");
 }
 if(!Array.isArray(doc.oversized_media_rows)||doc.oversized_media_rows.length!==expect.counts.oversize)bad("oversize_rows");
 else {
  const seen=new Set();let bytes=0,matched=0,inlineBytes=0;
  for(const r of doc.oversized_media_rows){
   const id=String(r.media_id);
   if(seen.has(id)||expect.oversize_urls[id]!==r.original_url)bad("oversize_original_url:"+id);seen.add(id);
   if(!Number.isInteger(r.stored_original_bytes)||r.stored_original_bytes<=1500000)bad("oversize_threshold:"+id);
   bytes+=r.stored_original_bytes;
   if(r.published_inline_post_ids?.length){matched++;inlineBytes+=r.stored_original_bytes;}
   if(r.browser_current_src!==null||r.browser_transfer_bytes!==null||r.derivative_authorized!==false)bad("unverified_wire_or_release:"+id);
   const t=r.conditional_960px;
   if(!Array.isArray(t)||t[0]>960||t[0]>r.native_px?.[0]||t[1]>r.native_px?.[1])bad("oversize_geometry:"+id);
  }
  if(bytes!==expect.counts.stored_bytes||matched!==expect.counts.matched||inlineBytes!==expect.counts.inline_bytes)bad("stored_aggregate");
 }
 if(doc.counts?.reviewed_sources!==expect.counts.source_rows||doc.counts?.p0!==6||doc.counts?.p1!==37||
 doc.counts?.oversized_originals!==15||doc.counts?.oversized_original_stored_bytes!==expect.counts.stored_bytes||
 doc.counts?.oversized_inline_matches!==11||doc.counts?.oversized_inline_bytes!==expect.counts.inline_bytes ||
 doc.counts?.verified_guest_broken!==0||doc.counts?.actual_guest_image_requests!==0||doc.counts?.proposed_76pct_wire_saving_proven!==false)bad("unverified_aggregates");
 if(doc.historical_inventory?.reported_broken_42_guest_confirmed!==false||doc.expanded_inventory?.mixed_date_source_census!==true)bad("historical_scope");
 if(doc.policy?.all_candidate_rehosting_hold!==true||doc.policy?.all_wordpress_writes_hold!==true||doc.policy?.no_42_broken_claim!==true||doc.policy?.no_76pct_wire_claim!==true)bad("release_policy");
 if(JSON.stringify(doc.browser_handoff?.first_slots)!==JSON.stringify(["285:5","285:2","287:5","418:1","418:2","407:1"]))bad("p0_handoff");
 return {pass:errors.length===0,errors};
}
module.exports={validate:(document)=>validate(document,EXPECTED)};
