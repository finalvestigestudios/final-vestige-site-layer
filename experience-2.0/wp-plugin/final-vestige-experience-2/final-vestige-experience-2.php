<?php
/**
 * Plugin Name:       Final Vestige Experience 2.0 (Staging Candidate)
 * Description:       Namespaced Experience 2.0 components for staging: Research Desk and Evidence Atlas shortcodes. Not authorized for production.
 * Version:           0.5.0-sprint5
 * Requires at least: 6.4
 * Requires PHP:      7.4
 * Author:            Final Vestige Studios
 * License:           Proprietary
 * Text Domain:       fv-ex2
 *
 * Isolation contract: this plugin is separate from the Final Vestige Site Layer plugin and from the PR #49 homepage
 * work. It stores nothing, registers no admin screens, makes no remote requests and adds no REST routes.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

define( 'FV_EX2_VERSION', '0.5.0-sprint5' );
define( 'FV_EX2_DIR', plugin_dir_path( __FILE__ ) );
define( 'FV_EX2_URL', plugin_dir_url( __FILE__ ) );
define( 'FV_EX2_ARTICLE_URL', 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/' );

require_once FV_EX2_DIR . 'includes/class-fv-ex2-assets.php';
require_once FV_EX2_DIR . 'includes/class-fv-ex2-renderer.php';
require_once FV_EX2_DIR . 'includes/class-fv-ex2-plugin.php';

FV_Ex2_Plugin::init();
