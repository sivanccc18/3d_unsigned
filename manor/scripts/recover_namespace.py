import bpy, math, random, json, os, bmesh, ast
from mathutils import Vector
from pathlib import Path
BASE=Path(bpy.data.filepath).resolve().parent if bpy.data.filepath else Path(__file__).resolve().parents[1];PREFIX='MV_'
scene=bpy.data.scenes['Manor_Verdant_1880'];bpy.context.window.scene=scene
ROOT=bpy.data.collections['MANOR | 庄园总集']
C={c.name:c for c in bpy.data.collections};M={m.name[3:]:m for m in bpy.data.materials if m.name.startswith('MV_')}
levels=[C['01 Ground | 一层'],C['02 Upper | 二层'],C['03 Attic | 三层阁楼']]
roofs=C['04 Roof | 屋顶·可整体隐藏'];gardens=C['05 Garden | 花园'];lighting=C['06 Cameras & Lights | 相机与灯光'];guides=C['07 Navigation | 导航标记']
struct=[C[f'L{i+1} Structure | 墙体楼板与楼梯'] for i in range(3)];facade=[C[f'L{i+1} Facade | 外墙木构与门窗'] for i in range(3)];furn=[C[f'L{i+1} Furniture | 家具'] for i in range(3)];rooms=[C[f'L{i+1} Rooms | 各房间饰面'] for i in range(3)];ceilings=[C[f'L{i+1} Ceiling | 天花·可隐藏'] for i in range(3)]
Z=[.48,4.48,8.48];room_c={};furn_c={};room_records=[];cameras={};openings=[]
for path in ['manor_core.py','manor_interiors.py']:
    tree=ast.parse((BASE/'scripts'/path).read_text());nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)]
    if path=='manor_core.py':nodes += [n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='layouts' for t in n.targets)]
    exec(compile(ast.Module(body=nodes,type_ignores=[]),path,'exec'),globals())
for i,layout in enumerate(layouts):
    for name,bounds in layout:
        key=name.split(' |')[0];room_c[(i,key)]=C[f'L{i+1} {name}'];furn_c[(i,key)]=C[f'L{i+1} {name} | furnishings'];room_records.append({'floor':i+1,'name':name,'bounds':bounds})
for ob in scene.objects:
    if ob.type=='CAMERA':cameras[ob.name[3:]]=ob
print('Restored namespace:',len(scene.objects),'objects')
