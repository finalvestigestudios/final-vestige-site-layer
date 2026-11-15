<?php
/**
 * FV Apollo R381 · source-backed journey bridge (STAGING RESEARCH ONLY).
 * Independent shortcode, never overwrites PR #158, homepage #49 or R377 owner.
 * No telemetry, checkout, image reproduction, geography, remote fetches or writes.
 */
if (!defined('ABSPATH')) { exit; }
const FV_R381_TAG = 'fv_apollo_evidence_to_investigation_r381';
const FV_R381_FREE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';

function fv_r381_fallback(): string {
    return '<section class="fv-r381" aria-label="Apollo source review unavailable"><h2>Research records unavailable</h2><p>The evidence path cannot be verified at present. The original investigation remains available.</p><p><a data-fv-r381-next href="'.FV_R381_FREE.'">Read the free Apollo 1 investigation</a></p></section>';
}

/** Only exact sealed R377 records; never trust a caller-supplied array. */
function fv_r381_verified(?array $records): bool {
    if (!function_exists('fv_r377_records') || $records === null) { return false; }
    $canonical = fv_r377_records();
    if ($canonical === null || $records !== $canonical || count($canonical) !== 6) { return false; }
    $id = array('01-ground-test', '05-ignition', '06-testing');
    $index = array(0, 4, 5);
    $url = array(
        'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/',
        'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/',
        'https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/',
    );
    foreach ($index as $pos => $n) {
        if (($canonical[$n]['id'] ?? '') !== $id[$pos] || ($canonical[$n]['evidence_url'] ?? '') !== $url[$pos]) { return false; }
    }
    return true;
}

function fv_r381_escape($v): string {
    return htmlspecialchars((string)$v, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

/** Compact evidence -> next-step proof, not a stand-in for the entire Research Desk. */
function fv_r381_render(?array $records): string {
    if (!fv_r381_verified($records)) { return fv_r381_fallback(); }
    static $serial = 0; $serial++;
    $uid = 'fv-r381-' . $serial;
    $picked = array($records[0], $records[4], $records[5]);
    $type = array('1967 investigation', '1967 cause finding', '2018 later-test account');
    $why = array(
        'Establishes what kind of test was underway; does not determine the ignition source.',
        'Records a probable electrical arc while preserving the unidentified exact initiator.',
        'Documents later deliberate tests, not three-digit fire incidents in January 1967.',
    );
    ob_start(); ?>
<section class="fv-r381" data-fv-r381 aria-labelledby="<?php echo fv_r381_escape($uid); ?>-title">
 <div class="fv-r381__wrap">
  <p class="fv-r381__eyebrow">APOLLO 1 / SOURCE-VERIFIED PATH</p>
  <h2 id="<?php echo fv_r381_escape($uid); ?>-title">Three records. One clear next step.</h2>
  <p class="fv-r381__lede">Before reading the full investigation, examine what NASA's records establish—and which conclusions they do not support. The 1967 Board report and later engineering history are different evidence types.</p>
  <ol class="fv-r381__steps">
  <?php foreach ($picked as $i => $r): ?>
   <li data-fv-r381-item>
    <article>
     <p class="fv-r381__meta"><?php echo fv_r381_escape(sprintf('%02d / 03', $i + 1)); ?> · <?php echo fv_r381_escape($type[$i]); ?></p>
     <h3><?php echo fv_r381_escape($r['heading']); ?></h3>
     <p><?php echo fv_r381_escape($r['claim']); ?></p>
     <p class="fv-r381__limit"><strong>Evidence limit:</strong> <?php echo fv_r381_escape($r['boundary']); ?></p>
     <details data-fv-r381-drawer>
      <summary>Review source custody and rights for record <?php echo (int)$i + 1; ?></summary>
      <div class="fv-r381__drawer">
       <p><strong>Source role:</strong> <?php echo fv_r381_escape($r['evidence_role']); ?></p>
       <p><strong>Why this record:</strong> <?php echo fv_r381_escape($why[$i]); ?></p>
       <p><a data-fv-r381-nasa href="<?php echo fv_r381_escape($r['evidence_url']); ?>" rel="noopener noreferrer">Open the NASA source document</a></p>
       <p><strong>Media rights:</strong> Linking to NASA documentation is not a license to reproduce images or use NASA marks in commercial products.</p>
      </div>
     </details>
     <p class="fv-r381__print"><strong>Document:</strong> <a href="<?php echo fv_r381_escape($r['evidence_url']); ?>"><?php echo fv_r381_escape($r['evidence_url']); ?></a></p>
    </article>
   </li>
  <?php endforeach; ?>
  </ol>
  <div class="fv-r381__next">
   <p class="fv-r381__note">The full reporting stays free. A classroom evidence kit is only a future proposal—not a product currently available to purchase.</p>
   <p><a data-fv-r381-next href="<?php echo FV_R381_FREE; ?>">Continue to the free Apollo 1 investigation</a></p>
  </div>
 </div>
</section>
<?php return (string)ob_get_clean();
}

function fv_r381_shortcode(): string {
    if (!function_exists('fv_r377_environment') || !fv_r377_environment()) { return fv_r381_fallback(); }
    return fv_r381_render(function_exists('fv_r377_records') ? fv_r377_records() : null);
}

/** Staging-only; direct post shortcodes only. No overwrite of prior shortcode owners. */
function fv_r381_prehead_assets(): void {
    if (!function_exists('fv_r377_environment') || !fv_r377_environment() ||
        !function_exists('is_singular') || !is_singular() ||
        !function_exists('get_queried_object_id') || !function_exists('get_post') ||
        !function_exists('has_shortcode') || !function_exists('wp_enqueue_style') ||
        !function_exists('plugins_url') || !fv_r381_verified(function_exists('fv_r377_records') ? fv_r377_records() : null)) { return; }
    $post = get_post((int)get_queried_object_id());
    if (!is_object($post) || !is_string($post->post_content ?? null) || !has_shortcode($post->post_content, FV_R381_TAG)) { return; }
    wp_enqueue_style('fv-apollo-r381',plugins_url('assets/evidence-to-investigation.css',__FILE__),array(),'r381-review-1');
}
if (function_exists('add_action')) {
    add_action('plugins_loaded', static function (): void {
        if (!function_exists('fv_r377_environment') || !fv_r377_environment() || !function_exists('fv_r377_records') ||
            !fv_r381_verified(fv_r377_records()) || !function_exists('shortcode_exists') ||
            shortcode_exists(FV_R381_TAG) || !function_exists('add_shortcode')) { return; }
        add_shortcode(FV_R381_TAG,'fv_r381_shortcode');
        add_action('wp_enqueue_scripts','fv_r381_prehead_assets',4);
    },95);
}
