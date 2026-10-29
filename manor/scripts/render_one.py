import bpy,sys,math
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1]
arg=sys.argv[sys.argv.index('--')+1:];key=arg[0]
scene=bpy.data.scenes['Manor_Verdant_1880'];bpy.context.window.scene=scene
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True;scene.cycles.max_bounces=5;scene.cycles.transmission_bounces=4
scene.render.image_settings.file_format='PNG';scene.render.resolution_x=1440;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
try:
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='METAL';prefs.get_devices()
    for d in prefs.devices:d.use=(d.type=='METAL')
    scene.cycles.device='GPU'
except:scene.cycles.device='CPU'
lookup={'exterior':('01 Exterior','01_exterior.png'),'drawing':('02 Drawing room','02_drawing_room.png'),'library':('03 Library','03_library.png'),'kitchen':('04 Kitchen','04_kitchen.png'),'bedroom':('05 Bedroom','05_bedroom.png'),'attic':('06 Attic','06_attic.png'),'rear':('08 Rear garden','08_rear_garden.png')}
if key in lookup:
    cam,file=lookup[key];scene.camera=bpy.data.objects['MV_'+cam]
else:
    floor=int(key[-1]);file=f'0{8+floor}_floor_{floor}.png'
    for name in ['04 Roof | 屋顶·可整体隐藏','05 Garden | 花园']:bpy.data.collections[name].hide_render=True
    for i,name in enumerate(['01 Ground | 一层','02 Upper | 二层','03 Attic | 三层阁楼'],1):bpy.data.collections[name].hide_render=(i!=floor)
    for i in range(1,4):bpy.data.collections[f'L{i} Ceiling | 天花·可隐藏'].hide_render=True
    d=bpy.data.cameras.new('Floor cutaway');o=bpy.data.objects.new('Floor cutaway',d);scene.collection.objects.link(o);o.location=(19,-27,35+(floor-1)*4);target=Vector((0,0,.48+(floor-1)*4));o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=36;scene.camera=o
    scene.cycles.samples=16;scene.render.resolution_x=1440;scene.render.resolution_y=1100
scene.render.filepath=str(BASE/file)
print('RENDERING',key,flush=True);bpy.ops.render.render(write_still=True);print('COMPLETE',file,flush=True)
