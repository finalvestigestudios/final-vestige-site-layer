"use strict";
const keys=new Set(["source","campaign","asset","event","cohort"]);
const sources=new Set(["youtube","tiktok","instagram","facebook","pinterest","x","bluesky"]);
const events=new Set(["campaign_landing","article_to_resource_click","offer_view","affiliate_outbound"]);
const token=/^[a-z0-9][a-z0-9_-]{0,63}$/;
function validate(row){if(!row||Object.getPrototypeOf(row)!==Object.prototype)throw Error("plain object only");
for(const k of Object.keys(row))if(!keys.has(k))throw Error("unapproved field");
for(const k of keys)if(typeof row[k]!=="string")throw Error("missing categorical field");
if(!sources.has(row.source)||!events.has(row.event))throw Error("unapproved category");
for(const k of ["campaign","asset","cohort"])if(!token.test(row[k]))throw Error("invalid category");
if(row.asset.startsWith("pending_"))throw Error("asset missing");return Object.freeze({...row});}
function summarizeSynthetic(rows){const cells=new Map();for(const x of rows){const row=validate(x);const key=[row.source,row.campaign,row.asset,row.event,row.cohort].join("|");cells.set(key,(cells.get(key)||0)+1)}return [...cells].map(([key,count])=>({key,count:count>=20?count:null,suppressed:count<20}));}
function collectLive(){throw Error("no live recording permitted");}
function confirmSale(){throw Error("cannot infer merchant sale from a click");}
module.exports={validate,summarizeSynthetic,collectLive,confirmSale};