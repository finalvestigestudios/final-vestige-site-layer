<?php
/**
 * Plugin Name: FV Focus Popup (Review Candidate)
 * Description: Opt-in Fieldbook dialog using existing Jetpack subscriptions. DRAFT: no production authorization.
 * Version: 0.1.0
 */
defined('ABSPATH') || exit;

/**
 * Add shortcode [fv_focus_popup] to a controlled staging page/template only.
 * Does NOT subscribe anyone, process PII, modify lists or send the book.
 * Native Jetpack block must render a working form or JS keeps /focus/ fallback visible.
 */
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

    wp_enqueue_style(
        'fv-focus-popup',
        plugins_url('focus-popup.css', __FILE__),
        array(),
        '0.1.0'
    );
    wp_enqueue_script(
        'fv-focus-popup',
        plugins_url('focus-popup.js', __FILE__),
        array(),
        '0.1.0',
        true
    );
    return $rendered;
});
