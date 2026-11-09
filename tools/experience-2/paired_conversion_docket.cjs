'use strict';
/** Read-only Page 6 + Focus Page 1579 release docket. Never writes to WordPress. */
const PINS=Object.freeze({homeModified:'2026-11-05T12:07:24',focusModified:'2026-11-05T17:44:02',frozenPr49:'10495883299d53596992c26a8987f629b2904670',focusRepairPr:1681,heroBridgePr:1689,formVerifierPr:1718});
function page(v){const p=v&&(v.structuredContent?.data||v.data||v);if(!p||typeof p.content!=='string')throw Error('MISSING_EDITOR_SOURCE');return p;}
function count(s,x){return s.split(x).length-1;}
function inspect(home,focus){
 const h=page(home),f=page(focus),H=h.content,F=f.content,e=[];
 if(h.id!==6||h.status!=='publish'||h.modified!==PINS.homeModified)e.push('HOME_VERSION_DRIFT');
 if(f.id!==1579||f.status!=='publish'||f.modified!==PINS.focusModified)e.push('FOCUS_VERSION_DRIFT');
 const margins=count(H,'class="fv-margin-strip__item"');if(margins!==72)e.push('MARGINS_NOT_72');
 const nav=(H.match(/<nav class="fv-hf__chapter-nav"[\s\S]*?<\/nav>/)||[])[0]||'';
 const chapters=(nav.match(/href="#fv-hf-[^"]+"/g)||[]).length;if(chapters!==7)e.push('CHAPTER_NAV_NOT_7');
 const hj=count(H,'<!-- wp:jetpack/subscriptions '),fj=count(F,'<!-- wp:jetpack/subscriptions ');
 if(hj!==1||fj!==1)e.push('NATIVE_JETPACK_BLOCK_DRIFT');
 if(!H.includes('The Victory Point note: an 1847 message')||!H.includes('NASA · Apollo 204 Review Board'))e.push('ARCHIVAL_SOURCE_CUSTODY_DRIFT');
 if(!F.includes('Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf')||!F.includes('52-page'))e.push('FIELD_BOOK_OR_EDITION_MISSING');
 const hero=(H.match(/<div class="fv-hf__opening-actions">[\s\S]*?<\/div>/)||[])[0]||'';
 if(!hero.includes('href="#fv-hf-evidence"')||!hero.includes('Read the investigations'))e.push('HERO_EVIDENCE_ACTIONS_DRIFT');
 const gift=F.match(/<script id="fvf-gift-v2">([\s\S]*?)<\/script>/)||[];
 if(gift.length!==2)e.push('FOCUS_GIFT_SCRIPT_MISSING');
 const risky=gift.length===2&&gift[1].includes('URLSearchParams')&&/get\(['"]subscribe['"]\)/.test(gift[1])&&gift[1].includes('if(q)')&&gift[1].includes('show()');
 return {source_integrity:e.length?'FAIL':'PASS',source_errors:e,
  observed:{home_modified:h.modified,focus_modified:f.modified,chapters,margins,homepage_jetpack_blocks:hj,focus_jetpack_blocks:fj,existing_homepage_focus_links:count(H,'href="/focus/"'),focus_in_first_hero:hero.includes('href="/focus/"'),published_query_can_claim_gift_ready:risky,fieldbook_pdf_ref_present:F.includes('Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf')}};
}
function assess(home,focus,receipts={}){
 const s=inspect(home,focus),b=[...s.source_errors];
 if(s.observed.published_query_can_claim_gift_ready)b.push('P0_SPOOFABLE_FOCUS_GIFT_UI_LIVE');
 if(!receipts.isolated_focus_repair_runtime)b.push('ISOLATED_FOCUS_REPAIR_RUNTIME_NOT_ACCEPTED');
 if(!receipts.verified_jetpack_confirmation)b.push('CONFIRMED_JETPACK_SUBSCRIPTION_NOT_VERIFIED');
 if(!receipts.verified_anonymous_guest_browser)b.push('ANONYMOUS_GUEST_BROWSER_NOT_VERIFIED');
 if(!receipts.independent_wcag_22_aa)b.push('WCAG_22_AA_NOT_ACCEPTED');
 if(!receipts.measured_lighthouse_cwv)b.push('LIGHTHOUSE_CWV_UNMEASURED');
 if(!receipts.media_delivered_and_rights_checked)b.push('MEDIA_BYTES_AND_RIGHTS_UNVERIFIED');
 if(!receipts.exact_sha_ci_and_qd)b.push('EXACT_SHA_CI_QD_NOT_ACCEPTED');
 if(!receipts.founder_specific_release_approval)b.push('FOUNDER_RELEASE_APPROVAL_REQUIRED');
 if(receipts.propose_hero_focus_bridge&&s.observed.published_query_can_claim_gift_ready)b.push('HERO_CTA_DEPENDS_ON_UNRELEASED_FOCUS_INTEGRITY_REPAIR');
 return {decision:s.source_integrity==='FAIL'?'SOURCE_DRIFT_HOLD':'RELEASE_HOLD',source:s,blockers:[...new Set(b)],immutable_frozen_pr_49_sha:PINS.frozenPr49,existing_proposals:{focus_repair:PINS.focusRepairPr,hero_focus_bridge:PINS.heroBridgePr,complete_form_verifier:PINS.formVerifierPr},site_writes:0,form_submissions:0,verified_leads_claimed:0,verified_sales_claimed:0,caveat:'No approval from source inspection. Real Jetpack/guest/browser/CI/QD and founder authorization mandatory.'};
}
module.exports={PINS,page,inspect,assess};
