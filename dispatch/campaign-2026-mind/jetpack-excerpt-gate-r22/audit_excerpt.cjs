'use strict';
/* Local-only modeled excerpt-vs-full gate. No network, CMS writes, tracking or mail. */
const fs=require('fs'),path=require('path'),assert=require('assert');
const root=path.resolve(__dirname,'..');
const LIMIT=55;
function draftBody(s){
 const p=s.indexOf('\n---\n');
 if(p<0)throw Error('missing editorial boundary');
 const tail=s.slice(p+5);
 const end=tail.search(/\n---\n|\n\*\*Pre-send compliance block/);
 const body=(end>=0?tail.slice(0,end):tail).trim();
 if(!body)throw Error('missing editorial body');
 return body;
}
function plain(s){
 return s.replace(/\[([^\]]+)\]\(https?:\/\/[^)]+\)/g,'$1')
  .replace(/<[^>]*>/g,' ').replace(/^\s*[-*+]\s+/gm,'')
  .replace(/[*_`#>]/g,'').replace(/\s+/g,' ').trim();
}
function scan(manifest,readFile){
 assert.equal(manifest.issues.length,6,'six original editions required');
 assert.equal(manifest.issues.filter(x=>x.kind==='commercial-review-pending').length,2,'4:2 allocation required');
 return manifest.issues.map(item=>{
  const name=String(item.number).padStart(2,'0')+'-'+item.slug+'.md';
  const source=readFile(name);
  const body=draftBody(source), stripped=plain(body), words=stripped.split(/\s+/);
  if(!source.includes('[[VALID_POSTAL_ADDRESS_REQUIRED]]')||
    !source.includes('[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]'))throw Error('legal hold missing '+name);
  if(!body.includes(item.editorial_cta))throw Error('CTA mismatch '+name);
  for(const field of ['Subject','Preheader']){
   const key=field.toLowerCase();
   if(!source.includes('**'+field+':** '+item[key]))throw Error('subject/preheader mismatch '+name);
  }
  const commercial=item.kind==='commercial-review-pending';
  if(commercial&&!item.editorial_cta.startsWith('[['))throw Error('commercial URL unexpectedly live');
  const excerpt=words.slice(0,LIMIT).join(' ');
  const disclosurePos=stripped.toLowerCase().indexOf('commercial disclosure:');
  return {
   issue:item.number,subject:item.subject,preheader:item.preheader,
   kind:item.kind,release:'HOLD_UNSENT',merchant_release:commercial?'HOLD_MERCHANT':'NOT_APPLICABLE',
   approx_full_visible_words:words.length,assumed_word_limit:LIMIT,
   model_visible_fraction:Math.round(1000*Math.min(LIMIT,words.length)/words.length)/10,
   model_excerpt_not_native:excerpt,
   full_body_exceeds_model_limit:words.length>LIMIT,
   commercial_disclosure_inside_model:disclosurePos>=0&&stripped.slice(0,disclosurePos).trim().split(/\s+/).length<LIMIT,
   cta_url_inside_model:excerpt.includes(item.editorial_cta),
   legal_address_verified:false,unsubscribe_operational_verified:false,
   approved_merchant_email_rights:false,real_native_email_verified:false,
   founder_final_send_approved:false
  };
 });
}
function escapeHTML(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
function reviewHtml(rows){
 const cards=rows.map(r=>'<article aria-labelledby="issue'+r.issue+'"><header><p class="eyebrow">ISSUE '+String(r.issue).padStart(2,'0')+' · '+escapeHTML(r.kind)+' · HOLD</p><h2 id="issue'+r.issue+'">'+escapeHTML(r.subject)+'</h2><p>Proposed preheader: '+escapeHTML(r.preheader)+' <em>(not native-verified)</em></p></header><div class="cols"><section><h3>Approximate 55-word opening</h3><blockquote>'+escapeHTML(r.model_excerpt_not_native)+'</blockquote><small>Simulated only; a custom WordPress excerpt changes this.</small></section><section><h3>Lost in this model</h3><p>About '+r.model_visible_fraction+'% of the '+r.approx_full_visible_words+'-word manuscript is visible. Primary CTA omitted: '+(!r.cta_url_inside_model?'yes':'no')+'.</p><p>'+ (r.merchant_release==='HOLD_MERCHANT'?'Commercial disclosure not shown in this opening. Merchant approval absent.':'Original evidence and CTA remain later in the full letter.')+'</p><p>Postal, unsubscribe and real recipient verification all remain outstanding.</p></section></div></article>').join('\n');
 return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Dispatch R22 — Excerpt risk</title><style>*{box-sizing:border-box}body{margin:0;color:#eee9dd;background:#111313;font:16px/1.6 system-ui,sans-serif}main{max-width:1080px;margin:auto;padding:30px 18px 70px}h1,h2,h3{line-height:1.2}h1{font-size:clamp(2rem,5vw,3.3rem)}article{margin-top:26px;padding:25px;background:#1d1e1e;border:1px solid #4a433a;border-left:5px solid #c5a16b}.eyebrow{font-size:.75rem;letter-spacing:.1em;color:#e6bf80}blockquote{margin:0;padding:17px;border-left:2px solid #91a6bb;background:#2a2b2a;overflow-wrap:anywhere}.cols{display:grid;grid-template-columns:1fr 1fr;gap:24px}.cols>*{min-width:0}p{overflow-wrap:anywhere}a{color:#edc58a}a:focus-visible{outline:3px solid white}small{color:#d7c4ac}.alert{border:2px solid #ddaa64;padding:14px;background:#392b15}em{color:#cfc7bc}@media(max-width:700px){.cols{grid-template-columns:1fr}article{padding:17px}}</style></head><body><main><h1>The 55-word problem</h1><p class="alert"><strong>ALL SIX HOLD_UNSENT.</strong> This is an offline approximation, NOT a received Jetpack email, editor-native preview or permission to send.</p><p>WordPress documents first-55-word excerpt behavior when no explicit post excerpt is set. This site currently selects excerpt-mode email. These six simulations show what may be missing from a newsletter intended to deliver substantive original reporting. A custom excerpt or native renderer can change the result.</p>'+cards+'<p>Source: <a href="https://wordpress.com/support/newsletter-settings/">WordPress newsletter settings</a>. Real deliverability must be verified separately under the existing no-send release protocol.</p></main></body></html>';
}
function run(){
 const manifest=JSON.parse(fs.readFileSync(path.join(root,'manifest.json'),'utf8'));
 const rows=scan(manifest,name=>fs.readFileSync(path.join(root,'issues',name),'utf8'));
 assert(rows.every(r=>r.release==='HOLD_UNSENT'));
 assert(rows.filter(r=>r.merchant_release==='HOLD_MERCHANT').length===2);
 const record={evidence_type:'MODEL_NOT_WORDPRESS_RECEIPT',
 source:'Original six-manuscript manifest and 2026-10-31 WordPress excerpt setting',
 initial_draft_head:'17d2976b0be23da220165a0684f1da7df343193d',
 first_55_words_only_if_post_lacks_explicit_excerpt:true,
 observed_config_excerpt:true,
 did_not_create_post_or_send:true,all_release:'HOLD_UNSENT',issues:rows};
 if(process.argv.includes('--write')){
  fs.writeFileSync(path.join(__dirname,'R22_MODEL_SNAPSHOT.json'),JSON.stringify(record,null,2)+'\n');
  fs.writeFileSync(path.join(__dirname,'OFFLINE_REVIEW.html'),reviewHtml(rows));
 }
 console.log('R22 local model: '+rows.length+' UNSENT; 2 HOLD_MERCHANT; excerpt 55-word assumption, NOT native rendering');
 rows.forEach(r=>console.log('#'+String(r.issue).padStart(2,'0')+' '+r.model_visible_fraction+'% model visible; CTA in excerpt='+r.cta_url_inside_model+'; release='+r.release));
 return record;
}
if(require.main===module)run();
module.exports={draftBody,plain,scan,reviewHtml,escapeHTML,run,LIMIT};
