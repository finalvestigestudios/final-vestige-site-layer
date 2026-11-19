"""Verify optional evidence plate failure never removes the underlying source catalogue."""
from pathlib import Path
import shutil
import subprocess
import tempfile
ROOT=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='fv-r466-') as name:
    work=Path(name);(work/'assets').mkdir()
    for source in ('apollo_rights_gallery.php','assets/gallery.css','assets/gallery.js'):
        shutil.copy2(ROOT/source,work/source)
    def render():
        cmd=['php','-r',f'require {repr(str(work/"apollo_rights_gallery.php"))};echo fv457_render();']
        return subprocess.run(cmd,check=True,capture_output=True,text=True).stdout
    absent=render()
    assert 'Evidence comparison temporarily unavailable' in absent
    assert absent.count('data-fv457-card=')==6
    assert absent.count('class="fv457__cta"')==1
    assert 'data-fv457-plate=' not in absent
    shutil.copy2(ROOT/'evidence_plates.php',work/'evidence_plates.php')
    valid=render()
    assert valid.count('data-fv457-plate=')==3
    (work/'evidence_plates.php').write_text(valid[:22])
    altered=render()
    assert altered.count('data-fv457-card=')==6
    assert 'Evidence comparison temporarily unavailable' in altered
    assert 'data-fv457-plate=' not in altered
print('PASS: 9 optional-component missing/valid/tampered source-custody invariants; not hosted')
