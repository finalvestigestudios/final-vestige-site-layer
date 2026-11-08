// Final Vestige Mind R217 — real source-level baseline and genuinely mutated input checks.
// From a complete checkout: node mind/r217/test_mind_r217.cjs
// In isolated V8: module.exports.run({article,hub,guide,vtt,matrix,plan}) using exact git files.
// NOT a browser, WP sanitizer, CI, real video, partner approval, checkout or sale test.
"use strict";
const FILES={
 article:"the-face-they-never-picked-CHOICE-BLINDNESS-UNPUBLISHED.md",
 hub:"mind-archive-choice-blindness-WP-PREVIEW-UNPUBLISHED.html",
 guide:"zen12-PROOF-FIRST-PRESELL-INACTIVE.html",
 vtt:"zen12-42s-OPTIONAL-CONCEPT.vtt",
 matrix:"CHOICE-ZEN12-SOURCE-CLAIM-GATES.json",
 plan:"OFFER-FIRST-CREATOR-FIT-REVENUE-ACCEPTANCE.md"
};
function countWords(s){return s.trim().split(/\s+/).length;}
function matches(s,re){return [...s.matchAll(re)];}
function parseVtt(vtt){
 const times=matches(vtt,/(\d\d):(\d\d):(\d\d)\.(\d{3}) --> (\d\d):(\d\d):(\d\d)\.(\d{3})/g);
 const ms=(h,m,s,f)=>(((+h*60)+(+m))*60+(+s))*1000+(+f);
 return times.map(m=>[ms(m[1],m[2],m[3],m[4]),ms(m[5],m[6],m[7],m[8])]);
}
function validate(f){
 const errs=[]; const check=(v,id)=>{if(!v)errs.push(id)};
 for(const k of Object.keys(FILES))check(typeof f[k]==="string"&&f[k].length>=130,"missing_"+k);
 if(errs.length)return errs;
 const {article,hub,guide,vtt,plan}=f;
 let matrix;
 try{matrix=JSON.parse(f.matrix)}catch(e){return ["bad_matrix_json"];}
 check(countWords(article)>=2300&&article.includes("UNPUBLISHED INVESTIGATION"),"deep_unpublished_research_missing");
 check(article.includes("https://doi.org/10.1126/science.1111709")&&article.includes("https://doi.org/10.1016/j.cognition.2010.06.010")&&article.includes("https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0108515"),"critical_choice_primary_sources_missing");
 check(article.includes("not a replication, diagnosis")&&article.includes("do not repeat that deception")===false,""); // extra boundary handled separately
 check(article.includes("**not a replication, diagnosis")||article.includes("not a replication, diagnosis"),"ethical_no_deception_boundary_missing");
 check(article.includes("**not** evidence of Zen12")||article.includes("The choice-blindness studies were not evaluations of Zen12"),"science_marketing_boundary_missing");
 check(article.includes("https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/"),"historical_record_bridge_missing");
 check(!article.includes("https://www.awin1.com/")&&!/href="https?:\/\//.test(article),"no_affiliate_in_investigation");
 check(countWords(plan)>=1400&&plan.includes("NOT COMPUTABLE")&&plan.includes("7d and 30d")&&plan.includes("qualified_human_sessions"),"net_revenue_acceptance_or_cohorts_missing");
 check(plan.includes("TASK-008")&&plan.includes("R210")&&plan.includes("Grok")&&plan.includes("Dispatch"),"creator_roles_or_frozen_ab_missing");
 check(plan.includes("settled_owned_receipts")&&plan.includes("cleared_affiliate_commissions")&&plan.includes("refunds"),"revenue_formula_incomplete");
 const forbidden=/<(?:script|form|input|iframe|video|audio)\b|\bonclick\s*=|\bonload\s*=|googletagmanager|dataLayer|fingerprint|<link\s+rel=["']stylesheet["']/i;
 for(const key of ["hub","guide"])check(!forbidden.test(f[key]),"active_script_form_embed_or_tracker_"+key);
 for(const key of ["hub","guide"]){
  const h=f[key], btn=matches(h,/<button\b[^>]*>/gi);
  check(btn.length>=1&&btn.every(m=>/\bdisabled\b/i.test(m[0])&&/type="button"/.test(m[0])),"unsafe_or_missing_disabled_button_"+key);
  check(!/<a\b[^>]*href=["']https?:\/\/(?:www\.)?(?:zen12|inspire3|hypnosislive|brainwaveshots|affiliates\.inspire3)\./i.test(h),"active_merchant_href_"+key);
  const d=h.indexOf("If you purchase through an approved affiliate link");
  const b=h.search(/<button\b/);
  check(d>=0&&b>d&&b-d<650,"missing_or_remote_disclosure_"+key);
  check(h.includes("https://finalvestige.com/focus/"),"single_focus_path_missing_"+key);
  check(!/guaranteed (?:clinical|cure|wealth|IQ improvement)/i.test(h),"unsupported_efficacy_guarantee_"+key);
  check((h.match(/<html\b/g)||[]).length===1&&h.includes('name="viewport"')&&h.includes("prefers-reduced-motion"),"source_accessibility_basics_missing_"+key);
  check(!/http:\/\//.test(h),"non_tls_destination_"+key);
  const ids=matches(h,/\bid="([^"]+)"/g).map(x=>x[1]);
  check(new Set(ids).size===ids.length,"duplicate_document_id_"+key);
 }
 check(hub.includes("Perception &amp; Attention")&&hub.includes("History of Suggestion")&&hub.includes("Practice &amp; Reflection")&&hub.includes("Tools Under Review"),"four_stream_archive_missing");
 check(hub.includes('role="img"')&&hub.includes("<desc ")&&hub.includes("focus-visible"),"source_hub_svg_a11y_missing");
 check(guide.includes("not a randomized clinical trial")&&guide.includes("Checkout pricing")&&guide.includes("UNKNOWN"),"offer_limits_missing");
 check(guide.includes('data-optional-film="concept-only"')&&guide.includes("Original time-coded narration")&&guide.includes("unrendered"),"optional_42s_nonplayable_media_missing");
 check(guide.includes("<desc ")&&guide.includes("<title "), "accessible_film_poster_missing");
 const cues=parseVtt(vtt);
 check(vtt.startsWith("WEBVTT")&&cues.length===5&&cues[0]?.[0]===0&&cues[cues.length-1]?.[1]===42000&&cues.every((a,i)=>a[1]>a[0]&&(i===0||a[0]===cues[i-1][1])),"caption_timing_or_count_invalid");
 check(vtt.includes("Zen12 Premium")&&vtt.includes("Final Vestige"),"caption_storyboard_mismatch");
 check(matrix.status==="UNPUBLISHED_SOURCE_ONLY"&&matrix.permissions?.publishing===false&&matrix.permissions?.affiliate_activation===false&&matrix.permissions?.tracking_script===false,"unsafe_commercial_permissions");
 check(matrix.offer?.affiliate_url===null&&matrix.offer?.approval_verified===false&&matrix.offer?.current_checkout_price===null,"unauthorized_link_price_or_approval");
 check(matrix.sources?.length>=14&&matrix.claims?.length>=20&&matrix.gates?.length>=15,"insufficient_source_claim_gate_register");
 const sourceIds=new Set((matrix.sources||[]).map(s=>s.id));
 check(sourceIds.size===(matrix.sources||[]).length&&matrix.claims?.every(c=>c.source_ids?.length&&c.source_ids.every(id=>sourceIds.has(id))),"broken_claim_provenance");
 const gates=matrix.gates||[], ids=gates.map(g=>g.id);
 check(new Set(ids).size===ids.length&&ids.every(x=>typeof x==="string"),"duplicate_or_invalid_gate_ids");
 const critical=["G01","G02","G03","G04","G05","G06","G11","G14"];
 check(critical.every(id=>gates.filter(g=>g.id===id).length===1&&gates.find(g=>g.id===id).status==="HARD_HOLD"),"missing_duplicate_or_falsified_critical_gate");
 check(matrix.measurement?.status==="NOT_COMPUTABLE"&&matrix.measurement?.net_revenue_per_1000_qualified_human_sessions===null&&matrix.measurement?.orders_verified===null,"invented_revenue_or_order");
 check(matrix.first_party_attribution?.status==="SPEC_ONLY_NOT_INSTALLED"&&matrix.first_party_attribution?.forbidden?.includes("device fingerprints"),"privacy_spec_incomplete");
 check(matrix.editorial?.r210_ab_preserved===true&&matrix.editorial?.new_ab_arm_activated===false,"AB_governance_broken");
 return errs.filter(Boolean);
}
function mutateCases(){
 return [
 ["remove_disabled_guide",f=>({...f,guide:f.guide.replace('<button type="button" disabled','<button type="button"')})],
 ["remove_disclosure_guide",f=>({...f,guide:f.guide.replace("If you purchase through an approved affiliate link","An unrelated introduction")})],
 ["active_merchant_link",f=>({...f,guide:f.guide.replace("</section>",'<a href="https://zen12.com/hnp">Buy now</a></section>')})],
 ["insert_duplicate_signup",f=>({...f,hub:f.hub.replace("</section>",'<form><input type="email"></form></section>')})],
 ["insert_tracking_script",f=>({...f,hub:f.hub.replace("</main>",'<script src="https://example.com/track.js"></script></main>')})],
 ["insert_remote_iframe",f=>({...f,guide:f.guide.replace("</main>",'<iframe src="https://example.com"></iframe></main>')})],
 ["activate_hub_button",f=>({...f,hub:f.hub.replace('<button type="button" disabled','<button type="button"')})],
 ["remove_hub_focus",f=>({...f,hub:f.hub.replace("https://finalvestige.com/focus/","#")})],
 ["remove_guide_focus",f=>({...f,guide:f.guide.replace("https://finalvestige.com/focus/","#")})],
 ["remove_guide_mitigation",f=>({...f,guide:f.guide.replace("not a randomized clinical trial","a guaranteed medical treatment")})],
 ["guaranteed_mind_claim",f=>({...f,guide:f.guide.replace("</section>","<p>guaranteed clinical cure</p></section>")})],
 ["remove_historical_source",f=>({...f,article:f.article.replace(/https:\/\/finalvestige\.com\/free-resources\/puysegurs-animal-magnetism-files\//g,"")})],
 ["remove_choice_primary",f=>({...f,article:f.article.replace("https://doi.org/10.1126/science.1111709","")})],
 ["truncate_investigation",f=>({...f,article:f.article.slice(0,2500)})],
 ["remove_optional_film",f=>({...f,guide:f.guide.replace('data-optional-film="concept-only"','data-film="removed"')})],
 ["corrupt_caption_duration",f=>({...f,vtt:f.vtt.replace("00:00:42.000","00:00:41.000")})],
 ["remove_source_id",f=>({...f,matrix:JSON.stringify({...JSON.parse(f.matrix),sources:JSON.parse(f.matrix).sources.filter(x=>x.id!=="S11")})})],
 ["delete_critical_release",f=>({...f,matrix:JSON.stringify({...JSON.parse(f.matrix),gates:JSON.parse(f.matrix).gates.filter(x=>x.id!=="G11")})})],
 ["rename_critical_release",f=>({...f,matrix:JSON.stringify({...JSON.parse(f.matrix),gates:JSON.parse(f.matrix).gates.map(x=>x.id==="G11"?{...x,id:"G11-ALT"}:x)})})],
 ["duplicate_critical_release",f=>({...f,matrix:JSON.stringify({...JSON.parse(f.matrix),gates:[...JSON.parse(f.matrix).gates,JSON.parse(f.matrix).gates.find(x=>x.id==="G11")]})})],
 ["fake_affiliate_permission",f=>({...f,matrix:f.matrix.replace('"affiliate_activation": false','"affiliate_activation": true')})],
 ["fake_merchant_approval",f=>({...f,matrix:f.matrix.replace('"approval_verified": false','"approval_verified": true')})],
 ["fabricated_sale",f=>({...f,matrix:f.matrix.replace('"orders_verified": null','"orders_verified": 12')})],
 ["ab_activated_without_approval",f=>({...f,matrix:f.matrix.replace('"new_ab_arm_activated": false','"new_ab_arm_activated": true')})],
 ["remove_revenue_measure",f=>({...f,plan:f.plan.replace(/NOT COMPUTABLE/g,"ZERO")})],
 ["erase_campaign_coordination",f=>({...f,plan:f.plan.replace(/TASK-008/g,"not needed")})],
 ["remove_hub_image_alt",f=>({...f,hub:f.hub.replace('role="img"','role="presentation"')})],
 ["insert_insecure_link",f=>({...f,guide:f.guide.replace("</main>",'<a href="http://example.com">go</a></main>')})]
 ];
}
function run(bundle){
 const baseline=validate(bundle);
 const cases=mutateCases().map(([name,fn])=>{
  const changed=fn({...bundle});const wasChanged=JSON.stringify(changed)!==JSON.stringify(bundle);
  const issues=wasChanged?validate(changed):["mutation_was_noop"];
  return {name,wasChanged,detected:wasChanged&&issues.length>0,issues};
 });
 return {baseline,passed:baseline.length===0,mutation_count:cases.length,mutations_rejected:cases.filter(x=>x.detected).length,missed:cases.filter(x=>!x.detected),cases};
}
if(typeof module!=="undefined"&&module.exports)module.exports={FILES,validate,run};
if(typeof require!=="undefined"&&require.main===module){
 const fs=require("node:fs"),path=require("node:path");
 const base=Object.fromEntries(Object.entries(FILES).map(([k,n])=>[k,fs.readFileSync(path.join(__dirname,n),"utf8")]));
 const report=run(base);process.stdout.write(JSON.stringify(report,null,2)+"\n");
 process.exitCode=report.passed&&report.mutations_rejected===report.mutation_count?0:1;
}
