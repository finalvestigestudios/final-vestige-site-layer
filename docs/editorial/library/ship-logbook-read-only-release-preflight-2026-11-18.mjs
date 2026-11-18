#!/usr/bin/env node
/**
 * Final Vestige Library: nine-guide read-only WordPress preflight.
 * Node 20+; no dependencies; no write, publish, email, social or spending actions.
 * WP_USER=... WP_APP_PASSWORD=... node this-file.mjs
 * Or supply --fixture path/to/exported-rest-json where each file is <id>.json.
 * Authenticated checks DO NOT constitute visual, screen-reader, print or email QA.
 */
import {readFile} from 'node:fs/promises';
import {resolve} from 'node:path';

const base=(process.env.WP_BASE||'https://finalvestige.com').replace(/\/$/,'');
const ids=[2886,2887,2888,2889,2890,2891,2892,2893,2894];
const slugs=['ship-logbook-archive-route','ship-logbook-missing-record','ship-logbook-vessel-identity','ship-logbook-page-anatomy','ship-logbook-crew-identity','ship-logbook-position-track','ship-logbook-port-dates','ship-logbook-message-chain','ship-logbook-correction-chain'];
const arg=process.argv.indexOf('--fixture');
const fixture=arg<0?null:process.argv[arg+1];
const failures=[],warnings=[],pages=[];
const flag=(sink,id,detail)=>sink.push({id,detail});
const attr=(tag,key)=>tag.match(new RegExp('\\b'+key+'\\s*=\\s*(["\\x27])(.*?)\\1','i'))?.[2]??null;
const canonical=url=>url.replace(/&amp;/g,'&').split(/[?#]/)[0].replace(/\/$/,'');
async function get(id) {
  if(fixture) return JSON.parse(await readFile(resolve(fixture,id+'.json'),'utf8'));
  if(!process.env.WP_USER||!process.env.WP_APP_PASSWORD) throw Error('Missing read-only WP_USER/WP_APP_PASSWORD');
  const token=Buffer.from(process.env.WP_USER+':'+process.env.WP_APP_PASSWORD).toString('base64');
  const url=base+'/wp-json/wp/v2/pages/'+id+'?context=edit&_fields=id,slug,status,parent,content,meta,link';
  const r=await fetch(url,{headers:{Authorization:'Basic '+token,Accept:'application/json'},signal:AbortSignal.timeout(18000),redirect:'error'});
  if(!r.ok)throw Error('Page '+id+' read returned HTTP '+r.status);
  return r.json();
}
function check(p,id,index) {
  const h=typeof p.content==='string'?p.content:(p.content?.raw||'');
  if(!h)flag(failures,id,'Missing edit-context raw content');
  for(const [k,v] of Object.entries({id,status:'draft',parent:77,slug:slugs[index]}))if(p[k]!==v)flag(failures,id,k+' expected '+v+' got '+p[k]);
  if(p.meta?.jetpack_seo_noindex!==true)flag(warnings,id,'Noindex not confirmed true in REST response');
  const anchors=[...h.matchAll(/\bid=(["'])(.*?)\1/g)].map(m=>m[2]);
  const duplicates=[...new Set(anchors.filter((s,j)=>anchors.indexOf(s)!==j))];
  if(duplicates.length)flag(failures,id,'Duplicate HTML IDs: '+duplicates.join(','));
  const links=[...h.matchAll(/<a\b[^>]*>/gi)].map(m=>attr(m[0],'href'));
  if(links.some(u=>!u||u==='#'||/^javascript:/i.test(u)))flag(failures,id,'Empty or unsafe href');
  const fragments=links.filter(u=>u?.startsWith('#')&&!anchors.includes(u.slice(1)));
  if(fragments.length)flag(failures,id,'Unresolved local fragment(s): '+fragments.join(','));
  const peer=links.filter(u=>u?.includes('/free-resources/ship-logbook-'));
  const missing=slugs.filter((s,j)=>j!==index&&!peer.some(u=>canonical(u).endsWith('/free-resources/'+s)));
  if(peer.length!==8||missing.length)flag(failures,id,'Expected eight peer links; found '+peer.length+'; missing '+missing.join(','));
  const current=(h.match(/\baria-current\s*=\s*["']page["']/gi)||[]).length;
  if(current!==1)flag(failures,id,'Expected one current page marker; got '+current);
  const imgs=[...h.matchAll(/<img\b[^>]*>/gi)].map(m=>m[0]);
  if(imgs.some(x=>attr(x,'alt')===null))flag(failures,id,'Image missing alt attribute');
  const svgs=[...h.matchAll(/<svg\b[\s\S]*?<\/svg>/gi)].map(m=>m[0]);
  if(svgs.some(x=>!/<title\b/i.test(x)||!/<desc\b/i.test(x)))flag(warnings,id,'SVG lacks title or desc');
  const controls=(h.match(/<(?:input|textarea|select|button)\b/gi)||[]).length;
  if(controls&&!/<label\b/i.test(h))flag(warnings,id,'Interactive form controls lack label; manual audit');
  const ext=[...new Set(links.filter(u=>/^https?:/i.test(u||'')))];
  if(!ext.some(u=>u.includes('archives.gov')||u.includes('titanicinquiry.org')))flag(warnings,id,'No direct institutional research link found');
  return {id,slug:p.slug,contentCharacters:h.length,blocks:(h.match(/<!-- wp:/g)||[]).length,links:links.length,peerLinks:peer.length,externalLinks:ext.length,htmlIds:anchors.length,svgs:svgs.length,scripts:(h.match(/<script\b/gi)||[]).length,controls,noindexConfirmed:p.meta?.jetpack_seo_noindex===true};
}
for(let i=0;i<ids.length;i++)try{pages.push(check(await get(ids[i]),ids[i],i))}catch(e){flag(failures,ids[i],String(e.message||e))}
const result={name:'FV Library maritime series — read-only structural preflight',generatedAt:new Date().toISOString(),mode:fixture?'offline fixture':'authenticated WP REST',filesAudited:pages.length,filesExpected:9,pages,failures,warnings,readyForPublication:false,
unverifiedReleaseGates:[
'Actual production-theme viewport and overflow QA at 320/390/768/1440',
'Real keyboard and screen-reader navigation',
'Worksheet interaction/print on the real production theme',
'External source responses, full PDF pages and item-specific rights',
'Nine sibling pages all public 200 with correct canonical at release',
'Enforceable per-page newsletter/social opt-out independently read back'
]};
process.stdout.write(JSON.stringify(result,null,2)+'\n');
if(failures.length)process.exitCode=1;
