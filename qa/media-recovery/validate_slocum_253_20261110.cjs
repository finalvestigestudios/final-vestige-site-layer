'use strict';
function assert(condition,message){if(!condition)throw new Error(message);}
function validate(a,c){
 assert(a.schema==='fv-slocum-253-seven-sources-v1','batch schema');
 assert(a.frozen_fixture.blob_sha==='9b16b828342a9ac338f3e65610fd3d8d508355e9','frozen snapshot SHA');
 assert(a.entries.length===7,'seven source records');
 assert(c.rows.length===288&&c.counts.researched_unique===188&&c.counts.unresearched===100&&c.counts.total_evidence_records===193,'site-wide counts');
 assert(c.rows.filter(r=>r.evidence.length).length===188,'researched coverage');
 assert(c.rows.filter(r=>r.evidence.length===0).length===100,'remaining coverage');
 assert(new Set(c.rows.map(r=>r.slot)).size===288,'unique slots');
 assert(a.reported_42_browser_verified===false&&a.measured_wire_reduction_76_percent===false,'no invented successes');
 const named=['PS%20General%20Slocum','General%20slocum%20burning','LCCN2009632218','LCCN2009632220','LCCN2009632224','LCCN2009632223','Memorial%20Tompkins'];
 for(let i=0;i<a.entries.length;i++){
  const e=a.entries[i],key='253:'+i,r=c.rows.find(q=>q.slot===key);
  assert(e.slot===key&&!!r,'slot');
  assert(e.original_published_url===r.stored_url&&e.original_published_url.includes(named[i]),'exact source join and named accession');
  assert(e.original_published_url.startsWith('https://commons.wikimedia.org/wiki/Special:Redirect/file/')&&e.original_published_url.endsWith('?width=1280'),'literal original URL');
  assert(e.guest_http_status===null&&e.origin_http_status===null&&e.guest_current_src===null&&e.guest_decoded_pixels===null&&e.guest_wire_bytes===null&&e.visitor_broken===null,'no fabricated HTTP or bytes');
  assert(r.guest_http_status===null&&r.guest_current_src===null&&r.guest_decoded_px===null&&r.guest_wire_bytes===null&&r.guest_broken===null,'census no fabricated browser measurements');
  for(const k of ['exact_binary_match_verified','scene_crop_match_verified','rights_cleared','download_allowed','cache_allowed','wp_upload_allowed','post_rewrite_allowed','release_allowed'])assert(e[k]===false,'release HOLD '+k);
  assert(r.cache_authorized===false&&r.wordpress_media_upload_authorized===false&&r.rights_cleared===false,'census release HOLD');
  const [w,h]=e.catalog_original_px,[dw,dh]=e.conditional_960px;
  assert(Number.isInteger(w)&&w>0&&Number.isInteger(h)&&h>0,'catalog geometry');
  assert(dw===Math.min(960,w)&&dh===Math.round(h*dw/w),'no upscaling, aspect ratio');
  assert(r.evidence.length===1&&r.evidence[0].batch==='slocum253','source evidence');
  assert(r.candidate_sources.length===1&&r.candidate_sources[0].item_rights_cleared===false,'candidate needs rights');
  assert(r.candidate_sources[0].catalog_url===e.commons_catalog_url,'catalog binding');
 }
 assert(a.entries.filter(e=>e.primary_archive_item_url).length===4,'four LOC records');
 for(const i of [2,3,4,5])assert(a.entries[i].primary_archive_item_url==='https://www.loc.gov/item/'+['2009632218','2009632220','2009632224','2009632223'][i-2]+'/','LOC accession join');
 return true;
}
if(typeof module!=='undefined')module.exports={validate};

