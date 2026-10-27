"""Blender: closed low-poly rock passage skins, simple fitted collision, shader lights."""
import bpy,bmesh,math,json,sys,numpy as np
from pathlib import Path
from collections import Counter,defaultdict
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt
S=Path(__file__).resolve().parents[1];D=S/'devassets/cave-passages';W=D/'build';W.mkdir(parents=True,exist_ok=True)
plans=json.loads((D/'passage-plan.json').read_text());roompolys={k:np.array(v,float) for k,v in json.loads((D/'room-footprints.json').read_text()).items()};ground_boundaries=np.array(json.loads((D/'floor-boundaries.json').read_text()));cache={}
def segment_distance(p,a,b):
 p=np.array(p,float);a=np.array(a,float);b=np.array(b,float);d=b-a;t=np.clip(np.sum((p-a)*d,axis=-1)/np.maximum(np.sum(d*d,axis=-1),1e-20),0,1);return np.linalg.norm(p-a-t[...,None]*d,axis=-1)
def boundary_distance(p,polygon):
 v=np.array(polygon,float)
 if np.linalg.norm(v[0]-v[-1])<1e-10:v=v[:-1]
 return float(np.min(segment_distance(p,v,np.roll(v,-1,axis=0))))
def inside(p,polygon,eps=0):
 v=np.array(polygon,float)
 if np.linalg.norm(v[0]-v[-1])<1e-10:v=v[:-1]
 if boundary_distance(p,v)<=max(eps,1e-10):return True
 x,y=p;hit=False
 for a,b in zip(v,np.roll(v,-1,axis=0)):
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:hit=not hit
 return hit
def polygon_distance(p,polygon):return 0.0 if inside(p,polygon) else boundary_distance(p,polygon)
def source_height(p):
 d=float(np.min(segment_distance(p,ground_boundaries[:,0],ground_boundaries[:,1])));return (3.5+1.4*math.sin(p[0]/180)+1.2*math.cos(p[1]/210))*min(1,d/48)
def gridh(i,j):
 key=(i,j)
 if key not in cache:cache[key]=source_height(np.array(key,float)*192)
 return cache[key]
def ground(x,y):
 i,j=math.floor(x/192),math.floor(y/192);u=x/192-i;v=y/192-j
 return (1-u)*gridh(i,j)+(u-v)*gridh(i+1,j)+v*gridh(i+1,j+1) if v<=u else (1-v)*gridh(i,j)+u*gridh(i+1,j+1)+(v-u)*gridh(i,j+1)

ground_unoffset=ground
def ground(x,y):return ground_unoffset(x,y)+.25
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
collision=[];report=[]
def material(name):return bpy.data.materials.get(name) or bpy.data.materials.new(name)
def mesh_obj(name,v,faces,mats,ids,uvs):
 m=bpy.data.meshes.new(name);m.from_pydata(v,[],faces);m.update();o=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(o)
 for mat in mats:m.materials.append(material(mat))
 uv=m.uv_layers.new(name='UVMap')
 for p,mi,tt in zip(m.polygons,ids,uvs):
  p.material_index=mi;p.use_smooth=(mi!=0)
  for li,t in zip(p.loop_indices,tt):uv.data[li].uv=t
 return o

def prism(points,direction,label):
 # Parallel extrusion of a convex planar face gives 5/6 stable planes.
 pp=np.array(points,float);d=np.array(direction,float);n=np.cross(pp[1]-pp[0],pp[2]-pp[0]);L=np.linalg.norm(n)
 if L<1e-5:return
 n/=L
 if n@d>0:n=-n
 front=pp+n*.15;back=pp+d;mid=np.r_[front,back].mean(0);planes=[[*n,float(n@front[0])],[*(-n),float(-n@back[0])]]
 for a,b in zip(pp,np.roll(pp,-1,axis=0)):
  nn=np.cross(b-a,d);length=np.linalg.norm(nn)
  if length<1e-6:return
  nn/=length
  if nn@(mid-a)>0:nn=-nn
  planes.append([*nn,float(nn@a)+.05])
 collision.append(dict(passage=label,planes=planes))

def export(path,objects,origin):
 out=['mtllib kolonia.mtl'];idx=1
 for o in objects:
  m=o.data;m.calc_loop_triangles();uv=m.uv_layers.active;out.append('g '+o.name);last=None
  for tri in m.loop_triangles:
   tp=[m.vertices[i].co for i in tri.vertices]
   if (tp[1]-tp[0]).cross(tp[2]-tp[0]).length<.0001:continue
   name=m.materials[tri.material_index].name
   if name!=last:out.append('usemtl '+name);last=name
   for li in tri.loops:
    p=o.matrix_world@m.vertices[m.loops[li].vertex_index].co-Vector(origin);n=o.matrix_world.to_3x3().inverted().transposed()@m.corner_normals[li].vector;n.normalize();t=uv.data[li].uv
    out.extend([f'v {p.x:.7f} {p.z:.7f} {-p.y:.7f}',f'vt {t.x:.7f} {-t.y:.7f}',f'vn {n.x:.7f} {n.z:.7f} {-n.y:.7f}'])
   out.append('f '+' '.join(f'{q}/{q}/{q}' for q in range(idx,idx+3)));idx+=3
 path.write_text('\n'.join(out)+'\n')

for plan in plans:
 polygon=np.array(plan['polygon'],float)[:-1];name=plan['name'];lo=np.floor(polygon.min(0)/96).astype(int)-1;hi=np.ceil(polygon.max(0)/96).astype(int)+1
 coords=[Vector(p[:2]) for p in polygon];n0=len(coords);edges=[(i,(i+1)%n0) for i in range(n0)];grid={}
 for i in range(lo[0],hi[0]+1):
  for j in range(lo[1],hi[1]+1):grid[i,j]=len(coords);coords.append(Vector((i*96,j*96)))
 for (i,j),vi in grid.items():
  for di,dj in [(1,0),(0,1),(1,1)]:
   if (i+di,j+dj) in grid:edges.append((vi,grid[i+di,j+dj]))
 verts,_,faces,*_=delaunay_2d_cdt(coords,edges,[],0,.06,False);xy=np.array([v[:] for v in verts]);keep=[]
 for f in faces:
  if len(f)!=3:continue
  if inside(xy[f].mean(0),polygon,.001):keep.append(f)
 used=sorted(set(i for f in keep for i in f));remap={old:new for new,old in enumerate(used)};xy=xy[used];faces=[[remap[i] for i in f] for f in keep];N=len(xy)
 # Boundary edges follow the interior on their left.
 counts=Counter(tuple(sorted((a,b))) for f in faces for a,b in zip(f,f[1:]+f[:1]));boundary=[(a,b) for f in faces for a,b in zip(f,f[1:]+f[:1]) if counts[tuple(sorted((a,b)))]==1]
 caps=[];normal_sum=defaultdict(lambda:np.zeros(2));capnormal_sum=defaultdict(lambda:np.zeros(2))
 for a,b in boundary:
  mid=(xy[a]+xy[b])/2;is_cap=any(polygon_distance(mid,roompolys[r])<.3 for r in plan['cap_rooms']);caps.append(is_cap)
  if is_cap:
   edge=xy[b]-xy[a];nn=np.array([-edge[1],edge[0]])/np.linalg.norm(edge);capnormal_sum[a]+=nn;capnormal_sum[b]+=nn
  if not is_cap:
   e=xy[b]-xy[a];normal=np.array([-e[1],e[0]])/np.linalg.norm(e);normal_sum[a]+=normal;normal_sum[b]+=normal
 caplines=[(xy[a],xy[b]) for (a,b),cap in zip(boundary,caps) if cap]
 def roof(p):
  d=boundary_distance(p,polygon);dc=min((float(segment_distance(p,*line)) for line in caplines),default=1000)
  fade=max(0,min(1,(dc-8)/56));return 221.75+fade*(78*math.sin(min(d/128,1)*math.pi/2)+(8*math.sin(p[0]/180)*math.cos(p[1]/150)+4*math.sin((p[0]+p[1])/87))*min(1,d/48))
 floorz=np.array([ground(*p) for p in xy]);roofz=np.array([roof(p) for p in xy]);vv=[(*p,z) for p,z in zip(xy,floorz)]+[(*p,z) for p,z in zip(xy,roofz)];ff=[];mi=[];uv=[]
 mats=['textures/kolonia/cave_ground','textures/kolonia/cave_base','textures/kolonia/cave_fracture']
 for f in faces:
  if np.cross(np.r_[xy[f[1]]-xy[f[0]],0],np.r_[xy[f[2]]-xy[f[0]],0])[2]<0:f=f[::-1]
  ff.append(f);mi.append(0);uv.append([(xy[i,1]/1024,xy[i,0]/1024) for i in f]);prism([vv[i] for i in f],[0,0,-16],name)
  rf=[i+N for i in f[::-1]];ff.append(rf);c=xy[f].mean(0);mat=2 if math.sin(c[0]/210)*math.cos(c[1]/190)>.65 else 1;mi.append(mat);uv.append([(vv[i][1]/1024,-vv[i][0]/1024) for i in rf]);prism([vv[i] for i in rf],[0,0,192],name)
 # Build complete wall runs with continuous length/height UVs.
 for (a,b),cap in zip(boundary,caps):
  if cap:
   axis=(xy[b]-xy[a]);axis/=np.linalg.norm(axis)
   for i in [a,b]:
    if i in normal_sum:normal_sum[i]=axis*(normal_sum[i]@axis)
 vertex_normal={i:n/max(np.linalg.norm(n),1e-9) for i,n in normal_sum.items()};rows={} ;wall_edges=[];walk_u={};unvisited=set(boundary)
 while unvisited:
  available=[edge for edge,cap in zip(boundary,caps) if cap and edge in unvisited];start=min(available if available else unvisited,key=lambda edge:tuple(np.round(np.r_[xy[edge[0]],xy[edge[1]]],3)));a,b=start;u=0
  while (a,b) in unvisited:
   unvisited.remove((a,b));walk_u[a]=u;u+=np.linalg.norm(xy[b]-xy[a]);walk_u[b]=u
   nxt=next((e for e in unvisited if e[0]==b),None)
   if nxt is None:break
   a,b=nxt
 for i,n in vertex_normal.items():
  row=[i]
  for z,base in [(80,9),(160,19)]:
   offset=base+6*math.sin(xy[i,0]/130+xy[i,1]/170);row.append(len(vv));vv.append((*(xy[i]+n*offset),z))
  row.append(i+N);rows[i]=row
 for (a,b),cap in zip(boundary,caps):
  if cap:continue
  outward=-np.array([-(xy[b]-xy[a])[1],(xy[b]-xy[a])[0],0]);outward/=np.linalg.norm(outward)
  ua,ub=walk_u.get(a,0),walk_u.get(b,0)
  if abs(ub-ua)>np.linalg.norm(xy[b]-xy[a])*2:ub=ua+np.linalg.norm(xy[b]-xy[a])
  for k in range(3):
   q=[rows[a][k],rows[a][k+1],rows[b][k+1],rows[b][k]];ff.append(q);mi.append(1);uv.append([(ua/1024,-vv[q[0]][2]/1024),(ua/1024,-vv[q[1]][2]/1024),(ub/1024,-vv[q[2]][2]/1024),(ub/1024,-vv[q[3]][2]/1024)])
   # Nonplanar quads use two exact triangles for collision.
   for ii in [(0,1,2),(0,2,3)]:prism([vv[q[j]] for j in ii],outward*40,name)
   if k==1:wall_edges.append((xy[a],xy[b],vertex_normal[a],vertex_normal[b],min(ua,ub)))
 # Bevel each opening back into the room jamb, closing the gap between the
 # bowed passage walls and the original rectangular portal.
 edge_faces=defaultdict(list)
 for fi,f in enumerate(ff):
  for ia,ib in zip(f,f[1:]+f[:1]):edge_faces[tuple(sorted((ia,ib)))].append((ia,ib,fi))
 open_edges=[items[0] for items in edge_faces.values() if len(items)==1];links={a:(b,fi) for a,b,fi in open_edges};unseen=set(links)
 while unseen:
  start=next(iter(unseen));loop=[];node=start
  while node in unseen:
   unseen.remove(node);loop.append(node);node=links[node][0]
  if len(loop)<4:continue
  base_for_vertex={vi:base for base,row in rows.items() for vi in row};outer={};normals={}
  for vi in loop:
   base=vi if vi<N else vi-N if vi<2*N else base_for_vertex[vi];nn=capnormal_sum[base];nn=nn/max(np.linalg.norm(nn),1e-9);normals[vi]=nn;p3=np.array(vv[vi]);out=p3.copy();out[:2]-=nn*8
   if vi<N:out[2]-=8
   elif vi<2*N:out[2]+=8
   else:out[:2]=xy[base]-vertex_normal[base]*8-nn*8
   outer[vi]=len(vv);vv.append(tuple(out))
  for ia in loop:
   ib,fi=links[ia];quad=[ib,ia,outer[ia],outer[ib]];basef=ff[fi];baseuv=np.array(uv[fi]);facepoints=np.array([vv[i] for i in basef]);C=facepoints.mean(0);B=np.linalg.svd(facepoints-C,full_matrices=False)[2][:2].T;A=np.c_[(facepoints-C)@B,np.ones(len(basef))];M=np.linalg.lstsq(A,baseuv,rcond=None)[0]
   tt=[(vv[i][1]/1024,vv[i][0]/1024) for i in quad] if mi[fi]==0 else [tuple(np.r_[(np.array(vv[i])-C)@B,1]@M) for i in quad];ff.append(quad);mi.append(mi[fi]);uv.append(tt);direction=normals[ia]+normals[ib];direction/=max(np.linalg.norm(direction),1e-9)
   for ids in [(0,1,2),(0,2,3)]:prism([vv[quad[j]] for j in ids],[*(direction*32),0],name)
 o=mesh_obj('Passage_'+name,vv,ff,mats,mi,uv);bpy.context.view_layer.objects.active=o;o.select_set(True)
 # Merge only truly coplanar pairs; curved faces keep the geometry they need.
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.001);bmesh.ops.dissolve_degenerate(bm,dist=.03,edges=list(bm.edges));bmesh.ops.join_triangles(bm,faces=[f for f in bm.faces if len(f.verts)==3],cmp_uvs=True,cmp_materials=True,angle_face_threshold=.00001,angle_shape_threshold=math.pi);bm.to_mesh(o.data);bm.free();o.data.update()
 solid=o.modifiers.new('Closed_rock_backing','SOLIDIFY');solid.thickness=8;solid.offset=-1;solid.use_rim=True
 for _ in range(3):o.data.materials.append(material('textures/common/caulk'))
 solid.material_offset=3;solid.material_offset_rim=0;bpy.ops.object.modifier_apply(modifier=solid.name);o.select_set(False)
 # Solidify copies edge UVs onto its closing rims, collapsing their UV area.
 # Give those narrow visible faces a real planar mapping at the same scale.
 o.data.calc_loop_triangles();layer=o.data.uv_layers.active;distorted=set()
 for tri in o.data.loop_triangles:
  if tri.material_index>=3:continue
  pp=np.array([o.data.vertices[i].co[:] for i in tri.vertices]);tt=np.array([layer.data[i].uv[:] for i in tri.loops]);E=pp[1:]-pp[0]
  if np.linalg.norm(np.cross(E[0],E[1]))<.0001:continue
  sig=np.linalg.svd(np.linalg.pinv(E)@(tt[1:]-tt[0]),compute_uv=False)
  if sig[1]<1e-9 or sig[0]/sig[1]>8:distorted.add(tri.polygon_index)
 if distorted:
  bm=bmesh.new();bm.from_mesh(o.data);bm.faces.ensure_lookup_table();bmesh.ops.triangulate(bm,faces=[bm.faces[i] for i in distorted],quad_method='BEAUTY',ngon_method='BEAUTY');bm.to_mesh(o.data);bm.free();o.data.update()
 layer=o.data.uv_layers.active
 for face in o.data.polygons:
  if face.material_index>=3:continue
  pp=np.array([o.data.vertices[i].co[:] for i in face.vertices]);tt=np.array([layer.data[i].uv[:] for i in face.loop_indices]);E=pp[1:]-pp[0];M=np.linalg.pinv(E)@(tt[1:]-tt[0]);sig=np.linalg.svd(M,compute_uv=False)
  if sig[1]>1e-9 and sig[0]/sig[1]<8:continue
  choices=[(np.linalg.norm(pp[j]-pp[i]),i,j) for i in range(len(pp)) for j in range(i+1,len(pp)) if np.linalg.norm(tt[j]-tt[i])>1e-9]
  if not choices:continue
  _,ia,ib=max(choices);tangent=pp[ib]-pp[ia];tangent/=np.linalg.norm(tangent);normal=np.array(face.normal[:]);across=np.cross(normal,tangent);across/=max(np.linalg.norm(across),1e-9);ut=tt[ib]-tt[ia];ut/=np.linalg.norm(ut);uvacross=np.array([-ut[1],ut[0]])
  for li,point in zip(face.loop_indices,pp):layer.data[li].uv=tt[ia]+((point-pp[ia])@tangent)*ut/1024+((point-pp[ia])@across)*uvacross/1024

 bm=bmesh.new();bm.from_mesh(o.data);assert all(len(e.link_faces)==2 for e in bm.edges),(name,'unclosed skin');bm.free();objects=[o]
 # Small mounted fungal brackets put shader light below the overhangs.
 travelled=0;last=-1e9;lights=0;light_positions=[]
 for a,b,na,nb,station in sorted(wall_edges,key=lambda e:e[4]):
  travelled+=np.linalg.norm(b-a)
  if travelled-last<280:continue
  p=(a+b)/2;n=na+nb;n/=max(np.linalg.norm(n),1e-9)
  if any(float(segment_distance(p,*line))<80 for line in caplines):continue
  if any(np.linalg.norm(p-q)<200 for q in light_positions):continue
  mounted_offset=(19+6*math.sin(p[0]/130+p[1]/170))*(221.75-184)/(221.75-160)+3;center=p+n*mounted_offset;bpy.ops.mesh.primitive_uv_sphere_add(segments=10,ring_count=6,radius=1,location=(*center,184));glow=bpy.context.object;glow.name='Fungal_light_'+str(lights);glow.scale=(28,4,14);glow.rotation_euler.z=math.atan2(n[1],n[0])-math.pi/2;glow.data.materials.append(material('textures/kolonia/cave_fungus_light'));objects.append(glow);light_positions.append(p);last=travelled;lights+=1
 bpy.context.view_layer.update();path=S/'models/kolonia'/('passage_'+name+'.obj');export(path,objects,plan['origin']);row=dict(name=name,model=path.name,triangles=sum(sum(len(p.vertices)-2 for p in ob.data.polygons) for ob in objects),lights=lights,quads=sum(sum(len(p.vertices)==4 for p in ob.data.polygons) for ob in objects));report.append(row);print(row,flush=True)
D=S/'devassets/cave-passages';D.mkdir(parents=True,exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=str(D/'passages.blend'),compress=True);(W/'passage-collision.json').write_text(json.dumps(collision));(W/'passage-art-report.json').write_text(json.dumps(report,indent=2));print('PASSAGES COMPLETE',len(collision),'simple collision parts',flush=True)

if bpy.app.background:
 import os
 sys.stdout.flush();os._exit(0)
