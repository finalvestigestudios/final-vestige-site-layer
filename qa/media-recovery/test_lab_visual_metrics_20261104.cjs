'use strict';
const assert=require('node:assert/strict');
const vm=require('node:vm');
const {test}=require('node:test');
const {DOCUMENT_START_SCRIPT,READ_EXPRESSION,interpretVisualLab}=require('./lab_visual_metrics_20261104.cjs');
function harness(unsupported=[]){
 const handlers=new Map(),window={};
 class Observer{
  constructor(cb){this.cb=cb}
  observe(options){if(unsupported.includes(options.type))throw Error('unsupported');handlers.set(options.type,this.cb)}
 }
 const context=vm.createContext({window,PerformanceObserver:Observer,Number,Math,String,Object});
 const inject=()=>vm.runInContext(DOCUMENT_START_SCRIPT,context);
 const read=()=>vm.runInContext(READ_EXPRESSION,context);
 const emit=(kind,entries)=>handlers.get(kind)({getEntries:()=>entries});
 return {window,handlers,inject,read,emit};
}
test('document-start observers supported; no fabricated LCP',()=>{
 const h=harness();h.inject();const s=h.read();
 assert.equal(s.version,1);assert.equal(s.layout_shift_score,0);
 assert.equal(s.layout_shift_supported,true);assert.equal(s.largest_contentful_paint_supported,true);
 assert.equal(s.largest_contentful_paint,null);
});
test('ignore recent input shifts; only retain tag name not text',()=>{
 const h=harness();h.inject();
 h.emit('layout-shift',[
  {value:.12,hadRecentInput:false,startTime:101.2,sources:[{node:{tagName:'IMG',innerText:'private'}}]},
  {value:.9,hadRecentInput:true,startTime:200,sources:[]},
  {value:.03,hadRecentInput:false,startTime:300,sources:[]}]);
 const s=h.read();assert.equal(s.layout_shift_score,.15);
 assert.equal(s.qualifying_layout_shift_events,2);assert.equal(s.excluded_recent_input_events,1);
 assert.equal(s.layout_shift_samples[0].affected_element_tags[0],'img');
 assert.doesNotMatch(JSON.stringify(s),/private/);
});
test('LCP last entry wins and no resource URLs collected',()=>{
 const h=harness();h.inject();
 h.emit('largest-contentful-paint',[
  {startTime:620,size:4000,element:{tagName:'H1'}},
  {startTime:750.4,size:18000,element:{tagName:'IMG',src:'https://example.com/private'}}]);
 const s=h.read().largest_contentful_paint;
 assert.equal(s.start_time_ms,750);assert.equal(s.element_tag,'img');
 assert.equal(s.element_is_image,true);assert.equal(s.size_px2,18000);
 assert.doesNotMatch(JSON.stringify(s),/private/);
});
test('missing PerformanceObserver leaves unknown scores null',()=>{
 const ctx=vm.createContext({window:{},Number,Math,String,Object});
 vm.runInContext(DOCUMENT_START_SCRIPT,ctx);
 const s=vm.runInContext(READ_EXPRESSION,ctx);
 assert.equal(s.layout_shift_supported,false);assert.equal(s.layout_shift_score,null);
 assert.equal(s.largest_contentful_paint_supported,false);
});
test('partially unsupported browser retains null for missing observer',()=>{
 const h=harness(['layout-shift']);h.inject();
 assert.equal(h.read().layout_shift_score,null);
 assert.equal(h.read().largest_contentful_paint_supported,true);
});
test('repeat injection cannot erase shifts',()=>{
 const h=harness();h.inject();h.emit('layout-shift',[{value:.25,hadRecentInput:false,startTime:1,sources:[]}]);
 h.inject();assert.equal(h.read().layout_shift_score,.25);
});
test('sample cap 20 while all qualifying shifts counted',()=>{
 const h=harness();h.inject();
 h.emit('layout-shift',Array.from({length:31},(_,i)=>({value:.01,hadRecentInput:false,startTime:i,sources:[]})));
 assert.equal(h.read().qualifying_layout_shift_events,31);
 assert.equal(h.read().layout_shift_samples.length,20);
});
test('read returns immutable snapshot values across later events',()=>{
 const h=harness();h.inject();const a=h.read();
 h.emit('layout-shift',[{value:.4,hadRecentInput:false,startTime:2,sources:[]}]);
 assert.equal(a.layout_shift_score,0);assert.equal(h.read().layout_shift_score,.4);
});
test('unverified document cannot claim visual metrics',()=>{
 const h=harness();h.inject();const v=interpretVisualLab(h.read(),h.read(),false);
 assert.equal(v.state,'UNVERIFIED');assert.equal(v.after_navigation,null);
 assert.equal(v.field_cwv_claim_permitted,false);
});
test('separate initial navigation and automated scroll samples; never field-CWV',()=>{
 const h=harness();h.inject();const a=h.read();
 h.emit('layout-shift',[{value:.4,hadRecentInput:false,startTime:2,sources:[]}]);
 const v=interpretVisualLab(a,h.read(),true);
 assert.equal(v.state,'LAB_OBSERVED_NOT_FIELD_CWV');
 assert.equal(v.after_navigation.layout_shift_score,0);
 assert.equal(v.after_automated_scroll.layout_shift_score,.4);
 assert.equal(v.field_cwv_claim_permitted,false);
});
test('missing final observer snapshot fails closed',()=>{
 const h=harness();h.inject();
 assert.equal(interpretVisualLab(h.read(),null,true).state,'UNVERIFIED');
});
test('negative and non-finite entries cannot increase scores',()=>{
 const h=harness();h.inject();
 h.emit('largest-contentful-paint',[{startTime:NaN,size:42,element:{tagName:'IMG'}}]);
 h.emit('layout-shift',[{value:-1,startTime:0},{value:NaN,startTime:0}]);
 assert.equal(h.read().largest_contentful_paint,null);
 assert.equal(h.read().layout_shift_score,0);
});
