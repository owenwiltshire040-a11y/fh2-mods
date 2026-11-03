"""Opel Corsa C — personal prototype. Dimensions based on source axle measurements.
Engine, handling, cockpit and lamps need an in-game review; see BUILD-NOTES.txt.
"""
import os
from PIL import Image
HERE=os.path.dirname(os.path.abspath(__file__))
MEDIA='OPE_daily05_2003__'
DONOR_ZIP=os.path.join(HERE,'donor_'+MEDIA+'.zip')
GEO=os.path.join(HERE,'geo.pkl')
TEXTURES={}
TEXTURES['t466bc8ce']=(Image.open(os.path.join(HERE,'textures','t466bc8ce.png')),512,False)
TEXTURES['t61e2f51c']=(Image.open(os.path.join(HERE,'textures','t61e2f51c.png')),512,False)
TEXTURES['td3d4ad73']=(Image.open(os.path.join(HERE,'textures','td3d4ad73.png')),512,False)
TEXTURES['tcbb4919b']=(Image.open(os.path.join(HERE,'textures','tcbb4919b.png')),512,False)
TEXTURES['t5d3c7de2']=(Image.open(os.path.join(HERE,'textures','t5d3c7de2.png')),512,False)
TEXTURES['t54036523']=(Image.open(os.path.join(HERE,'textures','t54036523.png')),512,False)
TEXTURES['t3597882b']=(Image.open(os.path.join(HERE,'textures','t3597882b.png')),512,False)
TEXTURES['tdfa7937a']=(Image.open(os.path.join(HERE,'textures','tdfa7937a.png')),512,False)
TEXTURES['tf5dc3ac0']=(Image.open(os.path.join(HERE,'textures','tf5dc3ac0.png')),512,False)
TEXTURES['te94b0fc1']=(Image.open(os.path.join(HERE,'textures','te94b0fc1.png')),512,False)
TEXTURES['t528cef87']=(Image.open(os.path.join(HERE,'textures','t528cef87.png')),512,False)
TEXTURES['t141a29d5']=(Image.open(os.path.join(HERE,'textures','t141a29d5.png')),512,False)
TEXTURES['t94cc3ece']=(Image.open(os.path.join(HERE,'textures','t94cc3ece.png')),512,False)
TEXTURES['ta9148041']=(Image.open(os.path.join(HERE,'textures','ta9148041.png')),512,False)
TEXTURES['t5e43c0b0']=(Image.open(os.path.join(HERE,'textures','t5e43c0b0.png')),512,False)
TEXTURES['t8f14bfb7']=(Image.open(os.path.join(HERE,'textures','t8f14bfb7.png')),512,False)
TEXTURES['t97912524']=(Image.open(os.path.join(HERE,'textures','t97912524.png')),512,False)
TEXTURES['t4789eb93']=(Image.open(os.path.join(HERE,'textures','t4789eb93.png')),512,False)
TEXTURES['tfc120a7e']=(Image.open(os.path.join(HERE,'textures','tfc120a7e.png')),512,False)
MATERIALS={'body': ('plain', 'paint'), 'black': ('textured', 't466bc8ce'), 'gray': ('textured', 't61e2f51c'), 'corsa_long': ('textured', 'td3d4ad73'), 'hatch': ('textured', 'tcbb4919b'), 'hatch_chmsl': ('textured', 't5d3c7de2'), 'pessima_engine': ('textured', 't54036523'), 'hatch_interior': ('textured', 't3597882b'), 'hatch_gauges': ('textured', 'tdfa7937a'), 'coupe_engine': ('textured', 'tf5dc3ac0'), 'oilcooler': ('textured', 'te94b0fc1'), 'hatch_glass': ('plain', 'glass'), 'white': ('textured', 't528cef87'), 'plastic': ('textured', 't141a29d5'), 'gauges': ('textured', 't94cc3ece'), 'material_17': ('textured', 'ta9148041'), 'corsa_short': ('textured', 't5e43c0b0'), 'koja': ('textured', 't8f14bfb7'), 'material': ('textured', 't97912524'), 'chrome': ('plain', 'chrome'), 'corsa_int': ('textured', 't4789eb93'), 'boot_ok.001': ('textured', 'tfc120a7e')}
BODY_PLAIN={'paint':(0,'carpaint'),'chrome':(0,'frame'),'black':(1,'blkplastic_hgl')}
GLASS_PLAIN={'glass':(0,'gls_windsheild')}
BODY_TEXTURED_LIKE={0:'carpaint',3:'carpaint'}
KEEP_PARTS={'body_a.modelbin','glassf_a.modelbin'}
RIM_MATERIALS=[]
ONE_SIDED=True
PRESERVE_UV_SEAMS=True
RIM_TRUST_NORMALS=True
TRACK_REFERENCE='rim_face'
RIM_FACE_GAP=.01
WHEEL_FIT=dict(profile='charger_rim_face')
STEER=(-0.34, 0.49973999999999996, 0.4)
HIPS=(-0.34, 0.263095, -0.05)
EYE=(-0.34, 0.84848, 0.0)
DRIVER_ANIMS_ZIP=None
AVPINS_TEMPLATE=None
PRESENT={'paint': '6b92b1', 'logo_text': 'OPEL', 'icon_base': 'Opel'}
PHYSICS={'car_id': 5005, 'make_offset': 104, 'make': 'Opel', 'make_profile': 'Opel', 'make_code': 'OPE', 'make_country': 7, 'make_icon': 'ARI', 'string_base': 65212, 'colour_offset': 1900, 'name': 'Corsa C', 'short_name': 'Corsa C', 'engine': {'name': '1.2L I4', 'sound': 'FOR_Fiesta_09', 'mass': 110.0, 'compression': 10.5, 'config': 3, 'cylinders': 1, 'aspiration': 1, 'boost': 0.0, 'inertia': 0.16, 'tank': 35, 'displacement': 1199, 'peak_hp': 74, 'peak_nm': 110, 'redline': 6500, 'stall': 750.0, 'start': 3000.0, 'curve': [(0, 33.0), (1000, 55.0), (2000, 88.0), (3500, 110), (4500, 104.5), (5500, 95.80860066503752), (6000, 87.8245506096177), (6500, 60.50000000000001)]}, 'drivetrain': {'drivetype': 1, 'mounting': 2, 'shift_system': 1, 'gears': [3.545, 1.904, 1.281, 0.951, 0.756], 'final_drive': 3.7, 'reverse': -3.214, 'shift_time': 0.35, 'lsd': (0.0, 0.0, 0.0, 0.0), 'clutch_nm': 250}, 'body': {'mass': 980, 'weight_front': 0.6, 'cm_height': 0.48, 'block': (1.90521449713707, 1.6633805750131614, 3.89442935628891), 'height': 1.6633805750131614, 'length': 3.89442935628891, 'width': 1.90521449713707, 'wheelbase': 2.491, 'model_wheelbase': 2.491, 'track_front': 'auto', 'track_rear': 'auto', 'ride_height': 0.16, 'bbox': (-0.952607248568535, 0.952607248568535, -0.03160861162090327, 1.631771963392258, -1.8064002298355104, 2.0880291264534)}, 'tyres': {'width_front': 185, 'width_rear': 185, 'aspect_front': 45, 'aspect_rear': 45, 'rim_in': 13, 'compound': 3}, 'brakes': {'front_mm': 256, 'front_type': 2, 'front_pistons': 1, 'rear_mm': 230, 'rear_type': 1, 'rear_pistons': 1, 'friction': 1.0}, 'suspension': {'front': (46.59142268041237, 3.334323711340206, 5.001536082474226), 'rear': (29.7879587628866, 2.1318536082474226, 3.197729896907216), 'swaybar_front': 5.910828865979382, 'swaybar_rear': 3.9405525773195875}, 'aero_front': (5.0, 5.0, 0.0, 0.0), 'aero_rear': (0.0, 0.0, 0.0, 0.0), 'car': {'year': 2003, 't60': 12.0, 't100': 50.0, 'top_mph': 110.0, 'price': 10000, 'pi': 0.15, 'drag': 150.0, 'downforce_front': 0.0, 'downforce_rear': -1.0, 'wi_force': 0.45, 'ratings': (3.0, 3.5, 3.0, 3.5, 3.0), 'steer_deg': 35.0, 'class': 1, 'family_model': 1, 'family_body': 1, 'family_special': 1, 'engine_placement': 1, 'powertrain': 0, 'material': 1, 'open_cockpit': 0, 'open_wheel': 0, 'thumbnail_of': 1086, 'bucket': 23}}
ARCH_MATERIALS=['body']
UPGRADE_PROFILE='upgrade_profile.py'

# Reviewed source wheel; mandatory custom geometry, no shared Charger face.
RIM_MATERIALS=['SOURCE_RIM']
RIM_R_REF=0.17779999999999999
RIM_SOURCE_TEXTURE='source_rim'
RIM_CLEAR_DONOR=True
MATERIALS['SOURCE_RIM']=None
TEXTURES['source_rim']=(Image.open(os.path.join(HERE,'textures','source_rim.png')).convert('RGB'),1024,False)
PHYSICS['tyres']={'width_front': 185, 'width_rear': 185, 'aspect_front': 40, 'aspect_rear': 40, 'rim_in': 14, 'compound': 3}
REQUIRE_SOURCE_WHEELS=True
