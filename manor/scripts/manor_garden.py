terrain=coll('Garden | 地形草坪与砂砾路',gardens);plants=coll('Garden | 花坛树篱与乔木',gardens);fixtures=coll('Garden | 座椅围栏与大门',gardens)
# Estate has a front court and a larger rear garden; human scale 62 x 58m.
box('Garden ground',(0,3,-.23),(62,58,.38),'Grass',terrain,.2)
# Fine grass variation in material rather than millions of grass objects.
m=M['Grass'];n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF');tc=n.new('ShaderNodeTexCoord');no=n.new('ShaderNodeTexNoise');no.inputs['Scale'].default_value=180;no.inputs['Detail'].default_value=3;l.new(tc.outputs['Generated'],no.inputs['Vector']);cr=n.new('ShaderNodeValToRGB');cr.color_ramp.elements[0].color=(.055,.115,.022,1);cr.color_ramp.elements[1].color=(.21,.32,.065,1);l.new(no.outputs['Fac'],cr.inputs[0]);l.new(cr.outputs[0],p.inputs['Base Color']);bu=n.new('ShaderNodeBump');bu.inputs['Strength'].default_value=.38;bu.inputs['Distance'].default_value=.025;l.new(no.outputs['Fac'],bu.inputs['Height']);l.new(bu.outputs[0],p.inputs['Normal'])
# Paths, never cover the footprint of house or stair entrances.
box('Front arrival walk',(0,-17.2,-.005),(3.9,14.4,.07),'gravel',terrain,.02)
box('Front terrace walk',(0,-11.0,-.005),(40,2.6,.07),'gravel',terrain)
for x in [-20.1,19.7]:box('Side garden path',(x,5.5,-.005),(2.2,35.5,.07),'gravel',terrain)
box('Rear cross path',(0,10.3,-.005),(40,2.4,.07),'gravel',terrain)
box('Rear axial walk',(0,19.6,-.005),(2.5,19,.07),'gravel',terrain)
box('Back garden walk',(0,28.3,-.005),(40,2.2,.07),'gravel',terrain)
for k in range(3):box('Back door step',(0,7.38+k*.33,.32-k*.16),(2.3,.36,.16),'Limestone',terrain,.015)
# Reusable leaf clumps, geometry is generated into a single mesh per plant.
def leaf_mesh(name,clusters,c,seed=1):
    rng=random.Random(seed);vs=[];fs=[];matids=[]
    for center,radii,count in clusters:
        cx,cy,cz=center;rx,ry,rz=radii
        for k in range(count):
            theta=rng.random()*math.tau;cost=rng.uniform(-1,1);sint=math.sqrt(1-cost*cost);rr=rng.random()**.33
            pos=Vector((cx+rx*rr*sint*math.cos(theta),cy+ry*rr*sint*math.sin(theta),cz+rz*rr*cost))
            length=rng.uniform(.075,.16);width=length*.55
            normal=Vector((rng.uniform(-1,1),rng.uniform(-1,1),rng.uniform(-.4,1))).normalized();u=normal.cross(Vector((0,0,1))).normalized()*length;v=normal.cross(u).normalized()*width
            j=len(vs);vs.extend([tuple(pos-u),tuple(pos-v),tuple(pos+normal*.02),tuple(pos+v),tuple(pos+u)]);fs.extend([(j,j+1,j+2),(j+1,j+4,j+2),(j+4,j+3,j+2),(j+3,j,j+2)]);matids.extend([rng.choices([0,1,2],[.45,.40,.15])[0]]*4)
    ob=mesh(name,vs,fs,'Leaf dark',c,False);ob.data.materials.append(M['Leaf']);ob.data.materials.append(M['Leaf light'])
    for p,mi in zip(ob.data.polygons,matids):p.material_index=mi
    return ob
# Trimmed yew hedges: dense surface leaves plus softened core, avoiding plastic blocks.
def hedge(name,x,y,w,d,h):
    core=box(name+' core',(x,y,h/2),(w,d,h),'Leaf dark',plants,.18)
    rng=random.Random(int((x+40)*100+y*10));clusters=[]
    count=max(2,int(w/.7));rows=max(1,int(d/.65))
    for ix in range(count):
        for iy in range(rows):clusters.append(((x-w/2+(ix+.5)*w/count,y-d/2+(iy+.5)*d/rows,h*.55),(.60,.52,h*.60),240))
    leaf_mesh(name+' foliage',clusters,plants,seed=rng.randrange(100000))
for x in [-8.1,8.1]:hedge('Front clipped hedge',x,-22.0,11.4,1.05,1.23)
for x in [-26,26]:hedge('Boundary yew hedge',x,5.0,1.15,47,1.65)
hedge('Rear clipped hedge',0,31,51,1.1,1.45)
# Four formal parterre beds front, four rear, gravel border and low clipped edges.
beds=[(-8,-16.2,7,5),(8,-16.2,7,5),(-8,17,10,8),(8,17,10,8)]
for bidx,(x,y,w,d) in enumerate(beds):
    box('Flowerbed earth',(x,y,-.014),(w,d,.035),'Earth',terrain)
    for yy in [y-d/2,y+d/2]:hedge('Parterre low hedge',x,yy,w,.40,.55)
    for xx in [x-w/2,x+w/2]:hedge('Parterre side hedge',xx,y,.4,d,.55)
    # Flower heads mesh, leaves separately. Dense lavender and roses in maintained borders.
    clusters=[]
    for k in range(36 if bidx<2 else 60):
        px=x+random.uniform(-w/2+.65,w/2-.65);py=y+random.uniform(-d/2+.65,d/2-.65);height=random.uniform(.36,.80)
        clusters.append(((px,py,height*.45),(.22,.22,height*.45),30))
        for j in range(3):
            xx=px+random.uniform(-.16,.16);yy=py+random.uniform(-.16,.16)
            beam('Flower stem',(xx,yy,.05),(xx,yy,height),.012,.012,'Leaf dark',plants)
            if bidx%2:
                for n in range(4):sphere('Lavender florets',(xx,yy,height-.04+n*.045),(.045,.045,.055),'Lavender',plants,1)
            else:
                for a in range(5):
                    ang=a*math.tau/5;sphere('Rose petal',(xx+math.cos(ang)*.04,yy+math.sin(ang)*.04,height),(.06,.045,.035),'Rose' if j%2 else 'White flower',plants,1)
    leaf_mesh('Flower foliage',clusters,plants,seed=100+bidx)
# Realistic branch silhouette with fine leaf geometry instead of sphere-only canopies.
def tree(x,y,h,seed):
    rng=random.Random(seed);cl=coll('Tree '+str(seed),plants);trunkheight=h*.56
    cyl('Tree trunk',(x,y,trunkheight/2),.32,trunkheight,'Walnut',cl,n=12,r2=.13)
    clusters=[]
    for k in range(12):
        a=k*2.399+rng.uniform(-.3,.3);reach=rng.uniform(1.1,2.7)*h/9;zz=h*.42+k*h*.025
        end=(x+math.cos(a)*reach,y+math.sin(a)*reach,zz+h*.15)
        curve('Oak branch',[(x,y,zz-.4),(x+math.cos(a)*reach*.5,y+math.sin(a)*reach*.5,zz+.2),end],.045,'Walnut',cl)
        for j in range(3):
            ex=end[0]+rng.uniform(-.7,.7);ey=end[1]+rng.uniform(-.7,.7);ez=end[2]+rng.uniform(-.2,.7)
            beam('Oak twig',end,(ex,ey,ez),.015,.015,'Walnut',cl)
            clusters.append(((ex,ey,ez),(.9,.82,1.0),210))
    clusters.append(((x,y,h*.85),(1.45,1.45,h*.18),1200))
    leaf_mesh('Oak canopy',clusters,cl,seed)
for k,(x,y,h) in enumerate([(-25,-18,8.5),(25,-19,9.5),(-24,13,10),(25,13,10.5),(-23,26,11),(23,27,12),(-10, 30,9),(12,30,10)]):tree(x,y,h,k+80)
# Entrance topiary in terracotta urns.
for x in [-3.75,3.75]:
    y=-10.0;cyl('Terracotta urn',(x,y,.36),.34,.70,'Burgundy timber',fixtures,n=24,r2=.45)
    cyl('Topiary stem',(x,y,1.03),.08,.7,'Walnut',plants,n=12)
    sphere('Topiary core',(x,y,1.65),(.52,.52,.75),'Leaf dark',plants)
    leaf_mesh('Topiary leaves',[((x,y,1.65),(.56,.56,.77),950)],plants,int(x*100+500))
# Benches with slatted seats and backs.
def bench(x,y,angle=0):
    def make():
        for xx in [-.82,.82]:
            for yy in [-.23,.23]:beam('Bench leg',(xx,yy,.05),(xx,yy,.50),.07,.07,'Iron',fixtures)
            curve('Bench side arm',[(xx,-.3,.56),(xx,-.28,.75),(xx,.25,.75)],.025,'Iron',fixtures)
        for k in range(5):box('Bench seat slat',(0,-.24+k*.12,.52),(2.0,.095,.06),'Walnut',fixtures,.016)
        for k in range(4):box('Bench back slat',(0,.30,.75+k*.13),(2.0,.07,.10),'Walnut',fixtures,.015)
        for xx in [-.85,.85]:beam('Bench back frame',(xx,.25,.4),(xx,.30,1.20),.05,.06,'Iron',fixtures)
    assembly('Garden bench',x,y,0,angle,fixtures,make)
for x,y,a in [(-16,-12.8,math.pi),(16,-12.8,math.pi),(-15,11.7,0),(15,11.7,0),(-4,26,0),(4,26,0)]:bench(x,y,a)
# Boundary iron fence and masonry gate pillars.
for xa,xb in [(-28,-2.6),(2.6,28)]:
    box('Front boundary wall',((xa+xb)/2,-24.4,.30),(xb-xa,.45,.6),'red_bricks_02',fixtures,.02)
    for zz in [.75,1.55]:beam('Fence rail',(xa,-24.4,zz),(xb,-24.4,zz),.035,.035,'Iron',fixtures)
    for k in range(int((xb-xa)/.24)):
        xx=xa+.12+k*.24;cyl('Fence picket',(xx,-24.4,1.18),.018,1.26,'Iron',fixtures,n=8);cyl('Spear finial',(xx,-24.4,1.87),.045,.12,'Iron',fixtures,n=6,r2=0)
for x in [-2.7,2.7]:
    box('Gate pillar',(x,-24.4,.99),(.75,.75,1.98),'red_bricks_02',fixtures,.03)
    box('Gate cap',(x,-24.4,2.03),(.9,.9,.16),'Limestone',fixtures,.025);sphere('Gate stone ball',(x,-24.4,2.29),(.22,.22,.22),'Limestone',fixtures)
# Gates initially open inward; retain hinge objects for game animation.
for s in [-1,1]:
    def make_gate():
        for zz in [.18,1.6]:box('Gate rail',(s*1.19,0,zz),(2.35,.07,.065),'Iron',fixtures)
        for k in range(10):
            xx=s*(.1+k*.23);cyl('Gate bar',(xx,0,.96),.02,1.7,'Iron',fixtures,n=8)
            curve('Gate scroll',[(xx,0,1.52),(xx+s*.10,0,1.72),(xx+s*.2,0,1.62)],.015,'Iron',fixtures)
    gate=assembly('Entrance gate hinge',-s*2.58,-24.4,0,s*math.radians(78),fixtures,make_gate);gate['interactive']='Rotate local Z';gate['open_angle_deg']=78
# Central rear sundial, not a fountain obstacle on axial walk.
cyl('Sundial base',(0,23, .10),.48,.2,'Limestone',fixtures,n=24)
cyl('Sundial pedestal',(0,23,.61),.19,.9,'Limestone',fixtures,n=16,r2=.14)
cyl('Sundial dial',(0,23,1.08),.42,.08,'Brass',fixtures,n=32)
mesh('Sundial gnomon',[(-.2,23,1.13),(.2,23,1.13),(0,23,1.36)],[(0,1,2)],'Brass',fixtures)
# Slightly widened path around sundial keeps two clear passing sides.
box('Sundial paving',(0,23,.02),(4,4,.04),'gravel',terrain)
# Scene context terrain is intentionally bounded, no road/car assets unrelated to period.
scene.camera=cameras['01 Exterior'];cameras['01 Exterior'].location=(43,-57,30);cameras['01 Exterior'].rotation_euler=(Vector((0,1,5.7))-cameras['01 Exterior'].location).to_track_quat('-Z','Y').to_euler();cameras['01 Exterior'].data.lens=43
camera('07 Garden arrival',(0,-29,2.0),(0,-1,7.2),24)
camera('08 Rear garden',(-34,39,18),(0,2,5),39)
print('GARDEN COMPLETE',len(scene.objects),'objects')
