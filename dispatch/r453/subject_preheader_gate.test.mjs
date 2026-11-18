/** Test from repository, not from WordPress; no sends, imports, writes to site or customers. */
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { lintEnvelopeField, lintManifestEnvelopes } from './subject_preheader_gate.mjs';
const manifest=JSON.parse(readFileSync(new URL('../r446/SOURCE_PINS_AND_RELEASE.json',import.meta.url),'utf8'));
test('source pinned manifest contains exactly 12 original/alternative pairs',()=>assert.equal(lintManifestEnvelopes(manifest).total_subject_preheader_pairs,12));
test('four alternative pairs contaminated by markdown formatting',()=>assert.equal(lintManifestEnvelopes(manifest).flagged_pairs,4));
test('only 01 02 05 06 alternatives affected',()=>assert.deepEqual(lintManifestEnvelopes(manifest).results.filter(x=>x.problems.length).map(x=>x.issue),[1,2,5,6]));
test('original manuscript pair metadata not flagged',()=>assert.ok(lintManifestEnvelopes(manifest).results.filter(x=>x.variant==='original').every(x=>!x.problems.length)));
test('hard reject CRLF header injection',()=>assert.ok(lintEnvelopeField('Hi\r\nBcc:abc@example.com','subject').includes('header_injection_newline')));
test('hard reject markdown prefix',()=>assert.ok(lintEnvelopeField('** Subject','subject').includes('markdown_contamination')));
test('hard reject html in subject',()=>assert.ok(lintEnvelopeField('<b>Subject</b>','subject').includes('html_contamination')));
test('flag unsupported guaranteed claims',()=>assert.ok(lintEnvelopeField('100% effective','subject').includes('unsupported_outcome_language')));
test('flag empty preheader',()=>assert.ok(lintEnvelopeField('','preheader').includes('missing_preheader')));
test('plain grounded subject accepted',()=>assert.deepEqual(lintEnvelopeField('The witness was also the experimenter','subject'),[]));
test('plain grounded preheader accepted',()=>assert.deepEqual(lintEnvelopeField('Puységur and the limits of a record','preheader'),[]));
