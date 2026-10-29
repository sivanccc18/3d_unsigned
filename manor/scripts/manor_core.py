import bpy, math, random, json, os, bmesh
from mathutils import Vector
from pathlib import Path
# BASE 由调用方决定：被 exec 时 build_scene.py 会注入 __file__；直接运行时取脚本上一级。
BASE=Path(globals()['__file__']).resolve().parents[1] if '__file__' in globals() else Path(bpy.data.filepath).resolve().parent
PREFIX='MV_'
random.seed(1829)
# Explicit new scene; existing scene and datablocks are not deleted.
scene=bpy.data.scenes.new('Manor_Verdant_1880')
bpy.context.window.scene=scene
scene.unit_settings.system='METRIC'; scene.unit_settings.scale_length=1
scene.render.engine='CYCLES'; scene.cycles.samples=32
scene.cycles.use_denoising=True
scene.render.resolution_x=1600; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
scene.world=bpy.data.worlds.new('MV_Daylight')
scene.world.use_nodes=True
wn=scene.world.node_tree.nodes; wl=scene.world.node_tree.links
wn.clear(); bg=wn.new('ShaderNodeBackground'); bg.name='Background'; wo=wn.new('ShaderNodeOutputWorld'); wl.new(bg.outputs[0],wo.inputs[0])
sky=wn.new('ShaderNodeTexSky'); sky.sky_type='MULTIPLE_SCATTERING' if 'MULTIPLE_SCATTERING' in [e.identifier for e in sky.bl_rna.properties['sky_type'].enum_items] else 'NISHITA'; sky.sun_elevation=math.radians(43); sky.sun_rotation=math.radians(140); sky.altitude=.15
wl.new(sky.outputs['Color'],wn.get('Background').inputs['Color']); wn.get('Background').inputs['Strength'].default_value=.35
ROOT=bpy.data.collections.new('MANOR | 庄园总集'); scene.collection.children.link(ROOT)
C={}; M={}; openings=[]; room_records=[]; cameras={}
def coll(name,parent=ROOT):
    c=bpy.data.collections.new(name); parent.children.link(c); C[name]=c; return c
levels=[coll('01 Ground | 一层'),coll('02 Upper | 二层'),coll('03 Attic | 三层阁楼')]
roofs=coll('04 Roof | 屋顶·可整体隐藏'); gardens=coll('05 Garden | 花园'); lighting=coll('06 Cameras & Lights | 相机与灯光'); guides=coll('07 Navigation | 导航标记')
struct=[]; facade=[]; furn=[]; rooms=[]; ceilings=[]
for i in range(3):
    struct.append(coll(f'L{i+1} Structure | 墙体楼板与楼梯',levels[i])); facade.append(coll(f'L{i+1} Facade | 外墙木构与门窗',levels[i])); furn.append(coll(f'L{i+1} Furniture | 家具',levels[i])); rooms.append(coll(f'L{i+1} Rooms | 各房间饰面',levels[i])); ceilings.append(coll(f'L{i+1} Ceiling | 天花·可隐藏',levels[i]))
def mat(name,col,rough=.5,metal=0):
    m=bpy.data.materials.new(PREFIX+name); m.diffuse_color=(*col,1); m.use_nodes=True
    m.node_tree.nodes.clear(); p=m.node_tree.nodes.new('ShaderNodeBsdfPrincipled'); p.name='Principled BSDF'; out=m.node_tree.nodes.new('ShaderNodeOutputMaterial'); m.node_tree.links.new(p.outputs[0],out.inputs['Surface']); p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
    M[name]=m; return m
wood=mat('Walnut',(0.12,.035,.022),.38)
# world-space fine grain for small carved oak elements
n=wood.node_tree.nodes;l=wood.node_tree.links;p=n.get('Principled BSDF');tc=n.new('ShaderNodeTexCoord');mapping=n.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(4,45,3);l.new(tc.outputs['Generated'],mapping.inputs[0]);noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=4;noise.inputs['Detail'].default_value=3;l.new(mapping.outputs[0],noise.inputs['Vector']);r=n.new('ShaderNodeValToRGB');r.color_ramp.elements[0].color=(.045,.012,.008,1);r.color_ramp.elements[1].color=(.21,.066,.032,1);l.new(noise.outputs['Fac'],r.inputs[0]);l.new(r.outputs[0],p.inputs['Base Color']);b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.14;b.inputs['Distance'].default_value=.012;l.new(noise.outputs['Fac'],b.inputs['Height']);l.new(b.outputs[0],p.inputs['Normal'])
for name,col,rough,metal in [('Burgundy timber',(.20,.045,.035),.48,0),('Limestone',(.65,.53,.35),.75,0),('Plaster',(.76,.69,.53),.8,0),('Ivory',(.86,.80,.65),.58,0),('Brass',(.44,.27,.075),.28,.75),('Iron',(.027,.033,.031),.46,.65),('Velvet sage',(.11,.20,.17),.88,0),('Velvet wine',(.30,.055,.057),.88,0),('Linen',(.79,.74,.60),.92,0),('Leather',(.09,.038,.016),.48,0),('Coal',(.01,.008,.006),.8,0),('Copper',(.46,.19,.07),.34,.7),('Ceramic',(.75,.81,.75),.21,0),('Earth',(.12,.074,.041),.96,0),('Slate',(.14,.17,.17),.85,0),('Leaf dark',(.052,.13,.025),.83,0),('Leaf',(.13,.24,.049),.83,0),('Leaf light',(.23,.34,.074),.83,0),('Rose',(.47,.09,.16),.75,0),('Lavender',(.28,.17,.39),.8,0),('White flower',(.86,.79,.63),.8,0),('Grass',(.18,.28,.058),.94,0),('Pages',(.63,.54,.37),.88,0),('Water',(.13,.28,.25),.1,.2)]: mat(name,col,rough,metal)
glass=mat('Glazing',(.79,.91,.92),.13); gp=glass.node_tree.nodes.get('Principled BSDF');gp.inputs['Transmission Weight'].default_value=1;gp.inputs['IOR'].default_value=1.46
em=mat('Warm lamp',(.92,.66,.30),.3);ep=em.node_tree.nodes.get('Principled BSDF');ep.inputs['Emission Color'].default_value=(1,.67,.28,1);ep.inputs['Emission Strength'].default_value=2
for i,col in enumerate([(.16,.04,.027),(.05,.095,.095),(.16,.12,.058),(.25,.13,.065),(.065,.075,.14)]):mat('Book'+str(i),col,.63)
def image_mat(name,file,scale=1,rough=.75):
    m=mat(name,(.5,.4,.3),rough);n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF');tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(BASE/'textures'/file),check_existing=True);uv=n.new('ShaderNodeTexCoord');v=n.new('ShaderNodeVectorMath');v.operation='SCALE';v.inputs[3].default_value=scale;l.new(uv.outputs['UV'],v.inputs[0]);l.new(v.outputs[0],tex.inputs['Vector']);l.new(tex.outputs['Color'],p.inputs['Base Color']);return m
manifest=json.loads((BASE/'textures/sources.json').read_text())
for asset,rec in manifest.items():
    m=mat(asset,(.4,.3,.2),.8); n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF');uv=n.new('ShaderNodeTexCoord');v=n.new('ShaderNodeVectorMath');v.operation='SCALE';v.inputs[3].default_value=1/rec['size_m'];l.new(uv.outputs['UV'],v.inputs[0])
    for kind,fname in rec['maps'].items():
        tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(BASE/'textures'/fname),check_existing=True);l.new(v.outputs[0],tex.inputs['Vector'])
        if kind=='Diffuse':l.new(tex.outputs['Color'],p.inputs['Base Color'])
        elif kind=='Rough':tex.image.colorspace_settings.name='Non-Color';l.new(tex.outputs['Color'],p.inputs['Roughness'])
        else:
            tex.image.colorspace_settings.name='Non-Color';nm=n.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.5;l.new(tex.outputs['Color'],nm.inputs['Color']);l.new(nm.outputs[0],p.inputs['Normal'])
for name in ['sage','blue','ivory']: image_mat('Wallpaper '+name,'wallpaper_'+name+'.jpg',1/.8)
image_mat('Rug','oriental_rug.jpg',1,.95);image_mat('Painting','landscape_painting.jpg',1,.72)
# Every mesh has real-scale local planar UVs; no un-applied cube scale.
def mesh(name,vs,fs,ma,c,uvmode=True):
    me=bpy.data.meshes.new(PREFIX+name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(PREFIX+name,me);c.objects.link(o)
    if ma:me.materials.append(M[ma] if isinstance(ma,str) else ma)
    if uvmode:
        uv=me.uv_layers.new(name='UVMap')
        for poly in me.polygons:
            axis=max(range(3),key=lambda a:abs(poly.normal[a]));axes=[(1,2),(0,2),(0,1)][axis]
            for li in poly.loop_indices:
                co=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]],co[axes[1]])
    return o
def box(name,loc,size,ma,c,bevel=0):
    x,y,z=(a/2 for a in size);vs=[(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]
    o=mesh(name,vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],ma,c);o.location=loc
    if bevel:
        mod=o.modifiers.new('Soft edges','BEVEL');mod.width=bevel;mod.segments=2
    return o
def beam(name,a,b,width,depth,ma,c):
    a=Vector(a);b=Vector(b);o=box(name,(a+b)/2,(width,depth,(b-a).length),ma,c,.01);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def cyl(name,loc,r,depth,ma,c,n=16,r2=None):
    if r2 is None:r2=r
    vs=[(math.cos(i*math.tau/n)*rr,math.sin(i*math.tau/n)*rr,z) for z,rr in [(-depth/2,r),(depth/2,r2)] for i in range(n)]
    fs=[tuple(reversed(range(n))),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    o=mesh(name,vs,fs,ma,c);o.location=loc
    for p in o.data.polygons:p.use_smooth=len(p.vertices)==4
    return o
def sphere(name,loc,scale,ma,c,sub=2):
    me=bpy.data.meshes.new(PREFIX+name);bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=sub,radius=1);bm.to_mesh(me);bm.free();o=bpy.data.objects.new(PREFIX+name,me);c.objects.link(o);o.location=loc;o.scale=scale;me.materials.append(M[ma]);
    for p in me.polygons:p.use_smooth=True
    return o
def curve(name,points,radius,ma,c):
    cu=bpy.data.curves.new(PREFIX+name,'CURVE');cu.dimensions='3D';cu.resolution_u=10;cu.bevel_depth=radius;cu.bevel_resolution=2;sp=cu.splines.new('BEZIER');sp.bezier_points.add(len(points)-1)
    for p,co in zip(sp.bezier_points,points):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
    o=bpy.data.objects.new(PREFIX+name,cu);c.objects.link(o);cu.materials.append(M[ma]);return o
def plane(name,loc,w,h,ma,c,vertical=False):
    vs=[(-w/2,-h/2,0),(w/2,-h/2,0),(w/2,h/2,0),(-w/2,h/2,0)]
    o=mesh(name,vs,[(0,1,2,3)],ma,c);o.location=loc
    if vertical:o.rotation_euler.x=math.pi/2
    if ma in ['Rug','Painting']:
        for i,uv in enumerate([(0,0),(1,0),(1,1),(0,1)]):o.data.uv_layers.active.data[i].uv=uv
    return o
def area(name,loc,target,power,size=3,color=(1,.85,.67)):
    d=bpy.data.lights.new(PREFIX+name,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=color;o=bpy.data.objects.new(PREFIX+name,d);lighting.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
def camera(name,loc,target,lens=28,ortho=None):
    d=bpy.data.cameras.new(PREFIX+name);o=bpy.data.objects.new(PREFIX+name,d);lighting.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_start=.05;d.clip_end=300
    if ortho:d.type='ORTHO';d.ortho_scale=ortho
    cameras[name]=o;return o
# wall builder divides actual solids around openings, no opaque wall behind glazing/doors.
def wall(name,p1,p2,z,h,th,ma,c,holes=[]):
    a=Vector((p1[0],p1[1],0));b=Vector((p2[0],p2[1],0));vec=b-a;L=vec.length;unit=vec/L;theta=math.atan2(vec.y,vec.x)
    bounds=sorted(set([0,L]+[max(0,min(L,v)) for s,w,bottom,top in holes for v in [s-w/2,s+w/2]]))
    for u,v in zip(bounds,bounds[1:]):
        if v-u<.001:continue
        active=[o for o in holes if o[0]-o[1]/2<(u+v)/2<o[0]+o[1]/2]
        intervals=[(0,h)]
        if active:
            low=min(o[2] for o in active);high=max(o[3] for o in active);intervals=[(0,low),(high,h)]
        for lo,hi in intervals:
            if hi-lo>.001:
                co=a+unit*((u+v)/2);ob=box(name,(co.x,co.y,z+(hi+lo)/2),(v-u,th,hi-lo),ma,c,.008);ob.rotation_euler.z=theta
    for s,w,bottom,top in holes:
        co=a+unit*s;openings.append({'wall':name,'center':[co.x,co.y,z+bottom],'width':w,'height':top-bottom,'angle':theta})
    return theta
# floor slabs with rectangular stair wells, preserve headroom across all storeys.
def slab(name,z,holes,c):
    xs=sorted(set([-12,12]+[v for x1,x2,y1,y2 in holes for v in [x1,x2]]));ys=sorted(set([-7,7]+[v for x1,x2,y1,y2 in holes for v in [y1,y2]]))
    for xa,xb in zip(xs,xs[1:]):
        for ya,yb in zip(ys,ys[1:]):
            mid=((xa+xb)/2,(ya+yb)/2)
            if any(x1<mid[0]<x2 and y1<mid[1]<y2 for x1,x2,y1,y2 in holes):continue
            box(name,(mid[0],mid[1],z-.13),(xb-xa,yb-ya,.26),'wood_floor',c)
# Floor walk levels = 0.48,4.48,8.48. Total 3 inhabited storeys, attic roof above.
Z=[.48,4.48,8.48]; H=4.0; wells=[(-1.85,1.85,1.35,6.8),(9.02,11.72,2.75,6.85)]
for i,z in enumerate(Z):slab(f'L{i+1}_Floor',z,[] if i==0 else wells,struct[i])
box('Foundation',(0,0,.08),(24.6,14.6,.64),'Limestone',struct[0],.035)
# Main house walls and windows.
win_centers=[-10,-7,-4,0,4,7,10]
for i,z in enumerate(Z):
    h=4 if i<2 else 1.55;cl=struct[i]
    front=[(x+12,1.65,1.0,3.12) for x in win_centers if x!=0]
    if i==0:front.append((12,2.35,0,3.12))
    elif i==1:front.append((12,2.35,0,3.12))
    else:front=[]
    back=[(x+12,1.5,1.15,3.1) for x in [-9.5,-6,-3.2,3.7,6.8,10.5]] if i<2 else []
    if i==0:back+=[(12,1.5,0,2.6)]
    if i<2:
        wall(f'L{i+1}_South',(-12,-7),(12,-7),z,h,.32,'plastered_wall_02',cl,front)
        wall(f'L{i+1}_North',(-12,7),(12,7),z,h,.32,'plastered_wall_02',cl,back)
        sideholes=[(p+7,1.5,1.08,3.05) for p in [-4.5,0,4.5]]
        wall(f'L{i+1}_West',(-12,-7),(-12,7),z,h,.32,'plastered_wall_02',cl,sideholes)
        wall(f'L{i+1}_East',(12,-7),(12,7),z,h,.32,'plastered_wall_02',cl,sideholes)
    else:
        wall('Attic knee south',(-12,-7),(12,-7),z,h,.26,'Plaster',cl)
        wall('Attic knee north',(-12,7),(12,7),z,h,.26,'Plaster',cl)
# Three parallel cross-gabled roofs, attics have 2.55 m clearance along all corridor routes.
# Gables face south. Valley eaves at 10.03m, ridges 14.7m.
for cx in [-8,0,8]:
    for yy in [-7,7]:
        vs=[(cx-4,yy,10.03),(cx+4,yy,10.03),(cx,yy,14.73)]
        ob=mesh('Attic_Gable',vs,[(0,1,2)],'Plaster',struct[2]);mod=ob.modifiers.new('Gable thickness','SOLIDIFY');mod.thickness=.24
    for side in [-1,1]:
        xedge=cx+side*4.28; vs=[(xedge,-7.55,9.85),(xedge,7.5,9.85),(cx,7.5,14.83),(cx,-7.55,14.83)]
        ob=mesh('Pitched clay roof',vs,[(0,1,2,3)],'clay_roof_tiles_02',roofs);mod=ob.modifiers.new('Roof decking','SOLIDIFY');mod.thickness=.16
        # UV roof aligned to sloped length and ridge direction
        length=math.hypot(4.28,4.98)
        for li,uv in enumerate([(0,0),(0,15.05),(length,15.05),(length,0)]):ob.data.uv_layers.active.data[li].uv=uv
        beam('Decorative bargeboard',(xedge,-7.62,9.85),(cx,-7.62,14.83),.20,.16,'Burgundy timber',roofs)
        beam('Bargeboard rear',(xedge,7.57,9.85),(cx,7.57,14.83),.16,.14,'Burgundy timber',roofs)
    beam('Ridge crest',(cx,-7.7,14.9),(cx,7.6,14.9),.18,.19,'Limestone',roofs)
    # Finials and carved gable kingpost + braces, over solid triangular attic gable.
    cyl('Gable finial',(cx,-7.62,15.2),.085,.85,'Burgundy timber',roofs,n=12,r2=.045)
    sphere('Finial knob',(cx,-7.62,15.67),(.12,.12,.15),'Brass',roofs)
    beam('Gable kingpost',(cx,-7.18,10.1),(cx,-7.18,14.65),.18,.11,'Burgundy timber',facade[2])
    for v in [1.0,2.0,3.0]:
        ht=4.7*(1-v/4)
        for s in [-1,1]:beam('Gable stud',(cx+s*v,-7.17,10.1),(cx+s*v,-7.17,10.03+ht),.12,.10,'Burgundy timber',facade[2])
    for s in [-1,1]:beam('Gable diagonal',(cx,-7.21,10.18),(cx+s*2.75,-7.21,11.12),.16,.10,'Burgundy timber',facade[2])
# Windows and doors framed independently, matching architectural openings.
def window(name,x,y,z,w,h,angle,c,curtains=False):
    created=[]
    def B(n,l,s,ma,bev=0):o=box(name+'_'+n,l,s,ma,c,bev);created.append(o);return o
    B('glass',(0,0,h/2),(w-.16,.035,h-.15),'Glazing')
    for a in [-w/2,w/2]:B('jamb',(a,0,h/2),(.11,.20,h+.15),'Limestone',.01)
    for b in [0,h]:B('lintel',(0,0,b),(w+.16,.21,.12),'Limestone',.01)
    B('sill',(0,-.08,-.08),(w+.28,.43,.12),'Limestone',.02)
    for a in [-w/6,w/6]:B('mullion',(a,-.026,h/2),(.055,.12,h),'Burgundy timber',.008)
    for b in [h*.35,h*.7]:B('transom',(0,-.045,b),(w,.1,.06),'Burgundy timber')
    # slender lead-light diamond pattern
    step=.36
    for sign in [-1,1]:
        for intercept in [i*step-h for i in range(int((w+2*h)/step)+2)]:
            pts=[]
            for xx in [-w/2+.07,w/2-.07]:
                zz=sign*xx+intercept
                if .06<=zz<=h-.06:pts.append((xx,-.068,zz))
            for zz in [.06,h-.06]:
                xx=sign*(zz-intercept)
                if -w/2+.07<xx<w/2-.07:pts.append((xx,-.068,zz))
            if len(pts)>=2:created.append(beam('Lead diamond',pts[0],pts[1],.009,.008,'Iron',c))
    if curtains:
        created.append(beam('Curtain pole',(-w/2-.32,.28,h+.2),(w/2+.32,.28,h+.2),.045,.045,'Brass',c))
        for sign in [-1,1]:
            for k in range(6):
                xx=sign*(w/2+.03)+(k-2.5)*.055
                created.append(cyl('Curtain fold',(xx,.3+math.sin(k)*.04,h/2-.06),.075,h+.18,'Velvet wine',c,n=10,r2=.065))
    co=Vector((x,y,z));ca=math.cos(angle);sa=math.sin(angle)
    for ob in created:
        px,py,pz=ob.location;ob.location=co+Vector((px*ca-py*sa,px*sa+py*ca,pz));ob.rotation_euler.z+=angle
    return created
for i,z in enumerate(Z[:2]):
    for x in win_centers:
        if x!=0:window(f'L{i+1}_FrontWindow',x,-7,z+1.0,1.65,2.12,0,facade[i],True)
    for x in [-9.5,-6,-3.2,3.7,6.8,10.5]:window(f'L{i+1}_RearWindow',x,7,z+1.15,1.5,1.95,math.pi,facade[i])
    for xx,ang in [(-12,-math.pi/2),(12,math.pi/2)]:
        for y in [-4.5,0,4.5]:window('Side window',xx,y,z+1.08,1.5,1.97,ang,facade[i])
# Timber coursing and verticals arranged between openings, not across glass.
for i,z in enumerate(Z[:2]):
    for y in [-7.2,7.2]:
        for height in [.18,.8,3.43,3.90]:box('Horizontal timber',(0,y,z+height),(24.25,.14,.15),'Burgundy timber',facade[i],.014)
        for x in [-12,-11.12,-8.52,-5.52,-2.5,-1.30,1.30,2.5,5.52,8.52,11.12,12]:box('Upright timber',(x,y,z+2),(.16,.16,4.0),'Burgundy timber',facade[i],.01)
        for cx in [-7,-4,4,7,10,-10]:
            for s in [-1,1]:beam('Panel diagonal',(cx,y,z+.24),(cx+s*.64,y,z+.76),.075,.09,'Burgundy timber',facade[i])
    for x in [-12.2,12.2]:
        for height in [.2,.8,3.43,3.91]:box('Side horizontal',(x,0,z+height),(.13,14.3,.15),'Burgundy timber',facade[i])
        for y in [-7,-5.6,-3.35,-1.2,1.2,3.4,5.65,7]:box('Side timber',(x,y,z+2),(.14,.15,4),'Burgundy timber',facade[i])
# Paneled hinged doors; initially open for passage, pivot at side jamb.
def door(name,x,y,z,w=1.2,h=2.55,ang=0,c=None,opened=95):
    if c is None:c=facade[0]
    group=[]
    for xx in [-w/2,w/2]:group.append(box(name+' jamb',(xx,0,h/2),(.13,.30,h+.1),'Walnut',c,.014))
    group.append(box(name+' lintel',(0,0,h),(w+.26,.3,.16),'Walnut',c,.02))
    pivot=bpy.data.objects.new(PREFIX+name+'_Hinge',None);c.objects.link(pivot);pivot.location=(x-w/2*math.cos(ang),y-w/2*math.sin(ang),z);pivot.rotation_euler.z=ang+math.radians(opened);pivot['interactive']='Rotate local Z to open or close';pivot['clear_width_m']=w-.12
    panel=box(name+' leaf',(w/2,0,h/2),(w-.10,.072,h-.07),'Walnut',c,.016);panel.parent=pivot
    for side in [-1,1]:
        for hh,ph in [(h*.27,h*.34),(h*.70,h*.40)]:
            ob=box(name+' raised panel',(w/2,side*.046,hh),(w-.33,.045,ph),'Burgundy timber',c,.012);ob.parent=pivot
        knob=sphere(name+' knob',(w-.21,side*.12,h*.46),(.049,.049,.049),'Brass',c);knob.parent=pivot
    for ob in group:
        px,py,pz=ob.location;ob.location=(x+px*math.cos(ang)-py*math.sin(ang),y+px*math.sin(ang)+py*math.cos(ang),z+pz);ob.rotation_euler.z=ang
    return pivot
for i,z in enumerate(Z[:2]):door('Main entrance' if i==0 else 'Balcony access',0,-7,z,2.2,3.08,0,facade[i],100)
door('Garden door',0,7,Z[0],1.45,2.56,math.pi,facade[0],100)
# Porch / balcony, stair access from garden path.
box('Porch terrace',(0,-8.45,.32),(5.6,3.15,.32),'Limestone',facade[0],.04)
for k in range(3):box('Entrance step',(0,-10.10-k*.34,.32-k*.16),(3.8,.42,.17),'Limestone',facade[0],.022)
box('Balcony deck',(0,-8.35,4.35),(5.5,2.85,.25),'wood_floor',facade[1],.02)
for x in [-2.5,2.5]:
    for y in [-9.6,-7.4]:
        box('Porch post',(x,y,2.40),(.19,.19,3.92),'Burgundy timber',facade[0],.015)
        for s in [-1,1]:beam('Porch bracket',(x,y,3.15),(x+s*.65,y,4.2),.12,.15,'Burgundy timber',facade[0])
        box('Balcony post',(x,y,5.00),(.18,.18,1.20),'Burgundy timber',facade[1],.012)
for y in [-9.65]:
    box('Balcony handrail',(0,y,5.47),(5.2,.16,.15),'Burgundy timber',facade[1],.02)
    for k in range(25):box('Balcony baluster',(-2.4+k*.2,y,4.94),(.045,.065,1.0),'Burgundy timber',facade[1],.005)
for x in [-2.5,2.5]:
    box('Balcony side handrail',(x,-8.5,5.47),(.15,2.3,.15),'Burgundy timber',facade[1])
    for k in range(11):box('Balcony side spindle',(x,-9.5+k*.2,4.94),(.055,.04,1),'Burgundy timber',facade[1])
# Corner turret outside main east wall. Two internal doors replace one side window later.
# Octagonal pavilion attaches via existing east-side opening, uses no intersecting closed mass.
tx,ty=13.8,-4.5;rad=2.05
for i,z in enumerate(Z[:2]):
    cyl('Tower floor',(tx,ty,z-.13),rad,.26,'wood_floor',struct[i],n=8)
    for k in range(8):
        a=math.tau*k/8+math.pi/8;b=math.tau*(k+1)/8+math.pi/8;p1=(tx+rad*math.cos(a),ty+rad*math.sin(a));p2=(tx+rad*math.cos(b),ty+rad*math.sin(b));L=math.dist(p1,p2)
        if k==3:continue
        wall('Turret wall',p1,p2,z,4,.18,'Plaster',struct[i],[(L/2,.85,1.05,3.05)])
        mid=((p1[0]+p2[0])/2,(p1[1]+p2[1])/2);angle=math.atan2(p2[1]-p1[1],p2[0]-p1[0]);window('Turret casement',*mid,z+1.05,.85,2,angle,facade[i])
        box('Tower timber',(p1[0],p1[1],z+2),(.13,.13,4),'Burgundy timber',facade[i])
        beam('Tower rail',(p1[0],p1[1],z+.82),(p2[0],p2[1],z+.82),.12,.12,'Burgundy timber',facade[i])
cyl('Turret spire',(tx,ty,10.62),2.35,4.8,'clay_roof_tiles_02',roofs,n=8,r2=.04)
cyl('Turret finial',(tx,ty,13.4),.055,1.1,'Iron',roofs,n=12)
# Four paired tall chimney stacks with projecting courses and pots.
for x,y in [(-9.7,2.3),(-2.5,4.9),(5.3,3.1),(9.5,-.5)]:
    bottom=10.7;top=16.0 if x<0 else 15.65
    box('Brick chimney',(x,y,(bottom+top)/2),(1.13,.92,top-bottom),'red_bricks_02',roofs,.035)
    for dz in [0,.22,.52]:box('Chimney corbel',(x,y,top-dz),(1.35,.112+.96,.14),'red_bricks_02',roofs,.012)
    for dx in [-.29,.29]:
        cyl('Terracotta pot',(x+dx,y,top+.38),.18,.69,'Burgundy timber',roofs,n=16,r2=.14)
        cyl('Pot rim',(x+dx,y,top+.71),.22,.10,'Burgundy timber',roofs,n=16)
        cyl('Pot opening',(x+dx,y,top+.766),.16,.012,'Coal',roofs,n=16)
# Interior corridor grid. X columns left wing, central hall, right wing.
for i,z in enumerate(Z):
    ht=3.72 if i<2 else 2.58
    # across house corridor borders y=-1 and +1.3
    frontdoors=[(4.4,1.3,0,2.58),(12,2.8,0,2.8),(19.2,1.3,0,2.58)]
    backdoors=[(4.4,1.3,0,2.58),(12,3.7,0,3.6 if i<2 else 2.58),(18.2,1.2,0,2.58),(22.35,1.2,0,2.58)]
    wall('Front corridor',(-12,-1),(12,-1),z,ht,.18,'Plaster',struct[i],frontdoors)
    wall('Rear corridor',(-12,1.3),(12,1.3),z,ht,.18,'Plaster',struct[i],backdoors)
    for x in [-2.5,2.5]:wall('Front room divider',(x,-7),(x,-1),z,ht,.18,'Plaster',struct[i])
    for x in [-2.5,2.5,8.8]:wall('Rear room divider',(x,1.3),(x,7),z,ht,.18,'Plaster',struct[i])
    # Guest wing split for two bedrooms / servant rooms; main ground dining stays whole.
    if i>0:
        wall('East bedroom partition',(7.3,-7),(7.3,-1),z,ht,.18,'Plaster',struct[i])
        # Add door from corridor to eastmost guest room using upper corridor segment replacement below
    # Kitchen rear pantry partition with real connecting doors.
    if i==0:wall('Kitchen pantry',(2.5,4.75),(8.8,4.75),z,ht,.16,'Plaster',struct[i],[(1.2,1.2,0,2.55),(4.8,1.2,0,2.55)])
    if i==0:wall('Pantry division',(5.6,4.75),(5.6,7),z,ht,.16,'Plaster',struct[i])
    # left rear rooms: library ground, master suite upper, attic storage
    if i==1:wall('Dressing partition',(-12,4.5),(-2.5,4.5),z,ht,.16,'Plaster',struct[i],[(4.5,1.2,0,2.55)])
    for x in [-7.6,7.2]:door(f'L{i+1} front room door',x,-1,z,1.25,2.54,0,facade[i],92)
    for x in [-7.6,6.2,10.35]:door(f'L{i+1} rear room door',x,1.3,z,1.15,2.54,math.pi,facade[i],94)
# Room labels stored on empties, no floating text in beauty views.
layouts=[
 [('Drawing room | 会客厅',(-11.8,-2.6,-6.8,-1.12)),('Entrance hall | 入口门厅',(-2.4,2.4,-6.8,-1.12)),('Dining room | 餐厅',(2.6,11.8,-6.8,-1.12)),('Library | 书房',(-11.8,-2.6,1.42,6.8)),('Main stair hall | 主楼梯厅',(-2.4,2.4,1.42,6.8)),('Kitchen | 厨房',(2.6,8.7,1.42,4.64)),('Pantry | 食品储藏',(2.6,5.5,4.85,6.8)),('Utility store | 杂物间',(5.7,8.7,4.85,6.8)),('Service stair | 服务楼梯',(8.9,11.8,1.42,6.8))],
 [('Master bedroom | 主卧',(-11.8,-2.6,-6.8,-1.12)),('Upper sitting room | 小起居室',(-2.4,2.4,-6.8,-1.12)),('Guest bedroom A | 客卧甲',(2.6,7.2,-6.8,-1.12)),('Guest bedroom B | 客卧乙',(7.4,11.8,-6.8,-1.12)),('Bath & washroom | 盥洗室',(-11.8,-7.2,1.42,4.4)),('Dressing room | 更衣室',(-7.1,-2.6,1.42,4.4)),('Linen store | 布草间',(-11.8,-2.6,4.6,6.8)),('Upper landing | 楼梯平台',(-2.4,2.4,1.42,6.8)),('Family study | 家庭书室',(2.6,8.7,1.42,6.8)),('Service stair upper | 后楼梯',(8.9,11.8,1.42,6.8))],
 [('Attic trunks | 阁楼储物',(-11.8,-2.6,-6.8,-1.12)),('Attic landing | 阁楼前厅',(-2.4,2.4,-6.8,-1.12)),('Servant room A | 仆人房甲',(2.6,7.2,-6.8,-1.12)),('Servant room B | 仆人房乙',(7.4,11.8,-6.8,-1.12)),('Old furniture store | 旧物间',(-11.8,-2.6,1.42,6.8)),('Attic stair hall | 阁楼楼梯厅',(-2.4,2.4,1.42,6.8)),('Drying room | 晾晒间',(2.6,8.7,1.42,6.8)),('Rear stair landing | 后梯平台',(8.9,11.8,1.42,6.8))]]
room_c={};furn_c={}
for i,layout in enumerate(layouts):
    for name,bounds in layout:
        rc=coll(f'L{i+1} {name}',rooms[i]);fc=coll(f'L{i+1} {name} | furnishings',furn[i]);room_c[(i,name.split(' |')[0])]=rc;furn_c[(i,name.split(' |')[0])]=fc
        ob=bpy.data.objects.new(PREFIX+name,None);guides.objects.link(ob);ob.location=((bounds[0]+bounds[1])/2,(bounds[2]+bounds[3])/2,Z[i]);ob.empty_display_size=.22;ob['floor']=i+1;ob['room']=name;ob['bounds']=list(bounds);room_records.append({'floor':i+1,'name':name,'bounds':bounds})
# U-shaped stairs: 24 risers at 0.1667m; 0.32m going; 1.45m clear each flight.
def staircase(name,x,y,z,width,run,c):
    n=12;rise=4/24;gap=.18;fw=(width-gap)/2;going=run/n
    for side in [0,1]:
        xx=x-width/2+fw/2 if side==0 else x+width/2-fw/2
        for k in range(n):
            yy=y+(k+.5)*going if side==0 else y+(n-k-.5)*going
            zz=z+(k+1)*rise if side==0 else z+2+(k+1)*rise
            box(name+' tread',(xx,yy,zz-.05),(fw,going+.035,.10),'Walnut',c,.012)
            box(name+' riser',(xx,yy-going/2,zz-rise/2),(fw,.035,rise),'Walnut',c)
        p0=(xx,y,z) if side==0 else (xx,y+run,z+2)
        p1=(xx,y+run,z+2) if side==0 else (xx,y,z+4)
        for dx in [-fw*.4,fw*.4]:beam(name+' stringer',(p0[0]+dx,p0[1],p0[2]-.08),(p1[0]+dx,p1[1],p1[2]-.08),.10,.19,'Walnut',c)
        for dx in [-fw*.47,fw*.47]:
            for k in range(n+1):
                yy=y+k*going;zz=z+k*rise if side==0 else z+4-k*rise
                cyl('Stair spindle',(xx+dx,yy,zz+.50),.022,.95,'Walnut',c,n=10)
            beam('Stair handrail',(p0[0]+dx,p0[1],p0[2]+1.0),(p1[0]+dx,p1[1],p1[2]+1.0),.068,.068,'Walnut',c)
    box(name+' half landing',(x,y+run+.55,z+1.90),(width,1.1,.2),'wood_floor',c)
    for dx in [-width/2,width/2]:
        box('Landing newel',(x+dx,y+run+1.0,z+2.55),(.12,.12,1.1),'Walnut',c,.015)
    beam('Landing rail',(x-width/2,y+run+1.06,z+3),(x+width/2,y+run+1.06,z+3),.07,.07,'Walnut',c)
    for k in range(int(width/.16)):cyl('Landing baluster',(x-width/2+.08+k*.16,y+run+1.05,z+2.50),.02,1,'Walnut',c,n=8)
for i in [0,1]:
    staircase('Grand stair',0,1.60,Z[i],3.40,3.84,struct[i]);staircase('Service stair',10.36,2.9,Z[i],2.35,2.64,struct[i])
# Floor edge safety rails above stair holes, but keep arrival mouths open at south.
for i in [1,2]:
    for x1,x2,y1,y2 in wells:
        for x in [x1,x2]:
            beam('Well edge rail',(x,y1,Z[i]+1),(x,y2,Z[i]+1),.06,.06,'Walnut',struct[i])
            for k in range(int((y2-y1)/.2)):cyl('Well baluster',(x,y1+k*.2,Z[i]+.5),.019,1,'Walnut',struct[i],n=8)
# Additional doorway in guest bedroom B and correct front-room boundaries: remove only own affected walls and rebuild.
for i in [1,2]:
    for ob in list(struct[i].objects):
        if ob.name.startswith('MV_Front corridor'):bpy.data.objects.remove(ob,do_unlink=True)
    wall('Front corridor',(-12,-1),(12,-1),Z[i],3.72 if i==1 else 2.58,.18,'Plaster',struct[i],[(4.4,1.3,0,2.58),(12,2.8,0,2.8),(17,1.25,0,2.58),(21.7,1.25,0,2.58)])
    # move the right entry door to guest A's actual entry
    for ob in list(facade[i].objects):
        if ob.name.startswith(f'MV_L{i+1} front room door') and (ob.location.x>2.5 or (ob.parent and ob.parent.location.x>2.5)):
            if not ob.parent:ob.location.x-=2.2
    door(f'L{i+1} Guest B',9.7,-1,Z[i],1.2,2.54,0,facade[i],92)
# Bathroom/dressing division and two passages in upper north partition.
wall('Bath dressing divider',(-7.2,1.3),(-7.2,4.5),Z[1],3.72,.16,'Plaster',struct[1],[(1.5,1.05,0,2.5)])
# Clear solid west-facing turret threshold by replacing side-wall segment and its window.
for i,z in enumerate(Z[:2]):
    for ob in list(struct[i].objects):
        if ob.name.startswith(f'MV_L{i+1}_East'):bpy.data.objects.remove(ob,do_unlink=True)
    for ob in list(facade[i].objects):
        if ob.name.startswith('MV_Side window') and ob.location.x>11.5 and abs(ob.location.y+4.5)<1.2:bpy.data.objects.remove(ob,do_unlink=True)
    wall(f'L{i+1}_East',(12,-7),(12,7),z,4,.32,'plastered_wall_02',struct[i],[(2.5,1.4,0,2.65),(7,1.5,1.08,3.05),(11.5,1.5,1.08,3.05)])
    # bay threshold bridge joins octagon floor to main building
    box('Turret threshold',(12.15,-4.5,z-.1),(.65,1.42,.2),'wood_floor',struct[i])
# Attic operable skylights/dormers are added on gable faces as real openings by cutting in next stage.
# Scene camera and sun
sunD=bpy.data.lights.new('MV_Afternoon sun','SUN');sunD.energy=2.3;sunD.angle=.12;sunD.color=(1,.91,.76);sun=bpy.data.objects.new('MV_Afternoon sun',sunD);lighting.objects.link(sun);sun.rotation_euler=(math.radians(27),math.radians(-24),math.radians(-32))
camera('01 Exterior',(35,-45, 24),(0,0,6.5),43)
camera('02 Drawing room',(-3.5,-1.85,2.1),(-9,-5,1.9),20)
camera('03 Library',(-3.25,1.95,2.1),(-9.3,5.4,1.8),21)
camera('04 Kitchen',(8.1,1.92,2.1),(3.2,4.1,1.5),20)
camera('05 Bedroom',(-3.2,-1.6,6.15),(-8.5,-4.6,5.8),22)
camera('06 Attic',(-3.4,-1.8,10.05),(-9,-4.5,9.5),21)
scene.camera=cameras['01 Exterior']
for a in bpy.context.screen.areas:
    if a.type=='VIEW_3D':
        a.spaces.active.clip_end=500;a.spaces.active.region_3d.view_distance=48;a.spaces.active.region_3d.view_location=(0,0,5);a.spaces.active.shading.type='MATERIAL'
scene['description']='Original three-storey explorable manor; user photo + Wightwick visual references. Layout is a game-oriented invention, not measured reconstruction.'
scene['walk_levels_m']=Z;scene['player_reference_height_m']=1.8
print('CORE COMPLETE',len(scene.objects),'objects',len(room_records),'rooms')
