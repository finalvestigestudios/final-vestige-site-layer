<?php
/**
 * Plugin Name: Final Vestige Site Layer
 * Description: Versioned, fail-closed delivery layer for QD-reviewed Final Vestige front-end features.
 * Version: 0.3.0
 * Author: Final Vestige Studios
 * Requires at least: 6.0
 * Requires PHP: 7.4
 */

defined( 'ABSPATH' ) || exit;

define( 'FVSL_VERSION', '0.3.0' );
define( 'FVSL_RELEASE_ID', 'FVSL-VESTIGE-ASSEMBLY-HOME-001' );
define( 'FVSL_PIPELINE_CANARY', 'FVS-E2E-20260911-A' );

/**
 * Exact QD-reviewed payload identities. Any byte drift disables the entire layer.
 *
 * @return array<string,array{file:string,bytes:int,sha256:string}>
 */
function fvsl_release_manifest() {
    return array(
        'signal-finder' => array(
            'file'   => 'signal-finder-wp-block-v1.txt',
            'bytes'  => 10370,
            'sha256' => '4ce83f3ef803e33a1f90d9ca970894e72a18ece34ea86eb7f104bc8086792e27',
        ),
        'evidence-map' => array(
            'file'   => 'evidence-map-wp-block-v1.txt',
            'bytes'  => 15319,
            'sha256' => 'ec62da9272052b7f57bb243dd939eb726ee18779cb5575233b3582dfe6aad008',
        ),
        'detail-lens' => array(
            'file'   => 'detail-lens-wp-block-v1.txt',
            'bytes'  => 15617,
            'sha256' => 'a4c20692a2c51643af17a1502cd93aabcf5e0a6c2a64ffdd35096411129ce859',
        ),
        'case-search' => array(
            'file'   => 'case-search-wp-block-v1.txt',
            'bytes'  => 17534,
            'sha256' => 'e313db1e31ff1fce01b8bbd5d8dda03673b9a52aadcc7cbecafd2cec50dcc6a7',
        ),
        'hero-assembly' => array(
            'file'   => 'hero-assembly-wp-block-v1.txt',
            'bytes'  => 1137,
            'sha256' => '5535880f3db7805b17b2766bcb8e8f6381456c037f8c67c3944f30c8aa8f86d0',
        ),
        'margins-wire' => array(
            'file'   => 'margins-wire-wp-block-v1.txt',
            'bytes'  => 4392,
            'sha256' => '004b6462e663155e5fede0620dd6f60fa13729984fbf69117aa1672a2e6102de',
        ),
        'investigation-walkthrough' => array(
            'file'   => 'investigation-walkthrough-wp-block-v1.txt',
            'bytes'  => 5180,
            'sha256' => '8d8efdfb50cb177c852ed87283f9ba0628bc033a7c0b51ca06ae627c391622bd',
        ),
        'library-inspector' => array(
            'file'   => 'library-inspector-wp-block-v1.txt',
            'bytes'  => 2646,
            'sha256' => '0d736919a7defab459f041c41aea77b851ceb63463e718b84e367a6b68f1b2d3',
        ),
    );
}

/**
 * Verify every release payload before any visitor-facing output is emitted.
 *
 * @return bool
 */
function fvsl_release_is_intact() {
    static $verified = null;

    if ( null !== $verified ) {
        return $verified;
    }

    foreach ( fvsl_release_manifest() as $item ) {
        $path = plugin_dir_path( __FILE__ ) . 'payloads/' . $item['file'];

        if ( ! is_readable( $path ) ) {
            $verified = false;
            return false;
        }

        $size = filesize( $path );
        if ( false === $size || (int) $size !== (int) $item['bytes'] ) {
            $verified = false;
            return false;
        }

        $actual_hash = hash_file( 'sha256', $path );
        if ( false === $actual_hash || ! hash_equals( $item['sha256'], $actual_hash ) ) {
            $verified = false;
            return false;
        }
    }

    $verified = true;
    return true;
}

/**
 * Preload the one editorial display face the homepage redesign's headlines
 * use (Fraunces). Every fv-* style already lists ui-serif/Georgia fallbacks,
 * so a missing or blocked font never breaks layout -- this only sharpens it.
 * Gated by the same release-integrity check as the footer payloads.
 *
 * @return void
 */
function fvsl_enqueue_display_font() {
    if ( is_admin() || ! fvsl_release_is_intact() ) {
        return;
    }

    echo "\n<link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">\n";
    echo "<link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>\n";
    echo '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400..600;1,9..144,400..600&display=swap">' . "\n";
}
add_action( 'wp_head', 'fvsl_enqueue_display_font' );

/**
 * Emit the exact reviewed payloads at the standard front-end footer hook.
 * Individual payloads contain their own fail-closed page qualification.
 *
 * @return void
 */
function fvsl_render_feature_layer() {
    if ( is_admin() || is_feed() || is_robots() || is_trackback() ) {
        return;
    }

    if ( ! fvsl_release_is_intact() ) {
        return;
    }

    echo "\n<!-- final-vestige-site-layer:" . esc_html( FVSL_VERSION ) . ' release:' . esc_html( FVSL_RELEASE_ID ) . " -->\n";

    foreach ( fvsl_release_manifest() as $item ) {
        $path = plugin_dir_path( __FILE__ ) . 'payloads/' . $item['file'];
        // phpcs:ignore WordPress.WP.AlternativeFunctions.file_system_operations_readfile -- local immutable plugin payload.
        readfile( $path );
        echo "\n";
    }

    echo "<!-- /final-vestige-site-layer -->\n";
}
add_action( 'wp_footer', 'fvsl_render_feature_layer', 99 );

/**
 * Make release identity visible in WordPress Site Health debug information.
 */
function fvsl_debug_information( $info ) {
    $info['final-vestige-site-layer'] = array(
        'label'  => 'Final Vestige Site Layer',
        'fields' => array(
            'version' => array(
                'label' => 'Version',
                'value' => FVSL_VERSION,
            ),
            'release' => array(
                'label' => 'Release',
                'value' => FVSL_RELEASE_ID,
            ),
            'integrity' => array(
                'label' => 'Payload integrity',
                'value' => fvsl_release_is_intact() ? 'PASS' : 'FAIL-CLOSED',
            ),
        ),
    );

    return $info;
}
add_filter( 'debug_information', 'fvsl_debug_information' );
