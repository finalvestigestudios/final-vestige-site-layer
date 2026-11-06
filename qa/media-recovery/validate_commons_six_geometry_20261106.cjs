'use strict';
// Read-only geometry/provenance acceptance gate. No media transfer or WP edits.
function validateSix(a,shards){
 const e=[],ok=(v,s)=>{if(!v)e.push(s)};
 if(!a||typeof a!=="object")return {ok:false,errors:["missing geometry"]};
 ok(a.schema==="fv-commons-6-source-dimension-grounding-v1"&&a.date==="2026-11-06","schema/date");
 ok(Array.isArray(a.rows)&&a.rows.length===6,"six rows");
 const m=new Map(shards.flatMap(s=>s.images).map(x=>[x.key,x]));
 const expected=["268:0","166:2","166:3","166:4","166:5","166:6"];
 ok(JSON.stringify(a.rows?.map(x=>x.key))===JSON.stringify(expected),"row sequence");
 for(const x of a.rows||[]){
  if(!x||typeof x!=="object"){e.push("bad row");continue;}
  const upstream=m.get(x.key);
  ok(!!upstream&&x.exact_stored_src===upstream.stored_src&&x.commons_file_page_candidate===upstream.catalog_lookup_url&&x.post_url===upstream.post_url,"source identity "+x.key);
  ok(x.requested_width_parameter_px===upstream?.requested_width_px,"width source "+x.key);
  const [w,h]=x.catalog_dimensions_native_px||[],[pw,ph]=x.proposed_preview_dimensions_no_upscale_px||[];
  ok(Number.isInteger(w)&&w>0&&Number.isInteger(h)&&h>0&&Number.isInteger(pw)&&pw>0&&Number.isInteger(ph)&&ph>0,"positive dimensions "+x.key);
  ok(pw===Math.min(960,w)&&ph===Math.round(h*pw/w),"no-upscale and ratio "+x.key);
  ok(typeof x.catalog_evidence_url==="string"&&x.catalog_evidence_url.startsWith("https://commons.wikimedia.org/wiki/"),"primary provenance "+x.key);
  ok(x.key==="268:0"?x.catalog_evidence_type==="individual_file_page":x.catalog_evidence_type==="commons_category_listing","type "+x.key);
  ok(x.license_release_approved===false&&x.item_visual_identity_verified===false&&x.wordpress_change_allowed===false&&x.media_caching_allowed===false,"rights gate "+x.key);
  ok(x.browser_render_verified===false&&x.browser_http===null&&x.cold_wire_bytes===null,"browser gate "+x.key);
  ok(Object.keys(x).every(z=>["key","post_url","exact_stored_src","commons_file_page_candidate","catalog_dimensions_native_px","catalog_evidence_url","catalog_evidence_type","proposed_preview_dimensions_no_upscale_px","requested_width_parameter_px","source_rights_note","license_release_approved","item_visual_identity_verified","browser_render_verified","browser_http","cold_wire_bytes","wordpress_change_allowed","media_caching_allowed"].includes(z)),"unexpected claim "+x.key);
 }
 ok(a.release?.no_enlargement===true&&a.release?.ceiling_width_px===960&&a.release?.downloaded_assets===0&&a.release?.wordpress_writes===0&&a.release?.approved_replacement_count===0&&a.release?.verified_visitor_failure_count===0,"release");
 return {ok:e.length===0,errors:e};
}
module.exports={validateSix};
if(typeof require==='function'&&require.main===module){const fs=require('node:fs'),path=require('node:path');const load=x=>JSON.parse(fs.readFileSync(path.join(__dirname,x),'utf8'));const r=validateSix(load('commons_six_native_geometry_20261106.json'),[load('commons_redirect_20261106_shard01.json'),load('commons_redirect_20261106_shard03.json')]);console.log(JSON.stringify(r,null,2));if(!r.ok)process.exitCode=1;}
