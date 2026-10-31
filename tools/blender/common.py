import bpy, math, random
from mathutils import Vector, Matrix
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
rng=random.Random(84)
def enum_value(owner,prop,name):
 items=owner.bl_rna.properties[prop].enum_items
 return next(item.identifier for item in items if item.identifier==name)
def new_scene(name):
 old=bpy.data.scenes.get(name)
 if old:
  old_objects=list(old.objects)
  if bpy.context.window.scene==old:bpy.context.window.scene=next(s for s in bpy.data.scenes if s!=old)
  bpy.data.scenes.remove(old)
  for o in old_objects:
   if not o.users_scene:bpy.data.objects.remove(o)
 scene=bpy.data.scenes.new(name);bpy.context.window.scene=scene
 scene.unit_settings.system=enum_value(scene.unit_settings,'system','METRIC');scene.unit_settings.scale_length=1
 return scene
def material(name,color,texture=None,spec=.2,shine=32,emission=0):
 m=bpy.data.materials.new('LVH_'+name);m.use_nodes=True
 bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
 bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=max(.15,1-math.sqrt(spec)*.65)
 if 'Metallic' in bs.inputs:bs.inputs['Metallic'].default_value=.6 if name in ('Brass','Metal','MetalEdge') else 0
 if emission:
  bs.inputs['Emission Color'].default_value=(*color,1);bs.inputs['Emission Strength'].default_value=emission
 m['color']=list(color);m['specular']=spec;m['shine']=shine;m['emission']=emission;m['texture']=texture or '-'
 if texture:
  img=bpy.data.images.load(str(ROOT/'assets'/texture),check_existing=False);tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=img;m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
 return m
def assign(o,m):
 if m:o.data.materials.append(m)
 return o
def parent(o,p):
 if p:o.parent=p
 return o
def empty(name,loc=(0,0,0),parent_obj=None):
 o=bpy.data.objects.new(name,None);bpy.context.scene.collection.objects.link(o);o.location=loc;parent(o,parent_obj);return o
def cube(name,loc,size,mat,bevel=.025,parent_obj=None):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=size
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 assign(o,mat);parent(o,parent_obj)
 uv=o.data.uv_layers.active
 for poly in o.data.polygons:
  axis=max(range(3),key=lambda i:abs(poly.normal[i]))
  axes=(1,2) if axis==0 else (0,2) if axis==1 else (0,1)
  for li in poly.loop_indices:
   co=o.data.vertices[o.data.loops[li].vertex_index].co
   uv.data[li].uv=(co[axes[0]]/size[axes[0]]+.5,co[axes[1]]/size[axes[1]]+.5)
 if bevel:
  typ=next(e.identifier for e in bpy.types.Modifier.bl_rna.properties['type'].enum_items if e.identifier=='BEVEL')
  b=o.modifiers.new('Soft crafted edges',typ);b.width=bevel;b.segments=2
 return o
def cyl(name,loc,radius,depth,mat,vertices=20,parent_obj=None,rotation=None,radius2=None):
 if radius2 is None:bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=loc)
 else:bpy.ops.mesh.primitive_cone_add(vertices=vertices,radius1=radius,radius2=radius2,depth=depth,location=loc)
 o=bpy.context.object;o.name=name
 if rotation:o.rotation_euler=rotation
 assign(o,mat);parent(o,parent_obj)
 b=o.modifiers.new('Rounded rims',next(e.identifier for e in bpy.types.Modifier.bl_rna.properties['type'].enum_items if e.identifier=='BEVEL'));b.width=.008;b.segments=2
 return o
def sphere(name,loc,scale,mat,segments=20,rings=12,parent_obj=None):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,radius=1,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;assign(o,mat);parent(o,parent_obj);return o
def torus(name,loc,radius,minor,mat,parent_obj=None,rotation=None):
 bpy.ops.mesh.primitive_torus_add(major_segments=40,minor_segments=10,location=loc,major_radius=radius,minor_radius=minor)
 o=bpy.context.object;o.name=name
 if rotation:o.rotation_euler=rotation
 assign(o,mat);parent(o,parent_obj);return o
def rod(name,a,b,radius,mat,parent_obj=None):
 a,b=Vector(a),Vector(b);o=cyl(name,(a+b)/2,radius,(b-a).length,mat,12,parent_obj)
 o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def light(name,loc,color,power,kind='POINT'):
 d=bpy.data.lights.new(name,enum_value(bpy.types.Light,'type',kind));d.energy=power;d.color=color
 o=bpy.data.objects.new(name,d);bpy.context.scene.collection.objects.link(o);o.location=loc
 return o
def face_mesh(name,verts,faces,mat,uvs=None,parent_obj=None):
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
 o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);assign(o,mat);parent(o,parent_obj)
 layer=mesh.uv_layers.new(name='UVMap')
 for poly in mesh.polygons:
  for k,li in enumerate(poly.loop_indices):
   vi=mesh.loops[li].vertex_index;v=mesh.vertices[vi].co
   layer.data[li].uv=uvs[vi] if uvs else (v.x,v.z)
 return o
