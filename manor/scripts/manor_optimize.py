# Collapse static component meshes by collection and existing assembly parent.
# Hinged doors/gates remain separate. All room/floor collection boundaries remain intact.
from collections import defaultdict
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
groups=defaultdict(list)
for ob in list(scene.objects):
    if ob.type!='MESH':continue
    par=ob.parent
    if par and par.get('interactive'):continue
    if len(ob.data.polygons)>40000:continue
    groups[(ob.users_collection[0],par)].append(ob)
count_before=len(scene.objects);total_merged=0
for (c,par),obs in groups.items():
    if len(obs)<4:continue
    verts=[];faces=[];uvs=[];poly_mats=[];smooth=[];materials=[];mat_lookup={}
    inv=par.matrix_world.inverted() if par else None
    for ob in obs:
        ev=ob.evaluated_get(deps);me=ev.to_mesh();mx=(inv@ob.matrix_world) if inv is not None else ob.matrix_world
        offset=len(verts);verts.extend(tuple(mx@v.co) for v in me.vertices)
        matmap={}
        for idx,ma in enumerate(me.materials):
            if ma not in mat_lookup:mat_lookup[ma]=len(materials);materials.append(ma)
            matmap[idx]=mat_lookup[ma]
        uv=me.uv_layers.active
        for p in me.polygons:
            faces.append(tuple(offset+i for i in p.vertices));poly_mats.append(matmap.get(p.material_index,0));smooth.append(p.use_smooth)
            for li in p.loop_indices:uvs.append(tuple(uv.data[li].uv) if uv else (0.,0.))
        ev.to_mesh_clear()
    name=(par.name if par else c.name)+' | mesh'
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
    for ma in materials:
        if ma:me.materials.append(ma)
    layer=me.uv_layers.new(name='UVMap');flat=[v for uv in uvs for v in uv];layer.data.foreach_set('uv',flat)
    me.polygons.foreach_set('material_index',poly_mats);me.polygons.foreach_set('use_smooth',smooth)
    new=bpy.data.objects.new(name,me);c.objects.link(new)
    if par:new.parent=par
    for ob in obs:bpy.data.objects.remove(ob,do_unlink=True)
    total_merged+=len(obs)
# Keep sculpted mouldings smooth where surfaces actually meet; no automatic smoothing of architecture.
scene['optimization']='Static mesh components consolidated per room/assembly; door hinge pivots retained; not an engine collision or LOD build.'
print('OPTIMIZED objects',count_before,'->',len(scene.objects),'components merged',total_merged)
# Store human-readable room index and reference provenance inside the .blend.
text=bpy.data.texts.new('START HERE | 庄园场景说明')
text.write('VERDANT MANOR | 原创三层英国庄园\n\n楼层：一层0.48m，二层4.48m，阁楼8.48m。米制。\n在 Outliner 隐藏 04 Roof 可查看阁楼；隐藏二、三层与天花可查看一层。\n相机：01外观、02会客厅、03书房、04厨房、05卧室、06阁楼、07入口、08后花园。\n门的 Hinge 空物体保留旋转轴，可旋转局部Z开合。\n原始默认场景 Scene 保留，当前工程另存，不覆盖用户已有文件。\n\n参考：用户照片（立面风格）+ Wightwick Manor外观、室内照片（仅视觉研究，未用作贴图）。\nhttps://victorianweb.org/art/architecture/ould/2.html\n照片作者 Laurent Bury / Philip Pankhurst；照片仅作参考，不包括在发布用素材包中。\n实拍PBR材质：Poly Haven，CC0，来源记于 textures/sources.json。墙纸、地毯、装饰画为本项目原创图案。\n\n这是可进入的建模场景，不是已经运行的游戏。碰撞体、NavMesh、门交互逻辑、引擎光照烘焙及材质转换尚需按目标游戏引擎配置。\nservice楼梯踏步0.22m，为紧凑后梯；楼梯射线净高和主要通路检查通过，不代表完整物理胶囊体测试。\n')
text.write('\n房间清单\n'+json.dumps(room_records,ensure_ascii=False,indent=2))
# Pack image assets so the delivered .blend is self-contained.
bpy.ops.file.pack_all()
scene.camera=cameras['01 Exterior'];scene.render.resolution_x=1600;scene.render.resolution_y=1100
for screen in bpy.data.screens:
    for a in screen.areas:
        if a.type=='VIEW_3D':
            a.spaces.active.shading.type='SOLID';a.spaces.active.shading.color_type='MATERIAL';a.spaces.active.clip_end=500
            a.spaces.active.region_3d.view_perspective='CAMERA'
            try:a.spaces.active.overlay.show_overlays=False
            except:pass
scene['reference_sources']='https://victorianweb.org/art/architecture/ould/2.html ; https://polyhaven.com'
summary={'rooms':len(room_records),'objects':len(scene.objects),'mesh_objects':sum(o.type=='MESH' for o in scene.objects),'mesh_polygons':sum(len(o.data.polygons) for o in scene.objects if o.type=='MESH'),'cameras':list(cameras),'textures_packed':sum(bool(im.packed_file) for im in bpy.data.images),'floor_levels_m':Z}
(BASE/'model_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Verdant_Manor.blend'))
print(json.dumps(summary,ensure_ascii=False))
