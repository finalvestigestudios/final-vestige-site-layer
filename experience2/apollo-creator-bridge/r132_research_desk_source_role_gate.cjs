'use strict';
/**
 * Apollo R132 Research Desk editorial-custody audit.
 * Read-only: verifies the isolated six-card review artifact, not a deployed page.
 * The original Research Desk PR #158 is deliberately not modified.
 */
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const PINNED_RESEARCH_DESK_BLOB='403d128c57b9bc82dac7c619651689070edef86c';
const RECORDS=Object.freeze([
 ['01','https://www.nasa.gov/image-detail/apollo-1-crew-honored/','1967-01','PHOTO_CONTEXT_ID_PROVISIONAL'],
 ['02','https://www.nasa.gov/image-detail/amf-s67-15717/','1967-01-03','PHOTO_CONTEXT_NOT_PRESSURE'],
 ['03','https://www.nasa.gov/image-detail/amf-s66-58038/','1966-10-18','PHOTO_CONTEXT_NOT_TELEMETRY'],
 ['04','https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/','2017-01-24','PHOTO_RETROSPECTIVE_NOT_FIRE'],
 ['05','https://www.nasa.gov/image-detail/amf-s67-21294/','1967-01-28','PHOTO_CONTEXT_NOT_IGNITION'],
 ['06','https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/','2017-01-24','PHOTO_RETROSPECTIVE_NOT_TEST']
]);
const BOARD='https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/';
function gitBlob(content){
 const body=Buffer.from(content,'utf8');
 return crypto.createHash('sha1').update(Buffer.from('blob '+body.length+'\0','utf8')).update(body).digest('hex');
}
function audit(html,upstream){
 const errors=[];
 if(typeof html!=='string'||!html.startsWith('<section class="fv-ex2-ledger"')) errors.push('INVALID_ROOT');
 if(typeof upstream==='string'&&gitBlob(upstream)!==PINNED_RESEARCH_DESK_BLOB) errors.push('UPSTREAM_PR158_SOURCE_DRIFT');
 if(!html.includes('data-fv-r132-research-bridge')||!html.includes('Technical claims rely on the Apollo 204 Review Board'))errors.push('MISSING_SOURCE_ROLE_KEY');
 if(!html.includes('All six photographs require individual reuse review'))errors.push('MISSING_RIGHTS_BOUNDARY');
 if(!html.includes('The crew-portrait catalog ID is provisional'))errors.push('PORTRAIT_UNCERTAINTY_NOT_VISIBLE');
 if(/<(?:img|picture|canvas|iframe|script|form|video|audio|embed|object)\b/i.test(html))errors.push('UNREVIEWED_MEDIA_OR_COLLECTION');
 if(/(?:utm_campaign|utm_content|paypal|payhip|checkout|affiliate|dataLayer|localStorage|sessionStorage|sendBeacon)\s*=/i.test(html))errors.push('UNAPPROVED_COMMERCE_OR_TRACKING');
 if(/\s+on(?:click|load|error|submit|input)\s*=/i.test(html))errors.push('INLINE_EVENT_HANDLER');
 const cards=[...html.matchAll(/<article class="fv-ex2-ledger__card" id="fv-ex2-ledger-apollo1-record-(\d{2})"[\s\S]*?<\/article>/g)];
 if(cards.length!==6)errors.push('SIX_CARD_COUNT_MISMATCH');
 const cardsById=new Map();
 for(const card of cards){
  const id=card[1];
  if(cardsById.has(id))errors.push('DUPLICATE_CARD_'+id);
  cardsById.set(id,card[0]);
 }
 for(const [id,url,date,role] of RECORDS){
  const card=cardsById.get(id);
  if(!card){errors.push('MISSING_CARD_'+id);continue;}
  if(!card.includes('data-fv-r132-photo-role="'+role+'"')||!card.includes('data-fv-r132-photo-date="'+date+'"'))errors.push('PHOTO_DATE_OR_ROLE_DRIFT_'+id);
  const links=[...card.matchAll(/<a\b[^>]*>/g)].map(x=>x[0]);
  const photo=links.filter(a=>a.includes('href="'+url+'"'));
  if(photo.length!==1||!photo[0].includes('noopener')||!photo[0].includes('noreferrer')||!card.includes('NASA photograph (visual context)'))errors.push('PHOTO_LINK_CUSTODY_'+id);
  if(id!=='01'&&!(links.some(a=>a.includes('href="'+BOARD+'"'))&&card.includes('Technical source: Apollo 204 Review Board')))errors.push('BOARD_TECHNICAL_SOURCE_MISSING_'+id);
  if(!card.includes('commercial republication and identifiable-person uses are not cleared'))errors.push('RIGHTS_DISCLOSURE_MISSING_'+id);
  if(id==='01'&&(!card.includes('S67-19766 unverified')||!card.includes('source page does not confirm')))errors.push('UNVERIFIED_PORTRAIT_ID_'+id);
  if((id==='04'||id==='06')&&!card.includes('2017 retrospective'))errors.push('RETROSPECTIVE_YEAR_UNCLEAR_'+id);
 }
 const photoLinks=[...html.matchAll(/href="https:\/\/www\.nasa\.gov\/image-detail\//g)].length;
 if(photoLinks!==6)errors.push('NASA_PHOTO_LINK_COUNT_'+photoLinks);
 if(!html.includes('data-fvx-tools hidden')||!html.includes('<details class="fv-ex2-ledger__fulltext">'))errors.push('NO_JS_FAIL_OPEN_UNPROVEN');
 if(html.includes('data-fv-r132-approved-live'))errors.push('UNAUTHORIZED_RELEASE_FLAG');
 return {schema:'fv.apollo.r132.source-roles.v1',status:errors.length?'FAIL':'PASS',errors,
  reviewed_records:cards.length,photo_links:photoLinks,upstream_checked:typeof upstream==='string',
  rights:'0_OF_6_CLEARED',release:'STAGING_HOLD',browser_acceptance:'NOT_ESTABLISHED',
  revenue:'NO_VERIFIED_OFFER_OR_CONFIRMED_PURCHASE'};
}
module.exports={audit,gitBlob,RECORDS,PINNED_RESEARCH_DESK_BLOB};
if(require.main===module){
 const content=fs.readFileSync(path.join(__dirname,'r132_research_desk_source_role_review.html'),'utf8');
 const extra=process.argv.indexOf('--upstream');
 const upstream=extra>=0&&process.argv[extra+1]?fs.readFileSync(process.argv[extra+1],'utf8'):undefined;
 const report=audit(content,upstream);
 process.stdout.write(JSON.stringify(report,null,2)+'\n');
 process.exitCode=report.status==='PASS'?0:2;
}
