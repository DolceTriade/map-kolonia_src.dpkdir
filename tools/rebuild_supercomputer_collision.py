#!/usr/bin/env python3
"""Rebuild fitted fullclip hulls after moving the static supercomputer models.

Save the map in Radiant first. This changes only the generated collision group.
"""
from pathlib import Path
import json,math,re,numpy as np
S=Path(__file__).resolve().parents[1]
MAP=S/'maps/kolonia.map'
def entities(text):
 masked=re.sub(r'"(?:\\.|[^"\\])*"|//[^\n]*',lambda m:' '*len(m[0]),text);depth=0;start=0;out=[]
 for i,c in enumerate(masked):
  if c=='{':
   if depth==0:start=i
   depth+=1
  elif c=='}':
   depth-=1
   if depth==0:out.append((start,i+1,text[start:i+1]))
 return out
def props(block):return dict(re.findall(r'^"([^"\n]+)"\s+"([^"\n]*)"',block,re.M))
def serialize(planes):
 rows=['{','brushDef','{']
 for q in planes:
  n=np.array(q[:3]);p=n*q[3];axis=np.eye(3)[np.argmin(abs(n))];u=np.cross(n,axis);u/=np.linalg.norm(u);v=np.cross(n,u)
  rows.append(' '.join('( '+' '.join(f'{x:.9f}' for x in pp)+' )' for pp in [p,p+v*128,p+u*128])+' ( ( 0.03125 0 0 ) ( 0 0.03125 0 ) ) common/fullclip 134217728 0 0')
 return '\n'.join(rows+['}','}'])
def main():
 text=MAP.read_text();models=[];hulls=json.loads((S/'devassets/supercomputer/computer-collision.json').read_text());brushes=[]
 for a,b,e in entities(text):
  p=props(e)
  if p.get('model')!='models/kolonia/sci_fi_supercomputer.obj':continue
  if p.get('angles') and any(abs(x)>.001 for x in map(float,p['angles'].split())):raise SystemExit('This helper supports yaw in angle; convert pitch/roll before rebuilding.')
  origin=np.array(list(map(float,p.get('origin','0 0 0').split())));scale=np.array(list(map(float,p.get('modelscale_vec',' '.join([p.get('modelscale','1')]*3)).split())));angle=math.radians(float(p.get('angle',0)));rot=np.array([[math.cos(angle),-math.sin(angle),0],[math.sin(angle),math.cos(angle),0],[0,0,1]]);inverse=np.linalg.inv(rot@np.diag(scale))
  for hull in hulls:
   planes=[]
   for q in hull:
    n=np.array(q[:3])@inverse;length=np.linalg.norm(n);planes.append([*(n/length),(q[3]+n@origin)/length])
   brushes.append(serialize(planes))
  models.append(p['origin'])
 if not models:raise SystemExit('No supercomputer models found; existing collision was preserved.')
 for a,b,e in reversed(entities(text)):
  if props(e).get('_kolonia_generated')=='supercomputer_collision':text=text[:a]+text[b:]
 text+='\n{\n"classname" "func_group"\n"_kolonia_generated" "supercomputer_collision"\n'+'\n'.join(brushes)+'\n}\n';MAP.write_text(text);print(f'Rebuilt {len(brushes)} fitted hulls for {len(models)} computers; model placements unchanged.')
if __name__=='__main__':main()
