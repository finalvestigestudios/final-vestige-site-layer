'use strict';
/**
 * FINAL VESTIGE — homepage preservation gate (read-only, never writes WordPress).
 * This does NOT compose a release. It rejects proposed homepage *raw Gutenberg block*
 * candidates that drop/alter all 72 Margins, the original Jetpack block, or Focus CTA,
 * or that create duplicate primary headings when paired with the seven-chapter flagship.
 * Never feed a private WP database export: use the PUBLIC homepage block content only.
 */
const fs = require('node:fs');
const crypto = require('node:crypto');
const path = require('node:path');
const MARGIN = /<span\b(?=[^>]*class="fv-margin-strip__item")(?=[^>]*style="--i:(\d+)")[^>]*>[\s\S]*?<\/span>/g;
const SUBSCRIPTIONS = /<!-- wp:jetpack\/subscriptions\b[^>]*\/-->/g;
const FOCUS_LINK = /<a\b[^>]*\bhref=["'](?:https:\/\/finalvestige\.com)?\/focus\/?["'][^>]*>/gi;
const CHAPTERS = ['fv-hf-title','fv-hf-chronicle','fv-hf-evidence','fv-hf-inquiry','fv-hf-method-title','fv-hf-observer','fv-hf-mind-title'];
const CASES = ['apollo','franklin','malbone'];
const SHA = s => crypto.createHash('sha256').update(s,'utf8').digest('hex');
function fail(message) { throw new Error('FV HOMEPAGE PRESERVATION HOLD: ' + message); }
function attest(legacy, candidate, opts={}) {
  if (typeof legacy !== 'string' || typeof candidate !== 'string' || !legacy || !candidate) fail('missing public Gutenberg raw content');
  const originalDigest=SHA(legacy);
  if (opts.expectedLegacySha && opts.expectedLegacySha !== originalDigest) fail('legacy source digest changed; re-review actual homepage ID 6');
  if (!opts.expectedLegacySha && opts.requireSourceDigest) fail('missing independently checked page-6 baseline digest');
  const items=[...legacy.matchAll(MARGIN)].map(m=>({index:Number(m[1]),markup:m[0]}));
  if(items.length !== 72 || new Set(items.map(x=>x.index)).size !== 72 ||
      items.some(x=>x.index<0 || x.index>71)) fail('original 72 Margins indexes not intact');
  const candItems=[...candidate.matchAll(MARGIN)].map(m=>({index:Number(m[1]),markup:m[0]}));
  if(candItems.length !== 72 || new Set(candItems.map(x=>x.index)).size !== 72) fail('candidate changed number/index uniqueness of 72 Margins');
  for(const item of items){
    const matches=candItems.filter(m=>m.index===item.index && m.markup===item.markup);
    if(matches.length!==1) fail('original Margins record '+item.index+' dropped or altered');
  }
  const oldSub=[...legacy.matchAll(SUBSCRIPTIONS)].map(m=>m[0]);
  const newSub=[...candidate.matchAll(SUBSCRIPTIONS)].map(m=>m[0]);
  if(oldSub.length !== 1 || newSub.length!==1 || oldSub[0]!==newSub[0]) fail('original Jetpack subscription block lost/changed/duplicated');
  const oldFocus=[...legacy.matchAll(FOCUS_LINK)].map(m=>m[0]);
  const candidateFocus=[...candidate.matchAll(FOCUS_LINK)].map(m=>m[0]);
  if(oldFocus.length < 2 || oldFocus.some(link=>!candidateFocus.includes(link))) fail('original Focus links were removed or altered');
  const h1=[...candidate.matchAll(/<h1\b[^>]*>/gi)];
  if(h1.length!==1) fail('candidate has '+h1.length+' H1 elements (expected 1, before theme chrome)');
  for(const id of CHAPTERS){
    const p=new RegExp('\\bid=["\']'+id+'["\']','g');
    if([...candidate.matchAll(p)].length!==1) fail('missing/duplicate flagship chapter anchor '+id);
  }
  for(const name of CASES){
    const p=new RegExp('\\bdata-fv-case=["\']'+name+'["\']','g');
    if([...candidate.matchAll(p)].length!==1) fail('missing/duplicate evidence case '+name);
  }
  if(/DESIGN STUDY\s*[·•]\s*NOT LIVE/.test(candidate) || /fv-hf__studio-controls/.test(candidate)) fail('development control UI leaked');
  if(/<script\b[^>]*src=["']https?:\/\//i.test(candidate)) fail('remote executable script in migration candidate');
  return {status:'PRESERVATION_SOURCE_GATE_PASSED_NOT_WORDPRESS_RELEASE',legacy_sha256:originalDigest,candidate_sha256:SHA(candidate),legacy_bytes:Buffer.byteLength(legacy),candidate_bytes:Buffer.byteLength(candidate),margins:items.length,jetpack_original_blocks:oldSub.length,original_focus_links:oldFocus.length,chapter_anchors:CHAPTERS.length,evidence_cases:CASES.length,h1:h1.length,limitations:['Does not certify WordPress renderer, Jetpack fulfillment, image bytes/rights, visual UX, axe WCAG, Lighthouse/CWV, or theme heading landmarks','Requires separate WordPress/Assembler staging and human review before release']};
}
if (require.main === module) {
  const args=process.argv.slice(2),opt=n=>args[args.indexOf(n)+1];
  for(const name of ['--legacy','--candidate','--expected-legacy-sha256','--receipt'])if(!args.includes(name)||!opt(name))fail('CLI requires '+name);
  const sha=opt('--expected-legacy-sha256');if(!/^[a-f0-9]{64}$/.test(sha))fail('malformed legacy SHA-256');
  const legacy=fs.readFileSync(path.resolve(opt('--legacy')),'utf8');
  const candidate=fs.readFileSync(path.resolve(opt('--candidate')),'utf8');
  const report=attest(legacy,candidate,{expectedLegacySha:sha,requireSourceDigest:true});
  if(fs.existsSync(opt('--receipt')))fail('refusing overwrite of an existing immutable receipt');
  fs.writeFileSync(opt('--receipt'),JSON.stringify(report,null,2)+'\n',{flag:'wx'});
  process.stdout.write(JSON.stringify({status:report.status,margins:report.margins,jetpack:report.jetpack_original_blocks,h1:report.h1})+'\n');
}
module.exports={attest,SHA};
