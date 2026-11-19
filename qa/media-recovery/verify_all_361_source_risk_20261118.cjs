'use strict';
// Read-only snapshot reconciliation. Never asserts guest image health or performs network / WP writes.
function widthHint(s){const m=String(s||"").match(/[?&](?:w|width|resize|fit)=(\d+)/);return m?Number(m[1]):null;}
function verify(a,sources,manifest){
 let errors=[],bad=x=>{if(errors.length<80)errors.push(x)};
 if(!a||a.schema!=="fv-66-all-image-slot-risk-audit-v1"||!Array.isArray(a.image_slots)||!Array.isArray(a.post_priority)||!Array.isArray(a.source_slices)||!Array.isArray(sources)||!manifest?.current_66?.git_blobs)return ["schema"];
 if(a.image_slots.length!==361||a.post_priority.length!==66||a.source_slices.length!==9||sources.length!==9)bad("coverage");
 if(a.current_66?.posts!==66||a.current_66?.inline_slots!==361||a.historical_61?.posts!==61||a.historical_61?.inline_slots!==355||a.current_66?.verified_visitor_broken!==null||a.current_66?.verified_76_percent_cold_image_wire_savings!==null)bad("unsupported_claim");
 const h=a.methods_and_release_hold||{};
 if(h.deployed!==false||h.wordpress_production_writes!==0||h.media_downloaded!==0||h.auto_replacements!==0||h.paid_calls!==0||a.wordpress_oversize?.visitor_wire_bytes!==null)bad("unsafe_production");
 const pin=new Map(manifest.current_66.git_blobs.map(x=>[x.path,x.sha])),post=new Map(),source=new Map();
 for(const s of sources){
  let expected=a.source_slices.find(x=>x.path===s.path);
  if(!expected||expected.git_blob!==s.sha||pin.get(s.path)!==s.sha||s.data?.schema!=="fv-66-view-slice-v1"||s.data?.production_writes!==0)bad("sha_or_snapshot_mismatch");
  for(const x of s.data.posts||[]){if(post.has(x.id))bad("duplicate_source_post");post.set(x.id,x);}
  for(const x of s.data.images||[]){let k=x.post_id+":"+x.slot;if(source.has(k))bad("duplicate_source_slot");source.set(k,x);}
 }
 if(post.size!==66||source.size!==361)bad("snapshot_cardinality");
 const rowById=new Map(),postById=new Map();
 for(const r of a.image_slots){if(rowById.has(r.slot))bad("duplicate_audit_slot");rowById.set(r.slot,r);}
 for(const x of a.post_priority){if(postById.has(x.post_id))bad("duplicate_post_summary");postById.set(x.post_id,x);}
 const flagcount={},routecount={},perpost=new Map();
 for(const [k,x] of source){
  const r=rowById.get(k),pg=post.get(x.post_id);
  if(!r||!pg){bad("source_row_missing");continue;}
  const attrs=["authored_view_src","source_origin_url","origin_host","route_type","width_attr","height_attr","has_srcset","has_sizes","alt"];
  if(r.post_id!==x.post_id||r.page_url!==pg.url||attrs.some(t=>r[t]!==x[t]))bad("source_row_drift");
  if(r.requested_width_hint_px!==widthHint(x.authored_view_src))bad("request_size_hint_drift");
  if(r.visitor_http_status!==null||r.visitor_decoded!==null||r.visitor_wire_bytes!==null||r.replacement_approved!==false||r.rights_review!=="HOLD_ITEM_LEVEL")bad("visitor_or_rights_fabrication");
  const flags=[];
  if(x.route_type==="third_party_direct")flags.push("DIRECT_EXTERNAL_ORIGIN");
  if(!(x.width_attr>0&&x.height_attr>0))flags.push("MISSING_EXPLICIT_DIMENSIONS");
  if(!x.has_srcset)flags.push("NO_SRCSET");
  if(x.authored_view_src.includes("/wiki/Special:Redirect/file/"))flags.push("WIKIMEDIA_IMAGE_REDIRECT_ROUTE");
  if(widthHint(x.authored_view_src)>960)flags.push("REQUESTED_WIDTH_HINT_GT_960");
  const confirmed=(a.known_404_origins_retriever_only||[]).find(q=>q.slot===k&&q.post_id===x.post_id&&q.url===x.source_origin_url&&q.observed_http===404);
  if(confirmed)flags.push("EXTERNAL_ORIGINAL_RETRIEVER_404");
  if(JSON.stringify(flags)!==JSON.stringify(r.flags)||r.original_public_retriever_http!==(confirmed?404:null)||r.original_probe_date!==(confirmed?"2026-11-18":null))bad("origin_probe_or_flag_drift");
  for(const f of flags)flagcount[f]=(flagcount[f]||0)+1;
  routecount[x.route_type]=(routecount[x.route_type]||0)+1;
  const z=perpost.get(x.post_id)||{n:0,d:0,s:0,t:0,w:0,b:0};z.n++;if(flags.includes("MISSING_EXPLICIT_DIMENSIONS"))z.d++;if(flags.includes("NO_SRCSET"))z.s++;if(flags.includes("DIRECT_EXTERNAL_ORIGIN"))z.t++;if(flags.includes("WIKIMEDIA_IMAGE_REDIRECT_ROUTE"))z.w++;if(confirmed)z.b++;perpost.set(x.post_id,z);
 }
 if(rowById.size!==361||postById.size!==66)bad("audit_cardinality");
 const sums=[["missing_both_explicit_dimensions","MISSING_EXPLICIT_DIMENSIONS"],["missing_srcset","NO_SRCSET"],["special_redirects","WIKIMEDIA_IMAGE_REDIRECT_ROUTE"],["requested_width_hint_over_960","REQUESTED_WIDTH_HINT_GT_960"]];
 if(sums.some(([field,f])=>a.current_66[field]!== (flagcount[f]||0))||JSON.stringify(routecount)!==JSON.stringify(a.current_66.route_types))bad("aggregate_drift");
 for(const [id,x] of post){const r=postById.get(id),v=perpost.get(id)||{n:0,d:0,s:0,t:0,w:0,b:0};if(!r||r.page_url!==x.url||r.title!==x.title||r.image_slots!==v.n||r.missing_dimensions!==v.d||r.missing_srcset!==v.s||r.direct_external!==v.t||r.image_redirects!==v.w||r.origin_404_probes!==v.b)bad("post_summary_drift");}
 if(!Array.isArray(a.source_image_recovery_candidates)||a.source_image_recovery_candidates.length!==6||a.source_image_recovery_candidates.some(c=>c.rehost_approved!==false||c.same_photo_crop_verified!==false||typeof c.rights!=="string"||!c.rights.length||!/^https:\/\/[^/]+/.test(c.catalog)))bad("unreviewed_candidate");
 if((a.known_404_origins_retriever_only||[]).some(c=>c.guest_browser_http!==null||c.visitor_browser_proven!==false))bad("fabricated_browser_404");
 return [...new Set(errors)];
}
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const manifest=require('./cohort_61_66_manifest_20261118.json');
function loadSnapshots(a){
 return a.source_slices.map(s=>{
  const raw=fs.readFileSync(path.resolve(__dirname,'../..',s.path));
  const sha=crypto.createHash('sha1').update(Buffer.concat([Buffer.from('blob '+raw.length+'\0'),raw])).digest('hex');
  if(sha!==s.git_blob)throw Error('git blob changed: '+s.path);
  return {path:s.path,sha,data:JSON.parse(raw.toString('utf8'))};
 });
}
module.exports={widthHint,verify,loadSnapshots};
if(require.main===module){
 const a=require('./all_361_source_slot_risk_20261118_2028.json');
 const errors=verify(a,loadSnapshots(a),manifest);
 console.log(JSON.stringify({gate:errors.length?'HOLD_CORRUPT':'REVIEW_ONLY_NO_GUEST_BROWSER',errors,posts:a.post_priority.length,slots:a.image_slots.length},null,2));
 if(errors.length)process.exitCode=1;
}
