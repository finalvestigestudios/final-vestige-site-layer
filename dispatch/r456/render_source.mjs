// Pure, review-only preview compiler. No networking, writes, recipient access or send actions.
// Exact same render() function executed in V8 on all six canonical master manuscript bodies.
export const render=function make(entry,markdown){
const must=(b,message)=>{if(!b)throw Error(message)};
const subject=(markdown.match(/^\*\*Subject:\*\*\s*(.+)$/m)||[])[1],preheader=(markdown.match(/^\*\*Preheader:\*\*\s*(.+)$/m)||[])[1],type=(markdown.match(/^\*\*Content type:\*\*\s*(.+)$/m)||[])[1];
must(subject===entry.subject&&preheader===entry.preheader&&type===entry.kind,"header mismatch");
must(entry.publish_state==="hold"&&entry.merchant_affiliate_url===null&&markdown.includes("UNSENT DRAFT"),"release altered");
const sections=markdown.split(/\n---\n/);must(sections.length===3,"manuscript has ambiguous internal/external boundary");
let body=sections[1].trim(),com=type==="commercial-review-pending";
must(body.length>400,"body too short");
must(body.includes("**Commercial disclosure:**")===com,"missing disclosure");
if(com)must(body.includes("[[APPROVED_"),"commercial warmup not blocked");
body=body.replace(/\[\[APPROVED_[A-Z0-9_]+_REQUIRED\]\]/g,"[GUIDE UNAVAILABLE — NO ACTIVE LINK]");
must(!body.includes("[[")&&!/https?:\/\/(zen12|hypnosislive|inspire3)\.com/i.test(body),"unsafe marker or merchant");
const links=[...body.matchAll(/\]\((https?:\/\/[^)\s]+)\)/g)].map(x=>x[1]);must(links.every(x=>x.startsWith("https://finalvestige.com/")),"non first-party link");
const esc=x=>String(x).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
const inline=x=>esc(x).replace(/\[([^\]]+)\]\((https:\/\/finalvestige\.com\/[^)\s]+)\)/g,'<a href="$2" style="color:#dfc08b;text-decoration:underline" rel="noopener">$1</a>').replace(/\*\*([^*]+)\*\*/g,"<strong>$1</strong>").replace(/\*([^*]+)\*/g,"<em>$1</em>");
const paragraphs=body.split(/\n\s*\n/).filter(Boolean).map(p=>{p=p.trim();if(p.startsWith("- "))return '<ul style="padding-left:24px;margin:0 0 19px">'+p.split("\n").map(s=>"<li>"+inline(s.replace(/^- /,""))+"</li>").join("")+"</ul>";return `<p style="font:16px/1.68 Arial,Helvetica,sans-serif;color:${p.startsWith("**Commercial disclosure:**")?"#f4d1a5":"#e5ded3"};margin:0 0 20px">${inline(p.replace(/\n/g," "))}</p>`}).join("\n");
const banner="OFFLINE REVIEW ONLY — UNSENT — NOT A JETPACK PREVIEW";
const html=`<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(banner)} | ${esc(subject)}</title></head><body style="margin:0;padding:0;background:#101312;color:#e5ded3;font-family:Arial,Helvetica,sans-serif"><table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="width:100%;background:#101312"><tr><td align="center" style="padding:22px 12px"><table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="max-width:620px;width:100%"><tr><td style="padding:14px 20px;background:#543329;color:#fff1e6;font:bold 13px/1.5 Arial,Helvetica,sans-serif">${esc(banner)}</td></tr><tr><td style="padding:29px 22px 16px;border:1px solid #424941"><p style="font:12px Arial,Helvetica,sans-serif;color:#d1b182;letter-spacing:1px">FINAL VESTIGE STUDIOS · THE DISPATCH · ISSUE ${String(entry.number).padStart(2,"0")}</p><h1 style="font:normal 30px/1.2 Georgia,'Times New Roman',serif;color:#f6efdf;margin:0 0 12px">${esc(subject)}</h1><p style="font:15px/1.6 Arial,Helvetica,sans-serif;color:#bcbab0;margin:0 0 25px">${esc(preheader)}</p>${paragraphs}<p style="padding-top:15px;border-top:1px solid #424941;font:12px/1.6 Arial,Helvetica,sans-serif;color:#f0b9b6">Review-only artifact. Final Vestige publisher mailing address, genuine Jetpack unsubscribe, recipient confirmation/welcome receipt, native email rendering and final founder release approval have NOT been verified. DO NOT SEND.</p></td></tr></table></td></tr></table></body></html>`;
const text=`${banner}\n\nTHE DISPATCH | ISSUE ${String(entry.number).padStart(2,"0")}\nSubject: ${subject}\nPreheader: ${preheader}\n\n${body.replace(/\[([^\]]+)\]\((https:\/\/finalvestige\.com\/[^)\s]+)\)/g,"$1 ($2)").replace(/\*\*/g,"").replace(/^\*([^*]+)\*$/gm,"$1")}\n\nREVIEW ONLY: FV mailing address, real unsubscribe rendering, consent/welcome receipt, and founder approval remain unverified. DO NOT SEND.\n`;
must(!html.includes("[[")&&!text.includes("[[")&&!html.includes("Pre-send compliance block")&&!text.includes("Pre-send compliance block"),"review-only note leaked");
must(!/<script|<img|@import|https:\/\/(?:zen12|hypnosislive|inspire3)\.com/i.test(html),"unsafe remote asset");
return {html,text,subject,preheader,type,links};
};
