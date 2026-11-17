"""Executable source/WordPress gate checks; never claims installed staging acceptance."""
from pathlib import Path
import hashlib, subprocess
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parents[1]
COUNT=0

def check(condition, description):
    global COUNT
    assert condition,description
    COUNT+=1

def php(code):
    result=subprocess.run(['php','-d','display_errors=1','-r',code],cwd=HERE,capture_output=True,text=True)
    assert result.returncode==0,(result.stdout,result.stderr)
    return result.stdout

def git_blob(p):
    b=p.read_bytes()
    return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()

check(git_blob(ROOT/'apollo-r430/staging-educator-case-lab.php')=='11a30d871bb0c5840aa3ee8932e12a6068b50cd3','parent php SHA')
check(git_blob(ROOT/'apollo-r430/assets/educator-case-lab.css')=='be6880577faed2453f5633a3718fce8dedf9ac3b','parent css SHA')
check(git_blob(ROOT/'apollo-r429/staging-attribution-bridge.php')=='c604bccf9873688ec1d9b64187d1a9a7fdcf89ac','grandparent php SHA')
check(git_blob(ROOT/'apollo-r429/assets/bridge.css')=='15942f8ef27d82695c8d2af8bdc8a807396da33e','grandparent css SHA')
base=f"define('ABSPATH',__DIR__); require {str(HERE/'staging-evidence-notebook.php')!r}; "
check(php(base+"echo fv_r431_verified()?'YES':'NO';")=='YES','source custody valid')
check('Evidence notebook unavailable' in php(base+"echo fv_r431_shortcode();"),'default inert disabled')
check('Evidence notebook unavailable' in php("define('FV_R431_ENABLED',true);define('FV_R431_STAGING_PAGE_ID',901);function wp_get_environment_type(){return 'production';}function is_singular(){return true;}function get_queried_object_id(){return 901;}"+base+"echo fv_r431_shortcode();"),'production blocked')
check('Evidence notebook unavailable' in php("define('FV_R431_ENABLED',true);define('FV_R431_STAGING_PAGE_ID',901);function wp_get_environment_type(){return 'staging';}function is_singular(){return true;}function get_queried_object_id(){return 900;}"+base+"echo fv_r431_shortcode();"),'other staging page blocked')
output=php("define('FV_R431_ENABLED',true);define('FV_R431_STAGING_PAGE_ID',901);function wp_get_environment_type(){return 'staging';}function is_singular(){return true;}function get_queried_object_id(){return 901;}"+base+"echo fv_r431_shortcode();")
check(output.count('class="fv-r430__question"')==3,'real 3 questions')
check(output.count('class="fv-r429__cta"')==1,'one and only one article CTA')
check(output.count('class="fv-r431__actions"')==1 and 'hidden' in output,'controls hidden by default')
check('Read the free Apollo 1 investigation' in output,'verified free article route')
check('utm_content=reviewed_' not in output,'missing query does not invent campaign')
check('<form' not in output and '<input type="email"' not in output,'no submission')
check('href="https://www.nasa.gov/' in output,'NASA record links retained')
check('type="button"' in output,'all enhanced controls are non-submit')
check('id="fv-r431-1-title"' in output,'new id scoped')
check('aria-live="polite"' in output,'accessible feedback')
check('NASA product' in output,'rights boundary')
check('Evidence notebook unavailable' in php(base+"echo fv_r431_render(31, []);"),'instance cap')
check('Evidence notebook unavailable' in php(base+"function fv_r430_render(){return 'wrong source';}echo fv_r431_render(1,[]);"),'untrusted preloaded PHP rejected')
# Exact-byte mutation / restoration is only made on the isolated local copy.
parent=ROOT/'apollo-r430/assets/educator-case-lab.css'
original=parent.read_bytes()
try:
    parent.write_bytes(original+b'/* unreviewed */')
    check(php(base+"echo fv_r431_verified()?'YES':'NO';")=='NO','mutated CSS blocked')
    check('Evidence notebook unavailable' in php(base+"echo fv_r431_render(1,[]);"),'mutated CSS fallback')
finally:parent.write_bytes(original)
check(php(base+"echo fv_r431_verified()?'YES':'NO';")=='YES','post-mutation restored')
# parent source symlink rejection
parent=ROOT/'apollo-r430/assets/educator-case-lab.css'
original=parent.read_bytes()
parent.unlink()
try:
    parent.symlink_to(ROOT/'apollo-r429/assets/bridge.css')
    check(php(base+"echo fv_r431_verified()?'YES':'NO';")=='NO','symlink refused')
finally:
    parent.unlink();parent.write_bytes(original)
check(php(base+"echo fv_r431_verified()?'YES':'NO';")=='YES','post-symlink restored')
print(f'PASS {COUNT}/{COUNT} exact-parent + staging-gate + adversarial PHP assertions')
