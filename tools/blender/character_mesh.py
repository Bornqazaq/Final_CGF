"""Continuous garment/body lofts with explicit normalized skin weights."""
import math,bpy
from mathutils import Vector
from common import face_mesh
def weighted(o,fn):
 groups={}
 for vertex in o.data.vertices:
  weights=fn(vertex.co);total=sum(weights.values())
  for name,value in weights.items():
   if value<=0:continue
   if name not in groups:groups[name]=o.vertex_groups.new(name=name)
   groups[name].add([vertex.index],value/total,'REPLACE')
 for p in o.data.polygons:p.use_smooth=True
 return o
def torso_weights(v):
 z=v.z
 if z<1.03:return {'Pelvis':1}
 if z<1.22:
  t=(z-1.03)/.19;return {'Spine':1-t,'Chest':t}
 return {'Chest':1}
def loft(name,rings,mat,weight_fn,segments=24,open_front=0):
 verts=[];uvs=[];faces=[];span=2*math.pi-open_front*2;n=segments if open_front==0 else segments+1
 for j,(z,rx,ry,cx,cy) in enumerate(rings):
  for i in range(n):
   a=-math.pi/2+open_front+span*i/segments;wrinkle=1+.012*math.sin(i*2.3+j*1.8)
   verts.append((cx+rx*math.cos(a)*wrinkle,cy+ry*math.sin(a)*wrinkle,z));uvs.append((i/segments,j/max(1,len(rings)-1)))
 for j in range(len(rings)-1):
  for i in range(segments if not open_front else n-1):
   k=(i+1)%n;faces.append((j*n+i,j*n+k,(j+1)*n+k,(j+1)*n+i))
 if not open_front:
  faces.append(tuple(reversed(range(n))));faces.append(tuple((len(rings)-1)*n+i for i in range(n)))
 return weighted(face_mesh(name,verts,faces,mat,uvs),weight_fn)
def tube(name,centers,radii,mat,weight_fn,sides=16):
 verts=[];uvs=[];faces=[];points=[Vector(c) for c in centers]
 for j,p in enumerate(points):
  direction=(points[min(j+1,len(points)-1)]-points[max(j-1,0)]).normalized()
  reference=Vector((0,0,1)) if abs(direction.z)<.9 else Vector((0,1,0))
  a=direction.cross(reference).normalized();b=direction.cross(a).normalized()
  ra,rb=radii[j] if isinstance(radii[j],tuple) else (radii[j],radii[j])
  for k in range(sides):
   theta=math.tau*k/sides;v=p+a*math.cos(theta)*ra+b*math.sin(theta)*rb
   verts.append(tuple(v));uvs.append((k/sides,j/(len(points)-1)))
 for j in range(len(points)-1):
  for k in range(sides):
   q=(k+1)%sides;faces.append((j*sides+k,j*sides+q,(j+1)*sides+q,(j+1)*sides+k))
 faces.append(tuple(reversed(range(sides))));faces.append(tuple((len(points)-1)*sides+k for k in range(sides)))
 return weighted(face_mesh(name,verts,faces,mat,uvs),weight_fn)
def constant(name):return lambda v:{name:1}
def arm_weights(side):
 def fn(v):
  x=abs(v.x)
  if x<.25:
   t=max(0,min(1,(x-.17)/.08));return {'Chest':1-t,'UpperArm.'+side:t}
  t=max(0,min(1,(x-.47)/.09));return {'UpperArm.'+side:1-t,'Forearm.'+side:t}
 return fn
def leg_weights(side):
 def fn(v):
  if v.z<.25:
   t=max(0,min(1,(v.z-.14)/.11));return {'Foot.'+side:1-t,'Shin.'+side:t}
  if v.z>.85:
   t=max(0,min(1,(v.z-.85)/.13));return {'Pelvis':t,'Thigh.'+side:1-t}
  t=max(0,min(1,(v.z-.43)/.12));return {'Thigh.'+side:t,'Shin.'+side:1-t}
 return fn
