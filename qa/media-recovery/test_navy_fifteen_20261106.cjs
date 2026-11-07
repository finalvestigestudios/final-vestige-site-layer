'use strict';
function runSuite(validate = require('./validate_navy_fifteen_20261106.cjs').validateNavyAudit,
                  seed = require('./navy_fifteen_primary_catalog_20261106.json')) {
  const clone = () => JSON.parse(JSON.stringify(seed));
  const select = (d,key) => d.records.find(x=>x.key===key);
  const cases = [
    ['baseline valid', d=>{},true],
    ['one row removed', d=>d.records.pop()],
    ['duplicate key', d=>d.records[1].key=d.records[0].key],
    ['bad source origin', d=>d.records[0].published_src='https://history.navy.mil.attacker.test/pixel'],
    ['bad article origin', d=>d.articles[0].post_url='https://external.example/'],
    ['missing alt', d=>d.records[0].published_alt=' '],
    ['invented origin HTTP code', d=>d.records[0].guest_browser.http_status=404],
    ['invented currentSrc', d=>d.records[0].guest_browser.current_src='https://example.com/pic.jpg'],
    ['invented decode', d=>d.records[0].guest_browser.natural_width=1],
    ['invented measured bytes', d=>d.records[0].guest_browser.encoded_bytes=1024],
    ['invented browser broken flag', d=>d.records[0].guest_browser.broken=true],
    ['licensing claimed cleared', d=>d.records[0].rights.status='CLEARED'],
    ['wrong third-party rehost permission', d=>d.records[0].rights.permission_to_rehost=true],
    ['illegal copy/cache permission', d=>d.records[0].rights.permission_to_cache=true],
    ['production write enabled', d=>d.records[0].word_press_write_authorized=true],
    ['publisher accession mismatch', d=>select(d,'280:0').source_catalog.accession='NH 12345'],
    ['publisher catalog wrong origin', d=>select(d,'288:0').source_catalog.url='https://site.example/file'],
    ['donated image credit missing', d=>select(d,'288:0').source_catalog.credit=''],
    ['preview exceeds 960', d=>select(d,'370:0').safe_960px_preview_candidate.width=961],
    ['preview stretches aspect', d=>select(d,'370:0').safe_960px_preview_candidate.height=1008],
    ['geometry no source master', d=>select(d,'280:2').safe_960px_preview_candidate={width:960,height:960}],
    ['conflicting official photo prematurely resized', d=>select(d,'370:1').safe_960px_preview_candidate={width:960,height:801}],
    ['second master lost', d=>select(d,'370:1').source_catalog.variant_masters.pop()],
    ['official high masters made same aspect', d=>select(d,'370:1').source_catalog.variant_masters[1].height=2380],
    ['post identity mismatch', d=>select(d,'370:0').post_id=288],
    ['false 42 broken claim', d=>d.caveats.reported_42_broken_images_unverified=false],
    ['false 76 percent measured claim', d=>d.caveats.claimed_76_percent_wire_reduction_unmeasured=false],
    ['invented first party repairs', d=>d.caveats.production_images_repaired=1],
    ['unlicensed cache happened', d=>d.caveats.third_party_image_caches=1],
    ['invented savings/guest data', d=>d.caveats.visitor_confirmed_broken_images=0],
    ['fabricated catalog count', d=>d.totals.official_catalog_accession_matches=15],
    ['missing source row in existing post', d=>d.articles[3].navy_image_count=3]
  ];
  let passed=0; const failures=[];
  for (const [name,mutate,shouldPass] of cases) {
    const data=clone(); mutate(data);
    let accepted=false;
    try { const result=validate(data); accepted=!!result.ok; }
    catch (_err) {}
    if (accepted===!!shouldPass) passed++;
    else failures.push(name+' (accepted='+accepted+', expected='+!!shouldPass+')');
  }
  if(failures.length) throw new Error(failures.join('\n'));
  return {passed, total:cases.length, validation:'isolated actual-source replay', native_browser_executed:false};
}
module.exports={runSuite};
if(typeof require !== 'undefined' && require.main===module) {
  try { console.log(JSON.stringify(runSuite())); }
  catch(e) { console.error(e.stack); process.exitCode=1; }
}
