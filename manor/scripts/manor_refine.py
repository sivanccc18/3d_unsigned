# Headroom, attic daylight and architectural finishing.
# Lift roof valleys 1.05m without adding a fourth occupied storey.
for ob in list(roofs.objects):ob.location.z+=1.05
for ob in list(struct[2].objects):
    if ob.name.startswith('MV_Attic_Gable'):ob.location.z+=1.05
    elif ob.name.startswith('MV_Attic knee'):
        for v in ob.data.vertices:
            if v.co.z>0:v.co.z+=1.05
for ob in list(facade[2].objects):
    if ob.name.startswith(('MV_Gable','MV_Finial')):ob.location.z+=1.05
# Attic lower walls complete the full width. Knee wall interior height now 2.60m.
for xx in [-12,12]:wall('Attic end wall',(xx,-7),(xx,7),Z[2],2.60,.26,'Plaster',struct[2])
# New small dormer-like windows on the front and rear gables; cut both knee and triangle.
# Draw rectangular opening spanning the knee wall and gable, so light truly reaches the attic.
for cx in [-8,0,8]:
    for yy in [-7,7]:
        cutter=box('TEMP_Attic_Window_Cut',(cx,yy,11.48),(1.48,.85,1.78),None,struct[2])
        targets=[o for o in list(struct[2].objects) if (o.name.startswith('MV_Attic_Gable') or o.name.startswith('MV_Attic knee'))]
        for ob in targets:
            # evaluate solidify then difference, only physically intersecting target meshes
            bpy.context.view_layer.objects.active=ob
            for md in list(ob.modifiers):
                if md.type=='SOLIDIFY':bpy.ops.object.modifier_apply(modifier=md.name)
            md=ob.modifiers.new('Real window opening','BOOLEAN');md.operation='DIFFERENCE';md.solver='EXACT';md.object=cutter
            bpy.ops.object.modifier_apply(modifier=md.name)
        bpy.data.objects.remove(cutter,do_unlink=True)
        window('Attic leaded window',cx,yy,10.59,1.42,1.72,0 if yy<0 else math.pi,facade[2])
# Gable centre timbers are cut around window instead of obscuring it.
for ob in list(facade[2].objects):
    if ob.name.startswith('MV_Gable kingpost'):bpy.data.objects.remove(ob,do_unlink=True)
for cx in [-8,0,8]:
    beam('Gable kingpost upper',(cx,-7.2,12.43),(cx,-7.2,15.68),.16,.10,'Burgundy timber',facade[2])
    for yy in [-7.18,7.18]:
        for zz in [8.70,10.15,11.09]:box('Attic timber course',(cx,yy,zz),(7.95,.12,.14),'Burgundy timber',facade[2],.009)
        for dx in [-3.9,-2.7,-1.7,1.7,2.7,3.9]:box('Attic lower upright',(cx+dx,yy,9.79),(.13,.12,2.6),'Burgundy timber',facade[2])
    # Fan-shaped struts above high window, as in Tudor revival carvings.
    for dx in [-1.7,-1.0,1.0,1.7]:beam('Gable fan',(cx,-7.22,12.62),(cx+dx,-7.22,13.5-abs(dx)*.2),.075,.07,'Burgundy timber',facade[2])
# Sparse exposed attic rafters on matching roof slopes.
for cx in [-8,0,8]:
    for yy in [-5.8,-3.2,0,3.2,5.8]:
        for s in [-1,1]:beam('Exposed roof rafter',(cx+s*4.0,yy,11.02),(cx,yy,15.72),.13,.15,'Walnut',struct[2])
        beam('Attic tie beam',(cx-3.2,yy,12.14),(cx+3.2,yy,12.14),.13,.16,'Walnut',struct[2])
# Additional one-storey west conservatory gives the estate an asymmetric silhouette.
cons=coll('L1 Conservatory | 侧翼玻璃暖房',levels[0])
box('Conservatory plinth',(-15.3,2.8,.28),(6.3,7.0,.44),'Limestone',cons,.03)
box('Conservatory floor',(-15.3,2.8,.47),(6.1,6.8,.05),'Limestone',cons)
for xx in [-18.3,-12.2]:
    for yy in [-.5,6.1]:box('Conservatory corner',(xx,yy,2.25),(.13,.13,3.5),'Burgundy timber',cons,.01)
for yy in [-.55,6.15]:
    for k in range(9):
        xx=-18.25+k*.75;box('Glazed bay upright',(xx,yy,2.22),(.06,.1,3.45),'Burgundy timber',cons)
    for zz in [.65,1.15,3.95]:box('Conservatory rail',(-15.25,yy,zz),(6.2,.09,.09),'Burgundy timber',cons)
    box('Conservatory glass',(-15.25,yy,2.3),(6.0,.025,3.1),'Glazing',cons)
for k in range(9):
    yy=-.5+k*.82;box('Garden room upright',(-18.3,yy,2.25),(.10,.06,3.5),'Burgundy timber',cons)
box('Garden room glass',(-18.3,2.8,2.3),(.025,6.5,3.1),'Glazing',cons)
for side in [-1,1]:
    ob=mesh('Conservatory roof', [(-15.25+side*3.25,-.75,4),(-15.25+side*3.25,6.35,4),(-15.25,6.35,5.8),(-15.25,-.75,5.8)],[(0,1,2,3)],'Glazing',cons)
    mod=ob.modifiers.new('Glazing thickness','SOLIDIFY');mod.thickness=.025
    for yy in [-.75+i*.71 for i in range(11)]:beam('Roof glazing bar',(-15.25+side*3.25,yy,4),(-15.25,yy,5.8),.05,.07,'Burgundy timber',cons)
beam('Conservatory ridge',(-15.25,-.8,5.8),(-15.25,6.4,5.8),.09,.09,'Burgundy timber',cons)
# Connect conservatory through west wall, replace centre window with real doorway.
for ob in list(struct[0].objects):
    if ob.name.startswith('MV_L1_West'):bpy.data.objects.remove(ob,do_unlink=True)
for ob in list(facade[0].objects):
    if ob.name.startswith('MV_Side window') and ob.location.x< -11.5 and abs(ob.location.y)<1.2:bpy.data.objects.remove(ob,do_unlink=True)
wall('L1_West',(-12,-7),(-12,7),Z[0],4,.32,'plastered_wall_02',struct[0],[(2.5,1.5,1.08,3.05),(7,1.5,0,2.65),(11.5,1.5,1.08,3.05)])
box('Conservatory threshold',(-12.12,0,.37),(.55,1.52,.22),'Limestone',cons)
door('Conservatory door',-12,0,Z[0],1.45,2.6,-math.pi/2,cons,95)
table(-15.4,2.7,Z[0],cons,1.5,.8,.7);chair(-15.4,3.6,Z[0],cons);chair(-15.4,1.9,Z[0],cons,math.pi)
for x,y in [(-17.6,.3),(-17.6,5.3),(-13.0,5.3)]:
    cyl('Conservatory pot',(x,y,.73),.32,.5,'Burgundy timber',cons,n=24,r2=.40)
    for k in range(7):
        a=k*math.tau/7;curve('Indoor palm',[(x,y,1),(x+.3*math.cos(a),y+.3*math.sin(a),1.9),(x+.65*math.cos(a),y+.65*math.sin(a),1.75)],.018,'Leaf dark',cons)
        sphere('Palm leaf',(x+.4*math.cos(a),y+.4*math.sin(a),1.77),(.13,.32,.035),'Leaf',cons)
# Substantial front bay window surrounds (do not add a sealed facade behind glazing).
for i,z in enumerate(Z[:2]):
    for xx in [-7,7]:
        # Stacked shallow oriel, supporting moulding and decorative canopy.
        box('Bay cornice',(xx,-7.30,z+3.27),(2.20,.60,.15),'Burgundy timber',facade[i],.025)
        for dx in [-.98,.98]:box('Bay pillar',(xx+dx,-7.29,z+2.05),(.15,.45,2.30),'Burgundy timber',facade[i],.018)
        box('Bay base',(xx,-7.27,z+.83),(2.22,.64,.20),'Limestone',facade[i],.024)
        for dx in [-.78,.78]:beam('Bay corbel',(xx+dx,-7.15,z+.39),(xx+dx,-7.46,z+.80),.12,.14,'Burgundy timber',facade[i])
# Gutters and downpipes.
for xx in [-12.36,-4,4,12.36]:
    beam('Lead valley gutter',(xx,-7.5,10.9),(xx,7.5,10.9),.09,.10,'Iron',roofs)
for xx in [-11.82,11.82]:
    for yy in [-7.3,7.3]:
        cyl('Rain downpipe',(xx,yy,5.6),.06,10.1,'Iron',facade[0],n=12)
        for zz in [1.2,3.6,5.8,8.2,10]:box('Pipe clamp',(xx,yy,zz),(.19,.10,.05),'Iron',facade[0])
# Remove timber bars across passageways (outside ground-level stringcourses).
for i in [0,1]:
    z=Z[i]
    for ob in list(facade[i].objects):
        if ob.name.startswith('MV_Horizontal timber') and abs(ob.location.y+7.2)<.03 and ob.location.z<z+1:
            height=ob.location.z;bpy.data.objects.remove(ob,do_unlink=True)
            for xa,xb in [(-12.12,-1.3),(1.3,12.12)]:box('Door clear timber',((xa+xb)/2,-7.2,height),(xb-xa,.14,.15),'Burgundy timber',facade[i])
        elif ob.name.startswith('MV_Side horizontal') and ob.location.x>12 and ob.location.z<z+1:
            height=ob.location.z;bpy.data.objects.remove(ob,do_unlink=True)
            for ya,yb in [(-7.15,-5.22),(-3.78,7.15)]:box('Tower door clear timber',(12.2,(ya+yb)/2,height),(.13,yb-ya,.15),'Burgundy timber',facade[i])
# Correct rear garden threshold and west conservatory rails too.
for ob in list(facade[0].objects):
    if ob.name.startswith('MV_Horizontal timber') and ob.location.y>7 and ob.location.z<1.45:
        h=ob.location.z;bpy.data.objects.remove(ob,do_unlink=True)
        for xa,xb in [(-12.12,-.85),(.85,12.12)]:box('Garden door clear course',((xa+xb)/2,7.2,h),(xb-xa,.14,.15),'Burgundy timber',facade[0])
    elif ob.name.startswith('MV_Side horizontal') and ob.location.x< -12 and ob.location.z<1.45:
        h=ob.location.z;bpy.data.objects.remove(ob,do_unlink=True)
        for ya,yb in [(-7.15,-.85),(.85,7.15)]:box('Conservatory clear course',(-12.2,(ya+yb)/2,h),(.13,yb-ya,.15),'Burgundy timber',facade[0])
# Key room connectivity markers for later validation.
nav=guides
for name,co in [('Player spawn',(0,-12,1.65)),('Front entry',(0,-7,Z[0]+1.65)),('Grand stair lower',(-.90,1.45,Z[0]+1.65)),('Grand stair upper',(.90,1.45,Z[1]+1.65)),('Attic arrival',(.90,1.45,Z[2]+1.65))]:
    o=bpy.data.objects.new(PREFIX+name,None);nav.objects.link(o);o.location=co;o.empty_display_type='ARROWS';o.empty_display_size=.35
print('REFINEMENT COMPLETE: attic valley headroom ~2.37m; real attic windows; connected conservatory.')
