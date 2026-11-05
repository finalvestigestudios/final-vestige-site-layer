'use strict';
/** Apollo R144: read-only, fail-closed media/source/no-JS custody for WP Atlas gallery.
 * This validates published HTML evidence; it does not grant image rights, audit network
 * delivery, verify checkout, test accessibility in a real page, or write WordPress.
 */
const RECORDS = Object.freeze([
 Object.freeze({index:0,id:'S66-58038',source:'https://www.nasa.gov/image-detail/amf-s66-58038/',asset:'https://finalvestige.com/wp-content/uploads/2026/11/apollo1-nasa-s66-58038.jpg'}),
 Object.freeze({index:1,id:'S67-15717',source:'https://www.nasa.gov/image-detail/amf-s67-15717/',asset:'https://finalvestige.com/wp-content/uploads/2026/11/apollo1-nasa-s67-15717.jpg'}),
 Object.freeze({index:2,id:'KSC-20170124-PH_KLS01_0129',source:'https://images.nasa.gov/details/KSC-20170124-PH_KLS01_0129',asset:'https://finalvestige.com/wp-content/uploads/2026/11/apollo1-nasa-ksc-20170124-three-part-hatch.jpg'}),
]);
function attr(tag,key){
 const m=tag.match(new RegExp('(?:\\s|^)'+key+'\\s*=\\s*(?:"([^"]*)"|\'([^\']*)\'|([^\\s>]+))','i'));
 return m ? (m[1]??m[2]??m[3]) : null;
}
const textOnly=s=>s.replace(/<[^>]*>/g,' ').replace(/&(?:#x[0-9a-f]+|#\d+|[a-z]+);/gi,' ').replace(/\s+/g,' ').trim();
function inspect(html){
 if(typeof html!=='string')throw new TypeError('Expected read-only HTML export string');
 const findings={photoCount:0,records:[],staticGallery:0,chronologySource:false,editorialOnlyNotice:false,enhancedSelector:'UNKNOWN',approvedForCommercialUse:false};
 const blockers=[];
 const fail=(code)=>{if(!blockers.includes(code))blockers.push(code);};
 const block=html.match(/<section\b[^>]*\bdata-fvx-chronology\b[^>]*>[\s\S]*?<\/section\s*>/i);
 if(!block){fail('CHRONOLOGY_MISSING');return {findings,blockers,release:'STAGING_HOLD'};}
 const region=block[0];
 findings.chronologySource=/https:\/\/www\.nasa\.gov\/missions\/apollo\/apollo-1\/report-of-the-apollo-204-review-board\//.test(region);
 if(!findings.chronologySource)fail('REVIEW_BOARD_REFERENCE_MISSING');
 if(!/data-fvx-chrono-gallery/.test(region))fail('GALLERY_MISSING');
 findings.staticGallery=(region.match(/data-fvx-chrono-photo\s*=/g)||[]).length;
 const note=region.match(/<p\b[^>]*class=["'][^"']*fvx-chrono-gallery__note[^"']*["'][^>]*>([\s\S]*?)<\/p>/i);
 if(!note||!/not the actual fire/i.test(textOnly(note[1])))fail('NON_FIRE_CONTEXT_NOTE_MISSING');
 const tool=region.match(/<div\b[^>]*\bdata-fvx-chrono-tool\b[^>]*>/i)?.[0]||'';
 if(!/\shidden(?:\s|=|>)/i.test(tool))fail('NO_JS_SLIDER_NOT_HIDDEN');
 if(!/\.fv-ex2\s*\[hidden\]\s*\{\s*display\s*:\s*none\s*!important/i.test(html))fail('HIDDEN_CSS_GUARD_MISSING');
 const figures=[...region.matchAll(/<figure\b([^>]*)>([\s\S]*?)<\/figure\s*>/gi)].filter(m=>/\bdata-fvx-chrono-photo\s*=/.test(m[1]));
 findings.photoCount=figures.length;
 if(figures.length!==3||findings.staticGallery!==3)fail('THREE_CONTEXT_PHOTOS_REQUIRED');
 figures.forEach((m,i)=>{
  const tag='<figure '+m[1]+'>',body=m[2],id=attr(tag,'data-fvx-chrono-photo');
  const img=body.match(/<img\b[^>]*>/i)?.[0]||'',cap=body.match(/<figcaption\b[^>]*>([\s\S]*?)<\/figcaption\s*>/i)?.[1]||'';
  const expected=RECORDS[i];const observed={slot:i,photoIndex:id,recordId:expected?.id||null,sourceFound:false,assetFound:false,altFound:false,dimensionsFound:false,visibleWithoutJs:true};
  if(id!==String(i))fail('PHOTO_ORDER_OR_ID_DRIFT');
  if(/\s(?:hidden|inert)(?:\s|=|>)/i.test(tag)||/\saria-hidden\s*=\s*["']true["']/i.test(tag)||/\sstyle\s*=\s*["'][^"']*display\s*:\s*none/i.test(tag)){observed.visibleWithoutJs=false;fail('NO_JS_CONTEXT_PHOTO_HIDDEN');}
  observed.sourceFound=!!expected&&cap.includes('href="'+expected.source+'"');
  observed.assetFound=!!expected&&attr(img,'src')===expected.asset;
  observed.altFound=!!(attr(img,'alt')||'').trim()&&(attr(img,'alt')||'').trim().length>=30;
  observed.dimensionsFound=Number(attr(img,'width'))>0&&Number(attr(img,'height'))>0;
  if(!observed.sourceFound)fail('NASA_ORIGINAL_IMAGE_RECORD_MISMATCH');
  if(!observed.assetFound)fail('IMAGE_ASSET_CUSTODY_DRIFT');
  if(!observed.altFound)fail('ALT_TEXT_INSUFFICIENT');
  if(!observed.dimensionsFound)fail('IMAGE_DIMENSIONS_MISSING');
  if(!cap||!/(?:does not depict|not a photograph|fifty years after)/i.test(textOnly(cap)))fail('IMAGE_CONTEXT_DESCRIPTION_MISSING');
  if(/(?:payhip\.com|buy now|add to cart|checkout)/i.test(body))fail('UNREVIEWED_MEDIA_COMMERCE_LINK');
  findings.records.push(observed);
 });
 findings.editorialOnlyNotice=/Editorial use only\. Do not use these images in promotional, product or merchandise contexts\./i.test(textOnly(html));
 if(!findings.editorialOnlyNotice)fail('EDITORIAL_ONLY_RIGHTS_NOTICE_MISSING');
 const bad="const photos = $(box, '[data-fvx-chrono-photo]');",fixed="const photos = $$(box, '[data-fvx-chrono-photo]');";
 findings.enhancedSelector=html.includes(bad)?'BROKEN_PUBLISHED_SELECTOR':html.includes(fixed)?'STAGING_REPAIR_PRESENT':'UNKNOWN';
 if(findings.enhancedSelector==='BROKEN_PUBLISHED_SELECTOR')fail('PUBLISHED_GALLERY_ENHANCEMENT_DEFECT');
 if(findings.enhancedSelector==='UNKNOWN')fail('GALLERY_ENHANCEMENT_SELECTOR_DRIFT');
 return {findings,blockers,release:'STAGING_HOLD'};
}
module.exports={inspect,RECORDS};
