import {test} from 'node:test';
import assert from 'node:assert/strict';
import {eligibleRecords,dailyRecord,recordById} from './discovery-core.mjs';
const record=(id,extra={})=>({id,reviewStatus:'approved',copyApproved:true,rightsApproved:true,sources:['https://example.org/source'],...extra});
test('rejects missing or unapproved records',()=>{
 assert.deepEqual(eligibleRecords([null,record('a',{copyApproved:false}),record('b',{rightsApproved:false}),record('c',{sources:[]}),record('d',{reviewStatus:'draft'})]),[]);
});
test('deduplicates and sorts',()=>assert.deepEqual(eligibleRecords([record('b'),record('a'),record('a')]).map(x=>x.id),['a','b']));
test('deterministic UTC selection regardless of input order',()=>{
 const d=new Date('2026-11-25T00:00:00Z');
 assert.equal(dailyRecord([record('a'),record('b')],d).id,dailyRecord([record('b'),record('a')],d).id);
});
test('invalid input and empty corpus fail closed',()=>{
 assert.equal(dailyRecord([],new Date()),null);
 assert.equal(dailyRecord([record('a')],new Date('invalid')),null);
 assert.equal(recordById([record('a',{copyApproved:false})],'a'),null);
});
