"use strict";
// Standalone, dependency-free LOCAL REVIEW renderer. This is not WordPress' real outgoing MIME.
const fs = require("node:fs");
const path = require("node:path");
const root = path.resolve(__dirname, "..");
const reviewDir = path.join(root, "previews");
const issueDir = path.join(root, "issues");
const styleP = "font-family:Arial,Helvetica,sans-serif;font-size:16px;line-height:1.72;color:#D8D2C7;margin:0 0 18px;";
function escapeHtml(s) {
  return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}
function inline(md) {
  let h=escapeHtml(md);
  h=h.replace(/\[([^\]\n]+)\]\((https:\/\/[^\s)]+)\)/g, function(_,label,url) {
    return '<a href="'+url+'" style="color:#E4C58E;text-decoration:underline;">'+label+'</a>';
  });
  h=h.replace(/\*\*([^*]+)\*\*/g,"<strong>$1</strong>");
  h=h.replace(/\*([^*]+)\*/g,"<em>$1</em>");
  h=h.replace(/\[\[([A-Z0-9_]+)\]\]/g, '<strong style="color:#FFD5AB;overflow-wrap:anywhere;word-break:break-all;">[UNVERIFIED: $1]</strong>');
  return h;
}
function bodyHtml(markdown) {
  return markdown.split(/\n\s*\n/).map(x=>x.trim()).filter(Boolean).map(block=>{
    if (block.startsWith("- ")) {
      const bits=block.split("\n").filter(x=>x.startsWith("- ")).map(line=>'<li style="'+styleP+'padding-bottom:6px;">'+inline(line.slice(2))+'</li>').join("");
      return '<ul style="padding-left:24px;margin:0 0 20px;">'+bits+'</ul>';
    }
    const hold=/\[\[APPROVED_[A-Z0-9_]+\]\]/.test(block);
    const disclosure=block.startsWith("**Commercial disclosure:");
    const css=styleP + (hold?"background:#29200E;border:1px solid #78603D;padding:16px;":"") + (disclosure?"color:#F4EFE6;":"");
    return '<p style="'+css+'">'+inline(block.replace(/\n/g," "))+'</p>';
  }).join("\n");
}
function parseSource(text) {
  const chunks=text.split(/\n---\n/);
  if(chunks.length<3)throw Error("Invalid source section separation");
  const header=chunks[0], body=chunks[1].trim(), footer=chunks.slice(2).join("\n---\n");
  const extract=name=>{
    const m=header.match(new RegExp("^\\*\\*"+name+":\\*\\*\\s*(.+)$","m"));
    if(!m)throw Error("Missing "+name);
    return m[1].trim();
  };
  return {subject:extract("Subject"),preheader:extract("Preheader"),kind:extract("Content type"),body,footer};
}
function renderHtml(entry,source) {
  const d=parseSource(source),num=String(entry.number).padStart(2,"0");
  if(d.subject!==entry.subject||d.preheader!==entry.preheader)throw Error("Manifest differs from source issue "+num);
  const content=bodyHtml(d.body),preview=escapeHtml(d.preheader);
  return '<!doctype html>\n<html lang="en">\n<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>UNSENT PREVIEW — '+escapeHtml(d.subject)+'</title></head>\n'+
    '<body style="margin:0;padding:0;background:#090A0A;color:#D8D2C7;">'+
    '<span aria-hidden="true" style="display:none!important;visibility:hidden;font-size:1px;line-height:1px;color:#090A0A;max-height:0;max-width:0;opacity:0;overflow:hidden;">'+preview+'</span>'+
    '<div role="note" style="background:#4D220F;text-align:center;padding:12px;color:#FFF0D4;font-family:Arial,sans-serif;font-weight:bold;font-size:13px;">DRAFT PREVIEW — NOT A SENT EMAIL — LEGAL AND MERCHANT GATES OPEN</div>'+
    '<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background:#090A0A;border-collapse:collapse;"><tr><td align="center" style="padding:28px 14px;">'+
    '<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="max-width:640px;border-collapse:collapse;background:#101111;border:1px solid #37342F;">'+
    '<tr><td style="padding:30px 32px 16px;border-bottom:1px solid #39352F;font-family:Arial,Helvetica,sans-serif;font-weight:700;font-size:12px;letter-spacing:2px;color:#B8955E;">FINAL VESTIGE STUDIOS &nbsp; / &nbsp; THE DISPATCH '+num+'</td></tr>'+
    '<tr><td style="padding:28px 32px 0;"><h1 style="font-family:Georgia,serif;font-size:32px;line-height:1.18;font-weight:normal;color:#F4EFE6;margin:0 0 14px;">'+escapeHtml(d.subject)+'</h1><p style="font-family:Arial,sans-serif;font-size:15px;line-height:1.5;color:#AAA49A;margin:0 0 24px;">'+preview+'</p></td></tr>'+
    '<tr><td style="padding:0 32px 16px;">'+content+'</td></tr>'+
    '<tr><td style="padding:24px 32px 26px;border-top:1px solid #39352F;">'+
    '<p style="font-family:Arial,sans-serif;font-size:13px;line-height:1.6;color:#AAA49A;margin:0 0 12px;">Final Vestige Studios · Source-led research, curious minds, and reader-supported investigations.</p>'+
    '<p style="font-family:Arial,sans-serif;font-size:12px;line-height:1.5;color:#F1C49E;margin:0 0 8px;">[VALID BUSINESS POSTAL ADDRESS REQUIRED — NOT MERCHANT ADDRESS]</p>'+
    '<p style="font-family:Arial,sans-serif;font-size:12px;line-height:1.5;color:#F1C49E;margin:0;">[VERIFY REAL WORDPRESS UNSUBSCRIBE IN DELIVERED TEST EMAIL]</p>'+
    '</td></tr></table></td></tr></table></body></html>\n';
}
function renderText(entry,source){
  const d=parseSource(source),num=String(entry.number).padStart(2,"0");
  const body=d.body.replace(/\[([^\]\n]+)\]\((https:\/\/[^\s)]+)\)/g,"$1 ($2)").replace(/\*\*([^*]+)\*\*/g,"$1").replace(/\*([^*]+)\*/g,"$1");
  return "UNSENT DRAFT — DO NOT SEND\nTHE DISPATCH / ISSUE "+num+"\nSubject: "+d.subject+"\nPreheader: "+d.preheader+"\n\n"+body+"\n\n---\nFinal Vestige Studios\n[[VALID_POSTAL_ADDRESS_REQUIRED]]\n[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]\n";
}
function indexHtml(items){
  const cards=items.map(item=>'<li><div class="meta">ISSUE '+String(item.number).padStart(2,"0")+' · '+(item.kind==="commercial-review-pending"?"COMMERCIAL HOLD":"EDITORIAL HOLD")+'</div><h2>'+escapeHtml(item.subject)+'</h2><p>'+escapeHtml(item.preheader)+'</p><a href="'+item.file+'.html">Review HTML</a> <a href="'+item.file+'.txt">View plain text</a></li>').join("\n");
  return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Final Vestige / The Dispatch — unsent previews</title><style>body{margin:0;background:#090A0A;color:#D8D2C7;font:17px/1.6 system-ui,Arial,sans-serif;}main{width:min(960px,calc(100% - 36px));margin:56px auto 90px}h1{font:normal clamp(36px,6vw,58px)/1.12 Georgia,serif;color:#F4EFE6}li{list-style:none;border-top:1px solid #4A4238;padding:24px 0}ul{padding:0}h2{font:normal 28px/1.25 Georgia,serif;color:#F4EFE6;margin:8px 0}p{margin:8px 0 16px}.meta{font-size:12px;letter-spacing:.1em;color:#D0AB71}a{color:#E4C58E;margin-right:18px}a:focus-visible{outline:3px solid #fff;outline-offset:4px}.hold{padding:20px;background:#3A2317;border:1px solid #AA7C5D;color:#FFDEC5}</style></head><body><main><p class="meta">FINAL VESTIGE STUDIOS / THE DISPATCH</p><h1>Six dispatches. None sent.</h1><p class="hold"><strong>REVIEW-ONLY.</strong> These standalone HTML snapshots are not real WordPress/Jetpack test emails. Every issue is held until legal footer, opt-out, audience, affiliate approval and founder sign-off. Product CTAs are deliberately non-functional.</p><ul>'+cards+'</ul><p>Source: <a href="../README.md">Campaign README</a> · Owner: Dispatch Campaign Studio</p></main></body></html>\n';
}
function build(check) {
  const manifest=JSON.parse(fs.readFileSync(path.join(root,"manifest.json"),"utf8")),items=[];
  const out=[];
  for(const item of manifest.issues){
    const slug=String(item.number).padStart(2,"0")+"-"+item.slug;
    const source=fs.readFileSync(path.join(issueDir,slug+".md"),"utf8");
    const html=renderHtml(item,source),txt=renderText(item,source);
    if(!html.includes("NOT A SENT EMAIL")||html.includes('href="[[APPROVED_'))throw Error("Safety gate failed for "+slug);
    out.push([slug+".html",html],[slug+".txt",txt]);items.push({number:item.number,kind:item.kind,subject:item.subject,preheader:item.preheader,file:slug});
  }
  out.push(["index.html",indexHtml(items)]);
  if(!check)fs.mkdirSync(reviewDir,{recursive:true});
  for(const pair of out){
    const file=path.join(reviewDir,pair[0]);
    if(check){if(fs.readFileSync(file,"utf8")!==pair[1])throw Error("Generated preview drift: "+pair[0]);}
    else fs.writeFileSync(file,pair[1],"utf8");
  }
  return out;
}
if(require.main===module){build(process.argv.includes("--check"));console.log("Dispatch preview assets verified/generated: 13 files");}
module.exports={build,parseSource,renderHtml,renderText,indexHtml};
