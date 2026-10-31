"""GLB is an exchange deliverable; runtime uses the documented LVH format."""
import bpy,sys,json
from pathlib import Path
import io_scene_gltf2
ROOT=Path(__file__).resolve().parents[2]
out=ROOT/'assets'/'exchange';out.mkdir(exist_ok=True)
props=bpy.ops.export_scene.gltf.get_rna_type().properties
targets=[('LVH_Vault','vault.glb')]
if 'LVH_AnimatedThief' not in bpy.data.scenes:targets.append(('LVH_Thief','thief.glb'))
for scene_name,filename in targets:
 scene=bpy.data.scenes[scene_name];bpy.context.window.scene=scene
 for obj in bpy.context.view_layer.objects:obj.select_set(False)
 objects=[o for o in scene.objects if o.type in ('MESH','EMPTY','ARMATURE')]
 for obj in objects:obj.select_set(True)
 bpy.context.view_layer.objects.active=objects[0]
 rig=next((o for o in objects if o.type=='ARMATURE'),None)
 if rig:
  rig.data.pose_position=next(e.identifier for e in rig.data.bl_rna.properties['pose_position'].enum_items if e.identifier=='POSE')
  rig.animation_data.action=bpy.data.actions['Idle']
  if len(rig.animation_data.action.slots):rig.animation_data.action_slot=rig.animation_data.action.slots[0]
 scene.frame_set(0)
 fmt=next(item[0] for item in io_scene_gltf2.get_format_items(scene,bpy.context) if item[0]=='GLB')
 mode=next(e.identifier for e in props['export_animation_mode'].enum_items if e.identifier=='ACTIONS')
 options={'filepath':str(out/filename),'export_format':fmt,'use_selection':True,'use_active_scene':True,'export_animations':True,'export_animation_mode':mode,'export_force_sampling':True,'export_yup':True,'export_apply':False,'export_skins':True}
 options={k:v for k,v in options.items() if k in props}
 bpy.ops.export_scene.gltf(**options)
 if rig:
  rig.animation_data.action=None
  rig.data.pose_position=next(e.identifier for e in rig.data.bl_rna.properties['pose_position'].enum_items if e.identifier=='REST')
 print('Exchange export:',filename,(out/filename).stat().st_size,'bytes')

if "LVH_AnimatedThief" in bpy.data.scenes:
 p=ROOT/"tools/blender/export_animated_exchange.py"
 exec(compile(p.read_text(),str(p),"exec"),{"__file__":str(p),"__name__":"__main__"})
