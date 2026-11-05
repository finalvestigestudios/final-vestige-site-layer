'use strict';
/** Staging-only R141: conservative source-HTML verification for Apollo's static reader action.
 * No HTTP, visitor analytics, WordPress writes, rights adjudication or purchase certification.
 * This token reader is not a replacement for a browser DOM/a11y audit. */
const {auditReaderContinuity,ARTICLE}=require('./r140_reader_continuity_gate.cjs');
const VOID=new Set(['area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr']);
const SKIP=new Set(['script','style','template','noscript','svg','iframe','object']);
function decode(s){return String(s).replace(/&(?:amp|lt|gt|quot|apos|nbsp|#(?:x[0-9a-f]+|\d+));/gi,m=>{const v=m.slice(1,-1).toLowerCase();const table={amp:'&',lt:'<',gt:'>',quot:'"',apos:"'",nbsp:' '};if(v in table)return table[v];if(v[0]==='#'){const n=v[1]==='x'?parseInt(v.slice(2),16):parseInt(v.slice(1),10);return n>0&&n<=0x10ffff?String.fromCodePoint(n):''}return m})}
function getAttr(raw,key){const r=new RegExp('(?:^|\\s)'+key+'(?:\\s*=\\s*(?:"([^"]*)"|\x27([^\x27]*)\x27|([^\\s/>]+)))?(?=\\s|/?>|$)','i');const m=raw.match(r);return m?decode(m[1]??m[2]??m[3]??''):null}
function attrPresent(raw,name){return getAttr(raw,name)!==null}
function isHidden(raw){const style=getAttr(raw,'style')||'';return attrPresent(raw,'hidden')||attrPresent(raw,'inert')||(getAttr(raw,'aria-hidden')||'').toLowerCase()==='true'||/(?:^|;)\s*(?:display\s*:\s*none|visibility\s*:\s*(?:hidden|collapse))(?:\s*!important)?\s*(?:;|$)/i.test(style)}
function tokens(html){const out=[];let p=0;while(p<html.length){const a=html.indexOf('<',p);if(a<0){out.push({type:'text',value:html.slice(p)});break}if(a>p)out.push({type:'text',value:html.slice(p,a)});if(html.startsWith('<!--',a)){const end=html.indexOf('-->',a+4);p=end<0?html.length:end+3;continue}let i=a+1,quote=null;for(;i<html.length;i++){const c=html[i];if(quote){if(c===quote)quote=null}else if(c==='"'||c==="'")quote=c;else if(c==='>')break}if(i===html.length){out.push({type:'error',value:'UNTERMINATED_TAG'});break}out.push({type:'tag',value:html.slice(a+1,i)});p=i+1}return out}
function readStaticLinks(html){const stack=[], links=[],errors=[];
 for(const token of tokens(html)){
  if(token.type==='error'){errors.push(token.value);break}
  if(token.type==='text'){for(const entry of stack)if(entry.link&&!entry.ignored)entry.link.text+=decode(token.value);continue}
  const t=token.value.trim();if(!t||t.startsWith('!')||t.startsWith('?'))continue;
  const closing=t[0]==='/';const m=t.match(/^\/?([a-z][\w:-]*)\b/i);if(!m)continue;
  const tag=m[1].toLowerCase();
  if(closing){const idx=stack.map(x=>x.tag).lastIndexOf(tag);if(idx<0){continue}for(const entry of stack.splice(idx)){if(entry.link)links.push(entry.link)}continue}
  const parentIgnored=stack.some(x=>x.ignored),parentHidden=stack.some(x=>x.hidden);
  const raw=t.slice(m[0].length),hidden=parentHidden||isHidden(raw),ignored=parentIgnored||SKIP.has(tag);
  const entry={tag,hidden,ignored,link:null};
  if(tag==='a'&&!ignored){entry.link={href:getAttr(raw,'href'),target:getAttr(raw,'target'),tabindex:getAttr(raw,'tabindex'),ariaLabel:getAttr(raw,'aria-label'),download:attrPresent(raw,'download'),hidden,text:''};if(stack.some(x=>x.link))errors.push('NESTED_ANCHOR')}
  if(!VOID.has(tag)&&!t.endsWith('/'))stack.push(entry);else if(entry.link)links.push(entry.link);
 }
 for(const entry of stack)if(entry.link)links.push(entry.link);
 return {links,errors};
}
function auditStrictReaderContinuity(atlas,article){const legacy=auditReaderContinuity(atlas,article);
 const html=typeof atlas?.content==='string'?atlas.content:atlas?.content?.rendered||'';
 const parsed=readStaticLinks(html);
 const named=parsed.links.filter(x=>x.text.replace(/\s+/g,' ').trim()==='Read the full investigation'||x.ariaLabel==='Read the full investigation');
 const good=named.filter(x=>x.text.replace(/\s+/g,' ').trim()==='Read the full investigation'&&x.href===ARTICLE&&!x.hidden&&x.target!=='_blank'&&!x.download&&(x.tabindex===null||x.tabindex==='0')&&(!x.ariaLabel||x.ariaLabel==='Read the full investigation'));
 const blockers=[...legacy.blockers];if(parsed.errors.length)blockers.push('SOURCE_MARKUP_NOT_UNAMBIGUOUS');if(named.length!==1||good.length!==1)blockers.push('STRICT_ACCESSIBLE_STATIC_CTA_NOT_VERIFIED');
 return Object.freeze({schema:'fv.apollo.r141.strict-dom-custody.v1',source_pair:legacy.source_pair,findings:{named_reader_links:named.length,valid_visible_reader_links:good.length,parse_warnings:parsed.errors.length},blockers:[...new Set(blockers)],source_gate:blockers.length?'REVIEW_REQUIRED':'SOURCE_LINK_CONTINUITY_ONLY',next_action:blockers.length?null:ARTICLE,browser:'NOT_TESTED',commercial_offer:'NOT_VERIFIED',media_rights:'REVIEW_REQUIRED',attributed_revenue:'NOT_OBSERVED',release:'STAGING_HOLD',approved_to_publish:false});
}
module.exports={auditStrictReaderContinuity,readStaticLinks};
