"""Blender: unwrap cave rock charts at the 0.5 reference texel density."""
import bpy,numpy as np,json,math,sys,os
from pathlib import Path
S=Path(__file__).resolve().parents[1];D=S/'devassets/cave-cleanup';W=D/'build';W.mkdir(parents=True,exist_ok=True);origins=json.loads((D/'model-origins.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
report=[]
for source in sorted((S/'models/kolonia').glob('*_organic.obj')):
 lines=source.read_text().splitlines();v=[];uv=[];group='';material='';faces=[];uv_ids=[];mats=[];mi=[];positions=[];lookup={}
 for line in lines:
  a=line.split()
  if not a:continue
  if a[0]=='v':p=np.array(list(map(float,a[1:4])))[[0,2,1]];p[1]*=-1;v.append(p)
  elif a[0]=='vt':uv.append(list(map(float,a[1:3])))
  elif a[0]=='g':group=' '.join(a[1:])
  elif a[0]=='usemtl':material=a[1]
  elif a[0]=='f' and group.endswith('_Rock_skin'):
   ids=[x.split('/') for x in a[1:]];face=[]
   for p in [v[int(x[0])-1] for x in ids]:
    key=tuple(np.round(p,6))
    if key not in lookup:lookup[key]=len(positions);positions.append(p)
    face.append(lookup[key])
   faces.append(face);uv_ids.append([int(x[1])-1 for x in ids])
   if material not in mats:mats.append(material)
   mi.append(mats.index(material))
 mesh=bpy.data.meshes.new(source.stem);mesh.from_pydata(positions,[],faces);mesh.update();o=bpy.data.objects.new(source.stem,mesh);bpy.context.collection.objects.link(o)
 for name in mats:mesh.materials.append(bpy.data.materials.get(name) or bpy.data.materials.new(name))
 mesh.uv_layers.new(name='UVMap')
 for poly,index in zip(mesh.polygons,mi):poly.material_index=index
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(60),island_margin=.008,area_weight=0,correct_aspect=False,scale_to_bounds=False);bpy.ops.object.mode_set(mode='OBJECT');layer=mesh.uv_layers.active
 # Detect real UV islands through shared edges, then equalize physical texel density.
 parent=list(range(len(mesh.polygons)))
 def find(a):
  while parent[a]!=a:parent[a]=parent[parent[a]];a=parent[a]
  return a
 edges={}
 for poly in mesh.polygons:
  ll=list(poly.loop_indices)
  for ia,ib in zip(ll,ll[1:]+ll[:1]):
   a,b=mesh.loops[ia].vertex_index,mesh.loops[ib].vertex_index;key=tuple(sorted((a,b)));tt={a:np.array(layer.data[ia].uv[:]),b:np.array(layer.data[ib].uv[:])}
   for pi,other in edges.get(key,[]):
    if all(np.linalg.norm(tt[v]-other[v])<1e-6 for v in key):parent[find(poly.index)]=find(pi)
   edges.setdefault(key,[]).append((poly.index,tt))
 islands={}
 for poly in mesh.polygons:islands.setdefault(find(poly.index),[]).append(poly)
 for polys in islands.values():
  area3=area2=0
  for p in polys:
   pp=np.array([mesh.vertices[i].co[:] for i in p.vertices]);tt=np.array([layer.data[i].uv[:] for i in p.loop_indices])
   for j in range(1,len(pp)-1):area3+=np.linalg.norm(np.cross(pp[j]-pp[0],pp[j+1]-pp[0]))/2;area2+=abs((tt[j,0]-tt[0,0])*(tt[j+1,1]-tt[0,1])-(tt[j,1]-tt[0,1])*(tt[j+1,0]-tt[0,0]))/2
  if area2<1e-12:continue
  factor=math.sqrt(area3/area2)/1024;center=np.mean([layer.data[i].uv[:] for p in polys for i in p.loop_indices],axis=0)
  for p in polys:
   for li in p.loop_indices:layer.data[li].uv=(np.array(layer.data[li].uv[:])-center)*factor+center
 updates={};bad=0;worst=0
 for poly,indices in zip(mesh.polygons,uv_ids):
  pp=np.array([mesh.vertices[i].co[:] for i in poly.vertices]);tt=np.array([layer.data[i].uv[:] for i in poly.loop_indices]);E=pp[1:]-pp[0]
  if len(pp)==3 and np.linalg.norm(np.cross(E[0],E[1]))>.01:
   sig=np.linalg.svd(np.linalg.pinv(E)@(tt[1:]-tt[0]),compute_uv=False);ratio=sig[0]/max(sig[1],1e-14);worst=max(worst,ratio);bad+=ratio>6
  for index,li in zip(indices,poly.loop_indices):updates[index]=layer.data[li].uv[:]
 ti=0
 for i,line in enumerate(lines):
  if line.startswith('vt '):
   if ti in updates:lines[i]='vt '+' '.join(f'{q:.9f}' for q in updates[ti])
   ti+=1
 (S/'models/kolonia'/source.name).write_text('\n'.join(lines)+'\n');o.location=origins.get(source.name,[0,0,0]);report.append(dict(model=source.name,faces=len(faces),islands=len(islands),distorted_faces=int(bad),worst_anisotropy=float(worst)));print(report[-1],flush=True)
(W/'uv-unwrap-report.json').write_text(json.dumps(report,indent=2));D.mkdir(exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=str(D/'rock-uv.blend'),compress=True);sys.stdout.flush();os._exit(0)
