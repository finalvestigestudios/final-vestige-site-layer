<?php
/**
 * Asset registration. Handles are registered early and enqueued only when a component renders (or the post
 * content visibly contains one), so pages without Experience 2.0 components load nothing.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

final class FV_Ex2_Assets {

	const STYLE  = 'fv-ex2';
	const SCRIPT = 'fv-ex2';

	/** @var array|null */
	private static $manifest = null;

	/** Build manifest written by tools/build_all.py: byte sizes and SHA-256 of every shipped asset and template. */
	public static function manifest(): array {
		if ( null === self::$manifest ) {
			self::$manifest = array();
			$path = FV_EX2_DIR . 'assets/manifest.json';
			$raw  = is_readable( $path ) ? file_get_contents( $path ) : false;
			$data = is_string( $raw ) ? json_decode( $raw, true ) : null;
			if ( is_array( $data ) ) {
				self::$manifest = $data;
			}
		}
		return self::$manifest;
	}

	/** Cache-busting version derived from the built content, so it changes exactly when the assets change. */
	public static function version(): string {
		$m = self::manifest();
		$css = isset( $m['css']['sha256'] ) ? substr( (string) $m['css']['sha256'], 0, 10 ) : '';
		$js  = isset( $m['js']['sha256'] ) ? substr( (string) $m['js']['sha256'], 0, 10 ) : '';
		return ( '' === $css || '' === $js ) ? FV_EX2_VERSION : $css . '-' . $js;
	}

	public static function register(): void {
		wp_register_style( self::STYLE, FV_EX2_URL . 'assets/fv-ex2.css', array(), self::version() );
		wp_register_script(
			self::SCRIPT,
			FV_EX2_URL . 'assets/fv-ex2.js',
			array(),
			self::version(),
			array(
				'in_footer' => true,
				'strategy'  => 'defer',
			)
		);
	}

	public static function enqueue(): void {
		// Registration is idempotent; this also covers renders that run before wp_enqueue_scripts.
		if ( ! wp_style_is( self::STYLE, 'registered' ) ) {
			self::register();
		}
		wp_enqueue_style( self::STYLE );
		wp_enqueue_script( self::SCRIPT );
	}

	/** Early enqueue (in <head>) when the current post content contains a component shortcode. */
	public static function maybe_enqueue_for_content(): void {
		$force = (bool) apply_filters( 'fv_ex2_force_assets', false );
		if ( $force ) {
			self::enqueue();
			return;
		}
		if ( ! is_singular() ) {
			return;
		}
		$post = get_post();
		if ( ! $post ) {
			return;
		}
		$content = (string) $post->post_content;
		foreach ( FV_Ex2_Plugin::SHORTCODES as $tag => $template ) {
			if ( has_shortcode( $content, $tag ) ) {
				self::enqueue();
				return;
			}
		}
	}
}
