<?php
/**
 * Apollo Experience 2.0 R381 — curated, non-geospatial Evidence Atlas (staging only).
 * Source-of-truth: the sealed six-document R377 custody record; no alternative claim input.
 * No visual NASA assets, third-party requests, tracking, transactions or database writes.
 */
if (!defined('ABSPATH')) { exit; }
const FV_R381_TAG = 'fv_apollo_curated_atlas_r381';
const FV_R381_FREE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
const FV_R381_CSS_SHA256 = 'e6d6e054781bdd4abb309d48e0c9498f5f59dd4d01436698763df97c70cecb3a';
const FV_R381_JS_SHA256 = '8d2099b9a34f060540063ba0697980658d5754f24bcb25c0b28e18c3368f5cda';

function fv_r381_escape($value): string {
    return htmlspecialchars((string) $value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}
function fv_r381_fallback(): string {
    return '<section class="fv-a381" aria-label="Apollo research sources unavailable"><h2>Evidence Atlas unavailable</h2>'
      . '<p>The reviewed source record did not pass verification, so no historical claims or source-to-event relationships are displayed here.</p>'
      . '<p><a data-fv-free-cta href="' . fv_r381_escape(FV_R381_FREE) . '">Read the existing free Apollo 1 investigation</a></p></section>';
}
function fv_r381_approved($records): bool {
    if (!function_exists('fv_r377_records') || !is_array($records) || count($records) !== 6) { return false; }
    $canonical = fv_r377_records();
    if (!is_array($canonical) || $records !== $canonical) { return false; }
    // Fixed, editorially reviewed classification. Never derive a physical map pin from an article title.
    $classes = array('test','hazard','record','record','uncertainty','response');
    foreach ($records as $i => $r) {
        if (!is_array($r) || ($r['id'] ?? '') !== array('01-ground-test','02-oxygen','03-fire-sequence','04-hatch','05-ignition','06-testing')[$i]
            || !in_array($classes[$i],array('test','hazard','record','uncertainty','response'),true)) { return false; }
    }
    return true;
}
function fv_r381_render($records): string {
    if (!fv_r381_approved($records)) { return fv_r381_fallback(); }
    static $counter = 0; ++$counter;
    $id = 'fv-a381-' . $counter;
    $groups = array(
        array('key'=>'ground','when'=>'January 27, 1967','heading'=>'The ground rehearsal','explain'=>'Test conditions, recorded sequence and escape constraints. These records do not establish an exact ignition point.', 'offset'=>0, 'length'=>4),
        array('key'=>'board','when'=>'1967 Board investigation','heading'=>'What the investigation concluded','explain'=>'Distinguish the most probable initiator from a conclusively identified spark.', 'offset'=>4, 'length'=>1),
        array('key'=>'response','when'=>'December 1967–February 1968','heading'=>'The later engineering response','explain'=>'These 102 deliberate test ignitions were not part of the January 1967 accident.', 'offset'=>5, 'length'=>1),
    );
    $facets = array('test','hazard','record','record','uncertainty','response');
    ob_start(); ?>
<section class="fv-a381" data-fv-atlas aria-labelledby="<?php echo fv_r381_escape($id); ?>-title">
 <div class="fv-a381__shell">
  <p class="fv-a381__eyebrow">FINAL VESTIGE · EXPERIENCE 2.0 · SOURCE-CUSTODY ATLAS</p>
  <h2 id="<?php echo fv_r381_escape($id); ?>-title">Six records. Three documentary moments. No invented links.</h2>
  <p class="fv-a381__intro">A research index for Apollo 1 that keeps the original investigation, its uncertainty and NASA's later engineering tests separate. Read the claim, its boundary and the NASA source for yourself. Nothing here requires JavaScript.</p>
  <p class="fv-a381__geography"><strong>Atlas method:</strong> This is a document-based collection, not a geographic plot. No coordinates, map pins, causal edges, photographs, logos or implied NASA sponsorship are supplied.</p>
  <nav class="fv-a381__rail" aria-label="Reviewed documentary phases"><ol>
   <?php foreach ($groups as $phase): ?>
    <li><a href="#<?php echo fv_r381_escape($id.'-'.$phase['key']); ?>"><span><?php echo fv_r381_escape($phase['when']); ?></span><strong><?php echo fv_r381_escape($phase['heading']); ?></strong></a></li>
   <?php endforeach; ?>
  </ol></nav>
  <div class="fv-a381__enhance" data-fv-atlas-controls hidden>
   <label for="<?php echo fv_r381_escape($id); ?>-filter">Explore a source role</label>
   <select id="<?php echo fv_r381_escape($id); ?>-filter" data-fv-atlas-filter>
    <option value="all">All six source records</option><option value="test">Ground test</option>
    <option value="hazard">Cabin hazard</option><option value="record">Recorded evidence / escape</option>
    <option value="uncertainty">Ignition uncertainty</option><option value="response">Later testing</option>
   </select>
   <button type="button" data-fv-atlas-reset>Show all records</button>
   <p role="status" aria-live="polite" aria-atomic="true" data-fv-atlas-status>Showing six source records.</p>
  </div>
  <?php foreach ($groups as $phase): ?>
   <section class="fv-a381__phase" id="<?php echo fv_r381_escape($id.'-'.$phase['key']); ?>" data-fv-atlas-phase aria-labelledby="<?php echo fv_r381_escape($id.'-'.$phase['key'].'-heading'); ?>">
    <header class="fv-a381__phasehead"><p><?php echo fv_r381_escape($phase['when']); ?></p><h3 id="<?php echo fv_r381_escape($id.'-'.$phase['key'].'-heading'); ?>"><?php echo fv_r381_escape($phase['heading']); ?></h3><p><?php echo fv_r381_escape($phase['explain']); ?></p></header>
    <ol class="fv-a381__plates">
    <?php for ($j = $phase['offset']; $j < $phase['offset'] + $phase['length']; ++$j): $r = $records[$j]; ?>
     <li class="fv-a381__plate" data-fv-atlas-plate data-fv-atlas-facet="<?php echo fv_r381_escape($facets[$j]); ?>">
      <article aria-labelledby="<?php echo fv_r381_escape($id.'-r'.$j); ?>">
       <p class="fv-a381__number">RECORD <?php echo fv_r381_escape(sprintf('%02d', $j+1)); ?> / 06 <span>· <?php echo fv_r381_escape($r['kind']); ?></span></p>
       <h4 id="<?php echo fv_r381_escape($id.'-r'.$j); ?>"><?php echo fv_r381_escape($r['heading']); ?></h4>
       <p><strong>Document supports:</strong> <?php echo fv_r381_escape($r['claim']); ?></p>
       <p class="fv-a381__boundary"><strong>Does not establish:</strong> <?php echo fv_r381_escape($r['boundary']); ?></p>
       <details class="fv-a381__drawer" data-fv-source-drawer>
        <summary>Source custody and limitations — record <?php echo fv_r381_escape($j+1); ?></summary>
        <div class="fv-a381__drawerbody">
         <p><strong>Role:</strong> <?php echo fv_r381_escape($r['evidence_role']); ?></p>
         <p><strong>Catalog distinction:</strong> <?php echo fv_r381_escape($r['catalog_note']); ?></p>
         <p><a data-fv-nasa-source href="<?php echo fv_r381_escape($r['evidence_url']); ?>" rel="noopener noreferrer">Read NASA evidence for record <?php echo fv_r381_escape($j+1); ?></a></p>
         <?php if ($r['context_url'] !== ''): ?>
          <p><strong>Later contextual account, not primary proof:</strong> <?php echo fv_r381_escape($r['context_role']); ?></p>
          <p><a href="<?php echo fv_r381_escape($r['context_url']); ?>" rel="noopener noreferrer">Read separately labeled NASA context</a></p>
         <?php endif; ?>
         <p><strong>Rights:</strong> A link for source inspection is not a license to reproduce photographs or NASA identifiers and does not indicate NASA endorsement.</p>
        </div>
       </details>
       <p class="fv-a381__print"><strong>Print source:</strong> <a href="<?php echo fv_r381_escape($r['evidence_url']); ?>"><?php echo fv_r381_escape($r['evidence_role']); ?></a></p>
      </article>
     </li>
    <?php endfor; ?>
    </ol>
   </section>
  <?php endforeach; ?>
  <aside class="fv-a381__method" aria-label="Research interpretation"><h3>A question worth keeping open</h3>
   <p>The Board identified an electrical arc as the most probable initiator but did not conclusively identify the specific ignition source. An interpretation cannot become a confirmed physical finding just because a later photograph or story appears persuasive.</p>
   <p><strong>Suggested classroom comparison:</strong> Select one finding and its stated limitation; explain what additional evidence would be required to strengthen the conclusion. This is a free research prompt, not a paid lesson kit.</p>
  </aside>
  <p class="fv-a381__cta"><a data-fv-free-cta href="<?php echo fv_r381_escape(FV_R381_FREE); ?>">Continue to the complete, free Apollo 1 investigation</a></p>
  <p class="fv-a381__caveat">A future educator dossier has not been verified as purchasable or rights-cleared. No purchase, subscriber or revenue outcome is claimed.</p>
 </div>
</section>
<?php return (string) ob_get_clean();
}

function fv_r381_shortcode($atts = array()): string {
    return fv_r381_render(function_exists('fv_r377_records') ? fv_r377_records() : null);
}
function fv_r381_assets_verified(): bool {
    $css = __DIR__ . '/assets/atlas.css'; $js = __DIR__ . '/assets/atlas.js';
    foreach (array($css=>FV_R381_CSS_SHA256, $js=>FV_R381_JS_SHA256) as $file=>$sha) {
        if (!is_file($file) || is_link($file) || !is_readable($file) || !hash_equals($sha,hash_file('sha256',$file))) { return false; }
    }
    return true;
}
function fv_r381_enqueue(): void {
    if (!function_exists('fv_r377_environment') || !fv_r377_environment()
        || !fv_r381_assets_verified() || !fv_r381_approved(function_exists('fv_r377_records') ? fv_r377_records() : null)
        || !function_exists('is_singular') || !is_singular() || !function_exists('get_queried_object_id')
        || !function_exists('get_post') || !function_exists('has_shortcode')
        || !function_exists('wp_enqueue_style') || !function_exists('wp_enqueue_script')
        || !function_exists('plugins_url')) { return; }
    $post = get_post((int)get_queried_object_id());
    if (!is_object($post) || !is_string($post->post_content ?? null) || !has_shortcode($post->post_content,FV_R381_TAG)) { return; }
    wp_enqueue_style('fv-apollo-r381-atlas',plugins_url('assets/atlas.css',__FILE__),array(),'r381-sealed-1');
    wp_enqueue_script('fv-apollo-r381-atlas',plugins_url('assets/atlas.js',__FILE__),array(),'r381-sealed-1',true);
}
if (function_exists('add_action')) {
    add_action('plugins_loaded', static function (): void {
        if (!function_exists('fv_r377_environment') || !fv_r377_environment()
          || !function_exists('add_shortcode') || !function_exists('shortcode_exists')
          || shortcode_exists(FV_R381_TAG)) { return; }
        add_shortcode(FV_R381_TAG,'fv_r381_shortcode');
        add_action('wp_enqueue_scripts','fv_r381_enqueue',1);
    },55);
}
