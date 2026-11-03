<?php
/**
 * EX2 synthetic-only WordPress core persistence probe.
 *
 * Executed ONLY in a disposable WordPress Playground PHP/WASM installation.
 * It never connects to WordPress.com. Do not deploy, install, or call on production.
 * Writes one DRAFT synthetic page and deletes it before exit.
 */
header( 'Content-Type: application/json; charset=utf-8' );

function fv_ex2_probe_fail( $reason ) {
    http_response_code( 422 );
    echo wp_json_encode( array( 'result' => 'FAIL', 'reason' => $reason ) );
    exit;
}
require_once __DIR__ . '/wp-load.php';

$fixture_path = __DIR__ . '/wp-content/fv-ex2-synthetic-candidate.html';
$marker_path  = __DIR__ . '/wp-content/fv-ex2-synthetic-only.marker';
if ( ! is_file( $marker_path ) || trim( file_get_contents( $marker_path ) ) !== 'SYNTHETIC_TEST_FIXTURE_ONLY' ) {
    fv_ex2_probe_fail( 'Synthetic-only marker absent' );
}
$host = (string) wp_parse_url( home_url(), PHP_URL_HOST );
if ( stripos( $host, 'finalvestige.com' ) !== false || ! in_array( $host, array( '127.0.0.1', 'localhost', '::1' ), true ) ) {
    fv_ex2_probe_fail( 'Refusing a nonlocal WordPress host' );
}
if ( ! is_file( $fixture_path ) ) {
    fv_ex2_probe_fail( 'Synthetic fixture absent' );
}
$source = file_get_contents( $fixture_path );
if ( ! is_string( $source ) || strlen( $source ) < 1000
    || strpos( $source, 'FV-EX2 PAGE6 REVIEW-ONLY' ) === false
    || strpos( $source, 'jetpack/subscriptions' ) === false ) {
    fv_ex2_probe_fail( 'Input is not the expected synthetic combined candidate' );
}
$source_sha = hash( 'sha256', $source );
$before_blocks = parse_blocks( $source );
if ( ! is_array( $before_blocks ) || count( $before_blocks ) < 2 ) {
    fv_ex2_probe_fail( 'Gutenberg parse failed before persistence' );
}
$record_pattern = '/<span class="fv-margin-strip__item" style="--i:\\d+">/';
if ( ! preg_match_all( $record_pattern, $source, $matches ) || count( $matches[0] ) !== 72 ) {
    fv_ex2_probe_fail( 'Synthetic Margins record count drift' );
}
$created_id = 0;
$report = null;
$cleanup = array( 'attempted' => false, 'deleted' => false, 'verified_absent' => false );
try {
    $created_id = wp_insert_post(
        array(
            'post_type'    => 'page',
            'post_title'   => 'FV EX2 Disposable Synthetic Core Readback',
            'post_status'  => 'draft',
            'post_content' => wp_slash( $source ),
        ),
        true
    );
    if ( is_wp_error( $created_id ) || ! is_int( $created_id ) || $created_id < 1 ) {
        throw new RuntimeException( 'WordPress core draft insertion failed' );
    }
    clean_post_cache( $created_id );
    $stored = get_post_field( 'post_content', $created_id, 'raw' );
    if ( ! is_string( $stored ) ) {
        throw new RuntimeException( 'WordPress core failed to return raw post content' );
    }
    $after_blocks = parse_blocks( $stored );
    $html_blocks = array_values( array_filter(
        $after_blocks,
        static function ( $block ) {
            return isset( $block['blockName'] ) && 'core/html' === $block['blockName'];
        }
    ) );
    $source_html_blocks = array_values( array_filter(
        $before_blocks,
        static function ( $block ) {
            return isset( $block['blockName'] ) && 'core/html' === $block['blockName'];
        }
    ) );
    $checks = array(
        'byte_identical_readback' => hash_equals( $source_sha, hash( 'sha256', $stored ) ),
        'block_count_preserved'   => count( $before_blocks ) === count( $after_blocks ),
        'html_blocks_preserved'   => count( $source_html_blocks ) === count( $html_blocks ) && count( $html_blocks ) >= 2,
        'margin_72_preserved'     => preg_match_all( $record_pattern, $stored, $matches ) === 72,
        'jetpack_comment_preserved' => substr_count( $stored, 'jetpack/subscriptions' ) === 1,
        'focus_present'          => strpos( $stored, 'Focus Fieldbook' ) !== false,
        'contrast_marker_once'   => substr_count( $stored, 'FV-EX2 PAGE6 REVIEW-ONLY' ) === 1,
        'chapter_nav_present'    => strpos( $stored, 'fv-hf__chapter-nav' ) !== false,
        'new_note_not_released'  => get_post_status( $created_id ) === 'draft',
    );
    $report = array(
        'result'       => in_array( false, $checks, true ) ? 'FAIL' : 'PASS',
        'data_class'   => 'SYNTHETIC_TEST_FIXTURE_ONLY',
        'test_type'    => 'WORDPRESS_CORE_DRAFT_SAVE_READBACK_NOT_GUTENBERG_EDITOR',
        'release'      => 'HOLD',
        'wordpress'    => get_bloginfo( 'version' ),
        'php'          => PHP_VERSION,
        'source_sha256' => $source_sha,
        'stored_sha256' => hash( 'sha256', $stored ),
        'source_bytes'  => strlen( $source ),
        'stored_bytes'  => strlen( $stored ),
        'parsed_blocks_before' => count( $before_blocks ),
        'parsed_blocks_after'  => count( $after_blocks ),
        'checks'       => $checks,
    );
} catch ( Throwable $error ) {
    // NEVER exit here: PHP's exit skips finally, which would strand the draft.
    $report = array(
        'result' => 'FAIL',
        'reason' => 'WordPress synthetic core exception: ' . get_class( $error ),
        'data_class' => 'SYNTHETIC_TEST_FIXTURE_ONLY',
        'test_type' => 'WORDPRESS_CORE_DRAFT_SAVE_READBACK_NOT_GUTENBERG_EDITOR',
        'release' => 'HOLD',
    );
} finally {
    if ( is_int( $created_id ) && $created_id > 0 ) {
        $cleanup['attempted'] = true;
        try {
            $deleted = wp_delete_post( $created_id, true );
            $cleanup['deleted'] = ! empty( $deleted );
            $cleanup['verified_absent'] = ! get_post( $created_id );
        } catch ( Throwable $cleanup_error ) {
            // Refuse PASS if cleanup throws. Never leak environment details.
            $cleanup['verified_absent'] = false;
        }
    }
}
$report['cleanup'] = $cleanup;
if ( $cleanup['attempted'] && ( ! $cleanup['deleted'] || ! $cleanup['verified_absent'] ) ) {
    $report['result'] = 'FAIL';
    $report['reason'] = 'Disposable draft cleanup could not be verified';
}
if ( 'PASS' !== $report['result'] ) {
    http_response_code( 422 );
}
echo wp_json_encode( $report );
