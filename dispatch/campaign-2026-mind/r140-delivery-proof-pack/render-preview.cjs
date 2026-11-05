"use strict";
// Local-only generator, no network, no WordPress, no email sending.
function escapeHtml(x){return String(x).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;")}

function inline(x){
 let links=[];
 const s=String(x).replace(/\[([^\]]+)\]\((https:\/\/[^)\s]+)\)/g,(whole,label,url)=>{
   if(!/^https:\/\/[a-z0-9.-]+(?:[/?#:]|$)/i.test(url)||url.includes('"')||url.includes("'")||/https:\/\/[^/?#]+@/.test(url))throw Error("Unsafe reference URL");
   const idx=links.length;links.push('<a style="color:#164467;text-decoration:underline" href="'+escapeHtml(url)+'">'+escapeHtml(label)+'</a>');return "@@LINK_"+idx+"@@";
 });
 return escapeHtml(s).replace(/\*\*([^*]+)\*\*/g,"<strong>$1</strong>").replace(/(?<!\*)\*([^*]+)\*(?!\*)/g,"<em>$1</em>").replace(/@@LINK_(\d+)@@/g,(_,n)=>links[Number(n)]);
}

function htmlBlocks(s){
 let out=[],p=[],list=false;
 function close(){if(p.length){out.push('<p style="margin:0 0 18px;line-height:1.65">'+inline(p.join(" "))+'</p>');p=[];}}
 function endList(){if(list){out.push("</ul>");list=false;}}
 for(const raw of String(s).split(/\r?\n/)){const line=raw.trim();
  if(!line){close();endList();continue}
  if(line==="---"){close();endList();out.push('<hr style="border:0;border-top:1px solid #bcb6aa;margin:20px 0">');continue}
  if(/^#{1,5} /.test(line)){close();endList();out.push('<h2 style="font:normal 22px/1.3 Georgia,serif">'+inline(line.replace(/^#+ /,""))+'</h2>');continue}
  if(line.startsWith("- ")){close();if(!list){list=true;out.push('<ul style="margin:0 0 20px;padding-left:24px">')}out.push('<li style="padding-bottom:8px;line-height:1.65">'+inline(line.slice(2))+'</li>');continue}
  endList();p.push(line);
 }
 close();endList();return out.join("\n");
}

function parseEdition(md){
 function field(s){let m=md.match(new RegExp("^\\*\\*"+s+":\\*\\*\\s*(.+)$","m"));if(!m)throw Error("Missing "+s);return m[1].trim()}
 const sub=field("Subject"),pre=field("Preheader"),kind=field("Content type");
 const idx=md.search(/^---[ \t]*$/m);if(idx<0)throw Error("No divider");
 return {sub,pre,kind,body:md.slice(idx).replace(/^---[^\n]*\n/,"").trim()};
}

function toPlain(s){return String(s).replace(/\[([^\]]+)\]\((https:\/\/[^)\s]+)\)/g,"$1 ($2)").replace(/\*\*/g,"").replace(/(?<!\*)\*([^*]+)\*(?!\*)/g,"$1").replace(/^#+\s*/gm,"").trim()}

function makeEmail(md,entry){
 const q=parseEdition(md);
 if(q.sub!==entry.subject||q.pre!==entry.preheader||q.kind!==entry.kind)throw Error("Source/manifest mismatch "+entry.number);
 if(entry.publish_state!=="hold"||entry.merchant_affiliate_url!==null)throw Error("Authorization violated");
 for(const marker of ["[[VALID_POSTAL_ADDRESS_REQUIRED]]","[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]"])if(!md.includes(marker))throw Error("Missing legal HOLD marker");
 if(entry.kind==="commercial-review-pending"&&(!md.includes("Commercial disclosure:")||!md.includes("[[APPROVED_")))throw Error("Commercial disclaimer/guide HOLD missing");
 if(entry.kind==="editorial"&&(!entry.editorial_cta.startsWith("https://finalvestige.com/")||!md.includes(entry.editorial_cta)))throw Error("Editorial CTA not verified");
 const html='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+escapeHtml(q.sub)+' — UNSENT</title></head><body style="margin:0;background:#f4efe6;color:#171b1c;font:16px/1.6 Arial,Helvetica,sans-serif"><div style="display:none;max-height:0;overflow:hidden;opacity:0">'+escapeHtml(q.pre)+'</div><table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0"><tr><td align="center" style="padding:18px 10px"><table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="max-width:640px;background:#fff"><tr><td style="padding:25px 23px"><p style="font-size:12px;letter-spacing:.1em;color:#6c4a2a">FINAL VESTIGE STUDIOS · THE DISPATCH</p><p role="note" style="border:2px solid #925131;background:#fff2e1;padding:13px;color:#653722;font-size:14px"><strong>OFFLINE REVIEW ONLY — UNSENT</strong><br>Not a genuine Jetpack preview or delivered email. All release and legal gates remain closed.</p><h1 style="font:normal 30px/1.2 Georgia,serif;color:#182326">'+escapeHtml(q.sub)+'</h1><p style="color:#56636a;font-size:15px">'+escapeHtml(q.pre)+'</p>'+htmlBlocks(q.body)+'<p style="border-top:1px solid #c8beb1;padding-top:17px;font-size:12px">Review artifact only: valid FV mailing address, unsubscribe operation, merchant permission and actual subscriber consent remain unverified.</p></td></tr></table></td></tr></table></body></html>';
 const text='FINAL VESTIGE STUDIOS — THE DISPATCH\nOFFLINE REVIEW ONLY · UNSENT · NO SENDING APPROVAL\n\nSubject: '+q.sub+'\nPreheader: '+q.pre+'\n\n'+toPlain(q.body)+'\n\nOffline artifact only; actual WordPress delivery/footer and address not verified.\n';
 return {html,text,edition:q};
}

function modelExcerpt(md,entry){const x=parseEdition(md),body=toPlain(x.body).replace(/\s+/g," ");return "# MODELS ONLY — NOT A REAL JETPACK EMAIL\n\nIssue "+entry.number+": "+x.sub+"\n\nJetpack/WordPress documentation presents an approximately 55-word excerpt in one context and approximately 350-character excerpt in another. Actual Final Vestige rendering has NOT been observed. A native Read More button may lead to the NEW newsletter POST, not the original manuscript CTA; no such future post exists.\n\n## Approximately 55 words\n"+body.split(" ").slice(0,55).join(" ")+"\n\nRead More → [[FUTURE_WORDPRESS_POST_NOT_CREATED]]\n\n## Approximately 350 characters\n"+body.slice(0,350)+"\n\nRead More → [[FUTURE_WORDPRESS_POST_NOT_CREATED]]\n\nIntended destination: "+entry.editorial_cta+"\n\nHOLD_UNSENT, no verified subscriber or affiliate activation.\n"}

function validateEmail(html,plain,entry){
 for(let v of [html,plain]){if(!v.includes("VALID_POSTAL_ADDRESS_REQUIRED")||!v.includes("JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED"))throw Error("Lost footer placeholder");}
 if(!html.includes('lang="en"')||!html.includes('<table role="presentation"')||!html.includes("OFFLINE REVIEW ONLY"))throw Error("Email semantically unsafe");
 if(/<script\b|<form\b|<iframe\b|<img\b|utm_campaign=|utm_source=|href=["'][^"']*APPROVED_/i.test(html))throw Error("Unsafe tracking, code or link");
 if((html.match(/<a\b/g)||[]).length===0)throw Error("No cited source URLs");
 if(entry.kind==="commercial-review-pending" && (![html,plain].every(v=>v.includes("Commercial disclosure")&&v.includes("APPROVED_"))))throw Error("Commercial hold lost");
 return true;
}

function buildAll(manifest,sources){
 if(manifest.status!=="DRAFT_UNSENT_NO_SCHEDULING"||manifest.issues.length!==6||manifest.issues.filter(x=>x.kind==="editorial").length!==4||manifest.issues.filter(x=>x.kind==="commercial-review-pending").length!==2)throw Error("4:2 original campaign invariant failed");
 let files={},audit=[];
 for(const entry of manifest.issues){const md=sources[entry.number];if(!md)throw Error("Missing issue source");const e=makeEmail(md,entry),p="issue-"+String(entry.number).padStart(2,"0");validateEmail(e.html,e.text,entry);files[p+"-full-offline.html"]=e.html;files[p+"-full-offline.txt"]=e.text;files[p+"-excerpt-models.md"]=modelExcerpt(md,entry);audit.push({edition:entry.number,kind:entry.kind,source_and_subject_match:true,html_review_only:true,plaintext_review_only:true,excerpt_simulated_only:true,affiliate_activated:false,real_jetpack_preview:false,release_approved:false});}
 files["asset-audit.json"]=JSON.stringify({state:"HOLD_UNSENT",mail_sent:false,source_campaign:manifest.id,independently_settled_orders:null,realized_net_revenue:null,recipient_eligibility:null,editions:audit},null,2)+"\n";return files;
}
module.exports={parseEdition,makeEmail,modelExcerpt,validateEmail,buildAll};
if(require.main===module){const fs=require("node:fs"),path=require("node:path");const here=__dirname,canonical=path.resolve(here,"..");const man=JSON.parse(fs.readFileSync(path.join(canonical,"manifest.json"),"utf8")),sources={};for(const i of man.issues){sources[i.number]=fs.readFileSync(path.join(canonical,"issues",String(i.number).padStart(2,"0")+"-"+i.slug+".md"),"utf8");}const files=buildAll(man,sources);for(const [name,v] of Object.entries(files)){fs.writeFileSync(path.join(here,name),v)}console.log("Generated "+Object.keys(files).length+" review-only assets; no network or email.");}
