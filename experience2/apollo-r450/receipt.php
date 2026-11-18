<?php
/**
 * R450 noncommercial evidence-receipt companion to the R449 Apollo staging journey.
 * Source-only prototype; never registers on a production WordPress environment.
 */
if (!defined('ABSPATH')) { return; }
const FV_R450_FREE_ARTICLE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
const FV_R450_DEPENDENCIES = [
    'apollo-r449/journey.php' => 'd92449dc6d557437210b3f6ecd61e5459fdceb29247ccf3bb17ce9ba6798e4bf',
    'apollo-r448/manifest.json' => '744ec9c2ca46693f116c7ea5a1edf4ec3416083384e11ade0d0b63ca900a9411',
    'apollo-r448/crosswalk.php' => '69e7c1b4130445a56b2e869ee2c4eae79c886679de1ee2e669cb818cab937536',
    'apollo-r440/staging-educator-intent.php' => '835460b85afa4305f5419f09caad0fb8839202051359251d4c173954ff9ffa87',
];
const FV_R450_CSS_SHA256 = '9fe38bb1e875b803dcd21e7ff93c8c6e39a4f13fcb739356d2475b9ad437dd7c';
const FV_R450_JS_SHA256 = '91f406195c85739c30be85f2537ed7bd6a1ca7e06058c540df20391866be4bb2';
function fv_r450_escape($value): string { return htmlspecialchars((string)$value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); }
function fv_r450_fallback(): string {
    return '<p class="fv-r450-fallback">The research receipt is unavailable. <a href="'.FV_R450_FREE_ARTICLE.'">Read the free Apollo 1 investigation</a>.</p>';
}
function fv_r450_file_ok(string $path, string $expected): bool {
    $root = realpath(dirname(__DIR__));
    if (!$root || !is_dir($root) || is_link(dirname(__DIR__)) || !preg_match('~^apollo-r(440|448|449)/[a-z0-9._/-]+$~D', $path)) return false;
    $cursor = $root;
    foreach (explode('/', $path) as $part) {
        if ($part === '' || $part === '.' || $part === '..') return false;
        $cursor .= '/'.$part;
        if (is_link($cursor)) return false;
    }
    $real = realpath($cursor);
    if (!$real || strncmp($real, $root.'/', strlen($root)+1) !== 0 || !is_file($real) || !is_readable($real)) return false;
    $hash = hash_file('sha256', $real);
    return is_string($hash) && hash_equals($expected, $hash);
}
function fv_r450_ready(): bool {
    foreach (FV_R450_DEPENDENCIES as $path=>$sha) if (!fv_r450_file_ok($path, $sha)) return false;
    foreach (['assets/receipt.css'=>FV_R450_CSS_SHA256, 'assets/receipt.js'=>FV_R450_JS_SHA256] as $path=>$sha) {
        $f = __DIR__.'/'.$path;
        if (is_link($f) || !is_file($f) || !is_readable($f) || !hash_equals($sha, (string)hash_file('sha256',$f))) return false;
    }
    return true;
}
function fv_r450_allowed(): bool {
    return defined('FV_R450_ENABLE_STAGING') && FV_R450_ENABLE_STAGING === true
       && defined('FV_R450_STAGING_PAGE_ID') && is_int(FV_R450_STAGING_PAGE_ID) && FV_R450_STAGING_PAGE_ID > 0
       && function_exists('wp_get_environment_type') && wp_get_environment_type() === 'staging'
       && function_exists('is_singular') && is_singular()
       && function_exists('get_queried_object_id') && get_queried_object_id() === FV_R450_STAGING_PAGE_ID;
}
function fv_r450_boot(): bool {
    if (!fv_r450_ready()) return false;
    if (!function_exists('fv_r449_render')) require_once dirname(__DIR__).'/apollo-r449/journey.php';
    if (!function_exists('fv_r448_data')) require_once dirname(__DIR__).'/apollo-r448/crosswalk.php';
    return function_exists('fv_r449_render') && function_exists('fv_r449_allowed') && fv_r449_allowed()
       && function_exists('fv_r448_data') && fv_r448_data() !== null;
}
function fv_r450_render(): string {
    // A page receives at most one investigation CTA, even if the shortcode is duplicated.
    static $rendered = false;
    if ($rendered) return '';
    if (!fv_r450_allowed() || !fv_r450_boot()) return fv_r450_fallback();
    $journey = fv_r449_render();
    $records = fv_r448_data();
    if (!$records || substr_count($journey, 'data-fv-r449') !== 1
        || substr_count($journey, 'href="'.FV_R450_FREE_ARTICLE.'"') !== 1
        || substr_count($journey, 'data-fv-r448-card') !== 4
        || substr_count($journey, 'data-r440-root') !== 1) return fv_r450_fallback();
    static $index = 0;
    if (++$index > 20) return fv_r450_fallback();
    $id = 'fv-r450-'.$index;
    ob_start(); ?>
<section class="fv-r450" data-fv-r450 aria-labelledby="<?php echo $id; ?>-heading">
  <h2 id="<?php echo $id; ?>-heading">Take the evidence trail into the classroom</h2>
  <p class="fv-r450__intro">An original, text-only source receipt. It separates source dates from historical events and includes limitations your students can challenge. No NASA images or endorsements; editorial review remains pending.</p>
  <details class="fv-r450__details">
    <summary>View four-source research receipt and interpretation checks</summary>
    <div class="fv-r450__records" data-r450-records>
    <?php foreach ($records['claims'] as $r): ?>
      <section class="fv-r450__record" data-r450-claim="<?php echo fv_r450_escape($r['id']); ?>">
        <h3><?php echo fv_r450_escape($r['title']); ?></h3>
        <p><strong>Date and type:</strong> <time datetime="<?php echo fv_r450_escape($r['date']); ?>"><?php echo fv_r450_escape($r['date']); ?></time> — <?php echo fv_r450_escape($r['date_context']); ?>; <?php echo fv_r450_escape($r['source_kind']); ?></p>
        <p><strong>Supported:</strong> <?php echo fv_r450_escape($r['supported']); ?></p>
        <p><strong>Not established:</strong> <?php echo fv_r450_escape($r['not_supported']); ?></p>
        <p><a href="<?php echo fv_r450_escape($r['source_url']); ?>" rel="noopener noreferrer">Official NASA source: <?php echo fv_r450_escape($r['source_title']); ?></a></p>
      </section>
    <?php endforeach; ?>
    </div>
  </details>
  <div class="fv-r450__export"><p>Use the source receipt for a student evidence check. Its text is original and free; the optional file download stays on this device and sends no answers to the website.</p>
    <div data-r450-export></div><p data-r450-status role="status" aria-live="polite"></p></div>
  <p class="fv-r450__note"><strong>Review state:</strong> Official NASA source identity cross-referenced; FV historical interpretation still requires independent editorial review. NASA media rights are not cleared for a sold product. The one next-step link to the free investigation appears above; this receipt adds no sales or signup action.</p>
</section>
<?php
    $receipt = (string)ob_get_clean();
    if (substr_count($receipt, 'data-r450-claim=') !== 4 || preg_match('~<form\b|<iframe\b|href\s*=\s*["\']https?://(?:[^"\']*payhip|[^"\']*checkout)~i', $receipt)) return fv_r450_fallback();
    $rendered = true;
    return $journey.$receipt;
}
function fv_r450_shortcode(): string { return fv_r450_render(); }
function fv_r450_enqueue(): void {
    if (!fv_r450_allowed() || !fv_r450_boot() || !function_exists('wp_enqueue_style') || !function_exists('wp_enqueue_script') || !function_exists('plugins_url')) return;
    // R449 owns inherited assets and loads only on the opt-in staging page.
    if (function_exists('fv_r449_enqueue')) fv_r449_enqueue();
    wp_enqueue_style('fv-r450-receipt', plugins_url('assets/receipt.css', __FILE__), [], 'r450');
    wp_enqueue_script('fv-r450-receipt', plugins_url('assets/receipt.js', __FILE__), [], 'r450', true);
}
if (function_exists('wp_get_environment_type') && wp_get_environment_type()==='staging' && function_exists('add_shortcode')) {
    add_shortcode('fv_apollo_source_receipt_r450', 'fv_r450_shortcode');
    if (function_exists('add_action')) add_action('wp_enqueue_scripts', 'fv_r450_enqueue', 30);
}
