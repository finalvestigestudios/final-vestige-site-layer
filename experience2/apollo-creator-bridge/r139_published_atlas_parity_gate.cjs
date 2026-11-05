'use strict';
/**
 * Apollo R139 — read-only WordPress Apollo Atlas metadata/source parity gate.
 * Caller supplies a previously READ snapshot (e.g., WP pages-get ID 2017).
 * No fetching, publishing, CMS writes, image reuse clearance, telemetry or sales.
 * Source parsing is not a DOM/browser/WordPress integration test. STAGING HOLD.
 */
const EXPECTED_URL='https://finalvestige.com/apollo-1-evidence-atlas/';
const SCHEMA='fv.apollo.r139.published-atlas-parity.v1';
const NASA_BOARD='https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/';
const distinct=a=>[...new Set(a)];
function attrs(tag){
 const result={};
 for(const m of tag.matchAll(/([\w:-]+)\s*=\s*(["'])(.*?)\2/g))result[m[1].toLowerCase()]=m[3];
 return result;
}
function auditPublishedAtlas(snapshot,review={}){
 const blockers=[];
 const page=snapshot&&typeof snapshot==='object'&&!Array.isArray(snapshot)?snapshot:{};
 const html=typeof page.content==='string'?page.content:page.content?.rendered;
 const hasHtml=typeof html==='string'&&html.length>100;
 if(page.id!==2017||page.status!=='publish'||page.link!==EXPECTED_URL||
    page.slug!=='apollo-1-evidence-atlas')blockers.push('WP_PUBLISHED_ROUTE_METADATA_NOT_MATCHED');
 if(!hasHtml)blockers.push('NO_READABLE_WORDPRESS_PAGE_SOURCE');
 const text=hasHtml?html:'';
 const anchors=[...text.matchAll(/<a\b[^>]*>/gi)].map(x=>attrs(x[0]));
 const images=[...text.matchAll(/<img\b[^>]*>/gi)].map(x=>attrs(x[0]));
 const sourceLinks=anchors.filter(a=>typeof a.href==='string'&&
  /^https:\/\/(www\.)?(nasa\.gov|images\.nasa\.gov)\//i.test(a.href));
 const chronologyRecords=[...text.matchAll(/\bid=["'](record-0[1-6])["']/g)].map(m=>m[1]);
 const missingAlt=images.filter(i=>!i.alt||!i.alt.trim()).length;
 const missingWidthHeight=images.filter(i=>!/^\d+$/.test(i.width||'')||
  !/^\d+$/.test(i.height||'')).length;
 const internalRoutes=anchors.map(a=>a.href||'').filter(x=>x.startsWith('#'));
 const internalIds=new Set([...text.matchAll(/\bid=["']([^"']+)["']/g)].map(x=>x[1]));
 const deadFragments=distinct(internalRoutes.filter(h=>!internalIds.has(h.slice(1))));
 const worksheetAnchor=anchors.filter(a=>a.href==='#classroom-preview');
 const hasWorksheet=worksheetAnchor.length===1&&internalIds.has('classroom-preview');
 const sourceBoard=sourceLinks.some(a=>a.href===NASA_BOARD);
 const uploadedNasaMedia=images.filter(i=>
  /(?:apollo1-nasa-|nasa\.gov|images\.nasa\.gov)/i.test(i.src||''));
 if(chronologyRecords.length!==6||distinct(chronologyRecords).length!==6)
  blockers.push('SIX_ATLAS_RECORDS_NOT_VERIFIED_IN_SOURCE');
 if(!sourceBoard)blockers.push('NASA_REVIEW_BOARD_LINK_MISSING');
 if(sourceLinks.length<6)blockers.push('INSUFFICIENT_NASA_SOURCE_LINKS');
 if(deadFragments.length)blockers.push('BROKEN_INTERNAL_FRAGMENT_REFERENCES');
 if(missingAlt)blockers.push('MISSING_IMAGE_ALT_TEXT');
 if(missingWidthHeight)blockers.push('UNSIZED_IMAGES_LAYOUT_SHIFT_RISK');
 if(!hasWorksheet)blockers.push('NO_MATCHING_FREE_CLASSROOM_WORKSHEET_PATH');
 if(uploadedNasaMedia.length)
  blockers.push('NASA_MEDIA_IN_LIVE_HTML_WITHOUT_SUPPLIED_INDIVIDUAL_REUSE_RECEIPTS');
 if(images.length && review.photoSpecificReuseReviewed===true)
  blockers.push('PHOTO_RIGHTS_CLAIM_REQUIRES_INDEPENDENT_MANIFEST_AND_REVIEW');
 // Route metadata from a WP API response is NOT browser acceptance or creator
 // publication proof. A separately reviewed route does not change that.
 if(review.independentlyReviewedLandingUrl!==EXPECTED_URL)
  blockers.push('LANDING_URL_NOT_SEPARATELY_REVIEWED');
 const candidateCheckoutLinks=anchors.filter(a=>/payhip\.com|checkout|cart/i.test(a.href||''));
 if(candidateCheckoutLinks.length)blockers.push('UNREVIEWED_COMMERCE_LINK_IN_ATLAS');
 return {
  schema:SCHEMA,source:'WORDPRESS_READ_ONLY_RESPONSE_NOT_BROWSER_PROOF',
  page:{id:page.id||null,slug:page.slug||null,status:page.status||null,
    link:page.link||null,modified:page.modified||null},
  findings:{source_html_characters:text.length,record_count:chronologyRecords.length,
    unique_records:distinct(chronologyRecords).length,nasa_source_links:sourceLinks.length,
    image_count:images.length,nasa_branded_image_references:uploadedNasaMedia.length,
    missing_alt_count:missingAlt,unsized_image_count:missingWidthHeight,
    dead_internal_fragments_count:deadFragments.length,dead_internal_fragments:deadFragments.slice(0,12),
    free_worksheet_route_present:hasWorksheet,checkout_candidates:candidateCheckoutLinks.length,
    review_board_source_present:sourceBoard},
  blockers:distinct(blockers),source_gate:blockers.length?'REVIEW_REQUIRED':'SOURCE_SNAPSHOT_PASS_ONLY',
  paid_offer:'NOT_VERIFIED',grok_publication:'NOT_VERIFIED',
  browser:'NOT_TESTED',axe:'NOT_TESTED',lcp_cls:'NOT_MEASURED',
  attribution:'NOT_OBSERVED',merchant_settled_sales:'NOT_OBSERVED',
  release:'STAGING_HOLD',approved_to_publish:false,
  caveat:'Live page status is WP metadata only. External rights, commercial approval and real browser behavior require independent evidence.'
 };
}
module.exports={auditPublishedAtlas,EXPECTED_URL,SCHEMA};
