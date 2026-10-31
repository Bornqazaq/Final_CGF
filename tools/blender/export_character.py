"""Export indexed skin meshes and sampled local TRS animation with inverse binds."""
import bpy,struct,json
from pathlib import Path
from mathutils import Matrix
from character_rig import pose
ROOT=Path(__file__).resolve().parents[2]
C=Matrix(((1,0,0,0),(0,0,1,0),(0,-1,0,0),(0,0,0,1)))
def write_string(f,value):
 b=value.encode('utf-8');f.write(struct.pack('<I',len(b)));f.write(b)
def matrix_values(m):return [m[r][c] for c in range(4) for r in range(4)]
def export(scene,rig,objects,clips):
 out=ROOT/'assets';(out/'meshes').mkdir(exist_ok=True)
 bones=list(rig.data.bones);bone_names=[b.name for b in bones]
 mats=[]
 for o in objects:
  for m in o.data.materials:
   if m not in mats:mats.append(m)
 lines=['# LVH character scene v1; vertices are in rig bind space']
 for m in mats:
  lines.append('material '+json.dumps(m.name)+' '+' '.join(str(v) for v in m.get('color',[1,1,1]))+f" {m.get('specular',.2)} {m.get('shine',32)} {m.get('emission',0)} "+json.dumps(m.get('texture','-')))
 rig.data.pose_position=next(e.identifier for e in rig.data.bl_rna.properties['pose_position'].enum_items if e.identifier=='REST')
 bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();records=[];total_triangles=0
 for mi,o in enumerate(objects):
  evaluated=o.evaluated_get(deps);mesh=evaluated.to_mesh();mesh.calc_loop_triangles();uv=mesh.uv_layers.active;verts=[];indices=[]
  normal_matrix=(C@o.matrix_world).to_3x3().inverted().transposed()
  group_names={g.index:g.name for g in o.vertex_groups}
  for triangle in mesh.loop_triangles:
   for li in triangle.loops:
    vi=mesh.loops[li].vertex_index;v=mesh.vertices[vi];p=C@o.matrix_world@v.co;n=(normal_matrix@mesh.corner_normals[li].vector).normalized();t=uv.data[li].uv if uv else (0,0)
    pairs=sorted([(g.weight,bone_names.index(group_names[g.group])) for g in v.groups if group_names.get(g.group) in bone_names],reverse=True)[:4]
    if not pairs:pairs=[(1,0)]
    total=sum(w for w,i in pairs);weights=[w/total for w,i in pairs]+[0]*(4-len(pairs));joints=[i for w,i in pairs]+[0]*(4-len(pairs))
    verts.append((*p,*n,*t,*weights,*joints));indices.append(len(indices))
  filename=f'thief_{mi:03}.lvhm'
  with (out/'meshes'/filename).open('wb') as f:
   f.write(struct.pack('<4sIII',b'LVHM',1,len(verts),len(indices)))
   for v in verts:f.write(struct.pack('<16f',*v))
   f.write(struct.pack('<'+'I'*len(indices),*indices))
  total_triangles+=len(indices)//3
  lines.append('mesh '+json.dumps(o.name)+' '+json.dumps('meshes/'+filename));records.append((o.name,mi,mats.index(o.data.materials[0])));evaluated.to_mesh_clear()
 for name,mi,mat in records:lines.append('node '+json.dumps(name)+f' -1 {mi} {mat} 4 '+' '.join(str(v) for v in matrix_values(Matrix.Identity(4))))
 (out/'thief.scene').write_text('\n'.join(lines)+'\n',encoding='utf-8')
 with (out/'thief.lvanim').open('wb') as f:
  f.write(struct.pack('<4sIII',b'LVHA',1,len(bones),len(clips)))
  for b in bones:
   write_string(f,b.name);f.write(struct.pack('<i',bones.index(b.parent) if b.parent else -1))
   inv=C@b.matrix_local.inverted()@C.inverted();f.write(struct.pack('<16f',*matrix_values(inv)))
  rig.data.pose_position=next(e.identifier for e in rig.data.bl_rna.properties['pose_position'].enum_items if e.identifier=='POSE')
  rig.animation_data.action=None
  for name,length in clips:
   write_string(f,name);f.write(struct.pack('<fI',length/24,length+1))
   for frame in range(length+1):
    pose(rig,name,frame/length);bpy.context.view_layer.update()
    for bone in bones:
     pb=rig.pose.bones[bone.name];local=pb.parent.matrix.inverted()@pb.matrix if pb.parent else pb.matrix
     local=C@local@C.inverted();t,q,s=local.decompose();f.write(struct.pack('<10f',*t,q.x,q.y,q.z,q.w,*s))
 rig.data.pose_position=next(e.identifier for e in rig.data.bl_rna.properties['pose_position'].enum_items if e.identifier=='REST')
 (ROOT/'evidence'/'character-export.json').write_text(json.dumps({'triangles':total_triangles,'bones':len(bones),'clips':[c[0] for c in clips],'max_influences':4,'axis_conversion':'x,z,-y'},indent=2))
 print('Character export:',total_triangles,'triangles; normalized skin weights; five sampled clips')
