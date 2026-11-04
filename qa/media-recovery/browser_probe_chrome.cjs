'use strict';
/** Browser proof harness, read-only. Node >=22; installed Chromium; no npm packages. */
const fs=require('node:fs'),os=require('node:os'),path=require('node:path');
const {spawn}=require('node:child_process');
const {loadSnapshot}=require('./validate_inventory.cjs');
const {classifyImages,pageHostVerified,countTransfer}=require('./browser_probe_core.cjs');
const {scopeByRequestId}=require('./request_id_wire_core.cjs');
const {selectCdpImageRequests}=require('./cdp_image_request_scope.cjs');
const {selectScreenshotTarget}=require('./screenshot_target_core.cjs');
const {MAX_STEPS,nextScrollTarget,evaluateCoverage}=require('./scroll_coverage_core.cjs');
const {assessPage,assessRun}=require('./image_census_coverage_core.cjs');
const {DOCUMENT_START_SCRIPT,READ_EXPRESSION,interpretVisualLab}=require('./lab_visual_metrics_20261104.cjs');
const {buildPriorityPlan}=require('./probe_p0_queue_core.cjs');
const auditedReleaseQueue=require('./p0_restoration_release_queue_20261101.json');
const nap=ms=>new Promise(done=>setTimeout(done,ms)),now=()=>new Date().toISOString();
function plan(snapshot,all){
 const posts=snapshot.parts.flatMap(x=>x.posts),images=snapshot.parts.flatMap(x=>x.images);
 const priority=buildPriorityPlan(snapshot,auditedReleaseQueue);
 return (all?posts.map(p=>p.id):priority.post_ids).map(id=>{
  const p=posts.find(v=>v.id===id);if(!p)throw Error('Missing post '+id);
  if(new URL(p.url).hostname!=='finalvestige.com')throw Error('Offsite page refused '+p.url);
  return {id,url:p.url,title:p.title,stored:images.filter(v=>v.post_id===id),
   priority_image_keys:priority.priority_targets.filter(t=>t.post_id===id).map(t=>t.image_key),
   priority_targets:priority.priority_targets.filter(t=>t.post_id===id)};
 });
}
class CDP{
 constructor(ws){
  this.ws=ws;this.next=1;this.pending=new Map();this.handlers=new Set();
  ws.addEventListener('message',event=>{
   let msg;try{msg=JSON.parse(event.data)}catch{return}
   if(msg.id){const r=this.pending.get(msg.id);if(r){this.pending.delete(msg.id);msg.error?r.reject(Error(msg.error.message)):r.resolve(msg.result||{})}return}
   for(const fn of this.handlers)fn(msg);
  });
 }
 on(fn){this.handlers.add(fn);return()=>this.handlers.delete(fn)}
 send(method,params={},timeout=12000){
  return new Promise((resolve,reject)=>{
   const id=this.next++,timer=setTimeout(()=>{this.pending.delete(id);reject(Error('CDP timeout '+method))},timeout);
   this.pending.set(id,{resolve:v=>{clearTimeout(timer);resolve(v)},reject:e=>{clearTimeout(timer);reject(e)}});
   this.ws.send(JSON.stringify({id,method,params}));
  });
 }
 close(){for(const [,p]of this.pending)p.reject(Error('CDP closed'));this.pending.clear();this.ws.close()}
}
async function launch(){
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'fv-media-'));
 const child=spawn(process.env.CHROMIUM_BIN||'/usr/bin/chromium',
  ['--headless=new','--no-sandbox','--disable-dev-shm-usage','--disable-extensions',
   '--no-first-run','--no-default-browser-check','--disable-background-networking',
   '--remote-debugging-port=0','--user-data-dir='+dir,'about:blank'],{stdio:'ignore'});
 try{
  let port=0;
  for(let i=0;i<80;i++){
   if(child.exitCode!==null)throw Error('Chromium exited before debugging started');
   try{port=Number(fs.readFileSync(path.join(dir,'DevToolsActivePort'),'utf8').split('\n')[0]);if(port>0)break}catch{}
   await nap(100);
  }
  if(!port)throw Error('Chromium debug port unavailable');
  const pages=await (await fetch('http://127.0.0.1:'+port+'/json/list')).json();
  const page=pages.find(e=>e.type==='page'&&e.webSocketDebuggerUrl);
  if(!page)throw Error('No Chrome page target');
  const ws=new WebSocket(page.webSocketDebuggerUrl);
  await Promise.race([new Promise((resolve,reject)=>{ws.addEventListener('open',resolve,{once:true});ws.addEventListener('error',reject,{once:true})}),nap(5000).then(()=>{throw Error('CDP websocket timeout')})]);
  return{cdp:new CDP(ws),child,dir};
 }catch(e){child.kill('SIGTERM');fs.rmSync(dir,{recursive:true,force:true});throw e}
}
const domScript='('+function(){
 const root=document.querySelector('article')||document.querySelector('main');
 const imgs=[...(root?root.querySelectorAll('img'):document.querySelectorAll('img'))];
 return{url:location.href,title:document.title,hasArticle:!!document.querySelector('article'),
  images:imgs.map((el,i)=>({index:i,alt:el.alt||'',src:el.getAttribute('src')||'',
   currentSrc:el.currentSrc||'',dataSrc:el.getAttribute('data-src')||'',complete:el.complete,
   naturalWidth:el.naturalWidth,naturalHeight:el.naturalHeight,loading:el.loading||'',
   rectWidth:Math.round(el.getBoundingClientRect().width),rectHeight:Math.round(el.getBoundingClientRect().height)})),
  pageHeight:Math.max(document.body.scrollHeight,document.documentElement.scrollHeight)};
}.toString()+')()';
const scrollMetricsScript='({pageHeight:Math.max(document.body.scrollHeight,document.documentElement.scrollHeight),viewportHeight:window.innerHeight,scrollY:window.scrollY})';
async function evaluate(cdp,expr){
 const r=await cdp.send('Runtime.evaluate',{expression:expr,returnByValue:true,awaitPromise:true},15000);
 if(r.exceptionDetails)throw Error('Browser evaluate exception');
 return r.result?.value;
}
function monitor(cdp){
 const reqs=new Map(),docFailures=[];
 const off=cdp.on(m=>{
  const p=m.params||{},id=p.requestId;
  if(m.method==='Network.requestWillBeSent'){
   const old=reqs.get(id)||{url_aliases:[],encodedDataLength:null};
   if(old.url&&old.url!==p.request.url)old.url_aliases.push(old.url);
   const r={...old,request_id:id,url:p.request.url,type:p.type||old.type||null};
   if(p.redirectResponse){r.url_aliases.push(p.redirectResponse.url);r.redirect_status=p.redirectResponse.status}
   reqs.set(id,r);
  }else if(m.method==='Network.responseReceived'){
   const r=reqs.get(id)||{};r.url=p.response.url;r.status=p.response.status;r.mime_type=p.response.mimeType||null;r.type=p.type||r.type||null;r.from_disk_cache=!!p.response.fromDiskCache;r.from_service_worker=!!p.response.fromServiceWorker;reqs.set(id,r);
  }else if(m.method==='Network.requestServedFromCache'){const r=reqs.get(id)||{};r.was_cached=true;reqs.set(id,r);
  }else if(m.method==='Network.loadingFinished'){
   const r=reqs.get(id)||{};r.encodedDataLength=Math.round(p.encodedDataLength||0);reqs.set(id,r);
  }else if(m.method==='Network.loadingFailed'){
   const r=reqs.get(id)||{};r.type=p.type||r.type||null;r.failed_error=p.errorText||'network_load_failed';reqs.set(id,r);
   if(p.type==='Document')docFailures.push({url:r.url||null,error:r.failed_error});
  }
 });
 return{records:()=>[...reqs.values()].map(x=>({...x,url_aliases:[...new Set(x.url_aliases||[])]})),docFailures:()=>docFailures,close:off};
}
async function inspect(cdp,page,outputDir){
 const started=now(),net=monitor(cdp);
 const readVisualLab=async()=>{try{return await evaluate(cdp,READ_EXPRESSION)}catch{return null}};
 try{
  await cdp.send('Page.navigate',{url:page.url},12000);await nap(1800);
  let doc=await evaluate(cdp,domScript),steps=0;
 // Snapshot BEFORE synthetic scrolling: subsequent shifts are diagnostic lab
 // events, not field CLS. Missing browser observer support stays null.
 const firstVisualLab=await readVisualLab();
  let coverage={complete:false,state:'no_article',reason:'article_element_missing'};
  if(doc?.hasArticle){
   let scanError=null;
   try{
    // Re-evaluate height after each step: lazy content can lengthen the page.
    while(steps<MAX_STEPS){
     const metrics=await evaluate(cdp,scrollMetricsScript);
     const next=nextScrollTarget({...metrics,steps});
     if(next===null)break;
     await evaluate(cdp,'window.scrollTo({top:'+next+',behavior:"instant"})');
     steps++;await nap(220);
    }
   }catch(e){scanError=String(e.message||e)}
   await nap(1000);doc=await evaluate(cdp,domScript);
   const endMetrics=await evaluate(cdp,scrollMetricsScript);
   coverage=evaluateCoverage({...endMetrics,steps,scanError});
  }
  const lastVisualLab=await readVisualLab();
  const records=net.records(),fail=net.docFailures();
  const verified=pageHostVerified(page.url,doc?.title,doc?.url,doc?.hasArticle,fail[0]?.error);
  // Only CDP Image resources may certify historical-photo load or failure.
  // XHR/Fetch/Document requests for the same URL must not mask a broken <img>.
  const imageRecords=selectCdpImageRequests(records);
  const images=classifyImages(page.stored,doc?.images||[],imageRecords,verified);
  const networkImages=imageRecords.map(x=>({
   request_id:x.request_id||null,url:x.url,url_aliases:x.url_aliases,status:x.status??null,error:x.failed_error||null,
   mime_type:x.mime_type||null,encoded_data_length:x.encodedDataLength??null,
   from_disk_cache:x.from_disk_cache===true,from_service_worker:x.from_service_worker===true,was_cached:x.was_cached===true}));
  const articleWire=scopeByRequestId(images,networkImages);
  const pageResult=verified?(coverage.complete?'inspected_browser':'inspected_browser_partial_scroll'):'blocked_or_unverified_page';
  const evidence=assessPage({page_result:pageResult,scroll_coverage:coverage,stored_image_count:page.stored.length,stored_images:images});
  const broken=images.filter(x=>x.verified_broken_in_browser===true),screenshots=[];
  // Distinct image slots may share an identical URL. Always use exact DOM index + ALT.
  // Screenshot coverage is independent of the verified browser/network failure count.
  const MAX_SCREENSHOTS_PER_POST=24;
  if(verified){
   for(const bad of broken.slice(0,MAX_SCREENSHOTS_PER_POST)){
    const target=selectScreenshotTarget(bad,doc?.images||[]);
    if(!target.ok){screenshots.push({image_key:bad.image_key,result:'skipped',reason:target.reason});continue}
    try{
     const scrolled=await evaluate(cdp,"(function(){const r=document.querySelector('article')||document.querySelector('main');const e=r?.querySelectorAll('img')["+target.index+"];if(!e)return false;e.scrollIntoView({block:'center'});return true})()");
     if(scrolled!==true){screenshots.push({image_key:bad.image_key,result:'skipped',reason:'dom_target_missing_at_scroll'});continue}
     await nap(150);
     const fresh=await evaluate(cdp,domScript);
     const recheck=selectScreenshotTarget(bad,fresh?.images||[]);
     if(!recheck.ok){screenshots.push({image_key:bad.image_key,result:'skipped',reason:'dom_changed_after_scroll:'+recheck.reason});continue}
     const shot=await cdp.send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false},12000);
     const basename='broken-'+page.id+'-'+bad.image_key.replace(':','-')+'.png';
     fs.writeFileSync(path.join(outputDir,basename),Buffer.from(shot.data,'base64'));
     screenshots.push({image_key:bad.image_key,result:'captured',filename:basename,rendered_index:target.index,current_src:bad.current_src});
    }catch(e){screenshots.push({image_key:bad.image_key,result:'error',reason:String(e.message||e)})}
   }
  }
  return{post_id:page.id,url:page.url,title:page.title,started,completed:now(),
   page_result:pageResult,
   document_url:doc?.url||null,document_title:doc?.title||null,document_network_failures:fail,
   rendered_image_count:doc?.images?.length||0,stored_image_count:page.stored.length,scrolled_steps:steps,scroll_coverage:coverage,
   stored_images:images,screenshots,screenshot_target_count:broken.length,
   screenshot_captured_count:screenshots.filter(x=>x.result==='captured').length,
   screenshot_unattempted_count:Math.max(0,broken.length-MAX_SCREENSHOTS_PER_POST),
   screenshot_limit_per_post:MAX_SCREENSHOTS_PER_POST,
   image_census:evidence,
   visual_lab:interpretVisualLab(firstVisualLab,lastVisualLab,verified),
   known_broken_count:evidence.known_broken_count,
   confirmed_broken_count:evidence.confirmed_broken_count,
   browser_wire_bytes_total:verified&&coverage.complete?countTransfer(records):null,
   image_wire_bytes_total:verified&&coverage.complete?countTransfer(imageRecords):null,
   // Distinguish measured article-photo traffic from unrelated page UI image traffic.
   article_image_wire_bytes_total:verified&&coverage.complete?articleWire.article_bytes:null,
   unattributed_image_wire_bytes_total:verified&&coverage.complete?articleWire.unattributed_bytes:null,
   matched_article_network_requests:verified&&coverage.complete?articleWire.matched_request_count:null,
   article_wire_attribution_mode:articleWire.attribution_mode,
   article_wire_evidence_complete:verified&&coverage.complete?articleWire.complete:false,
   article_wire_evidence_errors:articleWire.reasons,
   unmeasured_article_network_requests:verified&&coverage.complete?articleWire.unmeasured_article_requests:null,
   network_images:networkImages,
   interpretation:verified&&coverage.complete?'Logged-out Chromium reached page bottom, with currentSrc and network evidence; source rights still require review.':verified?'Partial browser scan; do not infer a complete broken-image census or weight baseline.':'Environment or page unverified: no claims of broken images are permitted.'};
 }catch(e){
  return{post_id:page.id,url:page.url,started,completed:now(),page_result:'probe_error',
   error:String(e.message||e),stored_image_count:page.stored.length,stored_images:[],
   visual_lab:interpretVisualLab(null,null,false),
   confirmed_broken_count:null,browser_wire_bytes_total:null,image_wire_bytes_total:null};
 }finally{net.close()}
}
async function main(){
 const args=process.argv.slice(2),all=args.includes('--all'),dry=args.includes('--plan'),desktop=args.includes('--desktop');
 if(args.some(x=>!['--all','--plan','--desktop'].includes(x)))throw Error('Allowed options: --plan, --all, --desktop');
 const pages=plan(loadSnapshot(),all);
 if(dry){console.log(JSON.stringify({mode:all?'all':'priority',page_count:pages.length,
  post_ids:pages.map(x=>x.id),image_sources:pages.reduce((n,p)=>n+p.stored.length,0),
  urls:pages.map(x=>x.url),priority_targets:pages.flatMap(x=>x.priority_targets),browser_probe_executed:false},null,2));return}
 const dir=path.join(__dirname,'runs');fs.mkdirSync(dir,{recursive:true});
 const result={schema_version:1,probe_version:4,created:now(),mode:all?'all':'priority',viewport:desktop?'1440x900':'390x844',
  probe:'logged-out Chrome CDP, no npm dependencies or WordPress writes',
  requested_pages:pages.length,priority_image_keys:pages.flatMap(x=>x.priority_image_keys),status:'starting',pages:[]};
 let browser;
 try{
  browser=await launch();const c=browser.cdp;
  await c.send('Page.enable');await c.send('Network.enable');await c.send('Runtime.enable');
  // Document-start observers see initial LCP/unsized-image shifts. Runtime
  // snapshots after navigation/automated scrolling are NOT real-user CWV.
  await c.send('Page.addScriptToEvaluateOnNewDocument',{source:DOCUMENT_START_SCRIPT});
  await c.send('Network.setCacheDisabled',{cacheDisabled:true});
  await c.send('Network.setBypassServiceWorker',{bypass:true});
  const browserInfo=await c.send('Browser.getVersion',{},12000);
  result.browser_product=browserInfo.product||null;
  result.run_profile={cache_disabled:true,service_worker_bypassed:true,
    scroll_step_px:720,scroll_wait_ms:220,settle_wait_ms:1000,
    document_start_visual_lab_observer:true,field_cwv_claim_permitted:false};
  await c.send('Emulation.setDeviceMetricsOverride',desktop?
   {width:1440,height:900,deviceScaleFactor:1,mobile:false}:
   {width:390,height:844,deviceScaleFactor:2,mobile:true});
  for(const p of pages){
   const r=await inspect(c,p,dir);result.pages.push(r);
   console.error('media '+r.post_id+': '+r.page_result+' / broken='+r.confirmed_broken_count);
  }
  result.status=result.pages.some(x=>x.page_result==='inspected_browser')?'partial_or_complete_browser_evidence':'all_pages_unverified';
 }catch(e){result.status='environment_or_browser_blocked';result.error=String(e.message||e)}
 finally{if(browser){try{browser.cdp.close()}catch{};browser.child.kill('SIGTERM');await nap(150);fs.rmSync(browser.dir,{recursive:true,force:true})}}
 result.finished=now();result.verified_pages=result.pages.filter(x=>x.page_result==='inspected_browser').length;
 result.image_census_coverage=assessRun(result.pages,result.requested_pages);
 result.confirmed_broken_count=result.image_census_coverage.confirmed_broken_count;
 if(result.image_census_coverage.complete)result.status='complete_browser_image_census';
 const filename=path.join(dir,'browser-audit-'+result.created.replace(/\D/g,'').slice(0,14)+'-'+(all?'all':'p0')+'-'+(desktop?'desktop':'mobile')+'.json');
 fs.writeFileSync(filename,JSON.stringify(result,null,2)+'\n');
 console.log(JSON.stringify({output:filename,status:result.status,verified_pages:result.verified_pages,
  known_broken_count:result.image_census_coverage.known_broken_count,unresolved_slots:result.image_census_coverage.unresolved_slot_count,
  confirmed_broken_count:result.confirmed_broken_count}));
 if(!result.image_census_coverage.complete)process.exitCode=2;
}
if(require.main===module)main().catch(e=>{console.error('MEDIA_PROBE_FATAL '+e.stack);process.exitCode=2});
module.exports={plan,inspect,monitor};
