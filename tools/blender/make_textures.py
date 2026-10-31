"""Original painted/procedural albedo textures; no downloaded texture assets."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import random, math
root=Path(__file__).resolve().parents[2]
out=root/'assets'/'textures';out.mkdir(parents=True,exist_ok=True)
rng=random.Random(2718)
def save(im,name):im.save(out/(name+'.png'))
def grain(name,base):
 im=Image.new('RGB',(512,512),base);d=ImageDraw.Draw(im)
 for i in range(260):
  y=rng.randrange(512);shade=rng.randint(-20,20);c=tuple(max(0,min(255,v+shade)) for v in base)
  pts=[(x,y+5*math.sin(x*.014+i)+2*math.sin(x*.045+i)) for x in range(-10,530,8)]
  d.line(pts,fill=c,width=rng.randint(1,6))
 for i in range(5):
  x,y=rng.randrange(512),rng.randrange(512)
  for j in range(6):d.arc((x-34-j*8,y-4-j*2,x+34+j*8,y+4+j*2),0,360,fill=tuple(max(0,v-12) for v in base),width=1)
 save(im,name)
grain('wood',(111,70,36));grain('darkwood',(68,41,23))
for name,base in [('stone',(126,113,87)),('plaster',(148,133,102)),('metal',(63,75,67)),('leather',(91,56,36)),('cloth',(58,39,28)),('denim',(86,64,46))]:
 im=Image.new('RGB',(512,512),base);d=ImageDraw.Draw(im)
 for i in range(650):
  x,y=rng.randrange(512),rng.randrange(512);s=rng.randrange(4,60);delta=rng.randint(-5,5)
  c=tuple(max(0,v+delta) for v in base);d.polygon([(x,y),(x+s,y-6),(x+s+8,y+s//3),(x+5,y+s//2)],fill=c)
 if name in ('cloth','denim'):
  for y in range(0,512,4):d.line((0,y,511,y),fill=tuple(v+3 for v in base))
 save(im.filter(ImageFilter.GaussianBlur(3.5)),name)
im=Image.new('RGB',(768,1024),(83,34,28));d=ImageDraw.Draw(im)
for inset,col in [(12,(139,91,47)),(26,(47,45,36)),(42,(151,107,61)),(60,(91,48,33)),(82,(148,106,59)),(91,(43,39,30))]:
 d.rectangle((inset,inset,767-inset,1023-inset),outline=col,width=6)
for y in range(116,940,85):
 for x in range(115,690,86):
  d.polygon([(x,y-20),(x+17,y),(x,y+20),(x-17,y)],outline=(133,87,49),width=3)
for r in range(220,15,-18):
 col=(136,92,53) if (r//18)%2 else (56,48,35)
 d.polygon([(384,512-r*1.4),(384+r,512),(384,512+r*1.4),(384-r,512)],outline=col,width=5)
for i in range(8000):
 x,y=rng.randrange(768),rng.randrange(1024);v=im.getpixel((x,y));d.point((x,y),fill=tuple(max(0,n-rng.randrange(3,18)) for n in v))
save(im,'rug')
im=Image.new('RGB',(512,512),(108,117,109));d=ImageDraw.Draw(im)
d.rectangle((0,0,511,240),fill=(176,147,95));d.ellipse((320,40,405,125),fill=(223,190,119))
for layer,color in [(0,(109,116,97)),(1,(77,95,82)),(2,(48,73,66)),(3,(34,54,47))]:
 pts=[(0,512)]+[(x,205+layer*57+40*math.sin(x*.012+layer*2)) for x in range(0,520,15)]+[(512,512)]
 d.polygon(pts,fill=color)
for x,y in [(85,280),(185,325),(360,290),(440,375)]:
 d.polygon([(x,y-100),(x+34,y),(x-34,y)],fill=(43,59,43));d.rectangle((x-3,y,x+3,y+35),fill=(53,43,30))
save(im,'landscape')
print('Created',len(list(out.glob('*.png'))),'original textures')
