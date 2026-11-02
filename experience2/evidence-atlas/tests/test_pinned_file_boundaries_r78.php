<?php
/** R78 genuine temporary-filesystem tests; not WordPress or production. */
error_reporting(E_ALL);
define('ABSPATH', '/local-fixture/');
function add_action(...$x): void {}
function add_shortcode(...$x): void {}
require_once __DIR__ . '/../integration/fv-ex2-apollo-suite.php';
$passed=0;
function r78_check($got,$want,string $label): void {
    global $passed;
    if ($got !== $want) { fwrite(STDERR,"FAIL ".$label."\n"); exit(1); }
    $passed++;
}
function r78_clean(string $path): void {
    if (is_link($path) || is_file($path)) { unlink($path); return; }
    if (!is_dir($path)) { return; }
    foreach (scandir($path) as $p) if ($p !== '.' && $p !== '..') r78_clean($path.'/'.$p);
    rmdir($path);
}
$tmp=sys_get_temp_dir().'/apollo-r78-'.bin2hex(random_bytes(6));
$root=$tmp.'/plugin';
mkdir($root.'/assets',0700,true);
mkdir($tmp.'/external',0700,true);
$files=[
    'main.php'=>'<?php /* approved plugin fixture */',
    'assets/a.css'=>'.a{display:block}',
    'assets/b.js'=>'window.b=true;',
    'assets/c.css'=>'.c{display:block}'
];
try {
    $pins=[];
    foreach ($files as $name=>$data) {
        file_put_contents($root.'/'.$name,$data);
        $pins[$name]=fv_ex2_apollo_git_blob($data);
    }
    r78_check(fv_ex2_apollo_match_desk_pins($root,$pins),true,'four-file profile');
    r78_check(fv_ex2_apollo_pinned_file($root,'main.php'),realpath($root.'/main.php'),'normal origin');
    r78_check(fv_ex2_apollo_pinned_file($root,'assets/a.css'),realpath($root.'/assets/a.css'),'normal nested file');
    r78_check(fv_ex2_apollo_pinned_file($root,'../external/a.css'),null,'parent traversal');
    r78_check(fv_ex2_apollo_pinned_file($root,'assets//a.css'),null,'empty segment');
    r78_check(fv_ex2_apollo_pinned_file($root,'assets/./a.css'),null,'dot segment');
    r78_check(fv_ex2_apollo_pinned_file($root,'missing.css'),null,'missing path');
    r78_check(fv_ex2_apollo_pinned_file($root,'assets/a?.css'),null,'unexpected character');
    $external=$tmp.'/external/a.css';
    file_put_contents($external,$files['assets/a.css']);
    unlink($root.'/assets/a.css');
    if (!symlink($external,$root.'/assets/a.css')) throw new RuntimeException('link setup failed');
    r78_check(fv_ex2_apollo_git_blob(file_get_contents($root.'/assets/a.css')),$pins['assets/a.css'],'linked bytes still match expected SHA');
    r78_check(fv_ex2_apollo_pinned_file($root,'assets/a.css'),null,'linked file rejected');
    r78_check(fv_ex2_apollo_match_desk_pins($root,$pins),false,'profile linked file rejected');
    unlink($root.'/assets/a.css');
    file_put_contents($root.'/assets/a.css',$files['assets/a.css']);
    r78_check(fv_ex2_apollo_match_desk_pins($root,$pins),true,'regular file restoration accepted');
    mkdir($tmp.'/external/assets');
    foreach (['a.css','b.js','c.css'] as $name) {
        file_put_contents($tmp.'/external/assets/'.$name,$files['assets/'.$name]);
        unlink($root.'/assets/'.$name);
    }
    rmdir($root.'/assets');
    if (!symlink($tmp.'/external/assets',$root.'/assets')) throw new RuntimeException('dir link failed');
    r78_check(fv_ex2_apollo_pinned_file($root,'assets/a.css'),null,'linked subdirectory rejected');
    r78_check(fv_ex2_apollo_match_desk_pins($root,$pins),false,'profile linked directory rejected');
    r78_check(fv_ex2_apollo_pinned_file($tmp.'/missing','main.php'),null,'missing root');
    $alias=$tmp.'/alias';
    if (!symlink($root,$alias)) throw new RuntimeException('root link failed');
    r78_check(fv_ex2_apollo_pinned_file($alias,'main.php'),null,'linked root rejected');
    r78_check(fv_ex2_apollo_match_desk_pins($alias,$pins),false,'profile linked root rejected');
    r78_check(fv_ex2_apollo_pinned_file($root,'main.php'),realpath($root.'/main.php'),'unrelated link does not invalidate origin');
    r78_check(fv_ex2_apollo_match_desk_pins($root,array_slice($pins,0,3,true)),false,'partial release profile refused');
    echo "R78 real filesystem custody: ".$passed." assertions passed\n";
} finally { r78_clean($tmp); }
