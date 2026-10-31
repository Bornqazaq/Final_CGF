"""Versioned native runtime export. Axes: Blender XYZ -> runtime X,Z,-Y."""
import bpy, struct, json, hashlib
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[2]
C=Matrix(((1,0,0,0),(0,0,1,0),(0,-1,0,0),(0,0,0,1)))
def export(scene,output='vault.scene'):
 out=ROOT/'assets';(out/'meshes').mkdir(exist_ok=True)
 deps=bpy.context.evaluated_depsgraph_get();lines=['# LVH scene format version 1; metres; right handed Y up']
 objects=[o for o in scene.objects if o.type in ('MESH','EMPTY')]
 ordered=[]
 def visit(o):
  if o in ordered:return
  if o.parent and o.parent in objects:visit(o.parent)
  ordered.append(o)
 for o in objects:visit(o)
 mats=[]
 for o in ordered:
  if o.type=='MESH':
   for m in o.data.materials:
    if m and m not in mats:mats.append(m)
 for m in mats:
  color=m.get('color',[1,1,1]);lines.append('material '+json.dumps(m.name)+' '+' '.join(str(v) for v in color)+f" {m.get('specular',.2)} {m.get('shine',32)} {m.get('emission',0)} "+json.dumps(m.get('texture','-')))
 records=[];mesh_count=0;cache={}
 for o in ordered:
  if o.type!='MESH':records.append((o,-1,0));continue
  evaluated=o.evaluated_get(deps);me=evaluated.to_mesh();me.calc_loop_triangles()
  uv=me.uv_layers.active;verts=[];indices=[]
  # Room pieces use a single material; character export splits material objects.
  for triangle in me.loop_triangles:
   for li in triangle.loops:
    vi=me.loops[li].vertex_index;p=C@me.vertices[vi].co;n=C.to_3x3()@me.corner_normals[li].vector;t=uv.data[li].uv if uv else (0,0)
    verts.append((*p,*n,*t,0,0,0,0,0,0,0,0));indices.append(len(indices))
  blob=struct.pack('<4sIII',b'LVHM',1,len(verts),len(indices))+b''.join(struct.pack('<16f',*v) for v in verts)+struct.pack('<'+'I'*len(indices),*indices)
  key=hashlib.sha256(blob).digest()
  if key in cache:mi=cache[key]
  else:
   mi=mesh_count;cache[key]=mi
   name=f'{output.split(".")[0]}_{mi:04}.lvhm';(out/'meshes'/name).write_bytes(blob)
   lines.append('mesh '+json.dumps(o.name)+' '+json.dumps('meshes/'+name));mesh_count+=1
  mat=o.data.materials[0] if o.data.materials else mats[0]
  records.append((o,mi,mats.index(mat)));evaluated.to_mesh_clear()

 for o,mi,material in records:
  parent_index=ordered.index(o.parent) if o.parent in ordered else -1
  local=(o.parent.matrix_world.inverted()@o.matrix_world) if parent_index>=0 else o.matrix_world
  local=C@local@C.inverted()
  flags=int(bool(o.get('dynamic',False)))+2*int(bool(o.get('screen',False)))
  p=o.parent
  while p:
   if p.get('dynamic',False):flags|=1
   p=p.parent
  values=[local[r][c] for c in range(4) for r in range(4)]
  lines.append('node '+json.dumps(o.name)+f' {parent_index} {mi} {material} {flags} '+' '.join(f'{v:.7g}' for v in values))
 (out/output).write_text('\n'.join(lines)+'\n',encoding='utf-8')
 print('Exported',output,mesh_count,'meshes',len(ordered),'nodes')
