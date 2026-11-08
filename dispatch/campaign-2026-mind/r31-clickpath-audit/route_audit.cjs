'use strict';
/**
 * R31: WordPress/Jetpack excerpt click-path audit.
 * Read-only, deterministic, no HTTP, no email, no subscriber access, no WordPress writes.
 * A Jetpack "Read more" points at the POST, not necessarily at the manifest's editorial CTA.
 */
function auditRoutes(manifest, excerpts, snapshot) {
 const errors=[],warnings=[],routes=[];
 const m=manifest||{}, x=excerpts||{}, s=snapshot||{};
 if(m.status!=='DRAFT_UNSENT_NO_SCHEDULING')errors.push('manifest_must_remain_unsent');
 if(m.mix?.editorial!==4||m.mix?.commercial_review_pending!==2)errors.push('founder_4_2_mix');
 if(!Array.isArray(m.issues)||m.issues.length!==6)errors.push('manifest_six');
 if(!Array.isArray(x.entries)||x.entries.length!==6)errors.push('excerpts_six');
 if(x.status!=='DRAFT_FOR_WORDPRESS_EDITOR_REVIEW_ONLY')errors.push('excerpt_status');
 if(s.email_new_posts_by_default!==false)errors.push('site_auto_send_not_disabled');
 if(s.email_content_format!=='excerpt')errors.push('live_setting_drift_requires_new_native_proof');
 if(!s.newsletter_enabled)errors.push('newsletter_unavailable');
 for(let i=0;i<6;i++){
   const a=m.issues?.[i], b=x.entries?.[i],n=i+1,commercial=n===3||n===5;
   if(!a||!b){errors.push('missing_edition_'+n);continue}
   const href=a.editorial_cta||'',copy=b.excerpt||'';
   if(a.number!==n||b.number!==n||a.subject!==b.subject)errors.push('subject_order_'+n);
   if(a.publish_state!=='hold'||a.merchant_affiliate_url!==null)errors.push('activation_'+n);
   if((a.kind==='commercial-review-pending')!==commercial)errors.push('allocation_'+n);
   if(/\b(?:https?:\/\/|utm_|aff_id=|clickbank)\b/i.test(copy))errors.push('unexpected_link_in_excerpt_'+n);
   if(/\[\[|\]\]/.test(copy))errors.push('placeholder_in_excerpt_'+n);
   if(commercial){
     if(!/^\[\[APPROVED_(ZEN12|HYPNOSIS_LIVE)_WARMUP_GUIDE_URL_REQUIRED\]\]$/.test(href))errors.push('unapproved_commercial_destination_'+n);
     if(!/affiliate/i.test(copy)||!/may earn a commission/i.test(copy))errors.push('missing_commercial_excerpt_disclosure_'+n);
   } else {
     if(!/^https:\/\/finalvestige\.com\//.test(href))errors.push('editorial_cta_not_internal_'+n);
     if(/affiliate|earn a commission/i.test(copy))errors.push('commercial_language_in_editorial_'+n);
   }
   const proseClickCue=/(?:^|[.!?]\s+)(?:Read |Open |Explore )/.test(copy);
   if(proseClickCue&&!/https?:\/\//.test(copy))warnings.push('issue_'+n+'_textual_read_cue_is_not_a_direct_hyperlink');
   routes.push({
      number:n,kind:a.kind,subject:a.subject,
      email_surface:'Jetpack custom excerpt (OPTIONAL; not approved)',
      email_primary_link_target:'Jetpack automatic Read-more → its newsletter post (NOT the editorial CTA)',
      newsletter_post_url:null,
      next_step_link_on_unpublished_post:href,
      destinations_verified_on_site:false,
      total_reader_hops_to_manifest_cta:2,
      direct_cta_in_email_verified:false,
      native_email_received:false,
      approved_to_send:false,
      legal_postal_footer_verified:false,
      functional_unsubscribe_verified:false,
      preheader_native_verified:false,
      status:commercial?'HOLD_UNSENT_AND_HOLD_MERCHANT':'HOLD_UNSENT'
   });
 }
 return {
   schema:'fv-dispatch-r31-clickpath-v1',
   evaluated_setting:s.email_content_format||null,
   operational_rule:'An excerpt is not an email containing the editorial link: WordPress Read-more opens the newsletter post. A second explicit site link is needed there.',
   all_emails_unsent:true,
   all_offers_inactive:true,
   all_destination_post_urls_unknown:true,
   errors,warnings,routes
 };
}
module.exports={auditRoutes};
if(require.main===module){
 const fs=require('node:fs'),path=require('node:path'),root=path.resolve(__dirname,'..');
 const m=JSON.parse(fs.readFileSync(path.join(root,'manifest.json'),'utf8'));
 const x=JSON.parse(fs.readFileSync(path.join(root,'delivery/wordpress_excerpt_copy.json'),'utf8'));
 const s=JSON.parse(fs.readFileSync(path.join(__dirname,'SITE_SNAPSHOT.json'),'utf8'));
 const result=auditRoutes(m,x,s);
 console.log(JSON.stringify(result,null,2));
 if(result.errors.length)process.exitCode=1;
}