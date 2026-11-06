'use strict';
const validate=function validate(a){const errors=[],ok=(v,m)=>{if(!v)errors.push(m)};if(!a)return {ok:false,errors:["missing"]};
const c=a.counts||{},r=a.release||{},q=a.claims||{},i=a.images||[];
ok(a.schema==="fv-navy-15-catalog-20261106-v1","schema");
ok(c.legacy_posts===61&&c.legacy_images===355&&c.navy_images===15&&JSON.stringify(c.articles)==="[274,280,288,370]","denominator");
ok(c.id_matches===10&&c.subject_only===1&&c.unknown===4,"identity counts");
ok(Array.isArray(a.inputs)&&a.inputs.length===8&&a.inputs.every(x=>x.sha?.length===40&&x.path?.startsWith("qa/media-recovery/parts/")),"source provenance");
ok(Array.isArray(a.rights_policy)&&a.rights_policy.length===3&&a.rights_policy.every(x=>x.startsWith("https://")),"copyright policies");
ok(r.copyright==="ITEM_LEVEL_HOLD"&&r.max_width===960&&r.no_upscale===true&&r.wordpress_writes===false&&r.binary_download===false&&r.external_caching===false,"release gates");
ok(q.broken_42==="NOT_BROWSER_VERIFIED"&&q.transfer_saving_76==="NOT_MEASURED"&&q.production_fixed===0,"claims");
ok(Array.isArray(i)&&i.length===15,"images count");
const seen=new Set(),posts=new Set();let ids=0,subs=0,unknown=0,calculated=0;
const exact={"370:0":"80-G-276907","370:1":"80-G-202485","370:3":"80-G-276940","370:4":"SC-427947","288:0":"NH-69586","280:0":"428-GX-USN-1129207","280:2":"NH-75561","280:3":"K-64683","280:5":"K-64728","274:4":"80-G-344565"};
for(const x of i){if(!x){errors.push("empty row");continue}ok(!seen.has(x.key)&&x.key?.startsWith(x.post_id+":"),"unique keys");seen.add(x.key);posts.add(x.post_id);
ok(x.source_url?.startsWith("https://www.history.navy.mil/")&&x.post_url?.startsWith("https://finalvestige.com/"),"exact source");
ok(typeof x.alt==="string"&&x.alt.length>20,"stored alt");ok(x.browser_http===null&&x.decoded_pixels===null&&x.transferred_bytes===null&&x.visitor_broken===null,"not browser verified");
ok(x.rights==="HOLD"&&x.cache_allowed===false&&x.wp_write_allowed===false&&x.no_upscale===true&&x.max_width===960,"item safeguards");
if(x.identity==="CATALOG_ID_IN_ORIGINAL"){ids++;ok(exact[x.key]===x.catalog_id,"registered catalog ID");const clean=t=>decodeURIComponent(t).toUpperCase().replace(/[^A-Z0-9]/g,"");ok(clean(x.source_url).includes(clean(x.catalog_id)),"ID embedded");}
else if(x.identity==="SUBJECT_ONLY"){subs++;ok(x.key==="274:1"&&x.catalog_id==="80-G-227987","subject only");}
else if(x.identity==="NOT_YET_MAPPED"){unknown++;ok(x.catalog_id===null&&x.catalog_url===null&&x.catalog_note===null,"pending stays null");}else errors.push("invalid identity");
if(x.catalog_id!==null)ok(x.catalog_url?.startsWith("https://www.history.navy.mil/"),"official catalog URL");
if(x.catalog_master){calculated++;const m=x.catalog_master,p=x.conditional_960;ok(m.width>=960&&m.height>0&&p?.width===960&&p?.height===Math.round(m.height*960/m.width)&&p.basis==="CATALOG_MASTER_ONLY_NOT_RENDERED","no-upscale conditional preview");}
else ok(x.conditional_960===null,"null when no master");
}
ok(seen.size===15&&posts.size===4&&ids===10&&subs===1&&unknown===4&&calculated===9,"coverage");
return {ok:errors.length===0,errors,metrics:{navy_sources:seen.size,verified_catalog_ids:ids,subject_candidates:subs,unmapped:unknown,conditional_geometry:calculated}};
};
module.exports={validate};
if(require.main===module){const fs=require('node:fs');const a=JSON.parse(fs.readFileSync(process.argv[2]||'qa/media-recovery/navy_15_primary_catalog_20261106.json','utf8'));const r=validate(a);console.log(JSON.stringify(r,null,2));if(!r.ok)process.exitCode=1;}
