'use strict';
/**
 * Apollo R143: exact, staging-only repair for the source-backed gallery
 * selector defect observed in published WP page 2017 (Nov 4 source).
 * Accept an explicit, read-only HTML export; never fetch or write WordPress.
 * Fails closed on drift. A source patch is NOT a browser/release clearance.
 */
const BAD="const photos = $(box, '[data-fvx-chrono-photo]');";
const FIX="const photos = $$(box, '[data-fvx-chrono-photo]');";
const ROUTE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
function count(s,needle){return s.split(needle).length-1;}
function inspect(html){
 if(typeof html!=='string')throw new TypeError('WordPress content must be a string');
 const scripts=[...html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script\s*>/gi)];
 const figures=[...html.matchAll(/<figure\b[^>]*\bdata-fvx-chrono-photo\s*=\s*(["'])(\d+)\1[^>]*>/gi)].map(x=>Number(x[2]));
 const gallery=html.includes('data-fvx-chrono-gallery');
 const slider=/<input\b[^>]*type=["']range["'][^>]*>/i.test(html);
 const sourceLinks=count(html,'Read the full investigation');
 const staticLinks=count(html,'href="'+ROUTE+'"');
 const originalCount=scripts.reduce((n,x)=>n+count(x[1],BAD),0);
 const fixedCount=scripts.reduce((n,x)=>n+count(x[1],FIX),0);
 const findings={gallery,slider,figures,originalCount,fixedCount,sourceLinks,staticLinks,scriptCount:scripts.length};
 const blockers=[];
 if(!gallery||!slider)blockers.push('GALLERY_OR_CHRONOLOGY_MISSING');
 if(figures.length!==3||figures.join(',')!=='0,1,2')blockers.push('THREE_ORDERED_CONTEXT_PHOTOS_NOT_CONFIRMED');
 if(scripts.length!==1)blockers.push('INLINE_SCRIPT_COUNT_DRIFT');
 if(originalCount+fixedCount!==1)blockers.push('EXACT_GALLERY_SELECTOR_DRIFT');
 if(sourceLinks!==1||staticLinks<1)blockers.push('EXISTING_READER_ACTION_DRIFT');
 return {findings,blockers};
}
function prepareGalleryRepair(html){
 const initial=inspect(html);
 if(initial.blockers.length)throw new Error('STAGING_HOLD '+initial.blockers.join(','));
 if(initial.findings.fixedCount===1)throw new Error('STAGING_HOLD ALREADY_REPAIRED');
 if(initial.findings.originalCount!==1)throw new Error('STAGING_HOLD EXPECTED_DEFECT_ABSENT');
 const output=html.replace(BAD,()=>FIX);
 if(count(output,FIX)!==1||count(output,BAD)!==0)throw new Error('STAGING_HOLD PATCH_NOT_UNIQUE');
 // Preserve every byte except the one additional "$" in the selector.
 if(output.replace(FIX,BAD)!==html)throw new Error('STAGING_HOLD UNEXPECTED_PATCH_DIFF');
 const check=inspect(output);
 if(check.blockers.length)throw new Error('STAGING_HOLD POSTPATCH_'+check.blockers.join(','));
 return Object.freeze({
  output,
  receipt:Object.freeze({schema:'fv.apollo.r143.gallery-selector-custody.v1',
   fixedSelector:FIX,referenceDefect:BAD,pre:initial.findings,post:check.findings,
   changedCharacters:1,approval:'STAGING_HOLD',actualBrowser:'NOT_TESTED',
   noJs:'UNCHANGED_SOURCE_REQUIRES_BROWSER_QA',mediaRights:'NOT_REVIEWED',
   merchant:'NOT_VERIFIED',realizedRevenue:'NOT_OBSERVED'})
 });
}
module.exports={inspect,prepareGalleryRepair,BAD,FIX};
