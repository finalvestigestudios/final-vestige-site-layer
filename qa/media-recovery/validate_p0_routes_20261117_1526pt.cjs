#!/usr/bin/env node
'use strict';
function verify(x){
 const fail=m=>{throw new Error(m)};
 const url=s=>typeof s==='string'&&s.startsWith('https://')&&s.length>12&&!/\s/.test(s);
 if(!x||x.schema!=='fv-p0-route-ledger-v1')fail('schema');
 const h=x.historical;if(!h||h.posts!==61||h.slots!==355||h.current_published_count_separate!==66||h.broken_42_browser_proven!==null||h.savings_76_wire_proven!==null||h.over_1500000_bytes!==20||h.stored_original_bytes!==64385752)fail('false metrics');
 if(x.production_writes!==0||x.subscription_spend!==0||!x.visitor||Object.values(x.visitor).some(v=>v!==null))fail('fabricated visitor or production data');
 const keys=['285:5','285:2','287:5','418:1','418:2','407:1'];
 if(!Array.isArray(x.entries)||x.entries.length!==6)fail('six slots');
 x.entries.forEach((e,i)=>{
  if(!e||e.slot!==keys[i]||!url(e.source_url))fail('slot/source');
  const p=e.probe;if(!p||p.guest_verified!==false)fail('retriever not Chromium');
  if(p.type==='HTTP_ERROR'){if(![403,404].includes(p.http_status)||p.tool_issue!==null)fail('HTTP result')}
  else if(p.type!=='TOOL_ERROR'||p.http_status!==null||!p.tool_issue)fail('tool error not HTTP');
  const c=e.replacement;if(!c||!url(c.catalog_url)||(c.candidate_url!==null&&!url(c.candidate_url))||!c.rights||c.exact_frame_verified!==false||c.rehost_cleared!==false||c.credit_confirmed!==false||c.binary_sha256!==null)fail('rights and provenance HOLD');
  const n=c.native_px,t=c.target_px;
  if(n===null){if(t!==null)fail('invented size')}
  else if(!Number.isSafeInteger(n.width)||!Number.isSafeInteger(n.height)||n.width<1||n.height<1||!t||t.width!==Math.min(960,n.width)||t.height!==Math.round(t.width*n.height/n.width))fail('960px no upscale');
  if(e.allowed_wp_upload!==false||e.allowed_post_rewrite!==false)fail('write forbidden');
 });
 if(x.entries[1].probe.type!=='TOOL_ERROR'||x.entries[5].probe.http_status!==null||x.entries[4].replacement.target_px.width!==600||x.entries[4].replacement.target_px.height!==463)fail('known cases');
 return {status:'HOLD',public_retriever_http_errors:4,public_retriever_tool_errors:2,guest_browser_confirmed_broken:null,rehost_authorized:false};
}
module.exports={verify};
if(require.main===module){try{const f=require('node:fs'),p=process.argv[2];if(!p)throw Error('Usage: node validate_p0_routes.cjs ledger.json');console.log(JSON.stringify(verify(JSON.parse(f.readFileSync(p,'utf8'))),null,2));}catch(e){console.error('HOLD: '+e.message);process.exitCode=1;}}
