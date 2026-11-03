"""Measured wheel fits and explicit rendering conventions. Never infer a confirmed profile."""
import json,pickle,zipfile,sys,importlib.util
from pathlib import Path
import numpy as np

PROFILES={
 'charger_rim_face':dict(reference='rim_face',track_factor=1.012,height='donor',tolerance=.03,face_gap=.01),
 'charger_legacy':dict(reference='legacy',track_factor=1.012,height='geometry',tolerance=.035,lip_gap=.04),
}

def load_spec(path):
 q=importlib.util.spec_from_file_location('wheel_fit_spec',path);s=importlib.util.module_from_spec(q);q.loader.exec_module(s);return s

def profile(S):
 name=getattr(S,'WHEEL_FIT',{}).get('profile')
 if name is not None and name not in PROFILES:raise ValueError('Unknown wheel fit profile: '+str(name))
 return name,dict(PROFILES[name]) if name else None

def tyre_size(S,front=True):
 t=S.PHYSICS['tyres'];side='front' if front else 'rear';w=float(t['width_'+side])/1000;aspect=float(t['aspect_'+side])/100;rim=float(t['rim_in'])*.0254/2
 if not (0<w<1 and 0<aspect<2 and .05<rim<1):raise ValueError('Invalid tyre dimensions')
 return dict(width=w,aspect=aspect,rim_radius=rim,radius=rim+w*aspect)

def spindles(path):
 from carbin import read_carbin
 with zipfile.ZipFile(path) as z:
  name=next(n for n in z.namelist() if n.lower().endswith('.carbin'));c=read_carbin(z.read(name))
 return {m['bone_name'].lower()[-2:]:np.array(m['transform'][12:15],float) for p in c['parts'] if p['part']['type']==43 for m in p['part']['models']}

def positions(S,G=None):
 from autotrack import apply
 apply(S);G=G or pickle.loads(Path(S.GEO).read_bytes());name,p=profile(S);b=S.PHYSICS['body'];donor=spindles(S.DONOR_ZIP) if p and p['height']=='donor' else {}
 mid=sum(float(G['wheels'][k]['centre'][2]) for k in ('HUB_LF','HUB_LR'))/2
 out={}
 for c in ('lf','rf','lr','rr'):
  front=c.endswith('f');side=-1 if c.startswith('l') else 1;ref=np.array(G['wheels']['HUB_'+c.upper()]['centre'],float).copy()
  ref[0]=side*float(b['track_front' if front else 'track_rear'])/2;ref[2]=mid+(1 if front else -1)*float(b['model_wheelbase'])/2
  if c in donor:ref[1]=donor[c][1]
  centre=ref.copy();tyre=tyre_size(S,front)
  if p and p['reference']=='rim_face':centre[0]-=side*tyre['width']/2
  out[c]=dict(reference=ref.tolist(),tyre_centre=centre.tolist(),**tyre)
 return out

def inspect_model(path):
 """Conservative source measurements. Four tyre meshes required for axis/fit suggestions."""
 import trimesh
 scene=trimesh.load(path,force='scene');candidates=[]
 for node in scene.graph.nodes_geometry:
  t,key=scene.graph[node];m=scene.geometry[key]
  if not isinstance(m,trimesh.Trimesh):continue
  v=trimesh.transform_points(m.vertices,t);lo,hi=v.min(0),v.max(0);size=hi-lo;thin=int(np.argmin(size));plane=[i for i in range(3) if i!=thin];diam=size[plane]
  mat=getattr(getattr(m.visual,'material',None),'name','') or '';hint=any(x in (node+' '+mat).lower() for x in ('tyre','tire','rubber'))
  if hint and .2<min(diam)<2 and max(diam)/min(diam)<1.15 and .05<size[thin]<.7*min(diam):
   candidates.append(dict(node=node,material=mat,centre=((lo+hi)/2).tolist(),width=float(size[thin]),outer_radius=float(diam.mean()/2),thin_axis=thin,bounds=[lo.tolist(),hi.tolist()]))
 # Multiple materials can describe one wheel. Retain the outermost tyre estimate per centre.
 unique=[]
 for c in sorted(candidates,key=lambda x:-x['outer_radius']):
  if not any(np.linalg.norm(np.array(c['centre'])-u['centre'])<.08 for u in unique):unique.append(c)
 result=dict(bounds=scene.bounds.tolist(),size=np.diff(scene.bounds,axis=0)[0].tolist(),candidates=unique,confidence='review',suggestion=None)
 if len(unique)==4 and len({c['thin_axis'] for c in unique})==1:
  thin=unique[0]['thin_axis'];centres=np.array([c['centre'] for c in unique]);forward=max((i for i in range(3) if i!=thin),key=lambda i:np.ptp(centres[:,i]));up=next(i for i in range(3) if i not in (thin,forward))
  rear,front=np.sort(centres[:,forward])[:2].mean(),np.sort(centres[:,forward])[2:].mean();cx=float(centres[:,thin].mean());scale=1.;frame='-'+('xyz'[thin])+','+'xyz'[up]+','+'xyz'[forward]
  result.update(confidence='four_tyre_meshes',suggestion=dict(frame=frame,centre_x=-cx,wheels=[float(front),float(rear),float(centres[:,up].mean()),float(np.ptp(centres[:,thin])/2)],tyre_radius=float(np.median([c['outer_radius'] for c in unique])),wheelbase=float(front-rear)))
 result['review']='Check front direction, chosen tyre meshes and nominal rim size. Outer lip radius is not nominal rim radius.'
 return result

def report(S):
 from autotrack import lips
 G=pickle.loads(Path(S.GEO).read_bytes());name,p=profile(S);errors=[];warnings=[];b=S.PHYSICS['body'];fit=positions(S,G);L=lips(S)
 if not name:warnings.append('Unprofiled legacy spec: wheel reference and runtime height are unverified. Choose WHEEL_FIT.profile for a new import.')
 if abs(float(G['wheelbase'])-float(b['model_wheelbase']))>.02:errors.append('ModelWheelbase differs from source axle spacing by more than 20 mm.')
 if p and p['reference']=='rim_face' and getattr(S,'TRACK_REFERENCE',None)!='rim_face':errors.append('Rim-face profile requires TRACK_REFERENCE="rim_face".')
 if p:
  donor=spindles(S.DONOR_ZIP)
  expected={'lf':[-.93045539,.15084539,1.59140003],'rf':[.93048829,.14618631,1.59396803],'lr':[-.93960112,.154369,-1.42373598],'rr':[.93867141,.1532625,-1.41304803]}
  if set(donor)!=set(expected) or any(np.max(np.abs(donor[k]-expected[k]))>.01 for k in expected if k in donor):errors.append('Donor spindle signature does not match the selected Charger profile; measure a new profile.')
  paint=[frag['V'] for mat,pp in G['parts'].items() if mat in S.MATERIALS and S.MATERIALS[mat] and S.MATERIALS[mat][1]=='paint' for frag in pp if len(frag['V'])]
  if paint:
   v=np.concatenate(paint)
   if abs(float((v[:,0].min()+v[:,0].max())/2))>.10:errors.append('Body is not centred laterally within 100 mm; check source centre X.')
 if abs(float(b['wheelbase'])-float(G['wheelbase']))>.05:warnings.append('Physical and model wheelbases differ by more than 50 mm; review the chosen real-car specification.')
 corner_reports={}
 for c,v in fit.items():
  wanted=np.array(G['wheels']['HUB_'+c.upper()]['centre']);actual=np.array(v['reference']);dy=float(actual[1]-wanted[1])
  if p and p['height']=='donor' and abs(dy)>p['tolerance']:errors.append(c.upper()+': source axle height differs from donor by more than 30 mm; align geometry before building.')
  if p and p['reference']=='rim_face':
   gap=abs(actual[0])-L['F' if c.endswith('f') else 'R'];target=getattr(S,'RIM_FACE_GAP',p['face_gap'])
   if abs(gap-target)>.003:errors.append(c.upper()+': rim-face reference misses measured arch target.')
   if getattr(S,'WHEEL_FIT',{}).get('geometry')=='open_wheel' and abs(v['tyre_centre'][0]-wanted[0])>.03:
    errors.append(c.upper()+': fitted tyre centre misses measured exposed-wheel centre by more than 30 mm.')
  if p and not getattr(S,'WHEEL_FIT',{}).get('allow_tyre_resize',False) and abs(float(G['wheels']['HUB_'+c.upper()]['radius'])-v['radius'])>.03:errors.append(c.upper()+': source tyre radius and database tyre size differ by more than 30 mm; correct dimensions or explicitly allow intentional resizing.')
  corner_reports[c]=dict(**v,source_axle=wanted.tolist(),height_error=dy)
 rim=None
 mats=getattr(S,'RIM_REFERENCE_MATERIALS',getattr(S,'RIM_MATERIALS',[]))
 if mats:
  centre=np.array(G['wheels']['HUB_LF']['centre']);vv=[]
  for mat in mats:
   for frag in G['parts'].get(mat,[]):
    v=frag['V'];k=(np.abs(v[:,1]-centre[1])<.4)&(np.abs(v[:,2]-centre[2])<.4)&(np.abs(v[:,0]-centre[0])<.45)
    if k.any():vv.append(v[k])
  if not vv:errors.append('No left-front rim geometry found for RIM_MATERIALS.')
  else:
   v=np.concatenate(vv);outer=float(np.hypot(v[:,1]-centre[1],v[:,2]-centre[2]).max());ref=getattr(S,'RIM_R_REF',None)
   rim=dict(outer_radius=outer,reference_radius=ref,width=float(np.ptp(v[:,0])))
   if name and ref is None:errors.append('Explicit nominal RIM_R_REF required; do not use the outer lip radius.')
   elif ref:
    lip=outer-float(ref);rim['lip_allowance']=lip
    if name and not -.002<=lip<=.025:errors.append('Rim lip/reference difference is outside -2..25 mm; check nominal size or contaminated rim geometry.')
 warnings.append('Preview width morph is an approximation for donor barrel vertices; final steering/suspension clearance still needs an in-game check.')
 return dict(profile=name,valid=not errors,errors=errors,warnings=warnings,arch_lips=L,corners=corner_reports,rim=rim,model_wheelbase=float(G['wheelbase']))

def check_database(S,d,data):
 """Post-upgrade hooks must not undo the fit dimensions."""
 tables=data.get('tables',{});carid=S.PHYSICS['car_id']
 def own(table,key,value,stock=False):
  return next((r for r in tables.get(table,{}).get('insert',[]) if r.get(key)==value and (not stock or r.get('IsStock'))),None)
 car=own('Data_Car','Id',carid);body=own('Data_CarBody','Id',carid*1000)
 if not car or not body:d['errors'].append('Built database is missing the car/body rows.')
 else:
  for side in ['Front','Rear']:
   t=tyre_size(S,side=='Front');expected={side+'TireWidthMM':round(t['width']*1000),side+'TireAspect':round(t['aspect']*100),side+'WheelDiameterIN':S.PHYSICS['tyres']['rim_in']}
   for key,value in expected.items():
    if car.get(key)!=value:d['errors'].append('Built database '+key+' differs from fitted specification.')
   for table,key,column,value in [('List_UpgradeCarBodyTireWidth'+side,'CarBodyId',side+'TireWidth',expected[side+'TireWidthMM']),('List_UpgradeRimSize'+side,'Ordinal',side+'WheelDiameter',expected[side+'WheelDiameterIN'])]:
    row=own(table,key,carid*1000 if key=='CarBodyId' else carid,True)
    if not row or row[column]!=value:d['errors'].append('Stock upgrade '+table+' disagrees with the fitted tyre/rim size.')
  for side,corner in [('Front','lf'),('Rear','lr')]:
   expected=abs(d['corners'][corner]['reference'][0])*2*1.012
   if abs(body['Model'+side+'TrackOuter']-expected)>.001:d['errors'].append('Built database '+side+' track differs from fit report.')
  midpoint=sum(v['reference'][2] for k,v in d['corners'].items() if k in ['lf','lr'])/2
  if abs(body.get('BottomCenterWheelbasePosZ',0)+midpoint)>.001:d['errors'].append('Built database axle midpoint differs from fitted geometry.')
 d['database_checked']=True;d['valid']=not d['errors'];return d


def main():
 import argparse
 a=argparse.ArgumentParser();a.add_argument('spec',nargs='?');a.add_argument('--inspect');a.add_argument('--database');a.add_argument('--out');args=a.parse_args()
 d=inspect_model(args.inspect) if args.inspect else report(load_spec(args.spec))
 if args.database and not args.inspect:d=check_database(load_spec(args.spec),d,json.loads(Path(args.database).read_text()))
 s=json.dumps(d,indent=2)
 if args.out:Path(args.out).write_text(s+'\n')
 else:print(s)
 if not args.inspect and not d['valid']:
  print('Wheel fit blocked: '+'; '.join(d['errors']),file=sys.stderr)
  raise SystemExit(2)
if __name__=='__main__':main()
