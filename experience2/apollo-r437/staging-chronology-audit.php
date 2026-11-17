<?php
/**
 * FV Apollo R437 / source-date ChronologyRail, staging-only and opt-in.
 * Renders verified R436 evidence plus a source-date audit; never writes WP data.
 */
if (!defined('ABSPATH')) { exit; }
const FV_R437_ARTICLE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
const FV_R437_PARENT = [
    'apollo-r436/staging-source-proof.php' => '0d725f8a2316d83ebed0aaaa021cffe74c4a463b',
    'apollo-r436/assets/source-proof.css' => '9baf61f57ed40b7c8798f6e5b0f832bcb26f9162',
];
const FV_R437_ASSETS = [
    'assets/chronology-audit.css' => '5da69288a2bd50995fcd2187cc662624e27b49aac68c7019b9aac7eab1369e70',
    'assets/chronology-audit.js' => '515350dc54788ab010e4f09ddee3fe56dc4b61a56ba94a8f13c443caa9ae89fc',
];
function fv_r437_e(string $s): string { return htmlspecialchars($s, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); }
function fv_r437_fallback(): string {
    return '<p class="fv-r437-fallback">The source-date audit is unavailable. <a href="'.FV_R437_ARTICLE.'">Read the free Apollo 1 investigation</a>.</p>';
}
function fv_r437_allowed(): bool {
    return defined('FV_R437_ENABLED') && FV_R437_ENABLED === true
        && defined('FV_R437_STAGING_PAGE_ID') && is_int(FV_R437_STAGING_PAGE_ID) && FV_R437_STAGING_PAGE_ID > 0
        && function_exists('wp_get_environment_type') && wp_get_environment_type() === 'staging'
        && function_exists('is_singular') && is_singular()
        && function_exists('get_queried_object_id') && get_queried_object_id() === FV_R437_STAGING_PAGE_ID;
}
function fv_r437_verified_file(string $base, string $relative, string $expected, bool $gitBlob): bool {
    $baseReal = realpath($base);
    if ($baseReal === false || !is_dir($baseReal) || is_link($base)) return false;
    $path = $baseReal;
    foreach (explode('/', $relative) as $segment) {
        if ($segment === '' || $segment === '.' || $segment === '..') return false;
        $path .= '/'.$segment;
        if (is_link($path)) return false;
    }
    $real = realpath($path);
    if ($real === false || !is_file($real) || !is_readable($real)
        || strncmp($real, $baseReal.'/', strlen($baseReal) + 1) !== 0) return false;
    $bytes = file_get_contents($real);
    if (!is_string($bytes)) return false;
    $actual = $gitBlob ? sha1('blob '.strlen($bytes)."\0".$bytes) : hash('sha256', $bytes);
    return hash_equals($expected, $actual);
}
function fv_r437_verify(): bool {
    foreach (FV_R437_PARENT as $file => $blob) {
        if (!fv_r437_verified_file(dirname(__DIR__), $file, $blob, true)) return false;
    }
    foreach (FV_R437_ASSETS as $file => $sha256) {
        if (!fv_r437_verified_file(__DIR__, $file, $sha256, false)) return false;
    }
    return true;
}
function fv_r437_parent(): bool {
    if (!fv_r437_verify()) return false;
    $expected = realpath(dirname(__DIR__).'/apollo-r436/staging-source-proof.php');
    if ($expected === false) return false;
    if (!function_exists('fv_r436_render')) require_once $expected;
    if (!function_exists('fv_r436_render') || !function_exists('fv_r436_parent')) return false;
    $loaded = new ReflectionFunction('fv_r436_render');
    if (realpath((string) $loaded->getFileName()) !== $expected) return false;
    return fv_r436_parent();
}
/** Dates denote four different event/document classes; no invented geographic relations. */
function fv_r437_records(): array {
    return [
        [ '1967-01-27', 'January 27, 1967', 'Event date', 'incident', 'Ground-test fire',
          'The crew died during a ground-test fire in the Apollo command module.',
          'This date does not establish the ignition point, and a training photograph does not capture the fire itself.',
          'https://sma.nasa.gov/sma-disciplines/accllp/apollo-1', 'NASA Safety: Apollo 1 investigation overview' ],
        [ '1967', '1967 · Review Board findings', 'Report findings (year, not claimed release day)', 'incident', 'Probable is not proven',
          'The Review Board called an electrical arc the most probable initiator; it did not conclusively identify one ignition source.',
          'Do not turn a probable mechanism into a claim that one precise wire or location was proven.',
          'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/', 'NASA: Apollo 204 Review Board report' ],
        [ '2017-01-27', 'January 27, 2017', 'Memorial opening date', 'retrospective', 'The later public exhibit',
          'NASA opened a tribute at the Apollo/Saturn V Center, including the original spacecraft hatch.',
          'A 2017 exhibit image proves what was displayed later; it is not a contemporary photograph of the accident.',
          'https://www.nasa.gov/news-release/nasa-unveils-tribute-to-crew-of-apollo-1/', 'NASA: 2017 tribute announcement' ],
        [ '2018-02-14', 'February 14, 2018', 'Publication date (tests occurred earlier)', 'retrospective', 'Retrospective flammability account',
          'NASA described 102 deliberate Command Module ignitions conducted from December 1967 to February 1968.',
          'The 2018 publication date and later mock-up experiments cannot be substituted for evidence of the January 1967 initiating spark.',
          'https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/', 'NASA: 50 Years Ago — Apollo Flammability Tests' ],
    ];
}
function fv_r437_audit(int $instance): string {
    $id = 'fv-r437-'.$instance;
    $html = '<section class="fv-r437__audit" data-fv-r437 aria-labelledby="'.$id.'-title">'
        .'<p class="fv-r437__kicker">RESEARCH DESK / DATE &amp; CLAIM CUSTODY</p>'
        .'<h2 id="'.$id.'-title">Four records. Four different kinds of dates.</h2>'
        .'<p class="fv-r437__intro">Follow the evidence without treating a photo, a report, an exhibit, and a later retrospective as interchangeable proof. Select a time period to compare sources; all four records remain available without JavaScript.</p>'
        .'<p class="fv-r437__legend">Chronological order follows the date shown, which may describe an event, a finding year, an exhibit opening, or a publication.</p>'
        .'<ol class="fv-r437__rail" data-r437-records aria-label="Dated Apollo source evidence">';
    foreach (fv_r437_records() as $record) {
        [$date,$dateLabel,$type,$period,$heading,$claim,$limit,$url,$sourceLabel] = $record;
        $html .= '<li class="fv-r437__plate" data-period="'.fv_r437_e($period).'">'
            .'<p class="fv-r437__date"><time datetime="'.fv_r437_e($date).'">'.fv_r437_e($dateLabel).'</time></p>'
            .'<p class="fv-r437__type">'.fv_r437_e($type).'</p>'
            .'<h3>'.fv_r437_e($heading).'</h3><p>'.fv_r437_e($claim).'</p>'
            .'<details><summary>Evidence boundary</summary><p>'.fv_r437_e($limit).'</p></details>'
            .'<p class="fv-r437__print"><strong>Evidence boundary: </strong>'.fv_r437_e($limit).'</p>'
            .'<p><a href="'.fv_r437_e($url).'" rel="noopener noreferrer">'.fv_r437_e($sourceLabel).'</a></p></li>';
    }
    return $html.'</ol><p class="fv-r437__rights">Records link directly to NASA; no NASA media or identifying marks are reproduced. Links do not license commercial reuse, and NASA does not endorse FV. See <a href="https://www.nasa.gov/nasa-brand-center/advertising-guidelines/" rel="noopener noreferrer">NASA media and advertising guidance</a>. This free source experience contains no commercial offer.</p></section>';
}
function fv_r437_render(int $instance, array $campaign = []): string {
    if ($instance < 1 || $instance > 30 || !fv_r437_parent()) return fv_r437_fallback();
    $parent = fv_r436_render($instance, $campaign);
    $needle = '<details class="fv-r436__proof"';
    if (substr_count($parent, $needle) !== 1 || substr_count($parent, 'class="fv-r429__cta"') !== 1) return fv_r437_fallback();
    // Older verified layers repeat a precise 1967-04-05 board date, while NASA's
    // own sources distinguish the report's drafting, signature and release.
    // Correct every displayed upstream instance to an unambiguous finding year.
    // Fail open to the free investigation if the expected source shape changes.
    $unverifiedDate = 'datetime="1967-04-05">1967-04-05</time>';
    if (substr_count($parent, $unverifiedDate) !== 4) return fv_r437_fallback();
    $parent = str_replace($unverifiedDate, 'datetime="1967">1967 · Board findings</time>', $parent);
    return '<div class="fv-r437" data-fv-r437-shell>'.str_replace($needle, fv_r437_audit($instance).$needle, $parent).'</div>';
}
function fv_r437_shortcode(): string {
    if (!fv_r437_allowed() || !fv_r437_verify()) return fv_r437_fallback();
    $instance = ($GLOBALS['fv_r437_instances'] ?? 0) + 1;
    if (!is_int($instance) || $instance > 30) return fv_r437_fallback();
    $GLOBALS['fv_r437_instances'] = $instance;
    return fv_r437_render($instance, $_GET);
}
function fv_r437_enqueue(): void {
    if (!fv_r437_allowed() || !fv_r437_parent() || !function_exists('fv_r436_enqueue')
        || !function_exists('plugins_url') || !function_exists('wp_enqueue_style')
        || !function_exists('wp_enqueue_script')) return;
    fv_r436_enqueue();
    wp_enqueue_style('fv-r437-chronology', plugins_url('assets/chronology-audit.css', __FILE__), ['fv-r436-source-proof'], 'r437');
    wp_enqueue_script('fv-r437-chronology', plugins_url('assets/chronology-audit.js', __FILE__), [], 'r437', true);
}
if (function_exists('add_shortcode')) add_shortcode('fv_apollo_chronology_audit_r437', 'fv_r437_shortcode');
if (function_exists('add_action')) add_action('wp_enqueue_scripts', 'fv_r437_enqueue', 22);
