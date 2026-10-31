'use strict';
// R23 offline-only compiler. NO WordPress API calls, no email/subscriber access.
function esc(s){return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;")}

function inl(s) {
 if(/[<>]|\x00/.test(s))throw Error("Raw markup forbidden");
 const links=[];
 let t=s.replace(/\[([^\]\n]+)\]\((https:\/\/[^\s)]+)\)/g,(_,label,url)=>{
  if(!/^https:\/\/[a-z0-9.-]+(?:[:\/?#]|$)/i.test(url)||/https:\/\/[^\/]*@/.test(url)||/clickbank|affiliates\.inspire3\.com/i.test(url))throw Error("Unsafe external link");
  let token="__FV_SAFE_LINK_"+links.length+"__";links.push([token,`<a href="${esc(url)}">${esc(label)}</a>`]);return token;
 });
 if(/\[[^\]]+\]\([^)]+\)/.test(t))throw Error("Unresolved Markdown URL");
 t=esc(t).replace(/\*\*([^*\n]+)\*\*/g,"<strong>$1</strong>").replace(/(^|[^\*])\*([^*\n]+)\*(?!\*)/g,"$1<em>$2</em>");
 for(let [token,markup] of links)t=t.replace(token,markup);
 return t;
}

function bodyFrom(s){
 if(!s.includes("UNSENT DRAFT")||!s.includes("[[VALID_POSTAL_ADDRESS_REQUIRED]]")||!s.includes("[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]"))throw Error("Unsent/legal hold removed");
 let i=s.indexOf("\n---\n"),j=s.indexOf("\n---\n**Pre-send compliance block",i+5);
 if(i<0||j<0)throw Error("No editorial/legal boundary");
 return s.slice(i+5,j).trim();
}

function genBlocks(body,commercial){
 const pieces=['<!-- wp:paragraph --><p><strong>DO NOT PUBLISH OR EMAIL — DRAFT ONLY</strong></p><!-- /wp:paragraph -->'];
 for(let chunk of body.split(/\n\s*\n/)){
  chunk=chunk.trim();if(!chunk)continue;
  if(chunk.startsWith("- ")){
   let lines=chunk.split("\n");if(lines.some(x=>!x.startsWith("- ")))throw Error("Bad list");
   pieces.push('<!-- wp:list --><ul class="wp-block-list">'+lines.map(x=>'<!-- wp:list-item --><li>'+inl(x.slice(2))+'</li><!-- /wp:list-item -->').join("")+'</ul><!-- /wp:list -->');
  }else{
   if(chunk.startsWith("#")||chunk.startsWith(">"))throw Error("Unsupported Markdown");
   let tokens=[...chunk.matchAll(/\[\[([A-Z][A-Z0-9_]+)\]\]/g)];
   if(tokens.length){if(!commercial||tokens.length!==1||!chunk.startsWith("**"))throw Error("Unexpected placeholder");chunk=chunk.replace(/\[\[([A-Z][A-Z0-9_]+)\]\]/g,"GUIDE NOT LIVE — NO LINK")}
   pieces.push("<!-- wp:paragraph --><p>"+inl(chunk.replace(/\n/g," "))+"</p><!-- /wp:paragraph -->");
  }
 }
 return pieces.join("\n");
}

function adapt(m,source){
 const commercial=m.kind==="commercial-review-pending",num=m.number;
 if(((num===3)||(num===5))!==commercial)throw Error("4:2 drift");
 if(m.publish_state!=="hold"||m.merchant_affiliate_url!==null)throw Error("Activation attempt");
 if(!source.startsWith("# THE DISPATCH — ISSUE "+String(num).padStart(2,"0")))throw Error("Wrong edition");
 if(!source.includes("**Subject:** "+m.subject)||!source.includes("**Preheader:** "+m.preheader))throw Error("Subject/preheader divergence");
 const body=bodyFrom(source);
 if(body.split(m.editorial_cta).length!==2)throw Error("CTA absent or repeated");
 if(commercial&&(!m.editorial_cta.startsWith("[[")||!body.includes("Commercial disclosure:")))throw Error("No commercial disclosure");
 if(!commercial&&!m.editorial_cta.startsWith("https://finalvestige.com/"))throw Error("Editorial URL not first party");
 const html=genBlocks(body,commercial);
 if(commercial&&(!html.includes("GUIDE NOT LIVE — NO LINK")||!html.includes("Commercial disclosure:")))throw Error("Commercial hold lost");
 if(!commercial&&!html.includes('href="'+esc(m.editorial_cta)+'"'))throw Error("Editorial CTA lost");
 if(html.includes("[[VALID_POSTAL")||html.includes("[[JETPACK_UNSUBSCRIBE"))throw Error("Legal placeholder leaked");
 return {issue:num,kind:m.kind,post_title:m.subject,preheader_unverified:m.preheader,primary_cta:m.editorial_cta,post_type:"post",wordpress_email_mode_observed:"excerpt",post_created:false,send_to_subscribers:false,legal_footer_proven:false,unsubscribe_proven:false,preheader_supported_proven:false,actual_native_email_preview:false,merchant_permission_proven:false,release_ready:false,blocks_html:html};
}

function board(rows){
 const style="body{margin:0;background:#0b0e12;color:#f4efe6;font:17px/1.6 system-ui,sans-serif}main{width:min(900px,calc(100% - 28px));margin:30px auto}article{background:#171b20;border:1px solid #555;margin:24px 0;padding:clamp(16px,4vw,38px);overflow-wrap:anywhere}h1,h2{font-family:Georgia,serif;line-height:1.18}h2{font-size:clamp(24px,5vw,34px)}a{color:#ffd395;overflow-wrap:anywhere}a:focus-visible{outline:3px solid #fff;outline-offset:3px}.notice{padding:20px;border:2px solid #ffd395;background:#36291f}small{color:#ffd395;font-weight:700}.pre,footer{color:#ded5c9}footer{font-size:13px;border-top:1px solid #555;padding-top:14px}@media(max-width:420px){main{margin:16px auto}article{margin:16px 0}}";
 const cards=rows.map(r=>`<article aria-labelledby="issue-${r.issue}"><header><small>ISSUE ${String(r.issue).padStart(2,"0")} · HOLD UNSENT · ${esc(r.kind)}</small><h2 id="issue-${r.issue}">${esc(r.post_title)}</h2><p class="pre">Proposed preheader, not WordPress-verified: ${esc(r.preheader_unverified)}</p></header><section>${r.blocks_html.replace(/<!-- \/?wp:[^>]+ -->/g,"")}</section><footer>Offline editorial proposal, not a native Jetpack email; no CMS post exists.</footer></article>`).join("");
 return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Dispatch R23 — WordPress draft bridge, UNSENT</title><style>'+style+'</style></head><body><main><h1>Dispatch · WordPress Draft Adaptation</h1><p class="notice"><strong>NOT A WORDPRESS EMAIL PREVIEW.</strong> Six Gutenberg candidates generated locally for editorial inspection. The live site uses excerpt emails; no post, subscriber contact, or email send is authorized.</p>'+cards+'</main></body></html>';
}
const fs=require('fs'), path=require('path');
const root=path.resolve(__dirname,'..'),output=path.join(__dirname,'proofs');
function compile(write){
 const m=JSON.parse(fs.readFileSync(path.join(root,'manifest.json'),'utf8'));
 if(m.status!=='DRAFT_UNSENT_NO_SCHEDULING'||m.issues.length!==6||m.mix.editorial!==4||m.mix.commercial_review_pending!==2)throw Error('manifest changed');
 const rows=m.issues.map((item,i)=>adapt(item,fs.readFileSync(path.join(root,'issues',String(i+1).padStart(2,'0')+'-'+item.slug+'.md'),'utf8')));
 const led={status:'SOURCE_ONLY_UNSENT',date:'2026-10-31',parent_pr:318,parent_exact_sha:'7d19991eb4310ecbe44ab7a04bd8faf503df24fd',live_wordpress_format:'excerpt',created_posts:0,sent_emails:0,recipient_consents_verified:false,rendered_unsubscribe_verified:false,postal_verified:false,editions:rows.map(({blocks_html,...meta})=>meta)};
 const outputs={'RELEASE_COMPATIBILITY.json':JSON.stringify(led,null,2)+'\n','OFFLINE_POST_REVIEW.html':board(rows)};
 rows.forEach(r=>outputs['issue-'+String(r.issue).padStart(2,'0')+'.blocks.html']=r.blocks_html+'\n');
 if(write)fs.mkdirSync(output,{recursive:true});
 for(const [name,value] of Object.entries(outputs)){
  const target=path.join(output,name);
  if(write)fs.writeFileSync(target,value,'utf8'); else if(fs.readFileSync(target,'utf8')!==value)throw Error('preview mismatch '+name);
 }
 console.log(rows.length+' Gutenberg review candidates '+(write?'generated':'verified')+' (NOT SENDABLE)');
}
if(require.main===module)compile(!process.argv.includes('--verify'));
module.exports={esc,inl,bodyFrom,genBlocks,adapt,board,compile};
