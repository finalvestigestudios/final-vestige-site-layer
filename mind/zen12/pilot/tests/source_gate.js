/* V8/Node reproducible source-only safety audit; accepts an explicit file-map. */
function audit(f){
 const p="mind/zen12/pilot/";
 const base=f["mind/zen12/page-zen12-guide.blocks.html"],guide=f[p+"evidence-buyers-guide.md"],claims=JSON.parse(f[p+"claims.json"]);
 const cap=f[p+"video/captions.vtt"],tr=f[p+"video/transcript.md"],man=JSON.parse(f[p+"video/manifest.json"]);
 const prog=f[p+"video/build_video.py"],renderer=f[p+"render_variants.py"],poster=f[p+"video/poster.svg"],plan=f[p+"measurement.md"];
 let r={};const c=(n,v)=>r[n]=!!v;
 c("WordPress base inherited",base.includes("<!-- wp:html -->"));
 c("exact original film section",base.split('<details class="fvz12__film">').length===2);
 c("base commercial link inactive",base.includes('data-fv-offer-state="unverified"')&&!base.includes('href="https://zen12.com/getstarted"'));
 c("original free Focus link",base.includes('href="/focus/"'));
 c("new guide full-length",guide.trim().split(/\s+/).length>=1800);
 c("original attention exercise",guide.includes("three unhurried breaths"));
 c("independent science sources",guide.includes("24395196")&&guide.includes("37205669"));
 c("meditation/entrainment not conflated",guide.includes("meditation studies and audio-stimulation studies are not the same"));
 c("product not personally tested",guide.includes("not purchased")&&guide.includes("Final Vestige used Zen12"));
 c("buyer reads current terms",guide.includes("written terms"));
 c("near-link disclosure",guide.includes("**Commercial disclosure:**"));
 c("no form in guide",!/<form\b|<input\b/i.test(guide));
 c("claims exactly 30",claims.claims.length===30);
 c("unique claim IDs",new Set(claims.claims.map(x=>x.id)).size===30);
 c("all claim sources",claims.claims.every(x=>claims.sources[x.source]));
 c("rejected efficiency",claims.claims.some(x=>x.id==="08"&&x.disposition.startsWith("exclude")));
 c("rejected health claim",claims.claims.some(x=>x.id==="10"&&x.disposition.startsWith("exclude")));
 c("rejected endorsement",claims.claims.some(x=>x.id==="22"&&x.disposition.startsWith("exclude")));
 c("no approved affiliate",!claims.affiliate_account_approved&&claims.affiliate_url===null);
 c("no product test invented",claims.paid_product_tested===false);
 c("MP4 exactly 40 seconds",man.duration_seconds===40);
 c("MP4 under 200kb",man.mp4_bytes<200000);
 c("MP4 sha in manifest",/^[0-9a-f]{64}$/.test(man.mp4_sha256));
 c("poster sha in manifest",/^[0-9a-f]{64}$/.test(man.poster_png_sha256));
 c("media not uploaded",man.media_uploaded_to_wordpress===false&&man.media_binaries_in_git===false);
 c("no third party media",man.no_borrowed_assets===true);
 c("caption timeline 40s",cap.includes("WEBVTT")&&cap.includes("00:00:40.000"));
 c("captions five scenes",(cap.match(/ --> /g)||[]).length===5);
 c("captions contain disclosure",cap.includes("commission"));
 c("visual description five scenes",(tr.match(/\*\*00:/g)||[]).length===5);
 c("poster accessible title",poster.includes("<title")&&poster.includes("<desc"));
 c("source only uses OS fonts",prog.includes("DejaVuSerif.ttf")&&!prog.includes("requests.get"));
 c("source no sound",prog.includes("'-an'"));
 c("source no external assets",!prog.includes("http://")&&!prog.includes("https://"));
 c("SHA-pinned media gate",renderer.includes("VIDEO_SHA=")&&renderer.includes("POSTER_SHA=")&&renderer.includes("raise ValueError"));
 c("only one film module substituted",renderer.includes("altered=baseline[:i]+html_video+baseline[j:]"));
 c("manual play only",renderer.includes('controls preload="none" playsinline'));
 c("no new trackers",!renderer.includes("sendBeacon")&&!renderer.includes("gtag("));
 c("A/B privacy policy",plan.includes("Never persist IP address")&&plan.includes("A click is not a sale"));
 c("live v proposed links labelled",plan.includes("Proposed and NOT LIVE"));
 return {passed:Object.values(r).filter(Boolean).length,total:Object.keys(r).length,failed:Object.keys(r).filter(k=>!r[k]),details:r};
}
if(typeof module!=="undefined"&&require.main===module){
 const fs=require("fs"),path=require("path"),root=path.resolve(__dirname,"../../../..");
 let f={};for(const name of ["mind/zen12/page-zen12-guide.blocks.html","mind/zen12/pilot/evidence-buyers-guide.md","mind/zen12/pilot/claims.json","mind/zen12/pilot/video/captions.vtt","mind/zen12/pilot/video/transcript.md","mind/zen12/pilot/video/manifest.json","mind/zen12/pilot/video/build_video.py","mind/zen12/pilot/render_variants.py","mind/zen12/pilot/video/poster.svg","mind/zen12/pilot/measurement.md"]){f[name]=fs.readFileSync(path.resolve(root,name),"utf8");}
 const o=audit(f);console.log(JSON.stringify(o,null,2));if(o.failed.length)process.exit(1);
}
