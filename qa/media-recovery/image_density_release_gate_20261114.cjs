'use strict';
/** Offline media density-and-release preflight. Does not fetch or alter images or WordPress. */
const fs=require('node:fs');
const {createHash}=require('node:crypto');
const digest=u=>createHash('sha256').update(u).digest('hex');
const positive=n=>Number.isFinite(n)&&n>0;
const integer=n=>Number.isSafeInteger(n)&&n>0;
const https=u=>{try{const x=new URL(u);return x.protocol==='https:'&&!x.username&&!x.password&&x.hostname.length>2}catch{return false}};
const FROZEN={
 '34:0':{post:34,media:39,width:1672,height:941,bytes:2892087,url_sha:'1018591a9732f43cd3e0d3dab31e7dd772d154d76ce0cc7e9c8db5675c528788',catalog_sha:'9575b594326c12f9cf6510e08a48e2d197f276fe01a3adaa3d6631179ab58071'},
 '35:0':{post:35,media:40,width:1672,height:941,bytes:2552136,url_sha:'5fdb4a9650f147190a7f66ff0f36147bfb258802ac25721043ce8d0ff4b94f8e',catalog_sha:'ffda402be4c8ca8445cdb43f648f41081f21986621bad6ef404bf3e3ac63d477'},
 '36:0':{post:36,media:41,width:1672,height:941,bytes:2498247,url_sha:'0c4e76e4b5b3894474a03467025605ca15e8287fcf5b255fc92e1f777c6b24b5',catalog_sha:'fc685a432e1b6df336de92fbfaea96a9b03c96897aaaeeb11964fef34a61c2a7'},
 '37:0':{post:37,media:42,width:1672,height:941,bytes:2488823,url_sha:'64841fe3e3af9bbc139868147c236ac36e19f49d809868f2844f14b2e3ff96c8',catalog_sha:'8451232d243f1374831f7775949e68a2846c867949f65eece3115a5e169f9169'},
 '38:0':{post:38,media:43,width:1672,height:941,bytes:2836245,url_sha:'7a7089270243c00338dd9b2f51f493841a08921268b72cdb836b9c13b8e0d5eb',catalog_sha:'8fc23a36d8be50e743e22bf3563dd1936cdeebd4789ce1ef088a446403e39798'},
 '621:0':{post:621,media:1257,width:4000,height:3000,bytes:4798395,url_sha:'7436579848ed5bb443387bb1d979f5b89b6c60f33e0bb3f6b17f59284a09a058',catalog_sha:'ae845ae6b36228411a8baa51d75ccc9870d60cc35fe2c49580f2328c7d042a7b'},
 '621:1':{post:621,media:1258,width:5667,height:3831,bytes:5553669,url_sha:'72854235c9292ca414fffdb30c9ab2d7698287a51906b14dead93a91d64adf02',catalog_sha:'a0a7b869cd9ca51619349b0f2ce528c9d0fffb745cf60b7a8142f31e772458ad'},
 '285:5':{post:285,media:null,width:819,height:614,bytes:null,url_sha:'f2b19a3806fc2bdcab18e64781a64506106f09a1b608984610f191b7b6a4100f',catalog_sha:'04265be0fbe50057b441189f877bdf7254c61c4ae236ca22d0755ac464ed6c90'},
 '418:2':{post:418,media:null,width:600,height:463,bytes:null,url_sha:'deea9612294737b05795af61a6b509cdfe7e12f59171b5b15728707e8a9b8eea',catalog_sha:'f033612a88bc7378ce5bfc13019cfe9ca3ad25715c31903ab21b310c9adb8803'}
};
function assess(ledger,observations={}){
 const issues=[],results=[];
 if(!ledger||ledger.schema!=='fv-media-density-preflight-v1'||!Array.isArray(ledger.items)||ledger.items.length!==9)issues.push('invalid_ledger_shape');
 if(!ledger?.policy||ledger.policy.max_width_px!==960||ledger.policy.no_upscale!==true||ledger.policy.wordpress_production_write!==false||ledger.policy.media_copy_authorized!==false||ledger.policy.release_authorized!==false)issues.push('unsafe_or_changed_policy');
 if(!observations||typeof observations!=='object'||Array.isArray(observations))issues.push('invalid_observations');
 const seen=new Set();
 for(const x of Array.isArray(ledger?.items)?ledger.items:[]){
  const reasons=[],f=FROZEN[x?.slot];
  if(!f||seen.has(x.slot))reasons.push('slot_missing_duplicate_or_unrecognized');
  seen.add(x.slot);
  if(!f){results.push({slot:x?.slot||null,state:'HOLD',reasons});continue}
  if(x.post_id!==f.post||x.media_id!==f.media||x.native_width_px!==f.width||x.native_height_px!==f.height||x.original_stored_bytes!==f.bytes)reasons.push('source_metadata_drift');
  if(!https(x.stored_source_url)||!https(x.catalog_url)||digest(x.stored_source_url)!==f.url_sha||digest(x.catalog_url)!==f.catalog_sha)reasons.push('missing_or_changed_frozen_source_catalog');
  if(x.guest_http_status!==null||x.guest_wire_bytes!==null||x.guest_current_src!==null||x.rights_to_rehost_verified!==false||x.binary_identity_verified!==false||x.cached_or_uploaded!==false)reasons.push('unsupported_existing_evidence_or_approval');
  const w=x.candidate_width_px,h=x.candidate_height_px;
  if(!integer(w)||!integer(h)||w>960||w>f.width||h>f.height)reasons.push('invalid_derivative_size_or_upscale');
  else if(Math.abs(w*f.height-h*f.width)/(w*f.height)>0.01)reasons.push('crop_or_ratio_not_reviewed');
  if(x.historical_scene_identity!=='UNVERIFIED'&&x.historical_scene_identity!=='RECONSTRUCTION_SAME_SOURCE')reasons.push('invented_scene_identity');
  const o=observations?.[x.slot];let density='NOT_MEASURED';
  if(o!==undefined){
   if(!o||typeof o!=='object'||Array.isArray(o)||!positive(o.css_width_px)||!positive(o.css_height_px)||!positive(o.dpr)||o.dpr>4||
      o.cold_browser_verified!==true||o.candidate_http_status!==200||o.candidate_decoded!==true||!https(o.candidate_current_src)||
      !integer(o.candidate_natural_width_px)||!integer(o.candidate_natural_height_px)||o.asset_identity_verified!==true){
     reasons.push('guest_css_dpr_or_network_evidence_unverified');density='UNVERIFIED';
   }else if(o.candidate_natural_width_px!==w||o.candidate_natural_height_px!==h){
     reasons.push('measured_candidate_dimensions_not_matched');density='UNVERIFIED';
   }else if(w+1e-8<o.css_width_px*o.dpr||h+1e-8<o.css_height_px*o.dpr){
     reasons.push('candidate_under_density_at_actual_css_dpr');density='INSUFFICIENT';
   }else density='DENSITY_SCREEN_PASS';
  }else reasons.push('guest_css_dpr_and_network_not_measured');
  if(x.slot==='621:1')reasons.push('historic_map_label_legibility_unverified');
  if(x.slot==='285:5')reasons.push('original_publisher_16_9_crop_vs_4_3_candidate');
  if(x.slot==='418:2')reasons.push('museum_resized_photo_binary_and_rights_unverified');
  reasons.push('rights_crop_visual_quality_and_editorial_staging_not_approved');
  results.push({slot:x.slot,source_url:x.stored_source_url,catalog_url:x.catalog_url,candidate_px:[w,h],css_width_max_dpr2_px:integer(w)?w/2:null,density,state:'HOLD',reasons:[...new Set(reasons)]});
 }
 for(const k of Object.keys(FROZEN))if(!seen.has(k))issues.push('frozen_slot_missing:'+k);
 if(Object.keys(observations||{}).some(k=>!FROZEN[k]))issues.push('unknown_observation_slot');
 return {schema:'fv-media-density-preflight-result-v1',state:'HOLD',source_inventory_valid:issues.length===0&&results.every(r=>!r.reasons.some(x=>['source_metadata_drift','slot_missing_duplicate_or_unrecognized','missing_or_changed_frozen_source_catalog','unsupported_existing_evidence_or_approval','invalid_derivative_size_or_upscale','crop_or_ratio_not_reviewed','invented_scene_identity'].includes(x))),issues,results,guest_measurement_count:results.filter(r=>r.density==='DENSITY_SCREEN_PASS'||r.density==='INSUFFICIENT').length,release_authorized:false,sitewide_76_percent_claim_supported:false};
}
if(require.main===module){try{const args=process.argv.slice(2);if(args.length<1||args.length>2)throw Error('Usage: node image_density_release_gate_20261114.cjs LEDGER.json [GUEST_OBSERVATIONS.json]');const a=JSON.parse(fs.readFileSync(args[0],'utf8'));const b=args[1]?JSON.parse(fs.readFileSync(args[1],'utf8')):{};const result=assess(a,b);process.stdout.write(JSON.stringify(result,null,2)+'\n');if(!result.source_inventory_valid)process.exitCode=2;}catch(e){console.error('INVALID_INPUT '+e.message);process.exitCode=2}}
module.exports={assess,FROZEN};
