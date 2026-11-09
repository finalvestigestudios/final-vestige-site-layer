/* R239 offline guard. Run: node dispatch/r239/test_release_guard.cjs
   This is NOT Jetpack output or an email sending program. */
'use strict';
const fs = require('node:fs');
const path = require('node:path');
function assert(x, reason) { if (!x) throw new Error(reason); }
function check(files) {
 const {md,txt,html,contract,manifest}=files;
 assert(contract.status==='HOLD_UNSENT_NOT_APPROVED','release hold');
 assert(contract.master_sha==='d57ccdba3aee8f065e143e101c2945f4f3d01647','master SHA');
 assert(contract.kind==='editorial'&&contract.proposed_edition===1,'editorial slot');
 assert(contract.master_mix.editorial===4 && contract.master_mix.commercial===2,'4:2 allocation');
 assert(manifest.status==='DRAFT_UNSENT_NO_SCHEDULING','master hold');
 assert(manifest.issues.length===6 && manifest.issues.every(x=>x.merchant_affiliate_url===null),'master unsent/no merchant URLs');
 assert(Object.values(contract.approval).every(x=>x===false),'no invented approval');
 assert(contract.merchant_affiliate_url===null && contract.net_revenue_per_1000_qualified_sessions===null,'no earnings inferred');
 for (const [label,s] of Object.entries({md,txt,html})) {
  assert(s.includes(contract.subject),'subject '+label);
  assert(s.includes(contract.preheader.replace(/&/g,'&amp;')),'preheader '+label);
  assert(s.includes(contract.cta),'verified destination '+label);
  assert(s.includes('[[VALID_POSTAL_ADDRESS_REQUIRED]]') && s.includes('[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]'),'legal placeholders '+label);
  for (const u of contract.source_links) assert(s.includes(u),'research source '+label);
  assert(!/utm_(source|medium|campaign|content)=|<script|<form|tracking-pixel|\baffiliate\s*href|\b1x1\b/i.test(s),'unexpected tracker/form '+label);
 }
 assert((md.match(/\*\*Explore the evidence:\*\*/g)||[]).length===1,'one markdown CTA');
 assert((txt.match(/EXPLORE THE EVIDENCE —/g)||[]).length===1,'one plaintext CTA');
 assert((html.match(/Explore the evidence ↗/g)||[]).length===1,'one HTML CTA');
 assert(/<html lang="en">/.test(html)&&/role="presentation"/.test(html),'HTML accessible email scaffolding');
 assert(!/<img\b|<iframe\b|<video\b|<svg\b|<style\b/i.test(html),'email no remote media/styles');
 const links=Array.from(html.matchAll(/href="([^"]+)"/g),m=>m[1]);
 assert(links.length===3 && links.every(x=>[contract.cta,...contract.source_links].includes(x)),'HTML outbound link allowlist');
 assert(md.split(/\s+/).length>=350,'substantive copy');
 assert(!/the product (has been|is) proven|guaranteed meditation results|every witness is wrong/i.test(md),'overclaim');
 return true;
}
if (require.main === module) {
 const root=__dirname; const master=path.join(root,'../campaign-2026-mind/manifest.json');
 check({md:fs.readFileSync(path.join(root,'ISSUE01_OPTIONAL_UNSENT.md'),'utf8'),txt:fs.readFileSync(path.join(root,'ISSUE01_REVIEW.txt'),'utf8'),html:fs.readFileSync(path.join(root,'ISSUE01_REVIEW.html'),'utf8'),contract:JSON.parse(fs.readFileSync(path.join(root,'RELEASE_CONTRACT.json'),'utf8')),manifest:JSON.parse(fs.readFileSync(master,'utf8'))});
 console.log('R239 offline source guard PASS — NEVER SEND');
}
module.exports={check};
