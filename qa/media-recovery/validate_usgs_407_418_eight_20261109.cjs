'use strict';
const EXPECTED={
  "407:0": "https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/vhp_img317.jpg",
  "407:2": "https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/media/images/EarthquakeLake1.jpg",
  "407:3": "https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/media/images/EarthquakeLake3.jpg",
  "407:4": "https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/thumbnails/image/img7536.jpg",
  "407:5": "https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/thumbnails/image/img7538.jpg",
  "407:6": "https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/thumbnails/image/img7537.jpg",
  "407:7": "https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/media/images/Quake%20lake%20and%20slide%2020230627.jpg",
  "418:5": "https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/styles/full_width/public/media/images/19460401_UNKNOWN_37-012_copy.jpg?itok=ASMRCahz"
};
function validate(d){
const e=[],bad=x=>e.push(x);
if(!d||d.schema!=='fv-usgs-eight-v1')return ['schema'];
if(d.source_census_blob!=='92a904c8da1ace1f972b2f00adf1a4847dde2b99')bad('census_sha');
if(!Array.isArray(d.rows)||d.rows.length!==8)return [...e,'count'];
if(d.counts?.researched_new!==8||d.counts?.tool_displayed!==7||d.counts?.tool_inaccessible!==1||d.counts?.guest_tested!==0||d.counts?.confirmed_broken!==0)bad('observation_counts');
if(d.performance?.measured_reduction_percent!==null||d.performance?.stored_bytes_are_network_bytes!==false||d.release_approved!==false)bad('performance_or_release');
if(d.site_qa?.owner_pr!==154||d.site_qa?.duplicate_collector!==false)bad('site_qa_owner');
const seen=new Set();let displayed=0,inaccessible=0;
for(const r of d.rows){
if(!Object.prototype.hasOwnProperty.call(EXPECTED,r.slot)||seen.has(r.slot))bad('slot');seen.add(r.slot);
if(r.stored_url!==EXPECTED[r.slot])bad('original_source_binding');
if(!r.post_url?.startsWith('https://finalvestige.com/')||r.post_id!==Number(r.slot.split(':')[0]))bad('post_binding');
if(r.origin_host!=='d9-wret.s3.us-west-2.amazonaws.com')bad('original_origin');
if(r.retriever?.observation==='IMAGE_RENDERED')displayed++;
else if(r.retriever?.observation==='TOOL_INACCESSIBLE')inaccessible++;
else bad('tool_outcome');
if(!String(r.retriever?.ref||'').startsWith('turn688438view')||r.retriever?.observed_on!=='2026-11-09')bad('provenance');
if(r.retriever?.origin_http!==null||r.retriever?.visitor_http!==null||r.visitor?.confirmed_broken!==null||r.visitor?.natural_width!==null||r.visitor?.natural_height!==null||r.visitor?.cold_wire_bytes!==null)bad('fabricated_browser');
if(!r.authority?.candidate_catalog_url?.startsWith('https://www.usgs.gov/')||r.authority?.exact_image_match!==false||r.authority?.rights_approved!==false)bad('rights_identity');
if(r.sizing?.native_width!==null||r.sizing?.native_height!==null||r.sizing?.output_width!==null||r.sizing?.output_height!==null||r.sizing?.max_width!==960||r.sizing?.upscale!==false)bad('unverified_geometry');
if(r.visual?.crop_approved!==false||r.visual?.caption_review_required!==true||!r.visual?.observed_scene)bad('scene_integrity');
if(!r.release||Object.keys(r.release).length!==5||Object.values(r.release).some(x=>x!==false))bad('production_gate');
}
if(seen.size!==8||displayed!==7||inaccessible!==1)bad('coverage_or_outcomes');
const bySlot=Object.fromEntries(d.rows.map(r=>[r.slot,r]));
if(!bySlot['407:7']?.visual.observed_scene.includes('2023'))bad('2023_context');
if(!bySlot['418:5']?.visual.observed_scene.includes('Hilo'))bad('hilo_context');
if(!bySlot['407:5']?.visual.observed_scene.includes('not direct 1959'))bad('geyser_context');
return [...new Set(e)];
}
module.exports={validate};
if(require.main===module){const fs=require('node:fs');const obj=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));const errors=validate(obj);console.log(errors.length?'HOLD '+errors.join(','):'PASS: eight URL-locked media rows');process.exitCode=errors.length?1:0;}
