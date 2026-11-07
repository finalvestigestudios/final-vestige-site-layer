'use strict';
const fs=require('node:fs'),path=require('node:path');
const filenames=['Palomares_H-Bomb_Incident.jpg','Operation_Chrome_Dome_route.jpg','USS_Skill_(MSO-471)_operating_off_the_coast_of_Spain,_in_February_1966_(428-NPC-36556).jpg','Zoeken_naar_H_bom_in_Spanje,_de_Alvin_wordt_te_water_gelaten,_Bestanddeelnr_918-8161.jpg','CURV-I-H-Bomb-Recovery-300x243.jpg','428-GX-_USN_118930_(26941557635).jpg','1966_Palomares_B-52_crash_-_recovered_H-bomb.jpg','Palomares_barrels.jpg','Recovered_Mk_28RI_bomb.JPG'];
function validate(d) {
 const e=[],need=(v,s)=>{if(!v)e.push(s)};
 need(d.schema==='fv-media-palomares367-v1'&&d.article?.id===367&&d.article?.status==='publish','identity');
 need(d.historical_census?.inline===355&&d.historical_census?.external===288&&d.fresh_prior_census?.inline===361&&d.fresh_prior_census?.external===294,'cohorts');
 need(d.reported_42_broken==='UNVERIFIED'&&d.claimed_76_percent_transfer_reduction==='UNMEASURED','unverified claims');
 need(d.site_qa_pr===154&&d.production_writes===0&&d.asset_downloads===0&&d.spend===0,'production HOLD');
 need(Array.isArray(d.rows)&&d.rows.length===9,'nine rows');
 let ext=0,unsized=0,requests=0,exceeds=0,masters=0;
 for(const [i,r] of (d.rows||[]).entries()){
  if(i>=9){e.push('extra row');break}
  need(r.slot==='367:'+i,'slot '+i);
  const src=typeof r.published_src==='string'?decodeURIComponent(r.published_src):'';
  const cat=typeof r.catalog_url==='string'?decodeURIComponent(r.catalog_url):'';
  need(src.startsWith('https://')&&src.includes(filenames[i]),'source identity '+i);
  need(typeof r.published_alt==='string'&&r.published_alt.length>20&&typeof r.published_caption==='string'&&r.published_caption.length>15,'ALT caption '+i);
  need(r.html_srcset===null,'stored srcset '+i);
  need(r.kind===(i===0?'first_party':'third_party'),'kind '+i);
  if(i===0)need(src.startsWith('https://finalvestige.com/wp-content/uploads/')&&JSON.stringify(r.html_dimensions)==='[425,329]','local photo');
  else {ext++;need(r.html_dimensions===null,'unsized '+i);unsized++}
  if(i===4){need(src.startsWith('https://navalunderseamuseum.org/')&&cat==='https://navalunderseamuseum.org/petrel-helmet/','museum custody');need(r.requested_width_px===null,'museum width')}
  else if(i>0){
   need(src.startsWith('https://commons.wikimedia.org/wiki/Special:Redirect/file/')&&cat.startsWith('https://commons.wikimedia.org/wiki/File:'),'Commons '+i);
   need(src.split('/file/')[1]?.split('?')[0].replace(/_/g,' ')===cat.split('/File:')[1]?.replace(/_/g,' '),'catalog file match '+i);
   need(r.requested_width_px===1280,'request 1280 '+i);requests++;
  }
  const m=r.catalog_master_px,p=r.preview_max_960_px;
  if(m){masters++;const w=Math.min(960,m[0]);need(Number.isInteger(m[0])&&Number.isInteger(m[1])&&m[0]>0&&m[1]>0,'master '+i);need(JSON.stringify(p)===JSON.stringify([w,Math.round(m[1]*w/m[0])]),'no-upscale '+i);need(r.request_exceeds_master===(r.requested_width_px!==null&&r.requested_width_px>m[0]),'request exceeds '+i)}
  else need(i===4&&p===null&&r.request_exceeds_master===false,'unknown geometry '+i);
  if(r.request_exceeds_master)exceeds++;
  need(r.rights_review==='HOLD'&&r.binary_match_verified===false&&r.rehost_authorized===false,'rights HOLD '+i);
  need(typeof r.archive_note==='string'&&r.archive_note.length>12&&typeof r.rights_label==='string'&&r.rights_label.length>=3,'archive record '+i);
  need(r.actual_guest_http===null&&r.actual_guest_current_src===null&&r.actual_guest_decode_px===null&&r.actual_guest_encoded_bytes===null&&r.actual_guest_broken===null,'no fabricated guest '+i);
 }
 const s=d.summary||{};
 need(ext===8&&unsized===8&&requests===7&&exceeds===4&&masters===8,'recount');
 need(s.inline===9&&s.third_party===ext&&s.unsized===unsized&&s.commons_requests_1280===requests&&s.requested_larger_than_catalog===exceeds&&s.known_catalog_geometry===masters&&s.confirmed_guest_failures===null,'summary');
 return {ok:e.length===0,errors:e,metrics:{images:9,offsite:ext,unsized,commons_1280:requests,requested_more_than_native:exceeds,known_geometry:masters}};
}
if(require.main===module){try{const file=process.argv[2]||path.join(__dirname,'palomares_367_nine_catalog_20261107.json');const result=validate(JSON.parse(fs.readFileSync(file,'utf8')));console.log(JSON.stringify(result,null,2));if(!result.ok)process.exitCode=1}catch(err){console.error(err.message);process.exitCode=2}}
module.exports={validate};
