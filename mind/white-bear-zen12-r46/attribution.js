'use strict';
/** Offline-only privacy contract. Not imported by any website code. */
const ACTIVE=false;
const CHANNELS=new Set(['direct','organic','tiktok','dispatch','other']);
const VARIANTS=new Set(['text','video']);
const TOPICS=new Set(['white_bear','zen12']);
function normalize(sample){
 if(!sample || typeof sample!=='object'||Array.isArray(sample)) return null;
 const keys=Object.keys(sample).sort();
 if(keys.join(',')!=='channel,topic,variant') return null; // deliberately reject uid, IP, timestamps, URLs, referrers
 const {channel,topic,variant}=sample;
 if(!CHANNELS.has(channel)||!TOPICS.has(topic)||!VARIANTS.has(variant))return null;
 return Object.freeze({channel,topic,variant});
}
function aggregateForReview(items,minCell=20){
 if(!Number.isInteger(minCell)||minCell<20)throw Error('privacy threshold cannot be lowered');
 const bucket=Object.create(null);
 for(const raw of items){const row=normalize(raw); if(!row)continue;const key=[row.channel,row.topic,row.variant].join('|');bucket[key]=(bucket[key]||0)+1;}
 return Object.freeze(Object.entries(bucket).filter(([,n])=>n>=minCell).map(([cell,count])=>Object.freeze({cell,count})));
}
function recordLiveEvent(){return false;} // hard off: no network, DOM, storage, cookies or logging
if(typeof module!=='undefined')module.exports={ACTIVE,normalize,aggregateForReview,recordLiveEvent};