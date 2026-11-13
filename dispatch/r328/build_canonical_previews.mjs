function esc(s){return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;")}

function inline(s){
 let a=esc(s);
 a=a.replace(/\[([^\]]+)\]\((https:\/\/[^)\s]+)\)/g,(_,label,url)=>{
   if(!/^https:\/\/finalvestige\.com\//.test(url)) throw Error("External live URL not approved: "+url);
   return `<a href="${esc(url)}" style="color:#80632e;text-decoration:underline">${label}</a>`;
 });
 return a.replace(/\*\*([^*]+)\*\*/g,"<strong>$1</strong>").replace(/\*([^*]+)\*/g,"<em>$1</em>");
}

function getBody(markdown){const blocks=markdown.split(/\n---\s*\n/);if(blocks.length<3)throw Error("Expected two original dividers");return blocks[1].trim()}

function buildIssue(markdown, entry){
 const body=getBody(markdown);
 if(!markdown.includes(entry.subject)||!markdown.includes(entry.preheader))throw Error("Subject/preheader differ from original");
 const blocks=body.split(/\n\s*\n/).map(p=>{
  let lines=p.trim().split(/\n/);
  if(lines.every(v=>/^\s*[-*]\s+/.test(v)))return `<ul style="margin:0 0 22px;padding-left:24px">${lines.map(v=>`<li style="margin:0 0 8px">${inline(v.replace(/^\s*[-*]\s+/,""))}</li>`).join("")}</ul>`;
  const isCTA=/^(?:\*\*(Read|Open|See|Visit|Examine)\b)/i.test(p);
  return `<p style="font:16px/1.65 Arial,Helvetica,sans-serif;color:#28312d;margin:0 0 20px;${isCTA?"font-weight:600;":""}">${lines.map(inline).join("<br>")}</p>`;
 });
 const commercial=entry.kind==="commercial-review-pending";
 if(commercial&&!body.includes("Commercial disclosure:"))throw Error("Missing original disclosure");
 const safety=`<p style="font:700 12px/1.5 Arial;color:#7f390f;margin:0 0 12px">REVIEW ONLY — DO NOT SEND OR COPY INTO WORDPRESS</p>`;
 const footer=`<div style="margin-top:30px;padding-top:18px;border-top:1px solid #c6bda9;font:12px/1.5 Arial;color:#53524b"><strong>UNVERIFIED COMPLIANCE FOOTER — RELEASE BLOCKED</strong><br>Publisher physical mailing address: [[VALID_POSTAL_ADDRESS_REQUIRED]]<br>Jetpack unsubscribe mechanism: [[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]<br>Rendered source, opt-out behavior and original final send approval remain unverified.</div>`;
 const html=`<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(entry.subject)} — UNSENT Review</title></head><body style="margin:0;background:#e9e7e1"><div style="background:#f7e4ca;padding:13px;text-align:center;font:bold 13px Arial;color:#713d13">FINAL VESTIGE — UNSENT OFFLINE REVIEW / NOT JETPACK RENDERING</div><div style="display:none;max-height:0;overflow:hidden;opacity:0;mso-hide:all">${esc(entry.preheader)}</div><table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="border-collapse:collapse"><tr><td align="center" style="padding:24px 12px"><table role="presentation" width="600" border="0" cellpadding="0" cellspacing="0" style="width:100%;max-width:600px;background:#fff;border-collapse:collapse"><tr><td style="padding:30px 24px;overflow-wrap:anywhere;word-break:normal">${safety}<p style="font:bold 12px/1.5 Arial;letter-spacing:1.5px;color:#876b40">FINAL VESTIGE STUDIOS · THE DISPATCH</p><h1 style="font:normal 32px/1.2 Georgia,serif;color:#17221c;margin:10px 0 22px">${esc(entry.subject)}</h1>${blocks.join("\n")}${footer}</td></tr></table></td></tr></table></body></html>`;
 const txt=`UNSENT OFFLINE REVIEW — NOT AN EMAIL OR JETPACK EXPORT\nFinal Vestige Studios / The Dispatch\nSubject: ${entry.subject}\nProposed preheader (delivery NOT verified): ${entry.preheader}\nEdition: ${entry.number} | ${entry.kind}\n\n${body.replace(/\*\*([^*]+)\*\*/g,"$1").replace(/\*([^*]+)\*/g,"$1").replace(/\[([^\]]+)\]\((https:\/\/[^)]+)\)/g,"$1 ($2)")}\n\n---\nRELEASE-BLOCKING COMPLIANCE PLACEHOLDERS\nPublisher physical mailing address: [[VALID_POSTAL_ADDRESS_REQUIRED]]\nJetpack unsubscribe mechanism: [[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]\nNEVER SEND — need native inbox evidence, audience consent, founder approval.${commercial?"\nMERCHANT RIGHTS / GUIDE LINK NOT AUTHORIZED.":""}\n`;
 return {html,txt};
}

export {buildIssue,getBody};
