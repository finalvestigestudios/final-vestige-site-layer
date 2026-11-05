/**
 * Review-only, fail-closed Page 6 patch for Hidden in the Margins reduced-motion parity.
 * Input: the PUBLIC Gutenberg content string of WordPress page ID 6.
 * Output: modified Gutenberg content string for isolated/nonproduction review.
 * No WordPress API calls, cookie reads, credentials, tracking, or production writes.
 */
export const EXPECTED_CHAPTERS = Object.freeze([
  "fv-hf-title", "fv-hf-chronicle", "fv-hf-evidence", "fv-hf-inquiry",
  "fv-hf-method-title", "fv-hf-observer", "fv-hf-mind-title"
]);
export const OLD_REDUCED_RULE = "@media(prefers-reduced-motion:reduce){.fv-margin-strip__window{height:auto;min-height:0;overflow:visible}.fv-margin-strip__window:before{top:14px}.fv-margin-strip__item{position:relative;display:none;left:auto;right:auto;top:auto;transform:none;opacity:1;filter:none;animation:none;padding:2px 0 6px 16px}.fv-margin-strip__item:nth-child(1){display:block}}";
const OPENING = '<!-- wp:html -->\n<div class="fv-margin-strip fv-margin-strip--rotator"';
const END_BLOCK = "<!-- /wp:html -->";
const OLD_WINDOW = 'aria-label="Rotating source and accountability notes"';
const NEW_WINDOW = 'aria-label="72 Hidden in the Margins historical notes"';
const OLD_LABEL = '<div class="fv-margin-strip__label">Hidden in the Margins</div>';
const NEW_LABEL = '<div class="fv-margin-strip__label">Hidden in the Margins<span class="fv-margin-strip__reduced-hint">Scroll or swipe to browse all 72 notes</span></div>';
const FRAGMENT_RE = /<span class="fv-margin-strip__item" style="--i:(\d+)">([\s\S]*?)<\/span>/g;
const FOCUS_RE = /href="(?:https:\/\/finalvestige\.com)?\/focus\/"/g;
const REDUCED_REPLACEMENT = [
  '.fv-margin-strip__reduced-hint{display:none}',
  '@media(prefers-reduced-motion:reduce){',
  '  .fv-margin-strip__inner{align-items:start}',
  '  .fv-margin-strip__label{white-space:normal}',
  '  .fv-margin-strip__reduced-hint{display:block;margin-top:7px;color:#d8d2c7;font-size:11px;letter-spacing:0;text-transform:none;line-height:1.45}',
  '  .fv-margin-strip__window{display:flex;align-items:stretch;gap:12px;position:relative;max-width:100%;height:auto;min-height:0;padding:8px 3px 13px 12px;overflow-x:auto;overflow-y:hidden;scroll-behavior:auto;scrollbar-width:auto}',
  '  .fv-margin-strip__window:before{display:none}',
  '  .fv-margin-strip__item{display:block;position:relative;flex:0 0 clamp(240px,68vw,450px);left:auto;right:auto;top:auto;margin:0;padding:10px 14px;min-height:60px;border-left:2px solid #b8955e;background:#171917;color:#d8d2c7;transform:none;opacity:1;filter:none;animation:none;white-space:normal;line-height:1.5}',
  '}',
  '@media(prefers-reduced-motion:reduce) and (forced-colors:active){',
  '  .fv-margin-strip__item{border-color:CanvasText;background:Canvas;color:CanvasText}',
  '}'
].join('\n');
const occurrences = (value, needle) => value.split(needle).length - 1;
const fail = msg => { throw new Error("REVIEW HOLD: " + msg); };
export function inspectPage6(html) {
  if (typeof html !== "string" || !html.startsWith(OPENING)) fail("unexpected or nonpublic Page 6 Gutenberg opening");
  const end = html.indexOf(END_BLOCK);
  if (end < 0) fail("missing first Gutenberg HTML closing marker");
  const block = html.slice(0, end);
  const tail = html.slice(end);
  if (occurrences(html, END_BLOCK) < 2) fail("incomplete WordPress page structure");
  if (occurrences(block, '<div class="fv-margin-strip__window"') !== 1) fail("window structure drift");
  if (occurrences(block, OLD_WINDOW) !== 1) fail("accessible-label drift or already patched");
  if (occurrences(block, OLD_LABEL) !== 1) fail("visible-label drift or already patched");
  if (occurrences(block, OLD_REDUCED_RULE) !== 1) fail("reduced-motion source rule changed; no blind CSS override");
  if (occurrences(block, "<style>") !== 1 || occurrences(block, "</style>") !== 1) fail("Margins stylesheet structure drift");
  if (occurrences(html, '<span class="fv-margin-strip__item"') !== 72) fail("historical fragment count changed");
  const records = [...block.matchAll(FRAGMENT_RE)];
  if (records.length !== 72 || [...tail.matchAll(FRAGMENT_RE)].length !== 0) fail("fragment markup drift");
  for (let i = 0; i < 72; i++) {
    if (+records[i][1] !== i || !records[i][2].trim()) fail("empty/duplicated/out-of-order historical fragment " + i);
  }
  for (const id of EXPECTED_CHAPTERS) {
    if (!tail.includes('href="#' + id + '"')) fail("missing flagship chapter anchor " + id);
  }
  const focusLinks = [...html.matchAll(FOCUS_RE)].length;
  if (focusLinks < 4) fail("Focus Fieldbook links missing (" + focusLinks + ")");
  if (occurrences(html, '<!-- wp:jetpack/subscriptions') !== 1) fail("Jetpack signup missing or duplicated");
  return { block, tail, records: records.map(m => m[2]), focusLinks };
}
export function patchPage6(html) {
  const pre = inspectPage6(html);
  let block = pre.block.replace(OLD_WINDOW, NEW_WINDOW)
    .replace(OLD_LABEL, NEW_LABEL)
    .replace(OLD_REDUCED_RULE, REDUCED_REPLACEMENT);
  if (block === pre.block || occurrences(block, "fv-margin-strip__reduced-hint") !== 3)
    fail("replacement failed");
  const output = block + pre.tail;
  // Exact bytes of all unrelated Gutenberg blocks and all original fragment texts.
  if (output.slice(output.indexOf(END_BLOCK)) !== pre.tail) fail("unrelated block changed");
  const records = [...output.matchAll(FRAGMENT_RE)].map(m => m[2]);
  if (JSON.stringify(records) !== JSON.stringify(pre.records)) fail("history text changed");
  if ([...output.matchAll(FOCUS_RE)].length !== pre.focusLinks) fail("Focus link changed");
  if (occurrences(output, NEW_WINDOW) !== 1 || occurrences(output, NEW_LABEL) !== 1) fail("accessible UX not installed");
  if (output.includes(OLD_REDUCED_RULE) || output.includes('class="fv-margin-strip__item" style="--i:72"')) fail("legacy rule or extra record survived");
  return { html: output, receipt: {
    status: "REVIEW_ONLY_NOT_TESTED_ON_WORDPRESS", record_count: records.length,
    focus_link_count: pre.focusLinks, chapter_count: EXPECTED_CHAPTERS.length,
    unchanged_tail_bytes: pre.tail.length,
    new_instruction: "Scroll or swipe to browse all 72 notes",
    stylesheet_scope: "original first public Gutenberg HTML block; reduced motion only"
  }};
}
