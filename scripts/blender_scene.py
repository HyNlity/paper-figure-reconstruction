"""Small deterministic backend; use custom builder for complex scientific geometry."""
import bpy,math,json,sys,argparse
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--spec',required=True);p.add_argument('--out',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);sp=Path(a.spec);s=json.loads(sp.read_text());cfg=s.get('scene',{});out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
if cfg.get('base_blend'):
 bpy.ops.wm.open_mainfile(filepath=str((sp.parent/cfg['base_blend']).resolve()))
 if cfg.get('scene_name'):bpy.context.window.scene=bpy.data.scenes[cfg['scene_name']]
else:
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;objects={}
def linear(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
for o in cfg.get('objects',[]):
 assert o['id'] not in bpy.data.objects,'Object ID collision: '+o['id']
 op={'cube':bpy.ops.mesh.primitive_cube_add,'sphere':bpy.ops.mesh.primitive_uv_sphere_add,'cylinder':bpy.ops.mesh.primitive_cylinder_add,'cone':bpy.ops.mesh.primitive_cone_add}[o['type']];op();ob=bpy.context.object;ob.name=o['id'];ob.location=o.get('location',[0,0,0]);ob.rotation_euler=[math.radians(v) for v in o.get('rotation_degrees',[0,0,0])];ob.scale=o.get('scale',[1,1,1]);objects[o['id']]=ob
 mat=bpy.data.materials.new(o['id']+' material');mat.use_nodes=True;n=mat.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(*[linear(v) for v in o.get('color',[.4,.5,.8])],1);n.inputs['Roughness'].default_value=o.get('roughness',.4);ob.data.materials.append(mat)
for o in cfg.get('objects',[]):
 if o.get('parent'):objects[o['id']].parent=objects[o['parent']]
ca=cfg.get('camera',{});bpy.ops.object.camera_add(location=ca.get('location',[6,-8,6]));cam=bpy.context.object;cam.name='PFR Camera';cam.rotation_euler=(Vector(ca.get('target',[0,0,0]))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type=ca.get('type','ORTHO');cam.data.ortho_scale=ca.get('ortho_scale',6);scene.camera=cam
for light in cfg.get('lights',[{'location':[3,-4,6],'energy':700,'size':5}]):
 bpy.ops.object.light_add(type='AREA',location=light['location']);ob=bpy.context.object;ob.data.energy=light['energy'];ob.data.shape='DISK';ob.data.size=light['size'];ob.rotation_euler=(-ob.location).to_track_quat('-Z','Y').to_euler()
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=cfg.get('samples',32);scene.cycles.use_denoising=True;scene.render.resolution_x=s['canvas']['width'];scene.render.resolution_y=s['canvas']['height'];scene.render.resolution_percentage=100;scene.render.film_transparent=cfg.get('transparent',True);scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.render.filepath=str(out/'render.png');bpy.ops.wm.save_as_mainfile(filepath=str(out/'figure.blend'));bpy.ops.render.render(write_still=True)
(out/'blender-manifest.json').write_text(json.dumps({'version':bpy.app.version_string,'objects':[{'id':ob.name,'type':ob.type} for ob in scene.objects],'images':[im.filepath for im in bpy.data.images if im.source=='FILE']},indent=2))
