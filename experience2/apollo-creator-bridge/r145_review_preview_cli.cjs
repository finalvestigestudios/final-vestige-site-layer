'use strict';
/**
 * R145 staging-only HTML artifact builder: one audited selector repair from an
 * explicitly supplied, read-only WordPress HTML export. Absolutely no network,
 * WordPress, analytics, merchant, deployment or GitHub writes.
 *
 * node r145_review_preview_cli.cjs --input /path/to/atlas-source.html --out /tmp/apollo-r145
 */
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {audit}=require('./r145_semantic_gallery_custody.cjs');
const {prepareGalleryRepair}=require('./r143_gallery_source_repair.cjs');
const sha256=s=>crypto.createHash('sha256').update(s).digest('hex');
const EXPECTED='PUBLISHED_GALLERY_ENHANCEMENT_DEFECT';
function prepare(html){
 if(typeof html!=='string')throw new TypeError('Explicit HTML string required');
 const before=audit(html);
 // This is NOT a generic CMS patcher: it only accepts the one source-backed defect.
 if(before.blockers.length!==1||before.blockers[0]!==EXPECTED)
   throw new Error('STAGING_HOLD SOURCE_NOT_SINGLE_KNOWN_GALLERY_DEFECT '+before.blockers.join(','));
 const repaired=prepareGalleryRepair(html);
 const after=audit(repaired.output);
 if(after.blockers.length)throw new Error('STAGING_HOLD POSTPATCH '+after.blockers.join(','));
 if(repaired.output.length!==html.length+1 ||
   repaired.receipt.changedCharacters!==1)
   throw new Error('STAGING_HOLD INTEGRITY_NOT_ONE_CHARACTER');
 const manifest={
   schema:'fv.apollo.r145.review-artifact.v1',
   source_sha256:sha256(html),
   review_html_sha256:sha256(repaired.output),
   source_characters:html.length,
   review_characters:repaired.output.length,
   change:'ONE_ADDED_DOLLAR_IN_PUBLISHED_GALLERY_SELECTOR',
   preflight:before.sourceGate,
   after_source_gate:after.sourceGate,
   source_records_verified:after.findings.sourceRecordCount,
   selected_next_action:'EXISTING_READ_FULL_INVESTIGATION',
   gallery_rights:'NOT_APPROVED_FOR_COMMERCIAL_REUSE',
   browser:'NOT_TESTED',
   axe:'NOT_TESTED',
   lcp_cls:'NOT_MEASURED',
   merchant:'NOT_VERIFIED',
   attributed_sales:'NOT_OBSERVED',
   release:'STAGING_HOLD',
   approved_to_publish:false
 };
 return Object.freeze({html:repaired.output,manifest:Object.freeze(manifest)});
}
function writeReview(inputPath,outDir){
 const input=path.resolve(inputPath),folder=path.resolve(outDir);
 if(!fs.statSync(input).isFile())throw new Error('Input must be a regular read-only HTML export');
 const html=fs.readFileSync(input,'utf8');
 const artifact=prepare(html);
 const outHTML=path.join(folder,'apollo-r145-local-review.html');
 const outJSON=path.join(folder,'apollo-r145-manifest.json');
 if(outHTML===input||outJSON===input)throw new Error('Output cannot overwrite original export');
 fs.mkdirSync(folder,{recursive:true});
 fs.writeFileSync(outHTML,artifact.html,'utf8');
 fs.writeFileSync(outJSON,JSON.stringify(artifact.manifest,null,2)+'\n','utf8');
 return {manifest:artifact.manifest,paths:[outHTML,outJSON]};
}
if(require.main===module){
 const args=process.argv,where=k=>args.indexOf(k);
 const i=where('--input'),o=where('--out');
 if(i<0||o<0||!args[i+1]||!args[o+1]){
   console.error('Usage: node r145_review_preview_cli.cjs --input READ_ONLY_HTML --out LOCAL_REVIEW_DIR');
   process.exitCode=64;
 }else{
   try{
     const result=writeReview(args[i+1],args[o+1]);
     process.stdout.write(JSON.stringify(result,null,2)+'\n');
   }catch(err){
     console.error(String(err.message||err));
     process.exitCode=2;
   }
 }
}
module.exports={prepare,writeReview};
