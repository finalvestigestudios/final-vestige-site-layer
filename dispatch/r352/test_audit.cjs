"use strict";
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path");
const audit=require("./audit.cjs");
const here=__dirname;
const original={
 meta:JSON.parse(fs.readFileSync(path.join(here,"candidate.json"),"utf8")),
 md:fs.readFileSync(path.join(here,"OPTIONAL_ISSUE01.md"),"utf8"),
 txt:fs.readFileSync(path.join(here,"OPTIONAL_ISSUE01.txt"),"utf8"),
 html:fs.readFileSync(path.join(here,"OPTIONAL_ISSUE01.html"),"utf8")
};
const copy=()=>JSON.parse(JSON.stringify(original));
assert.equal(audit(copy()).pass,true,"clean source-only candidate should pass offline format gate");
const mutate=[
 x=>{x.meta.flags.release_authorized=true},x=>{x.meta.flags.sent=true},
 x=>{x.meta.flags.provider_confirmed_consent=true},
 x=>{x.meta.state="READY_TO_SEND"},
 x=>{x.meta.original_campaign_pr=49},
 x=>{x.meta.primary_cta_url="https://hypnosislive.com/mental-skills/total-focus"},
 x=>{x.html=x.html.replace('data-primary-cta="true"','data-primary-cta="false"')},
 x=>{x.html=x.html.replace('lang="en"','')},
 x=>{x.html=x.html.replace('role="presentation"','')},
 x=>{x.html=x.html.replace('RELEASE BLOCKED','ALL CLEAR')},
 x=>{x.html+="<script>bad()</script>"},
 x=>{x.html+="<form method=\"post\"></form>"},
 x=>{x.md=x.md.replace('**One primary CTA:**','**Extra link:**')},
 x=>{x.md=x.md.replace('not a universal estimate','a global estimate')},
 x=>{x.txt=x.txt.replace(x.meta.primary_cta_url,'BROKEN CTA')},
 x=>{x.md=x.md.replace('[[VALID_POSTAL_ADDRESS_REQUIRED]]','')},
 x=>{x.meta.preheader='X'.repeat(125)},
 x=>{x.meta.sources[0].url='https://example.com/unverified'},
];
for(const [i,fn] of mutate.entries()){const v=copy();fn(v);assert.equal(audit(v).pass,false,'mutation '+i+' must not pass')}
console.log('PASS: 1 baseline + '+mutate.length+' adversarial cases; source-only; NO_SEND');
