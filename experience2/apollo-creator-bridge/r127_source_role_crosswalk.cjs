#!/usr/bin/env node
'use strict';
/**
 * R127 — read-only provenance crosswalk for the *actual* Apollo staging HTML
 * and the independent Research Desk PR #158 template. No fetch, network,
 * CMS, visitor storage or data collection. Release is FAIL-CLOSED.
 *
 * node experience2/apollo-creator-bridge/r127_source_role_crosswalk.cjs \
 *   --research-ref feature/experience-2-source-ledger-pilot-20261030 \
 *   --output /tmp/apollo-source-crosswalk.json
 * If PR #158 is not fetched locally, pass --research-file /path/ledger.html.
 */
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const child = require('node:child_process');
const {auditRoute}=require('./r129_creator_route_gate.cjs');
const ROOT = __dirname;
const NASA_BOARD = 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/';
const EXPECTED = Object.freeze([
  ['01','https://www.nasa.gov/image-detail/apollo-1-crew-honored/','PORTRAIT_CATALOG_PROVISIONAL'],
  ['02','https://www.nasa.gov/image-detail/amf-s67-15717/','PHOTO_IS_NOT_OXYGEN_MEASUREMENT'],
  ['03','https://www.nasa.gov/image-detail/amf-s66-58038/','PHOTO_IS_NOT_INSTRUMENT_TRACE'],
  ['04','https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/','RETROSPECTIVE_2017_HATCH'],
  ['05','https://www.nasa.gov/image-detail/amf-s67-21294/','PHOTO_CANNOT_PROVE_IGNITION'],
  ['06','https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/','RETROSPECTIVE_2017_REDESIGN']
]);
const sha256 = text => crypto.createHash('sha256').update(text,'utf8').digest('hex');
// Git blob pinned to independently maintained Research Desk draft PR #158.
const TRUSTED_RESEARCH_BLOB = '403d128c57b9bc82dac7c619651689070edef86c';
const gitBlobSha = text => {
  const bytes=Buffer.from(text,'utf8');
  return crypto.createHash('sha1').update(Buffer.from('blob '+bytes.length+'\0')).update(bytes).digest('hex');
};
const anchorAttr=(tag,name)=> {
  const m=tag.match(new RegExp('(?:^|\\s)'+name+'\\s*=\\s*"([^"]*)"','i'));
  return m ? m[1] : null;
};
const imageAnchors=block=>[...block.matchAll(/<a\b[^>]*>/gi)]
  .map(m=>({href:anchorAttr(m[0],'href'),rel:anchorAttr(m[0],'rel')}))
  .filter(a=>a.href && a.href.startsWith('https://www.nasa.gov/image-detail/'));
const referrerSafe=link=>link && ['noreferrer','noopener'].every(token=>
  (link.rel||'').toLowerCase().split(/\s+/).includes(token));
const visibleText = section => section.replace(/<[^>]*>/g,' ').replace(/&nbsp;/g,' ').replace(/\s+/g,' ').trim();
const extract = (html, tag, idprefix) => {
  const matches = [...html.matchAll(new RegExp('<'+tag+'\\b[^>]*\\bid="'+idprefix+'(0[1-6])"[^>]*>[\\s\\S]*?<\\/'+tag+'>','g'))];
  return new Map(matches.map(m=>[m[1],m[0]]));
};
const photoUrl = block => (block.match(/href="(https:\/\/www\.nasa\.gov\/image-detail\/[^"]+)"/i)||[])[1]||null;
function audit(apollo, research) {
  const photos=extract(apollo,'tr','photo-source-');
  const desk=extract(research,'article','fv-ex2-ledger-apollo1-record-');
  const errors=[], unresolved=[], records=[];
  const creatorRoute=auditRoute(apollo);
  errors.push(...creatorRoute.errors.map(code=>'CREATOR_ROUTE_'+code));
  const actualResearchBlob=gitBlobSha(research);
  const snapshotVerified=actualResearchBlob===TRUSTED_RESEARCH_BLOB;
  if(photos.size!==6)errors.push('APOLLO_PHOTO_RECORD_COUNT');
  if(desk.size!==6)errors.push('DESK_RECORD_COUNT');
  const duplicate = (html, pattern) => [...html.matchAll(pattern)].length!==6;
  if(duplicate(apollo,/<tr\b[^>]*\bid="photo-source-0[1-6]"/g))
    errors.push('APOLLO_SOURCE_IDS_NOT_EXACTLY_SIX');
  if(duplicate(research,/<article\b[^>]*\bid="fv-ex2-ledger-apollo1-record-0[1-6]"/g))
    errors.push('DESK_SOURCE_IDS_NOT_EXACTLY_SIX');
  for(const [id,expectedUrl,reason] of EXPECTED) {
    const p=photos.get(id)||'', d=desk.get(id)||'';
    const aurl=photoUrl(p), durl=photoUrl(d);
    const kind=(d.match(/fv-ex2-ledger__kind">([^<]+)/)||[])[1]||'MISSING';
    const text=visibleText(d);
    if(!p || !d)errors.push('MISSING_RECORD_'+id);
    if(aurl!==expectedUrl || durl!==expectedUrl)errors.push('NASA_URL_MISMATCH_'+id);
    if(!p.includes('data-fv-source-kind="photograph"'))
      errors.push('APOLLO_ROLE_NOT_MACHINE_READABLE_'+id);
    // Privacy tokens must belong to the precise photo anchor, not a sibling.
    const photoLinks=imageAnchors(p), deskLinks=imageAnchors(d);
    if(photoLinks.length!==1 || deskLinks.length!==1)
      errors.push('PHOTO_SOURCE_LINK_CARDINALITY_'+id);
    if(!referrerSafe(photoLinks[0]))
      errors.push('APOLLO_PHOTO_REFERRER_LEAK_'+id);
    if(id==='01' && !/\bprovisional\b|\bunconfirmed\b/i.test(text))
      unresolved.push('R158_'+reason);
    if(id==='02' && kind==='PRIMARY REVIEW BOARD RECORD' &&
       !/photograph.{0,80}(?:not|visual)|visual context/i.test(text))
      unresolved.push('R158_'+reason);
    if(id==='03' && kind==='INSTRUMENT CHRONOLOGY' &&
       !/photograph.{0,80}(?:not|visual)|visual context/i.test(text))
      unresolved.push('R158_'+reason);
    if((id==='04'||id==='06') && !/\bretrospective\b|\b2017\b/i.test(text))
      unresolved.push('R158_'+reason);
    if(id==='05' && /ignition|arc/i.test(text) &&
       !/photograph.{0,80}(?:not|visual)|visual context/i.test(text))
      unresolved.push('R158_'+reason);
    records.push({id,apollo_photo_url:aurl,desk_photo_url:durl,
      nasa_url_match:aurl===expectedUrl&&durl===expectedUrl,
      desk_label:kind,technical_source:NASA_BOARD,
      image_role:'VISUAL_CONTEXT_ONLY',media_reuse:'INDIVIDUAL_REVIEW_REQUIRED',
      issue_code:reason});
  }
  // The printable worksheet has its own six links: preserve URL custody,
  // uniqueness and referrer protection independently of the table.
  const handout=[...apollo.matchAll(/<li\b[^>]*data-fv-student-photo="(0[1-6])"[^>]*>[\s\S]*?<\/li>/g)];
  if(handout.length!==6 || new Set(handout.map(m=>m[1])).size!==6)
    errors.push('STUDENT_WORKSHEET_SOURCE_COUNT');
  for(const [id,url] of EXPECTED){
    const matching=handout.filter(m=>m[1]===id);
    const links=matching.length===1?imageAnchors(matching[0][0]):[];
    if(links.length!==1 || links[0].href!==url)
      errors.push('STUDENT_WORKSHEET_SOURCE_MISMATCH_'+id);
    if(!referrerSafe(links[0]))
      errors.push('STUDENT_WORKSHEET_SOURCE_PRIVACY_'+id);
  }
  const documentedDates=['1966-10-18','1967-01-03','1967-01-28','2017-01-24'];
  const dateRows=[...apollo.matchAll(/<li\b[^>]*data-fv-photo-day="([^"]+)"[^>]*>[\s\S]*?<\/li>/g)];
  if(dateRows.length!==4 || dateRows.some((m,i)=>
    m[1]!==documentedDates[i] || !m[0].includes('<time datetime="'+m[1]+'">')))
    errors.push('PHOTO_CHRONOLOGY_DATE_DRIFT');
  if(!/<aside\b[^>]*data-fv-photo-month-uncertain(?:\s|>)/.test(apollo) ||
     !/<time datetime="1967-01">January 1967<\/time>/.test(apollo) ||
     !/provisional/i.test(apollo.split('<aside data-fv-photo-month-uncertain')[1]||''))
    errors.push('PROVISIONAL_PORTRAIT_DATE_MISSING');
  if(!apollo.includes('data-fv-source-role-warning') ||
     !/Apollo 204 Review Board/.test(apollo))
    errors.push('VISIBLE_NOJS_EVIDENCE_BOUNDARY_MISSING');
  if(/<img\b|<picture\b|<iframe\b/i.test(apollo))
    errors.push('UNREVIEWED_EMBEDDED_MEDIA');
  // Rights decisions and independent historical review remain external gates
  // even after the editorial warnings are corrected.
  return {schema:'fv.apollo.research-desk.crosswalk.v1',
    source_sha256:{apollo:sha256(apollo),research_desk:sha256(research)},
    research_desk_snapshot:{expected_git_blob:TRUSTED_RESEARCH_BLOB,
      actual_git_blob:actualResearchBlob,
      status:snapshotVerified?'PINNED_PR158_SOURCE_VERIFIED':'UNREVIEWED_SOURCE_DRIFT'},
    source_custody:snapshotVerified?'VERIFIED_SNAPSHOT':'BLOCKED_UNREVIEWED_SOURCE',
    source: {apollo:'Apollo isolated staging',research_desk:'Independent PR #158 (read-only)'},
    creator_route:creatorRoute,
    record_count:records.length,records,integrity_errors:errors,
    editorial_flags:unresolved,photograph_rights_approved:0,
    research_desk_edited:false,
    link_integrity:errors.length?'FAIL':'PASS',
    release_status:'STAGING_HOLD',
    conversion_status:'NO_VERIFIED_MATCHING_PAID_SKU',
    claims:{qualified_sessions:'UNOBSERVABLE',merchant_paid_orders:'UNOBSERVABLE',net_revenue:'UNOBSERVABLE'}};
}
function main(argv) {
  let researchFile=null, researchRef=null, output=null;
  for(let i=0;i<argv.length;i++) {
    const arg=argv[i];
    if(arg==='--research-file')researchFile=argv[++i];
    else if(arg==='--research-ref')researchRef=argv[++i];
    else if(arg==='--output')output=argv[++i];
    else throw new Error('unknown argument '+arg);
  }
  if(Boolean(researchFile)===Boolean(researchRef))
    throw new Error('supply exactly one of --research-file or --research-ref');
  const apollo=fs.readFileSync(path.join(ROOT,'landing-preview.html'),'utf8');
  const desk=researchFile?fs.readFileSync(researchFile,'utf8'):
    child.execFileSync('git',['show',researchRef+':experience2/research-desk/templates/ledger.html'],
      {cwd:ROOT,encoding:'utf8',maxBuffer:8*1024*1024});
  const report=audit(apollo,desk);
  const json=JSON.stringify(report,null,2)+'\n';
  if(output)fs.writeFileSync(output,json,'utf8');
  else process.stdout.write(json);
  // Unknown rights and unresolved editorial scope are failures, never a green release.
  process.exitCode=report.link_integrity==='PASS' &&
    report.source_custody==='VERIFIED_SNAPSHOT' && report.editorial_flags.length===0 &&
    report.photograph_rights_approved===6 ? 0 : 2;
}
module.exports={audit,EXPECTED,photoUrl,extract,gitBlobSha,TRUSTED_RESEARCH_BLOB,imageAnchors};
if(require.main===module){try{main(process.argv.slice(2));}catch(err){
  process.stderr.write('R127_CROSSWALK_BLOCKED: '+err.message+'\n');process.exitCode=2;}}
