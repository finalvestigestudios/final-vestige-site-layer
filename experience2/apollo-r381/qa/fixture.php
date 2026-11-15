<?php
// Isolated local PHP-rendered fixture, NOT installed WordPress.
define('ABSPATH',__DIR__.'/');
require_once __DIR__ . '/../../apollo-r377/source-role-desk.php';
require_once __DIR__ . '/../atlas.php';
?><!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Apollo Curated Atlas R381 — LOCAL FIXTURE</title>
<style><?php readfile(__DIR__.'/../assets/atlas.css'); ?></style>
<script><?php readfile(__DIR__.'/../assets/atlas.js'); ?></script>
</head><body style="margin:0;background:#101517"><?php echo fv_r381_shortcode(); ?></body></html>
