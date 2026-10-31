'use strict';
// Dispatch R29. OFFLINE ONLY. No API, network, email, WordPress or subscriber access.
const HOLD='DO NOT PUBLISH OR EMAIL — DRAFT ONLY';
const legal=['[[VALID_POSTAL_ADDRESS_REQUIRED]]','[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]'];
function audit(manifest,sources,firstBlocks,live={auto:false,mode:'excerpt',native:false,postal:false,unsub:false}){
 const errors=[],rows=[];
 if(manifest.status!=='DRAFT_UNSENT_NO_SCHEDULING') errors.push('campaign-status');
 if(manifest.mix?.editorial!==4||manifest.mix?.commercial_review_pending!==2||manifest.issues?.length!==6)errors.push('campaign-four-two');
 if(live.auto!==false||live.mode!=='excerpt')errors.push('current-wordpress-settings-drift');
 if(live.native||live.postal||live.unsub)errors.push('unverified-native-or-legal-evidence-asserted');
 const seen=new Set();
 for(let ix=0;ix<6;ix++){
  const x=manifest.issues[ix],raw=sources[ix],block=firstBlocks[ix],n=ix+1,commercial=n===3||n===5;
  if(!x||!raw||!block){errors.push(n+':missing-input');continue}
  if(x.number!==n||x.publish_state!=='hold'||x.merchant_affiliate_url!==null)errors.push(n+':activation');
  if((x.kind==='commercial-review-pending')!==commercial)errors.push(n+':role');
  if(!raw.includes('**Subject:** '+x.subject)||!raw.includes('**Preheader:** '+x.preheader))errors.push(n+':subject-preheader-drift');
  if(seen.has(x.subject)||x.subject.length>65||x.preheader.length>105)errors.push(n+':metadata-honesty');
  seen.add(x.subject);
  if(legal.some(k=>!raw.includes(k)))errors.push(n+':legal-hold-missing');
  if(!block.trim().startsWith('<!-- wp:paragraph --><p><strong>'+HOLD+'</strong>'))errors.push(n+':gutenberg-first-block-hold-missing');
  const parts=raw.split('\n---\n');
  if(parts.length<3){errors.push(n+':source-boundary');continue}
  const body=parts[1];
  if(body.split(x.editorial_cta).length!==2)errors.push(n+':cta-not-exactly-once');
  if(commercial){
   if(!x.editorial_cta.startsWith('[[')||!body.includes('**Commercial disclosure:**')||body.indexOf('**Commercial disclosure:**')>body.indexOf(x.editorial_cta))errors.push(n+':merchant-hold-or-disclosure');
  }else if(!x.editorial_cta.startsWith('https://finalvestige.com/'))errors.push(n+':external-editorial-cta');
  if(/clickbank|affiliates\.inspire3|utm_source=|aff_id=/i.test(body))errors.push(n+':earning-or-tracking-link');
  const visible=body.replace(/\[([^\]]+)\]\(https:\/\/[^)]+\)/g,'$1').replace(/\*\*/g,'').replace(/\s+/g,' ').trim();
  const first350=visible.slice(0,350),first55=visible.split(/\s+/).slice(0,55).join(' ');
  rows.push({number:n,kind:x.kind,subject:x.subject,subject_characters:x.subject.length,proposed_preheader_not_verified:x.preheader,preheader_characters:x.preheader.length,first_native_candidate_block_is_hold:true,editorial_first_140_characters_simulated:visible.slice(0,140),model_350_characters: first350,model_55_words:first55,cta_in_350:first350.includes(x.editorial_cta),cta_in_55:first55.includes(x.editorial_cta),commercial_disclosure_in_350:commercial?first350.includes('Commercial disclosure:'):null,received_email_proven:false,legal_footer_proven:false,release_status:commercial?'HOLD_UNSENT_AND_MERCHANT':'HOLD_UNSENT'});
 }
 return {schema:'fv-dispatch-inbox-contract-r29',parent_exact_sha:'6db066be8c479f17756406f39c429ba6c1b6dad2',snapshot_utc:'2026-10-31T22:38:53Z',not_actual_jetpack_email:true,errors,release_ready:false,issues:rows};
}
function escapeHTML(v){return String(v).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;')}
function reviewHtml(data){
 const cells=data.issues.map(x=>'<article aria-labelledby="issue-'+x.number+'"><span class="tag">ISSUE '+String(x.number).padStart(2,'0')+' · '+(x.kind==='editorial'?'EDITORIAL':'COMMERCIAL HOLD')+'</span><h2 id="issue-'+x.number+'">'+escapeHTML(x.subject)+'</h2><p><strong>Unverified proposed preheader:</strong> '+escapeHTML(x.proposed_preheader_not_verified)+'</p><dl><dt>First Gutenberg candidate block (intentional safety hold)</dt><dd class="risk">'+escapeHTML(HOLD)+'</dd><dt>Editorial opening—hypothetical display, not an inbox screenshot</dt><dd>'+escapeHTML(x.editorial_first_140_characters_simulated)+'</dd></dl><p class="muted">'+escapeHTML(x.release_status)+' · CTA absent from both modeled short excerpts</p></article>').join('');
 return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Final Vestige Dispatch — native inbox contract review (NOT A DELIVERED EMAIL)</title><style>:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#090b0b;color:#f4efe6;font:16px/1.6 system-ui,sans-serif}main{max-width:1060px;margin:0 auto;padding:clamp(18px,4vw,60px)}h1,h2{font-family:Georgia,serif;line-height:1.13}h1{font-size:clamp(30px,5vw,58px)}h2{font-size:clamp(23px,3vw,32px)}.alert{border:2px solid #e8c38b;background:#39271a;padding:24px;margin:24px 0 38px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,390px),1fr));gap:20px}article{padding:clamp(16px,3vw,26px);border:1px solid #565047;background:#151718;overflow-wrap:anywhere}dt,.tag{font-weight:700;color:#f3c789;font-size:13px}dd{margin:6px 0 22px}.risk{color:#ffb9a9}.muted{color:#c8c0b4;font-size:14px}a{color:#f3c789}a:focus-visible{outline:3px solid #fff;outline-offset:4px}.skip{position:absolute;left:-9999px}.skip:focus{left:12px;top:12px;padding:12px;background:#fff;color:#000}@media(max-width:420px){.grid{grid-template-columns:1fr}} </style></head><body><a class="skip" href="#main">Skip to review</a><main id="main"><p class="tag">FINAL VESTIGE STUDIOS · SOURCE-CONTROLLED REVIEW</p><h1>Six draft letters. No verified inbox presentation.</h1><p class="alert" role="note"><strong>HOLD ALL SIX — NOTHING SENT.</strong> This is a synthetic offline board, NOT an actual Jetpack email, WordPress-native preview, legal proof, or screenshot of any inbox. The site currently uses excerpt emails and automatic new-post sends are OFF. Intended preheaders are not verified controls. Commercial #03/#05 require written affiliate email permission.</p><div class="grid" aria-label="Six source and inbox reviews">'+cells+'</div><p class="muted">No subscriber identities, active affiliate earning links, mailing, publishing or tracking. The draft-only Gutenberg warning remains on purpose until a separately authorized release.</p></main></body></html>';
}
module.exports={audit,reviewHtml,HOLD};
if(require.main===module){
 const fs=require('fs'),path=require('path'),dir=path.resolve(__dirname,'..'),m=JSON.parse(fs.readFileSync(path.join(dir,'manifest.json'),'utf8'));
 const sources=m.issues.map(x=>fs.readFileSync(path.join(dir,'issues',String(x.number).padStart(2,'0')+'-'+x.slug+'.md'),'utf8'));
 const blocks=m.issues.map(x=>fs.readFileSync(path.join(dir,'wordpress-post-bridge-r23','proofs','issue-'+String(x.number).padStart(2,'0')+'.blocks.html'),'utf8').split('\n')[0]);
 const result=audit(m,sources,blocks);
 if(result.errors.length)throw Error(result.errors.join('; '));
 fs.writeFileSync(path.join(__dirname,'INBOX_CONTRACT.json'),JSON.stringify(result,null,2)+'\n');
 fs.writeFileSync(path.join(__dirname,'REVIEW_BOARD.html'),reviewHtml(result));
 console.log('6/6 source issues HOLD, 0 verified native email proofs; no network or mail');
}