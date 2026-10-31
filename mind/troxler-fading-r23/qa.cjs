"use strict";
/**
 * Final Vestige Studios — Mind R23 source audit.
 * Node-only standard library; no dependencies, network requests, telemetry or file writes.
 * node mind/troxler-fading-r23/qa.cjs
 * node mind/troxler-fading-r23/qa.cjs --mutation
 * Source checks != a WordPress staging/browser/medical accuracy certification.
 */
const fs=require("node:fs"),path=require("node:path");
const names=["investigation.md","zen12-guide-A.wp.html","zen12-guide-B.wp.html","claims-and-permissions.csv","troxler-original-static.svg","troxler-image-insertion-DRAFT.html","mind-hub-concept.wp.html","zen12-40s-UNMASTERED.vtt","pilot-and-measurement-HOLD.md","measurement-OFF.json"];
const filesFromDisk=()=>Object.fromEntries(names.map(n=>[n,fs.readFileSync(path.join(__dirname,n),"utf8")]));
const chars=(x)=>[...x].length;
const stripFilm=s=>s.replace(/<section aria-labelledby="r23-video-marker">[\s\S]*?<\/section>/,"");
const contrast=(a,b)=>{
 const rgb=h=>[1,3,5].map(i=>parseInt(h.slice(i,i+2),16)/255).map(v=>v<=.04045?v/12.92:Math.pow((v+.055)/1.055,2.4));
 const lum=h=>rgb(h).reduce((s,n,i)=>s+n*[.2126,.7152,.0722][i],0);
 const x=lum(a),y=lum(b);return(Math.max(x,y)+.05)/(Math.min(x,y)+.05);
};
function audit(f){
 let n=0;const issues=[];const ok=(b,label)=>{n++;if(!b)issues.push(label)};
 for(const name of names)ok(typeof f[name]==="string"&&f[name].length>30,"Missing or empty "+name);
 const i=f["investigation.md"]||"",a=f["zen12-guide-A.wp.html"]||"",b=f["zen12-guide-B.wp.html"]||"",c=f["claims-and-permissions.csv"]||"",s=f["troxler-original-static.svg"]||"",h=f["mind-hub-concept.wp.html"]||"",v=f["zen12-40s-UNMASTERED.vtt"]||"",p=f["pilot-and-measurement-HOLD.md"]||"",mi=f["troxler-image-insertion-DRAFT.html"]||"",j=f["measurement-OFF.json"]||"";
 ok(i.split(/\s+/).length>1700,"Investigation too brief");
 ok((i.match(/https:\/\//g)||[]).length>=10,"Insufficient investigation source and live links");
 ok(i.includes("1804")&&i.includes("microsaccades"),"Missing historical/explanatory essentials");
 ok(i.includes("not a psychometric instrument")&&i.includes("not a substitute"),"Investigation safety/limits missing");
 ok(!/affiliate (link|CTA)|buy now|purchase (Zen12|here)/i.test(i),"Commercial CTA in independent investigation");
 ok(a.includes('<article class="fv-mind-r23"')&&b.includes('<article class="fv-mind-r23"'),"Missing scope");
 ok(a.includes("Twelve Minutes Is a Real Commitment"),"Missing honest hook");
 ok(a.includes("seller")&&a.includes("product-specific")&&a.includes("not a certification"),"Efficacy distinction missing");
 ok(stripFilm(b)===a,"Variant editorial/offer copy mismatch");
 ok(b.includes("Full accessible transcript")&&b.includes("00")&&b.includes("40-second"),"Video transcript/concept missing");
 ok(!/<video\b|autoplay|<iframe\b/i.test(a),"A contains player, iframe or autoplay");
 ok(!/<video\b|autoplay|<iframe\b/i.test(b.replace(/no autoplay/i,"")),"B contains active media or iframe");
 ok(!/<script\b|<form\b|onclick\s*=|onload\s*=/i.test(a+b),"Executable script or form introduced");
 ok(!/href=["'][^"']*(aff_id|affiliate_id|ref=|hop=|clickbank|trackid)/i.test(a+b),"Potential affiliate tracking URL");
 ok(!/href=["']https?:\/\/(www\.)?zen12\.com\/(getstarted|about|research)["'][^>]*rel=["'][^"']*sponsored/i.test(a+b),"Non-earning reference confused with sponsored link");
 ok(a.includes('type="button" class="inactive" disabled aria-disabled="true"')&&b.includes('type="button" class="inactive" disabled aria-disabled="true"'),"Purchase controls not disabled");
 ok(a.includes("Final Vestige may earn a commission")&&b.includes("Final Vestige may earn a commission"),"Near-CTA disclosure missing");
 ok(a.indexOf('Affiliate disclosure:')>=0&&a.indexOf('class="inactive"')-a.indexOf('Affiliate disclosure:')<600,"Disclosure too far from CTA");
 ok(b.indexOf('Affiliate disclosure:')>=0&&b.indexOf('class="inactive"')-b.indexOf('Affiliate disclosure:')<600,"Video B disclosure too far");
 ok(a.includes("prefers-reduced-motion:reduce")&&b.includes("prefers-reduced-motion:reduce"),"Reduced-motion styling absent");
 ok(a.includes("@media(max-width:680px)")&&b.includes("@media(max-width:680px)"),"Responsive breakpoint absent");
 ok(a.includes(':focus-visible')&&b.includes(':focus-visible'),"Visible keyboard focus absent");
 ok(a.includes("https://zen12.com/about")&&a.includes("https://zen12.com/getstarted"),"Exact offer source links missing");
 ok(a.includes("https://www.nccih.nih.gov/health/meditation-and-mindfulness-effectiveness-and-safety"),"Independent research context missing");
 ok(a.includes("https://finalvestige.com/focus/")&&a.includes("https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/"),"Existing genuine content link missing");
 ok(!/\<form\b|\<script\b|\<iframe\b/i.test(h),"Hub embeds unwanted subscriptions/scripts");
 ok(h.includes("proposed home")&&h.includes("Mind hub PR #172"),"Hub design review separation missing");
 ok(h.includes("https://finalvestige.com/focus/")&&h.includes("https://finalvestige.com/editorial-standards/"),"Hub existing pages not linked");
 ok((c.match(/^"\d{2}","/gm)||[]).length===52,"Claim matrix must have 52 numbered claims");
 ok(c.includes("NOT_VERIFIED")&&c.includes("UNSUBSTANTIATED_EFFICACY")&&c.includes("FTC_POLICY"),"Matrix not separating claims and permission");
 ok(!/\[INSERT|example\.com|myaffiliateid/i.test(a+b+c),"Placeholders or fake affiliate URLs");
 ok(s.includes('<svg')&&s.includes('<title')&&s.includes('<desc'),"SVG accessible semantic metadata missing");
 ok(!/<animate|<script|<foreignObject|onload\s*=/i.test(s),"SVG contains active content");
 ok(mi.includes("No image? No problem.")&&mi.includes("not a medical"),"Demo fallback missing");
 ok(v.startsWith("WEBVTT")&&v.includes("UNMASTERED")&&v.includes("00:00:40.000"),"Draft caption gating missing");
 ok(p.includes("No conversion claims")&&p.includes("UNPUBLISHED")&&p.includes("A:")&&p.includes("B:"),"Experiment plan/inactive policy missing");
 ok(p.includes("No cookies")&&p.includes("first-party")&&p.includes("founder"),"Privacy/release gates missing");
 let m={};try{m=JSON.parse(j)}catch(e){}ok(m.enabled===false&&m.affiliate_links_active===false&&m.collector_url===null,"Measurement must be OFF");
 ok(m.cookies===false&&m.local_storage===false&&m.third_party_services===false,"Measurement data minimization absent");
 ok(m.outbound_clicks_are_sales===false,"Clicks conflated with sales");
 ok(Array.isArray(m.forbidden_fields)&&m.forbidden_fields.includes("ip")&&m.forbidden_fields.includes("email"),"Missing privacy field denial");
 ok(contrast("#f8f2e6","#101b20")>=7,"Main body contrast below AAA");
 ok(contrast("#d1d8d7","#101b20")>=7,"Muted text contrast below AAA");
 ok(contrast("#f1cb91","#101b20")>=7,"Links contrast below AAA");
 ok(contrast("#fff3da","#2b3739")>=7,"Disclosure contrast below AAA");
 return {passed:n-issues.length,total:n,issues,contrast:{body:contrast("#f8f2e6","#101b20"),muted:contrast("#d1d8d7","#101b20"),link:contrast("#f1cb91","#101b20"),disclosure:contrast("#fff3da","#2b3739")}};
}
function mutations(f){
 const cases=[
 ["remove near-link disclosure",g=>g["zen12-guide-A.wp.html"]=g["zen12-guide-A.wp.html"].replace(/Affiliate disclosure:[^<]+/,"")],
 ["activate purchase CTA",g=>g["zen12-guide-A.wp.html"]=g["zen12-guide-A.wp.html"].replace(' disabled aria-disabled="true"',"")],
 ["insert malicious third-party script",g=>g["zen12-guide-B.wp.html"]+='<script src="https://tracker.example.com/x.js"></script>'],
 ["insert hidden email form",g=>g["zen12-guide-A.wp.html"]+='<form><input type=email></form>'],
 ["insert iframe",g=>g["zen12-guide-A.wp.html"]+='<iframe src="https://zen12.com/"></iframe>'],
 ["insert real player",g=>g["zen12-guide-A.wp.html"]+='<video controls src="x.mp4"></video>'],
 ["delete visible transcript",g=>g["zen12-guide-B.wp.html"]=g["zen12-guide-B.wp.html"].replace("Full accessible transcript","Full missing transcript")],
 ["alter shared core editorial",g=>g["zen12-guide-B.wp.html"]=g["zen12-guide-B.wp.html"].replace("An Hour in Twelve","Two Hours in Twelve")],
 ["activate measurement",g=>g["measurement-OFF.json"]=g["measurement-OFF.json"].replace('"enabled": false','"enabled": true')],
 ["remove matrix row",g=>g["claims-and-permissions.csv"]=g["claims-and-permissions.csv"].split("\n").slice(0,-2).join("\n")+"\n"],
 ["add dubious affiliate URL",g=>g["zen12-guide-A.wp.html"]+='<a href="https://zen12.com/getstarted?aff_id=guessed">buy</a>'],
 ["delete reduced motion handling",g=>g["zen12-guide-A.wp.html"]=g["zen12-guide-A.wp.html"].replace("prefers-reduced-motion:reduce","prefers-motion:true")],
 ["remove demo fallback",g=>g["troxler-image-insertion-DRAFT.html"]=g["troxler-image-insertion-DRAFT.html"].replace("No image? No problem.","Missing image fallback")],
 ["add active SVG script",g=>g["troxler-original-static.svg"]+='<script>alert(1)</script>']
 ];
 return cases.map(([name,mutate])=>{const clone={...f};mutate(clone);const r=audit(clone);return {name,caught:r.issues.length>0,failures:r.issues}});
}
if(require.main===module){
 const f=filesFromDisk(),r=audit(f);console.log(JSON.stringify(r,null,2));if(process.argv.includes("--mutation")){const m=mutations(f);console.log(JSON.stringify(m,null,2));if(m.some(x=>!x.caught))process.exitCode=1;}if(r.issues.length)process.exitCode=1;
}
module.exports={audit,mutations,filesFromDisk,names,stripFilm,contrast};
