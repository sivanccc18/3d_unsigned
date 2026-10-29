import bpy, math, json
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1]
ns={};exec(compile((BASE/'scripts/recover_namespace.py').read_text(),'recover_namespace.py','exec'),ns)
scene=ns['scene'];Z=ns['Z'];box=ns['box'];plane=ns['plane'];beam=ns['beam'];coll=ns['coll'];facade=ns['facade'];room_c=ns['room_c'];furn_c=ns['furn_c'];M=ns['M'];roofs=ns['roofs'];lighting=ns['lighting']
# Shift furniture away from east bedroom/servant-room door landings.
for ob in scene.objects:
    if ob.type!='EMPTY' or not ob.children:continue
    x,y,z=ob.location
    if abs(y+1.8)<.05 and x>2.5 and z>4:
        if ob.name.startswith('MV_Chair') or ob.name.startswith('MV_Table'):ob.location.x-=1.25;ob.location.y-=.35
# Rebuild bath/dressing finishes with the connecting opening at y=2.8.
for key,x1,x2 in [('Bath & washroom',-11.8,-7.2),('Dressing room',-7.1,-2.6)]:
    c=room_c[(1,key)]
    for ob in list(c.objects):bpy.data.objects.remove(ob,do_unlink=True)
    for xx in [x1,x2]:
        internal=abs(xx+7.2)<.02 or abs(xx+7.1)<.02
        intervals=[(1.42,2.18),(3.42,4.4)] if internal else [(1.42,4.4)]
        for ya,yb in intervals:
            for zz,h,w in [(.1,.2,.055),(1.03,.085,.055),(.52,.78,.025)]:box('Bathroom oak finish',(xx,(ya+yb)/2,Z[1]+zz),(w,yb-ya,h),'Walnut',c,.009)
            if internal:
                p=plane('Door clear wallpaper',(xx,(ya+yb)/2,Z[1]+2.32),yb-ya,2.45,'Wallpaper ivory',c,True);p.rotation_euler.z=math.pi/2 if key.startswith('Bath') else -math.pi/2
        if internal:
            p=plane('Wallpaper over bathroom door',(xx,2.8,Z[1]+3.08),1.24,1.00,'Wallpaper ivory',c,True);p.rotation_euler.z=math.pi/2 if key.startswith('Bath') else -math.pi/2
# Remove gable diagonal faces that overlap high attic windows; foliage/static meshes joined elsewhere untouched.
import bmesh
for ob in facade[2].objects:
    if ob.type!='MESH':continue
    bm=bmesh.new();bm.from_mesh(ob.data);target=[]
    for f in bm.faces:
        coords=[ob.matrix_world@v.co for v in f.verts];center=sum(coords,Vector())/len(coords)
        if -7.32<center.y<-7.12 and 11.19<center.z<12.08 and any(abs(center.x-cx)<1.55 for cx in [-8,0,8]):
            # Diagonal timber faces only: not panes, window jambs or wall panels.
            if abs(f.normal.y)<.98 and any(abs(c.z-center.z)>.03 for c in coords):target.append(f)
    if target:bmesh.ops.delete(bm,geom=target,context='FACES')
    bm.to_mesh(ob.data);bm.free();ob.data.update()
# Separate conservatory roofing and furnishings for predictable hide/show.
cons=bpy.data.collections.get('L1 Conservatory | 侧翼玻璃暖房');consroof=coll('Roof | 暖房玻璃屋顶',roofs);consfurn=coll('L1 Conservatory furnishings | 暖房家具',ns['furn'][0])
for ob in list(cons.objects):
    if ob.name.startswith(('MV_Conservatory roof','MV_Roof glazing bar','MV_Conservatory ridge')):
        cons.objects.unlink(ob);consroof.objects.link(ob)
    elif ob.parent is not None or (ob.type=='EMPTY' and not ob.get('interactive')):
        cons.objects.unlink(ob);consfurn.objects.link(ob)
# Give upholstery rounded edges and a fine woven normal (original authoring rounded modifiers were lost on joins).
for name in ['Velvet sage','Velvet wine','Linen','Leather']:
    m=M[name];n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF');tc=n.new('ShaderNodeTexCoord');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=210;noise.inputs['Detail'].default_value=2;l.new(tc.outputs['Generated'],noise.inputs['Vector']);b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.18;b.inputs['Distance'].default_value=.012;l.new(noise.outputs['Fac'],b.inputs['Height']);l.new(b.outputs['Normal'],p.inputs['Normal'])
for ob in scene.objects:
    if ob.type=='MESH' and ob.parent and ob.parent.name.startswith(('MV_Sofa','MV_Chair','MV_Bed','MV_Table','MV_Cabinet')):
        mod=ob.modifiers.new('Fine furniture edges','BEVEL');mod.width=.014;mod.segments=2;mod.limit_method='ANGLE'
# Outdoor lighting: a physically plausible sky for indirect illumination plus bright visible sky.
n=scene.world.node_tree.nodes;l=scene.world.node_tree.links;n.clear()
sky=n.new('ShaderNodeTexSky');sky.sky_type='HOSEK_WILKIE';sky.sun_direction=Vector((-.55,-.45,.72)).normalized();sky.turbidity=2.5
bg=n.new('ShaderNodeBackground');bg.inputs['Strength'].default_value=.5;l.new(sky.outputs['Color'],bg.inputs['Color'])
visible=n.new('ShaderNodeBackground');visible.inputs['Color'].default_value=(.43,.64,.82,1);visible.inputs['Strength'].default_value=.7
lp=n.new('ShaderNodeLightPath');mix=n.new('ShaderNodeMixShader');l.new(lp.outputs['Is Camera Ray'],mix.inputs[0]);l.new(bg.outputs[0],mix.inputs[1]);l.new(visible.outputs[0],mix.inputs[2]);out=n.new('ShaderNodeOutputWorld');l.new(mix.outputs[0],out.inputs[0])
for ob in scene.objects:
    if ob.type=='LIGHT' and ob.data.type=='SUN':ob.data.energy=1.8
scene.view_settings.exposure=-.25
# Extend ground beyond authored estate; not more planted land, only backdrop under sky.
back=coll('Garden | 远景地面',ns['gardens']);box('Distant meadow',(0,10,-.51),(480,480,.1),'Grass',back)
# Adjust photo viewpoints to avoid standing behind opened door leaves.
def aim(name,loc,target,lens):
    o=ns['cameras'][name];o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=lens
# Look across room toward fireplace and blue-green wallcovering.
aim('01 Exterior',(37,-49,23),(0,1,6.0),43)
aim('02 Drawing room',(-10.9,-6.35,2.05),(-3.0,-2.25,1.8),20)
aim('03 Library',(-10.8,2.0,2.08),(-4.3,5.9,1.75),21)
aim('04 Kitchen',(7.9,1.82,2.14),(3.4,4.12,1.5),17)
aim('05 Bedroom',(-10.7,-6.3,6.05),(-3.8,-2.6,5.65),21)
aim('06 Attic',(-9.0,-1.6,10.12),(-6.3,-6.0,9.6),19)
aim('08 Rear garden',(-35,42,23),(0,2,5.0),40)
# Wider validation: include east doors, bathroom connection and all service staircase treads.
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
def probe(name,a,b):
    a=Vector(a);d=Vector(b)-a;hit,loc,normal,idx,ob,mt=scene.ray_cast(deps,a,d.normalized(),distance=d.length)
    return {'name':name,'clear':not hit,'blocker':ob.name if hit else None,'at':list(loc) if hit else None}
result=json.loads((BASE/'validation.json').read_text());tests=result['tests']
for i in [1,2]:
    for x in [5,9.7]:
        for dx in [-.3,0,.3]:tests.append(probe(f'L{i+1} guest door width {x} / {dx}',(x+dx,.15,Z[i]+1.4),(x+dx,-2.05,Z[i]+1.4)))
for i in [0,1]:
    for side in [0,1]:
        for k in range(12):
            x=10.36+(-.6325 if side==0 else .6325);y=2.9+(k+.5)*.22 if side==0 else 2.9+(12-k-.5)*.22;z=Z[i]+(k+1)/6 if side==0 else Z[i]+2+(k+1)/6
            tests.append(probe(f'L{i+1} service stair {side} tread {k}',(x,y,z+.12),(x,y,z+2.07)))
tests.append(probe('Bath to dressing',(-7.65,2.8,Z[1]+1.4),(-6.65,2.8,Z[1]+1.4)))
result['tests']=tests;result['test_scope']='Main-route samples, width samples at east guest entrances, main-stair samples and all service-stair treads; not a physics capsule test.'
(BASE/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps({'total_tests':len(tests),'blocked':[t for t in tests if not t['clear']]},ensure_ascii=False),flush=True)
# Pack portable textures and save updated final .blend with all collections visible.
for c in ns['levels']+ns['ceilings']+[roofs,ns['gardens']]:c.hide_render=False;c.hide_viewport=False
scene.camera=ns['cameras']['01 Exterior'];scene.render.resolution_x=1600;scene.render.resolution_y=1100
scene.cycles.samples=32;scene.render.film_transparent=False
text=bpy.data.texts.get('START HERE | 庄园场景说明')
if text:text.write('\nFinal review: bedroom doorway furnishings moved; bath/dressing finishes opened; conservatory roof separated; service-stair clearance tests added. See validation.json for exact results.\n')
summary=json.loads((BASE/'model_summary.json').read_text());summary.update({'objects':len(scene.objects),'mesh_objects':sum(o.type=='MESH' for o in scene.objects),'mesh_polygons':sum(len(o.data.polygons) for o in scene.objects if o.type=='MESH'),'passage_probes':len(tests),'probe_failures':sum(not t['clear'] for t in tests)})
(BASE/'model_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Verdant_Manor.blend'));print('POLISH_SAVED',flush=True)
