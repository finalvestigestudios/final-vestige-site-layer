'use strict';
// Read-only release gate; Node CLI uses local JSON only, no fetches or CMS writes.
function fail(s){throw Error('Skyway recovery HOLD: '+s)}
function verify(a){
 if(!a||a.schema!=='fv-skyway-2875-candidate-decision-v1'||a.source_p0_image_key!=='287:5'||a.article_id!==287)fail('identity');
 if(a.published_original_source_url!=='https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg')fail('source drift');
 if(a.visitor_browser_http_status!==null||a.visitor_browser_natural_dimensions!==null||a.visitor_browser_transferred_bytes!==null||a.visitor_broken!==null)fail('fabricated browser proof');
 if(a.reported_42_broken!=='UNVERIFIED'||a.reported_76_percent_transfer_reduction!=='UNMEASURED')fail('unverified sitewide claims');
 for(const k of ['replacement_authorized','wordpress_write_authorized','image_downloaded','site_qa_collector_modified','homepage_modified'])if(a[k]!==false)fail('unsafe action '+k);
 if(a.spend_usd!==0||a.conditional_max_width_px!==960||a.no_upscaling!==true)fail('funds or geometry');
 if(!Array.isArray(a.observations)||a.observations.length!==2)fail('retriever observations');
 const seenStatus=new Set(),seenCandidate=new Set();
 for(const o of a.observations){
  if(o.method!=='web_open_retriever'||o.status_is_guest_browser_http!==false||o.status_is_authoritative_origin_http!==false||o.content_pixel_sha256!==null)fail('retriever misrepresented as browser/origin');
  if(!['404_NOT_FOUND_FROM_RETRIEVER','IMAGE_RENDERED_FROM_RETRIEVER'].includes(o.result))fail('unverified wrapper result');
  seenStatus.add(o.result);
 }
 if(seenStatus.size!==2)fail('missing original/relocated comparison');
 if(!Array.isArray(a.candidates)||a.candidates.length!==4)fail('candidate count');
 for(const c of a.candidates){
  if(typeof c.candidate_id!=='string'||seenCandidate.has(c.candidate_id))fail('candidate identity');seenCandidate.add(c.candidate_id);
  if(!c.catalog_url?.startsWith('https://')||!c.creator_or_credit||!c.license||!c.relationship||!c.description)fail('source/rights provenance');
  if(c.item_level_rights_verified!==false||c.wp_upload_authorized!==false||c.requires_alt_change!==true)fail('premature release');
  if(c.pixel_width!==null||c.pixel_height!==null||c.conditional_preview_width!==null||c.conditional_preview_height!==null)fail('invented dimensions');
 }
 if(!seenCandidate.has('usf-gandy-4724')||!seenCandidate.has('usf-gandy-4754')||!seenCandidate.has('florida-memory-rc09236')||!seenCandidate.has('publisher-relocated-same-name'))fail('missing authoritative option');
 const a0=a.candidates.find(c=>c.candidate_id==='publisher-relocated-same-name');
 if(a0.asset_or_item_url!=='https://media.stpetecatalyst.com/uploads/2020/04/Skyway-Bridge-documentary.jpg'||!a0.license.includes('not established'))fail('publisher identity/rights');
 const usf=a.candidates.find(c=>c.candidate_id==='usf-gandy-4724');
 if(!usf.description.includes('catalog ALT describes a boat bow'))fail('missing catalog conflict');
 if(!Array.isArray(a.restoration_requirements)||a.restoration_requirements.length<6)fail('rollback guard');
 return {decision:'HOLD_NO_CMS_WRITE',audited_candidates:4,known_guest_broken:null,can_publish:false};
}
function previewSize(w,h){
 if(!Number.isInteger(w)||!Number.isInteger(h)||w<=0||h<=0)fail('intrinsic dimension unknown');
 const newWidth=Math.min(960,w);
 return {width:newWidth,height:Math.round(h*newWidth/w)};
}
module.exports={verify,previewSize};
if(require.main===module){
 try{const fs=require('node:fs');const p=process.argv[2];if(!p)fail('supply local audit path');
 const s=fs.readFileSync(p,'utf8');if(s.length>80000)fail('oversized input');
 console.log(JSON.stringify(verify(JSON.parse(s)),null,2));
 }catch(e){console.error(e.message);process.exitCode=2;}
}
