from pathlib import Path
import urllib.request, json, concurrent.futures, random, math
from PIL import Image, ImageDraw, ImageFilter
BASE=Path(__file__).resolve().parents[1]
TEX=BASE/'textures'
if not TEX.exists(): TEX.mkdir(parents=True)
# 已有完整贴图则跳过（仓库自带 textures/，无需联网与 Pillow；删除 textures/ 可强制重新生成）。
if (TEX/'sources.json').exists() and len(list(TEX.glob('*.jpg')))>=20:
    print('Textures already present:',len(list(TEX.glob('*.jpg'))),'jpg; prepare_materials skipped.')
    raise SystemExit(0)
ASSETS={'wood_floor':1.7,'red_bricks_02':2.5,'clay_roof_tiles_02':2.5,'gravel':2.0,'plastered_wall_02':2.23}
def get(url):
    req=urllib.request.Request(url,headers={'User-Agent':'ManorSceneBuilder/1.0 (Poly Haven CC0 material study)'})
    return urllib.request.urlopen(req,timeout=60).read()
def fetch(asset):
    data=json.loads(get('https://api.polyhaven.com/files/'+asset)); result={}
    for channel in ['Diffuse','Rough','nor_gl']:
        entry=data[channel]['2k']['jpg']; p=TEX/(asset+'_'+channel+'.jpg')
        p.write_bytes(get(entry['url'])); result[channel]=p.name
    return asset,{'source':'https://polyhaven.com/a/'+asset,'license':'CC0','size_m':ASSETS[asset],'maps':result}
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
    manifest=dict(ex.map(fetch,ASSETS))
(TEX/'sources.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
random.seed(91)
# Original botanical wallpaper: a repeat, not a scan of a copyrighted photograph.
for name,bg,stem,leaf,flower in [('sage',(96,111,90),(175,160,103),(152,163,113),(214,189,142)),('blue',(46, 75,86),(168,158,110),(101,139,131),(211,179,132)),('ivory',(205,194,162),(140,134,92),(121,143,111),(169,116,91))]:
    im=Image.new('RGB',(768,768),bg); d=ImageDraw.Draw(im)
    for cx in [-192,192,576,960]:
        for cy in [-384,0,384,768]:
            pts=[]
            for k in range(61):
                y=cy+k*6.4; x=cx+48*math.sin(k/60*math.tau); pts.append((x,y))
            d.line(pts,fill=stem,width=5)
            for k in range(8):
                y=cy+35+k*43; x=cx+48*math.sin((y-cy)/384*math.tau); side=(-1)**k
                leafpts=[(x,y),(x+side*58,y-36),(x+side*72,y-13),(x+side*44,y+9)]
                d.polygon(leafpts,fill=leaf); d.line([(x,y),(x+side*60,y-18)],fill=stem,width=2)
            for a in range(7):
                theta=a*math.tau/7; x=cx+math.cos(theta)*22; y=cy+193+math.sin(theta)*22
                d.ellipse((x-12,y-19,x+12,y+19),fill=flower)
            d.ellipse((cx-9,cy+184,cx+9,cy+202),fill=stem)
    pix=im.load()
    for _ in range(60000):
        x=random.randrange(768); y=random.randrange(768); c=pix[x,y]; v=random.randint(-7,7); pix[x,y]=tuple(max(0,min(255,a+v)) for a in c)
    im.save(TEX/('wallpaper_'+name+'.jpg'),quality=94)
# Original carpet pattern with woven texture and nested botanical borders.
im=Image.new('RGB',(1024,1536),(85,37,31)); d=ImageDraw.Draw(im)
colors=[(33,53,61),(191,153,96),(91,47,39),(187,158,106),(38,66,72)]
for pad,c in zip([18,34,50,70,102],colors):
    d.rectangle((pad,pad,1023-pad,1535-pad),outline=c,width=14)
for y in range(142,1450,96):
    for x in range(146,910,96):
        off=42 if (y//96)%2 else 0; xx=x+off
        d.polygon([(xx,y-23),(xx+18,y),(xx,y+23),(xx-18,y)],fill=(156,118, 70))
        for dx,dy in [(0,-31),(0,31),(-26,0),(26,0)]: d.ellipse((xx+dx-4,y+dy-7,xx+dx+4,y+dy+7),fill=(185,154,104))
for r,c in [(275,(189,154,104)),(256,(37,60,66)),(212,(155,83,55)),(190,(175,141,86)),(160,(33,61,66))]:
    d.polygon([(512,768-r*1.65),(512+r,768),(512,768+r*1.65),(512-r,768)],fill=c)
for a in range(16):
    t=a*math.tau/16; x=512+math.cos(t)*90;y=768+math.sin(t)*145
    d.ellipse((x-13,y-23,x+13,y+23),fill=(192,159,106))
d.ellipse((475,714,549,822),fill=(165,91,57))
pix=im.load()
for y in range(1536):
    for x in range(1024):
        c=pix[x,y]; v=random.randint(-8,8)+(3 if x%3==0 else -2); pix[x,y]=tuple(max(0,min(255,a+v)) for a in c)
im.save(TEX/'oriental_rug.jpg',quality=94)
# Original landscape painting for the frames.
im=Image.new('RGB',(1024,640),(190,205,205)); d=ImageDraw.Draw(im)
for y in range(640):
    col=(int(172+y*.07),int(191+y*.04),int(192-y*.025)) if y<360 else (88,109,76)
    d.line((0,y,1024,y),fill=col)
for i in range(5):
    pts=[(0,640)]+[(x,340+i*40+math.sin(x/140+i)*35+random.random()*18) for x in range(0,1050,25)]+[(1024,640)]
    d.polygon(pts,fill=(110-i*10,128-i*9,105-i*10))
for i in range(35):
    x=random.randrange(1024);y=random.randrange(340,590);r=random.randrange(12,50)
    d.line((x,y,x,y-r*2),fill=(66,61,43),width=4);d.ellipse((x-r,y-r*3,x+r,y-r),fill=(65,85+random.randrange(25),57))
im=im.filter(ImageFilter.GaussianBlur(1.2)); im.save(TEX/'landscape_painting.jpg',quality=93)
print(json.dumps({'downloaded_PBR_sets':list(manifest),'original_patterns':['sage','blue','ivory','oriental_rug','landscape_painting'],'output':str(TEX)},ensure_ascii=False))
