<?php
/** R435: source-photo custody correction, staging only. No remote media, tracking or CMS writes. */
if (!defined('ABSPATH')) { exit; }
const FV_R435_ARTICLE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
const FV_R435_PARENT = [
  'apollo-r434/staging-research-route.php' => 'eca13090d34fb905ff3d82f240410c443ab0fc4b',
  'apollo-r434/assets/research-route.css' => '61b0260fa444fa33e66827220f2fe19b5e5800d9'
];
const FV_R435_CATALOG_SHA256 = '2d75ee450c733db4308738864d5677a42743f3da0a2249dc65e3219a4ca7d800';
function fv_r435_fallback(): string {
  return '<p class="fv-r435-fallback">The photo source index is unavailable. <a href="'.FV_R435_ARTICLE.'">Read the free Apollo 1 investigation</a>.</p>';
}
function fv_r435_allowed(): bool {
  return defined('FV_R435_ENABLED') && FV_R435_ENABLED === true
    && defined('FV_R435_STAGING_PAGE_ID') && is_int(FV_R435_STAGING_PAGE_ID) && FV_R435_STAGING_PAGE_ID > 0
    && function_exists('wp_get_environment_type') && wp_get_environment_type() === 'staging'
    && function_exists('is_singular') && is_singular()
    && function_exists('get_queried_object_id') && get_queried_object_id() === FV_R435_STAGING_PAGE_ID;
}
function fv_r435_verify(): bool {
  $root = realpath(dirname(__DIR__));
  if ($root === false) return false;
  foreach (FV_R435_PARENT as $relative => $expected) {
    $cursor = dirname(__DIR__);
    foreach (explode('/', $relative) as $segment) {
      $cursor .= '/'.$segment;
      if (is_link($cursor)) return false;
    }
    $path = realpath($cursor);
    if ($path === false || !is_file($path) || !is_readable($path)
      || strncmp($path, $root.DIRECTORY_SEPARATOR, strlen($root)+1) !== 0) return false;
    $bytes = file_get_contents($path);
    if (!is_string($bytes) || !hash_equals($expected, sha1('blob '.strlen($bytes)."\0".$bytes))) return false;
  }
  $catalog = __DIR__.'/source_catalog.json';
  if (is_link($catalog) || !is_file($catalog) || !is_readable($catalog)) return false;
  $bytes = file_get_contents($catalog);
  return is_string($bytes) && hash_equals(FV_R435_CATALOG_SHA256, hash('sha256', $bytes));
}
function fv_r435_catalog(): array {
  if (!fv_r435_verify()) return [];
  $raw = json_decode((string) file_get_contents(__DIR__.'/source_catalog.json'), true);
  if (!is_array($raw) || count($raw) !== 6) return [];
  $seen = [];
  foreach ($raw as $record) {
    if (!is_array($record)) return [];
    foreach (['id','date','kind','subject','url','limits','credit','media_reuse'] as $field) {
      if (!isset($record[$field]) || !is_string($record[$field]) || $record[$field] === '') return [];
    }
    if (!str_starts_with($record['url'], 'https://www.nasa.gov/image-detail/')
      || !preg_match('~^https://www\.nasa\.gov/image-detail/[a-z0-9_-]+/$~', $record['url'])
      || !preg_match('/^\d{4}-\d{2}(-\d{2})?$/', $record['date'])
      || !str_starts_with($record['media_reuse'], 'NOT REVIEWED')) return [];
    if (isset($seen[$record['id']])) return [];
    $seen[$record['id']] = true;
  }
  usort($raw, static fn($a,$b) => strcmp($a['date'],$b['date']));
  return $raw;
}
function fv_r435_parent(): bool {
  if (!fv_r435_verify()) return false;
  if (!empty($GLOBALS['fv_r435_parent_loaded'])) {
    return function_exists('fv_r434_render') && function_exists('fv_r434_parent') && fv_r434_parent();
  }
  if (function_exists('fv_r434_render') || function_exists('fv_r433_render')) return false;
  require_once dirname(__DIR__).'/apollo-r434/staging-research-route.php';
  if (!function_exists('fv_r434_parent') || !fv_r434_parent() || !function_exists('fv_r434_render')) return false;
  $GLOBALS['fv_r435_parent_loaded'] = true;
  return true;
}
function fv_r435_render(int $instance, array $campaign=[]): string {
  if ($instance < 1 || $instance > 30 || !fv_r435_parent()) return fv_r435_fallback();
  $records = fv_r435_catalog();
  if (count($records) !== 6) return fv_r435_fallback();
  $base = fv_r434_render($instance, $campaign);
  if (substr_count($base, 'class="fv-r429__cta"') !== 1
    || substr_count($base, 'class="fv-r434__deep"') !== 1
    || substr_count($base, 'class="fv-r434__next"') !== 1) return fv_r435_fallback();
  $escape = static fn(string $s): string => htmlspecialchars($s, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
  $id = 'fv-r435-'.$instance;
  $gallery = '<details class="fv-r435__catalog" data-fv-r435-catalog><summary>Inspect six NASA photograph records and what they cannot prove</summary>';
  $gallery .= '<p>These are links to NASA catalogue pages, not reproduced photographs. A source photograph is not automatically the source of a historical claim. Dates are the catalogue subject dates, not webpage publication dates.</p>';
  $gallery .= '<ol class="fv-r435__grid" aria-label="Dated source photo catalogue">';
  foreach ($records as $n => $r) {
    $gallery .= '<li class="fv-r435__plate"><span class="fv-r435__index">CATALOG '.($n+1).' / 6</span>';
    $gallery .= '<time datetime="'.$escape($r['date']).'">'.$escape($r['date']).'</time>';
    $gallery .= '<h3>'.$escape($r['subject']).'</h3><p class="fv-r435__kind">'.$escape($r['kind']).' · '.$escape($r['id']).'</p>';
    $gallery .= '<details class="fv-r435__drawer"><summary>Source custody, limits and reuse</summary><p><strong>What this image cannot prove:</strong> '.$escape($r['limits']).'</p>';
    $gallery .= '<p><strong>Catalogued credit:</strong> '.$escape($r['credit']).'</p><p><strong>Media status:</strong> '.$escape($r['media_reuse']).'</p></details>';
    $gallery .= '<a href="'.$escape($r['url']).'" rel="noopener noreferrer">Inspect original NASA catalogue</a></li>';
  }
  $gallery .= '</ol><p class="fv-r435__rights">No NASA photo files or logos are embedded. Indexing a NASA catalogue URL does not authorize a commercial digital-product reproduction, imply NASA endorsement or resolve third-party/publicity rights. Each photograph requires an individual rights check before use.</p></details>';
  $needle = '<details class="fv-r434__deep"';
  if (substr_count($base, $needle) !== 1) return fv_r435_fallback();
  return '<div class="fv-r435" data-fv-r435>'.str_replace($needle, $gallery.$needle, $base).'</div>';
}
function fv_r435_shortcode(): string {
  if (!fv_r435_allowed() || !fv_r435_verify()) return fv_r435_fallback();
  $n = ($GLOBALS['fv_r435_instance_count'] ?? 0) + 1;
  if (!is_int($n) || $n > 30) return fv_r435_fallback();
  $GLOBALS['fv_r435_instance_count'] = $n;
  return fv_r435_render($n, $_GET);
}
function fv_r435_enqueue(): void {
  if (!fv_r435_allowed() || !fv_r435_parent() || !function_exists('plugins_url') || !function_exists('wp_enqueue_style')) return;
  // Reuse exact upstream CSS and private notebook JS only after the whole source chain passes custody.
  if (!function_exists('fv_r434_enqueue')) return;
  fv_r434_enqueue();
  wp_enqueue_style('fv-r435-photo-custody', plugins_url('assets/photo-custody.css', __FILE__), ['fv-r434-source-route'], 'r435');
}
if (function_exists('add_shortcode')) add_shortcode('fv_apollo_photo_custody_r435', 'fv_r435_shortcode');
if (function_exists('add_action')) add_action('wp_enqueue_scripts', 'fv_r435_enqueue', 21);
