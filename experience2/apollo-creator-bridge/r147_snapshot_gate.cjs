'use strict';
/** R147: fail-closed provenance for offline WordPress raw-content review, NOT live acceptance. */
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {prepare}=require('./r145_review_preview_cli.cjs');
const BASELINE=Object.freeze({
 id:2017,slug:'apollo-1-evidence-atlas',status:'publish',modified:'2026-11-04T17:09:24',
 link:'https://finalvestige.com/apollo-1-evidence-atlas/',
 rawCharacters:96274,repairedCharacters:96275,
 rawSha256:'cdaca5ae9d10534a067a8f4095a1362eb1078af48694238860d7f470233849bc',
 repairedSha256:'39dd5adcfe1a4ad1d501a1a94d760b1037111a487908698e649ecaa5103334e7'
});
function digest(s){return crypto.createHash('sha256').update(s,'utf8').digest('hex');}
function auditMetadata(m,base=BASELINE){
 if(!m||typeof m!=='object'||Array.isArray(m))return ['MISSING_INDEPENDENT_WP_METADATA'];
 const errors=[];
 for(const k of ['id','slug','status','modified','link'])
  if(m[k]!==base[k])errors.push('WP_'+k.toUpperCase()+'_DRIFT');
 if(m.source!=='WORDPRESS_AUTHORIZED_READ')errors.push('UNTRUSTED_EXPORT_PROVENANCE');
 return errors;
}
function inspect({html,metadata,baseline=BASELINE,previewFn=prepare,hashFn=digest}){
 const blockers=auditMetadata(metadata,baseline);
 if(typeof html!=='string'||html.length===0)blockers.push('SOURCE_CONTENT_ABSENT');
 const inputSha=typeof html==='string'?hashFn(html):null;
 if(typeof html==='string'&&html.length!==baseline.rawCharacters)blockers.push('SOURCE_CHARACTER_COUNT_DRIFT');
 if(inputSha!==baseline.rawSha256)blockers.push('SOURCE_DIGEST_DRIFT');
 const receipt={
  schema:'fv.apollo.r147.published-snapshot-custody.v1',
  wordpress:{id:baseline.id,slug:baseline.slug,modified:baseline.modified,link:baseline.link},
  input_sha256:inputSha,expected_input_sha256:baseline.rawSha256,
  source_scope:'RAW_GUTENBERG_CONTENT_NOT_RENDERED_WORDPRESS_THEME',
  network:'NOT_USED',browser:'NOT_EXECUTED',axe:'NOT_EXECUTED',
  production_lcp_cls:'NOT_MEASURED',rights:'NOT_CLEARED_FOR_PRODUCT',
  merchant:'NOT_VERIFIED',sales:'NOT_OBSERVED',release:'STAGING_HOLD',approved_to_publish:false
 };
 if(blockers.length)return {ok:false,blockers,receipt:{...receipt,status:'SOURCE_HOLD'}};
 let review;
 try{review=previewFn(html);}catch(e){
  blockers.push('EXISTING_R145_REPAIR_GATE_FAILED');
  return {ok:false,blockers,receipt:{...receipt,status:'SOURCE_HOLD',repair_error:String(e.message||e).slice(0,140)}};
 }
 const rendered=review?.html,patchedSha=typeof rendered==='string'?hashFn(rendered):null;
 if(typeof rendered!=='string'||rendered.length!==baseline.repairedCharacters)blockers.push('REVIEW_CHARACTER_COUNT_DRIFT');
 if(patchedSha!==baseline.repairedSha256)blockers.push('REVIEW_DIGEST_DRIFT');
 if(review?.manifest?.release!=='STAGING_HOLD'||review?.manifest?.approved_to_publish!==false)
  blockers.push('STAGING_GOVERNANCE_RECEIPT_MISSING');
 if(blockers.length)return {ok:false,blockers,receipt:{...receipt,status:'REVIEW_HOLD',review_sha256:patchedSha}};
 return {ok:true,blockers:[],html:rendered,receipt:{...receipt,
  status:'SOURCE_SNAPSHOT_MATCH_OFFLINE_QA_PENDING',review_sha256:patchedSha,
  review_characters:rendered.length,source_records:review.manifest.source_records_verified,
  selected_action:'READ_FULL_INVESTIGATION',historical_image_use:'EDITORIAL_ONLY_REVIEW_REQUIRED',
  browser_runner:'r146_offline_browser_acceptance.py'}};
}
function regular(p){const s=fs.lstatSync(p);if(!s.isFile()||s.isSymbolicLink())throw Error('STAGING_HOLD INPUT_NOT_REGULAR_FILE');}
function writeReview(input,metadataPath,outDir){
 const file=path.resolve(input),meta=path.resolve(metadataPath),out=path.resolve(outDir);
 if(file===meta)throw Error('STAGING_HOLD SOURCE_AND_METADATA_NOT_DISTINCT');
 regular(file);regular(meta);
 if(fs.existsSync(out))throw Error('STAGING_HOLD OUTPUT_ALREADY_EXISTS');
 const result=inspect({html:fs.readFileSync(file,'utf8'),metadata:JSON.parse(fs.readFileSync(meta,'utf8'))});
 if(!result.ok)throw Error('STAGING_HOLD '+result.blockers.join(','));
 fs.mkdirSync(out,{recursive:false});
 const artifact=path.join(out,'apollo-r147-offline-review.html'),manifest=path.join(out,'r147_source_receipt.json');
 fs.writeFileSync(artifact,result.html,{flag:'wx',encoding:'utf8'});
 fs.writeFileSync(manifest,JSON.stringify(result.receipt,null,2)+'\n',{flag:'wx',encoding:'utf8'});
 return {artifact,manifest,receipt:result.receipt};
}
if(require.main===module){
 const args=process.argv,flag=k=>args.indexOf(k),a=flag('--input'),b=flag('--metadata'),c=flag('--out');
 if(a<0||b<0||c<0||!args[a+1]||!args[b+1]||!args[c+1]){
  console.error('Usage: node r147_snapshot_gate.cjs --input RAW_WP_CONTENT.html --metadata WP_METADATA.json --out NEW_DIR');process.exitCode=64;
 }else try{console.log(JSON.stringify(writeReview(args[a+1],args[b+1],args[c+1]),null,2));}
 catch(e){console.error(String(e.message||e));process.exitCode=2;}
}
module.exports={BASELINE,auditMetadata,inspect,writeReview,digest};
