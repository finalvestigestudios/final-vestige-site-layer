'use strict';
const fs=require('node:fs');
function validate(d){
let e=[],f=s=>e.push(s);
if(d?.schema!=="fv-media-tmi285-v1"||d.wp?.post_id!==285||!d.wp?.modified)f("revision/schema");
if(d?.baseline?.posts!==61||d.baseline.images!==355||d.baseline.reported_broken!==42||d.baseline.verified_broken!==null)f("unverified historical census");
if(d?.baseline?.claimed_savings_percent!==76||d.baseline.measured_savings_percent!==null||d.baseline.visitor_bytes!==null||d.baseline.oversize_original_count!==20||d.baseline.oversize_original_stored_bytes!==64385752)f("fabricated visitor-byte statistics");
if(!Array.isArray(d.items)||d.items.length!==6)f("image census");
else d.items.forEach((x,i)=>{
if(x.slot!==`285:${i}`)f("slot "+i);
if(!/^https:\/\//.test(x.authored||"")||!/^https:\/\//.test(x.view_url||""))f("url "+i);
if(x.view_url!==x.view_html.replace(/&#038;/g,"&").replace(/&amp;/g,"&"))f("entity URL "+i);
if(!x.alt||x.view_markup.width!==null||x.view_markup.height!==null||x.view_markup.srcset!==false||x.view_markup.sizes!==false)f("markup "+i);
if(x.jetpack!==(i!==3))f("proxy "+i);
if(Object.entries(x.guest).some(([k,v])=>k==="broken"?v!==false:v!==null))f("invented browser observation "+i);
if(i===5&&(!x.retriever_note||!x.retriever_note.includes("NOT verified")))f("retriever not separate from browser");
if(!x.candidates.length)f("missing candidate "+i);
for(const c of x.candidates){
if(!/^https:\/\//.test(c.catalog_url)||!c.source||!c.rights_note)f("bad catalog "+i);
if(c.rights_cleared!==false||c.exact_frame_verified!==false||c.wordpress_rehosting_approved!==false||c.binary_sha256!==null)f("premature clearance "+i);
if(c.catalog_native_px===null){if(c.review_px!==null)f("fabricated native pixels "+i);}
else {const [w,h]=c.catalog_native_px,cap=Math.min(960,w);if(!Number.isInteger(w)||!Number.isInteger(h)||w<=0||h<=0||c.review_px?.[0]!==cap||c.review_px?.[1]!==Math.round(h*cap/w))f("upscale/geometry "+i);}
}
});
const s=d?.safety||{};if(s.site_qa_collector!=="PR #154"||s.no_homepage_scope!==true||s.no_upscale!==true||s.max_width_px!==960||s.wordpress_writes!==0||s.downloads!==0||s.rehosts!==0||s.decision!=="HOLD")f("unsafe operations");
return {ok:e.length===0,errors:e,release:"HOLD"};
}
module.exports={validate};
if(require.main===module){let x=JSON.parse(fs.readFileSync(process.argv[2]||__dirname+'/'+"tmi285_archive_rights_20261116_2327pt.json",'utf8'));let r=validate(x);console.log(JSON.stringify(r,null,2));process.exitCode=r.ok?0:1;}
