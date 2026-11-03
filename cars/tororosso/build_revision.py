"""Compatibility-first update, built without deleting saved component IDs."""
from pathlib import Path
import json,zipfile,copy,math,re,sys,shutil,subprocess
import numpy as np
P=Path(__file__).resolve().parent;ROOT=P.parents[1];sys.path[:0]=[str(ROOT/'fh2re')]
from geometry import Part
from gltf_bridge import decode_group
import struct
from body_swap import material_names
BASE=P/'input/confirmed-0.6.2';OLD=P/'quarantine/Toro Rosso STR1 0.7.0';OUT=ROOT/'output/Toro Rosso STR1';OUT.mkdir(exist_ok=True)
for f in BASE.glob('*'):
 if f.is_file():shutil.copy2(f,OUT/f.name)
D=json.loads((BASE/'database.json').read_text());T=D['tables'];K=11900/16700;stockcurve=next(c['TorqueCurveFullThrottleID'] for c in T['List_UpgradeEngineCamshaft']['insert'] if c['IsStock']);oldpeak=next(c['TorqueScale'] for c in T['List_TorqueCurve']['insert'] if c['TorqueCurveID']==stockcurve)
raw=Path('/Users/owen/Desktop/untitled folder/TJ2005_engine.ini').read_text(encoding='latin1');pts=[tuple(map(float,m)) for m in re.findall(r'RPMTorque=\(\s*([-\d.]+),\s*([-\d.]+),\s*([-\d.]+)\)',raw)];xs,ys=zip(*[(r[0],r[2]) for r in pts]);peak=max(ys)
for c in T['List_TorqueCurve']['insert']:
 c.update(TorqueScale=peak*c['TorqueScale']/oldpeak,ZeroThrottleTorqueScale=110.,NumTorqueValues=169)
 for i in range(246):c['v'+str(i)]=max(float(np.interp(i*100,xs,ys)),0.)/peak if i<=167 else -2.63 if i==168 else 0.
 for i in range(11):c['v'+str(i)]=max(c['v10'],.05)
for c in T['List_UpgradeEngineCamshaft']['insert']:c.update(RedlineRPM=16700.,TorqueCurveMaxRPM=16800.,NumRPMEntriesArray=169,StallRPM=2800.,StartRPM=8500.)
for r in T['List_UpgradeDrivetrainTransmission']['insert']:r['FinalDriveRatio']/=K
for c in T['Data_Engine']['insert']:c.update(MediaName='BMW_P83_03',EngineGraphingMaxTorque=330.,EngineGraphingMaxPower=540.)
curve=next(c for c in T['List_TorqueCurve']['insert'] if c['TorqueCurveID']==stockcurve);power=max(i*100*math.pi/30*curve['TorqueScale']*curve['v'+str(i)] for i in range(168));T['Data_Car']['insert'][0].update(SimPeakPower=power/100,SimPeakTorque=peak/100,SimPeakAngVel=16700*math.pi/30,SimPeakTorqueAngVel=15500*math.pi/30,SimRedlineAngVel=16700*math.pi/30)
# Preserve selectable and saved upgrade IDs. Make the old aftermarket stages compatible race options.
# Engine parts retain their IDs but no longer add roadcar mass/displacement/boost.
legacy=[]
for table,data in T.items():
 if not table.startswith('List_Upgrade'):continue
 for row in data.get('insert',[]):
  if row.get('IsStock'):continue
  legacy.append((table,row.get('Id')))
  if 'EngineID' in row:
   for k in ['MassDiff','WeightDistDiff','TorqueScale','Boost','BoostPressure','PowerScale']:
    if k in row:row[k]=1. if k in ['TorqueScale','PowerScale'] else 0.
   if 'Price' in row:row['Price']=0
   # Existing turbo/conversion rows stay as compatibility entries; no new forced-induction path is introduced.
(OUT/'database.json').write_text(json.dumps(D,indent=1));meta=json.loads((OUT/'mod.json').read_text());meta.update(version='0.7.1',description='Compatibility-first STR1 update: full CTDP 16,700rpm curve, F1 V10 sound, source front/rear rims, corrected steering UVs and simplified dashboard. Saved part IDs retained.',dependencies=['zs-williams-fw24']);(OUT/'mod.json').write_text(json.dumps(meta,indent=2))
z=zipfile.ZipFile(OLD/'media/cars/STR_ToroRosso_1_06.zip');names={n.lower():n for n in z.namelist()};steer=names['scene/interior/dash/steeringwheel_a.modelbin'];part=Part(z.read(steer));nm=material_names(part)
if '--dashboard' not in sys.argv:
 # Static screen first: remove the native gauge material completely from this trial.
 for b in part.b.blobs:
  if b['tag']=='MatI' and part.b.meta(b,'Name').decode()=='str1_digitalGauge':
   black=next(x for x in part.b.blobs if x['tag']=='MatI' and part.b.meta(x,'Name').decode()=='blkplastic_mgl');b['data']=bytearray(black['data'])
 for r in part.render:
  if nm[id(r['blob'])]=='str1_digitalGauge':r['indices']=[r['indices'][0]]*3
trial=P/'build/revision-static';trial.mkdir(exist_ok=True)
# Replace a surviving Charger taillight with the actual STR1 rain-light panel.
sys.path.insert(0,str(ROOT/'f1'))
import lightbuild
body=Part(z.read(names['scene/exterior/platform/body_a.modelbin']));bn=material_names(body);verts=[];normals=[]
for r in body.render:
 if bn[id(r['blob'])]=='str1_light' and len(r['indices'])>3:
  d,_=decode_group(body,r['group']);ix=np.array(r['indices']);verts.append(d['POSITION'][ix,:3]);normals.append(d['NORMAL0'][ix,:3])
assert verts
LV=np.concatenate(verts);LN=np.concatenate(normals);LV[:,2]-=.004
lamp=lightbuild.build_tail_from_207((ROOT/'f1/lamp_tail_part.modelbin').read_bytes(),{'tail':(LV,LN)})
lightdata=bytearray(z.read(names['lights.bin']));o=12
for _ in range(struct.unpack_from('<I',lightdata,8)[0]):ln=struct.unpack_from('<I',lightdata,o)[0];o+=6+ln
count=struct.unpack_from('<I',lightdata,o)[0];centre=(LV.min(0)+LV.max(0))/2
for i in range(count):
 for at in [12,44]:struct.pack_into('<3f',lightdata,o+4+76*i+at,*centre)
cz=OUT/'media/cars/STR_ToroRosso_1_06.zip';cz.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(cz,'w',zipfile.ZIP_DEFLATED) as dst:
 for n in z.namelist():
  if n.lower().startswith('ui/'):continue
  dst.writestr(n,part.build() if n==steer else lamp if n.lower().endswith('/taillightl_a.modelbin') else bytes(lightdata) if n.lower()=='lights.bin' else z.read(n))
 if '--dashboard' in sys.argv:
  xaml='''<Page xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation" xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml" xmlns:local="clr-namespace:ForzaUI" x:Class="DigitalGauge.STR_ToroRosso_1_06" DataContext="{Binding RelativeSource={x:Static RelativeSource.Self}}">
<Page.Resources><local:DigitalGaugeConfig x:Key="Config" HasClock="False" HasExternalTemp="False" UseDegreesF="True" UseMPH="True" UsePsi="True" MaxBoost="0" MinBoost="0" MaxSpeed="000" HasAbsLight="False" HasStmLight="False" HasTcsLight="False" HasGAccelX="False" HasGAccelY="False" HasShiftLights="False" HasTextTach="True" HasLapPlaceInfo="False" HasTextBoost="False" HasTextGAccel="False" HasTextOdometer="False" HasTextFuel="False" MaxFuel="0" MaxGear="7" MaxRpm="16700"/></Page.Resources>
<Canvas Width="640" Height="180" Background="Black"><TextBlock Canvas.Left="10" Canvas.Top="5" Width="120" FontFamily="DG5_QuartzMS" FontSize="115" Foreground="#FFE3E99E" Text="{Binding Gear}"/><TextBlock Canvas.Left="145" Canvas.Top="5" Width="240" FontFamily="DG5_QuartzMS" FontSize="80" Foreground="#FFE3E99E" Text="{Binding Speed}"/><TextBlock Canvas.Left="400" Canvas.Top="5" Width="230" FontFamily="DG5_QuartzMS" FontSize="66" Foreground="#FFE3E99E" Text="{Binding TextTach}"/><TextBlock Canvas.Left="170" Canvas.Top="112" FontFamily="DG5_QuartzMS" FontSize="28" Foreground="#FFE3E99E" Text="MPH"/><TextBlock Canvas.Left="440" Canvas.Top="112" FontFamily="DG5_QuartzMS" FontSize="28" Foreground="#FFE3E99E" Text="RPM"/></Canvas></Page>'''
  dst.writestr('UI/STR_ToroRosso_1_06.xaml',xaml)
shutil.copytree(BASE/'media/stripped',OUT/'media/stripped',dirs_exist_ok=True)
(P/'build/revision-summary.json').write_text(json.dumps(dict(version='0.7.1',dashboard='--dashboard' in sys.argv,legacy_ids_preserved=len(legacy),power_hp=power/745.699872,runtime_tested=False),indent=2));print('Built revision',meta['version'],'dashboard=', '--dashboard' in sys.argv)
