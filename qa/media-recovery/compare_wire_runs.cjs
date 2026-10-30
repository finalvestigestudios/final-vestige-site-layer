'use strict';
const fs=require('node:fs'),{compareWireRuns}=require('./compare_wire_core.cjs');
if(require.main===module)try{
 const a=process.argv.slice(2);
 if(a.length!==2)throw Error('Usage: node qa/media-recovery/compare_wire_runs.cjs before.json after.json');
 const load=f=>{if(fs.statSync(f).size>25*1024*1024)throw Error('Overlarge audit report');return JSON.parse(fs.readFileSync(f,'utf8'))};
 const r=compareWireRuns(load(a[0]),load(a[1]));
 console.log(JSON.stringify(r,null,2));if(!r.comparable)process.exitCode=2;
}catch(e){console.error('NOT_COMPARABLE: '+e.message);process.exitCode=2}

