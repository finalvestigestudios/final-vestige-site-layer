"use strict";
/*
 * Final Vestige Mind R23: OFFLINE, NON-DEPLOYABLE, COARSE COUNTER MODEL.
 * No collection endpoint, network, pixel, cookies, storage, or runtime page import.
 * Reject raw referrers, identifiers and unknown fields; publishing suppresses thin cells.
 * Run node mind/troxler-fading-r23/privacy-aggregate-OFF.cjs --selftest
 */
const ENABLED=false;
const variantSet=new Set(["A","B"]),sourceSet=new Set(["direct","internal","organic","social","other"]),kindSet=new Set(["presentation","approved_outbound_click"]);
const allowedKeys=["kind","period","source","variant"];
function guard(event){
 if(!event||typeof event!=="object"||Array.isArray(event))throw new Error("Event must be object");
 const keys=Object.keys(event).sort();if(keys.join("|")!==allowedKeys.slice().sort().join("|"))throw new Error("Unknown or missing fields; refuse PII");
 if(!variantSet.has(event.variant)||!sourceSet.has(event.source)||!kindSet.has(event.kind))throw new Error("Invalid coarse category");
 if(!/^20\d{2}-W(?:0[1-9]|[1-4]\d|5[0-3])$/.test(event.period))throw new Error("Period must be coarse ISO week");
 return [event.period,event.variant,event.source,event.kind].join("|");
}
function aggregateOfflineSyntheticEvents(events){
 if(!Array.isArray(events)||events.length>10000)throw new Error("Use a bounded local synthetic event array");
 const count=new Map();for(const event of events){const k=guard(event);count.set(k,(count.get(k)||0)+1)}
 return [...count].map(([key,n])=>({key,count:n})).sort((a,b)=>a.key.localeCompare(b.key));
}
function safeReport(cells,minimum=20){
 if(!Number.isInteger(minimum)||minimum<20)throw new Error("At least 20 required for public cell");
 return cells.map(c=>({key:c.key,count:c.count>=minimum?c.count:null,suppressed:c.count<minimum}));
}
function selftest(){
 let n=0;const ok=(cond,label)=>{n++;if(!cond)throw new Error(label)};
 const e=()=>({kind:"presentation",period:"2026-W44",source:"organic",variant:"A"});
 ok(ENABLED===false,"Should never enable itself");
 ok(guard(e())==="2026-W44|A|organic|presentation","Stable categorization");
 for(const key of ["ip","email","raw_referrer","click_id","utm","user_agent","visitor_id","url","time","name"]){let caught=false;try{guard({...e(),[key]:"private"})}catch(_){caught=true}ok(caught,"Reject "+key)}
 for(const field of ["kind","period","source","variant"]){const q=e();delete q[field];let caught=false;try{guard(q)}catch(_){caught=true}ok(caught,"Missing "+field)}
 const invalid=[{...e(),source:"exact search query"},{...e(),variant:"C"},{...e(),kind:"sale"},{...e(),period:"2026-10-31"},{...e(),period:"2026-W88"}];
 for(const q of invalid){let caught=false;try{guard(q)}catch(_){caught=true}ok(caught,"Reject invalid category")}
 let cells=aggregateOfflineSyntheticEvents([e(),e(),{...e(),kind:"approved_outbound_click"}]);
 ok(cells.length===2&&cells[0].count+cells[1].count===3,"Aggregate count");
 const report=safeReport(cells);ok(report.every(x=>x.suppressed&&x.count===null),"Suppress thin cells");
 let caught=false;try{safeReport(cells,1)}catch(_){caught=true}ok(caught,"No easy suppression bypass");
 ok(!Object.keys(module.exports).includes("track")&&!Object.keys(module.exports).includes("send"),"No live tracking API");
 return {tests:n,passed:n,enabled:ENABLED,storage:"none",network:"none"};
}
module.exports={ENABLED,guard,aggregateOfflineSyntheticEvents,safeReport,selftest};
if(require.main===module){if(process.argv.includes("--selftest"))console.log(JSON.stringify(selftest(),null,2));else console.log("OFF: no event collection or network, run --selftest for synthetic tests");}
