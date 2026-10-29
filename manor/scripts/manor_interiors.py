# Run after manor_core.py in the same namespace.
# Furniture assemblies: origin on floor, facing local -Y; all dimensions in metres.
def assembly(name,x,y,z,angle,c,builder):
    before=set(c.objects);builder();obs=[o for o in c.objects if o not in before];root=bpy.data.objects.new(PREFIX+name,None);c.objects.link(root);root.location=(x,y,z);root.rotation_euler.z=angle
    for o in obs:
        if o.parent is None:o.parent=root
    return root

def leg(x,y,h,c,ma='Walnut',r=.055):
    cyl('Turned leg',(x,y,h*.47),r,h*.82,ma,c,n=12,r2=r*.68)
    for zz,rr in [(h*.10,r*1.13),(h*.77,r*1.22),(h*.86,r)]:sphere('Turned ring',(x,y,zz),(rr,rr,rr*.6),ma,c)
def table(x,y,z,c,w=1.5,d=.85,h=.76,angle=0):
    def make():
        box('Table top',(0,0,h),(w,d,.075),'Walnut',c,.035)
        for yy in [-d*.39,d*.39]:box('Table apron',(0,yy,h-.15),(w-.17,.055,.19),'Walnut',c,.012)
        for xx in [-w*.41,w*.41]:
            for yy in [-d*.37,d*.37]:leg(xx,yy,h-.08,c)
    return assembly('Table',x,y,z,angle,c,make)
def chair(x,y,z,c,angle=0,velvet='Velvet sage',arm=False):
    def make():
        box('Chair seat',(0,0,.49),(.59,.57,.11),velvet,c,.075)
        for xx in [-.22,.22]:
            for yy in [-.21,.21]:leg(xx,yy,.46,c,r=.033)
        for xx in [-.245,.245]:beam('Chair back stile',(xx,.23,.35),(xx,.3,1.09),.035,.05,'Walnut',c)
        box('Chair back cushion',(0,.29,.86),(.49,.11,.40),velvet,c,.075)
        box('Chair carved crest',(0,.29,1.105),(.59,.08,.08),'Walnut',c,.035)
        if arm:
            for xx in [-.31,.31]:
                leg(xx,-.1,.7,c,r=.026);beam('Arm rest',(xx,-.25,.74),(xx,.28,.76),.065,.065,'Walnut',c)
    return assembly('Chair',x,y,z,angle,c,make)
def sofa(x,y,z,c,angle=0,w=2.3,velvet='Velvet sage'):
    def make():
        for xx in [-w*.39,w*.39]:
            for yy in [-.32,.32]:leg(xx,yy,.24,c,r=.055)
        box('Sofa frame',(0,0,.29),(w,.90,.18),'Walnut',c,.045)
        box('Upholstered back',(0,.35,.82),(w-.16,.23,.89),velvet,c,.10)
        for k in range(3):box('Seat cushion',(-w/3+(k*w/3),-.07,.52),(w/3-.07,.68,.18),velvet,c,.09)
        for xx in [-w/2+.10,w/2-.10]:
            box('Sofa arm',(xx,-.02,.73),(.21,.91,.30),velvet,c,.095)
            curve('Carved arm scroll',[(xx,-.5,.61),(xx,-.49,.85),(xx,-.33,.89),(xx,.24,.93)],.048,'Walnut',c)
        for xx in [-w*.28,0,w*.28]:
            for zz in [.78,1.02]:sphere('Upholstery button',(xx,.215,zz),(.023,.018,.024),'Brass',c)
        for xx in [-w*.28,w*.28]:
            ob=box('Throw pillow',(xx,.01,.83),(.43,.16,.40),'Velvet wine',c,.075);ob.rotation_euler.y=xx*.2
    return assembly('Sofa',x,y,z,angle,c,make)
def cabinet(x,y,z,c,w=1.6,h=1.05,angle=0):
    def make():
        box('Cabinet carcass',(0,0,h/2),(w,.48,h),'Walnut',c,.025)
        box('Cabinet cornice',(0,0,h+.04),(w+.09,.56,.08),'Walnut',c,.02)
        for yy in [h*.24,h*.52,h*.8]:
            box('Drawer front',(0,-.255,yy),(w-.12,.045,h*.22),'Burgundy timber',c,.012)
            for xx in [-w*.24,w*.24]:sphere('Drawer handle',(xx,-.303,yy),(.052,.024,.025),'Brass',c)
    return assembly('Cabinet',x,y,z,angle,c,make)
def bookshelf(x,y,z,c,w=2.0,h=2.75,angle=0):
    def make():
        box('Bookcase back',(0,.17,h/2),(w,.08,h),'Walnut',c)
        for xx in [-w/2,w/2]:box('Bookcase upright',(xx,0,h/2),(.11,.42,h),'Walnut',c,.014)
        for zz in [0,h]:box('Bookcase cornice',(0,0,zz),(w+.15,.49,.13),'Walnut',c,.018)
        for sh in range(6):
            zz=.15+sh*.43
            box('Library shelf',(0,0,zz),(w,.44,.062),'Walnut',c,.009)
            xpos=-w/2+.10
            while xpos<w/2-.12:
                bw=random.uniform(.046,.09);bh=random.uniform(.23,.35);bd=random.uniform(.18,.25)
                cover=M['Book'+str(random.randrange(5))];bc=box('Bound volume',(xpos+bw/2,-.023,zz+.034+bh/2),(bw,bd,bh),cover,c,.005)
                box('Book pages',(xpos+bw/2,-.017,zz+.034+bh/2),(bw-.012,bd-.025,bh-.025),'Pages',c)
                # visible spine faces -Y
                for height in [.045,bh-.04]:box('Gold spine band',(xpos+bw/2,-.025-bd/2,zz+.034+height),(bw*.8,.008,.006),'Brass',c)
                xpos+=bw+.012
    return assembly('Bookcase',x,y,z,angle,c,make)
def picture(x,y,z,c,w=1.4,h=.85,angle=0):
    def make():
        plane('Landscape canvas',(0,-.022,0),w,h,'Painting',c,True)
        for xx in [-w/2-.045,w/2+.045]:box('Gilt frame vertical',(xx,-.02,0),(.09,.08,h+.16),'Brass',c,.018)
        for zz in [-h/2-.045,h/2+.045]:box('Gilt frame horizontal',(0,-.02,zz),(w+.18,.08,.09),'Brass',c,.018)
    return assembly('Framed landscape',x,y,z,angle,c,make)
def fireplace(x,y,z,c,angle=0,w=2.05):
    def make():
        box('Hearth stone',(0,-.24,.08),(w+.38,1.0,.16),'Slate',c,.018)
        box('Firebox dark recess',(0,.15,.66),(w*.69,.075,1.06),'Coal',c)
        for xx in [-w*.40,w*.40]:box('Fireplace pier',(xx,0,.75),(.26,.43,1.4),'Limestone',c,.02)
        box('Fireplace lintel',(0,0,1.47),(w,.48,.22),'Limestone',c,.024)
        box('Oak mantel',(0,-.025,1.63),(w+.24,.62,.12),'Walnut',c,.028)
        box('Chimney breast',(0,.21,2.45),(w+.02,.17,1.55),'Walnut',c,.015)
        picture(0,.10,2.40,c,w*.76,.85)
        for k in range(6):beam('Fire grate',(-w*.29+k*w*.116,-.36,.16),(-w*.29+k*w*.116,-.36,.58),.022,.022,'Iron',c)
        for height in [.22,.46]:beam('Grate rail',(-w*.34,-.36,height),(w*.34,-.36,height),.032,.032,'Iron',c)
        for k in range(3):ob=cyl('Hearth log',(0,-.04,.20+k*.055),.075,w*.55,'Walnut',c,n=10);ob.rotation_euler.y=math.pi/2;ob.rotation_euler.z=k*.18
        for xx in [-.7,.7]:vase(xx,-.05,1.70,c,.21)
    return assembly('Fireplace',x,y,z,angle,c,make)
def vase(x,y,z,c,h=.32,ma='Ceramic'):
    cyl('Vase foot',(x,y,z+.015),h*.22,.03,ma,c,n=20)
    sphere('Vase body',(x,y,z+h*.44),(h*.28,h*.28,h*.35),ma,c,2)
    cyl('Vase neck',(x,y,z+h*.79),h*.13,h*.28,ma,c,n=20,r2=h*.17)
    cyl('Vase lip',(x,y,z+h*.96),h*.19,.03,ma,c,n=20)
def lamp(x,y,z,c):
    cyl('Lamp base',(x,y,z+.026),.16,.05,'Brass',c,n=24)
    cyl('Lamp stem',(x,y,z+.25),.031,.4,'Brass',c,n=16)
    cyl('Fabric lamp shade',(x,y,z+.52),.25,.29,'Linen',c,n=32,r2=.15)
    sphere('Lamp glow',(x,y,z+.43),(.07,.07,.1),'Warm lamp',c)
def chandelier(x,y,z,c,r=.65):
    cyl('Pendant chain',(x,y,z+.38),.018,.76,'Brass',c,n=10)
    sphere('Pendant hub',(x,y,z),(.13,.13,.18),'Brass',c)
    for k in range(6):
        a=k*math.tau/6;dx=math.cos(a);dy=math.sin(a)
        curve('Chandelier arm',[(x,y,z),(x+dx*r*.55,y+dy*r*.55,z-.18),(x+dx*r,y+dy*r,z-.1),(x+dx*r,y+dy*r,z+.06)],.018,'Brass',c)
        cyl('Candle cup',(x+dx*r,y+dy*r,z+.05),.085,.06,'Brass',c,n=16)
        cyl('Candle',(x+dx*r,y+dy*r,z+.18),.026,.22,'Ivory',c,n=12)
        sphere('Candle flame',(x+dx*r,y+dy*r,z+.31),(.035,.035,.07),'Warm lamp',c)
    area('Warm chandelier', (x,y,z+.16),(x,y,z-3),170,2.4,(1,.76,.47))
def rug(x,y,z,c,w,d):return plane('Oriental rug',(x,y,z+.018),w,d,'Rug',c)
def bed(x,y,z,c,w=1.9,angle=0,canopy=False):
    def make():
        for xx in [-w*.46,w*.46]:
            for yy in [-1.0,1.0]:leg(xx,yy,.48,c,r=.07)
        box('Bed frame',(0,0,.43),(w+.14,2.22,.24),'Walnut',c,.03)
        box('Mattress',(0,0,.64),(w,2.10,.27),'Linen',c,.12)
        box('Coverlet',(0,-.26,.78),(w+.025,1.62,.12),'Velvet sage',c,.09)
        box('Headboard',(0,1.075,.94),(w+.12,.12,1.2),'Walnut',c,.04)
        box('Headboard upholstered panel',(0,1.00,1.10),(w-.16,.07,.50),'Velvet wine',c,.07)
        box('Footboard',(0,-1.09,.70),(w+.12,.10,.70),'Walnut',c,.04)
        for xx in [-w*.25,w*.25]:box('Pillow',(xx,.70,.85),(w*.43,.45,.18),'Linen',c,.085)
        if canopy:
            for xx in [-w*.54,w*.54]:
                for yy in [-1.13,1.13]:
                    cyl('Four poster',(xx,yy,1.45),.055,2.9,'Walnut',c,n=16)
                    sphere('Bed finial',(xx,yy,2.95),(.09,.09,.12),'Walnut',c)
            for yy in [-1.13,1.13]:box('Canopy crossrail',(0,yy,2.82),(w+ .22,.12,.16),'Walnut',c,.015)
            for xx in [-w*.54,w*.54]:box('Canopy siderail',(xx,0,2.82),(.12,2.38,.16),'Walnut',c,.015)
    return assembly('Bed',x,y,z,angle,c,make)
def trunk(x,y,z,c,angle=0,w=1.15):
    def make():
        box('Travel trunk',(0,0,.38),(w,.62,.70),'Leather',c,.055)
        box('Trunk lid',(0,0,.75),(w+.03,.65,.12),'Walnut',c,.04)
        for xx in [-w*.33,w*.33]:
            box('Trunk strap',(xx,-.318,.39),(.045,.02,.70),'Brass',c)
            box('Trunk top strap',(xx,0,.82),(.045,.65,.015),'Brass',c)
        box('Trunk lock',(0,-.33,.60),(.085,.03,.11),'Brass',c,.012)
    return assembly('Travel trunk',x,y,z,angle,c,make)
# Room wall treatments split at door/window positions, avoid blocking openings.
for i,layout in enumerate(layouts):
    z=Z[i]
    for name,b in layout:
        key=name.split(' |')[0];c=room_c[(i,key)];x1,x2,y1,y2=b
        if 'stair' in key.lower() or 'landing' in key.lower():continue
        # Decorative rails along side walls only; remain away from main corridor doors.
        for xx in [x1,x2]:
            box('Oak skirting',(xx,(y1+y2)/2,z+.10),(.055,y2-y1,.20),'Walnut',c,.009)
            box('Dado moulding',(xx,(y1+y2)/2,z+1.03),(.055,y2-y1,.085),'Walnut',c,.009)
            # panels limited below sill level on exterior edges.
            for k in range(int((y2-y1)/.62)):
                yy=y1+.32+k*.62;box('Wainscot panel',(xx,yy,z+.52),(.028,.52,.82),'Walnut',c,.006)
        # interior side-facing wallpaper, where no outside openings occur.
        if i<2 and x1>-11:
            ob=plane('Botanical wallcover', (x1+.012,(y1+y2)/2,z+2.32),y2-y1,2.45,'Wallpaper '+('blue' if i==0 else 'ivory'),c,True);ob.rotation_euler.z=-math.pi/2
        if i<2 and x2<11:
            ob=plane('Botanical wallcover',(x2-.012,(y1+y2)/2,z+2.32),y2-y1,2.45,'Wallpaper '+('sage' if i==0 else 'ivory'),c,True);ob.rotation_euler.z=math.pi/2
        if i<2:
            box('Room ceiling',((x1+x2)/2,(y1+y2)/2,z+3.77),(x2-x1,y2-y1,.065),'Ivory',ceilings[i])
            for yy in [y1,y2]:box('Cornice',((x1+x2)/2,yy,z+3.60),(x2-x1,.12,.18),'Ivory',c,.018)
            for xx in [x1,x2]:box('Cornice',(xx,(y1+y2)/2,z+3.60),(.12,y2-y1,.18),'Ivory',c,.018)
# Corridors receive runners, wall lights and framed paintings. All routes >= 1.2 m.
for i,z in enumerate(Z):
    c=coll(f'L{i+1} Corridor decor',furn[i]);rug(0,.14,z,c,22,1.4)
    for x in [-10,-4,3.3,8.6]:
        picture(x,1.18,z+2.08,c,.85,.58)
    for x in [-9,0,8]:chandelier(x,.16,z+3.1 if i<2 else z+2.25,c,.32)
# Main drawing room: fireplace east, seating around carpet, piano west/front.
z=Z[0];c=furn_c[(0,'Drawing room')]
rug(-7.8,-4.0,z,c,5.4,3.6)
sofa(-7.9,-5.95,z,c,math.pi,2.65)
sofa(-10.65,-3.7,z,c,math.pi/2,2.0)
chair(-5.6,-2.7,z,c,.35,'Velvet wine',True)
table(-7.8,-3.8,z,c,1.8,.95,.55)
vase(-7.8,-3.8,z+.60,c,.30)
fireplace(-2.74,-4.1,z,c,-math.pi/2,2.15)
cabinet(-10.4,-1.45,z,c,1.7,1.05,math.pi)
picture(-10.4,-1.38,z+2.15,c,1.55,.92,math.pi)
chandelier(-7.7,-3.8,z+2.94,c,.74)
# Upright piano, keyboard and music book.
def piano_make():
    box('Piano cabinet',(0,0,.80),(1.55,.52,1.52),'Walnut',c,.025);box('Piano keyboard',(0,-.40,.82),(1.38,.35,.075),'Ivory',c,.012)
    for k in range(35):box('Ivory key',(-.66+k*.038,-.44,.865),(.033,.27,.02),'Ivory',c)
    for k in range(25):
        if k%7 not in [2,6]:box('Ebony key',(-.64+k*.051,-.37,.89),(.023,.14,.04),'Iron',c)
    box('Music rest',(0,-.29,1.12),(.65,.06,.43),'Walnut',c,.014)
assembly('Upright piano',-11.45,-5.65,z,math.pi/2,c,piano_make)
# Library walls filled with individual bound volumes; desk not on entry path.
c=furn_c[(0,'Library')]
for x in [-10.1,-7.85,-5.6]:bookshelf(x,6.50,z,c,2.05,2.9)
bookshelf(-11.45,3.50,z,c,2.3,2.9,math.pi/2)
rug(-7.6,3.9,z,c,5.8,3.4)
table(-7.7,4.4,z,c,2.0,1.0,.79)
chair(-7.7,5.25,z,c,0,'Leather',True)
chair(-9.4,2.7,z,c,math.pi/4,'Velvet wine',True)
lamp(-8.35,4.4,z+.84,c)
box('Open book pages',(-7.55,4.23,z+.86),(.42,.30,.035),'Pages',c,.008)
fireplace(-2.75,4.4,z,c,-math.pi/2,2.0)
chandelier(-7.8,3.9,z+2.96,c,.6)
# Dining room table, 10 chairs, plates and glassware.
c=furn_c[(0,'Dining room')];rug(7,-4.1,z,c,6.3,3.6);table(7,-4.1,z,c,4.1,1.35,.8)
for x in [5.5,6.5,7.5,8.5]:
    chair(x,-5.25,z,c,math.pi,'Velvet wine');chair(x,-2.95,z,c,0,'Velvet wine')
    for yy in [-4.53,-3.67]:
        cyl('Dining plate',(x,yy,z+.86),.16,.022,'Ceramic',c,n=28)
        cyl('Wine glass foot',(x+.23,yy,z+.86),.045,.012,'Glazing',c,n=12)
        cyl('Wine stem',(x+.23,yy,z+.94),.007,.14,'Glazing',c,n=10)
        sphere('Wine bowl',(x+.23,yy,z+1.04),(.05,.05,.065),'Glazing',c)
chair(4.4,-4.1,z,c,-math.pi/2,'Velvet wine');chair(9.6,-4.1,z,c,math.pi/2,'Velvet wine')
cabinet(6.7,-6.5,z,c,2.5,1.05,0);vase(6.7,-6.5,z+1.1,c,.40)
chandelier(7,-4.1,z+2.92,c,.76)
# Entrance and upper sitting room
c=furn_c[(0,'Entrance hall')];rug(0,-3.4,z,c,2.1,3.1);cabinet(-2.05,-4.6,z,c,1.4,.86,math.pi/2);vase(-2.05,-4.6,z+.94,c,.4);chandelier(0,-4.5,z+3.05,c,.46)
# Kitchen: range, workbench, stone sink, hanging pans.
c=furn_c[(0,'Kitchen')]
box('Kitchen flags',(5.65,3.05,z+.012),(6,3.15,.022),'Limestone',c)
box('Cast iron range',(3.8,4.22,z+.5),(2.1,.70,1),'Iron',c,.035)
for x in [3.2,3.8,4.4]:
    box('Range oven door',(x,3.85,z+.47),(.55,.05,.54),'Iron',c,.04);sphere('Oven knob',(x+.13,3.79,z+.58),(.045,.025,.035),'Brass',c)
    cyl('Hotplate',(x,4.16,z+1.018),.22,.025,'Iron',c,n=24)
box('Range hood',(3.8,4.25,z+2.5),(2.4,.95,.4),'Iron',c,.025)
box('Flue',(3.8,4.25,z+3.15),(.50,.45,1),'Iron',c)
table(6.4,3.15,z,c,1.85,.75,.9)
box('Chopping board',(6.2,3.15,z+.97),(.6,.42,.055),'Walnut',c,.03)
cabinet(8.3,3.25,z,c,1.7,.86,-math.pi/2)
box('Sink rim',(8.19,3.25,z+.94),(.67,1.14,.16),'Ceramic',c,.055)
box('Sink basin dark',(8.19,3.25,z+1.025),(.40,.80,.012),'Slate',c,.06)
curve('Swan neck tap',[(8.52,3.25,z+1),(8.52,3.25,z+1.4),(8.30,3.25,z+1.46),(8.22,3.25,z+1.3)],.023,'Brass',c)
for x in [3.2,4,4.8]:
    curve('Pan hook',[(x,4.53,z+2.04),(x,4.43,z+1.95),(x,4.46,z+1.84)],.01,'Iron',c)
    pot=cyl('Copper pan',(x,4.40,z+1.50),.22,.10,'Copper',c,n=24);pot.rotation_euler.x=math.pi/2
    beam('Pan handle',(x,4.4,z+1.68),(x,4.4,z+1.9),.045,.025,'Iron',c)
chandelier(6,3.1,z+3.10,c,.32)
# Pantry shelving and kitchen utility
for key,x in [('Pantry',4),('Utility store',7.2)]:
    c=furn_c[(0,key)]
    for zz in [.5,1.2,1.9]:
        box('Utility shelf',(x,6.40,z+zz),(2.4,.48,.065),'Walnut',c)
        for xx in [x-.8,x-.3,x+.3,x+.8]:vase(xx,6.4,z+zz+.04,c,.35,'Ceramic' if key=='Pantry' else 'Copper')
    trunk(x,5.5,z,c,w=1.2)
# Main master bedroom
z=Z[1];c=furn_c[(1,'Master bedroom')]
rug(-7.7,-4.2,z,c,5.8,3.8);bed(-8.0,-4.5,z,c,2.05,0,True)
for x in [-9.60,-6.4]:cabinet(x,-3.7,z,c,.74,.65);lamp(x,-3.7,z+.72,c)
fireplace(-2.75,-4.4,z,c,-math.pi/2,1.85)
chair(-10.6,-2.4,z,c,0,'Velvet wine',True);cabinet(-10.5,-6.5,z,c,1.8,1.05)
chandelier(-7.4,-3.2,z+3.02,c,.52)
for key,x in [('Guest bedroom A',4.9),('Guest bedroom B',9.65)]:
    c=furn_c[(1,key)];bed(x,-4.4,z,c,1.5);rug(x,-3.3,z,c,3.1,3.9);cabinet(x+1.25,-3.75,z,c,.65,.7);lamp(x+1.25,-3.75,z+.78,c);chair(x,-1.8,z,c,0);chandelier(x,-3.3,z+3.12,c,.32)
c=furn_c[(1,'Upper sitting room')];sofa(0,-4.9,z,c,0,1.9);table(0,-3.7,z,c,1.05,.6,.56);rug(0,-4,z,c,2.4,3.2)
c=furn_c[(1,'Family study')];bookshelf(5.6,6.5,z,c,3,2.8);table(6.5,3.7,z,c,1.8,.8,.8);chair(6.5,4.5,z,c);lamp(5.9,3.7,z+.85,c);rug(5.6,3.8,z,c,4.1,3.4)
c=furn_c[(1,'Bath & washroom')]
# Clawfoot bath with hollow visible basin mesh.
vs=[];fs=[];N=48
for zz,rx,ry in [(.25,.55,1.0),(.78,.68,1.08),(.78,.56,.95),(.34,.40,.80)]:
    vs += [(math.cos(k*math.tau/N)*rx,math.sin(k*math.tau/N)*ry,zz) for k in range(N)]
for ring in range(3):fs += [(ring*N+k,ring*N+(k+1)%N,(ring+1)*N+(k+1)%N,(ring+1)*N+k) for k in range(N)]
fs.append(tuple(range(3*N,4*N)));ob=mesh('Clawfoot bath',vs,fs,'Ceramic',c);ob.location=(-10.5,2.9,z)
for xx in [-.4,.4]:
    for yy in [-.75,.75]:sphere('Bath clawfoot',(-10.5+xx,2.9+yy,z+.16),(.08,.09,.18),'Brass',c)
cabinet(-8.3,4.05,z,c,1.25,.8);vase(-8.3,4.05,z+.87,c,.23)
c=furn_c[(1,'Dressing room')]
for x in [-6.4,-4.6]:cabinet(x,3.95,z,c,1.5,2.8)
c=furn_c[(1,'Linen store')]
for x in [-10,-7,-4]:cabinet(x,6.4,z,c,2,1.3);trunk(x,5.4,z,c,w=.8)
# Attic furniture, exposed rafters and storage. Ceiling clearance minimum 2.35m after patch.
z=Z[2]
for key,x in [('Servant room A',4.9),('Servant room B',9.65)]:
    c=furn_c[(2,key)];bed(x,-4.4,z,c,1.0);trunk(x+1.1,-5.6,z,c,w=.8);table(x,-1.8,z,c,.8,.5,.7);chair(x,-2.5,z,c,math.pi)
c=furn_c[(2,'Attic trunks')]
for x,y,a in [(-10.6,-5.6,0),(-8.8,-5.6,.08),(-6.7,-5.5,0),(-4.6,-5.9,-.1),(-10.3,-2.2,.2),(-4.1,-2.2,0)]:trunk(x,y,z,c,a,1.2)
for x in [-9.8,-7.8,-5.8]:
    for zz in [.65,1.3,1.95]:box('Attic shelf',(x,-6.35,z+zz),(1.75,.52,.065),'Walnut',c)
    for zz in [.8,1.45]:box('Linen storage box',(x,-6.35,z+zz+.16),(1.1,.43,.32),'Linen',c,.025)
c=furn_c[(2,'Old furniture store')]
for x,y in [(-10.5,5.7),(-8.5,5.7),(-6,5.7)]:cabinet(x,y,z,c,1.5,1.3)
for x,y in [(-10,2.6),(-8.5,3),(-5,3.8)]:chair(x,y,z,c,.3,'Leather');trunk(x+.7,y+.6,z,c,w=.7)
c=furn_c[(2,'Drying room')]
for x in [4,7]:
    for y in [3,5.8]:box('Drying rack upright',(x,y,z+1.1),(.055,.055,2.2),'Walnut',c)
    for yy in [3.3,3.8,4.3,4.8,5.3]:beam('Drying rack rail',(x-.3,yy,z+1.8),(x+.3,yy,z+1.8),.03,.03,'Walnut',c)
# Separate illumination provides usable game-reference interior previews.
for i,layout in enumerate(layouts):
    for name,b in layout:
        if 'stair' in name.lower() or 'landing' in name.lower():continue
        x=(b[0]+b[1])/2;y=(b[2]+b[3])/2
        area('Room soft bounce',(x,y,Z[i]+(3.4 if i<2 else 2.2)),(x,y,Z[i]),240 if i<2 else 140,3.1,(1,.86,.69))
print('INTERIORS COMPLETE',len(scene.objects),'objects')
