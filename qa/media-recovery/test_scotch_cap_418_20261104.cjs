'use strict';
const clone=(x)=>JSON.parse(JSON.stringify(x));
function runCases(validate, audit, frozen) {
  const labels=[];
  function accepts(label) {let r=validate(audit,frozen);if(!r.ok) throw Error(label+': '+r.errors.join('; '));labels.push(label);}
  function rejects(label, mutate) {let a=clone(audit), f=clone(frozen);mutate(a,f);let r=validate(a,f);if(r.ok) throw Error('unsafe audit accepted: '+label);labels.push(label);}
  accepts('untampered six-slot audit');
  rejects('one image missing',a=>a.rows.pop());
  rejects('extra invented image',a=>a.rows.push(clone(a.rows[0])));
  rejects('swapped slot',a=>{let t=a.rows[0];a.rows[0]=a.rows[1];a.rows[1]=t;});
  rejects('altered source',a=>a.rows[0].source_url='https://elsewhere.test/foo.jpg');
  rejects('altered ALT',a=>a.rows[3].alt='A different scene');
  rejects('duplicate source',a=>a.rows[1].source_url=a.rows[0].source_url);
  rejects('altered frozen inventory source',(_a,f)=>f.images.find(x=>x.key==='418:2').source_url='https://elsewhere.test/a.jpg');
  rejects('altered frozen inventory caption',(_a,f)=>f.images.find(x=>x.key==='418:3').alt='Unverified');
  rejects('wrong frozen blob',a=>a.frozen_source.git_blob_sha='badsha');
  rejects('fake origin 200',a=>a.rows[1].probe.origin_http_status=200);
  rejects('fake browser 404',a=>a.rows[2].probe.browser_http_status=404);
  rejects('fake response MIME',a=>a.rows[4].probe.browser_mime='image/jpeg');
  rejects('fake decoded pixels',a=>a.rows[4].probe.decoded_natural_width=1000);
  rejects('fake CDP bytes',a=>a.rows[0].probe.cdp_encoded_data_bytes=300);
  rejects('invented browser session',a=>a.http_evidence.guest_browser_used=true);
  rejects('invented HTTP samples',a=>a.http_evidence.origin_get_statuses_measured=6);
  rejects('invented wire reduction',a=>a.http_evidence.actual_bytes_measured=1);
  rejects('unknown retrieval probe kind',a=>a.rows[3].probe.kind='HTTP_404');
  rejects('rehost approved without rights',a=>a.rows[2].rights_gate.rehost_authorized=true);
  rejects('WP upload approved without rights',a=>a.rows[1].rights_gate.wp_upload_authorized=true);
  rejects('image review gate cleared',a=>a.rows[1].rights_gate.requires_item_level_review=false);
  rejects('960 upscaling enabled',a=>a.rows[2].derivative.no_upscale=false);
  rejects('max width over 960',a=>a.rows[2].derivative.hard_max_width_px=1280);
  rejects('invented derivative dimensions',a=>a.rows[2].derivative.preverified_960_derivative_dimensions=[960,741]);
  rejects('preview dimensions forged',a=>a.rows[2].derivative.known_candidate_preview_dimensions=[960,741]);
  rejects('600px preview fake large',a=>{a.rows[2].archival.rendition_dims=[1200,926];a.rows[2].derivative.known_candidate_preview_dimensions=[1200,926];});
  rejects('missing museum catalog evidence',a=>a.rows[0].archival.catalog='');
  rejects('non https archival rendition',a=>a.rows[2].archival.rendition='http://example.test/a.jpg');
  rejects('invented CMS pair widths',a=>a.verification.img_tags_with_width_and_height=6);
  rejects('false CMS URL reconciliation',a=>a.verification.six_src_matches=false);
  rejects('sitewide reduction promoted to fact',a=>a.baseline.reported_reduction_unmeasured_percent=0);
  rejects('production WP changes',a=>a.production_changes.wp_writes=1);
  rejects('third party binary downloaded',a=>a.production_changes.downloaded_or_rehosted_images=1);
  rejects('unexpected paid spend',a=>a.production_changes.cost_usd=1);
  return {passed:labels.length,labels};
}
module.exports={runCases};
if (typeof require==='function' && require.main===module) {
  const fs=require('node:fs'),path=require('node:path');
  const root=__dirname;
  const audit=JSON.parse(fs.readFileSync(path.join(root,'scotch_cap_418_primary_recovery_20261104.json'),'utf8'));
  const frozen=JSON.parse(fs.readFileSync(path.join(root,'parts/01.json'),'utf8'));
  const {validate}=require('./validate_scotch_cap_418_20261104.cjs');
  const result=runCases(validate,audit,frozen);
  console.log('Scotch Cap media custody tests '+result.passed+'/'+result.passed+' PASS');
}
