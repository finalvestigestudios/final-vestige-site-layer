'use strict';
function validate(a){const errors=[],yes=(x,m)=>{if(!x)errors.push(m);};
if(!a||typeof a!=='object')return {ok:false,errors:['missing']};
yes(a.schema==='FV_USGS_NINE_20261106','schema');
yes(a.counts?.images===9&&a.counts?.official_originals_rendered===9&&a.counts?.stored_rendered===8&&a.counts?.stored_wrapper_unsupported===1&&a.counts?.exact_original_urls===7&&a.counts?.variants===2,'counts');
yes(a.assertions?.visitor_confirmed_broken===null&&a.assertions?.reported_42_broken==='UNVERIFIED'&&a.assertions?.claimed_76_percent_transfer_reduction==='UNMEASURED','uncertainty');
yes(a.assertions?.production_wp_writes===0&&a.assertions?.media_downloads===0&&a.assertions?.media_copies===0,'no production actions');
yes(Array.isArray(a.images)&&a.images.length===9,'nine slots');
const keys=['407:0','407:1','407:2','407:3','407:4','407:5','407:6','407:7','418:5'],seen=new Set();
for(const i of Array.isArray(a.images)?a.images:[]){const k=i?.key||'?';yes(keys.includes(k)&&!seen.has(k),k+' unique');seen.add(k);
yes(i.source_url?.startsWith('https://d9-wret.s3.us-west-2.amazonaws.com/')&&i.publisher_original_url?.startsWith('https://d9-wret.s3.us-west-2.amazonaws.com/')&&i.usgs_catalog_url?.startsWith('https://www.usgs.gov/media/images/'),k+' provenance');
yes(i.exact_original_url===(i.source_url===i.publisher_original_url)&&i.exact_original_url===(k!=='407:1'&&k!=='418:5'),k+' exact identity');
yes(i.retriever_publisher_original==='RENDERED'&&i.retriever_stored_source===(k==='407:1'?'UNSUPPORTED_BINARY_WRAPPER':'RENDERED'),k+' retriever');
yes(i.browser_http===null&&i.browser_broken===null&&i.natural_pixels===null&&i.wire_bytes===null,k+' no invented browser evidence');
yes(i.usgs_catalog_rights==='Public Domain'&&i.rights==='HOLD_ITEM_LEVEL'&&i.wp_cache===false&&i.wp_write===false,k+' rights');
yes(i.max_width===960&&i.no_upscale===true&&typeof i.credit==='string'&&i.credit.length>=12,k+' size/credit');
if(['407:2','407:3','407:7'].includes(k)){const g=i.cms_dimensions,p=i.conditional_960;yes(g?.width===1024&&p?.width===960&&p.height===Math.round(960*g.height/1024),k+' conditional HTML ratio');}
else yes(i.cms_dimensions===null&&i.conditional_960===null,k+' no invented geometry');
}
yes(keys.every(k=>seen.has(k)),'full cohort');
return {ok:errors.length===0,errors,source_only:true};}
if(typeof module!=='undefined')module.exports={validate};
