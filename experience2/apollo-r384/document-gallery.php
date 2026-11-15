<?php
/**
 * Apollo Experience 2.0 R384: staging-only, NASA-linked text-document gallery.
 * This is not a gallery of reproduced NASA photography or scanned copyrighted pages.
 * No collection, telemetry, commerce, background jobs or WordPress writes.
 */
if (!defined('ABSPATH')) { exit; }

const FV_R384_TAG = 'fv_apollo_source_gallery_r384';
const FV_R384_FREE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
const FV_R384_BOARD = 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/';
const FV_R384_TESTS = 'https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/';
const FV_R384_CSS_SHA256 = 'b684a4a463665c0f2f37f08cdf7ea9c73e91519ac9a14f1f04103130114bfa73';
const FV_R384_MEDIA = 'https://www.nasa.gov/nasa-brand-center/images-and-media/';

function fv_r384_h($v): string {
    return htmlspecialchars((string) $v, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}
function fv_r384_fallback(): string {
    return '<section class="fv-r384" aria-label="Apollo source gallery unavailable"><h2>Source gallery unavailable</h2>'
      . '<p>Source custody could not be verified; no documentary interpretation is displayed.</p>'
      . '<p><a data-fv-free-cta href="' . fv_r384_h(FV_R384_FREE) . '">Read the existing free Apollo 1 investigation</a></p></section>';
}
/** Do not trust shortcodes, query strings or mutable attributes as source records. */
function fv_r384_records() {
    if (!function_exists('fv_r377_environment') || !fv_r377_environment()
      || !function_exists('fv_r377_records') || !function_exists('fv_r381_approved')) { return false; }
    $records = fv_r377_records();
    if (!fv_r381_approved($records)) { return false; }
    $ids = array('01-ground-test','02-oxygen','03-fire-sequence','04-hatch','05-ignition','06-testing');
    foreach ($records as $i => $r) {
        if (!is_array($r) || ($r['id'] ?? '') !== $ids[$i]
          || ($r['evidence_url'] ?? '') !== ($i === 5 ? FV_R384_TESTS : FV_R384_BOARD)) { return false; }
        foreach (array('heading','claim','boundary','evidence_role','catalog_note','kind') as $field) {
            if (!isset($r[$field]) || !is_string($r[$field]) || trim($r[$field]) === '') { return false; }
        }
        // No unreviewed external contextual links or injected protocols.
        if (!in_array($r['context_url'] ?? '', array('',
          'https://www.nasa.gov/history/55-years-ago-tragedy-on-the-launch-pad/',
          'https://www.nasa.gov/history/apollo-1-crew-honored-in-new-tribute-exhibit/'), true)) { return false; }
    }
    return $records;
}
/** Native document details work with JavaScript completely disabled. */
function fv_r384_render(): string {
    $records = fv_r384_records();
    if ($records === false) { return fv_r384_fallback(); }
    static $instance = 0; $instance++;
    $prefix = 'fv-r384-' . $instance;
    $phases = array(
      array('key'=>'event', 'title'=>'January 27, 1967 · the test and fire', 'indices'=>array(0,1,2,3)),
      array('key'=>'finding', 'title'=>'1967 · what the Board could not prove', 'indices'=>array(4)),
      array('key'=>'later', 'title'=>'December 1967–February 1968 · later testing', 'indices'=>array(5)),
    );
    ob_start(); ?>
<section class="fv-r384" data-fv-r384-gallery aria-labelledby="<?php echo fv_r384_h($prefix); ?>-title">
 <div class="fv-r384__inner">
  <p class="fv-r384__eyebrow">FINAL VESTIGE STUDIOS / APOLLO EVIDENCE COLLECTION</p>
  <h2 id="<?php echo fv_r384_h($prefix); ?>-title">Six documented questions. <em>Two underlying NASA publications.</em></h2>
  <p class="fv-r384__intro">Browse the original 1967 investigation and NASA's later engineering account through six carefully separated questions. These are text-based source cards, not reproductions or an interactive geographic map.</p>
  <p class="fv-r384__rights"><strong>Source and rights notice:</strong> NASA hosts the linked material. NASA photography, identifiers and third-party media are <strong>not reproduced or commercially licensed by these links</strong>. This independent editorial collection is not endorsed by NASA. <a href="<?php echo fv_r384_h(FV_R384_MEDIA); ?>" rel="noopener noreferrer">NASA media-use guidance</a>.</p>
  <nav class="fv-r384__rail" aria-label="Three documented phases"><ol>
  <?php foreach ($phases as $phase): ?>
   <li><a href="#<?php echo fv_r384_h($prefix . '-' . $phase['key']); ?>"><?php echo fv_r384_h($phase['title']); ?></a></li>
  <?php endforeach; ?>
  </ol></nav>
  <?php foreach ($phases as $phase): ?>
   <section class="fv-r384__phase" id="<?php echo fv_r384_h($prefix . '-' . $phase['key']); ?>" aria-labelledby="<?php echo fv_r384_h($prefix . '-' . $phase['key']); ?>-heading">
    <h3 id="<?php echo fv_r384_h($prefix . '-' . $phase['key']); ?>-heading"><?php echo fv_r384_h($phase['title']); ?></h3>
    <ol class="fv-r384__grid">
    <?php foreach ($phase['indices'] as $index): $record = $records[$index]; ?>
     <li class="fv-r384__card" data-fv-r384-record data-fv-r384-source-id="<?php echo fv_r384_h($record['id']); ?>">
      <article>
       <p class="fv-r384__number">SOURCE QUESTION <?php echo fv_r384_h(sprintf('%02d',$index+1)); ?> / 06 · <?php echo fv_r384_h($record['kind']); ?></p>
       <h4><?php echo fv_r384_h($record['heading']); ?></h4>
       <p><strong>Document supports:</strong> <?php echo fv_r384_h($record['claim']); ?></p>
       <p class="fv-r384__limit"><strong>Does not establish:</strong> <?php echo fv_r384_h($record['boundary']); ?></p>
       <details class="fv-r384__drawer"><summary>Inspect custody and catalog limitations</summary>
        <p><strong>Source role:</strong> <?php echo fv_r384_h($record['evidence_role']); ?></p>
        <p><strong>What a photograph cannot prove:</strong> <?php echo fv_r384_h($record['catalog_note']); ?></p>
        <p>These are links to the original host; no NASA media or identifying marks are embedded.</p>
       </details>
       <p class="fv-r384__source"><a data-fv-r384-nasa href="<?php echo fv_r384_h($record['evidence_url']); ?>" rel="noopener noreferrer">Inspect NASA source for question <?php echo fv_r384_h($index+1); ?></a></p>
      </article>
     </li>
    <?php endforeach; ?>
    </ol>
   </section>
  <?php endforeach; ?>
  <aside class="fv-r384__next"><h3>Continue the investigation</h3><p>Compare a documented finding with its stated limitation before drawing a conclusion. The complete story remains free. A paid educator kit is not currently verified as an available offer.</p>
   <p><a data-fv-free-cta href="<?php echo fv_r384_h(FV_R384_FREE); ?>">Read the complete free Apollo 1 investigation</a></p>
  </aside>
 </div>
</section>
<?php return (string) ob_get_clean();
}
function fv_r384_shortcode($atts = array()): string { return fv_r384_render(); }
function fv_r384_assets_verified(): bool {
    $file = __DIR__ . '/assets/gallery.css';
    return is_file($file) && !is_link($file) && is_readable($file)
      && hash_equals(FV_R384_CSS_SHA256, hash_file('sha256',$file));
}
function fv_r384_enqueue(): void {
    if (fv_r384_records() === false || !fv_r384_assets_verified()
      || !function_exists('is_singular') || !is_singular()
      || !function_exists('get_queried_object_id') || !function_exists('get_post')
      || !function_exists('has_shortcode') || !function_exists('wp_enqueue_style')
      || !function_exists('plugins_url')) { return; }
    $post = get_post((int)get_queried_object_id());
    if (!is_object($post) || !is_string($post->post_content ?? null)
      || !has_shortcode($post->post_content,FV_R384_TAG)) { return; }
    wp_enqueue_style('fv-apollo-r384-gallery',plugins_url('assets/gallery.css',__FILE__),array(),'r384-reviewed-1');
}
if (function_exists('add_action')) {
    add_action('plugins_loaded', static function (): void {
        if (fv_r384_records() === false || !function_exists('add_shortcode')
          || !function_exists('shortcode_exists') || shortcode_exists(FV_R384_TAG)) { return; }
        add_shortcode(FV_R384_TAG,'fv_r384_shortcode');
        add_action('wp_enqueue_scripts','fv_r384_enqueue',5);
    },75);
}