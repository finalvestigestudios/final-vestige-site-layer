'use strict';
/** Read-only upstream query integrity gate. No HTTP/image fetching or WordPress writes. */
function normalizeHTML(s){return String(s).replace(/&#0*38;|&#x0*26;|&amp;/gi,"&");}
function getPairs(url){
 const s=normalizeHTML(url);
 if(!/^https:\/\/[^/?#]+\/[^#]*$/i.test(s))throw Error("invalid_https_url");
 const q=s.indexOf("?"); if(q<0)return [];
 return s.slice(q+1).split("&").map(part=>{
  if(!part)throw Error("empty_query_part");
  const i=part.indexOf("="),k=i<0?part:part.slice(0,i),v=i<0?"":part.slice(i+1);
  const decode=x=>decodeURIComponent(x.replace(/\+/g," "));
  const out=[decode(k),decode(v)];
  if(!out[0])throw Error("empty_query_key");
  return out;
 });
}
function collectRows(first,second){
 if(first?.schema!=="fv-wp-26-edit-view-lineage-v1"||first.rows?.length!==26||second.rows?.length!==42)
   throw Error("unverified_scope");
 const all=[
  ...first.rows.map(x=>({key:x.key,edit:x.edit_source_url,view:x.view_src,mode:x.view_url_mode,post_id:x.post_id})),
  ...second.rows.map(x=>({key:x.key,edit:x.edit_src,view:x.view_src,mode:x.view_mode,post_id:x.post_id}))
 ];
 const seen=new Set();
 const counts={posts:0,slots:all.length,original_query_bearing:0,original_query_absent:0,parameters_preserved:0,parameters_missing:0,flagged_keys:[]};
 const posts=new Set(),query_rows=[];
 for(const r of all){
  if(!/^\d+:\d+$/.test(r.key)||r.key.split(":")[0]!==String(r.post_id)||seen.has(r.key))
    throw Error("duplicate_or_invalid_slot");
  seen.add(r.key);posts.add(r.post_id);
  const origin=getPairs(r.edit),rendered=getPairs(r.view);
  if(!origin.length){counts.original_query_absent++;continue;}
  counts.original_query_bearing++;
  const used=new Set(),missing=[];
  for(const [name,value] of origin){
   let found=-1;
   for(let i=0;i<rendered.length;i++)if(!used.has(i)&&rendered[i][0]===name&&rendered[i][1]===value){found=i;break;}
   if(found===-1)missing.push({name,value});else used.add(found);
  }
  if(missing.length){counts.parameters_missing++;counts.flagged_keys.push(r.key);}
  else counts.parameters_preserved++;
  query_rows.push({key:r.key,post_id:r.post_id,source_mode:r.mode,edit_source_url:r.edit,view_source_url:r.view,origin_query_pairs:origin.map(([name,value])=>({name,value})),missing_query_pairs:missing,query_fidelity:missing.length?"ORIGIN_PARAM_DROPPED":"PRESERVED",guest_current_src:null,guest_http_status:null,jetpack_http_status:null,guest_decode_width:null,guest_transfer_bytes:null,cache_authorized:false,wp_upload_authorized:false,post_rewrite_authorized:false});
 }
 counts.posts=posts.size;counts.flagged_keys.sort();
 if(counts.posts!==10||counts.slots!==68||counts.original_query_bearing!==24||counts.original_query_absent!==44||counts.parameters_preserved!==22||counts.parameters_missing!==2||counts.flagged_keys.join(",")!=="288:5,418:5")throw Error("unexpected_snapshot_delta:"+JSON.stringify(counts));
 return {counts,query_rows};
}
function checkLedger(ledger,first,second){
 const d=collectRows(first,second);
 if(ledger?.schema!=="fv-query-fidelity-68-v1"||
    JSON.stringify(ledger.counts)!==JSON.stringify(d.counts)||
    JSON.stringify(ledger.query_rows)!==JSON.stringify(d.query_rows))throw Error("ledger_source_mismatch");
 const required=["288:5","418:5"];
 if(!Array.isArray(ledger.risk_candidates)||ledger.risk_candidates.length!==2||
    required.some(key=>!ledger.risk_candidates.some(r=>r.key===key)))throw Error("candidate_mapping_missing");
 for(const r of ledger.risk_candidates)if(r.rights_to_rehost_verified!==false||
    r.max_review_width_px!==960||r.native_dimensions_px!==null||r.preview_dimensions_px!==null||
    r.no_upscale!==true||r.cache_authorized!==false||r.wp_upload_authorized!==false||
    r.publication_authorized!==false||r.guest_failure_verified!==false||
    typeof r.official_catalog_url!=="string"||!r.official_catalog_url.startsWith("https://"))
    throw Error("unsafe_candidate");
 if(ledger.claims?.guest_confirmed_broken_count!==null||ledger.claims?.transferred_byte_savings_percent!==null||
   ledger.actions?.wordpress_production_writes!==0||ledger.actions?.media_downloads!==0||
   ledger.actions?.published_block_rewrites!==0||ledger.actions?.production_deploys!==0||
   ledger.actions?.subscription_spend_usd!==0)throw Error("unverified_claim_or_action");
 return true;
}
module.exports={normalizeHTML,getPairs,collectRows,checkLedger};
if(require.main===module){
 const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
 const base=__dirname;
 const sources=['wp_view_proxy_26_20261115.json','wp_view_six_archival_posts_42_slots_20261115.json'];
 const expected=["dcb735226eb71fcba302b38ae3ab3a73751fe2a8","978f1cb9fe3b17d6766ea89668cedb9e94074cb4"];
 const objs=sources.map((name,i)=>{
   const bytes=fs.readFileSync(path.join(base,name));
   const sha=crypto.createHash('sha1').update('blob '+bytes.length+'\0').update(bytes).digest('hex');
   if(sha!==expected[i])throw Error('frozen_source_blob_drift:'+name+':'+sha);
   return JSON.parse(bytes.toString('utf8'));
 });
 const ledger=JSON.parse(fs.readFileSync(path.join(base,'query_token_fidelity_68_20261115.json'),'utf8'));
 checkLedger(ledger,objs[0],objs[1]);
 process.stdout.write('PASS 68 source/view slots, 24 query-bearing, 2 missing itok tokens, 0 guest statuses\n');
}
