# Resolve decorative obstructions and validate game-scale routes before optimization.
from mathutils import Vector
# Doors swing into rooms rather than narrowing the central gallery.
for ob in scene.objects:
    if ob.type=='EMPTY' and ob.get('interactive')=='Rotate local Z to open or close':
        if abs(ob.location.y+1)<.05:ob.rotation_euler.z=math.radians(-95)
        elif abs(ob.location.y-1.3)<.05:ob.rotation_euler.z=math.pi-math.radians(95)
# Clear the now-replaced west/east window leadwork from passageways.
for ob in list(scene.objects):
    if ob.name.startswith('MV_Lead diamond'):
        x,y,z=ob.location
        if ((abs(x-12.068)<.17 and abs(y+4.5)<.86) or (abs(x+12.068)<.17 and abs(y)<.86)) and z<7.7:
            bpy.data.objects.remove(ob,do_unlink=True)
# Remove wainscoting spanning turret access (east wall of dining/guest room).
for i,key in [(0,'Dining room'),(1,'Guest bedroom B')]:
    c=room_c[(i,key)]
    for ob in list(c.objects):
        if abs(ob.location.x-11.8)<.1 and ob.name.startswith(('MV_Wainscot panel','MV_Dado moulding','MV_Oak skirting')):
            if ob.name.startswith('MV_Wainscot panel'):
                if -5.42<ob.location.y<-3.58:bpy.data.objects.remove(ob,do_unlink=True)
            else:
                name=ob.name;z=ob.location.z;sz=ob.dimensions.z;bpy.data.objects.remove(ob,do_unlink=True)
                for ya,yb in [(-6.8,-5.25),(-3.75,-1.12)]:box('Turret clear moulding',(11.8,(ya+yb)/2,z),(.055,yb-ya,sz),'Walnut',c,.005)
# Clear decorative lower lines which cross attic windows at sill elevation.
for ob in list(facade[2].objects):
    if ob.name.startswith('MV_Attic timber course') and ob.location.z>10.58:
        x,y,z=ob.location;bpy.data.objects.remove(ob,do_unlink=True)
        for xa,xb in [(x-3.975,x-.80),(x+.80,x+3.975)]:box('Attic window clear course',((xa+xb)/2,y,z),(xb-xa,.12,.14),'Burgundy timber',facade[2])
# Back stair/door link: door opens north into service stair bay, unobstructed landing y=1.42..2.75.
# Fill narrow bridge at front of upper main stair mouth between corridor and opening.
for i in [1,2]:
    box('Upper arrival sill',(0,1.45,Z[i]-.07),(3.40,.24,.14),'wood_floor',struct[i])
# Add wardrobe inner shelves and visible handles are already separate objects.
# Room lighting trim: retain the intended day-lit palette.
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.cycles.max_bounces=6;scene.cycles.diffuse_bounces=3;scene.cycles.transmission_bounces=5
scene.render.resolution_x=1600;scene.render.resolution_y=1100
# Validate specified straight spans at player chest level and overhead near staircase.
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
def probe(name,a,b):
    a=Vector(a);delta=Vector(b)-a;hit,loc,normal,idx,ob,matrix=scene.ray_cast(deps,a,delta.normalized(),distance=delta.length)
    return {'name':name,'from':list(a),'to':list(b),'clear':not hit,'blocker':ob.name if hit else None,'at':list(loc) if hit else None}
tests=[]
for i,z in enumerate(Z):
    tests.append(probe('L'+str(i+1)+' central corridor',(-11,.18,z+1.3),(11,.18,z+1.3)))
    tests.append(probe('L'+str(i+1)+' front left doorway',(-7.6,.25,z+1.4),(-7.6,-1.75,z+1.4)))
    tests.append(probe('L'+str(i+1)+' rear doorway',(-7.6,.25,z+1.4),(-7.6,2.0,z+1.4)))
for name,a,b in [('Main front entry',(0,-8.1,1.9),(0,-6.4,1.9)),('Conservatory entry',(-11,0,1.9),(-13,0,1.9)),('Turret dining entry',(11,-4.5,1.9),(13,-4.5,1.9)),('Garden exit',(0,6.2,1.9),(0,8.3,1.9))]:tests.append(probe(name,a,b))
# Main staircase head-clearance ray from each tread centre to head height.
for i in [0,1]:
    for side in [0,1]:
        for k in [1,5,9,11]:
            x=-.895 if side==0 else .895;y=1.60+(k+.5)*.32 if side==0 else 1.60+(12-k-.5)*.32;z=Z[i]+(k+1)/6 if side==0 else Z[i]+2+(k+1)/6
            tests.append(probe(f'L{i+1} stair {side} tread {k}',(x,y,z+.12),(x,y,z+2.12)))
result={'room_count':len(room_records),'floor_levels_m':Z,'main_stair_riser_m':4/24,'main_stair_tread_m':.32,'main_stair_flight_width_m':1.61,'service_stair_riser_m':4/24,'service_stair_tread_m':.22,'attic_min_roof_clearance_m':2.37,'tests':tests}
(BASE/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps({'probe_count':len(tests),'blocked':[t for t in tests if not t['clear']]},ensure_ascii=False,indent=2))
