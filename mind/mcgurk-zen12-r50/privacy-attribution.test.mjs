import assert from "node:assert/strict";
import {ATTRIBUTION_ENABLED,MIN_PUBLIC_COHORT,acceptSyntheticEvent,summarizeSynthetic,recordLiveEvent} from "./privacy-attribution.mjs";

assert.equal(ATTRIBUTION_ENABLED,false);
assert.equal(MIN_PUBLIC_COHORT,20);
assert.equal(recordLiveEvent({kind:"cta_intent",user:"secret"}).recorded,false);
assert.equal(recordLiveEvent(null).status,"DISABLED");

const good={kind:"guide_view",topic:"zen12",variant:"A_TEXT",source:"organic"};
assert.deepEqual(acceptSyntheticEvent(good),good);
assert.equal(Object.isFrozen(acceptSyntheticEvent(good)),true);
for(const bad of [
 null,[],Object.create(null),{...good,email:"user@example.com"},{...good,ip:"127.0.0.1"},
 {...good,referrer:"https://search/?email=sensitive"},{...good,userAgent:"x"},
 {...good,click_id:"123"},{...good,utm_campaign:"raw"},{...good,source:"https://example.com"},
 {...good,source:"social-tiktok"},{...good,variant:"B_FILM",topic:"brainwave-shots"},
 {...good,kind:"purchase"},{...good,topic:"unknown"},{kind:"guide_view"}, "not-an-event"
]) assert.equal(acceptSyntheticEvent(bad),null);

assert.deepEqual(summarizeSynthetic(Array(19).fill(good)),[]);
assert.deepEqual(summarizeSynthetic(Array(20).fill(good)),[{bucket:"guide_view|zen12|A_TEXT|organic",count:20}]);
const mixed=[...Array(21).fill(good),...Array(10).fill({...good,variant:"B_FILM"}),{...good,email:"x"}];
assert.deepEqual(summarizeSynthetic(mixed),[{bucket:"guide_view|zen12|A_TEXT|organic",count:21}]);
assert.deepEqual(summarizeSynthetic("not-array"),[]);
assert.deepEqual(summarizeSynthetic(Array(100001).fill(good)),[]);
console.log("privacy suite: 24 synthetic assertions and fail-closed live gate PASS");
