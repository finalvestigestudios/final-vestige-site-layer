'use strict';
// Offline fail-closed source-custody verifier for the 288-position report.
function verifyHostRisk(ledger,report) {
 const mistakes=[];
 function fail(code){mistakes.push(code)}
 if(ledger?.schema!=="fv-media-coverage-288-exact-v1"||ledger?.rows?.length!==288||ledger.counts?.total_external!==288)fail("invalid_source_contract");
 if(report?.schema!=="fv-media-upstream-clusters-v1")fail("invalid_report_schema");
 if(report?.counts?.external_positions!==288||report.counts?.upstream_hosts!==80||report.counts?.web_retriever_wrapper_4xx_5xx_slots!==27)fail("bad_census_counts");
 const index=new Map();
 for(const r of ledger?.rows||[]){
  if(index.has(r.slot))fail("duplicate_source_slot:"+r.slot);
  index.set(r.slot,r);
 }
 const groups=new Map();
 for(const g of report?.upstream_hosts||[]){
  if(groups.has(g.upstream_host))fail("duplicate_origin_host");
  groups.set(g.upstream_host,g);
  const actual=ledger.rows.filter(r=>r.origin_host===g.upstream_host);
  if(g.source_positions!==actual.length||g.affected_posts!==new Set(actual.map(r=>r.post_id)).size)fail("incorrect_host_count:"+g.upstream_host);
  if(JSON.stringify([...g.source_slots].sort())!==JSON.stringify(actual.map(r=>r.slot).sort()))fail("wrong_host_slot_set:"+g.upstream_host);
  if(g.origin_status!==null||g.guest_confirmed_broken!==null||g.rights_cleared!==false)fail("host_overclaimed_status_rights:"+g.upstream_host);
  if(!actual.some(r=>r.stored_url===g.sample_exact_source_url))fail("host_sample_does_not_exist:"+g.upstream_host);
 }
 if(groups.size!==80||[...groups.values()].reduce((n,g)=>n+g.source_positions,0)!==288)fail("host_distribution_not_288");
 if(report?.counts?.top_three_host_positions!==151||[...groups.values()].sort((a,b)=>b.source_positions-a.source_positions).slice(0,3).reduce((n,g)=>n+g.source_positions,0)!==151)fail("top_three_not_151");
 const actualAlerts=ledger.rows.filter(r=>r.evidence.some(e=>Number.isInteger(e.retriever_wrapper_code)&&e.retriever_wrapper_code>=400));
 const alerts=report?.web_retriever_warning_rows||[];
 if(actualAlerts.length!==27||alerts.length!==27)fail("wrong_wrapper_warning_count");
 const alertSet=new Set();
 for(const w of alerts){
  const s=index.get(w.slot);
  if(!s||alertSet.has(w.slot))fail("duplicate_or_fabricated_warning_slot");
  alertSet.add(w.slot);
  if(!s||s.stored_url!==w.original_exact_url||s.origin_host!==w.origin_host)fail("warning_not_bound_to_original:"+w.slot);
  const expected=[...new Set((s?.evidence||[]).map(e=>e.retriever_wrapper_code).filter(n=>Number.isInteger(n)&&n>=400))];
  if(JSON.stringify(expected)!==JSON.stringify(w.web_retriever_codes_not_origin_status))fail("wrong_retriever_observation:"+w.slot);
  if(w.guest_status!==null||w.visitor_broken!==null||w.guest_wire_bytes!==null||w.release!=="HOLD")fail("warning_promoted_to_guest_or_release:"+w.slot);
  for(const c of w.catalog_candidates||[])if(c.item_cleared!==false||c.visual_identity_verified!==false)fail("candidate_unapproved:"+w.slot);
 }
 for(const r of actualAlerts)if(!alertSet.has(r.slot))fail("missing_wrapper_slot:"+r.slot);
 const queue=["285:5","285:2","287:5","418:1","418:2","407:1"];
 if((report.p0_queue||[]).length!==6)fail("wrong_P0_size");
 for(let i=0;i<6;i++){
  const r=index.get(queue[i]), q=(report.p0_queue||[])[i];
  if(!q||q.slot!==queue[i]||q.original_url!==r?.stored_url||q.guest_http_status!==null||q.guest_broken!==null||q.staging_approval!==false)fail("P0_unsafe_or_wrong:"+queue[i]);
  for(const c of q?.candidates||[])if(c.cleared!==false)fail("P0_candidate_unapproved:"+queue[i]);
 }
 const proxy=[...index.values()].filter(r=>r.stored_url.startsWith("https://i0.wp.com/")&&r.origin_host!=="i0.wp.com");
 if(proxy.length!==2||(report.jetpack_delivery_vs_upstream||[]).length!==2||!proxy.every(r=>report.jetpack_delivery_vs_upstream.some(p=>p.slot===r.slot&&p.stored_url===r.stored_url&&p.upstream_host===r.origin_host)))fail("proxy_source_identity_wrong");
 if(report.counts?.reported_42_guest_confirmed!==false||report.counts?.confirmed_guest_broken!==0||report.counts?.proposed_76_percent_wire_saving_measured!==false||report.counts?.oversize_stored_bytes!==47096779)fail("unverified_performance_or_failure_claim");
 if(!Object.values(report.release||{}).every(v=>v===false))fail("unexpected_authorized_change");
 return {ok:mistakes.length===0,errors:mistakes};
}
module.exports={verifyHostRisk};
if(require.main===module){const fs=require('node:fs'),path=require('node:path');const dir=__dirname;const ledger=JSON.parse(fs.readFileSync(path.join(dir,'coverage_288_exact_pr1703_20261110.json'),'utf8'));const report=JSON.parse(fs.readFileSync(path.join(dir,'upstream_host_risk_288_20261111.json'),'utf8'));const result=verifyHostRisk(ledger,report);if(!result.ok){console.error(result.errors.join('\n'));process.exitCode=1;}else console.log('PASS: 288 positions, 80 hosts, 27 retriever-only warnings, P0 release holds');}
