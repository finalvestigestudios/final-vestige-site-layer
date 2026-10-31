'use strict';
function parseUtc(v) {
 if (typeof v !== 'string') return null;
 if (/^\d{4}-\d\d-\d\d \d\d:\d\d:\d\d$/.test(v)) v=v.replace(' ','T')+'Z';
 if (!/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?(?:Z|[+-]\d\d:\d\d)$/.test(v)) return null;
 const time=Date.parse(v); return Number.isFinite(time)?time:null;
}
function assess(snapshot,{asOf,maxHours=24}={}){
 if (!snapshot || typeof snapshot!=='object' || Array.isArray(snapshot)) throw Error('JSON object required');
 if (!Number.isFinite(maxHours)||maxHours<=0)throw Error('Invalid maxHours');
 const now=parseUtc(asOf||new Date().toISOString());if(now===null)throw Error('asOf must have timezone');
 const b=(snapshot.backup||snapshot).backups||{};
 const findings=[];const add=(code,level,evidence)=>findings.push({code,level,evidence});
 if(b.last_attempt_failed===true)add('FAILED_ATTEMPT','P0',String(b.last_attempt_status||'failed'));
 else if(b.last_attempt_failed!==false)add('ATTEMPT_UNKNOWN','UNKNOWN','Missing last_attempt_failed boolean');
 if(b.backup_in_progress===true)add('IN_PROGRESS','INFO','Do not treat as successful recovery');
 const last=parseUtc(b.last_backup_when);
 let age_hours=null;
 if(last===null)add('SUCCESS_TIMESTAMP_MISSING','UNKNOWN','No parseable last_backup_when');
 else if(last>now)add('CLOCK_CONFLICT','UNKNOWN','Last success is after asOf');
 else {
  age_hours=Number(((now-last)/3600000).toFixed(2));
  if(age_hours>maxHours)add('OLD_RECOVERY_POINT','REVIEW',age_hours+' hours since last successful point');
  const changes=(Array.isArray(snapshot.activities)?snapshot.activities:[])
   .filter(e=>e&&typeof e.name==='string'&&/^(post|plugin|theme|setting|menu|widget)__/.test(e.name)&&/(updated|published|changed_|deleted|trashed|created|activated|deactivated|installed)/.test(e.name))
   .map(e=>({name:e.name,time:parseUtc(e.date)}))
   .filter(e=>e.time!==null&&e.time>last&&e.time<=now)
   .sort((a,b)=>b.time-a.time);
  if(changes.length)add('WRITES_SINCE_RECOVERY_POINT','REVIEW',
    changes.length+' writes; latest '+changes[0].name+' '+new Date(changes[0].time).toISOString());
 }
 const status=findings.some(f=>f.level==='P0')?'ATTENTION':findings.some(f=>f.level==='UNKNOWN')?'UNKNOWN':findings.some(f=>f.level==='REVIEW')?'REVIEW':'NO_ALERTS_IN_SNAPSHOT';
 return {status,age_hours,as_of:new Date(now).toISOString(),findings};
}
module.exports={assess,parseUtc};
if(require.main===module){
 const fs=require('node:fs'),args=process.argv.slice(2);
 try {
  if(!args[0])throw Error('Usage: node guard.cjs snapshot.json [--as-of ISO8601] [--max-hours 24]');
  const i=args.indexOf('--as-of'),j=args.indexOf('--max-hours');
  const result=assess(JSON.parse(fs.readFileSync(args[0],'utf8')),{asOf:i<0?undefined:args[i+1],maxHours:j<0?24:Number(args[j+1])});
  process.stdout.write(JSON.stringify(result,null,2)+'\n');if(result.status==='ATTENTION')process.exitCode=1;
 }catch(e){process.stderr.write(String(e.message)+'\n');process.exitCode=2;}
}