import subprocess
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
failed=[]
for key in ['drawing','library','kitchen','bedroom','attic','rear','floor1','floor2','floor3']:
    print('START',key,flush=True)
    proc=subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','--factory-startup','-b',str(BASE/'Verdant_Manor.blend'),'--python',str(BASE/'scripts/render_one.py'),'--',key],capture_output=True,text=True)
    # Blender sometimes exits with native allocator failure after a successfully saved render.
    good='COMPLETE ' in proc.stdout
    print('\n'.join(line for line in proc.stdout.splitlines() if any(s in line for s in ['COMPLETE','Saved:','Error','Traceback','RENDERING'])),flush=True)
    print('RESULT',key,'OK' if good else 'FAILED','exit',proc.returncode,flush=True)
    if not good:failed.append(key);print(proc.stdout[-3000:],proc.stderr[-1500:],flush=True)
print('FINISHED',failed,flush=True)
if failed:raise SystemExit(1)
