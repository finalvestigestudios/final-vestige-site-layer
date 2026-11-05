'use strict';
const fs=require('node:fs');
const expected=["https://cdn.loc.gov/service/pnp/ggbain/19600/19622v.jpg","https://commons.wikimedia.org/wiki/Special:Redirect/file/Wreck_of_the_Eastland,_Chicago,_1915.jpg","https://commons.wikimedia.org/wiki/Special:Redirect/file/EastlandKenosha.jpg","https://commons.wikimedia.org/wiki/Special:Redirect/file/Helen_Repa_Eastland_Disaster_photo.png?width=1280","https://cdn.loc.gov/service/pnp/ggbain/19600/19623v.jpg","https://commons.wikimedia.org/wiki/Special:Redirect/file/Photograph_of_The_Eastland_(upside_down)_on_Chicago_River,_Chicago._-_NARA_-_281841.jpg?width=1280"];
function validate(d){const e=[];function bad(s){e.push(s)}
if(d?.schema!=='fv.eastland.214.source-v1'||d?.source_inventory?.blob_sha!=='0f3dfe398a76838049cebba7cb773d5c5a0c8c69')bad('corpus');
if(d?.baseline?.posts!==61||d?.baseline?.image_references!==355||d?.baseline?.offsite!==288||d?.baseline?.reported_42_broken!=='UNVERIFIED'||d?.baseline?.reported_76_percent!=='UNMEASURED')bad('baseline');
if(d?.production_changes!==0||d?.third_party_downloads!==0||d?.permissions!=='HOLD')bad('release');
if(!Array.isArray(d?.images)||d.images.length!==6)bad('six');
const seen=new Set();
for(const x of d?.images||[]){
if(seen.has(x.key))bad('duplicate');seen.add(x.key);
const slot=Number(x.key?.split(':')[1]);if(!Number.isInteger(slot)||slot<0||slot>5||x.key!=='214:'+slot||x.original_source_url!==expected[slot])bad('URL/slot');
if(typeof x.alt!=='string'||x.alt.length<25)bad('alt');
if(x.guest_http_status!==null||x.guest_natural_width!==null||x.guest_bytes!==null||x.origin_http_status!==null||x.exact_binary_verified!==false)bad('fabricated evidence');
if(x.rehost_authorized!==false||x.wordpress_write_authorized!==false||x.remediation_status!=='HOLD')bad('publication');
if(typeof x.copyright_review!=='string'||x.copyright_review.length<25||typeof x.editorial_finding!=='string'||x.editorial_finding.length<25)bad('rights/chronology');
if(x.master_width===null||x.master_height===null){if(x.master_width!==null||x.master_height!==null||x.conditional_width!==null||x.conditional_height!==null||x.primary_or_catalog_record!==null)bad('unknown geometry');}
else{const w=x.master_width,h=x.master_height;if(!Number.isInteger(w)||!Number.isInteger(h)||w<=0||h<=0||x.conditional_width!==Math.min(960,w)||x.conditional_height!==Math.round(h*Math.min(960,w)/w)||!x.primary_or_catalog_record?.startsWith('https://'))bad('dimensions');}
}if(seen.size!==6)bad('distinct');return {ok:e.length===0,errors:e};}
if(require.main===module){const p=process.argv[2]||require('node:path').join(__dirname,'eastland_214_catalog_20261105.json');const r=validate(JSON.parse(fs.readFileSync(p,'utf8')));console.log(JSON.stringify(r));process.exitCode=r.ok?0:1;}
module.exports={validate};
