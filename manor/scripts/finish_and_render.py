import bpy, json, math, ast, os, time
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
ns={};exec(compile((BASE/'scripts/recover_namespace.py').read_text(),'recover_namespace.py','exec'),ns)
exec(compile((BASE/'scripts/manor_validate.py').read_text(),'manor_validate.py','exec'),ns)
scene=ns['scene'];bpy.context.window.scene=scene
# Save recovery before any optional native consolidation.
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Verdant_Manor.blend'))
# Native joins only for bookcase/chair/bed/sofa assemblies, not evaluated mesh extraction.
# Avoid mutating the dependency graph while evaluated meshes are being read.
parents=[o for o in scene.objects if o.type=='EMPTY' and not o.get('interactive') and len(o.children)>3]
for parent in parents:
    obs=[o for o in parent.children if o.type=='MESH']
    if len(obs)<4:continue
    bpy.ops.object.select_all(action='DESELECT')
    for ob in obs:ob.select_set(True)
    bpy.context.view_layer.objects.active=obs[0]
    # Modifier application is omitted; join keeps original base geometries and active modifier.
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
# Reuse only metadata/final save tail from original optimization script.
s=(BASE/'scripts/manor_optimize.py').read_text();s=s[s.index('# Keep sculpted mouldings'):]
ns['count_before']=13782;ns['total_merged']=0
exec(compile(s,'save_metadata','exec'),ns)
# Render previews in a separate process so the live editor is not blocked.
scene.render.image_settings.file_format='PNG';scene.render.resolution_x=1280;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True
scene.cycles.max_bounces=5;scene.cycles.diffuse_bounces=2;scene.cycles.transmission_bounces=4
try:
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='METAL';prefs.get_devices()
    for d in prefs.devices:d.use=True
    scene.cycles.device='GPU';print('Metal devices:',[(d.name,d.type) for d in prefs.devices],flush=True)
except Exception as e:print('Using CPU:',str(e),flush=True);scene.cycles.device='CPU'
for cam,filename in [('01 Exterior','01_exterior.png'),('02 Drawing room','02_drawing_room.png'),('03 Library','03_library.png'),('04 Kitchen','04_kitchen.png'),('05 Bedroom','05_bedroom.png'),('06 Attic','06_attic.png'),('08 Rear garden','08_rear_garden.png')]:
    scene.camera=ns['cameras'][cam];scene.render.filepath=str(BASE/filename)
    print('RENDER_START',filename,flush=True);bpy.ops.render.render(write_still=True);print('RENDER_DONE',filename,flush=True)
# Architectural cutaways for each floor. Restore visibility after each render.
scene.render.resolution_x=1280;scene.render.resolution_y=900;scene.cycles.samples=12
ns['roofs'].hide_render=True;ns['gardens'].hide_render=True
# Conservatory is part of ground floor, keep present only for first-floor view.
cut=ns['camera']('09 Floor cutaway',(22,-26,30),(0,0,2),40,35)
for i in range(3):
    for j in range(3):ns['levels'][j].hide_render=(j!=i);ns['ceilings'][j].hide_render=True
    cut.location=(19,-25,32+i*4);cut.rotation_euler=(ns['Vector']((0,0,ns['Z'][i]+1))-cut.location).to_track_quat('-Z','Y').to_euler();scene.camera=cut
    scene.render.filepath=str(BASE/f'0{9+i}_floor_{i+1}.png');bpy.ops.render.render(write_still=True);print('FLOOR_DONE',i+1,flush=True)
print('ALL_PREVIEWS_COMPLETE',flush=True)
