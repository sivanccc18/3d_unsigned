"""finish_and_render.py 的无渲染变体：合并网格 + 写元数据 + 保存最终 .blend，
跳过 10 张 Cycles 预览渲染（可选、耗时长）。需要预览图时再单独跑 finish_and_render.py。

运行：blender --background --factory-startup manor/Verdant_Manor.blend --python manor/scripts/finish_build.py
"""
import bpy, json, math, ast, os, time
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
ns={};exec(compile((BASE/'scripts/recover_namespace.py').read_text(),'recover_namespace.py','exec'),ns)
exec(compile((BASE/'scripts/manor_validate.py').read_text(),'manor_validate.py','exec'),ns)
scene=ns['scene'];bpy.context.window.scene=scene
# Save recovery before any optional native consolidation.
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Verdant_Manor.blend'))
# Native joins only for bookcase/chair/bed/sofa assemblies, not evaluated mesh extraction.
parents=[o for o in scene.objects if o.type=='EMPTY' and not o.get('interactive') and len(o.children)>3]
for parent in parents:
    obs=[o for o in parent.children if o.type=='MESH']
    if len(obs)<4:continue
    bpy.ops.object.select_all(action='DESELECT')
    for ob in obs:ob.select_set(True)
    bpy.context.view_layer.objects.active=obs[0]
    active=obs[0]
    for mod in list(active.modifiers):active.modifiers.remove(mod)
    bpy.ops.object.join();active.name=parent.name+' | mesh'
# Second pass join unparented meshes per room/facade collection. Leaves already batched.
for c in list(bpy.data.collections):
    if not c.name.startswith(('L1 ','L2 ','L3 ')):continue
    obs=[o for o in c.objects if o.type=='MESH' and o.parent is None]
    if len(obs)<5:continue
    bpy.ops.object.select_all(action='DESELECT')
    for ob in obs:ob.select_set(True)
    bpy.context.view_layer.objects.active=obs[0];active=obs[0]
    for mod in list(active.modifiers):active.modifiers.remove(mod)
    bpy.ops.object.join();active.name=c.name+' | mesh'
bpy.ops.object.select_all(action='DESELECT')
print('Native consolidation:',len(scene.objects),flush=True)
# Metadata + packed textures + final save (tail of manor_optimize.py, no preview renders).
s=(BASE/'scripts/manor_optimize.py').read_text();s=s[s.index('# Keep sculpted mouldings'):]
ns['count_before']=13782;ns['total_merged']=0
exec(compile(s,'save_metadata','exec'),ns)
print('FINISH_BUILD_SAVED',flush=True)
