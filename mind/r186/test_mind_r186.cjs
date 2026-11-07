/* R186 non-network source regression. Run: node mind/r186/test_mind_r186.cjs
   Exact committed content is authoritative; no CMS or merchant writes. */
"use strict";
const files={
 article:"white-bear-thought-suppression-INVESTIGATION-UNPUBLISHED.md",
 matrix:"source-verified-seller-claims-and-purchase-gates.json",
 A:"zen12-A-independent-text-UNPUBLISHED.html",
 B:"zen12-B-optional-42s-concept-UNPUBLISHED.html",
 hub:"mind-archive-FOUR-STREAM-WORDPRESS-DRAFT-UNPUBLISHED.html",
 plan:"ONE-OFFER-CONVERSION-REVENUE-AND-AB-ACCEPTANCE.md",
 errata:"../r185/the-question-that-changed-the-crash-INVESTIGATION-UNPUBLISHED.md"
};
function validate(f) {
 const fails=[],checks=[];
 function ok(name,bool){checks.push(name);if(!bool)fails.push(name);}
 const a=f.article||"",m=f.matrix||"",A=f.A||"",B=f.B||"",h=f.hub||"",p=f.plan||"",e=f.errata||"";
 let data;try{data=JSON.parse(m)}catch(_){data=null;}
 ok("all seven source artifacts available",Object.keys(files).every(k=>typeof f[k]==="string"&&f[k].length>1000));
 ok("science cites Wegner 1987 primary",a.includes("3612492/")&&a.includes("1987")&&a.includes("rebound"));
 ok("science cites cognitive load paper",a.includes("8295117/")&&a.includes("nine-digit"));
 ok("article does not sell product",a.includes("no affiliate recommendation")&&a.includes("not proof")&& !/https?:\/\/(www\.)?awin1\.com/i.test(a));
 ok("article recognizes original limits",a.includes("after")&&a.includes("experimental")&&a.includes("not")&&a.includes("treatment"));
 ok("article cites thought suppression review",a.includes("annurev.psych.51.1.59"));
 ok("R185 date corrected",e.includes("More than fifty years later")&&!e.includes("Forty-eight years later"));
 ok("R185 primary full-text trail supplied",e.includes("LoftusPalmer_ReconstructionAuto_JVLVB1974.pdf"));
 ok("JSON parses",!!data);
 ok("affiliate activation false",data?.affiliate_activation===false);
 ok("earning link absent",data?.affiliate_earning_url===null);
 ok("verified paid orders absent",data?.verified_merchant_orders===null);
 ok("qualified humans not made up",data?.qualified_human_sessions===null);
 ok("net revenue not fabricated",data?.realized_net_revenue===null);
 ok("source coverage",data?.evidence?.length>=12);
 ok("claim decisions present",data?.claims?.length>=23);
 ok("release gates explicit",data?.gates?.length>=10);
 ok("publisher authorization closed",data?.gates?.find(x=>x.id==="publisher_identity")?.state==="BLOCKED");
 ok("seller evidence precise",m.includes("https://zen12.com/hnp")&&m.includes("https://hypnosislive.com/mental-skills/total-focus")&&m.includes("24.44"));
 ok("FTC source contract",m.includes("ftcs-endorsement-guides")&&m.includes("health-products-compliance-guidance"));
 ok("HTML no script, iframe or form",![A,B,h].some(s=>/<(?:script|iframe|form)\b/i.test(s)));
 ok("HTML no inline JS or autoplay",![A,B,h].some(s=>/\bon(?:click|load|error|mouseover)\s*=|autoplay|javascript:/i.test(s)));
 ok("CTA native disabled BOTH", [A,B].every(s=>(s.match(/<button type="button" disabled aria-disabled="true">/g)||[]).length===1));
 ok("disclosure immediately before button BOTH",[A,B].every(s=>/class="disclosure"[^>]*>[\s\S]*?may earn a commission[\s\S]*?<\/p>\s*<button type="button" disabled/i.test(s)));
 ok("no commission earnings URL in HTML",![A,B,h].some(s=>/awin1\.com|clickbank|[?&](hop|affid|affiliate_id|ref)=|data-earning-url=|rel="sponsored"/i.test(s)));
 ok("only one free signup destination", [A,B,h].every(s=>s.includes('https://finalvestige.com/focus/'))&&![A,B,h].some(s=>(s.match(/<form\b/gi)||[]).length>0));
 ok("seller link is informational", [A,B].every(s=>s.includes('href="https://zen12.com/hnp" rel="noopener noreferrer"')));
 ok("no active merchant buying anchor",[A,B].every(s=>!/<a\b[^>]*href="https?:\/\/(?:www\.)?(?:zen12\.com|affiliates\.inspire3\.com)\/[^"]*"[^>]*>\s*(?:Buy|Get Started|Purchase)/i.test(s)));
 ok("no remote media or active film",[A,B,h].every(s=>!/<(?:video|audio|source|track)\b/i.test(s)));
 ok("prototype noindex",[A,B,h].every(s=>s.includes('content="noindex,nofollow"')));
 ok("A/B only one film difference",B.replace(/<section id="optional-film"[\s\S]*?<\/section>/,"")===A);
 ok("B film truly 42s transcript and accessible poster",B.includes("00:37–00:42")&&B.includes("Read the complete 42-second transcript")&&B.includes("aria-label="));
 ok("B source-first and no autoplay",B.includes("No playback, autoplay")&&B.includes("NO ACTIVE AFFILIATE LINK"));
 ok("hub four editorial streams",["PERCEPTION & ATTENTION","HISTORY OF SUGGESTION","PRACTICE & REFLECTION","TOOLS UNDER REVIEW"].every(t=>h.includes(t)));
 ok("hub focus one-list declaration",h.includes("One existing Jetpack/Dispatch subscriber list"));
 ok("plan explicitly segregates paid orders",p.includes("affiliate_click")&&p.includes("merchant_confirmed_purchase")&&p.includes("NOT COMPUTABLE"));
 ok("plan creator IDs withheld",p.includes("No actual Grok public post URL")&&p.includes("TASK-008"));
 ok("plan no release or paid services",p.includes("No live WordPress")&&p.includes("No product has independently confirmed paid commissions"));
 return {checks,failures:fails,passed:checks.length-fails.length};
}
function mutations(f){
 const edits=[
 ["activate merchant button","A",s=>s.replace('type="button" disabled','type="button"')],
 ["remove A disclosure","A",s=>s.replace('may earn a commission','might offer a free cookie')],
 ["activate B merchant button","B",s=>s.replace('type="button" disabled','type="button"')],
 ["remove B disclosure","B",s=>s.replace('may earn a commission','maybe paid')],
 ["inject tracker","A",s=>s.replace("</body>",'<script src="https://tracker.example/a.js"></script></body>')],
 ["inject form","hub",s=>s.replace("</body>",'<form action="/signup"><input></form></body>')],
 ["insert earning URL","B",s=>s.replace("</body>",'<a href="https://www.awin1.com/cread.php?ref=12">Earn</a></body>')],
 ["pretend approved","matrix",s=>s.replace('"affiliate_activation": false','"affiliate_activation": true')],
 ["invent URL","matrix",s=>s.replace('"affiliate_earning_url": null','"affiliate_earning_url": "https://fake.test"')],
 ["invent sale","matrix",s=>s.replace('"verified_merchant_orders": null','"verified_merchant_orders": 2')],
 ["invent denominator","matrix",s=>s.replace('"qualified_human_sessions": null','"qualified_human_sessions": 23')],
 ["invent money","matrix",s=>s.replace('"realized_net_revenue": null','"realized_net_revenue": 300')],
 ["delete source","article",s=>s.replace("3612492/","0000000/")],
 ["erase caveat","article",s=>s.replace("no affiliate recommendation","paid recommendation")],
 ["revert date","errata",s=>s.replace("More than fifty years later","Forty-eight years later")],
 ["erase primary source","errata",s=>s.replace("LoftusPalmer_ReconstructionAuto_JVLVB1974.pdf","missing.pdf")],
 ["remove video captions","B",s=>s.replace("00:37–00:42","00:37–xx:xx")],
 ["break no-js equivalence","A",s=>s.replace("A free timer be enough?","A paid timer is necessary?")],
 ["mismatch exact seller","matrix",s=>s.replace("https://zen12.com/hnp","https://wrong.example/offer")],
 ["remove merchant gate","matrix",s=>s.replace('"state": "BLOCKED"','"state": "APPROVED"')]
 ]; let detected=0; const failures=[];
 for(const [name,key,edit] of edits){const g={...f,[key]:edit(f[key])};if(g[key]===f[key]){failures.push(name+": mutation was a no-op");continue;}const result=validate(g);if(!result.failures.length)failures.push(name+": baseline validator missed alteration");else detected++;}
 return {total:edits.length,detected,failures};
}
module.exports={files,validate,mutations};
if(typeof require==="function"&&typeof process==="object"&&require.main===module){
 const fs=require("fs"),path=require("path"),input={};
 for(const [k,v] of Object.entries(files))input[k]=fs.readFileSync(path.resolve(__dirname,v),"utf8");
 const pos=validate(input),neg=mutations(input);
 console.log(JSON.stringify({assertions:pos.checks.length,passed:pos.passed,failed:pos.failures,mutations:neg},null,2));
 if(pos.failures.length||neg.failures.length||neg.detected!==neg.total)process.exitCode=1;
}
