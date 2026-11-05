'use strict';
/**
 * Apollo R145. Evidence custody must refer to actual, accessible HTML DOM
 * structure—not imaginary image/source tags inside comments or templates.
 * Source-only gate; no browser, source licensing, revenue or release approval.
 */
const {inspect:legacy,RECORDS}=require('./r144_gallery_media_custody.cjs');
const VOID=new Set(['area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr']);
const RAW=new Set(['script','style','template','noscript','svg','math','textarea','title','xmp','iframe','object','noembed','noframes']);
function attrs(s){
 const out=Object.create(null),duplicates=[];
 const re=/([^\s=/>]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'\x60=<>]+)))?/g;
 for(const m of s.matchAll(re)){
   const key=m[1].toLowerCase();
   if(Object.hasOwn(out,key))duplicates.push(key);
   out[key]=m[2]??m[3]??m[4]??'';
 }
 return {out,duplicates};
}
function hidden(a){
 const style=(a.style||'').replace(/\/\*[\s\S]*?\*\//g,'');
 return Object.hasOwn(a,'hidden')||Object.hasOwn(a,'inert')||
  (a['aria-hidden']||'').toLowerCase()==='true'||
  /(?:^|;)\s*(?:display\s*:\s*none|visibility\s*:\s*(?:hidden|collapse))(?:\s*!important)?\s*(?:;|$)/i.test(style);
}
function parseStructure(html){
 if(typeof html!=='string')throw new TypeError('Expected read-only HTML');
 const stack=[],figures=[],warnings=[],counts={chronologies:0,galleries:0};
 let pos=0;
 while(pos<html.length){
   const at=html.indexOf('<',pos);
   if(at<0)break;
   if(html.startsWith('<!--',at)){
     const end=html.indexOf('-->',at+4);
     if(end<0){warnings.push('UNTERMINATED_COMMENT');break;}
     pos=end+3;continue;
   }
   if(html.startsWith('<!',at)||html.startsWith('<?',at)){
     const end=html.indexOf('>',at+2);
     if(end<0){warnings.push('UNTERMINATED_DECLARATION');break;}
     pos=end+1;continue;
   }
   let end=at+1,quote='';
   for(;end<html.length;end++){
     const c=html[end];
     if(quote){if(c===quote)quote='';}
     else if(c==='"'||c==="'")quote=c;
     else if(c==='>')break;
   }
   if(end>=html.length){warnings.push('UNTERMINATED_TAG');break;}
   const contents=html.slice(at+1,end).trim();
   pos=end+1;
   const m=contents.match(/^(\/)?([a-z][\w:-]*)\b/i);
   if(!m)continue;
   const close=Boolean(m[1]),tag=m[2].toLowerCase();
   if(close){
     const i=stack.map(x=>x.tag).lastIndexOf(tag);
     if(i<0)continue;
     if(i!==stack.length-1 && stack.slice(i).some(x=>x.chrono||x.gallery||x.figure))
       warnings.push('MALFORMED_CHRONOLOGY_NESTING');
     stack.splice(i);
     continue;
   }
   const {out:a,duplicates}=attrs(contents.slice(m[0].length));
   if(duplicates.length && (stack.some(x=>x.chrono)||Object.hasOwn(a,'data-fvx-chronology')))
     warnings.push('DUPLICATE_GALLERY_ATTRIBUTE');
   const ancestorChrono=stack.some(x=>x.chrono);
   const chrono=tag==='section'&&Object.hasOwn(a,'data-fvx-chronology');
   if(chrono){counts.chronologies++;if(ancestorChrono)warnings.push('NESTED_CHRONOLOGY');}
   const inChrono=chrono||ancestorChrono;
   const gallery=Object.hasOwn(a,'data-fvx-chrono-gallery');
   if(gallery){counts.galleries++;if(!ancestorChrono)warnings.push('GALLERY_OUTSIDE_CHRONOLOGY');}
   const inGallery=gallery||stack.some(x=>x.gallery);
   const isHidden=hidden(a)||stack.some(x=>x.hidden);
   const parentFigure=[...stack].reverse().find(x=>x.figure)?.figure||null;
   const inCaption=stack.some(x=>x.caption);
   let figure=null;
   if(Object.hasOwn(a,'data-fvx-chrono-photo')){
     if(tag!=='figure'||!inChrono||!inGallery||parentFigure)
       warnings.push('MISPLACED_CONTEXT_PHOTO');
     else {
       figure={index:a['data-fvx-chrono-photo'],hidden:isHidden,images:[],links:[],captionCount:0};
       figures.push(figure);
     }
   }
   if(tag==='figcaption'&&parentFigure)parentFigure.captionCount++;
   if(tag==='img'&&parentFigure)parentFigure.images.push({
     src:a.src||null,alt:a.alt??null,width:a.width??null,height:a.height??null,hidden:isHidden
   });
   if(tag==='a'&&parentFigure&&inCaption)parentFigure.links.push({
     href:a.href||null,hidden:isHidden,ariaLabel:a['aria-label']??null,role:a.role??null
   });
   if(RAW.has(tag)){
     // Raw-content elements do not create navigable gallery records.
     const regex=new RegExp('<\\/\\s*'+tag+'\\s*>','i');
     const found=regex.exec(html.slice(pos));
     if(!found){warnings.push('UNTERMINATED_RAW_CONTENT');break;}
     pos+=found.index+found[0].length;
     continue;
   }
   if(!VOID.has(tag)&&!contents.endsWith('/'))
     stack.push({tag,chrono,gallery,figure,caption:tag==='figcaption'&&Boolean(parentFigure),hidden:isHidden});
 }
 if(stack.some(x=>x.chrono||x.gallery||x.figure))warnings.push('UNCLOSED_CHRONOLOGY_MARKUP');
 return {figures,warnings:[...new Set(warnings)],counts};
}
function audit(html){
 const base=legacy(html),structure=parseStructure(html);
 const blockers=[...base.blockers],fail=code=>{if(!blockers.includes(code))blockers.push(code);};
 if(structure.warnings.length)fail('GALLERY_MARKUP_AMBIGUOUS');
 if(structure.counts.chronologies!==1||structure.counts.galleries!==1)fail('GALLERY_SCOPE_NOT_UNIQUE');
 if(structure.figures.length!==3||structure.figures.some((f,i)=>f.index!==String(i)))
   fail('THREE_VISIBLE_SCOPED_FIGURES_NOT_CONFIRMED');
 for(let i=0;i<structure.figures.length;i++){
   const f=structure.figures[i],r=RECORDS[i];
   if(!r){fail('UNEXPECTED_CONTEXT_PHOTO');continue;}
   if(f.hidden||f.images.some(x=>x.hidden)||f.links.some(x=>x.hidden))
     fail('SOURCE_CONTENT_INACCESSIBLE_WITHOUT_JS');
   if(f.captionCount!==1||f.images.length!==1)fail('FIGURE_IMAGE_CAPTION_STRUCTURE_DRIFT');
   const img=f.images[0];
   if(!img||img.src!==r.asset||!img.alt||img.alt.trim().length<30||
      !(Number(img.width)>0&&Number(img.height)>0))
     fail('VISIBLE_IMAGE_CUSTODY_NOT_CONFIRMED');
   if(f.links.length!==1||f.links[0].href!==r.source ||
      f.links[0].ariaLabel===''||(f.links[0].role&&f.links[0].role!=='link'))
     fail('VISIBLE_ORIGINAL_SOURCE_LINK_NOT_CONFIRMED');
 }
 return Object.freeze({
   schema:'fv.apollo.r145.gallery-semantic-custody.v1',
   findings:{
     scopedChronologies:structure.counts.chronologies,
     scopedGalleries:structure.counts.galleries,
     sourceRecordCount:structure.figures.length,
     parserWarnings:structure.warnings,
     photos:structure.figures.map(f=>({index:f.index,hidden:f.hidden,
       images:f.images.length,visibleOriginalLinks:f.links.filter(a=>!a.hidden).length}))
   },
   blockers,sourceGate:blockers.length?'REVIEW_REQUIRED':'SOURCE_STRUCTURE_PASS',
   browser:'NOT_TESTED',axe:'NOT_TESTED',lcp_cls:'NOT_MEASURED',
   photoCommercialRights:'NOT_APPROVED',merchant:'NOT_VERIFIED',
   verifiedSales:'NOT_OBSERVED',release:'STAGING_HOLD'
 });
}
module.exports={parseStructure,audit};
