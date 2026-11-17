'use strict';
const fs=require('node:fs');
const KEYS=["285:2","285:5","287:5","407:1","418:1","418:2","287:0","287:3","418:5"];
const stop=s=>{throw Error('HOLD: '+s)};
const url=s=>s===null||(typeof s==='string'&&/^https:\/\/[^\s/@]+(?:\/|$)/.test(s));
function validate(d){
 if(!d||d.schema!=='fv-media-official-p0-triage-v1'||d.prior_audit_blob!=='71924f0c656c520786ade4d49a59b0dd2fbc5d0c')stop('source pin');
 if(d.claimed_42_broken_verified!==false||d.claimed_76_percent_measured!==false||d.production_writes!==0||d.downloaded_media!==0||d.spent_usd!==0)stop('unsupported claim or unsafe write');
 if(!Array.isArray(d.records)||d.records.length!==9||d.records.some((r,i)=>r.key!==KEYS[i]))stop('priority image slots');
 let n=0;
 for(let i=0;i<d.records.length;i++){const r=d.records[i];
   if(r.priority!==(i<6?'P0':'P1')||!url(r.view_url)||!r.view_url||r.guest_status!==null||r.guest_broken!==null||Object.values(r.permissions).some(Boolean))stop('visitor evidence or permissions');
   if(r.candidate){n++;const c=r.candidate;
     if(!['Florida Memory','US Coast Guard','US Geological Survey'].includes(c.archive)||!c.id||!url(c.official_catalog)||!c.official_catalog||!url(c.source_file)||!c.relation||!c.rights)stop('catalog evidence');
     if(c.identity_verified!==false||c.item_rights_cleared!==false||c.max_width!==960||c.no_upscale!==true)stop('item rights and image identity');
     if(c.native_px===null){if(c.review_px!==null)stop('native dimensions unknown')}
     else {const p=c.native_px,q=c.review_px;
       if(!Array.isArray(p)||!Array.isArray(q)||p.length!==2||q.length!==2||![...p,...q].every(v=>Number.isSafeInteger(v)&&v>0))stop('invalid image geometry');
       const width=Math.min(p[0],960),height=Math.max(1,Math.round(p[1]*width/p[0]));
       if(q[0]!==width||q[1]!==height)stop('distorted/upscaled derivative');
     }
   }
 }
 if(n!==4)stop('candidate count');
 return {result:'HOLD_QA_ONLY',p0_slots:6,other_slots:3,archive_slot_candidates:n};
}
if(require.main===module){try{if(process.argv.length!==3)stop('usage: validator file.json');console.log(JSON.stringify(validate(JSON.parse(fs.readFileSync(process.argv[2],'utf8')))))}catch(e){console.error(e.message);process.exitCode=2}}
module.exports={validate};
