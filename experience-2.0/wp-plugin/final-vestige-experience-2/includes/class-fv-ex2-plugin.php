<?php
/** Wiring: shortcodes and asset hooks. Shortcode attributes are deliberately ignored. */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

final class FV_Ex2_Plugin {

	/** Shortcode tag => template name. */
	const SHORTCODES = array(
		'fv_ex2_research_desk' => 'research-desk',
		'fv_ex2_atlas'         => 'atlas',
	);

	public static function init(): void {
		add_action( 'wp_enqueue_scripts', array( 'FV_Ex2_Assets', 'register' ), 5 );
		add_action( 'wp_enqueue_scripts', array( 'FV_Ex2_Assets', 'maybe_enqueue_for_content' ), 20 );
		foreach ( self::SHORTCODES as $tag => $template ) {
			add_shortcode(
				$tag,
				static function () use ( $template ) {
					return FV_Ex2_Renderer::render( $template );
				}
			);
		}
	}
}
