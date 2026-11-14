export function esc(s){return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");}
export function inline(s){
 let t=esc(s);
 t=t.replace(/\[([^\]]+)\]\((https:\/\/[^)\s]+)\)/g,(m,label,url)=>/^https:\/\/finalvestige\.com\/[a-z0-9/._-]*$/i.test(url)?`<a href="${url}" style="color:#6c512a;text-decoration:underline">${label}</a>`:`${label} (unverified link: ${esc(url)})`);
 t=t.replace(/\*\*([^*]+)\*\*/g,"<strong>$1</strong>").replace(/(?<!\*)\*([^*\n]+)\*(?!\*)/g,"<em>$1</em>");
 t=t.replace(/`([^`]+)`/g,"<code>$1</code>");return t;
}
export function render(body,entry){
 const isCommercial=entry.kind==="commercial-review-pending";
 let raw=body.split(/\r?\n/),parts=[],block=[];
 const flush=()=>{if(block.length){parts.push(`<p style="margin:0 0 16px;line-height:1.65">${inline(block.join(" "))}</p>`);block=[]}};
 const start=raw.findIndex(x=>x.trim()==="---");let lines=raw.slice(start+1);
 for(let s of lines){s=s.trim();if(!s){flush();continue}if(s==="---"){flush();continue}if(/^#/.test(s)){flush();parts.push(`<h2 style="font-size:17px;line-height:1.3">${inline(s.replace(/^#+\s*/,""))}</h2>`);continue}if(/^>\s?/.test(s)){flush();parts.push(`<p style="border-left:3px solid #a47a45;padding:6px 10px;color:#7a5e40">${inline(s.replace(/^>\s?/,""))}</p>`);continue} if(/^\[\[APPROVED_/.test(s)){flush();parts.push(`<p role="note" style="border:1px solid #805121;padding:10px;color:#805121">OFFER GUIDE CTA DISABLED — NOT LIVE / NOT APPROVED</p>`);continue} if(s.startsWith("**Read the Zen12 evaluation:**")||s.startsWith("**See the forthcoming independent guide:**")){flush();parts.push(`<p style="padding:12px;border:1px solid #b6a082;background:#faf5eb">${inline(s.replace(/\[\[APPROVED_[A-Z0-9_]+\]\]/g,"[INACTIVE — OFFER GUIDE AWAITING APPROVAL]"))}</p>`);continue}block.push(s);}
 flush();
 let html=`<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(entry.subject)} — HOLD preview</title></head><body style="margin:0;padding:20px 12px;background:#f3f1ed;color:#242321;font-family:Arial,Helvetica,sans-serif"><table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="border-collapse:collapse"><tr><td align="center"><table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="width:100%;max-width:600px;background:white;border:1px solid #d9d1c3;border-collapse:collapse"><tr><td style="padding:25px 24px"><p style="color:#6e614e;font-size:12px;letter-spacing:1px">FINAL VESTIGE STUDIOS / THE DISPATCH</p><p style="background:#fce8dd;border:1px solid #ad5429;color:#7b3014;padding:10px;font-size:14px"><strong>HOLD · UNSENT DRAFT · OFFLINE SIMULATION</strong><br>NOT a native Jetpack preview, subscriber email, or sending authorization.</p><h1 style="font-family:Georgia,serif;font-size:28px;line-height:1.14;color:#20201e">${esc(entry.subject)}</h1><p style="font-size:14px;color:#716759"><strong>Simulated preheader only:</strong> ${esc(entry.preheader)}</p>${parts.join("\n")}<div style="border-top:1px solid #b8b0a3;padding-top:15px;font-size:13px;color:#675e52"><p>Publisher address: <strong>NOT VERIFIED — VALID FINAL VESTIGE POSTAL ADDRESS REQUIRED</strong></p><p>Unsubscribe: <strong>NOT VERIFIED — ACTUAL JETPACK LINK / OPTOUT MUST BE TESTED</strong></p><p>Editorial/product copy is source-derived and not approved for publication or email.</p></div></td></tr></table></td></tr></table></body></html>`;
 const plain=`FINAL VESTIGE STUDIOS / THE DISPATCH\nHOLD — UNSENT DRAFT — OFFLINE SIMULATION. NOT A RECEIVED EMAIL.\nSubject: ${entry.subject}\nSimulated preheader: ${entry.preheader}\n\n${body.replace(/\[\[APPROVED_[A-Z0-9_]+\]\]/g,"[INACTIVE — OFFER GUIDE NOT LIVE / NOT APPROVED]").replace(/\*\*([^*]+)\*\*/g,"$1").replace(/\*([^*\n]+)\*/g,"$1").replace(/\[([^\]]+)\]\(([^)]+)\)/g,"$1 ($2)")}\n\nDO NOT SEND — actual publisher address and Jetpack unsubscribe are not verified.\n`;
 return {html,plain};
}
export function check(originals,manifest,proof={}){
const problems=[];
const kinds=manifest.issues.map(x=>x.kind);
if(originals.length!==6||manifest.issues.length!==6||kinds.filter(x=>x==="editorial").length!==4||kinds.filter(x=>x==="commercial-review-pending").length!==2)problems.push("Campaign 4:2 inventory mismatch");
if(manifest.status!=="DRAFT_UNSENT_NO_SCHEDULING")problems.push("Master status is not unsent");
for(let i=0;i<originals.length;i++){
const entry=manifest.issues[i],b=originals[i]?.content??"";
if(!b.includes(entry.subject)||!b.includes(entry.preheader))problems.push("Issue "+(i+1)+" metadata mismatch");
if(!b.includes("UNSENT DRAFT")||!b.includes("[[VALID_POSTAL_ADDRESS_REQUIRED]]")||!b.includes("[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]"))problems.push("Issue "+(i+1)+" no hard-stop footer/status");
if(entry.kind==="commercial-review-pending"&&(!b.includes("Commercial disclosure:")||!entry.editorial_cta.startsWith("[[APPROVED_")||entry.merchant_affiliate_url!==null))problems.push("Issue "+(i+1)+" merchant hold broken");
}
const mandatory=["publisher_postal_verified","real_jetpack_preview_verified","received_email_verified","received_email_optout_function_verified","consent_recipient_dedup_verified","welcome_fieldbook_receipt_verified","founder_final_campaign_approved"];
const merchant=["named_partner_approval_verified","email_channel_allowed_verified","issued_affiliate_url_verified","live_guide_verified","checkout_price_refund_verified","specific_claim_review_verified"];
const proofMissing=mandatory.filter(k=>proof[k]?.status!=="verified"||!proof[k]?.source_ref);
const commercialMissing=merchant.filter(k=>proof[k]?.status!=="verified"||!proof[k]?.source_ref);
return {valid_source:problems.length===0,problems,all_send_state:"HOLD_UNSENT",editorial_state:proofMissing.length?"HOLD_SHARED_DELIVERY":"HUMAN_REVIEW_CANDIDATE_ONLY",commercial_state:proofMissing.length||commercialMissing.length?"HOLD_MERCHANT":"HUMAN_REVIEW_CANDIDATE_ONLY",shared_missing:proofMissing,merchant_missing:commercialMissing,note:"Offline tool cannot validate external proof, confer sender approval, or authorize a send."};
}
