'use strict';
/** Read-only local CLI. RELEASE requires the immutable 61/355 source ledger. Usage: node qa/media-recovery/cli_weight_claim_pair_gate_20261102.cjs --before path --after path [--approvals path] */
const fs=require('node:fs');
const {assessFrozenPair}=require('./frozen_census_claim_gate_20261102.cjs');
function parse(argv){
 const out={};const allow=new Set(['--before','--after','--approvals']);
 for(let i=0;i<argv.length;i+=2){
  if(!allow.has(argv[i])||!argv[i+1]||argv[i+1].startsWith('--')||out[argv[i]])throw Error('Invalid flag/value: '+String(argv[i]));
  out[argv[i]]=argv[i+1];
 }
 if(!out['--before']||!out['--after'])throw Error('Required: --before <browser-audit.json> --after <browser-audit.json>');
 return out;
}
function run(argv){
 const args=parse(argv);
 const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
 return assessFrozenPair(read(args['--before']),read(args['--after']),args['--approvals']?read(args['--approvals']):[]);
}
if(require.main===module){
 try{
  const result=run(process.argv.slice(2));
  console.log(JSON.stringify(result,null,2));
  if(result.status!=='MEASURED')process.exitCode=2;
 }catch(e){console.error(JSON.stringify({status:'NOT_MEASURED',error:String(e.message||e),savings_percent:null}));
  process.exitCode=2}
}
module.exports={parse,run};
