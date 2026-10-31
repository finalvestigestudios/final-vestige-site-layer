<?php
/**
 * Plugin Name: FV Focus Popup (Review Candidate)
 * Description: Opt-in Fieldbook dialog using existing Jetpack subscriptions. DRAFT: no production authorization.
 * Version: 0.1.1
 */
defined('ABSPATH') || exit;

/**
 * Add shortcode [fv_focus_popup] to a controlled staging page/template only.
 * Does NOT subscribe anyone, process PII, modify lists or send the book.
 * Native Jetpack block must render a working form or JS keeps /focus/ fallback visible.
 */
/**
 * Enqueue styles from wp_head, before the content shortcode renders.
 * Shortcodes rendered only in template parts are NOT guaranteed early CSS;
 * production placement must be a page content block, verified in staging.
 */
function fv_focus_popup_enqueue_assets() {
    wp_enqueue_style(
        'fv-focus-popup',
        plugins_url('focus-popup.css', __FILE__),
        array(),
        '0.1.1'
    );
    wp_enqueue_script(
        'fv-focus-popup',
        plugins_url('focus-popup.js', __FILE__),
        array(),
        '0.1.1',
        true
    );
}
add_action('wp_enqueue_scripts', static function () {
    if (!is_singular()) {
        return;
    }
    $post = get_post();
    if (!is_object($post) || !isset($post->post_content)) {
        return;
    }
    if (has_shortcode((string) $post->post_content, 'fv_focus_popup')) {
        fv_focus_popup_enqueue_assets();
    }
});

add_shortcode('fv_focus_popup', static function () {
    // Repeated blocks would duplicate IDs and dialog controls; fail to a normal link.
    static $rendered_once = false;
    if ($rendered_once) {
        return '<p><a href="/focus/">Explore the Seven Day Focus Fieldbook</a></p>';
    }
    $rendered_once = true;
    $html_path = plugin_dir_path(__FILE__) . 'focus-popup.html';
    if (!is_readable($html_path)) {
        return '<p><a href="/focus/">Explore the Seven Day Focus Fieldbook</a></p>';
    }
    $html = file_get_contents($html_path);
    if (!is_string($html)) {
        return '<p><a href="/focus/">Explore the Seven Day Focus Fieldbook</a></p>';
    }

    // Let WordPress render the real Jetpack subscriptions block. Never fabricate a form.
    $rendered = do_blocks($html);

    fv_focus_popup_enqueue_assets(); // fallback for alternate render paths; WP deduplicates handles
    return $rendered;
});
