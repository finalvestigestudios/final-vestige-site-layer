<?php
/** Real local HTTP staging renderer. WordPress API shim; NOT installed WordPress. */
define('ABSPATH','/mock-wp/');
function add_action($name,$fn,$priority=10) {}
function plugins_url($name,$file) { return '/assets/review-custody.css'; }
function wp_style_is($handle,$state) { return false; }
function add_shortcode($name,$fn) {}
require __DIR__ . '/../../apollo-r277/apollo-review-shortcode.php';
?><!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>R278 authentic Apollo source custody · HTTP/CSP</title></head><body><main><h1>Apollo 1: public primary-source custody</h1><?php
  echo fv_r277_render_shortcode(['state'=>'approved','merchant_url'=>'https://evil.invalid/shop']);
  echo fv_r277_render_shortcode(['receipt_sha256'=>str_repeat('a',64)]);
?></main></body></html>
