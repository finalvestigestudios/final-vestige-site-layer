'use strict';
/** Offline source-identity/rights gate; never downloads, rehosts, rewrites or claims HTTP. */
const fs=require('node:fs');
const crypto=require('node:crypto');
const path=require('node:path');
const EXPECTED_SLOTS=['252:0','252:1','252:2','252:3','252:4','252:5'];
const MISMATCH=new Set(['252:1','252:4','252:5']);
const EXPECTED_SOURCE_SHA256='6a23056933a0bb97e481d1fc4474d42b70a857db8b648443942c955354d36c41';
function validate(d){
 const problems=[];const req=(ok,msg)=>{if(!ok)problems.push(msg)};
 req(d.post_id===252 && d.post_url==='https://finalvestige.com/2026/08/18/they-thought-the-books-were-charcoal/','post binding');
 req(d.audit_date==='2026-11-14' && d.post_modified_wp_local==='2026-11-14T18:44:18','snapshot provenance');
 req(Array.isArray(d.items)&&d.items.length===6,'six-slot inventory');
 req(d.browser_failure_count===null && d.claimed_42_broken_in_visitor_browser===null && d.claimed_76_percent_network_savings===null && d.production_changes===0,'unsupported sitewide claim');
 const images=Array.isArray(d.items)?d.items:[];
 const digest=crypto.createHash('sha256').update(images.map(x=>x.source_url).join('\n')).digest('hex');
 req(digest===EXPECTED_SOURCE_SHA256,'original source URL custody');
 images.forEach((im,i)=>{
  const key=EXPECTED_SLOTS[i];req(im.key===key && im.slot===i,\`slot binding \${i}\`);
  let parsed;try{parsed=new URL(im.source_url)}catch{}
  req(parsed?.protocol==='https:' && parsed?.hostname==='commons.wikimedia.org' && parsed?.pathname.startsWith('/wiki/Special:Redirect/file/'),\`untrusted source \${key}\`);
  let fn=null;try{fn=decodeURIComponent(parsed.pathname.split('/').pop()).replace(/ /g,'_')}catch{}
  req(fn===im.catalog_filename,\`catalog filename mismatch \${key}\`);
  req(im.catalog_url===\`https://commons.wikimedia.org/wiki/File:\${im.catalog_filename.replace(/ /g,'_')}\`,\`catalog link mismatch \${key}\`);
  const w=im.catalog_dimensions_px?.width,h=im.catalog_dimensions_px?.height;
  const tw=im.max_width_960_preserve_aspect_px?.width,th=im.max_width_960_preserve_aspect_px?.height;
  req(Number.isInteger(w)&&w>0&&Number.isInteger(h)&&h>0&&tw===Math.min(w,960)&&th===Math.round(h*tw/w),\`native/no-upscale geometry \${key}\`);
  req(im.browser_status===null && im.visitor_natural_width===null && im.visitor_transfer_bytes===null && im.source_binary_sha256===null,\`invented browser or binary proof \${key}\`);
  req(im.rights_cleared_for_rehost===false && im.wp_media_upload_authorized===false && im.replacement_binary_created===false,\`unauthorized publication \${key}\`);
  req(typeof im.live_alt==='string'&&typeof im.live_caption==='string'&&typeof im.catalog_description==='string'&&im.catalog_description.length>45&&typeof im.catalog_rights_claim==='string',\`missing descriptive provenance \${key}\`);
  req(im.identity_disposition===(MISMATCH.has(key)?'editorial_mismatch':'accurate_subject'),\`editorial classification \${key}\`);
  req(MISMATCH.has(key)?typeof im.proposed_alt_review_only==='string'&&im.proposed_alt_review_only.length>50:im.proposed_alt_review_only===null,\`editorial suggestion \${key}\`);
 });
 req(images[1]?.catalog_description?.includes('Ground plan') && images[1]?.live_alt?.includes('papyrus rolls'), 'Villa-plan-versus-scrolls identity');
 req(images[4]?.catalog_description?.includes('Casanova')&&images[4]?.live_alt?.includes('carbonized'), 'drawing-versus-fragment identity');
 req(images[5]?.catalog_description?.includes('Handwritten')&&images[5]?.live_alt?.includes('Digitized'), 'transcription-versus-papyrus identity');
 req(images[0]?.catalog_rights_claim==='CC BY 4.0'&&images[0]?.live_caption?.includes('CC BY 4.0'),'licensed research image credit');
 return problems;
}
if(require.main===module){const p=process.argv[2]||path.join(__dirname,'herculaneum_252_six_visual_identity_20261114.json');const errors=validate(JSON.parse(fs.readFileSync(p,'utf8')));if(errors.length){console.error(errors.join('\n'));process.exitCode=1}else console.log('PASS: 6 exact sources; 3 caption identity holds; rights/960px/browser claims fail closed')}
module.exports={validate};
