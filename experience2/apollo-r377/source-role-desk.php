<?php
/**
 * FV Apollo Experience R377 — source-role distinction for Research Desk, STAGING ONLY.
 * Independent of PR #158, the R376 gate, homepage #49 and any WordPress production plugin.
 * No remote requests, images, maps, transactions, analytics, e-mail, or data mutation.
 */
if (!defined('ABSPATH')) { exit; }

const FV_R377_SOURCE_SHA256 = '60bfa330398b7684463c95afcc7e6ef347d44f22d5a2f1350286a660edb3a76f';
const FV_R377_FREE_URL = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
const FV_R377_TAG = 'fv_apollo_source_role_desk_r377';

function fv_r377_esc($text): string {
    return htmlspecialchars((string) $text, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

function fv_r377_fallback(): string {
    return '<section class="fv-r377" aria-label="Apollo source verification unavailable">'
        . '<h2>Source review unavailable</h2><p>Source relationships could not be verified; no historical evidence is displayed.</p>'
        . '<p><a data-fv-free-cta href="'.fv_r377_esc(FV_R377_FREE_URL).'">Read the existing free Apollo 1 investigation</a></p></section>';
}

/** Fail closed on historical claims, fail open to existing free investigation. */
function fv_r377_records(?string $path = null): ?array {
    $path = $path ?? (__DIR__ . '/custody.json');
    if (!is_file($path) || is_link($path) || !is_readable($path)) { return null; }
    $bytes = file_get_contents($path);
    if (!is_string($bytes) || !hash_equals(FV_R377_SOURCE_SHA256, hash('sha256', $bytes))) { return null; }
    $data = json_decode($bytes, true);
    if (!is_array($data) || ($data['schema'] ?? null) !== 'fv.apollo.research-desk.source-custody.v1'
        || !isset($data['records']) || !is_array($data['records']) || count($data['records']) !== 6) { return null; }
    $ids = array('01-ground-test','02-oxygen','03-fire-sequence','04-hatch','05-ignition','06-testing');
    $approved = array(
        'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/',
        'https://www.nasa.gov/history/55-years-ago-tragedy-on-the-launch-pad/',
        'https://www.nasa.gov/history/apollo-1-crew-honored-in-new-tribute-exhibit/',
        'https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/',
    );
    foreach ($data['records'] as $i => $record) {
        if (!is_array($record) || ($record['id'] ?? null) !== $ids[$i]) { return null; }
        foreach (array('heading','kind','claim','boundary','evidence_role','catalog_note') as $k) {
            if (!isset($record[$k]) || !is_string($record[$k]) || trim($record[$k]) === '') { return null; }
        }
        if (!isset($record['evidence_url']) || !is_string($record['evidence_url']) ||
            !in_array($record['evidence_url'], $approved, true)) { return null; }
        if (!isset($record['context_url'], $record['context_role']) ||
            !is_string($record['context_url']) || !is_string($record['context_role']) ||
            ($record['context_url'] !== '' && !in_array($record['context_url'], $approved, true)) ||
            ($record['context_url'] === '') !== ($record['context_role'] === '')) { return null; }
    }
    return $data['records'];
}

/** Render has no client-side dependency; native details reveal full source meaning. */
function fv_r377_render(?array $records): string {
    if ($records === null || count($records) !== 6) { return fv_r377_fallback(); }
    // Revalidate canonical structure, never render an arbitrary externally supplied array.
    $sealed = fv_r377_records();
    if ($sealed === null || $records !== $sealed) { return fv_r377_fallback(); }
    static $instance = 0;
    $instance++;
    $uid = 'fv-r377-' . $instance;
    ob_start(); ?>
<section class="fv-r377" data-fv-r377 aria-labelledby="<?php echo fv_r377_esc($uid); ?>-title">
 <div class="fv-r377__inner">
  <p class="fv-r377__kicker">APOLLO 1 · RESEARCH DESK · SOURCE ROLES</p>
  <h2 id="<?php echo fv_r377_esc($uid); ?>-title">What the record shows—and what a photo cannot prove</h2>
  <p class="fv-r377__intro">Six reviewed findings distinguish a primary investigation from later NASA histories and photograph catalog entries. An image catalog record is not telemetry or evidence of an ignition point. No archival images, NASA logos or geographic connections are used.</p>
  <ol class="fv-r377__grid">
  <?php foreach ($records as $index => $record): ?>
   <li class="fv-r377__item" data-fv-r377-record>
    <article>
     <p class="fv-r377__number">SOURCE <?php echo fv_r377_esc(sprintf('%02d', $index + 1)); ?> / 06 · <?php echo fv_r377_esc($record['kind']); ?></p>
     <h3><?php echo fv_r377_esc($record['heading']); ?></h3>
     <p><strong>Supported:</strong> <?php echo fv_r377_esc($record['claim']); ?></p>
     <p class="fv-r377__boundary"><strong>Limit:</strong> <?php echo fv_r377_esc($record['boundary']); ?></p>
     <details data-fv-r377-source>
      <summary>Inspect source role and limitations for record <?php echo fv_r377_esc($index + 1); ?></summary>
      <div class="fv-r377__source">
       <p><strong>Supports the claim:</strong> <?php echo fv_r377_esc($record['evidence_role']); ?></p>
       <p><a data-fv-r377-evidence href="<?php echo fv_r377_esc($record['evidence_url']); ?>" rel="noopener noreferrer">Read NASA evidence for record <?php echo fv_r377_esc($index + 1); ?></a></p>
       <?php if ($record['context_url'] !== ''): ?>
        <p><strong>Additional context (not primary proof):</strong> <?php echo fv_r377_esc($record['context_role']); ?></p>
        <p><a data-fv-r377-context href="<?php echo fv_r377_esc($record['context_url']); ?>" rel="noopener noreferrer">Read separately labeled NASA context</a></p>
       <?php endif; ?>
       <p><strong>Image-catalog limitation:</strong> <?php echo fv_r377_esc($record['catalog_note']); ?></p>
       <p><strong>Rights:</strong> External links provide research access only, not a license to reproduce photography, a permission to use NASA identifiers or an endorsement of commercial offers.</p>
      </div>
     </details>
     <p class="fv-r377__print"><strong>Evidence source:</strong> <a href="<?php echo fv_r377_esc($record['evidence_url']); ?>"><?php echo fv_r377_esc($record['evidence_role']); ?></a></p>
    </article>
   </li>
  <?php endforeach; ?>
  </ol>
  <p class="fv-r377__method">Source-role audit corrects the risk that NASA photograph S66-58038 could be mistaken for an instrument record. All historical records remain freely inspectable. This is an independent staging review of the Research Desk source model, not a change to PR #158.</p>
  <p class="fv-r377__cta"><a data-fv-free-cta href="<?php echo fv_r377_esc(FV_R377_FREE_URL); ?>">Read the full free Apollo 1 investigation</a></p>
  <p class="fv-r377__disclaimer">An educator dossier is a proposed future offer, not a verified purchasable product. No NASA endorsement or paid conversion is claimed.</p>
 </div>
</section>
<?php return (string) ob_get_clean();
}

function fv_r377_environment(): bool {
    if (!defined('FV_R377_STAGING_ENABLED') || FV_R377_STAGING_ENABLED !== true ||
        !defined('FV_R377_APPROVED_HOST') || !function_exists('wp_get_environment_type') ||
        !function_exists('home_url') || wp_get_environment_type() !== 'staging') { return false; }
    $host = FV_R377_APPROVED_HOST;
    if (!is_string($host) || !preg_match('/^[a-z0-9][a-z0-9.-]{1,250}[a-z0-9]$/D', $host) ||
        in_array($host, array('finalvestige.com','www.finalvestige.com','localhost','127.0.0.1'),true)) { return false; }
    $url = parse_url(home_url('/'));
    return is_array($url) && ($url['scheme'] ?? '') === 'https' && ($url['host'] ?? '') === $host &&
        !isset($url['user']) && !isset($url['pass']) && (!isset($url['port']) || (int) $url['port'] === 443);
}

function fv_r377_shortcode($atts = array()): string {
    return fv_r377_render(fv_r377_records());
}

function fv_r377_enqueue(): void {
    if (!fv_r377_environment() || !function_exists('is_singular') || !is_singular() ||
        !function_exists('get_post') || !function_exists('get_queried_object_id') ||
        !function_exists('has_shortcode') || !function_exists('wp_enqueue_style') || !function_exists('plugins_url')) { return; }
    $post = get_post((int)get_queried_object_id());
    if (!is_object($post) || !is_string($post->post_content ?? null) ||
        !has_shortcode($post->post_content,FV_R377_TAG) || fv_r377_records() === null) { return; }
    wp_enqueue_style('fv-apollo-r377-source-role',plugins_url('assets/source-role.css',__FILE__),array(),'r377-reviewed-1');
}

// No registration on production or wrong host; do not overwrite an existing shortcode owner.
if (function_exists('add_action')) {
    add_action('plugins_loaded', static function (): void {
        if (!fv_r377_environment() || !function_exists('add_shortcode') || !function_exists('shortcode_exists') ||
            shortcode_exists(FV_R377_TAG)) { return; }
        add_shortcode(FV_R377_TAG, 'fv_r377_shortcode');
        add_action('wp_enqueue_scripts','fv_r377_enqueue',1);
    },50);
}
