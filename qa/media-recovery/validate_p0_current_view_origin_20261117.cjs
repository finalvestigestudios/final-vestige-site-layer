'use strict';
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const PINNED=["698b613c41e792b2e0100547a07f4b519c0a908a","1c8cd5d1fd015705c0937d68471fb54546ed2f67","32210de4d0f46ae2547d604d9f1d02769e98bd32","0d5bf91705d7b9956ac7097ebb896c9b142afc51","c0d54c30769b0276a143c2f77b897202d818105f","38718a55ce8fb52eb09cf04765c444a9df1255c9","8cdd86e25bbc6aff1654eeff3fc65f3f42b1e4af","d2c1716c99ff9886e6dac60c6a42926c801be7f4","0248e5d62e589dd6cfc0ec543b5c22a7c14128ea"];
function verifyCrosswalk(r,slices){
  const fail=m=>{throw Error(m);},obj=x=>x!==null&&typeof x==="object"&&!Array.isArray(x);
  const parse=x=>{if(typeof x!=="string")return null;const m=/^https:\/\/([^/?#]+)(\/[^?#]*)?(?:\?[^#]*)?$/.exec(x);return m&&!m[1].includes("@")?{host:m[1].toLowerCase(),path:m[2]||"/"}:null;};
  if(!obj(r)||r.schema!=="fv-p0-current-view-exact-origin-v1"||!Array.isArray(r.slots)||r.slots.length!==6||!Array.isArray(slices)||slices.length!==9||!Array.isArray(r.source_slices)||r.source_slices.length!==9)fail("Unrecognized/missing P0 or nine-slice input");
  const posts=new Map(),imgs=new Map();let total=0,offsite=0;
  for(let i=0;i<9;i++){
    const s=slices[i],pin=r.source_slices[i];
    if(!obj(s)||s.schema!=="fv-66-view-slice-v1"||s.slice!==i+1||s.listing_total!==66||!Array.isArray(s.posts)||!Array.isArray(s.images)||!obj(pin)||pin.path!==`qa/media-recovery/live_66_view_slice_${i+1}_20261117.json`||!/^[a-f0-9]{40}$/.test(pin.sha))fail("Source pin/order");
    for(const p of s.posts){
      if(!Number.isInteger(p.id)||posts.has(p.id)||!parse(p.url)||p.list_modified!==p.view_modified||!Number.isInteger(p.image_slots))fail("Malformed/duplicate post");
      posts.set(p.id,{...p,count:0,ext:0});
    }
    for(const im of s.images){
      const a=parse(im.authored_view_src),b=parse(im.source_origin_url),key=`${im.post_id}:${im.slot}`,p=posts.get(im.post_id);
      if(!a||!b||!p||imgs.has(key)||!Number.isInteger(im.slot)||im.slot<0||b.host!==im.origin_host||!["third_party_direct","third_party_jetpack","first_party_jetpack"].includes(im.route_type)||im.visitor_http_status!==null||im.visitor_wire_bytes!==null||im.visitor_decode!==null||im.rights_rehosting!=="HOLD"||im.replacement_approved!==false)fail("Malformed/duplicate image or fabricated guest");
      const jp=/^i[0-3]\.wp\.com$/.test(a.host);
      if((im.route_type==="third_party_direct"&&(jp||b.host==="finalvestige.com"))||(im.route_type==="third_party_jetpack"&&(!jp||b.host==="finalvestige.com"))||(im.route_type==="first_party_jetpack"&&(!jp||b.host!=="finalvestige.com")))fail("Source host classification");
      imgs.set(key,im);p.count++;const off=im.route_type!=="first_party_jetpack";p.ext+=off?1:0;total++;offsite+=off?1:0;
    }
  }
  if(posts.size!==66||total!==361||offsite!==294)fail("Full 66/361/294 census mismatch");
  for(const p of posts.values()){if(p.count!==p.image_slots||p.ext!==p.third_party_slots)fail("Per-post image count drift");for(let i=0;i<p.image_slots;i++)if(!imgs.has(`${p.id}:${i}`))fail("Image slot gap");}
  const order=["285:5","285:2","287:5","418:1","418:2","407:1"];let numeric=0,tool=0,different=0;
  for(let i=0;i<6;i++){
    const e=r.slots[i],im=imgs.get(order[i]),post=posts.get(e?.post_id),a=parse(e?.authored_view_src),b=parse(e?.origin_url_view_exact);
    if(!obj(e)||e.slot!==order[i]||!im||!post||!a||!b||post.url!==e.post_url||post.view_modified!==e.view_revision||im.authored_view_src!==e.authored_view_src||im.source_origin_url!==e.origin_url_view_exact||im.origin_host!==e.origin_host||im.alt!==e.alt||im.route_type!==e.source_route||e.source_route!=="third_party_jetpack")fail("P0 actual VIEW/alt/revision mismatch");
    if(!/^i[0-3]\.wp\.com$/.test(a.host)||decodeURIComponent(a.path)!==`/${b.host}${decodeURIComponent(b.path)}`)fail("Unproven Jetpack-origin path join");
    if(!parse(e.previous_probe_url)||e.previous_probe_was_exact!==(e.previous_probe_url===e.origin_url_view_exact))fail("False lexical original URL identity");
    if(!e.previous_probe_was_exact)different++;
    if(!obj(e.probe)||e.probe.requested_url!==e.origin_url_view_exact||e.probe.method!=="independent public retriever, not guest browser"||!e.probe.checked_at)fail("Origin probe not exact");
    if(e.probe.kind==="HTTP_ERROR"){if(![403,404].includes(e.probe.status)||e.probe.note!==null)fail("Unproven numeric HTTP");numeric++;}
    else if(e.probe.kind==="TOOL_ERROR"){if(e.probe.status!==null||typeof e.probe.note!=="string"||!e.probe.note)fail("Retriever wrapper error cannot be origin HTTP");tool++;}
    else fail("Unknown observer status");
    if(!obj(e.visitor)||Object.values(e.visitor).some(x=>x!==null)||e.rights!=="HOLD"||e.rehost_allowed!==false||e.wp_write_allowed!==false||e.post_rewrite_allowed!==false)fail("Fabricated guest/rights or forbidden writes");
    const c=e.candidate;
    if(!obj(c)||c.rehost_cleared!==false||c.exact_frame_verified!==false||c.binary_sha256!==null)fail("Replacement not approved");
    if((c.native_px===null)!==(c.target_px===null))fail("Unverified native pixel dimensions");
    if(c.native_px){const n=c.native_px,t=c.target_px;if(![n.width,n.height,t.width,t.height].every(v=>Number.isInteger(v)&&v>0)||Math.max(t.width,t.height)>960||t.width>n.width||t.height>n.height||Math.abs(t.width/n.width-t.height/n.height)>0.003)fail("No upscale/960/aspect gate");}
  }
  if(different!==1||r.slots[0].previous_probe_was_exact!==false||numeric!==4||tool!==2)fail("P0 results or path normalization misrepresented");
  const x=r.summary;
  if(!obj(x)||x.posts_in_source_snapshot!==66||x.images_in_source_snapshot!==361||x.external_origin_slots!==294||x.P0_source_slots!==6||x.public_origin_numeric_http_errors!==4||x.public_retriever_tool_errors!==2||x.previous_origin_url_spelling_differences!==1||x.guest_confirmed_failures!==null||x.verified_76_percent_wire_savings!==null||x.visitor_transfer_bytes!==null||x.oversized_originals_decimal_1_5MB!==20||x.oversized_stored_bytes!==64385752||x.production_writes!==0||x.subscription_spend_usd!==0)fail("Unverified performance/production claim");
  return {status:"SOURCE_ONLY_HOLD",source_posts:66,source_image_slots:361,source_external_slots:294,p0_matched:6,previous_probe_path_differences:1,exact_view_derived_origin_probes:6,origin_http_errors:4,retriever_tool_errors:2,confirmed_guest_failures:null,rights_approvals:0};
}
function loadPinned(){return PINNED.map((sha,i)=>{const file=path.join(__dirname,'live_66_view_slice_'+(i+1)+'_20261117.json');const raw=fs.readFileSync(file);const actual=crypto.createHash('sha1').update('blob '+raw.length+'\0').update(raw).digest('hex');if(actual!==sha)throw Error('Immutable source blob mismatch slice '+(i+1));return JSON.parse(raw.toString('utf8'));});}
module.exports={verifyCrosswalk,loadPinned,PINNED};
if(require.main===module){try{const file=process.argv[2];if(!file)throw Error('Usage: node validate_p0_current_view_origin_20261117.cjs report.json');const r=JSON.parse(fs.readFileSync(file,'utf8'));console.log(JSON.stringify(verifyCrosswalk(r,loadPinned()),null,2));}catch(e){console.error('HOLD: '+e.message);process.exitCode=1;}}
