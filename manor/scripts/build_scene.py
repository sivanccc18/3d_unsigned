"""Rebuild the authored manor in a new Blender scene; does not delete existing scenes.
Run with Blender's Python editor or Blender --background --python build_scene.py.
Download materials first with prepare_materials.py if textures are missing.
"""
from pathlib import Path
import bpy
BASE=Path(__file__).resolve().parents[1]
if bpy.data.scenes.get('Manor_Verdant_1880'):
    raise RuntimeError('Manor_Verdant_1880 already exists. Open a fresh Blender file before rebuilding; existing scene is not modified.')
ns={'__file__':str(BASE/'scripts'/'manor_core.py')}  # manor_core 用它解析相对 BASE
for name in ['manor_core.py','manor_interiors.py','manor_refine.py','manor_garden.py','manor_validate.py']:
    exec(compile((BASE/'scripts'/name).read_text(),name,'exec'),ns)
ns['scene'].camera=ns['cameras']['01 Exterior']
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Verdant_Manor_rebuilt.blend'))
print('Rebuilt scene saved without replacing original deliverable.')
