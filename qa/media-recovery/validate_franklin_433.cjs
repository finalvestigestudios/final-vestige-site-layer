"use strict";
/* Pure, fail-closed archival audit check; no HTTP or WordPress writes. */
const PINNED={"433:1":"https://upload.wikimedia.org/wikipedia/commons/0/08/HMS_Erebus_and_Terror_-_ILN_1845.jpg","433:2":"https://upload.wikimedia.org/wikipedia/commons/9/9e/Dr_John_Rae%2C_with_relics_from_the_Franklin_Expedition%2C_gold_medal%2C_and_map%2C_August_1886_%28PORTRAITS_2459%29.jpg","433:3":"https://upload.wikimedia.org/wikipedia/commons/thumb/a/ad/%281860%29_Map_of_the_probable_routes_taken_by_HMS_Erebus_and_HMS_Terror_during_Franklin%27s_lost_expedition_%26_results_of_McClintock%27s_Arctic_Expedition.jpg/1280px-%281860%29_Map_of_the_probable_routes_taken_by_HMS_Erebus_and_HMS_Terror_during_Franklin%27s_lost_expedition_%26_results_of_McClintock%27s_Arctic_Expedition.jpg","433:4":"https://upload.wikimedia.org/wikipedia/commons/thumb/3/39/L23402-c8qmb-t3-05-rx.jpg/1280px-L23402-c8qmb-t3-05-rx.jpg","433:5":"https://d3d0lqu00lnqvz.cloudfront.net/media/media/cea975ac-62ed-4c2f-bf13-67a0f3a90092.jpg"};
function validate(a){
 const errors=[],bad=v=>errors.push(v);
 if(a?.schema!=="fv-franklin-five-offsite-v1"||a?.post?.id!==433)bad("schema/post");
 if(a?.frozen_fixture?.blob_sha!=="948bc1b65b42799aa40cfdb810ddf6ffd80886b6")bad("source snapshot");
 const b=a?.historical_baseline;
 if(b?.posts!==61||b?.images!==355||b?.external!==288||b?.broken_42_browser_confirmed!==false||b?.claimed_76pct_reduction_measured!==false||b?.oversized_originals_gt_1_5_decimal_mb!==15||b?.oversized_stored_original_bytes!==47096779)bad("unsupported historical claims");
 if(a?.first_party_preserved?.slot!=="433:0"||!a?.first_party_preserved?.url?.startsWith("https://finalvestige.com/"))bad("first party");
 if(!Array.isArray(a?.rows)||a.rows.length!==5)return {ok:false,errors:[...errors,"row count"]};
 const used=new Set();let displayed=0,inaccessible=0;
 for(const r of a.rows){
  if(!Object.prototype.hasOwnProperty.call(PINNED,r.slot)||used.has(r.slot)||r.original_url!==PINNED[r.slot]||r.post_id!==433)bad("source:"+r.slot);
  used.add(r.slot);
  if(!r.original_alt||!r.archival_record||!r.archival_candidate_url?.startsWith("https://")||!r.credit_to_verify||!r.visual_caveat||!r.rights_review)bad("provenance:"+r.slot);
  if(r.retrieval?.method!=="web.open exact literal URL"||r.retrieval?.origin_http_status!==null)bad("fabricated origin status:"+r.slot);
  if(r.retrieval?.observed==="VIEWER_DISPLAYED")displayed++;
  else if(r.retrieval?.observed==="VIEWER_INACCESSIBLE")inaccessible++;
  else bad("viewer observation:"+r.slot);
  if(!r.visitor||Object.values(r.visitor).some(v=>v!==null))bad("fabricated browser:"+r.slot);
  if(!r.release||Object.values(r.release).some(v=>v!==false)||Object.keys(r.release).length!==7)bad("unsafe release:"+r.slot);
  let d=r.candidate_catalog_original_dimensions,t=r.conditional_max_960px_dimensions;
  if(!Array.isArray(d)||d.length!==2||!d.every(v=>Number.isInteger(v)&&v>0))bad("archive dimensions:"+r.slot);
  if(r.slot==="433:5"){if(t!==null)bad("unmatched poster dimensions");}
  else if(!Array.isArray(t)||t[0]!==Math.min(d[0],960)||Math.abs(t[1]-Math.round(d[1]*t[0]/d[0]))>1)bad("upscale/aspect:"+r.slot);
 }
 if(used.size!==5||displayed!==2||inaccessible!==3)bad("observations");
 const c=a?.retriever_counts;
 if(c?.rendered!==2||c?.tool_inaccessible!==3||c?.actual_visitor_http_results!==0)bad("summary");
 return {ok:errors.length===0,errors};
}
module.exports={validate,PINNED};
if(require.main===module){const fs=require("node:fs"),p=require("node:path");const d=JSON.parse(fs.readFileSync(p.join(__dirname,"franklin_433_five_source_20261109.json"),"utf8"));const r=validate(d);console.log(JSON.stringify(r));if(!r.ok)process.exitCode=1}
