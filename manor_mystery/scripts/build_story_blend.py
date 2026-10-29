import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1]
a=json.loads((P/'assets/anchors.json').read_text())
s=bpy.data.scenes['Manor_Verdant_1880'];bpy.context.window.scene=s
existing=set(s.objects)
def signature(objects):
    return sorted((o.name,tuple(round(v,7) for row in o.matrix_world for v in row),len(o.data.vertices) if o.type=='MESH' else 0) for o in objects)
before=signature(existing)
root=bpy.data.collections.new('MYSTERY | 新增搜证内容');s.collection.children.link(root)
chars=bpy.data.collections.new('Mystery Characters | 三位辩论人物');root.children.link(chars)
clues=bpy.data.collections.new('Mystery Evidence | 三件核心物证');root.children.link(clues)
markers=bpy.data.collections.new('Mystery Anchors | 夜间位置与调查点');root.children.link(markers)
def world(p): return Vector((p[0],-p[2],p[1]))
def imported(name,c,position,height=None,width=None):
    old=set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(P/'assets/story'/f'{name}.glb'))
    obs=set(bpy.data.objects)-old
    holder=bpy.data.objects.new('Mystery_'+name,None);c.objects.link(holder)
    for ob in obs:
        for co in list(ob.users_collection):co.objects.unlink(ob)
        c.objects.link(ob)
        if ob.parent is None:ob.parent=holder
    bpy.context.view_layer.update()
    pts=[ob.matrix_world@Vector(corner) for ob in obs if ob.type=='MESH' for corner in ob.bound_box]
    lo=Vector(tuple(min(p[i] for p in pts) for i in range(3)));hi=Vector(tuple(max(p[i] for p in pts) for i in range(3)))
    scale=height/(hi.z-lo.z) if height else width/max(hi.x-lo.x,hi.y-lo.y)
    for ob in obs:
        if ob.parent==holder:ob.location-=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
    holder.scale=(scale,scale,scale);holder.location=world(position)
    holder['source_asset']='MagicLomix/art/models/'+name+'.glb'
    return holder
for name,n in a['npcs'].items():
    h=imported(name,chars,n['day'],height=n['height'])
    dx=a['debateCamera'][0]-n['day'][0];dz=a['debateCamera'][2]-n['day'][2]
    h.rotation_euler.z=math.atan2(dx,dz)
    marker=bpy.data.objects.new('Night_'+name,None);markers.objects.link(marker);marker.location=world(n['night']);marker.empty_display_type='CIRCLE';marker.empty_display_size=.35;marker['room']=n['room']
for name,n in a['evidence'].items():
    if 'model' in n:imported(name,clues,n['position'],height=n.get('height'),width=n.get('width'))
    else:
        marker=bpy.data.objects.new('Investigation_'+name,None);markers.objects.link(marker);marker.location=world(n['position']);marker.empty_display_type='CUBE';marker.empty_display_size=.15
assert signature(existing)==before,'Original manor transforms changed'
for im in bpy.data.images:
    if im.source=='FILE' and not im.packed_file:
        try:im.pack()
        except Exception:pass
s['mystery_note']='Independent layout copy. Original manor unchanged. Runtime gameplay lives in browser. Day debate / night investigation-social.'
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Verdant_Manor_Mystery.blend'))
if not (P/'tests').exists(): (P/'tests').mkdir(parents=True)
(P/'tests/blend-validation.json').write_text(json.dumps({'original_objects':len(existing),'original_objects_unchanged':signature(existing)==before,'added_objects':len(set(s.objects)-existing),'blend':str(P/'Verdant_Manor_Mystery.blend')},ensure_ascii=False,indent=2))
print('MYSTERY_BLEND_SAVED',len(existing),len(s.objects))
