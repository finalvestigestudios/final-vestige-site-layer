// Final Vestige Dispatch · Native WordPress excerpt handoff guard (READ ONLY)
// Node 20+, no dependencies, no network, no WordPress/mail API, no subscriber access.
// This checks source consistency. It intentionally NEVER declares a message SEND-READY.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const here = path.dirname(fileURLToPath(import.meta.url));
const campaign = path.resolve(here, '..');
function load(p) { return JSON.parse(fs.readFileSync(path.join(campaign,p),'utf8')); }
const manifest = load('manifest.json');
const proposed = load('delivery/wordpress_excerpt_copy.json');
const contract = load('native-email-contract/NATIVE_DELIVERY_PARITY.json');
const issues = manifest.issues;
const errs = [];
if (manifest.status !== 'DRAFT_UNSENT_NO_SCHEDULING') errs.push('campaign is not draft-unsent');
if (issues.length !== 6 || proposed.entries.length !== 6) errs.push('campaign count not six');
if (issues.filter(x=>x.kind==='editorial').length !== 4) errs.push('editorial allocation not four');
if (issues.filter(x=>x.kind==='commercial-review-pending').length !== 2) errs.push('offer allocation not two');
if (contract.status !== 'HOLD_UNSENT') errs.push('contract release state not HOLD');
for (let n=1;n<=6;n++){
  const item=issues.find(x=>x.number===n), ex=proposed.entries.find(x=>x.number===n);
  if (!item || !ex) {errs.push('issue/excerpt missing '+n);continue;}
  const name=String(n).padStart(2,'0')+'-'+item.slug+'.md';
  const body=fs.readFileSync(path.join(campaign,'issues',name),'utf8');
  if (!body.includes('**Subject:** '+item.subject) || ex.subject !== item.subject) errs.push('subject drift '+n);
  if (!body.includes('**Preheader:** '+item.preheader)) errs.push('planned preheader drift '+n);
  if (!body.includes('[[VALID_POSTAL_ADDRESS_REQUIRED]]')) errs.push('postal HOLD removed '+n);
  if (!body.includes('[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]')) errs.push('unsubscribe HOLD removed '+n);
  if (item.publish_state !== 'hold' || item.merchant_affiliate_url !== null) errs.push('merchant/publish activated '+n);
  if (typeof ex.excerpt !== 'string' || ex.excerpt.trim().split(/\s+/).length<35) errs.push('insufficient custom excerpt '+n);
  if (/https?:\/\/(?:www\.)?(zen12\.com|hypnosislive\.com)/i.test(ex.excerpt)) errs.push('merchant URL in excerpt '+n);
  if ([3,5].includes(n)){
    if(item.kind!=='commercial-review-pending' || !item.editorial_cta.startsWith('[[APPROVED_')) errs.push('offer route activated '+n);
    if(!/(affiliate|commission|qualifying link)/i.test(ex.excerpt)) errs.push('no commercial disclosure in email excerpt '+n);
  } else {
    if(item.kind!=='editorial' || !item.editorial_cta.startsWith('https://finalvestige.com/')) errs.push('editorial CTA invalid '+n);
  }
}
// R11 PARITY PROVENANCE. The review board is not authoritative unless every
// row matches the exact canonical manifest and unsent proposed excerpt.
// A green source check still NEVER authorizes sending or implies rendered email.
if (new Set(issues.map(x=>x.number)).size !== 6) errs.push('duplicate manifest issue numbers');
if (new Set(proposed.entries.map(x=>x.number)).size !== 6) errs.push('duplicate proposed excerpt numbers');
if (new Set((contract.rows ?? []).map(x=>x.number)).size !== 6) errs.push('duplicate parity review row numbers');
for (let n=1;n<=6;n++){
  const item=issues.find(x=>x.number===n);
  const ex=proposed.entries.find(x=>x.number===n);
  const row=(contract.rows ?? []).find(x=>x.number===n);
  if (!item || !ex || !row){errs.push('parity row or source missing '+n);continue;}
  if (row.subject!==item.subject) errs.push('parity subject drift '+n);
  if (row.preheader_plan!==item.preheader) errs.push('parity preheader drift '+n);
  if (row.kind!==item.kind) errs.push('parity allocation drift '+n);
  if (row.proposed_custom_excerpt_NOT_APPLIED!==ex.excerpt) errs.push('parity excerpt drift '+n);
  const expectedCta=item.editorial_cta; // Exact current manifest parity, including DISABLED merchant-guide placeholders.
  if (row.original_editorial_cta!==expectedCta) errs.push('parity CTA drift '+n);
  if (row.actual_native_preheader!=='UNVERIFIED' ||
      row.actual_received_mime!=='NOT_RECEIVED' ||
      row.actual_read_more!=='NOT_VERIFIED' ||
      row.actual_postal_footer!=='NOT_VERIFIED' ||
      row.actual_unsubscribe!=='NOT_VERIFIED' ||
      row.release!=='HOLD_UNSENT')
    errs.push('unearned native rendering claim '+n);
}
if (contract.all_issues_send_approval!==false ||
    contract.all_issues_received_email_verified!==false ||
    contract.site?.welcome_delivered!=='UNVERIFIED' ||
    contract.commercial_offer_permissions!=='UNKNOWN')
  errs.push('unearned site, commercial, or founder authorization');
const site=contract.site ?? {};
if (site.email_content_format !== 'excerpt' || site.email_new_posts_by_default !== false) errs.push('source snapshot no longer reflects audited newsletter settings');
const counts=contract.subscribers ?? {};
if (counts.unique_permissioned_deliverable !== null) errs.push('recipient count inferred without private reconciliation');
if (contract.rows?.length !== 6 || !contract.rows.every(x=>x.release==='HOLD_UNSENT' && x.actual_received_mime==='NOT_RECEIVED')) errs.push('false receipt/release claim');
const report={source_gate:errs.length?'INVALID':'SOURCE_ONLY_PASS',release:'HOLD_UNSENT',issues_checked:6,editorial:4,commercial:2,errors:errs,
    site_snapshot_requires_recheck:true,real_WordPress_MIME_received:false,founder_send_authorized:false};
console.log(JSON.stringify(report,null,2));
if(errs.length)process.exitCode=1;
