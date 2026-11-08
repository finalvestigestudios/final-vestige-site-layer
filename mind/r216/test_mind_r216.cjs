// Final Vestige Studios / R216 reproducible SOURCE-level integrity and genuinely mutated-artifact tests.
// Run from complete checkout: node mind/r216/test_mind_r216.cjs
// In non-Node V8, call module.exports.run(bundle), where bundle contains committed files as strings.
// These tests do NOT prove browser, WCAG2.2 AA, live WordPress sanitizer, affiliate approval, checkout,
// attribution, video rendering, actual sales, or qualified-human-session measurements.
"use strict";
const FILES={
 article:"the-word-that-refused-to-stay-its-color-STROOP-UNPUBLISHED.md",
 hub:"mind-archive-ink-and-attention-WP-PREVIEW-UNPUBLISHED.html",
 A:"zen12-ink-A-TEXT-UNPUBLISHED.html",
 B:"zen12-ink-B-OPTIONAL-42S-UNRENDERED.html",
 vtt:"zen12-ink-42s-concept.vtt",
 matrix:"STROOP-ZEN12-PROOF-COMMERCE-GATES.json",
 plan:"CONVERSION-FIRST-CREATOR-FIT-REVENUE-AB-ACCEPTANCE.md"
};
const reSource=(text)=>/https:\/\/psychclassics\.yorku\.ca\/Stroop\//.test(text);
function normalizedArm(html,optional){
 let s=html.replace(/^<!--[^]*?-->\s*/,"");
 if(optional) s=s.replace(/<details class="box" data-optional-film="concept-only">[\s\S]*?<\/details>\s*/,"");
 return s.replace(/\s+/g," ").trim();
}
function captionTimes(vtt){
 const cues=[];
 const exp=/(\d\d):(\d\d):(\d\d)\.(\d{3}) --> (\d\d):(\d\d):(\d\d)\.(\d{3})/g;
 for(const m of vtt.matchAll(exp)){
  const toMs=(a,b,c,d)=>((+a*3600)+(+b*60)+(+c))*1000+(+d);
  cues.push([toMs(m[1],m[2],m[3],m[4]),toMs(m[5],m[6],m[7],m[8])]);
 }
 return cues;
}
function validate(f){
 const problems=[];
 for(const key of Object.keys(FILES)){if(typeof f[key]!=="string" || f[key].length<120) problems.push("missing_or_empty_"+key);}
 if(problems.length) return problems;
 const article=f.article,hub=f.hub,A=f.A,B=f.B,vtt=f.vtt,plan=f.plan;
 let matrix;
 try{matrix=JSON.parse(f.matrix)}catch(e){return ["invalid_JSON_matrix"];}
 const check=(ok,id)=>{if(!ok) problems.push(id);};
 check(article.trim().split(/\s+/).length>=2000,"article_word_count");
 check(reSource(article)&&article.includes("https://doi.org/10.1037/h0054651"),"original_primary_study_source_missing");
 check(article.includes("47 seconds")&&article.includes("74.3 percent")&&article.includes("2.3 seconds")&&article.includes("110.3 seconds versus 63.3 seconds")&&article.includes("Experiment 1 enrolled 70")&&article.includes("Experiment 2 used 100"),"historic_stroop_comparison_corrupt");
 check(/did \*\*not\*\* regard as reliable/.test(article)&&article.includes("eight days"),"history_uncertainty_or_practice_missing");
 check(article.includes("not a medical test or commercial endorsement")&&article.includes("not a research result"),"historical_study_not_diagnosis_boundary_missing");
 check(article.includes("https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/"),"puysegur_evidence_bridge_missing");
 check(article.includes("not a therapeutic claim")&&article.includes("No earning link"),"science_commerce_separation_missing");
 check(article.includes("UNPUBLISHED")&&article.includes("No earning link"),"article_unpublished_context_missing");
 check(plan.split(/\s+/).length>=1300&&plan.includes("NOT COMPUTABLE")&&plan.includes("qualified_human_sessions"),"paid_measurement_plan_missing");
 const forbid=/<(?:script|form|iframe|input|video|audio)\b|\bonclick\s*=|\bonload\s*=|googletagmanager|dataLayer|fingerprint/i;
 for(const key of ["hub","A","B"]){check(!forbid.test(f[key]),"unauthorized_form_script_or_embed_"+key);}
 for(const key of ["hub","A","B"]){
   const h=f[key];
   const buttons=[...h.matchAll(/<button\b[^>]*>/gi)].map(m=>m[0]);
   check(buttons.length>=1&&buttons.every(tag=>/\bdisabled\b/.test(tag)&&/\btype="button"/.test(tag)),"active_or_missing_buy_control_"+key);
   check(!/<a\b[^>]*href="https?:\/\/(?:www\.)?(?:zen12|inspire3|affiliates\.inspire3|hypnosislive|brainwaveshots)\./i.test(h),"active_merchant_link_"+key);
   check(h.includes("If you purchase through an approved affiliate link in a future guide, Final Vestige may earn a commission at no additional cost to you."),"commission_disclosure_missing_"+key);
   const disclosureAt=h.indexOf("If you purchase through an approved affiliate link");
   const buttonAt=h.search(/<button\b/);
   check(disclosureAt>=0&&buttonAt>disclosureAt&&buttonAt-disclosureAt<450,"commission_disclosure_not_adjacent_"+key);
   check(h.includes("https://finalvestige.com/focus/"),"existing_focus_path_missing_"+key);
 }
 check(hub.includes("PERCEPTION &amp; ATTENTION")&&hub.includes("HISTORY OF SUGGESTION")&&hub.includes("PRACTICE &amp; REFLECTION")&&hub.includes("TOOLS UNDER REVIEW"),"four_stream_archive_missing");
 check(hub.includes('role="img"')&&hub.includes("<desc ")&&hub.includes("prefers-reduced-motion")&&hub.includes("focus-visible"),"hub_accessibility_source_gates_missing");
 check(A.includes("not a randomized or blinded clinical trial")&&A.includes("no second signup form"),"buyer_free_trial_limit_missing");
 check(B.includes('data-optional-film="concept-only"')&&B.includes("NOT been timed")&&B.includes("NOT been generated"),"optional_video_concept_missing");
 check(B.includes("<title id=")&&B.includes("<desc id=")&&B.includes("Original time-coded narration / transcript"),"film_poster_transcript_accessibility_missing");
 check(normalizedArm(A,false)===normalizedArm(B,true),"AB_copy_not_equivalent");
 const cues=captionTimes(vtt);
 check(vtt.startsWith("WEBVTT")&&cues.length===5&&cues[0]?.[0]===0&&cues[4]?.[1]===42000&&cues.every((x,i)=>x[1]>x[0]&&(i===0||cues[i-1][1]===x[0])),"VTT_cues_or_duration_invalid");
 check(vtt.includes("Stroop")&&vtt.includes("Zen12")&&vtt.includes("worth paying for"),"VTT_transcript_key_points_missing");
 check(matrix.sources?.length>=18&&matrix.claims?.length>=22&&matrix.gates?.length>=16,"matrix_inadequate_records");
 const ids=new Set((matrix.sources||[]).map(x=>x.id));
 check((matrix.claims||[]).every(x=>x.source_ids?.length&&x.source_ids.every(id=>ids.has(id))),"claim_source_ids_broken");
 check(matrix.status==="UNPUBLISHED_NOT_SELLING"&&matrix.permissions?.affiliate_activation===false&&matrix.permissions?.publishing===false&&matrix.permissions?.tracking_script===false,"commerce_release_flags_unsafe");
 const critical=["G01","G02","G03","G04","G07","G08","G09","G11","G14"];
 const gates=matrix.gates||[];
 check(gates.every(g=>typeof g.id==="string")&&new Set(gates.map(g=>g.id)).size===gates.length,"duplicate_or_invalid_gate_id");
 check(critical.every(id=>gates.filter(g=>g.id===id).length===1&&gates.find(g=>g.id===id).status==="HARD_HOLD"),"critical_partner_or_release_gate_missing_duplicate_or_falsified");
 check(matrix.measurement?.status==="NOT_COMPUTABLE"&&matrix.measurement?.event_names?.includes("cleared_affiliate_conversion"),"revenue_state_unverified");
 check(plan.includes("R210")&&plan.includes("existing Jetpack")&&plan.includes("Grok")&&plan.includes("TASK-008"),"governance_or_funnel_plan_missing");
 check(plan.includes("realized_net = ")&&plan.includes("qualified_traffic_RPM")&&plan.includes("7d and 30d"),"revenue_math_or_cohort_missing");
 check(plan.includes("360/390/768/1440/1920")&&plan.includes("WP sanitizer")&&plan.includes("keyboard"),"real_browser_pending_gates_missing");
 return problems.filter(Boolean);
}
function mutators(){
 return [
 ["remove_disabled_A", f=>({...f,A:f.A.replace('<button type="button" disabled','<button type="button"')})],
 ["remove_disclosure_A",f=>({...f,A:f.A.replace("If you purchase through an approved affiliate link in a future guide, Final Vestige may earn a commission at no additional cost to you.","")})],
 ["script_injection_A",f=>({...f,A:f.A.replace("</section>","<script>track()</script></section>")})],
 ["merchant_href_A",f=>({...f,A:f.A.replace("</section>",'<a href="https://zen12.com/hnp">Buy</a></section>')})],
 ["fake_signup_B",f=>({...f,B:f.B.replace("</section>","<form><input type=email></form></section>")})],
 ["drop_optional_film_B",f=>({...f,B:f.B.replace(/<details class="box" data-optional-film="concept-only">[\s\S]*?<\/details>/,"")})],
 ["change_B_headline",f=>({...f,B:f.B.replace("What are you actually buying when you buy twelve minutes of focus?","Guaranteed IQ improvement in 12 minutes")})],
 ["autoplay_B",f=>({...f,B:f.B.replace("</section>",'<video autoplay src="promo.mp4"></video></section>')})],
 ["remove_focus_hub",f=>({...f,hub:f.hub.replace(/https:\/\/finalvestige\.com\/focus\//g,"#")})],
 ["activate_hub",f=>({...f,hub:f.hub.replace('<button type="button" disabled','<button type="button"')})],
 ["duplicate_form_hub",f=>({...f,hub:f.hub.replace("</section>","<form><input type=email></form></section>")})],
 ["remove_article_primary",f=>({...f,article:f.article.replace(/https:\/\/psychclassics\.yorku\.ca\/Stroop\//g,"")})],
 ["distort_primary_result",f=>({...f,article:f.article.replace("47 seconds","470 seconds")})],
 ["erase_historic_limit",f=>({...f,article:f.article.replace("did **not** regard as reliable","regarded as reliable")})],
 ["erase_publication_gate",f=>({...f,matrix:f.matrix.replace('"publishing": false','"publishing": true')})],
 ["fake_affiliate_approval",f=>({...f,matrix:f.matrix.replace('"affiliate_activation": false','"affiliate_activation": true')})],
 ["fake_critical_gate",f=>({...f,matrix:f.matrix.replace('"id": "G01",\n      "criterion": "Final Vestige-specific partner acceptance signed/verified",\n      "owner": "FOUNDER_MIND",\n      "status": "HARD_HOLD"','"id": "G01",\n      "criterion": "Final Vestige-specific partner acceptance signed/verified",\n      "owner": "FOUNDER_MIND",\n      "status": "VERIFIED"')})],
 ["break_source_ref",f=>({...f,matrix:f.matrix.replace('"S01"','"ZZ0"')})],
 ["bad_VTT_duration",f=>({...f,vtt:f.vtt.replace("00:00:42.000","00:00:40.000")})],
 ["erase_plan_NC",f=>({...f,plan:f.plan.replace(/NOT COMPUTABLE/g,"ZERO")})],
 ["erase_film_transcript",f=>({...f,B:f.B.replace("Original time-coded narration / transcript","Voice-only advertisement")})],
 ["remove_archive_svg_accessibility",f=>({...f,hub:f.hub.replace('role="img"','role="presentation"')})],
 ["remove_article_word_count",f=>({...f,article:f.article.slice(0,2100)})],
 ["remove_A_focus",f=>({...f,A:f.A.replace("https://finalvestige.com/focus/","#")})],
 ["delete_critical_gate_G11",f=>({...f,matrix:JSON.stringify({...JSON.parse(f.matrix),gates:JSON.parse(f.matrix).gates.filter(g=>g.id!=="G11")})})],
 ["rename_critical_gate_G11",f=>({...f,matrix:JSON.stringify({...JSON.parse(f.matrix),gates:JSON.parse(f.matrix).gates.map(g=>g.id==="G11"?{...g,id:"G11_RENAMED"}:g)})})],
 ["duplicate_critical_gate_G11",f=>({...f,matrix:JSON.stringify({...JSON.parse(f.matrix),gates:[...JSON.parse(f.matrix).gates,JSON.parse(f.matrix).gates.find(g=>g.id==="G11")]})})],
 ["remove_error_adjusted_historic_qualifier",f=>({...f,article:f.article.replace("110.3 seconds versus 63.3 seconds","just guesses")})]
 ];
}
function run(bundle){
 const baseline=validate(bundle);
 const cases=mutators().map(([name,mutate])=>{const changed=mutate({...bundle});const violations=validate(changed);return {name,detected:violations.length>0,violations};});
 return {baseline,passed:baseline.length===0,mutations_total:cases.length,mutations_rejected:cases.filter(x=>x.detected).length,missed:cases.filter(x=>!x.detected),cases};
}
if(typeof module!=="undefined"&&module.exports) module.exports={FILES,validate,run};
if(typeof require!=="undefined"&&require.main===module){
 const fs=require("node:fs"),path=require("node:path");
 const bundle=Object.fromEntries(Object.entries(FILES).map(([k,n])=>[k,fs.readFileSync(path.join(__dirname,n),"utf8")]));
 const report=run(bundle);
 process.stdout.write(JSON.stringify(report,null,2)+"\n");
 process.exitCode=report.passed&&report.mutations_rejected===report.mutations_total?0:1;
}
