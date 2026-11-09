#!/usr/bin/env node
/* Review-only: propose an additional first-screen Focus route on published
 * WordPress Page 6. Never writes to any CMS. JSON input is a READ-ONLY WP export.
 * This is NOT a checkout, lead, affiliate, or revenue tracking integration.
 */
'use strict';
const fs = require('node:fs');
const crypto = require('node:crypto');
const assert = require('node:assert/strict');
const sha = s => crypto.createHash('sha256').update(s, 'utf8').digest('hex');
const OLD_ACTIONS = `            <div class="fv-hf__opening-actions">
              <a class="fv-hf__button fv-hf__button--gold" href="#fv-hf-evidence">Enter the evidence room <span aria-hidden="true">↗</span></a>
              <a class="fv-hf__text-link" href="https://finalvestige.com/blog/">Read the investigations <span aria-hidden="true">↗</span></a>
            </div>`;
const NEW_ACTIONS = `            <div class="fv-hf__opening-actions">
              <a class="fv-hf__button fv-hf__button--gold" href="#fv-hf-evidence">Enter the evidence room <span aria-hidden="true">↗</span></a>
              <a class="fv-hf__text-link fv-hf__focus-bridge" href="/focus/" aria-label="Explore the free 52-page Seven Day Focus Fieldbook">Explore the free 52-page Focus Fieldbook <span aria-hidden="true">↗</span></a>
              <a class="fv-hf__text-link" href="https://finalvestige.com/blog/">Read the investigations <span aria-hidden="true">↗</span></a>
            </div>`;
const REQUIRE = Object.freeze({id:6, status:'publish', modified:'2026-11-05T12:07:24', margins:72, chapterLinks:7});
function fail(message){throw new Error('REVIEW_FAIL_CLOSED:'+message);}
function extract(resp){
  const p=resp.structuredContent?.data ?? resp.data ?? resp;
  if(p.id!==REQUIRE.id || p.status!==REQUIRE.status || p.modified!==REQUIRE.modified) fail('PAGE_ID_STATUS_OR_MODIFIED_DRIFT');
  if(typeof p.content!=='string')fail('MISSING_RAW_GUTENBERG_CONTENT');
  return p.content;
}
function build(resp){
  const src=extract(resp);
  if(src.split(OLD_ACTIONS).length!==2)fail('EXACT_HERO_ACTIONS_MISSING_OR_DUPLICATED');
  if((src.match(/class="fv-margin-strip__item"/g)||[]).length!==REQUIRE.margins)fail('72_MARGINS_DRIFT');
  if((src.match(/<nav class="fv-hf__chapter-nav"/g)||[]).length!==1)fail('CHAPTER_NAV_MISSING');
  const nav=src.match(/<nav class="fv-hf__chapter-nav"[\s\S]*?<\/nav>/)?.[0]??'';
  if((nav.match(/href="#fv-hf-[^"]+"/g)||[]).length!==REQUIRE.chapterLinks)fail('7_CHAPTER_LINKS_DRIFT');
  if((src.match(/<!-- wp:jetpack\/subscriptions /g)||[]).length!==1)fail('NATIVE_JETPACK_BLOCK_DRIFT');
  if((src.match(/href="\/focus\/"/g)||[]).length<1)fail('ORIGINAL_FOCUS_ROUTES_MISSING');
  if(!src.includes('The Victory Point note: an 1847 message') || !src.includes('NASA · Apollo 204 Review Board'))fail('SOURCE_CUSTODY_DRIFT');
  if(!src.includes('Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf') && !src.includes('focus_complete_cover.webp'))fail('FIELD_BOOK_ASSET_DRIFT');
  const next=src.replace(OLD_ACTIONS,NEW_ACTIONS);
  const i=src.indexOf(OLD_ACTIONS);
  assert.equal(next.slice(0,i),src.slice(0,i),'prefix drift');
  assert.equal(next.slice(i+NEW_ACTIONS.length),src.slice(i+OLD_ACTIONS.length),'suffix drift');
  assert.equal((next.match(/class="fv-margin-strip__item"/g)||[]).length,72);
  assert.equal((next.match(/<!-- wp:jetpack\/subscriptions /g)||[]).length,1);
  assert.equal((next.match(/class="fv-hf__focus-bridge"/g)||[]).length,0); // exact class pair, not a standalone class
  assert.equal((next.match(/href="\/focus\/"/g)||[]).length,(src.match(/href="\/focus\/"/g)||[]).length+1);
  return {candidate:next, receipt:{decision:'REVIEW_ONLY_NOT_APPROVED',source_page_id:6,source_modified:REQUIRE.modified,source_sha256:sha(src),candidate_sha256:sha(next),old_hero_actions_sha256:sha(OLD_ACTIONS),new_hero_actions_sha256:sha(NEW_ACTIONS),changed_ranges:1,unrelated_editor_bytes_identical:true,first_screen_new_focus_links:1,seven_chapters_preserved:true,margin_records_preserved:72,native_jetpack_block_preserved:true,new_script_count:0,new_external_asset_count:0,affiliate_links_added:0,analytics_added:0,confirmed_leads:0,verified_purchases:0,wp_writes:0}};
}
if(require.main===module){
  if(process.argv.length!==5){console.error('Usage: node patch_hero_focus_bridge.cjs read_only_page6.json candidate.html receipt.json');process.exit(2)}
  try {const r=build(JSON.parse(fs.readFileSync(process.argv[2],'utf8')));fs.writeFileSync(process.argv[3],r.candidate);fs.writeFileSync(process.argv[4],JSON.stringify(r.receipt,null,2)+'\n');console.log(JSON.stringify(r.receipt,null,2))} catch(e){console.error(e.message);process.exit(1)}
}
module.exports={build,extract,OLD_ACTIONS,NEW_ACTIONS,REQUIRE};
