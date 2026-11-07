'use strict';
function validate(a){
 const errors=[],chk=(b,s)=>{if(!b)errors.push(s)};
 chk(a.schema==='fv-hero-png-wp-metadata-v1'&&a.method.includes('NOT visitor-browser'),'method');
 chk(a.reported_broken_42==='UNVERIFIED'&&a.claimed_76pct_wire_reduction==='UNMEASURED','claims');
 chk(a.visitor_http===null&&a.visitor_transfer_bytes===null,'guest metrics');
 chk(a.rights==='HOLD'&&a.alpha==='UNKNOWN'&&a.production_changed===false,'holds');
 chk(Array.isArray(a.rows)&&a.rows.length===5,'row count');
 let sum=0;const ps=new Set(),ms=new Set();
 for(const r of a.rows){
  chk(r.slot===r.post+':0'&&r.media===r.post+5&&!ps.has(r.post)&&!ms.has(r.media),'unique slots');
  ps.add(r.post);ms.add(r.media);
  chk(r.post_url.startsWith('https://finalvestige.com/2026/08/16/'),'post URL');
  chk(/^https:\/\/finalvestige\.com\/wp-content\/uploads\/2026\/08\/[a-z0-9-]+\.png$/.test(r.original_src),'origin URL');
  chk(r.mime==='image/png'&&JSON.stringify(r.native_px)==='[1672,941]'&&r.cms_subsizes===0,'actual metadata');
  chk(JSON.stringify(r.stored_html_px)==='[1024,576]'&&r.stored_srcset===false,'source HTML');
  chk(r.stored_alt.length>15&&r.figcaption.startsWith('AI-assisted historical reconstruction')&&r.media_alt_reconstruction===true&&r.media_title_reconstruction===true,'historic provenance disclosure');
  chk(JSON.stringify(r.proposed_preview)==='[960,540]'&&r.derivative_created===false,'conditional no-upscale');
  chk(r.guest_http===null&&r.guest_current_src===null&&r.guest_encoded_bytes===null&&r.guest_decode===null,'no fabricated browser result');
  chk(r.rights_hold===true&&r.visual_hold===true&&r.download===false&&r.wp_write===false,'no publication');
  sum+=r.original_bytes;
 }
 chk([...ps].sort((a,b)=>a-b).join(',')==='34,35,36,37,38','posts');
 chk([...ms].sort((a,b)=>a-b).join(',')==='39,40,41,42,43','media');
 chk(sum===13267538&&sum===a.original_storage_bytes,'storage only');
 return {ok:errors.length===0,errors,metrics:{rows:ps.size,recorded_original_storage_bytes:sum,visitor_transfer_measured:false}};
}
if(typeof module!=='undefined')module.exports={validate};
if(typeof require!=='undefined'&&require.main===module){const fs=require('node:fs');const r=validate(JSON.parse(fs.readFileSync(process.argv[2],'utf8')));console.log(JSON.stringify(r,null,2));if(!r.ok)process.exitCode=1;}
