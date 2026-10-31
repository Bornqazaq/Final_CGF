"""Original T-pose rig and five authored actions; no imported motion."""
import bpy,math
from mathutils import Vector,Matrix
def create_rig():
 arm=bpy.data.armatures.new('ThiefSkeleton');rig=bpy.data.objects.new('ThiefRig',arm);bpy.context.scene.collection.objects.link(rig)
 bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
 definitions=[('Root',(0,0,0),(0,0,.15),None),('Pelvis',(0,0,.92),(0,0,1.03),'Root'),('Spine',(0,0,1.03),(0,0,1.23),'Pelvis'),('Chest',(0,0,1.23),(0,0,1.44),'Spine'),('Neck',(0,0,1.44),(0,0,1.55),'Chest'),('Head',(0,0,1.55),(0,0,1.79),'Neck')]
 for side,s in [('L',1),('R',-1)]:
  definitions += [('Shoulder.'+side,(s*.07,0,1.42),(s*.24,0,1.42),'Chest'),('UpperArm.'+side,(s*.24,0,1.42),(s*.52,0,1.42),'Shoulder.'+side),('Forearm.'+side,(s*.52,0,1.42),(s*.77,0,1.42),'UpperArm.'+side),('Hand.'+side,(s*.77,0,1.42),(s*.91,0,1.42),'Forearm.'+side),('Thigh.'+side,(s*.12,0,.92),(s*.12,0,.48),'Pelvis'),('Shin.'+side,(s*.12,0,.48),(s*.12,0,.13),'Thigh.'+side),('Foot.'+side,(s*.12,0,.13),(s*.12,-.18,.06),'Shin.'+side)]
 for name,head,tail,parent in definitions:
  bone=arm.edit_bones.new(name);bone.head=head;bone.tail=tail
  if parent:bone.parent=arm.edit_bones[parent]
 bpy.ops.object.mode_set(mode='OBJECT');rig.show_in_front=True
 return rig
def rotation(rig,name,matrix):
 bone=rig.pose.bones[name];basis=rig.data.bones[name].matrix_local.to_3x3()
 bone.rotation_mode='QUATERNION';bone.rotation_quaternion=(basis.inverted()@matrix.to_3x3()@basis).to_quaternion()
def pose(rig,state,phase):
 for p in rig.pose.bones:p.location=(0,0,0);p.rotation_mode='QUATERNION';p.rotation_quaternion=(1,0,0,0);p.scale=(1,1,1)
 crouch=state in ('CrouchIdle','CrouchWalk');walk=state in ('Walk','CrouchWalk');breath=.005*math.sin(phase*math.tau)
 root_y=.08 if crouch else 0
 root_z=-.40 if crouch else -.07 if walk else -.004*(.5+.5*math.sin(phase*math.tau))
 root=rig.pose.bones['Root'];root.location=rig.data.bones['Root'].matrix_local.to_3x3().inverted()@Vector((0,root_y,root_z))
 rotation(rig,'Spine',Matrix.Rotation(math.radians(40 if crouch else 1),4,'X'))
 rotation(rig,'Chest',Matrix.Rotation(math.radians(25 if crouch else -1),4,'X'))
 rotation(rig,'Neck',Matrix.Rotation(math.radians(-35 if crouch else 0),4,'X'))
 for side,s in [('L',1),('R',-1)]:
  cycle=phase*math.tau+(0 if s==1 else math.pi);swing=math.sin(cycle)
  # Analytic two-link legs follow a planted stance and lifted swing.
  # A stance foot moves backward locally at exactly one stride per cycle.
  u=(phase+(0 if s==1 else .5))%1;stride=.75 if crouch else 1.2
  foot_y=0;foot_z=.13
  if walk:
   if u<.5:foot_y=-stride*.25+stride*u
   else:
    q=(u-.5)*2;smooth=q*q*(3-2*q)
    foot_y=stride*.25-stride*.5*smooth;foot_z+=(.04 if crouch else .10)*math.sin(math.pi*q)
  dy=foot_y-root_y;h=.92+root_z-foot_z
  l1=.44;l2=.35;distance=max(.091,min(l1+l2-.00001,math.sqrt(h*h+dy*dy)))
  knee=math.acos(max(-1,min(1,(distance*distance-l1*l1-l2*l2)/(2*l1*l2))))
  offset=math.acos(max(-1,min(1,(l1*l1+distance*distance-l2*l2)/(2*l1*distance))))
  thigh=math.atan2(dy,h)-offset
  rotation(rig,'Thigh.'+side,Matrix.Rotation(thigh,4,'X'));rotation(rig,'Shin.'+side,Matrix.Rotation(knee,4,'X'));rotation(rig,'Foot.'+side,Matrix.Rotation(-(thigh+knee),4,'X'))
  swing_arm=(-swing*.25 if walk else .02*math.sin(cycle))
  upper=Matrix.Rotation(swing_arm+(-math.radians(65) if crouch else 0),4,'X')@Matrix.Rotation(s*math.radians(70 if crouch else 78),4,'Y')
  rotation(rig,'UpperArm.'+side,upper)
  # Counter the leaning torso; bend crouched elbows forward instead of spreading arms.
  rotation(rig,'Forearm.'+side,Matrix.Rotation(-s*math.radians(35),4,'Z') if crouch else Matrix.Rotation(-s*math.radians(8),4,'Y'))
 if state=='Interact':
  amount=math.sin(math.pi*phase)
  rotation(rig,'UpperArm.R',Matrix.Rotation(-amount*.9,4,'Z')@Matrix.Rotation(-math.radians(78)+amount*.55,4,'Y'));rotation(rig,'Forearm.R',Matrix.Rotation(amount*.55,4,'Z'))
def animate(rig):
 clips=[('Idle',48),('Walk',24),('CrouchIdle',48),('CrouchWalk',32),('Interact',24)];rig.animation_data_create()
 names={name for name,length in clips}
 for old in list(bpy.data.actions):
  if old.name.split('.')[0] in names and 'duration_frames' in old and old.use_fake_user and old.users<=1:bpy.data.actions.remove(old)
 for name,length in clips:
  action=bpy.data.actions.new(name);action.use_fake_user=True;rig.animation_data.action=action
  for frame in range(0,length+1,2):
   pose(rig,name,frame/length)
   for bone in rig.pose.bones:
    bone.keyframe_insert(data_path='rotation_quaternion',frame=frame,group=bone.name);bone.keyframe_insert(data_path='location',frame=frame,group=bone.name)
  action['duration_frames']=length;action['lvh_source']='LaserVaultHeist'
 rig.animation_data.action=None;pose(rig,'Idle',0)
 return clips
