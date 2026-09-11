<?php
/**
 * Plugin Name: Final Vestige Deployment Bridge
 * Description: Fail-closed deployment receiver for the Final Vestige Site Layer. Accepts only HMAC-authenticated, hash-verified production releases.
 * Version: 0.3.0
 * Author: Final Vestige Studios
 * Requires at least: 6.5
 * Requires PHP: 8.1
 */

defined('ABSPATH') || exit;

define('FVDB_VERSION', '0.3.0');
define('FVDB_FILE', __FILE__);
define('FVDB_EXPECTED_REPOSITORY', 'finalvestigestudios/final-vestige-site-layer');
define('FVDB_EXPECTED_BRANCH', 'production');
define('FVDB_TARGET_SLUG', 'final-vestige-site-layer');
define('FVDB_TARGET_MAIN', 'final-vestige-site-layer.php');
define('FVDB_REST_NAMESPACE', 'fv-deploy/v1');

require_once __DIR__ . '/includes/class-fvdb-state.php';
require_once __DIR__ . '/includes/class-fvdb-auth.php';
require_once __DIR__ . '/includes/class-fvdb-lock.php';
require_once __DIR__ . '/includes/class-fvdb-package.php';
require_once __DIR__ . '/includes/class-fvdb-admin.php';
require_once __DIR__ . '/includes/class-fvdb-core.php';

FVDB_Core::boot();
