'use strict';
function validate(a,fixture){
 const errors=[];
 const bad=(e)=>errors.push(e);
 const f=(fixture.images||[]).filter(x=>x.post_id===220).sort((x,y)=>x.slot-y.slot);
 if(a.schema!=='fv-media-thresher-220-source-evidence-v1'||a.post_id!==220||a.rows?.length!==7||f.length!==7)bad('wrong_scope_or_count');
 if(a.source_fixture_blob_sha!=='9b16b828342a9ac338f3e65610fd3d8d508355e9')bad('fixture_sha_mismatch');
 if(a.counts?.confirmed_guest_broken!==0||a.counts?.wordpress_changes!==0)bad('fabricated_failure_or_write');
 if(!String(a.performance_policy).includes('UNMEASURED'))bad('false_performance_claim');
 const seen=new Set();
 (a.rows||[]).forEach((r,i)=>{
   const o=f[i];
   if(!o||r.slot!==o.key||r.post_id!==220||r.stored_original_url!==o.source_url||r.stored_alt!==o.alt||r.source_fixture_blob_sha!==a.source_fixture_blob_sha)bad('source_identity:'+i);
   if(seen.has(r.slot))bad('duplicate:'+i); seen.add(r.slot);
   const v=r.source_observation||{};
   if(v.method!=='WEB_OPEN_INDEPENDENT_RETRIEVER'||v.result!=='TOOL_INACCESSIBLE'||v.origin_http_status!==null||v.visitor_http_status!==null||v.visitor_image_decoded_px!==null||v.visitor_transferred_bytes!==null||v.confirmed_broken!==null)bad('invented_http_or_browser:'+i);
   const c=r.candidate||{}, n=c.native_catalog_pixels, out=c.conditional_max_960_pixels;
   if(!Array.isArray(n)||!Array.isArray(out)||n.length!==2||out.length!==2||!n.every(Number.isInteger)||!out.every(Number.isInteger)||n.some(x=>x<=0)||out.some(x=>x<=0))bad('invalid_dimensions:'+i);
   else {const w=Math.min(960,n[0]),h=Math.round(n[1]*w/n[0]);if(out[0]!==w||out[1]!==h||out[0]>n[0]||out[1]>n[1]+1)bad('upscale_or_geometry:'+i);}
   if(c.individual_rights_cleared!==false||c.exact_binary_or_crop_match!==false||c.image_identity_sha256!==null||c.upscaling_allowed!==false)bad('unverified_release:'+i);
   if(!c.commons_catalog_url?.startsWith('https://commons.wikimedia.org/wiki/File:'))bad('invalid_catalog:'+i);
   for(const [k,v] of Object.entries(r.release||{}))if(v!==false)bad('production_write:'+k+':'+i);
   if(Object.keys(r.release||{}).length!==5)bad('release_contract:'+i);
   if(i===4&&(!String(c.historical_integrity_note).includes('1964')||c.catalog_accession!==null||c.relationship!=='COMMONS_ONLY_NO_VERIFIED_PRIMARY_ACCESSION'))bad('trieste_false_provenance');
   if(i===6&&!String(c.historical_integrity_note).includes('1964'))bad('rudder_false_chronology');
   if(i===2&&!String(c.rights_observation).includes('Cavas'))bad('skylark_rights_provenance');
 });
 return {ok:errors.length===0,errors};
}
module.exports={validate};
if(require.main===module){const fs=require('node:fs'),path=require('node:path');const base=__dirname;const a=JSON.parse(fs.readFileSync(path.join(base,'thresher_220_seven_navy_20261109.json'),'utf8'));const f=JSON.parse(fs.readFileSync(path.join(base,'../../qa/media-recovery/parts/05.json'),'utf8'));const x=validate(a,f);console.log(JSON.stringify(x));if(!x.ok)process.exitCode=1;}
