// R289 — deliberately offline. No HTTP, sending, subscriber reads, analytics or merchant activation.
function decodeForAudit(raw){
 let v=String(raw).replace(/[\u200b-\u200f\u2060\ufeff]/g,"");
 for(let i=0;i<3;i++){
  v=v.replace(/&#(x[0-9a-f]{1,6}|\d{1,7});?/gi,(all,n)=>{const code=n[0].toLowerCase()==="x"?parseInt(n.slice(1),16):parseInt(n,10);return code>0&&code<=0x10ffff?String.fromCodePoint(code):all;}).replace(/&(?:period|dot);/gi,".").replace(/&amp;/gi,"&");
  try{v=decodeURIComponent(v)}catch{}
 }
 return v.toLowerCase().replace(/\s*\.\s*/g,".");
}
function findMerchantDomains(raw){
 const norm=decodeForAudit(raw);
 const res=[];
 for(const host of ["zen12.com","hypnosislive.com","inspire3.com"]){if(norm.includes(host))res.push(host)}
 return res;
}
function classifyPreview(raw){
 const merchants=findMerchantDomains(raw), placeholders=(raw.match(/\[\[[A-Z][A-Z0-9_]*\]\]/g)||[]);
 return {merchant_domains:merchants,requires_release_hold:merchants.length>0||placeholders.length>0||!/REVIEW ONLY — DO NOT EMAIL OR PUBLISH/.test(raw),placeholder_count:placeholders.length, has_editorial_source:/https:\/\/www\.nccih\.nih\.gov\/health\//i.test(raw)};
}
function stripSellerSources(txt){
 let edits=0;
 const out=txt.split("\n").map(line=>{
   if(line.startsWith("- ")&&findMerchantDomains(line).length){
    edits++;
    return line.replace(/https?:\/\/[^\s)]+/g,"[URL RESERVED IN NON-SENDING SOURCE LEDGER]");
   }
   return line;
 }).join("\n");
 return {out,edits};
}
export {decodeForAudit,findMerchantDomains,classifyPreview,stripSellerSources};
if(process.argv[1]&&import.meta.url.endsWith(process.argv[1].replaceAll('\\','/'))){
  const fs=await import('node:fs');
  const root=new URL('.',import.meta.url);
  for(const n of ['03','05']){
    const orig=fs.readFileSync(new URL('../r287/issue-'+n+'.txt',root),'utf8');
    const safe=fs.readFileSync(new URL('issue-'+n+'.safe-review.txt',root),'utf8');
    const report={issue:n,original_commercial_source_urls:findMerchantDomains(orig),review_specimen_merchant_links:findMerchantDomains(safe),release:classifyPreview(safe).requires_release_hold?'HOLD_UNSENT':'ERROR_UNEXPECTED_READY'};
    console.log(JSON.stringify(report));
    if(report.review_specimen_merchant_links.length||report.release!=='HOLD_UNSENT')process.exitCode=1;
  }
}
