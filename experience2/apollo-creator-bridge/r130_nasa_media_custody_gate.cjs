'use strict';
/** R130: conservative NASA image source/custody gate; never treats citation as a paid-media license. */
const CANONICAL = Object.freeze([
  ['01','https://www.nasa.gov/image-detail/apollo-1-crew-honored/','1967-01','MONTH_ONLY'],
  ['02','https://www.nasa.gov/image-detail/amf-s67-15717/','1967-01-03','DAY'],
  ['03','https://www.nasa.gov/image-detail/amf-s66-58038/','1966-10-18','DAY'],
  ['04','https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/','2017-01-24','DAY'],
  ['05','https://www.nasa.gov/image-detail/amf-s67-21294/','1967-01-28','DAY'],
  ['06','https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/','2017-01-24','DAY']
]);
function auditMediaLedger(ledger,apollo) {
  const errors=[];
  if (!ledger || ledger.schema!=='fv.apollo.media-custody.v1' ||
      !Array.isArray(ledger.records) || ledger.records.length!==6 ||
      typeof apollo!=='string') return {
      schema:'fv.apollo.media-audit.v1', status:'FAIL',
      errors:['INVALID_LEDGER_OR_APOLLO_SOURCE'],release_status:'STAGING_HOLD'};
  const urls=new Set();
  for (let i=0;i<CANONICAL.length;i++){
    const [id,url,date,precision]=CANONICAL[i],r=ledger.records[i];
    if (!r || r.id!==id || r.source_url!==url || r.record_date!==date ||
        r.date_precision!==precision || urls.has(r.source_url))
      errors.push('UNTRUSTED_MEDIA_RECORD_'+id);
    if (!r) continue;
    urls.add(r.source_url);
    if (r.source_role!=='VISUAL_CONTEXT_NOT_TECHNICAL_MEASUREMENT' ||
        r.rights_status!=='NOT_CLEARED_FOR_FV_REPUBLICATION' ||
        r.endorsement!=='NOT_NASA_ENDORSED' ||
        !['PERSON_LIKENESS_NEEDS_REVIEW','UNDETERMINED_NOT_WAIVED'].includes(r.publicity_review))
      errors.push('UNSUPPORTED_RIGHTS_OR_SOURCE_CLAIM_'+id);
    if(r.metadata_evidence!==(id==='04'?'SECONDARY_NASA_ORIGIN_REFERENCE_ONLY':'PRIMARY_PAGE_VERIFIED'))
      errors.push('SOURCE_METADATA_VERIFICATION_OVERCLAIM_'+id);
    if(id==='01' && (r.catalog_status!=='S67-19766_PROPOSED_NOT_VERIFIED' ||
        r.date_precision!=='MONTH_ONLY'))errors.push('CREW_ID_DATE_OVERCLAIM');
    if ((id==='04'||id==='06') && r.visual_role!=='RETROSPECTIVE_DISPLAY')
      errors.push('RETROSPECTIVE_EXHIBIT_MISCLASSIFIED_'+id);
    if(!r.metadata_support || !/^https:\/\//.test(r.metadata_support))
      errors.push('UNTRACEABLE_MEDIA_EVIDENCE_'+id);
    const tableTag=apollo.match(new RegExp('<tr\\b[^>]*\\bid="photo-source-'+id+'"[^>]*>','i'));
    const handoutTag=apollo.match(new RegExp('<li\\b[^>]*\\bdata-fv-student-photo="'+id+'"[^>]*>','i'));
    if (!tableTag || !/\bdata-fv-photo-rights="not-cleared"/.test(tableTag[0]) ||
        !handoutTag || !/\bdata-fv-photo-rights="not-cleared"/.test(handoutTag[0]))
      errors.push('VISIBLE_REGISTER_WORKSHEET_RIGHTS_MARKER_'+id);
    const tableRow=apollo.match(new RegExp('<tr\\b[^>]*\\bid="photo-source-'+id+'"[^>]*>[\\s\\S]*?<\\/tr>','i'));
    const handout=apollo.match(new RegExp('<li\\b[^>]*\\bdata-fv-student-photo="'+id+'"[^>]*>[\\s\\S]*?<\\/li>','i'));
    if(!tableRow || !handout || !tableRow[0].includes('href="'+url+'"') ||
       !handout[0].includes('href="'+url+'"'))
      errors.push('REGISTER_TO_STUDENT_SOURCE_DRIFT_'+id);
  }
  if(!ledger.media_policy_sources || ledger.media_policy_sources.length<2 ||
     ledger.commercial_image_reuse!=='HOLD_ALL_SIX_INDIVIDUAL_REVIEWS')
    errors.push('GLOBAL_MEDIA_POLICY_GATE_REMOVED');
  if(/<\s*(?:img|picture|iframe|video)\b/i.test(apollo))
    errors.push('UNREVIEWED_EMBEDDED_MEDIA');
  if(!/none of the six linked photographs is cleared for commercial republication \(0\/6\)/i.test(apollo) ||
     !/individual photograph reuse assessments remain incomplete \(0\/6\)/i.test(apollo))
    errors.push('VISIBLE_RIGHTS_DISCLOSURE_MISSING');
  return {schema:'fv.apollo.media-audit.v1',status:errors.length?'FAIL':'PASS_SOURCE_CUSTODY_ONLY',
    errors,record_count:CANONICAL.length,official_metadata_verified_count:5,
    secondary_only_metadata_count:1,commercially_cleared_count:0,
    image_binaries_embedded:false,release_status:'STAGING_HOLD',
    commercial_offer_status:'NO_VERIFIED_PAID_APOLLO_SKU'};
}
module.exports={auditMediaLedger,CANONICAL};
if(require.main===module){
 const fs=require('node:fs'),path=require('node:path');
 const dir=__dirname, report=auditMediaLedger(
   JSON.parse(fs.readFileSync(path.join(dir,'r130_nasa_media_custody.json'),'utf8')),
   fs.readFileSync(path.join(dir,'landing-preview.html'),'utf8'));
 process.stdout.write(JSON.stringify(report,null,2)+'\n');
 process.exitCode=report.errors.length?2:0; // source custody only; never production/revenue acceptance
}
