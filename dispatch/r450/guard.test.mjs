import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import {review} from "./guard.mjs";
const html=fs.readFileSync(new URL("./ISSUE05_SUBSCRIBER_ONLY_REVIEW.html",import.meta.url),"utf8");
const txt=fs.readFileSync(new URL("./ISSUE05_SUBSCRIBER_ONLY_REVIEW.txt",import.meta.url),"utf8");
const man=JSON.parse(fs.readFileSync(new URL("./SOURCE_AND_RELEASE_GATES.json",import.meta.url),"utf8"));
const run=(h=html,t=txt,m=man)=>review(h,t,m);
test("actual committed HTML/plaintext remain HOLD and pass structural checks",()=>{assert.equal(run().pass,true);assert.equal(run().release,"HOLD_UNSENT")});
const cases=[
["internal notes in text",html,txt+" SUBSCRIBER-FACING CANDIDATE COPY ENDS","INTERNAL_NOTES_LEAK"],
["internal notes in HTML",html+" Reviewer internal",txt,"INTERNAL_NOTES_LEAK"],
["script injected",html+"<script>1</script>",txt,"UNSAFE_MARKUP"],
["tracking image inserted",html+'<img src="x">',txt,"UNSAFE_MARKUP"],
["form inserted",html+"<form></form>",txt,"UNSAFE_MARKUP"],
["affiliate link inserted",html+'<a href="https://x/?affiliate_id=10">Buy</a>',txt,"UNAPPROVED_REFERRAL"],
["promo link inserted",html+'<a href="https://zen12.com/secret/">Buy</a>',txt,"UNAPPROVED_REFERRAL"],
["missing main disclosure",html.replace("Commercial disclosure",""),txt,"MISSING_DISCLOSURE"],
["missing guide text",html.replaceAll("[GUIDE UNAVAILABLE","[REMOVED GUIDE"),txt,"FAKE_GUIDE_LINK"],
["missing postal",html.replaceAll("[[VALID_FV_POSTAL_ADDRESS_REQUIRED]]",""),txt,"UNVERIFIED_POSTAL"],
["missing unsubscribe",html,txt.replaceAll("[[RENDERED_JETPACK_UNSUBSCRIBE_REQUIRED]]",""),"UNVERIFIED_UNSUBSCRIBE"],
["missing Gutenberg citation",html.replaceAll("gutenberg.org/ebooks/78413",""),txt,"MISSING_SOURCE:gutenberg.org/ebooks/78413"]
];
for(const [name,h,t,expected] of cases)test(name,()=>assert.ok(run(h,t).errors.includes(expected),name));
test("release cannot be changed to send",()=>assert.ok(run(html,txt,{...man,release:"SEND"}).errors.includes("UNAUTHORIZED_RELEASE")));
test("email affiliate permission cannot be fabricated",()=>assert.ok(run(html,txt,{...man,merchant_email_permission:true}).errors.includes("FALSE_ATTESTATION")));
test("revenue cannot be imputed from CTA",()=>assert.ok(run(html,txt,{...man,revenue_per_1000:15}).errors.includes("FABRICATED_REVENUE")));
test("source text contains no end-delimiter",()=>assert.equal(txt.includes("SUBSCRIBER-FACING CANDIDATE COPY ENDS"),false));
test("source mail copy retains Hypnosis Live, not substituted Total Focus",()=>{assert.match(txt,/Hypnosis Live/);assert.match(txt,/NOT Total Focus/)});
