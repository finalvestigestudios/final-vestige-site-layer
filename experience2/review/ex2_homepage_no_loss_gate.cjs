"use strict";
/** Final Vestige EX2: READ-ONLY WordPress Page 6 loss-prevention gate.
 * Two LOCAL editor-source files only; never writes files, WordPress or network.
 * Structural PASS is NEVER production release permission.
 */
const REQUIRED_IDS=["fv-hf-title","fv-hf-chronicle","fv-hf-evidence","fv-hf-inquiry","fv-hf-method-title","fv-hf-observer","fv-hf-mind-title"];
const count=(s,re)=>[...s.matchAll(re)].length;
function inventory(s){
 if(typeof s!=="string"||!s.length)throw Error("Source required");
 const margins=[...s.matchAll(/<span\b[^>]*\bclass\s*=\s*["'][^"']*\bfv-margin-strip__item\b[^"']*["'][^>]*>([\s\S]*?)<\/span>/gi)].map(m=>m[1].trim());
 const images=[...s.matchAll(/<img\b[^>]*>/gi)].map(m=>(m[0].match(/\bsrc\s*=\s*["']([^"']+)["']/i)||[])[1]||"");
 const foundIds=[...s.matchAll(/\bid\s*=\s*["']([^"']+)["']/gi)].map(m=>m[1]);
 const ids=Object.fromEntries(REQUIRED_IDS.map(id=>[id,foundIds.filter(v=>v===id).length]));
 const chapterNav=count(s,/\bclass\s*=\s*["'][^"']*\bfv-hf__chapter-nav\b[^"']*["']/gi);
 const jetpack=count(s,/<!--\s*wp:jetpack\/subscriptions\b/gi);
 const focus=count(s,/<a\b[^>]*\bhref\s*=\s*["'](?:https:\/\/finalvestige\.com)?\/focus\/?(?:\?[^"']*)?["']/gi);
 return {margins,images,ids,chapterNav,jetpack,focus};
}
function admit(published,proposed){
 const b=inventory(published),a=inventory(proposed),f=[];
 if(b.margins.length!==72)f.push("baseline_margins_not_72");
 if(a.margins.length!==72)f.push("candidate_margins_not_72");
 if(JSON.stringify(a.margins)!==JSON.stringify(b.margins))f.push("margin_text_or_order_changed");
 if(b.chapterNav!==1)f.push("baseline_chapter_nav_not_one");
 if(a.chapterNav!==1)f.push("candidate_nav_missing_or_duplicated");
 for(const id of REQUIRED_IDS){if(b.ids[id]!==1)f.push("baseline_anchor_"+id);if(a.ids[id]!==1)f.push("candidate_anchor_"+id);}
 if(b.jetpack!==1)f.push("baseline_jetpack_not_one");
 if(a.jetpack!==1)f.push("candidate_jetpack_missing_or_duplicated");
 if(b.focus<1)f.push("baseline_focus_missing");
 if(a.focus<b.focus)f.push("candidate_focus_decreased");
 let images=[...a.images];for(const src of b.images){let i=images.indexOf(src);if(i<0)f.push("source_image_removed");else images.splice(i,1);}
 if(images.length)f.push("new_image_needs_rights_and_transfer_QA");
 if(a.images.includes(""))f.push("image_without_src");
 return {status:f.length?"HOLD":"STRUCTURAL_PASS_RELEASE_HOLD",failures:[...new Set(f)],
 before:{margins:b.margins.length,chapterNav:b.chapterNav,ids:b.ids,jetpack:b.jetpack,images:b.images.length,focus:b.focus},
 after:{margins:a.margins.length,chapterNav:a.chapterNav,ids:a.ids,jetpack:a.jetpack,images:a.images.length,focus:a.focus}};
}
if(typeof module!=="undefined"&&module.exports)module.exports={inventory,admit,REQUIRED_IDS};
if(typeof require==="function"&&typeof module!=="undefined"&&require.main===module){
 const fs=require("node:fs"),argv=process.argv.slice(2);
 if(argv.length!==2||argv.some(x=>/^https?:\/\//i.test(x))){console.error("Usage: node ex2_homepage_no_loss_gate.cjs PUBLISHED_RAW.txt PROPOSED_RAW.txt");process.exit(2);}
 const result=admit(fs.readFileSync(argv[0],"utf8"),fs.readFileSync(argv[1],"utf8"));console.log(JSON.stringify(result,null,2));
 process.exit(result.status==="STRUCTURAL_PASS_RELEASE_HOLD"?0:1);
}