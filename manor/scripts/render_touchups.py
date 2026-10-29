from pathlib import Path
import subprocess
BASE=Path(__file__).resolve().parents[1]
for key in ['exterior','attic','rear','floor3']:
    p=subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','--factory-startup','-b',str(BASE/'Verdant_Manor.blend'),'--python',str(BASE/'scripts/render_one.py'),'--',key],capture_output=True,text=True)
    ok='COMPLETE ' in p.stdout;print(key,'OK' if ok else 'FAILED',flush=True)
    if not ok:print(p.stdout[-3000:],p.stderr,flush=True);raise SystemExit(1)
print('TOUCHUPS_COMPLETE',flush=True)
