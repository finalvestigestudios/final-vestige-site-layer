'use strict';
/**
 * Fail-closed measurement adapter bound to eleven specifically verified
 * 2026-11-08 WordPress raw inline image positions (eight published articles).
 * Uses the separate offline CDP pair evaluator; does not collect traffic,
 * fetch binaries, clear rights, modify WordPress or approve deployment.
 * Other images in the article are NOT measured by this adapter.
 */
const {evaluatePair,INVENTORY_BLOB}=require('./measure_image_transfer_pair_20261111.cjs');
const EXPOSURE_BLOB='5e474e1cb293353b2226d84fceedca0a182894d8';
const PINS=Object.freeze([
  {
    "slot": "34:0",
    "post_id": 34,
    "media_id": 39,
    "page": "https://finalvestige.com/2026/08/16/the-morning-san-francisco-lost-its-water/",
    "src": "https://finalvestige.com/wp-content/uploads/2026/08/bceca0bd-a16f-44f7-be08-16376fbf08ca.png",
    "stored_bytes": 2892087
  },
  {
    "slot": "35:0",
    "post_id": 35,
    "media_id": 40,
    "page": "https://finalvestige.com/2026/08/16/the-boat-that-refused-to-die/",
    "src": "https://finalvestige.com/wp-content/uploads/2026/08/377e08da-e121-4f57-9174-1548343402b3.png",
    "stored_bytes": 2552136
  },
  {
    "slot": "36:0",
    "post_id": 36,
    "media_id": 41,
    "page": "https://finalvestige.com/2026/08/16/the-city-that-went-underground/",
    "src": "https://finalvestige.com/wp-content/uploads/2026/08/a44f673d-a8a8-4c83-9f29-7e24dd55156b.png",
    "stored_bytes": 2498247
  },
  {
    "slot": "37:0",
    "post_id": 37,
    "media_id": 42,
    "page": "https://finalvestige.com/2026/08/16/how-petra-made-water-flow-through-stone/",
    "src": "https://finalvestige.com/wp-content/uploads/2026/08/c1237ffd-4a47-4988-8254-e3b021069e72.png",
    "stored_bytes": 2488823
  },
  {
    "slot": "38:0",
    "post_id": 38,
    "media_id": 43,
    "page": "https://finalvestige.com/2026/08/16/the-cisterns-beneath-san-francisco/",
    "src": "https://finalvestige.com/wp-content/uploads/2026/08/01340c2e-1165-4ca0-aa96-87398a83d13a.png",
    "stored_bytes": 2836245
  },
  {
    "slot": "269:1",
    "post_id": 269,
    "media_id": 1714,
    "page": "https://finalvestige.com/2026/08/18/the-watch-lost-its-hands-halifax-explosion/",
    "src": "https://finalvestige.com/wp-content/uploads/2026/10/halifax-explosion-map.png",
    "stored_bytes": 1543002
  },
  {
    "slot": "299:0",
    "post_id": 299,
    "media_id": 389,
    "page": "https://finalvestige.com/2026/08/19/thirty-men-were-enough-vasa/",
    "src": "https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/vasa-01-2020.jpg?fit=1024%2C676&ssl=1",
    "stored_bytes": 2822969
  },
  {
    "slot": "299:1",
    "post_id": 299,
    "media_id": 388,
    "page": "https://finalvestige.com/2026/08/19/thirty-men-were-enough-vasa/",
    "src": "https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/vasa-modell-2020.jpg?fit=1024%2C681&ssl=1",
    "stored_bytes": 8176362
  },
  {
    "slot": "299:7",
    "post_id": 299,
    "media_id": 382,
    "page": "https://finalvestige.com/2026/08/19/thirty-men-were-enough-vasa/",
    "src": "https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/vasa-med-gamla-och-nya-stottor_vasa-with-old-and-new-supports.jpg?fit=1024%2C683&ssl=1",
    "stored_bytes": 2318980
  },
  {
    "slot": "621:0",
    "post_id": 621,
    "media_id": 1257,
    "page": "https://finalvestige.com/2026/08/23/six-miles-an-hour-malbone-street-wreck/",
    "src": "https://finalvestige.com/wp-content/uploads/2026/08/edit-017-v01-malbone-tunnel-generalpunger-original.jpg",
    "stored_bytes": 4798395
  },
  {
    "slot": "621:1",
    "post_id": 621,
    "media_id": 1258,
    "page": "https://finalvestige.com/2026/08/23/six-miles-an-hour-malbone-street-wreck/",
    "src": "https://finalvestige.com/wp-content/uploads/2026/08/edit-017-v02-nypl-5003296-original.jpg",
    "stored_bytes": 5553669
  }
].map(row=>Object.freeze(row)));
const P0_FIRST=true;
function hold(reason,slot=null){
 return {status:'HOLD',reason,detail:slot,
   image_network_before_bytes:null,image_network_after_bytes:null,
   reduction_percent:null,target_76_percent_met:null,
   pinned_oversize_slot_pair_verified:false,full_article_transfer_verified:false,
   sitewide_transfer_savings_verified:false,production_change_allowed:false};
}
function same(a,b){return JSON.stringify([...a].sort())===JSON.stringify([...b].sort())}
function evaluatePinnedPair(input){
 if(!input||input.schema!=='fv-cold-transfer-pair-v1'||
    input.source_ledger_blob_sha!==INVENTORY_BLOB||
    input.oversize_exposure_blob_sha!==EXPOSURE_BLOB||
    !Number.isSafeInteger(input.post_id))return hold('FROZEN_SOURCE_PROVENANCE_NOT_BOUND');
 const cohort=PINS.filter(x=>x.post_id===input.post_id);
 if(!cohort.length)return hold('POST_NOT_IN_REVIEWED_OVERSIZE_COHORT');
 const expected=cohort.map(x=>x.slot);
 if(!Array.isArray(input.expected_slots)||!same(input.expected_slots,expected))
   return hold('PARTIAL_OR_FOREIGN_OVERSIZE_SLOT_COHORT');
 for(const phase of ['before','after']){
   const c=input[phase];
   if(!c||c.page_url!==cohort[0].page||!Array.isArray(c.images))
     return hold('PUBLISHED_ARTICLE_URL_OR_CAPTURE_MISMATCH');
   if(!same(c.images.map(x=>x&&x.slot),expected))
     return hold('PARTIAL_OR_FOREIGN_CAPTURE_IMAGE_SLOTS');
   for(const p of cohort){
     const x=c.images.find(im=>im.slot===p.slot);
     // Self-attested approval bits and identical image_identity strings are
     // NOT independent permission to swap a photograph or optimization URL.
     if(x.current_src!==p.src||x.request_url!==p.src||x.final_response_url!==p.src)
       return hold('UNREVIEWED_SOURCE_OR_DELIVERY_URL_CHANGE',p.slot);
     if(x.image_identity!=='wp-media:'+p.media_id)
       return hold('UNBOUND_MEDIA_IDENTITY',p.slot);
   }
 }
 const result=evaluatePair(input);
 if(result.status!=='VERIFIED_SINGLE_POST_COLD_PAIR')
   return {...result,pinned_oversize_slot_pair_verified:false,
     full_article_transfer_verified:false,sitewide_transfer_savings_verified:false,
     production_change_allowed:false};
 return {...result,status:'VERIFIED_PINNED_OVERSIZE_SLOTS_COLD_PAIR',
   pinned_oversize_slot_pair_verified:true,
   pinned_oversize_slots:expected,pinned_oversize_source_stored_bytes:
     cohort.reduce((n,x)=>n+x.stored_bytes,0),
   full_article_transfer_verified:false,sitewide_transfer_savings_verified:false,
   production_change_allowed:false,
   scope:'only reviewed >1.5 MB original source slots, not all image requests, article bytes or sitewide bytes'};
}
module.exports={evaluatePinnedPair,PINS,EXPOSURE_BLOB,P0_FIRST};
