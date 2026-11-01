<?php
/**
 * Renders bundled, release-reviewed templates. Nothing the visitor or an editor supplies is placed in the markup,
 * and every template is verified against the build manifest before output, so a stale or tampered file degrades to a
 * plain link instead of unreviewed content.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

final class FV_Ex2_Renderer {

	const PLACEHOLDER = '{{fvx-instance}}';

	/** @var array<string,int> Render counts per template, used to keep element ids unique on one page. */
	private static $counts = array();

	/** Allow-list: template name => file. Never built from input. */
	private static function files(): array {
		return array(
			'research-desk' => 'templates/research-desk.html',
			'atlas'         => 'templates/atlas.html',
		);
	}

	/** Test hook: reset per-request state. */
	public static function reset(): void {
		self::$counts = array();
	}

	public static function fallback(): string {
		return '<p class="fv-ex2-fallback">This research view is unavailable. <a href="' . esc_url( FV_EX2_ARTICLE_URL )
			. '">Read the original Apollo 1 investigation</a>.</p>';
	}

	public static function render( string $template ): string {
		$files = self::files();
		if ( ! isset( $files[ $template ] ) ) {
			return self::fallback();
		}
		$path = FV_EX2_DIR . $files[ $template ];
		$raw  = is_readable( $path ) ? file_get_contents( $path ) : false;
		if ( ! is_string( $raw ) || '' === trim( $raw ) ) {
			return self::fallback();
		}
		$manifest = FV_Ex2_Assets::manifest();
		$expected = isset( $manifest['templates'][ $template ]['sha256'] ) ? (string) $manifest['templates'][ $template ]['sha256'] : '';
		if ( '' === $expected || ! hash_equals( $expected, hash( 'sha256', $raw ) ) ) {
			error_log( 'fv-ex2: template ' . $template . ' does not match the build manifest; serving fallback.' ); // phpcs:ignore WordPress.PHP.DevelopmentFunctions.error_log_error_log
			return self::fallback();
		}

		self::$counts[ $template ] = ( self::$counts[ $template ] ?? 0 ) + 1;
		$n        = self::$counts[ $template ];
		$instance = 1 === $n ? 'apollo1' : 'apollo1-' . $n;
		$markup   = str_replace( self::PLACEHOLDER, $instance, $raw );

		FV_Ex2_Assets::enqueue();
		return $markup;
	}
}
