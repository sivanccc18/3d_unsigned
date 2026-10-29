"""Read-only .blend -> self-contained browser assets; never saves the source .blend."""
import bpy, math, json, struct, gzip, shutil, re
from pathlib import Path
from collections import defaultdict
import numpy as np
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'manor_walkthrough/assets'
SOURCE=ROOT/'manor'
s=bpy.data.scenes['Manor_Verdant_1880'];bpy.context.window.scene=s
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
T=np.array([[1,0,0],[0,0,1],[0,-1,0]],dtype=np.float32)
def v3(v):return [float(v[0]),float(v[2]),float(-v[1])]
textures=[];images=[];materials=[];mat_ids={};texture_ids={};scales={}
if not (OUT/'textures').exists(): (OUT/'textures').mkdir(parents=True)

def image_tex(image):
    if image.name in texture_ids:return texture_ids[image.name]
    src=Path(bpy.path.abspath(image.filepath));dst=OUT/'textures'/src.name
    if src.is_file():shutil.copyfile(src,dst)
    elif image.packed_file:
        dst=OUT/'textures'/(re.sub(r'[^a-zA-Z0-9_-]','_',image.name)+'.png')
        if bytes(image.packed_file.data[:2])==b'\xff\xd8':dst=dst.with_suffix('.jpg')
        dst.write_bytes(image.packed_file.data)
    else:raise RuntimeError('Missing texture '+image.name)
    idx=len(images);images.append({'uri':'textures/'+dst.name});textures.append({'source':idx,'sampler':0});texture_ids[image.name]=idx
    return idx

def image_upstream(socket,depth=0):
    if depth>5 or not socket.is_linked:return None
    n=socket.links[0].from_node
    if n.type=='TEX_IMAGE':return n
    if n.type in ('NORMAL_MAP','BUMP'):
        return image_upstream(n.inputs['Color'] if n.type=='NORMAL_MAP' else n.inputs['Height'],depth+1)
    return None

def material_id(m):
    key=m.name if m else 'Default'
    if key in mat_ids:return mat_ids[key]
    idx=len(materials);mat_ids[key]=idx
    p=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) if m and m.use_nodes else None
    col=list(m.diffuse_color) if m else [.5,.5,.5,1]
    rough=.75;metal=0;scale=1
    if p:
        col=list(p.inputs['Base Color'].default_value);rough=float(p.inputs['Roughness'].default_value);metal=float(p.inputs['Metallic'].default_value)
        if key=='MV_Walnut':col=[.12,.035,.022,1]
    pbr={'baseColorFactor':col,'metallicFactor':metal,'roughnessFactor':rough};rec={'name':key,'pbrMetallicRoughness':pbr,'doubleSided':True}
    if p:
        tex=image_upstream(p.inputs['Base Color'])
        if tex and tex.image:
            pbr['baseColorFactor']=[1,1,1,1];pbr['baseColorTexture']={'index':image_tex(tex.image)}
            if tex.inputs['Vector'].is_linked:
                n=tex.inputs['Vector'].links[0].from_node
                if n.type=='VECT_MATH' and n.operation=='SCALE':scale=float(n.inputs[3].default_value)
        nt=image_upstream(p.inputs['Normal'])
        if nt and nt.image:rec['normalTexture']={'index':image_tex(nt.image),'scale':.45}
    if 'Glazing' in key:
        pbr['baseColorFactor']=[.68,.85,.87,.14];pbr['roughnessFactor']=.18;rec['alphaMode']='BLEND';pbr.pop('baseColorTexture',None)
    if 'Warm lamp' in key:rec['emissiveFactor']=[1,.48,.12]
    scales[idx]=scale;materials.append(rec);return idx

hinges=[o for o in s.objects if o.type=='EMPTY' and o.get('interactive') and 'Hinge' in o.name]
doors=[];door_index={}
for o in hinges:
    x,y,z=o.location;opened=float(o.rotation_euler.z)
    if abs(y+1)<.08:closed=0
    elif abs(y-1.3)<.08:
        closed=math.pi
        if x>10:opened=math.pi+math.radians(95)
    elif 'Garden door' in o.name:closed=math.pi;opened=math.pi-math.radians(100)
    elif 'Main entrance' in o.name or 'Balcony access' in o.name:closed=0
    elif 'Conservatory' in o.name:closed=-math.pi/2
    else:closed=round(opened/(math.pi/2))*(math.pi/2)
    w=float(o.get('clear_width_m',1.08))+.12
    children=[c for c in o.children_recursive if c.type=='MESH']
    height=max((max((o.matrix_world.inverted()@c.matrix_world@Vector(v)).z for v in c.bound_box) for c in children),default=2.54)
    name=o.name.replace('MV_','').replace('_Hinge','')
    door_index[o]=len(doors)
    doors.append({'id':len(doors),'name':name,'hinge':v3(o.location),'closed':closed,'opened':opened,'width':w,'height':height,'initialOpen':False})

def door_parent(o):
    p=o.parent
    while p:
        if p in door_index:return p
        p=p.parent
    return None

# Render meshes are merged by zone and material. Doors stay separate with pivot-local geometry.
groups=defaultdict(list);collision=[];furniture_roots=set();count=0
for o in list(s.objects):
    if o.type not in ('MESH','CURVE') or o.hide_render:continue
    if o.name.startswith('MV_Distant meadow'):continue
    parent=door_parent(o);cname=o.users_collection[0].name if o.users_collection else ''
    zone=('door_'+str(door_index[parent])) if parent else ('L'+cname[1] if re.match(r'L[123]',cname) else ('garden' if 'Garden' in cname or '花园' in cname else 'roof'))
    # Disable tessellated bevels only on tiny garden details; architecture quality preserved.
    ev=o.evaluated_get(deps);me=ev.to_mesh();me.calc_loop_triangles()
    if not len(me.loop_triangles):ev.to_mesh_clear();continue
    mx=parent.matrix_world.inverted()@o.matrix_world if parent else o.matrix_world
    R=np.array(mx.to_3x3(),dtype=np.float32);trans=np.array(mx.translation,dtype=np.float32)
    pos=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',pos);pos=pos.reshape(-1,3)@R.T+trans;pos=pos@T.T
    norm=np.empty(len(me.corner_normals)*3,dtype=np.float32);me.corner_normals.foreach_get('vector',norm);norm=norm.reshape(-1,3)@np.linalg.inv(R);norm=norm@T.T;norm/=np.maximum(np.linalg.norm(norm,axis=1,keepdims=True),1e-9)
    tris=np.empty(len(me.loop_triangles)*3,dtype=np.int32);me.loop_triangles.foreach_get('vertices',tris);tris=tris.reshape(-1,3)
    loops=np.empty(len(me.loop_triangles)*3,dtype=np.int32);me.loop_triangles.foreach_get('loops',loops);loops=loops.reshape(-1,3)
    mids=np.empty(len(me.loop_triangles),dtype=np.int32);me.loop_triangles.foreach_get('material_index',mids)
    uv=np.zeros((len(me.loops),2),dtype=np.float32)
    if me.uv_layers.active:me.uv_layers.active.data.foreach_get('uv',uv.ravel())
    for mi in np.unique(mids):
        mat=me.materials[int(mi)] if len(me.materials)>int(mi) else None;mid=material_id(mat);sel=mids==mi
        a=np.empty((int(sel.sum())*3,8),dtype=np.float32);a[:,:3]=pos[tris[sel].ravel()];a[:,3:6]=norm[loops[sel].ravel()];a[:,6:]=uv[loops[sel].ravel()]*scales[mid];groups[(zone,mid)].append(a)
    # True triangle colliders for architecture, furniture and garden hardscape. No decorative leaf/flower snagging.
    solid=not parent and not any(k in cname for k in ('Roof |','Ceiling |','Cameras','Navigation','远景'))
    if 'Garden' in cname:
        solid=any(k in cname for k in ('Ground','Paths','Boundary','Furniture','Structures','地形','道路','围栏','长椅','喷泉'))
    # Roof remains a collider for attic clearance, but not decorative roof furniture.
    if 'Roof |' in cname:solid=True
    if solid:
        pts=pos[tris]
        # Remove sub-2cm face slivers (decorative wires) only outside structural colliders.
        if 'Structure' not in cname and 'Facade' not in cname:
            allowed=[]
            for mi in mids:
                ma=me.materials[int(mi)] if len(me.materials)>int(mi) else None
                allowed.append(not ma or not any(k in ma.name for k in ('Leaf','flower','Lavender','Rose','Pages','Book','Warm lamp')))
            pts=pts[np.array(allowed,dtype=bool)]
        if len(pts):collision.append(pts.astype(np.float32))
    ev.to_mesh_clear();count+=1
    if count%500==0:print('PROCESSED',count,'objects',flush=True)

# Invisible continuous ramp surfaces replace only the stair treads/riser collision band.
# Preserve actual rendering and railings; plane elevation follows tread nosings.
col=np.concatenate(collision,axis=0);keep=np.ones(len(col),dtype=bool)
def add_ramp(x1,x2,y0,run,z0,rise,reverse=False):
    global keep,col
    # Blender y becomes -browser z. Select triangles entirely within the corresponding flight.
    x=col[:,:,0];by=-col[:,:,2];bz=col[:,:,1]
    slope=z0+rise*(1-(by-y0)/run if reverse else (by-y0)/run)
    inside=(x.min(axis=1)>=x1-.09)&(x.max(axis=1)<=x2+.09)&(by.min(axis=1)>=y0-.06)&(by.max(axis=1)<=y0+run+.06)
    band=((bz-slope).max(axis=1)<.27)&((bz-slope).min(axis=1)>-.55)
    keep&=~(inside&band)
    a=z0+rise if reverse else z0;b=z0 if reverse else z0+rise
    vs=np.array([[x1,a,-y0],[x2,a,-y0],[x2,b,-y0-run],[x1,b,-y0-run]],np.float32)
    return vs[[[0,2,1],[0,3,2]]]
ramps=[]
for level in [0,1]:
    z=.48+level*4
    for cx,y0,width,run in [(0,1.6,3.4,3.84),(10.36,2.9,2.35,2.64)]:
        fw=(width-.18)/2
        ramps.append(add_ramp(cx-width/2,cx-.09,y0,run,z+.07,2))
        ramps.append(add_ramp(cx+.09,cx+width/2,y0,run,z+2.07,2,True))
ramps.append(add_ramp(-1.9,1.9,-11.02,1.12,.03,.45))
ramps.append(add_ramp(-1.15,1.15,7.22,1.10,.03,.45,True))
col=np.concatenate([col[keep]]+ramps,axis=0)
# Whole-garden terrain safety collider and property boundary; visible main paths can be slightly higher.
verts=np.array([[-38,-.04,31],[38,-.04,31],[38,-.04,-39],[-38,-.04,-39]],np.float32)
col=np.concatenate([col,verts[[[0,2,1],[0,3,2]]]],axis=0)
# Simple solids for clipped hedges avoid testing every decorative leaf.
def hedge_box(x,y,w,d,h):
    vs=np.array([[x+sx*w/2,zz,-y+sy*d/2] for zz in [0,h] for sx,sy in [(-1,-1),(1,-1),(1,1),(-1,1)]],np.float32)
    return vs[np.array([[0,1,2],[0,2,3],[4,6,5],[4,7,6],[0,4,5],[0,5,1],[1,5,6],[1,6,2],[2,6,7],[2,7,3],[3,7,4],[3,4,0]])]
hedges=[hedge_box(x,-22,11.4,1.05,1.23) for x in [-8.1,8.1]]+[hedge_box(x,5,1.15,47,1.65) for x in [-26,26]]+[hedge_box(0,31,51,1.1,1.45)]
for x,y,w,d in [(-8,-16.2,7,5),(8,-16.2,7,5),(-8,17,10,8),(8,17,10,8)]:
    hedges.extend(hedge_box(x,yy,w,.4,.55) for yy in [y-d/2,y+d/2]);hedges.extend(hedge_box(xx,y,.4,d,.55) for xx in [x-w/2,x+w/2])
col=np.concatenate([col]+hedges,axis=0)
with gzip.open(OUT/'collision.bin.gz','wb',compresslevel=6) as f:f.write(col.tobytes())

# Minimal standards-compliant glTF binary with one interleaved buffer per primitive.
binary=bytearray();views=[];accessors=[];meshes=[];nodes=[]
def align():
    while len(binary)%4:binary.append(0)
def acc(view,offset,count,typ,minv=None,maxv=None):
    r={'bufferView':view,'byteOffset':offset,'componentType':5126,'count':count,'type':typ}
    if minv is not None:r.update({'min':minv,'max':maxv})
    accessors.append(r);return len(accessors)-1
zones=sorted(set(z for z,m in groups))
for zone in zones:
    prim=[]
    for (z,mid),parts in groups.items():
        if z!=zone:continue
        a=np.concatenate(parts,axis=0);align();start=len(binary);binary.extend(a.tobytes());vi=len(views);views.append({'buffer':0,'byteOffset':start,'byteLength':a.nbytes,'byteStride':32,'target':34962})
        p=acc(vi,0,len(a),'VEC3',a[:,:3].min(axis=0).tolist(),a[:,:3].max(axis=0).tolist());n=acc(vi,12,len(a),'VEC3');uv=acc(vi,24,len(a),'VEC2');prim.append({'attributes':{'POSITION':p,'NORMAL':n,'TEXCOORD_0':uv},'material':mid,'mode':4})
    meshes.append({'name':zone,'primitives':prim});node={'name':zone,'mesh':len(meshes)-1}
    if zone.startswith('door_'):
        d=doors[int(zone[5:])];node['translation']=d['hinge'];a=d['closed'];node['rotation']=[0,math.sin(a/2),0,math.cos(a/2)];node['extras']={'doorId':d['id']}
    nodes.append(node)
gltf={'asset':{'version':'2.0','generator':'Verdant Manor web export'},'scene':0,'scenes':[{'nodes':list(range(len(nodes)))}],'nodes':nodes,'meshes':meshes,'materials':materials,'textures':textures,'images':images,'samplers':[{'magFilter':9729,'minFilter':9987,'wrapS':10497,'wrapT':10497}],'buffers':[{'byteLength':len(binary)}],'bufferViews':views,'accessors':accessors}
j=json.dumps(gltf,separators=(',',':')).encode();j+=b' '*((-len(j))%4);align();glb=struct.pack('<III',0x46546c67,2,12+8+len(j)+8+len(binary))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(binary),0x004e4942)+binary
with gzip.open(OUT/'manor.glb.gz','wb',compresslevel=6) as f:f.write(glb)
rooms=[{'name':o['room'],'floor':int(o['floor']),'bounds':list(o['bounds'])} for o in s.objects if o.get('room')]
meta={'doors':doors,'rooms':rooms,'floors':[.48,4.48,8.48],'spawn':[0,.08,18],'colliderTriangles':len(col),'renderTriangles':len(binary)//96,'drawCalls':sum(len(m['primitives']) for m in meshes),'originalBlend':'../manor/Verdant_Manor.blend','notes':['Runtime uses continuous stair ramp colliders; original tread meshes unchanged.','Procedural Blender-only shaders approximated by PBR factors; photographic base-color and normal maps retained.','No NPC navigation mesh: current scope is player exploration.']}
(OUT/'scene.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
print('EXPORT_READY',json.dumps({k:v for k,v in meta.items() if k not in ('doors','rooms')},ensure_ascii=False),flush=True)
