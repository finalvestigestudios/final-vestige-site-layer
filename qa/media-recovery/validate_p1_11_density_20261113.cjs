'use strict';
// Offline-only. Never fetches an image or modifies WordPress. Validates a frozen CMS snapshot.
const fs = require('node:fs');
const EXPECT = new Map([
  [39,[34,2892087,'bceca0bd-a16f-44f7-be08-16376fbf08ca.png',960,540,'DIRECT',0]],
  [40,[35,2552136,'377e08da-e121-4f57-9174-1548343402b3.png',960,540,'DIRECT',0]],
  [41,[36,2498247,'a44f673d-a8a8-4c83-9f29-7e24dd55156b.png',960,540,'DIRECT',0]],
  [42,[37,2488823,'c1237ffd-4a47-4988-8254-e3b021069e72.png',960,540,'DIRECT',0]],
  [43,[38,2836245,'01340c2e-1165-4ca0-aa96-87398a83d13a.png',960,540,'DIRECT',0]],
  [1257,[621,4798395,'edit-017-v01-malbone-tunnel-generalpunger-original.jpg',960,720,'DIRECT',7]],
  [1258,[621,5553669,'edit-017-v02-nypl-5003296-original.jpg',960,649,'DIRECT',7]],
  [1714,[269,1543002,'halifax-explosion-map.png',960,960,'DIRECT',5]],
  [388,[299,8176362,'vasa-modell-2020.jpg',960,639,'JETPACK',7]],
  [389,[299,2822969,'vasa-01-2020.jpg',960,634,'JETPACK',7]],
  [382,[299,2318980,'vasa-med-gamla-och-nya-stottor_vasa-with-old-and-new-supports.jpg',960,640,'JETPACK',6]]
]);
const NATIVE = new Map([[39,[1672,941]],[40,[1672,941]],[41,[1672,941]],[42,[1672,941]],[43,[1672,941]],[1257,[4000,3000]],[1258,[5667,3831]],[1714,[1280,1280]],[388,[4256,2832]],[389,[2147,1417]],[382,[1800,1200]]]);
const failClosed = (errors,reason) => {errors.push(reason);};
const exact = (filename,id) => 'https://finalvestige.com/wp-content/uploads/2026/'+(id===1714?'10/':'08/')+filename;
const integer = n => Number.isSafeInteger(n) && n>0;
function validateAndPlan(a) {
  const errors=[];
  if(!a || typeof a!=='object' || Array.isArray(a)) return {status:'HOLD',errors:['document-invalid'],production_release_allowed:false};
  if(a.schema!=='fv-11-oversize-density-bridge-v1' || a.provenance?.worklist_blob!=='2acd06a4ca4317646006eb6591face3fe76fedec' || a.provenance?.source_15_blob!=='5e474e1cb293353b2226d84fceedca0a182894d8') failClosed(errors,'baseline-custody');
  if(!Array.isArray(a.rows) || a.rows.length!==11) failClosed(errors,'eleven-rows-required');
  let total=0,direct=0,jetpack=0;const ids=new Set(),posts=new Set();
  const rows=[];
  for(const r of Array.isArray(a.rows)?a.rows:[]){
    if(!r || typeof r!=='object'){failClosed(errors,'row-invalid');continue;}
    const x=EXPECT.get(r.media_id); if(!x){failClosed(errors,'unknown-media:'+r.media_id);continue;}
    if(ids.has(r.media_id))failClosed(errors,'duplicate:'+r.media_id);ids.add(r.media_id);
    const [post,size,filename,width,height,kind,subsizes]=x,source=exact(filename,r.media_id),tag=r.media_id;
    if(r.post_id!==post || r.original_url!==source || r.stored_original_bytes!==size || r.embedding_kind!==kind || r.generated_subsizes!==subsizes) failClosed(errors,'source-binding:'+tag);
    if(!Array.isArray(r.native_px) || r.native_px[0]!==NATIVE.get(tag)[0] || r.native_px[1]!==NATIVE.get(tag)[1]) failClosed(errors,'native-dimensions-custody:'+tag);
    if(r.conditional_960px?.[0]!==width || r.conditional_960px?.[1]!==height || !Array.isArray(r.native_px) || !r.native_px.every(integer) || r.native_px[0]<width || r.native_px[1]<height) failClosed(errors,'no-upscale-and-geometry:'+tag);
    if(kind==='DIRECT' && r.published_src!==source) failClosed(errors,'original-inline-url:'+tag);
    if(kind==='JETPACK' && (!/^https:\/\/i0\.wp\.com\/finalvestige\.com\/wp-content\/uploads\//.test(r.published_src||'') || !r.published_src.includes(filename) || !r.published_src.includes('fit=1024'))) failClosed(errors,'jetpack-identity:'+tag);
    if(r.guest_http_status!==null || r.guest_current_src!==null || r.guest_wire_bytes!==null || r.guest_css_width!==null || r.guest_dpr!==null || r.candidate_wire_bytes!==null || r.rights_release_authorized!==false || r.derivative_created!==false) failClosed(errors,'unverified-guest-rights:'+tag);
    if(r.editorial_gate!==(r.media_id===1714?'MAP_LABEL_ZOOM_AND_AUTHOR_RIGHTS':kind==='JETPACK'?'EXISTING_CDN_TRANSFORM_AND_RIGHTS':r.media_id>=1257?'ARCHIVAL_ITEM_RIGHTS':'CREATOR_RIGHTS_AND_SCENE_PARITY')) failClosed(errors,'editorial-gate:'+tag);
    if(!integer(size)) failClosed(errors,'bytes-invalid:'+tag);
    total+=size;posts.add(post);if(kind==='DIRECT')direct+=size;else jetpack+=size;
    rows.push({media_id:tag,post_id:post,source_url:source,inline_kind:kind,original_stored_bytes:size,derivative_ceiling_px:[width,height],max_css_width_dpr1:width,max_css_width_dpr2:width/2,max_css_width_dpr3:width/3,guest_status:'UNMEASURED',decision:'HOLD_RIGHTS_CSS_DPR_WIRE_AND_VISUAL_QA'});
  }
  if(ids.size!==11 || posts.size!==8 || total!==38480915 || direct!==25162604 || jetpack!==13318311) failClosed(errors,'cohort-reconciliation');
  if(a.metrics?.total_stored_bytes!==38480915 || a.metrics?.direct_original_stored_bytes!==25162604 || a.metrics?.jetpack_original_stored_bytes!==13318311 || a.metrics?.guest_wire_baseline_bytes!==null || a.metrics?.guest_wire_candidate_bytes!==null || a.metrics?.claimed_76_percent_verified!==false || a.metrics?.visitor_confirmed_broken!==null) failClosed(errors,'storage-is-not-wire');
  if(a.safety?.wordpress_writes!==0 || a.safety?.image_downloads!==0 || a.safety?.media_caching!==0 || a.safety?.home_design_changes!==0 || a.safety?.subscription_spend_usd!==0 || a.safety?.qa_collector!=='Site QA #154') failClosed(errors,'unsafe-scope');
  return {status:errors.length?'HOLD':'AUDIT_VALIDATED_NO_RELEASE',errors,production_release_allowed:false,visitor_savings_verified:false,counts:{rows:ids.size,posts:posts.size,stored_bytes:total,direct_original_stored_bytes:direct,jetpack_original_stored_bytes:jetpack},rows};
}
if(require.main===module){
 const file=process.argv[2];if(!file){console.error('usage: node validate_p1_11_density_20261113.cjs <audit.json>');process.exit(2)}
 try{const out=validateAndPlan(JSON.parse(fs.readFileSync(file,'utf8')));console.log(JSON.stringify(out,null,2));if(out.status!=='AUDIT_VALIDATED_NO_RELEASE')process.exitCode=1;}catch(e){console.error('HOLD '+e.message);process.exitCode=1;}
}
module.exports={validateAndPlan};
