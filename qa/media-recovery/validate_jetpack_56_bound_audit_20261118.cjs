'use strict';
// Offline image QUERY-bound reconciliation: no HTTP, media downloads, or WP writes.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const pins=["698b613c41e792b2e0100547a07f4b519c0a908a","1c8cd5d1fd015705c0937d68471fb54546ed2f67","32210de4d0f46ae2547d604d9f1d02769e98bd32","0d5bf91705d7b9956ac7097ebb896c9b142afc51","c0d54c30769b0276a143c2f77b897202d818105f","38718a55ce8fb52eb09cf04765c444a9df1255c9","8cdd86e25bbc6aff1654eeff3fc65f3f42b1e4af","d2c1716c99ff9886e6dac60c6a42926c801be7f4","0248e5d62e589dd6cfc0ec543b5c22a7c14128ea"],crossPin='66aa70b1982237015b87b1901ea0100fe9e64181';
const hold=msg=>{throw Error('HOLD: '+msg)};
const gitSha=str=>{const b=Buffer.from(str,'utf8');return crypto.createHash('sha1').update('blob '+b.length+'\\0').update(b).digest('hex')};
function loadSources(){
 const parts=pins.map((pin,i)=>{const raw=fs.readFileSync(path.join(__dirname,'live_66_view_slice_'+(i+1)+'_20261117.json'),'utf8');if(gitSha(raw)!==pin)hold('source slice SHA changed');return JSON.parse(raw)});
 const raw=fs.readFileSync(path.join(__dirname,'live_20_oversized_to_66_post_inline_crosswalk_20261117.json'),'utf8');
 if(gitSha(raw)!==crossPin)hold('media crosswalk SHA changed');
 return {parts,cross:JSON.parse(raw)};
}
function parseBound(src){
 if(typeof src!=='string')return null;
 let u;try{u=new URL(src)}catch{return null}
 if(u.protocol!=='https:'||!/^i[0-3]\.wp\.com$/.test(u.hostname))return null;
 const type=u.searchParams.has('resize')?'resize':u.searchParams.has('fit')?'fit':null;
 if(!type)return null;
 const m=/^(\d+),(\d+)$/.exec(u.searchParams.get(type));
 return m?{type,width:Number(m[1]),height:Number(m[2])}:null;
}
function build(parts,cross){
 const posts=parts.flatMap(x=>x.posts),all=parts.flatMap(x=>x.images);
 if(parts.length!==9||posts.length!==66||all.length!==361||new Set(all.map(x=>x.post_id+':'+x.slot)).size!==361||cross.items.length!==20)hold('source count drift');
 const pmap=new Map(posts.map(p=>[p.id,p])),orig=new Map();
 for(const item of cross.items)for(const r of item.inline_exact_origin_slots){
  if(orig.has(r.slot_id))hold('duplicate crosswalk slot');
  orig.set(r.slot_id,{media_id:item.id,original_stored_bytes:item.original_bytes});
 }
 let rows=[],atmost=0,other=0;
 for(const x of all){
  const bound=parseBound(x.authored_view_src),key=x.post_id+':'+x.slot;
  if(!pmap.has(x.post_id))hold('orphan image');
  if(!bound){other++;continue}
  if(bound.width<=960){atmost++;continue}
  rows.push({slot:key,post_id:x.post_id,post_url:pmap.get(x.post_id).url,published_src:x.authored_view_src,origin_url:x.source_origin_url,route_type:x.route_type,query_transform:bound.type,query_bound_width_px:bound.width,query_bound_height_px:bound.height,has_srcset:x.has_srcset,has_sizes:x.has_sizes,oversized_original:orig.get(key)||null,guest_current_src:null,guest_http_status:null,guest_decoded_raster_px:null,guest_wire_bytes:null,guest_broken:null,license_clearance:'HOLD',master_sha256:null,replacement_approved:false,derivative_width_limit_px:960,no_upscale:true});
 }
 rows.sort((a,b)=>a.post_id-b.post_id||Number(a.slot.split(':')[1])-Number(b.slot.split(':')[1]));
 const summary={source_posts:66,source_slots:361,query_over_960:rows.length,posts_affected:new Set(rows.map(x=>x.post_id)).size,first_party_proxy:rows.filter(x=>x.route_type==='first_party_jetpack').length,third_party_proxy:rows.filter(x=>x.route_type==='third_party_jetpack').length,srcset_present:rows.filter(x=>x.has_srcset).length,query_at_most_960:atmost,no_pair_or_direct:other,large_stored_original_matches:rows.filter(x=>x.oversized_original).length,matched_stored_original_bytes:rows.reduce((v,x)=>v+(x.oversized_original?.original_stored_bytes||0),0),confirmed_broken_guest:null,measured_savings_percent:null,visitor_bytes:null};
 return {schema:'fv-jetpack-query-bounds-56-v1',source_date:'2026-11-17',source_git_blob_pins:pins,crosswalk_blob_pin:crossPin,summary,rows,release:{status:'HOLD',wp_production_writes:0,rehosts:0,downloads:0,new_browser_collector:false,cost_usd:0,homepage_design_changes:0}};
}
function validate(ledger,parts,cross){
 const recalculated=build(parts,cross);
 const sum=recalculated.summary;
 if(JSON.stringify([sum.query_over_960,sum.posts_affected,sum.first_party_proxy,sum.third_party_proxy,sum.srcset_present,sum.query_at_most_960,sum.no_pair_or_direct,sum.large_stored_original_matches,sum.matched_stored_original_bytes])!==JSON.stringify([56,24,40,16,35,30,275,11,38480915]))hold('unexpected reference counts');
 try{assert.deepStrictEqual(ledger,recalculated)}catch{hold('URL, dimension, rights, status or cost claim mismatch')}
 return {status:'HOLD',query_candidates:56,affected_posts:24,large_original_stored_bytes_not_transfers:38480915,guest_broken_count:null,measured_reduction:null};
}
module.exports={loadSources,parseBound,build,validate};
if(require.main===module){try{const {parts,cross}=loadSources(),f=process.argv[2]||path.join(__dirname,'jetpack_56_bound_audit_20261118.json');console.log(JSON.stringify(validate(JSON.parse(fs.readFileSync(f,'utf8')),parts,cross),null,2));}catch(e){console.error(e.message);process.exitCode=1;}}
