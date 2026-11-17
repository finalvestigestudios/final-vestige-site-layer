'use strict';
function validate(m){
 const e=[],a=(condition,msg)=>{if(!condition)e.push(msg)};
 a(m.schema==='fv-sitewide-media-source-collision-20261117-v1','schema');
 a(m.evidence_method==='HISTORICAL_WORDPRESS_AUTHORED_SOURCE_PLUS_FRESH_AUTHENTICATED_WP_VIEW_NO_GUEST_CRAWL','method');
 a(m.source_parts?.ref==='4366489a68620d26592d8438b4402feb453c3166'&&m.source_parts?.files?.length===8,'8 source pins');
 for(let i=0;i<8;i++){const p=m.source_parts?.files?.[i]||{};a(p.path===('qa/media-recovery/parts/'+String(i+1).padStart(2,'0')+'.json')&&/^[a-f0-9]{40}$/.test(p.sha||''),'pin '+i)}
 const h=m.historical||{};
 a(h.posts===61&&h.image_references===355&&h.distinct_urls===353,'historical count');
 a(h.first_party===60&&h.jetpack_proxy===7&&h.external===170&&h.wikimedia_redirect===118&&h.offsite_refs===288,'sources');
 a(m.host_concentration?.length===h.distinct_hosts,'hosts length');
 a(m.host_concentration?.reduce((n,r)=>n+r.count,0)===355,'hosts sum');
 a(m.host_concentration?.find(x=>x.host==='commons.wikimedia.org')?.count===118,'Wikimedia concentration');
 a(m.identical_original_url_groups?.length===2,'two repeated URL groups');
 const all=[];
 for(const g of m.identical_original_url_groups||[]){a(g.slots?.length===2,'pair length');a(g.slots?.[0]?.view_url===g.slots?.[1]?.view_url,'published identical');
 for(const s of g.slots||[]){all.push(s.key);a(s.source_url===g.source_url&&/^https:\/\//.test(s.view_url||''),'matching src');
 a(s.guest_current_src===null&&s.guest_http_status===null&&s.guest_mime===null&&s.guest_decode===null&&s.guest_natural_width===null&&s.guest_transfer_bytes===null,'invented guest evidence '+s.key)}
 }
 a(JSON.stringify(all.sort())===JSON.stringify(['213:2','213:6','291:2','291:5']),'exact slots');
 a(m.identical_original_url_groups?.find(x=>x.slots?.[0]?.key==='291:2')?.classification==='VISUAL_ALT_MISMATCH_SOURCE_LEVEL','Teton mismatch');
 a(m.identical_original_url_groups?.find(x=>x.slots?.[0]?.key==='213:2')?.classification==='SHARED_OFFICIAL_MAP_CONTEXT_REVIEW','Mann no failure');
 const c=m.archive_candidate||{};
 a(c.target_slot==='291:2'&&c.accession==='NAID 28894684'&&c.catalog==='https://catalog.archives.gov/id/28894684','NARA id');
 a(JSON.stringify(c.current_commons_native_px)==='[2558,1728]'&&JSON.stringify(c.proportional_review_px)==='[960,649]','960px');
 a(c.crop_revision?.startsWith('2023 Commons')&&c.same_as_current_published_frame_verified===false,'crop provenance');
 a(c.downloaded_binary_sha256===null&&c.browser_status===null&&c.rights_approved===false&&c.wp_rehosting_approved===false,'no fabricated clearance');
 const claims=m.claims||{};
 a(claims.reported_42_visitor_broken_confirmed===false&&claims.proposed_76_percent_wire_reduction_measured===false&&claims.wire_bytes_observed===null,'visitor claims');
 a(claims.over_1_5_decimal_MB_media_originals===20&&claims.over_1_5_decimal_MB_original_bytes===64385752,'stored originals');
 for(const [k,v]of Object.entries(m.safety||{}))a(v===true,'safety '+k);
 a(Object.keys(m.safety||{}).length===7,'all safety gates');
 a(m.plan?.includes('Site QA #154')&&m.plan?.includes('rollback'),'plan');
 return{ok:e.length===0,errors:e,metrics:{image_references:355,distinct_urls:353,duplicates:2,hosts:h.distinct_hosts}};
}
if(typeof require!=='undefined'&&typeof module!=='undefined'&&require.main===module){
const fs=require('node:fs'),path=require('node:path');
try{const p=process.argv[2]||path.join(__dirname,'origin_collision_61_20261117_0323pt.json');const verdict=validate(JSON.parse(fs.readFileSync(p,'utf8')));console.log(JSON.stringify(verdict,null,2));if(!verdict.ok)process.exitCode=1;}catch(e){console.error('MEDIA_AUDIT_READ_ERROR '+e.message);process.exitCode=2}
}
if(typeof module!=='undefined')module.exports={validate};
