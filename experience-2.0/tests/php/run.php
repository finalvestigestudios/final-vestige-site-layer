<?php
/**
 * Harness that loads the plugin against minimal WordPress stubs and reports observations as JSON.
 * This is NOT WordPress. It proves the plugin's own logic; real-WordPress behaviour is covered separately.
 *
 * Usage: php run.php <plugin_dir> <scenario>
 * Scenarios: render | assets-hit | assets-miss | injection | fallback-probe
 */
$plugin_dir = rtrim( $argv[1], '/\\' ) . DIRECTORY_SEPARATOR;
$scenario   = $argv[2] ?? 'render';

define( 'ABSPATH', __DIR__ . '/' );
$GLOBALS['fvx_hooks']     = array();
$GLOBALS['fvx_shortcodes'] = array();
$GLOBALS['fvx_enqueued']  = array( 'style' => array(), 'script' => array() );
$GLOBALS['fvx_registered'] = array();
$GLOBALS['fvx_log']       = array();
$GLOBALS['fvx_post']      = null;
$GLOBALS['fvx_singular']  = false;

function plugin_dir_path( $f ) { global $plugin_dir; return $plugin_dir; }
function plugin_dir_url( $f ) { return 'https://example.test/wp-content/plugins/final-vestige-experience-2/'; }
function add_action( $hook, $cb, $prio = 10 ) { $GLOBALS['fvx_hooks'][ $hook ][] = array( $prio, $cb ); }
function add_shortcode( $tag, $cb ) { $GLOBALS['fvx_shortcodes'][ $tag ] = $cb; }
function apply_filters( $tag, $value ) { return $value; }
function wp_register_style( $h, $src, $deps = array(), $ver = false ) { $GLOBALS['fvx_registered'][ $h ] = array( 'type' => 'style', 'src' => $src, 'ver' => $ver ); return true; }
function wp_register_script( $h, $src, $deps = array(), $ver = false, $args = array() ) { $GLOBALS['fvx_registered'][ $h ] = array( 'type' => 'script', 'src' => $src, 'ver' => $ver, 'args' => $args ); return true; }
function wp_style_is( $h, $list = 'enqueued' ) { return 'registered' === $list ? isset( $GLOBALS['fvx_registered'][ $h ] ) : in_array( $h, $GLOBALS['fvx_enqueued']['style'], true ); }
function wp_enqueue_style( $h ) { $GLOBALS['fvx_enqueued']['style'][] = $h; }
function wp_enqueue_script( $h ) { $GLOBALS['fvx_enqueued']['script'][] = $h; }
function is_singular() { return $GLOBALS['fvx_singular']; }
function get_post() { return $GLOBALS['fvx_post']; }
function has_shortcode( $content, $tag ) { return false !== strpos( $content, '[' . $tag ); }
function esc_url( $u ) { return htmlspecialchars( $u, ENT_QUOTES ); }
function error_log_stub( $m ) { $GLOBALS['fvx_log'][] = $m; }
// Route the plugin's error_log() calls into the harness log instead of stderr.
ini_set( 'error_log', sys_get_temp_dir() . '/fvx-php-errors.log' );

require $plugin_dir . 'final-vestige-experience-2.php';

function fvx_run_hooks( $hook ) {
	$list = $GLOBALS['fvx_hooks'][ $hook ] ?? array();
	usort( $list, function ( $a, $b ) { return $a[0] <=> $b[0]; } );
	foreach ( $list as $item ) { call_user_func( $item[1] ); }
}
function fvx_ids( $html ) { preg_match_all( '/\sid="([^"]+)"/', $html, $m ); return $m[1]; }

$out = array( 'scenario' => $scenario );
$tag = 'fv_ex2_research_desk';

switch ( $scenario ) {
	case 'render':
		$a = call_user_func( $GLOBALS['fvx_shortcodes'][ $tag ] );
		$b = call_user_func( $GLOBALS['fvx_shortcodes'][ $tag ] );
		$ids = array_merge( fvx_ids( $a ), fvx_ids( $b ) );
		$out['shortcodes']      = array_keys( $GLOBALS['fvx_shortcodes'] );
		$out['first_has_title'] = false !== strpos( $a, 'id="fv-ex2-desk-apollo1-title"' );
		$out['second_has_title'] = false !== strpos( $b, 'id="fv-ex2-desk-apollo1-2-title"' );
		$out['duplicate_ids']   = array_values( array_diff_assoc( $ids, array_unique( $ids ) ) );
		$out['placeholder_left'] = false !== strpos( $a . $b, '{{fvx-instance}}' );
		$out['atlas_ok']        = false !== strpos( call_user_func( $GLOBALS['fvx_shortcodes']['fv_ex2_atlas'] ), 'data-fvx="atlas"' );
		$out['enqueued']        = $GLOBALS['fvx_enqueued'];
		$out['registered_after_render'] = array_keys( $GLOBALS['fvx_registered'] );
		break;
	case 'assets-hit':
		$GLOBALS['fvx_singular'] = true;
		$GLOBALS['fvx_post']     = (object) array( 'post_content' => "Intro\n[fv_ex2_research_desk]\nOutro" );
		fvx_run_hooks( 'wp_enqueue_scripts' );
		$out['enqueued']   = $GLOBALS['fvx_enqueued'];
		$out['registered'] = $GLOBALS['fvx_registered'];
		break;
	case 'assets-miss':
		$GLOBALS['fvx_singular'] = true;
		$GLOBALS['fvx_post']     = (object) array( 'post_content' => 'A normal post with no components.' );
		fvx_run_hooks( 'wp_enqueue_scripts' );
		$out['enqueued']   = $GLOBALS['fvx_enqueued'];
		$out['registered'] = array_keys( $GLOBALS['fvx_registered'] );
		break;
	case 'injection':
		// Attributes are passed by WordPress as the first argument; the callback must ignore them entirely.
		$evil = call_user_func( $GLOBALS['fvx_shortcodes'][ $tag ], array( 'instance' => 'x"><script>alert(1)</script>', 'template' => '../../wp-config' ) );
		$out['contains_script'] = false !== stripos( $evil, '<script' );
		$out['contains_payload'] = false !== strpos( $evil, 'alert(1)' );
		$out['has_desk_markup'] = false !== strpos( $evil, 'data-fvx="desk"' );
		break;
	case 'fallback-probe':
		$html = call_user_func( $GLOBALS['fvx_shortcodes'][ $tag ] );
		$out['is_fallback'] = false !== strpos( $html, 'fv-ex2-fallback' );
		$out['has_article_link'] = false !== strpos( $html, 'the-hatch-opened-inward-apollo-1' );
		$out['no_desk_markup'] = false === strpos( $html, 'data-fvx="desk"' );
		$out['enqueued'] = $GLOBALS['fvx_enqueued'];
		break;
}
echo json_encode( $out );
