'use strict';
/**
 * R142 strengthening of R141 Apollo reader custody: static-source check ONLY.
 * A successful result proves no more than an unambiguous HTML source link;
 * computed CSS, JavaScript, screen readers and network redirects require
 * separate browser acceptance. Not a sale, traffic, licensing or release gate.
 */
const {auditReaderContinuity,ARTICLE} = require('./r140_reader_continuity_gate.cjs');

const VOID = new Set(['area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr']);
// Native browser HTML parsing treats markup in these contexts as non-navigable.
const NON_NAVIGABLE = new Set([
  'script','style','template','noscript','svg','math','iframe','object',
  'textarea','title','xmp','plaintext','noembed','noframes',
  'select','option','optgroup'
]);
const NAME_AFFECTING = new Set(['img','input','svg','math','object','canvas']);
const TARGET_LABEL = 'Read the full investigation';

function decode(value) {
  return String(value).replace(/&(?:amp|lt|gt|quot|apos|nbsp|#(?:x[0-9a-f]+|\d+));/gi, (entity) => {
    const key=entity.slice(1,-1).toLowerCase();
    const named={amp:'&',lt:'<',gt:'>',quot:'"',apos:"'",nbsp:' '};
    if(Object.hasOwn(named,key)) return named[key];
    if(key[0]==='#'){
      const n=key[1]==='x'?parseInt(key.slice(2),16):parseInt(key.slice(1),10);
      return n>0 && n<=0x10ffff && !(n>=0xd800 && n<=0xdfff)?String.fromCodePoint(n):'';
    }
    return entity;
  });
}
function getAttr(raw,key){
  const re=new RegExp('(?:^|\\s)'+key+'(?:\\s*=\\s*(?:"([^"]*)"|\\x27([^\\x27]*)\\x27|([^\\s/>]+)))?(?=\\s|/?>|$)','i');
  const m=raw.match(re);
  return m?decode(m[1]??m[2]??m[3]??''):null;
}
const has=(raw,key)=>getAttr(raw,key)!==null;
function hiddenByMarkup(raw){
  const style=(getAttr(raw,'style')||'').replace(/\/\*[\s\S]*?\*\//g,'');
  return has(raw,'hidden') || has(raw,'inert') ||
    (getAttr(raw,'aria-hidden')||'').toLowerCase()==='true' ||
    /(?:^|;)\s*(?:display\s*:\s*none|visibility\s*:\s*(?:hidden|collapse))(?:\s*!important)?\s*(?:;|$)/i.test(style);
}
function tokenize(html){
  const out=[];let p=0;
  while(p<html.length){
    const a=html.indexOf('<',p);
    if(a<0){out.push({type:'text',value:html.slice(p)});break;}
    if(a>p)out.push({type:'text',value:html.slice(p,a)});
    if(html.startsWith('<!--',a)){
      const end=html.indexOf('-->',a+4);
      if(end<0){out.push({type:'error',value:'UNTERMINATED_COMMENT'});break;}
      p=end+3;continue;
    }
    let i=a+1,quote=null;
    for(;i<html.length;i++){
      const c=html[i];
      if(quote){if(c===quote)quote=null;}
      else if(c==='"'||c==="'")quote=c;
      else if(c==='>')break;
    }
    if(i===html.length){out.push({type:'error',value:'UNTERMINATED_TAG'});break;}
    out.push({type:'tag',value:html.slice(a+1,i)});
    p=i+1;
  }
  return out;
}
function readStaticLinks(html){
  const stack=[],links=[],errors=[];
  for(const token of tokenize(String(html))){
    if(token.type==='error'){errors.push(token.value);break;}
    if(token.type==='text'){
      // aria-hidden/hidden descendants are not permitted to supply the CTA name.
      if(stack.some(x=>x.hidden || x.ignored))continue;
      const value=decode(token.value);
      for(const item of stack)if(item.link)item.link.text+=value;
      continue;
    }
    const rawTag=token.value.trim();
    if(!rawTag || rawTag.startsWith('!') || rawTag.startsWith('?'))continue;
    const closing=rawTag[0]==='/';
    const match=rawTag.match(/^\/?([a-z][\w:-]*)\b/i);
    if(!match)continue;
    const tag=match[1].toLowerCase();
    if(closing){
      const index=stack.map(x=>x.tag).lastIndexOf(tag);
      if(index<0){
        if(tag==='a')errors.push('UNMATCHED_ANCHOR_CLOSE');
        continue;
      }
      for(const item of stack.splice(index))if(item.link)links.push(item.link);
      continue;
    }
    const raw=rawTag.slice(match[0].length);
    const parentIgnored=stack.some(x=>x.ignored);
    const parentHidden=stack.some(x=>x.hidden);
    const parentCollapsed=stack.some(x=>x.collapsed);
    const hidden=parentHidden || hiddenByMarkup(raw);
    const ignored=parentIgnored || NON_NAVIGABLE.has(tag);
    const collapsed=parentCollapsed || (tag==='details'&&!has(raw,'open'));

    // Any descendant whose accessible-name contribution cannot be safely
    // established without rendering prevents provisional source approval.
    if(!parentIgnored && !parentHidden){
      const insideAnchors=stack.filter(x=>x.link);
      for(const item of insideAnchors){
        if(!item.link || hidden)continue;
        if(NAME_AFFECTING.has(tag) || has(raw,'aria-label') || has(raw,'aria-labelledby') ||
           has(raw,'role') || (tag==='span'&&has(raw,'title'))){
          item.link.ambiguousName=true;
        }
      }
    }
    const entry={tag,hidden,ignored,collapsed,link:null};
    if(tag==='a' && !ignored){
      entry.link={
        href:getAttr(raw,'href'),target:getAttr(raw,'target'),
        tabindex:getAttr(raw,'tabindex'),ariaLabel:getAttr(raw,'aria-label'),
        ariaLabelledby:getAttr(raw,'aria-labelledby'),role:getAttr(raw,'role'),
        download:has(raw,'download'),hidden:hidden||collapsed,
        ambiguousName:false,text:''
      };
      if(stack.some(x=>x.link))errors.push('NESTED_ANCHOR');
    }
    if(!VOID.has(tag) && !rawTag.endsWith('/'))stack.push(entry);
    else if(entry.link)links.push(entry.link);
  }
  for(const item of stack)if(item.link){
    links.push(item.link);
    errors.push('UNTERMINATED_ANCHOR');
  }
  return {links,errors};
}
function auditStrictReaderContinuity(atlas,article){
  const legacy=auditReaderContinuity(atlas,article);
  const html=typeof atlas?.content==='string'?atlas.content:atlas?.content?.rendered||'';
  const parsed=readStaticLinks(html);
  const normalized=(s)=>s.replace(/\s+/g,' ').trim();
  const named=parsed.links.filter(x=>normalized(x.text)===TARGET_LABEL || x.ariaLabel===TARGET_LABEL);
  const valid=named.filter(x=>
    normalized(x.text)===TARGET_LABEL && x.href===ARTICLE && !x.hidden &&
    x.target!=='_blank' && !x.download && !x.ambiguousName &&
    (x.tabindex===null||x.tabindex==='0') &&
    (x.ariaLabel===null||x.ariaLabel===TARGET_LABEL) &&
    x.ariaLabelledby===null && (x.role===null||x.role==='link')
  );
  const blockers=[...legacy.blockers];
  if(parsed.errors.length)blockers.push('SOURCE_MARKUP_NOT_UNAMBIGUOUS');
  if(named.length!==1 || valid.length!==1)blockers.push('STRICT_ACCESSIBLE_STATIC_CTA_NOT_VERIFIED');
  const status=blockers.length?'REVIEW_REQUIRED':'SOURCE_LINK_CONTINUITY_ONLY';
  return Object.freeze({
    schema:'fv.apollo.r142.strict-accessible-name-custody.v1',
    source_pair:legacy.source_pair,
    findings:{
      named_reader_links:named.length,
      valid_visible_reader_links:valid.length,
      parse_warnings:parsed.errors.length,
      accessible_name_ambiguous:parsed.links.filter(x=>x.ambiguousName).length
    },
    blockers:[...new Set(blockers)],source_gate:status,
    next_action:blockers.length?null:ARTICLE,
    browser:'NOT_TESTED',axe:'NOT_TESTED',lcp_cls:'NOT_MEASURED',
    commercial_offer:'NOT_VERIFIED',media_rights:'REVIEW_REQUIRED',
    attributed_revenue:'NOT_OBSERVED',release:'STAGING_HOLD',approved_to_publish:false
  });
}
module.exports={auditStrictReaderContinuity,readStaticLinks};
