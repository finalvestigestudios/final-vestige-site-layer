"use strict";
function domain(url){const m=/^https?:\/\/([^/?#]+)/i.exec(url);if(!m)return null;const raw=m[1].toLowerCase();if(/^i[0-3]\.wp\.com$/.test(raw)){const x=/^https?:\/\/i[0-3]\.wp\.com\/([^/?#]+)/i.exec(url);return x?x[1].toLowerCase():null}return raw}
function hash(s){let h=2166136261;for(let i=0;i<s.length;i++)h=Math.imul(h^s.charCodeAt(i),16777619);return (h>>>0).toString(16).padStart(8,"0")}
function canon(d){return JSON.stringify(d.rows.map(x=>[x.slot,x.stored_url,x.origin_host,x.researched,x.external_retriever,x.candidate?.catalog_url,x.candidate?.conditional_960_px]));}
function core(d,expected){
 const e=[];if(!d||!Array.isArray(d.rows)||!Array.isArray(d.groups))return ["not_a_document"];
 const c=d.counts||{};
 if(d.schema!=="fv-media-80-host-upstream-v1"||c.posts!==61||c.all_slots!==355||c.all_distinct_urls!==353||c.offsite_origin_slots!==288||c.origin_hosts!==80||c.researched!==50||c.pending!==238||c.wp_com_delivery!==9||c.wp_com_upstream_first_party!==7||c.wp_com_upstream_external!==2||c.guest_broken_42_verified!==false||c.transfer_saving_76pct_measured!==false||c.stored_large_media_count!==15||c.stored_large_media_bytes!==47096779)e.push("unverified_totals");
 if(!Array.isArray(d.source_refs)||d.source_refs.length!==8||!Array.isArray(d.other_refs)||d.other_refs.length!==2)e.push("missing_provenance");
 if(d.rows.length!==288||hash(canon(d))!==expected)e.push("changed_source_or_research_reference");
 let n=0,offProxy=0;const ids=new Set(),hosts=new Map();
 for(const x of d.rows){
  if(!x||typeof x!=="object"){e.push("malformed_row");continue;}
  if(ids.has(x.slot)||!x.slot||x.post_id!==Number(x.slot.split(":")[0]))e.push("post_slot_binding");ids.add(x.slot);
  if(domain(x.stored_url)!==x.origin_host||["finalvestige.com","www.finalvestige.com"].includes(x.origin_host))e.push("origin_mismatch");
  if(x.visitor_http!==null||x.visitor_dimensions!==null||x.visitor_wire_bytes!==null||x.visitor_broken!==null)e.push("invented_browser_observation");
  if(!x.release||Object.keys(x.release).sort().join(",")!=="block_rewrite,cache,mirror,wordpress_upload"||Object.values(x.release).some(a=>a!==false))e.push("unapproved_release");
  if(/^i[0-3]\.wp\.com$/.test(x.delivery_host))offProxy++;
  if(x.researched){n++;if(!x.external_retriever||x.external_retriever.method!=="TOOL_WRAPPER_NOT_ORIGIN_HTTP"||!x.candidate||x.candidate.exact_image_match!==false||x.candidate.rights_cleared!==false||x.candidate.visual_approved!==false)e.push("rights_or_identity_fabrication");
  const p=x.candidate?.conditional_960_px,m=x.candidate?.native_px;if(p!==null){if(!Array.isArray(p)||p.length!==2||p.some(v=>!Number.isInteger(v)||v<=0)||p[0]>960)e.push("bad_resize");if(Array.isArray(m)&&m.length===2&&(p[0]>m[0]||p[1]>m[1]))e.push("upscaling");}}
  else if(x.candidate!==null||x.external_retriever!==null)e.push("fake_source_research");
  const h=hosts.get(x.origin_host)||{n:0,k:0,posts:new Set(),urls:new Set()};h.n++;h.k+=x.researched?1:0;h.posts.add(x.post_id);h.urls.add(x.stored_url);hosts.set(x.origin_host,h)
 }
 if(ids.size!==288||n!==50||offProxy!==2||hosts.size!==80||d.groups.length!==80)e.push("coverage");
 for(const g of d.groups){const q=hosts.get(g.host);if(!q||g.slots!==q.n||g.researched!==q.k||g.pending!==q.n-q.k||g.posts!==q.posts.size||g.distinct_urls!==q.urls.size)e.push("host_rollup");}
 return [...new Set(e)];
}
const EXPECTED_FINGERPRINT="dc27c388";function validate(doc){return core(doc,EXPECTED_FINGERPRINT)}
module.exports={validate,EXPECTED_FINGERPRINT};
if(require.main===module){const fs=require("node:fs");const f=process.argv[2]||"qa/media-recovery/offsite_upstream_288_20261109.json";const errors=validate(JSON.parse(fs.readFileSync(f,"utf8")));console.log(errors.length?errors.join("\n"):"PASS 288 upstream offsite source slots / 80 hosts / 50 researched / 238 pending");process.exitCode=errors.length?1:0;}
