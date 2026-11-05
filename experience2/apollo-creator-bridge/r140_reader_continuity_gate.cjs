'use strict';
/** Apollo R140: offline read-only gate for a real Atlas -> real investigation CTA.
 * Parsed WP metadata is not proof of HTTP/browser navigation, publication by Grok,
 * NASA image permissions, email capture or a transaction. NO fetching or writes.
 */
const crypto = require('node:crypto');
const ATLAS = 'https://finalvestige.com/apollo-1-evidence-atlas/';
const ARTICLE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
const BOARD = 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/';
const EXPECTED = Object.freeze({ atlas:{id:2017,slug:'apollo-1-evidence-atlas',link:ATLAS}, article:{id:434,slug:'the-hatch-opened-inward-apollo-1',link:ARTICLE} });
function htmlOf(p){ const c=p&&p.content; return typeof c==='string'?c:(typeof c?.rendered==='string'?c.rendered:''); }
function attr(markup,key){const re=new RegExp('(?:^|\\s)'+key+'\\s*=\\s*(["\\x27])([\\s\\S]*?)\\1','i');return (markup.match(re)||[])[2]??null;}
function removeTags(html){return html.replace(/<[^>]*>/g,'').replace(/&nbsp;/g,' ').replace(/&amp;/g,'&').replace(/&#0*39;|&apos;/g,"'").replace(/&quot;/g,'"').replace(/\s+/g,' ').trim();}
function anchors(html){const out=[];const regex=/<a\b([^>]*)>([\s\S]*?)<\/a\s*>/gi;for(const m of html.matchAll(regex)){const open=m[1];out.push({href:attr(open,'href'),name:attr(open,'aria-label')||removeTags(m[2]),target:attr(open,'target'),download:attr(open,'download'),hidden:attr(open,'aria-hidden')==='true'||/(?:^|\s)(?:hidden|inert)(?=\s|=|$)/i.test(open),tabindex:attr(open,'tabindex')});}return out;}
function isSnapshot(p,spec){return p&&p.id===spec.id&&p.status==='publish'&&p.slug===spec.slug&&p.link===spec.link;}
function auditReaderContinuity(atlas, article, review={}){
 const reasons=[];const ah=htmlOf(atlas),bh=htmlOf(article);
 if(!isSnapshot(atlas,EXPECTED.atlas))reasons.push('ATLAS_METADATA_UNVERIFIED');
 if(!isSnapshot(article,EXPECTED.article))reasons.push('ARTICLE_METADATA_UNVERIFIED');
 if(ah.length<200||bh.length<200)reasons.push('HTML_SOURCE_MISSING');
 const staticHtml=ah.replace(/<script\b[^>]*>[\s\S]*?<\/script\s*>/gi,'').replace(/<template\b[^>]*>[\s\S]*?<\/template\s*>/gi,'');
 const links=anchors(staticHtml); const readerLinks=links.filter(a=>/read the full investigation/i.test(a.name||''));
 const verified=readerLinks.filter(a=>a.name.trim()==='Read the full investigation'&&a.href===ARTICLE&& !a.hidden && a.target!== '_blank' && a.download===null && a.tabindex!=='-1');
 if(readerLinks.length!==1 || verified.length!==1)reasons.push('READ_INVESTIGATION_CTA_NOT_ONE_VALID_STATIC_LINK');
 if(!/Apollo 1|Hatch Opened Inward/i.test(article?.title?.rendered??article?.title??''))reasons.push('ARTICLE_TITLE_NOT_CONFIRMED');
 if(!ah.includes(BOARD)||!bh.includes(BOARD))reasons.push('APOLLO_REVIEW_BOARD_CROSS_SOURCE_MISSING');
 const actual=links.filter(a=>a.href===ARTICLE).length;
 if(actual<1)reasons.push('INTERNAL_INVESTIGATION_LINK_MISSING');
 const noJs=verified.length===1; // Anchor exists outside JS/template in the original HTML source.
 const safeInputs=(p)=>crypto.createHash('sha256').update(htmlOf(p)).digest('hex');
 return Object.freeze({schema:'fv.apollo.r140.reader-continuity.v1',read_only:true,
  source_pair:{atlas_id:atlas?.id??null,article_id:article?.id??null,atlas_sha256:safeInputs(atlas),article_sha256:safeInputs(article)},
  findings:{static_reader_cta_count:readerLinks.length,valid_reader_cta_count:verified.length,article_links_in_atlas:actual,article_primary_board_link_present:bh.includes(BOARD),no_js_link_in_html:noJs,worksheet_in_production_not_assumed:true},
  blockers:[...new Set(reasons)],source_gate:reasons.length?'REVIEW_REQUIRED':'SOURCE_LINK_CONTINUITY_ONLY',
  landing_destination:ATLAS,next_action:reasons.length?null:ARTICLE,
  commercial_offer:'NOT_VERIFIED',paid_order:'NOT_OBSERVED',qualified_grok_sessions:'NOT_OBSERVED',browser:'NOT_TESTED',axe:'NOT_TESTED',lcp_cls:'NOT_MEASURED',media_rights:'REVIEW_REQUIRED',
  release:'STAGING_HOLD',approved_to_publish:false,
  caveat:'The no-JS static link is source-observed only; real browser behavior, WordPress rendering, NASA image rights and settled transactions require separate independent proof.'});
}
module.exports={auditReaderContinuity,ATLAS,ARTICLE,BOARD};
