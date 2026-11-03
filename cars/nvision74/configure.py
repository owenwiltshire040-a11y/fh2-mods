from pathlib import Path
import importlib.util,json,pickle,pprint,shutil
p=Path(__file__).resolve().parent;root=p.parents[1]
x=importlib.util.spec_from_file_location('base',root/'cars/modely2025/spec.py');m=importlib.util.module_from_spec(x);x.loader.exec_module(m);P=m.PHYSICS
P.update(car_id=4301,make_offset=14,make='Hyundai',make_profile='Hyundai',make_code='HYU',make_country=6,string_base=65400,colour_offset=9000,name='N Vision 74',short_name='N Vision 74')
P['body'].update(mass=2000.,weight_front=.48,cm_height=.42,block=(1.995,1.,4.952),height=1.331,length=4.952,width=1.995,wheelbase=2.905,model_wheelbase=2.905,track_front='auto',track_rear='auto',bbox=(-1.08,1.08,-.22,1.12,-2.75,2.45))
P['drivetrain']['drivetype']=2
P['tyres'].update(width_front=295,width_rear=345,aspect_front=30,aspect_rear=30,rim_in=21,compound=4)
P['brakes'].update(front_mm=390.,rear_mm=380.,front_pistons=3,rear_pistons=2)
P['car'].update(year=2023,t60=3.8,t100=8.5,top_mph=155.,price=1,pi=.75,drag=200.,downforce_front=30.,downforce_rear=90.,ratings=(7.,7.,8.,7.,8.),bucket=35)
A=json.loads((p/'source-analysis.json').read_text());G=pickle.loads((p/'geo.pkl').read_bytes());c=G['wheels']['HUB_LF']['centre']
for f in G['parts']['SOURCE_RIM']:f['V'][:,1:]=c[1:]+(f['V'][:,1:]-c[1:])*.9995
(p/'geo.pkl').write_bytes(pickle.dumps(G));w=json.loads((p/'source-wheel.json').read_text());w['outer_lip_radius']*=.9995;w['preparation_note']='Front source design retained on all corners; radial normalisation 0.9995 accommodates packed lip precision. Source rear design differs in diameter; game uses a common nominal 21-inch rim.';(p/'source-wheel.json').write_text(json.dumps(w,indent=2))
s='''"""N Vision 74: supplied model, measured 2.905m wheelbase, native electric RWD.
500kW/900Nm follows Hyundai; mass, handling, gearing and cockpit provisional.
FH2 approximates the hydrogen/fuel-cell system with its battery-electric powertrain.
"""
import os
from PIL import Image
HERE=os.path.dirname(os.path.abspath(__file__))
MEDIA='HYU_NVision74_23_A'
DONOR_ZIP=f'{HERE}/donor_{MEDIA}.zip'
GEO=f'{HERE}/geo.pkl'
TEXTURES={}
BODY_PLAIN={'paint':(0,'carpaint'),'chrome':(0,'frame'),'black':(1,'blkplastic_hgl')}
BODY_TEXTURED_LIKE={0:'carpaint',3:'carpaint'}
GLASS_PLAIN={'glass':(0,'gls_windsheild')}
ONE_SIDED=True
PRESERVE_UV_SEAMS=True
RIM_MATERIALS=['SOURCE_RIM']
RIM_R_REF=.2667
RIM_SOURCE_TEXTURE='source_rim'
REQUIRE_SOURCE_WHEELS=True
TRACK_REFERENCE='rim_face'
RIM_FACE_GAP=0.
WHEEL_FIT=dict(profile='charger_rim_face')
KEEP_PARTS={'body_a.modelbin','glassf_a.modelbin'}
STEER=(-.38,.67,.31)
HIPS=(-.38,.22,-.2)
EYE=(-.38,.88,-.07)
STEERING_MATERIALS=[]  # Source steering wheel retained static.
DRIVER_ANIMS_ZIP=None
AVPINS_TEMPLATE=None
PRESENT=dict(paint='bfc2c6',use_make=(17,'_&857938132'))
UPGRADE_PROFILE='electric_db.py'
LIGHTS={'head':dict(mats=['HEAD_EMITTER']),'tail':dict(mats=['TAIL_EMITTER'])}
LAMP_CLEANUP='lamp_cleanup.py'
'''
for mat,fn in A['textures'].items():
 key='t'+fn[:-4];s+=f"TEXTURES[{key!r}]=(Image.open(os.path.join(HERE,'textures',{fn!r})).convert('RGB'),512,False)\n"
s+="TEXTURES['source_rim']=TEXTURES["+repr('t'+A['textures']['SOURCE_RIM'][:-4])+"]\n"
s+='MATERIALS='+pprint.pformat(A['mapping'],width=110)+'\n';s+="MATERIALS['HEAD_EMITTER']=('plain','black')\nMATERIALS['TAIL_EMITTER']=('plain','black')\n"
s+='PHYSICS='+pprint.pformat(P,width=100)+'\n';(p/'spec.py').write_text(s)
shutil.copy2(root/'cars/modely2025/lamp_cleanup.py',p/'lamp_cleanup.py')
e=(root/'cars/modely2025/electric_db.py').read_text().replace('Dual Motor AWD - provisional','Hydrogen-electric RWD - provisional').replace('800.','700.').replace('75.','62.4').replace('650.','900.').replace('500.','900.').replace('295000.','500000.').replace('DrivetypeID=3','DrivetypeID=2').replace('5.55','5.0').replace('GearRatio1=1.62','GearRatio1=1.5').replace('RearToqueSplit=.55','RearToqueSplit=1.0').replace('2950.','5000.').replace('1992*','2000*')
e=e.replace('MotorGraphingMaxPower=900.','MotorGraphingMaxPower=500.').replace('SimPeakTorque=5.','SimPeakTorque=9.').replace("r['ManufacturerID']=81","r['ManufacturerID']=17").replace('single-speed AWD and EV upgrades configured','single-speed RWD and EV upgrades configured')
(p/'electric_db.py').write_text(e)
pkg=p/'pkg/Hyundai N Vision 74';pkg.mkdir(parents=True,exist_ok=True)
(pkg/'mod.json').write_text(json.dumps(dict(format_version=1,id='owen-hyundai-nvision74',name='Hyundai N Vision 74 (2023)',author='Owen',version='0.1.0',description='Supplied N Vision 74 model, original textured source wheels, detailed cabin and native electric RWD. Personal conversion; hydrogen simulation and handling approximate.',database='database.json',strings='strings.json',media='media',dependencies=[]),indent=2))
(pkg/'CREDITS.txt').write_text('Personal conversion of the model supplied by Owen in 2023-hyundai-n-vision-74-concept. Original model author/license not included in supplied folder; retain source provenance. Hyundai vehicle design/trademarks belong to their owners. Conversion tools: fh2-mods and Extra Options.\n')
(p/'BUILD-NOTES.txt').write_text('Source: supplied local GLB. Hyundai official dimensions and powertrain target: https://www.hyundai-n.com/en/models/rolling-lab/n-vision-74\nUniform scale to measured 2.905m wheelbase. Source extras extend past published overall dimensions. Common source front rim design used on four animated corners; rear source wheels not baked into body. Provisional 2000kg, gearing, cockpit/handling. FH2 battery-electric approximation of hydrogen-electric drivetrain. Runtime exterior inspection required.\n')
print('Configured',p)
