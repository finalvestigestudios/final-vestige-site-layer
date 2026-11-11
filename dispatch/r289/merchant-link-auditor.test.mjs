import assert from 'node:assert/strict';
import fs from 'node:fs';
import {findMerchantDomains,classifyPreview,stripSellerSources} from './merchant-link-auditor.mjs';
const pairs=[["simple zen","https://zen12.com/about",true],["uppercase","HTTPS://ZEN12.COM/buy",true],["hypnosis","https://hypnosislive.com/mental-skills/total-focus",true],["inspire","www.inspire3.com",true],["percent","https%3A%2F%2Fzen12.com%2Fsecret",true],["twice","https%253A%252F%252Fhypnosislive.com",true],["entity dot","https://zen12&#46;com/secret",true],["entity scheme","&#104;ttps://zen12.com/buy",true],["zero-width","zen12​.com",true],["spaced period","zen12 . com",true],["amp entity","https://zen12&period;com",true],["plain brand","Zen12 is an audio program.",false],["academic","https://www.nccih.nih.gov/health/hypnosis",false],["puysegur","https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/",false],["plain copy","If you buy through a link on our guide, FV may earn a commission.",false]];
let checked=0;
for(const [name,raw,expected] of pairs){assert.equal(findMerchantDomains(raw).length>0,expected,name);checked++}
for(const n of ['03','05']){
 const original=fs.readFileSync(new URL('../r287/issue-'+n+'.txt',import.meta.url),'utf8');
 const safe=fs.readFileSync(new URL('issue-'+n+'.safe-review.txt',import.meta.url),'utf8');
 assert.deepEqual(stripSellerSources(original).out,safe,'derivation '+n);
 assert.equal(findMerchantDomains(safe).length,0,'no auto-linkable seller domain '+n);
 assert.ok(classifyPreview(safe).requires_release_hold,'review hold '+n);
 assert.ok(classifyPreview(safe).has_editorial_source,'research retained '+n);
 checked+=4;
}
console.log('R289: '+checked+'/'+checked+' offline email-link regression checks PASSED. No inbox tests performed.');
