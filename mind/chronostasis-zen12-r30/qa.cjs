"use strict";
const REQUIRED=["investigation.md","investigation.wp.html","zen12-guide.md","zen12-text.wp.html","zen12-video.wp.html","mind-archive.wp.html","NAVIGATION_MEASUREMENT_PLAN.md","CLAIMS_MATRIX.csv","EVIDENCE_NOTES.md","render_film.py","zen12-evidence-40s.vtt","zen12-film-poster.svg","FILM_SPEC.md","privacy-off.cjs","qa.cjs"];
function audit(files){
 let n=0;const failures=[]; const guard=(name,check)=>{n++;if(!check)failures.push(name);};
 for(const f of REQUIRED)guard("present:"+f,typeof files[f]==="string"&&files[f].length>10);
 if(failures.length)return{passed:n-failures.length,failed:failures,total:n};
 const a=files["zen12-text.wp.html"],b=files["zen12-video.wp.html"],md=files["zen12-guide.md"],invest=files["investigation.md"],hub=files["mind-archive.wp.html"],film=files["zen12-evidence-40s.vtt"],csv=files["CLAIMS_MATRIX.csv"],priv=files["privacy-off.cjs"];
 const filmModule=/<section class="film"[^>]*>[\s\S]*?<\/section>/;
 const Bcore=b.replace(filmModule,"").replace('data-fv-mind-variant="B"','data-fv-mind-variant="A"');
 guard("AB-identical-offer-copy",Bcore===a);
 guard("B contains static optional film",filmModule.test(b)&&/40-second/.test(b));
 guard("unhosted-control-hidden",!b.includes("<video")&&!b.includes("autoplay")===false); // handled additionally by strict checks below
 guard("no player anywhere",![a,b,hub].some(x=>/<video\b|<iframe\b|<script\b/i.test(x)));
 guard("no live earning link",![a,b,hub].some(x=>/href=["']https?:\/\/(?:zen12\.com|affiliates\.inspire3\.com)/i.test(x)));
 guard("no forms",![a,b,hub].some(x=>/<form\b/i.test(x)));
 guard("no inline onclick",![a,b,hub].some(x=>/on(?:click|load|error)\s*=/i.test(x)));
 for(const [name,x] of [["A",a],["B",b]]){
   guard(name+" disabled offer",/<button[^>]*\bdisabled\b/.test(x)&&x.includes("Affiliate offer unavailable pending approval"));
   guard(name+" near-link disclosure",x.includes('class="disclosure"')&&x.indexOf('class="disclosure"')<x.lastIndexOf('class="hold"'));
   guard(name+" no broken anchor",!x.includes('href="#"'));
   guard(name+" full tiers",["Beginner","Premium","Advanced"].every(t=>x.includes(t)));
   guard(name+" cited PLOS",x.includes("10.1371/journal.pone.0286023"));
   guard(name+" Focus original",x.includes("https://finalvestige.com/focus/"));
   guard(name+" scoped style",x.includes(".fv-z12-30")&&!x.includes("body:has("));
 }
 guard("reader-guide depth",md.trim().split(/\s+/).length>=1500);
 guard("original-research depth",invest.trim().split(/\s+/).length>=2000);
 guard("no investigate commerce",!/affiliate link|purchase zen12|buy now/i.test(invest));
 guard("chronostasis source",invest.includes("10.1038/35104551"));
 guard("experimental challenge",invest.includes("10.1016/j.concog.2003.10.006"));
 guard("source archive bridge",invest.includes("puysegurs-animal-magnetism-files"));
 guard("hub current published Focus",hub.includes("finalvestige.com/focus/"));
 guard("hub no preview-only links",!hub.includes('href="/mind/'));
 guard("hub no new Jetpack form",!hub.includes("wp-block-jetpack-subscriptions"));
 guard("ethics first",md.includes("does not repeat the hour-in-twelve-minutes promise"));
 guard("no synthetic health proof",md.includes("not trials of Zen12"));
 guard("phone caveat",md.includes("Displaying a field does not establish it is mandatory"));
 guard("checkout count caveat",md.includes("countdown"));
 guard("merchant tiers",["24 MP3s","48 MP3s"].every(t=>md.includes(t)));
 guard("matrix rows >=50",csv.trim().split(/\n/).length>=51);
 guard("matrix seller vs proof",csv.includes("unsupported_product_specific")&&csv.includes("seller_only"));
 guard("matrix hard holds",csv.includes("NOT_VERIFIED")&&csv.includes("hard_hold"));
 guard("privacy disabled",priv.includes("const ENABLED=false"));
 guard("privacy suppress small group",priv.includes("THRESHOLD=10"));
 guard("poster descriptive",files["zen12-film-poster.svg"].includes("<desc"));
 guard("video film silent",files["FILM_SPEC.md"].includes("silent"));
 guard("no mp4 embedded",!a.includes(".mp4")&&!b.includes(".mp4"));
 const re=/(\d\d):(\d\d):(\d\d)\.\d{3} --> (\d\d):(\d\d):(\d\d)\.\d{3}/g;let m,segments=[];while((m=re.exec(film))!==null){const sec=(h,mi,s)=>+h*3600+(+mi)*60+(+s);segments.push([sec(m[1],m[2],m[3]),sec(m[4],m[5],m[6])]);}
 guard("five VTT cues",segments.length===5);
 guard("VTT contiguous 40 sec",segments.length===5&&segments[0][0]===0&&segments[4][1]===40&&segments.every((v,i)=>v[1]>v[0]&&(i===0||v[0]===segments[i-1][1])));
 guard("no unmatched anchor",!a.includes("href=#"));
 return {passed:n-failures.length,failed:failures,total:n};
}
function adversarial(files){
 const cases=[
 ["revenue-link",{"zen12-text.wp.html":files["zen12-text.wp.html"].replace("Affiliate offer unavailable pending approval",'<a href="https://zen12.com/getstarted">Buy</a>')}],
 ["enabled-offer",{"zen12-text.wp.html":files["zen12-text.wp.html"].replace("disabled aria-disabled","enabled aria-disabled")}],
 ["missing disclosure",{"zen12-text.wp.html":files["zen12-text.wp.html"].replace('class="disclosure"','class="hidden"')}],
 ["new-list",{"mind-archive.wp.html":files["mind-archive.wp.html"]+"<form></form>"}],
 ["privacy-on",{"privacy-off.cjs":files["privacy-off.cjs"].replace("const ENABLED=false","const ENABLED=true")}],
 ["video-autoplay",{"zen12-video.wp.html":files["zen12-video.wp.html"]+"<video autoplay></video>"}],
 ["copy-drift",{"zen12-video.wp.html":files["zen12-video.wp.html"].replace("TWELVE IS","THIRTEEN IS")}],
 ["broken-link",{"zen12-text.wp.html":files["zen12-text.wp.html"]+'<a href="#">oops</a>'}],
 ["short-investigation",{"investigation.md":"hello world"}],
 ["unchecked-claims",{"CLAIMS_MATRIX.csv":"claim,source\nnone,none"}],
 ["tier-error",{"zen12-guide.md":files["zen12-guide.md"].replace("48 MP3s","18 MP3s")}],
 ["bad-captions",{"zen12-evidence-40s.vtt":files["zen12-evidence-40s.vtt"].replace("00:00:40.000","00:00:39.000")}],
 ]; return cases.map(([name,changes])=>({name,detected:audit({...files,...changes}).failed.length>0}));
}
module.exports={REQUIRED,audit,adversarial};
if(typeof require!=="undefined"&&require.main===module){const fs=require("node:fs"),path=require("node:path");const root=__dirname;const files=Object.fromEntries(REQUIRED.map(n=>[n,fs.readFileSync(path.join(root,n),"utf8")]));const r=audit(files),mut=adversarial(files);console.log(JSON.stringify({audit:r,mutations:mut},null,2));if(r.failed.length||mut.some(x=>!x.detected))process.exitCode=1;}
