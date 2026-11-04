import test from 'node:test';
import assert from 'node:assert/strict';
import {GUEST_VIEWPORTS,assertPublishedMarginParity,assertAnonymousNoJSState}
  from './guest_render_source_contract.mjs';

test('seven unique guest viewports cover 320-1920 and separately label CSS zoom proxy',()=>{
  assert.deepEqual(GUEST_VIEWPORTS.map(v=>v.width),[320,360,390,720,768,1440,1920]);
  assert.equal(GUEST_VIEWPORTS.find(v=>v.width===720).height,450);
  assert.match(GUEST_VIEWPORTS.find(v=>v.width===720).kind,/not-physical-zoom/);
  assert.ok(GUEST_VIEWPORTS.every(v=>v.height>0));
});
test('exact 72-source preservation accepts complete published content',()=>{
  const expected=Array.from({length:72},(_,i)=>'Published record '+i);
  assert.equal(assertPublishedMarginParity([...expected],expected),true);
});
test('all 72 single-record mutations are rejected, including last record',()=>{
  const expected=Array.from({length:72},(_,i)=>'Published record '+i);
  for(let i=0;i<72;i++) {
    const actual=[...expected];actual[i]+=' [tampered]';
    assert.throws(()=>assertPublishedMarginParity(actual,expected),
      new RegExp('index '+i));
  }
});
test('truncation, duplicate, swapped and HTML-escaped text are rejected',()=>{
  const expected=Array.from({length:72},(_,i)=>i===2?'Evidence & sources':'Record '+i);
  for(const actual of [
    expected.slice(0,71),
    [...expected.slice(0,71),expected[0]],
    [...expected.slice(0,2),expected[3],expected[2],...expected.slice(4)],
    expected.map(s=>s.replace('&','&amp;'))
  ])assert.throws(()=>assertPublishedMarginParity(actual,expected));
});
const valid={admin_bar:false,logged_in:false,details:true,summary_visible:true,
  evidence:2,focus:true,focus_visible:true,margins:72,margin_position:'static',
  margin_opacity:'1',window_overflow:'auto',horizontal_overflow:false,
  margin_readability:Array.from({length:72},()=>({display:'block',visibility:'visible',
    position:'static',opacity:'1',width:180,height:24,ancestor_hidden:false}))};
test('anonymous JavaScript-disabled document-flow meaning passes exact valid contract',()=>{
  assert.equal(assertAnonymousNoJSState(valid),true);
});
test('no-JS disclosure, offer and readability defects fail individually',()=>{
  const attacks=[
    {admin_bar:true},{logged_in:true},{details:false},{summary_visible:false},
    {evidence:1},{focus:false},{focus_visible:false},{margins:71},
    {margin_position:'absolute'},{margin_opacity:'0'},
    {window_overflow:'hidden'},{horizontal_overflow:true}
  ];
  for(const change of attacks)
    assert.throws(()=>assertAnonymousNoJSState({...valid,...change}),
      'Must reject '+JSON.stringify(change));
});

test('all 72 no-JS record boxes must be independently visible',()=>{
  for(let i=0;i<72;i++) {
    const rows=valid.margin_readability.map(r=>({...r}));
    rows[i].display='none';
    assert.throws(()=>assertAnonymousNoJSState({...valid,margin_readability:rows}),
      new RegExp('at '+i));
  }
});
test('ancestor, ARIA, inert, invisible, zero-height and off-flow defects fail closed',()=>{
  const flaws=[{ancestor_hidden:true},{visibility:'hidden'},{opacity:'0'},
    {width:0},{height:0},{position:'absolute'}];
  for(const flaw of flaws){
    const rows=valid.margin_readability.map(r=>({...r}));
    rows[47]={...rows[47],...flaw};
    assert.throws(()=>assertAnonymousNoJSState({...valid,margin_readability:rows}),
      /at 47/);
  }
  assert.throws(()=>assertAnonymousNoJSState({...valid,margin_readability:valid.margin_readability.slice(0,71)}),
    /72 Margins/);
});
