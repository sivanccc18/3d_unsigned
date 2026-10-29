"""校验六件人物/物证 GLB 已在仓库 assets/story/ 中，并生成哈希清单。

背景：这些 GLB 生成自 MagicLomix 项目的 Tripo 流程（商用授权未验证），
仓库已直接附带；如需从 MagicLomix 源重新复制，用 --source 指定其根目录。

用法：
  python3 prepare.py                      # 校验仓库自带 GLB
  python3 prepare.py --source /path/to/MagicLomix/2026-10-28/1
"""
from pathlib import Path
import json, hashlib, argparse, shutil

root = Path(__file__).resolve().parents[1]
names = ['rochester', 'doctor', 'grace', 'laudanum', 'mother_diary', 'father_letter']
ap = argparse.ArgumentParser()
ap.add_argument('--source', default=None, help='MagicLomix 项目根目录（可选）')
a = ap.parse_args()
records = []
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()

if a.source:
    src = Path(a.source)
    for n in names:
        p = src / 'art/models' / f'{n}.glb'
        assert p.is_file(), f'source missing: {p}'
        shutil.copy2(p, root / 'assets/story' / p.name)
        records.append({'name': n, 'sha256': digest(p), 'copy': 'assets/story/' + p.name})
else:
    for n in names:
        p = root / 'assets/story' / f'{n}.glb'
        assert p.is_file(), f'repository missing: {p}'
        records.append({'name': n, 'sha256': digest(p), 'path': 'assets/story/' + p.name})

(root / 'assets/source_manifest.json').write_text(json.dumps(
    {'story_assets': records,
     'license_note': 'Source assets generated with Tripo (MagicLomix project); commercial license not verified.'},
    ensure_ascii=False, indent=2))
print('OK', len(records), 'GLB verified in assets/story/')
