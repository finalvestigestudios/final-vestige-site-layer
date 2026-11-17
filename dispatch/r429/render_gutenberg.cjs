"use strict";
// R429 read-only deterministic WordPress Gutenberg serializer for ORIGINAL PR #175 ONLY.
// This module never accesses WordPress or calls a network API. Release always remains blocked.
function escapeHtml(s){return s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;")}
function mdInline(s){
  let t=escapeHtml(s);
  t=t.replace(/\[([^\]]+)\]\((https:\/\/finalvestige\.com\/[^)\s]+)\)/g,(_all,name,url)=>`<a href="${url}">${name}</a>`);
  t=t.replace(/\*\*([^*]+)\*\*/g,"<strong>$1</strong>").replace(/\*([^*]+)\*/g,"<em>$1</em>");
  return t;
}
function buildIssue(markdown,entry){
  const sub=markdown.match(/^\*\*Subject:\*\*\s*(.+)$/m)?.[1]||"";
  const pre=markdown.match(/^\*\*Preheader:\*\*\s*(.+)$/m)?.[1]||"";
  const type=markdown.match(/^\*\*Content type:\*\*\s*(.+)$/m)?.[1]||"";
  if(sub!==entry.subject||pre!==entry.preheader||type!==entry.kind)throw Error("Canonical metadata mismatch #"+entry.number);
  const pieces=markdown.split(/\n---\n/);
  if(pieces.length!==3)throw Error("Need exactly two source separators #"+entry.number);
  const content=pieces[1].trim();
  const paragraphs=content.split(/\n{2,}/).map(s=>s.trim()).filter(Boolean);
  const blocks=[];
  for(const p of paragraphs){
    if(p.startsWith("- ")){
      const items=p.split("\n").filter(Boolean);
      if(!items.every(s=>s.startsWith("- ")))throw Error("List mixed syntax");
      blocks.push(`<!-- wp:list --><ul class="wp-block-list">${items.map(s=>`<li>${mdInline(s.slice(2))}</li>`).join("")}</ul><!-- /wp:list -->`);
    }else{
      if(p.includes("\n"))throw Error("Unexpected hard break in paragraph");
      blocks.push(`<!-- wp:paragraph --><p>${mdInline(p)}</p><!-- /wp:paragraph -->`);
    }
  }
  const expected=entry.editorial_cta;
  const actualLinks=[...blocks.join("\n").matchAll(/href="([^"]+)"/g)].map(x=>x[1]);
  const commercial=entry.kind!=="editorial";
  if(commercial&&(!content.includes("[[APPROVED_")||actualLinks.some(u=>!u.startsWith("https://finalvestige.com/"))))throw Error("commercial blocked guide required");
  if(!commercial&&!actualLinks.includes(expected))throw Error("primary CTA lost");
  const reserved= "This is an UNSENT source-control transport specimen, NOT an authorized WordPress post. Do not copy to a live post or use Send test email without founder approval.";
  const top=`<!-- wp:paragraph --><p><strong>EDITORIAL HOLD — DO NOT PUBLISH OR EMAIL.</strong> ${escapeHtml(reserved)}</p><!-- /wp:paragraph -->`;
  const footer=`<!-- wp:paragraph --><p><strong>PRE-SEND BLOCKER (unverified):</strong> Sender Final Vestige Studios. Physical mailing address: <code>[[VALID_POSTAL_ADDRESS_REQUIRED]]</code>. Jetpack unsubscribe: <code>[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]</code>. Native Jetpack preview, received-message compliance and consent not attested.</p><!-- /wp:paragraph -->`;
  const html=`${top}\n${blocks.join("\n")}\n${footer}\n`;
  if(/<(script|iframe|img|form|video|style|link|input)\b/i.test(html))throw Error("Forbidden active element");
  if(/https?:\/\/(?!finalvestige\.com\/)/.test(html))throw Error("External URL in specimen");
  return {issue_number:entry.number,subject:sub,preheader:pre,kind:type,html,paragraphs:paragraphs.length,hrefs:actualLinks,
    status:"SOURCE_SPECIMEN_HOLD_NOT_WORDPRESS_DRAFT",proposed_post_status:"draft",send_subscription:false,
    preheader_jetpack_email_header_verified:false,requires_manual_jetpack_preview:true,requires_founder_release:true};
}
module.exports={escapeHtml,mdInline,buildIssue};
if(require.main===module){const fs=require("node:fs"),path=require("node:path");const p=path.join(__dirname,"..","campaign-2026-mind");const master=JSON.parse(fs.readFileSync(path.join(p,"manifest.json"),"utf8"));const slugs=["01-the-mind-is-not-a-camera","02-before-hypnosis-had-a-name","03-the-twelve-minute-question","04-the-hatch-and-the-spark","05-before-you-press-play","06-the-evidence-log"];for(let i=0;i<slugs.length;i++){const md=fs.readFileSync(path.join(p,"issues",slugs[i]+".md"),"utf8"),expected=fs.readFileSync(path.join(__dirname,"issue_0"+(i+1)+"_wp_blocks.html"),"utf8");const rendered=buildIssue(md,master.issues[i]).html;if(rendered!==expected)throw Error("RENDER DRIFT issue "+(i+1));}console.log("PASS 6/6 deterministic Gutenberg source-parity checks; HOLD_UNSENT");}
