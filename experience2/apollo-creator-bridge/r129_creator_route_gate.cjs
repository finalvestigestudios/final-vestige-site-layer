'use strict';
/** Apollo R129 source-only route, privacy and commercial preflight. No network. */
const ALLOWED_EXTERNAL = Object.freeze([
  "https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/",
  "https://sma.nasa.gov/sma-disciplines/accllp/apollo-1",
  "https://www.nasa.gov/apollo-1-resources/",
  "https://www.nasa.gov/image-detail/apollo-1-crew-honored/",
  "https://www.nasa.gov/image-detail/amf-s67-15717/",
  "https://www.nasa.gov/image-detail/amf-s66-58038/",
  "https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/",
  "https://www.nasa.gov/image-detail/amf-s67-21294/",
  "https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/",
  "https://www.nasa.gov/nasa-brand-center/",
  "https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/"
]);
const ALLOWED=new Set(ALLOWED_EXTERNAL);
function attr(tag,name) {
  const pairs=[...tag.matchAll(/([^\s=/>]+)\s*=\s*(?:"([^"]*)"|'([^']*)')/g)];
  const pair=pairs.find(m=>m[1].toLowerCase()===name.toLowerCase());
  return pair?(pair[2]===undefined?pair[3]:pair[2]):null;
}
function auditRoute(html) {
  const errors=[];
  if(typeof html!=='string' || !html.startsWith('<!doctype html>'))
    return {schema:'fv.apollo.route-gate.v1',status:'FAIL',errors:['NONCANONICAL_DOCUMENT']};
  const links=[...html.matchAll(/<a\b[^>]*>/gi)].map(m=>m[0]);
  const ids=new Set([...html.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]));
  let nasaCount=0,externalCount=0;
  for(let i=0;i<links.length;i++) {
    const tag=links[i],href=attr(tag,'href');
    if([...tag.matchAll(/\bhref\s*=/gi)].length!==1 ||
       !href || (!/^#[A-Za-z0-9_-]+$/.test(href) && !ALLOWED.has(href))) {
      errors.push('UNREVIEWED_LINK_'+i); continue;
    }
    if(href.startsWith('#') && !ids.has(href.slice(1)))
      errors.push('BROKEN_FRAGMENT_'+i);
    if(!href.startsWith('#')) {
      externalCount++;
      if(href.startsWith('https://www.nasa.gov/') || href.startsWith('https://sma.nasa.gov/')) {
        nasaCount++;
        const rel=(attr(tag,'rel')||'').toLowerCase().split(/\s+/);
        if(!rel.includes('noopener')||!rel.includes('noreferrer'))
          errors.push('NASA_REFERRER_PROTECTION_'+i);
      }
    }
    if(/\s+on[a-z]+\s*=/i.test(tag))
      errors.push('INLINE_LINK_HANDLER_'+i);
    if(attr(tag,'target')==='_blank' &&
       !(attr(tag,'rel')||'').toLowerCase().split(/\s+/).includes('noopener'))
      errors.push('UNSAFE_NEW_WINDOW_'+i);
  }
  const primary=links.filter(tag=>/\bdata-fv-primary-cta(?:\s|>)/.test(tag));
  if(primary.length!==1 || attr(primary[0]||'','href')!=='#classroom-preview' ||
     /\bhidden(?:\s|>)/.test(primary[0]||'')) errors.push('PRIMARY_CLASSROOM_ACTION_INVALID');
  if(!/<section\b[^>]*\bid="classroom-preview"[^>]*>/.test(html) ||
     /<section\b[^>]*\bid="classroom-preview"[^>]*\bhidden(?:\s|>)/.test(html) ||
     !/Free source-analysis exercise/.test(html))
    errors.push('NO_JS_CLASSROOM_DESTINATION_INVALID');
  if(!/<article\b[^>]*\bid="student-print-preview"/.test(html) ||
     !/<ol\b[^>]*data-fv-student-prompts/.test(html) ||
     !/<section\b[^>]*data-fv-student-photo-index/.test(html))
    errors.push('WORKSHEET_INTEGRITY_UNPROVEN');
  if(/<(?:form|input|iframe|img|picture|video|audio|object|embed|canvas)\b/i.test(html))
    errors.push('UNREVIEWED_MEDIA_OR_DATA_COLLECTION');
  if(/<script\b[^>]*\bsrc\s*=|<link\b[^>]*\bhref\s*=\s*["']https?:|@import\b|url\s*\(\s*["']?https?:/i.test(html))
    errors.push('UNREVIEWED_EXTERNAL_ASSET');
  if(/\b(?:fetch\s*\(|XMLHttpRequest\b|sendBeacon\s*\(|localStorage\b|sessionStorage\b|document\.cookie\b|gtag\s*\(|dataLayer\b)/i.test(html))
    errors.push('UNREVIEWED_TRACKING_OR_STORAGE');
  if(/<meta\b[^>]*http-equiv\s*=\s*["']refresh|<base\b/i.test(html))
    errors.push('UNREVIEWED_REDIRECT_OR_BASE');
  if(/\s+on(?:click|load|error|submit|input|focus|mouseover)\s*=/i.test(html))
    errors.push('INLINE_HANDLER_REQUIRES_REVIEW');
  if(!/<meta name="robots" content="noindex,nofollow">/.test(html))
    errors.push('STAGING_INDEX_BLOCK_REMOVED');
  if(nasaCount!==22) errors.push('NASA_REFERENCE_CARDINALITY_CHANGED');
  if(externalCount!==23) errors.push('EXTERNAL_DESTINATION_CARDINALITY_CHANGED');
  return {schema:'fv.apollo.route-gate.v1',status:errors.length?'FAIL':'PASS',errors,
    link_count:links.length,nasa_link_count:nasaCount,external_link_count:externalCount,
    primary_cta_count:primary.length,source_status:'SOURCE_ONLY_NOT_BROWSER_ACCEPTANCE',
    commerce_status:'NO_VERIFIED_PAID_OFFER_OR_MERCHANT',
    attribution_status:'UNOBSERVABLE_NOT_A_SALE'};
}
module.exports={auditRoute,ALLOWED_EXTERNAL,attr};
if(require.main===module){const fs=require('node:fs'),path=require('node:path');const report=auditRoute(fs.readFileSync(path.join(__dirname,'landing-preview.html'),'utf8'));process.stdout.write(JSON.stringify(report,null,2)+'\n');process.exitCode=report.status==='PASS'?0:2;}
