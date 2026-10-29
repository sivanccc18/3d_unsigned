#!/usr/bin/env python3
"""Verdant Manor《未签的判决》源工程一键重建（宿主编排脚本，本机无需 bpy）。

产物：
  manor/Verdant_Manor_rebuilt.blend      构建场景（润色前）
  manor/Verdant_Manor.blend              润色 + 合并后的最终工程
  manor_walkthrough/assets/              浏览器游戏运行资产（manor.glb.gz 等）
  manor_mystery/Verdant_Manor_Mystery.blend  搜证版工程（含人物/物证集合）

用法：
  python3 build_all.py                     # 默认 Blender 路径
  python3 build_all.py --blender /path/to/Blender
  python3 build_all.py --with-renders      # 额外渲染 10 张 Cycles 预览图（很慢）

环境要求：Blender 5.2.2 LTS（开发与验证版本；其他大版本 bpy API 可能不兼容）。
贴图已随仓库附带；只有删除 manor/textures/ 后重建才需要联网 + Pillow。
"""
import argparse, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BLENDER_DEFAULT = '/Applications/Blender.app/Contents/MacOS/Blender'

def run(step, cmd, expect=None):
    print(f'\n=== [{step}] {" ".join(str(c) for c in cmd)} ===', flush=True)
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True)
    tail = '\n'.join((r.stdout or '').splitlines()[-14:])
    print(tail, flush=True)
    if r.returncode != 0:
        sys.exit(f'[{step}] 失败，退出码 {r.returncode}\n{tail}')
    if expect and expect not in (r.stdout or ''):
        sys.exit(f'[{step}] 退出码 0 但缺少标志输出 "{expect}"，判定失败')
    print(f'[{step}] 完成', flush=True)

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument('--blender', default=BLENDER_DEFAULT, help='Blender 可执行文件路径')
ap.add_argument('--with-renders', action='store_true', help='额外渲染 10 张 Cycles 预览图（很慢）')
a = ap.parse_args()
B = a.blender
if not Path(B).exists():
    sys.exit(f'找不到 Blender: {B}（用 --blender 指定，如 /Applications/Blender.app/Contents/MacOS/Blender）')
print(f'Blender: {B}')

run('1 贴图（已附带则跳过；缺失时需联网 + Pillow）', [sys.executable, ROOT / 'manor/scripts/prepare_materials.py'])
run('2 构建场景（约 1-3 分钟）', [B, '--background', '--factory-startup', '--python', ROOT / 'manor/scripts/build_scene.py'], expect='Rebuilt scene saved')
run('3 润色与通路校验', [B, '--background', '--factory-startup', ROOT / 'manor/Verdant_Manor_rebuilt.blend', '--python', ROOT / 'manor/scripts/final_polish.py'], expect='POLISH_SAVED')
finish = 'finish_and_render.py' if a.with_renders else 'finish_build.py'
run(f'4 合并网格并保存最终工程（{finish}）', [B, '--background', '--factory-startup', ROOT / 'manor/Verdant_Manor.blend', '--python', ROOT / 'manor/scripts' / finish], expect='FINISH_BUILD_SAVED')
run('5 导出浏览器游戏资产', [B, '--background', '--factory-startup', ROOT / 'manor/Verdant_Manor.blend', '--python', ROOT / 'manor_walkthrough/scripts/export_web.py'], expect='EXPORT_READY')
run('6 校验六件人物/物证 GLB', [sys.executable, ROOT / 'manor_mystery/scripts/prepare.py'], expect='OK 6 GLB verified')
run('7 生成搜证版工程', [B, '--background', '--factory-startup', ROOT / 'manor/Verdant_Manor.blend', '--python', ROOT / 'manor_mystery/scripts/build_story_blend.py'], expect='MYSTERY_BLEND_SAVED')

print('\n全部完成。产物：')
for p in ['manor/Verdant_Manor.blend', 'manor_walkthrough/assets/manor.glb.gz', 'manor_mystery/Verdant_Manor_Mystery.blend']:
    f = ROOT / p
    print(f'  {"OK " if f.exists() else "缺失"} {p} {f.stat().st_size//1048576}MB' if f.exists() else f'  缺失 {p}')
