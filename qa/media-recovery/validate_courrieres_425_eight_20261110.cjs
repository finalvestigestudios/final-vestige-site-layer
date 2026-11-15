"use strict";
const PINS=[{"slot":"425:1","src":"https://commons.wikimedia.org/wiki/Special:Redirect/file/Catastrophe_de_Courri%C3%A8res_-_Groupe_de_Sauveteurs,_Fosse_n%C2%B0_2.jpg?width=960","alt":"Mine rescuers gathered at Courrières pit number 2 during rescue operations after the March 10, 1906 explosion."},{"slot":"425:2","src":"https://commons.wikimedia.org/wiki/Special:Redirect/file/Catastrophe_de_Courri%C3%A8res_-_La_remonte_des_victimes.jpg?width=960","alt":"Rescue and recovery workers bringing victims to the surface during the 1906 Courrières mine disaster."},{"slot":"425:3","src":"https://commons.wikimedia.org/wiki/Special:Redirect/file/Catastrophe_de_Courri%C3%A8res_-_Les_rescap%C3%A9s_sont_soign%C3%A9s.jpg?width=1280","alt":"Survivors of the Courrières mine disaster receiving medical care after emerging from the mine in March 1906."},{"slot":"425:4","src":"https://commons.wikimedia.org/wiki/Special:Redirect/file/Catastrophe_de_Courri%C3%A8res_-_Arriv%C3%A9e_des_Sauveteurs_allemands.jpg?width=960","alt":"German mine rescuers arriving in northern France to assist after the 1906 Courrières mine disaster."},{"slot":"425:5","src":"https://commons.wikimedia.org/wiki/Special:Redirect/file/Catastrophe_de_Courri%C3%A8res_-_Appareil_Guglielminetti-Drager_(01).jpg?width=1280","alt":"A rescuer demonstrating Guglielminetti-Dräger breathing equipment associated with the 1906 Courrières mine rescue effort."},{"slot":"425:6","src":"https://commons.wikimedia.org/wiki/Special:Redirect/file/Courri%C3%A8res_1906_LeJ.jpg?width=960","alt":"Contemporary Le Petit Journal illustration depicting recovery operations after the Courrières mine disaster in March 1906."},{"slot":"425:7","src":"https://commons.wikimedia.org/wiki/Special:Redirect/file/Catastrophe_de_Courri%C3%A8res_-_Berthou,_le_dernier_survivant,_24_jours_dans_la_Mine_en_feu.jpg?width=960","alt":"Auguste Berthon, the Courrières miner who emerged alive on April 4, 1906 after approximately twenty-five days underground."},{"slot":"425:8","src":"https://commons.wikimedia.org/wiki/Special:Redirect/file/Catastrophe_de_Courri%C3%A8res_-_La_gr%C3%A8ve_des_mineurs.jpg?width=1280","alt":"Coal miners marching during the strike that followed the Courrières disaster in 1906."}];
function target(w,h){return w<=960?[w,h]:[960,Math.round(h*960/w)];}
function validate(a){
 const e=[];
 if(a?.schema!=="fv-courrieres-eight-v1"||a?.frozen_fixture_sha!=="948bc1b65b42799aa40cfdb810ddf6ffd80886b6")e.push("bad_header");
 if(!Array.isArray(a?.rows)||a.rows.length!==8)return e.concat("wrong_row_count");
 const seen=new Set();
 for(let i=0;i<8;i++){
  const r=a.rows[i],p=PINS[i];
  if(r?.slot!==p.slot||r?.post_id!==425||seen.has(r?.slot))e.push("slot_"+i); seen.add(r?.slot);
  if(r?.stored_original_url!==p.src||r?.stored_original_alt!==p.alt||r?.source_fixture_sha!=="948bc1b65b42799aa40cfdb810ddf6ffd80886b6")e.push("frozen_url_or_alt_"+i);
  const filename=decodeURIComponent((r?.stored_original_url||"").split("?")[0].split("/").pop()).replace(/_/g," ");
  if(filename!==r?.catalog?.title||!r?.catalog?.file_page_url.startsWith("https://commons.wikimedia.org/wiki/File:"))e.push("catalog_title_"+i);
  const wh=r?.catalog?.native_catalog_px||[];
  if(wh.length!==2||!wh.every(v=>Number.isInteger(v)&&v>0))e.push("catalog_native_px_"+i);
  else if(JSON.stringify(r?.conditional_sizing?.target_px)!==JSON.stringify(target(...wh))||r?.conditional_sizing?.max_width_px!==960||r?.conditional_sizing?.no_upscale!==true)e.push("bad_size_"+i);
  if(r?.catalog?.html_retriever!=="CATALOG_READABLE"||r?.catalog?.primary_catalog_item_independently_verified!==false)e.push("catalog_claim_"+i);
  const pr=r?.independent_redirect_probe;
  if(pr?.method!=="WEB_TEXT_RETRIEVER_NOT_HTTP_CLIENT"||pr?.status!=="TOOL_INACCESSIBLE")e.push("fake_probe_"+i);
  for(const k of ["origin_http_status","final_location","visitor_http_status","visitor_natural_px","visitor_encoded_bytes","visitor_broken"])if(pr?.[k]!==null)e.push("invented_network_result_"+i+"_"+k);
  if(r?.conditional_sizing?.derivative_created!==false)e.push("fake_derivative_"+i);
  for(const k of ["same_original_binary_verified","individual_rights_cleared","attribution_cleared","visual_approved","download_authorized","cache_authorized","wp_upload_authorized","block_rewrite_authorized"])if(r?.release_gate?.[k]!==false)e.push("unsafe_release_"+i+"_"+k);
 }
 const c=a?.counts||{};
 if(c.catalog_html_readable!==8||c.new_exact_source_research_slots!==8||c.actual_visitor_broken_confirmed!==0||c.actual_visitor_loaded_confirmed!==0||c.reported_42_broken_confirmed!==false||c.proposed_76_percent_wire_savings_measured!==false||c.oversize_wp_original_count!==15||c.oversize_wp_original_stored_bytes!==47096779)e.push("false_summary");
 return e;
}
module.exports={validate,PINS,target};
if(require.main===module){
 const fs=require("node:fs"),path=require("node:path");
 const file=path.join(__dirname,"courrieres_425_eight_catalog_20261110.json");
 const errors=validate(JSON.parse(fs.readFileSync(file,"utf8")));
 if(errors.length){console.error(errors.join("\n"));process.exit(1);}
 console.log("PASS: eight frozen sources, rights/caching HOLD, no invented origin/guest outcomes.");
}
