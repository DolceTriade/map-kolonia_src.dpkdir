"""Blender: reshape existing cave skins; preserve their openings and closed backs."""
import bpy,bmesh,numpy as np,json,math,collections
from pathlib import Path
from mathutils import Vector
S=Path(__file__).resolve().parents[1];D=S/'devassets/cave-renewal';W=D/'build';W.mkdir(parents=True,exist_ok=True)
def read_obj(path):
 vertices=[];uvs=[];normals=[];groups=[]
 for line in path.read_text().splitlines():
  a=line.split()
  if not a:continue
  if a[0]=='v':vertices.append(tuple(map(float,a[1:4])))
  elif a[0]=='vt':uvs.append(tuple(map(float,a[1:3])))
  elif a[0]=='vn':normals.append(tuple(map(float,a[1:4])))
  elif a[0]=='g':groups.append(dict(name=' '.join(a[1:]),faces=[]))
  elif a[0]=='usemtl':groups[-1]['material']=a[1]
  elif a[0]=='f':groups[-1]['faces'].append([tuple(int(k)-1 for k in q.split('/')) for q in a[1:]])
 return np.array(vertices),np.array(uvs),np.array(normals),groups
ns={'read_obj':read_obj}
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
rooms=json.loads((D/'rooms.json').read_text());meta={};report=[]
def warp(points,room):
 p=np.array(points,float).copy();o=np.array(list(map(float,room['origin'].split())));v=p-o;x,y,z=v.T;z=z+o[2];h=room['height'];a,b=room['extent']
 # Keep door thresholds and their surrounding jambs fixed, and fade deformation
 # in above the doors. The surrounding structural shell is never moved.
 rho=np.maximum(abs(x)/a,abs(y)/b);door=np.maximum(np.clip((240-abs(x))/64,0,1),np.clip((240-abs(y))/64,0,1))*np.clip((rho-.65)/.2,0,1)*np.clip((270-z)/50,0,1)
 strength=1-door;phase=room['entity']*.71;vertical=np.sin(np.pi*np.clip(z/h,0,1))
 radial=np.maximum(1,np.sqrt(x*x+y*y));bulge=strength*vertical*np.clip((rho-.4)/.35,0,1)*(12+10*np.sin(y/170+z/135+phase)*np.cos(x/190))
 p[:,0]-=bulge*x/radial
 p[:,1]-=bulge*y/radial
 ceiling=np.clip((z-240)/(h-240),0,1)**2
 p[:,2]+=-strength*ceiling*(20+14*np.sin(x/190+phase)*np.cos(y/170)+7*np.sin((x+y)/95))
 return p

def make(name,v,faces,uvs,materials,matids):
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(v,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o)
 for name in materials:
  m=bpy.data.materials.get(name) or bpy.data.materials.new(name);mesh.materials.append(m)
 layer=mesh.uv_layers.new(name='UVMap')
 for p,uv,mi in zip(mesh.polygons,uvs,matids):
  p.material_index=mi;p.use_smooth=True
  for li,t in zip(p.loop_indices,uv):layer.data[li].uv=t
 return o

def export(path,objects):
 out=['mtllib kolonia.mtl'];vi=1
 for o in objects:
  m=o.data;m.calc_loop_triangles();uv=m.uv_layers.active;out.append('g '+o.name);last=None
  for tri in m.loop_triangles:
   mat=m.materials[tri.material_index].name
   if mat!=last:out.append('usemtl '+mat);last=mat
   ids=[]
   for li in tri.loops:
    loop=m.loops[li];p=o.matrix_world@m.vertices[loop.vertex_index].co;n=m.corner_normals[li].vector;t=uv.data[li].uv
    out.extend([f'v {p.x:.7f} {p.z:.7f} {-p.y:.7f}',f'vt {t.x:.7f} {t.y:.7f}',f'vn {n.x:.7f} {n.z:.7f} {-n.y:.7f}']);ids.append(f'{vi}/{vi}/{vi}');vi+=1
   out.append('f '+' '.join(ids))
 path.write_text('\n'.join(out)+'\n')
for room in rooms:
 path=S/room['model'];v,uv,norm,groups=ns['read_obj'](path);engine=v[:,[0,2,1]].copy();engine[:,1]*=-1
 rock=[g for g in groups if g['name'].startswith(('Layered_wet_limestone','Moss_colonisation_pockets','Low_wet_cave_vault'))]
 allids=np.unique([q[0] for g in rock for f in g['faces'] for q in f]);ext=np.max(abs(engine[allids,:2]),axis=0);vault=[q[0] for g in rock if g['name'].startswith('Low_wet_cave_vault') for f in g['faces'] for q in f];h=float(np.percentile(engine[vault if vault else allids,2]+64,98));room['height']=max(300,h);room['extent']=ext.tolist();meta[path.name]=room
 origin=np.array(list(map(float,room['origin'].split())));changed=warp(engine+origin,room)-origin;objects=[];before=0;after=0
 # Weld front, backing, and rim positions before reducing geometry, keeping the
 # closed shell intact instead of decimating disconnected front sheets.
 for skin,selected in [('Rock_skin',rock),('Soft_details',[g for g in groups if g not in rock])]:
  if not selected:continue
  positions=[];faces=[];tex=[];mats=[];mis=[];lookup={}
  for g in selected:
   for face in g['faces']:
    ids=[];tt=[];center=changed[[q[0] for q in face]].mean(0)
    material=g['material']
    if skin=='Rock_skin':
     # Keep the existing scan as the main rock; moss uses the aerial scan.
     if 'Moss_' in g['name']:material='textures/kolonia/cave_aerial'
     elif math.sin(center[0]/210+room['entity'])*math.cos(center[1]/230+center[2]/160)>.38:material='textures/kolonia/cave_fracture'
     else:material='textures/kolonia/cave_base'
    if material not in mats:mats.append(material)
    for vi,ti,ni in face:
     p=changed[vi];key=tuple(p.round(6))
     if key not in lookup:lookup[key]=len(positions);positions.append(p)
     ids.append(lookup[key]);t=uv[ti].copy()
     if material=='textures/kolonia/cave_fracture':
      # Tilt the layered scan to follow dipping rock rather than a brick grid.
      ang=.32;c=math.cos(ang);ss=math.sin(ang);t=np.array([c*t[0]-ss*t[1],ss*t[0]+c*t[1]])*2
     tt.append(t)
    faces.append(ids);tex.append(tt);mis.append(mats.index(material))
  o=make(path.stem+'_'+skin,positions,faces,tex,mats,mis);before+=len(faces)
  if skin=='Rock_skin':
   bpy.context.view_layer.objects.active=o;o.select_set(True);mod=o.modifiers.new('Efficient_large_forms','DECIMATE');mod.ratio=.48;mod.use_collapse_triangulate=True;bpy.ops.object.modifier_apply(modifier=mod.name);o.select_set(False)
   bm=bmesh.new();bm.from_mesh(o.data);assert all(len(e.link_faces)==2 for e in bm.edges),(path.name,'nonclosed rock shell');bm.free()
  after+=sum(len(p.vertices)-2 for p in o.data.polygons);objects.append(o)
 export(path.with_name(path.stem+'_organic.obj'),objects)
 # Place the editable source at its actual map location.
 for o in objects:o.location=origin
 report.append({'model':path.name,'before_triangles':before,'after_triangles':after});print(report[-1],flush=True)
(W/'room-meta.json').write_text(json.dumps(meta));(W/'art-report.json').write_text(json.dumps(report,indent=2))
# Transform the original, already fitted collision cells. Keep their support
# directions instead of constructing hundreds of tiny bevel planes.
newclips=[]
for cell in json.loads((D/'old-clips.json').read_text()):
 room=meta[cell['model']];points=np.array(cell['points']);center=points.mean(0);eps=.1;J=np.column_stack([(warp([center+np.eye(3)[i]*eps],room)[0]-warp([center-np.eye(3)[i]*eps],room)[0])/(2*eps) for i in range(3)]);B=J@np.diag(1+2/np.maximum(np.ptp(points,axis=0),2));inv=np.linalg.inv(B);destination=warp([center],room)[0];planes=[]
 for row in cell['planes']:
  row=np.array(row);raw=row[:3]@inv;L=np.linalg.norm(raw);n=raw/L;d=(row[3]-row[:3]@center)/L+n@destination;planes.append([*n,d])
 newclips.append({'brush':cell['brush'],'model':cell['model'],'planes':planes})
(W/'new-clips.json').write_text(json.dumps(newclips));bpy.ops.wm.save_as_mainfile(filepath=str(D/'caves.blend'),compress=True);print('ALL CAVE ART COMPLETE',flush=True)
