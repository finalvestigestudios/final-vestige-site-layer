'use strict';
/** Full live source census; read-only, requires six JSON parts, optional frozen 355 baseline. Never verifies visitor browser loading. */
const fs=require('node:fs');
function verify(parts,prior=null){
 const errs=[],add=(s)=>{if(errs.length<90)errs.push(s);};let posts=[],rows=[];
 if(!Array.isArray(parts)||parts.length!==6)return{valid:false,errors:["six_batches_required"]};
 for(let pi=0;pi<6;pi++){
  const b=parts[pi],expect=Math.min(12,66-pi*12);
  if(b?.schema!=="fv-live-wp-source-batch-v1"||b.page!==pi+1||b.total_published!==66||
     !Array.isArray(b.post_range)||b.post_range[0]!==pi*12||b.post_range[1]!==pi*12+expect-1||
     !Array.isArray(b.posts)||b.posts.length!==expect){add("batch_header:"+pi);continue;}
  posts.push(...b.posts);
  for(const p of b.posts){
   if(!Number.isInteger(p.id)||!/^https:\/\/finalvestige\.com\//.test(p.url||"")||
      !Array.isArray(p.images)||p.image_count!==p.images.length||!p.modified)add("post_metadata:"+p.id);
   for(let j=0;j<(p.images||[]).length;j++){
    const x=p.images[j];rows.push(x);
    if(x.key!==p.id+":"+j)add("slot_key:"+p.id+":"+j);
    if(!/^https?:\/\/[^/?#]+/.test(x.original_url||"")){add("non_http_src:"+x.key);continue;}
    const u=/^https?:\/\/([^/?#]+)(\/[^?#]*)?(?:\?([^#]*))?/i.exec(x.original_url);
    const h=u[1].toLowerCase(), expected=["finalvestige.com","www.finalvestige.com"].includes(h)?"first_party":/^i[0-3]\.wp\.com$/.test(h)?(/^\/(?:www\.)?finalvestige\.com\//.test(u[2]||"")?"first_party_jetpack":"external_jetpack"):h==="commons.wikimedia.org"&&(u[2]||"").startsWith("/wiki/Special:Redirect/file/")?"wikimedia_redirect":"external";
    const q=(u[3]||"").match(/(?:^|&)width=(\d+)(?:&|$)/),width=q?Number(q[1]):null;
    if(x.host!==h||x.origin!==expected||x.query_width!==width)add("source_class_or_query:"+x.key);
    if(typeof x.alt!=="string"||!x.alt.trim())add("missing_alt:"+x.key);
    if(x.html_width!==null&&(!Number.isSafeInteger(x.html_width)||x.html_width<1))add("bad_html_width:"+x.key);
    if(x.html_height!==null&&(!Number.isSafeInteger(x.html_height)||x.html_height<1))add("bad_html_height:"+x.key);
    if(x.actual_browser_http_status!==null||x.actual_browser_decoded!==null||x.actual_browser_transfer_bytes!==null)add("invented_browser_status:"+x.key);
    if(x.rights!=="HOLD"||x.local_cache_authorized!==false||x.wp_write_authorized!==false||x.max_derivative_width!==960||x.no_upscale!==true)add("unsafe_rights_or_write:"+x.key);
   }
  }
 }
 if(new Set(posts.map(p=>p.id)).size!==66||posts.length!==66)add("post_count_or_duplicate");
 if(new Set(rows.map(r=>r.key)).size!==361||rows.length!==361)add("slot_count_or_duplicate");
 const count=k=>rows.filter(r=>r.origin===k).length,external=count("external")+count("wikimedia_redirect")+count("external_jetpack");
 const unique=new Set(rows.map(r=>r.original_url)).size,missing=rows.filter(r=>!r.html_width||!r.html_height).length,wide=rows.filter(r=>r.query_width>960).length;
 if(unique!==359||external!==294||count("first_party")!==60||count("first_party_jetpack")!==7||count("wikimedia_redirect")!==124||missing!==311||wide!==79)add("aggregate_count_mismatch");
 let drift=null,newSlots=null;
 if(prior!==null){
  if(!Array.isArray(prior?.rows)||prior.rows.length!==355)add("invalid_baseline_355");
  else {
   const old=new Map(prior.rows.map(r=>[r.key,r.original_url])),live=new Map(rows.map(r=>[r.key,r.original_url]));
   drift=[...old].filter(([k,url])=>live.get(k)!==url).map(([k])=>k);
   newSlots=[...live.keys()].filter(k=>!old.has(k));
   if(drift.length!==0)add("legacy_url_drift:"+drift.slice(0,3).join(","));
   if(newSlots.length!==6||newSlots.some(k=>!["1926:0","1924:0","1920:0","1920:1","1917:0","1917:1"].includes(k)))add("new_slot_identity");
  }
 }
 return{valid:errs.length===0,errors:errs,summary:{posts:posts.length,slots:rows.length,unique_urls:unique,external,first_party:count("first_party"),first_party_jetpack:count("first_party_jetpack"),wikimedia_redirect:count("wikimedia_redirect"),missing_dimensions:missing,source_query_width_over_960:wide,legacy_drift_keys:drift,new_slots:newSlots,actual_browser_verified:false,claim_42_broken:"UNVERIFIED",claim_76_percent:"UNMEASURED",production_changes:0}};
}
module.exports={verify};
if(require.main===module){const inputs=process.argv.slice(2);if(inputs.length!==6&&inputs.length!==7)throw Error('Usage: node validate_live66_source_drift_v1.cjs part01.json ... part06.json [previous355.json]');const ps=inputs.slice(0,6).map(p=>JSON.parse(fs.readFileSync(p,'utf8'))),old=inputs[6]?JSON.parse(fs.readFileSync(inputs[6],'utf8')):null;const r=verify(ps,old);process.stdout.write(JSON.stringify(r,null,2)+'\n');if(!r.valid)process.exitCode=1;}
