"""Measure real evaluated skinning and validate weights, clips and foot contact."""
import bpy,json,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'/'blender'))
from character_rig import pose
scene=bpy.data.scenes['LVH_Thief'];bpy.context.window.scene=scene;rig=next(o for o in scene.objects if o.type=='ARMATURE')
rig.data.pose_position=next(e.identifier for e in rig.data.bl_rna.properties['pose_position'].enum_items if e.identifier=='POSE')
result={'poses':{},'weight_errors':0,'max_weights':0}
for ob in scene.objects:
 if ob.type!='MESH':continue
 for vertex in ob.data.vertices:
  weights=[g.weight for g in vertex.groups];result['max_weights']=max(result['max_weights'],len(weights))
  if not weights or abs(sum(weights)-1)>1e-4:result['weight_errors']+=1
for clip in ['Idle','Walk','CrouchIdle','CrouchWalk','Interact']:
 bounds=[]
 for phase in [0,.125,.25,.375,.5,.625,.75,.875]:
  pose(rig,clip,phase);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();zs=[]
  for ob in scene.objects:
   if ob.type=='MESH':
    ev=ob.evaluated_get(deps);zs.extend((ev.matrix_world@Vector(v)).z for v in ev.bound_box)
  bounds.append([round(min(zs),4),round(max(zs),4)])
 result['poses'][clip]=bounds
rig.data.pose_position=next(e.identifier for e in rig.data.bl_rna.properties['pose_position'].enum_items if e.identifier=='REST')
(ROOT/'evidence'/'character-pose-bounds.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result))
