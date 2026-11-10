'use strict';
/**
 * Read-only exact-source audit safeguards. No network activity, image downloads,
 * WordPress calls, post writes or production side effects.
 *
 * Native: node qa/media-recovery/validate_akron_219_coverage_194_20261110.cjs
 */
const fs = require('node:fs');
const path = require('node:path');

const inventoryPath = path.join(__dirname,'offsite_upstream_288_20261109.json');
const auditPath = path.join(__dirname,'akron_219_six_navy_20261110.json');
const priorPath = path.join(__dirname,'coverage_188_exact_pr1703_20261110.json');
const ledgerPath = path.join(__dirname,'coverage_194_exact_pr1703_20261110.json');
const bad = (errors,msg)=>{errors.push(msg);};

function auditErrors(audit,frozen) {
  const errors=[];
  if(audit?.schema !== 'fv-media-akron-219-six-v1') bad(errors,'schema');
  if(!Array.isArray(audit?.rows)||audit.rows.length!==6) return ['audit_exact_six'];
  if(!Array.isArray(frozen?.rows)||frozen.rows.length!==288) return ['frozen_count'];
  const index=new Map(frozen.rows.map(row=>[row.slot,row]));
  const seen=new Set();
  for(let i=0;i<6;i++){
    const row=audit.rows[i], slot='219:'+i, canonical=index.get(slot);
    if(row?.slot!==slot||seen.has(row.slot))bad(errors,'position:'+slot);
    seen.add(row.slot);
    if(!canonical||row.stored_url!==canonical.stored_url||row.post_url!==canonical.post_url)bad(errors,'literal_src:'+slot);
    if(row.source_kind!=='wikimedia_special_redirect_1280'||row.post_id!==219)bad(errors,'source_kind:'+slot);
    const v=row.retrieval;
    if(v?.method!=='web.open published literal URL'||v?.result!=='TOOL_INACCESSIBLE'||v?.confirmation_of_broken!==false||v?.tool_wrapper_status!==null||v?.actual_origin_http_status!==null||v?.visitor_browser_http_status!==null||v?.visitor_decoded_dimensions!==null||v?.visitor_transferred_bytes!==null)bad(errors,'fabricated_or_missing_visitor_result:'+slot);
    const c=row.candidate;
    if(!c||typeof c.primary_catalog_url!=='string'||!c.primary_catalog_url.startsWith('https://')||typeof c.commons_catalog_url!=='string'||!c.commons_catalog_url.startsWith('https://commons.wikimedia.org/wiki/File:'))bad(errors,'catalog:'+slot);
    const [w,h]=c?.archive_pixel_dimensions||[],[outW,outH]=c?.conditional_960px_dimensions||[];
    if(!Number.isInteger(w)||!Number.isInteger(h)||w<=0||h<=0||outW!==Math.min(w,960)||outH!==Math.round(h*outW/w)||outW>960||outW>w||outH>h)bad(errors,'resize:'+slot);
    if(c?.exact_binary_and_crop_match_verified!==false||c?.reuse_rights_cleared!==false||!c?.rights_review||!c?.creator_credit||!c?.scene||!c?.proposed_alt)bad(errors,'rights_or_identity:'+slot);
    if(!row.release||Object.values(row.release).some(v=>v!==false)||row.retrieval.confirmation_of_broken!==false)bad(errors,'release_hold:'+slot);
  }
  const army=audit.rows[2];
  if(army?.candidate?.accession!=='NH 98039'||!army.candidate.creator_credit.includes('Army Air Corps')||!army.candidate.rights_review.includes('CONFLICT'))bad(errors,'army_air_corps_catalog_conflict');
  if(audit.rows[3]?.candidate?.conditional_960px_dimensions?.[0]!==740||audit.rows[4]?.candidate?.conditional_960px_dimensions?.[0]!==740||audit.rows[5]?.candidate?.conditional_960px_dimensions?.[0]!==590)bad(errors,'do_not_upscale_narrow_sources');
  return errors;
}

function ledgerErrors(ledger,prior,audit){
  const errors=[];
  if(ledger?.schema!=='fv-media-exact-coverage-194-v1')bad(errors,'ledger_schema');
  if(!Array.isArray(ledger?.rows)||ledger.rows.length!==288||!Array.isArray(prior?.rows)||prior.rows.length!==288)return ['ledger_frozen_count'];
  if(ledger.counts?.researched_unique!==194||ledger.counts?.unresearched!==94||ledger.counts?.total_external!==288||ledger.counts?.total_evidence_records!==199)bad(errors,'ledger_counts');
  if(ledger.counts?.guest_browser_confirmed_broken!==0||ledger.counts?.guest_browser_confirmed_loaded!==0||ledger.counts?.reported_42_broken_browser_confirmed!==false||ledger.counts?.wire_reduction_76_percent_measured!==false)bad(errors,'invented_guest_outcomes');
  const slots=new Set(),newRows=new Map(ledger.rows.map(z=>[z.slot,z])),auditSlots=new Set(audit.rows.map(z=>z.slot));
  if(newRows.size!==288)bad(errors,'unique_slots');
  for(const prev of prior.rows){
    const next=newRows.get(prev.slot);
    if(!next){bad(errors,'lost_slot:'+prev.slot);continue}
    if(auditSlots.has(prev.slot)){
      const rec=audit.rows.find(z=>z.slot===prev.slot);
      if(prev.evidence.length||next.evidence?.length!==1||!Array.isArray(next.candidate_sources)||next.candidate_sources.length!==1)bad(errors,'candidate_evidence:'+prev.slot);
      if(next.stored_url!==rec.stored_url||next.evidence?.[0]?.retriever_only_observation!=='TOOL_INACCESSIBLE'||next.candidate_sources?.[0]?.conditional_960px?.join(',')!==rec.candidate.conditional_960px_dimensions.join(','))bad(errors,'candidate_binding:'+prev.slot);
      if(next.evidence?.[0]?.blob_sha!==ledger.batch_sources?.at(-1)?.blob_sha)bad(errors,'evidence_blob_pin:'+prev.slot);
      for(const field of ['guest_http_status','guest_current_src','guest_decoded_px','guest_wire_bytes','guest_broken'])if(next[field]!==null)bad(errors,'fabricated_guest:'+prev.slot+':'+field);
      for(const field of ['rights_cleared','exact_pixel_match_verified','download_authorized','cache_authorized','wordpress_media_upload_authorized','post_rewrite_authorized'])if(next[field]!==false)bad(errors,'released:'+prev.slot+':'+field);
    } else if(JSON.stringify(prev)!==JSON.stringify(next))bad(errors,'unrelated_row_mutation:'+prev.slot);
  }
  if(ledger.rows.filter(z=>z.evidence?.length>0).length!==194||ledger.rows.filter(z=>z.evidence?.length===0).length!==94)bad(errors,'actual_count');
  if(ledger.batch_sources?.at(-1)?.file!=='qa/media-recovery/akron_219_six_navy_20261110.json'||ledger.batch_sources?.at(-1)?.source_records!==6)bad(errors,'batch_provenance');
  return errors;
}

module.exports={auditErrors,ledgerErrors};
if(require.main===module){
 const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
 const errors=[...auditErrors(read(auditPath),read(inventoryPath)),...ledgerErrors(read(ledgerPath),read(priorPath),read(auditPath))];
 if(errors.length){console.error(errors.join('\n'));process.exitCode=1;}
 else console.log('PASS: six archived Akron sources, 194/288 evidence-bound positions, all releases HOLD');
}
