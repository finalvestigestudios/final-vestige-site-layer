"use strict";
function fail(code){throw Error("FV_HOLD:"+code);}
function unpack(o){const x=o && (o.structuredContent?.data||o.data||o.result?.data||o.result||o);if(!x||typeof x.content!=="string")fail("CONTENT_REQUIRED");return x;}
function num(s,re){return (s.match(re)||[]).length;}
function links(s){return [...s.matchAll(/<a[^>]*href=["']([^"']+)["']/gi)].map(m=>m[1]);}
function audit(input){
  const checks=[];const blocked=[];
  const check=(name,pass,detail)=>{checks.push({name,pass:!!pass,detail});if(!pass)blocked.push(name);};
  const specs=[["home",6],["focus",1579],["dispatch",523]];
  const doc={};
  for(const [name,id] of specs){
    const e=unpack(input[name+"Edit"]),v=unpack(input[name+"View"]);
    doc[name]=e;
    check(name+":identity",e.id===id&&v.id===id&&e.status==="publish"&&v.status==="publish","both WordPress contexts are published");
    check(name+":editor_native_jetpack",num(e.content,/<!-- wp:jetpack\/subscriptions/g)===1,"one native block in authenticated editor content");
    const fallback=v.content.includes("post_type=page")&&v.content.includes("wp-block-jetpack-subscriptions");
    const noForm=num(v.content,/<form[\s>]/gi)===0&&num(v.content,/<input[^>]*type=["']email["']/gi)===0;
    check(name+":rest_fallback_documented",fallback&&noForm,"REST fallback observed, not front-end evidence");
  }
  check("home:72_margins",num(doc.home.content,/class=["']fv-margin-strip__item["']/g)===72,"72 authored records retained");
  check("home:focus_entry",links(doc.home.content).some(x=>x==="/focus/"||x==="https://finalvestige.com/focus/"),"home offers Focus");
  check("focus:pdf_link",doc.focus.content.includes("Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf"),"52-page asset destination");
  check("focus:consent",doc.focus.content.includes("privacy-policy")&&doc.focus.content.includes("The Dispatch"),"privacy and list disclosure");
  check("dispatch:focus_entry",links(doc.dispatch.content).some(x=>x==="/focus/"),"Dispatch returns to Focus");
  const fakeSuccess=/URLSearchParams\(window\.location\.search\)/.test(doc.focus.content)&&/if\(q\)\{if\(bad\.indexOf\(q\)<0\)\{show\(\)/.test(doc.focus.content);
  check("focus:no_query_based_gift_success",!fakeSuccess,"draft PR #1681 addresses the existing false-success path");
  if(!input.hostedAnonymousBrowser)blocked.push("HOSTED_BROWSER_FORM_NOT_VERIFIED");
  else blocked.push("INDEPENDENT_BROWSER_RECEIPT_REVIEW_REQUIRED");
  return {decision:"HOLD",scope:"WordPress edit/view snapshots, NOT browser",checks,blocked:[...new Set(blocked)],restFallbackObserved:[6,1579,523].filter((id,i)=>checks.some(c=>c.name===specs[i][0]+":rest_fallback_documented"&&c.pass)),productionWrites:0,subscriberSubmissions:0,confirmedPaidOrders:0};
}
if(typeof module!=="undefined")module.exports={audit};
if(typeof require!=="undefined"&&require.main===module){
 const fs=require("node:fs");
 if(process.argv.length!==8){console.error("Usage: node audit_live_optin_context.cjs homeEdit.json homeView.json focusEdit.json focusView.json dispatchEdit.json dispatchView.json");process.exit(2);}
 try{const names=["homeEdit","homeView","focusEdit","focusView","dispatchEdit","dispatchView"];const d={};names.forEach((n,i)=>d[n]=JSON.parse(fs.readFileSync(process.argv[2+i],"utf8")));const result=audit(d);console.log(JSON.stringify(result,null,2));process.exit(2);}catch(e){console.error(e.message);process.exit(2);}
}
