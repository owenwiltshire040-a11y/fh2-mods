"""Opel Vectra C — personal prototype. Dimensions based on source axle measurements.
Engine, handling, cockpit and lamps need an in-game review; see BUILD-NOTES.txt.
"""
import os
from PIL import Image
HERE=os.path.dirname(os.path.abspath(__file__))
MEDIA='OPE_daily09_2003__'
DONOR_ZIP=os.path.join(HERE,'donor_'+MEDIA+'.zip')
GEO=os.path.join(HERE,'geo.pkl')
TEXTURES={}
TEXTURES['ta25c30f4']=(Image.open(os.path.join(HERE,'textures','ta25c30f4.png')),512,False)
TEXTURES['tb4093013']=(Image.open(os.path.join(HERE,'textures','tb4093013.png')),512,False)
TEXTURES['tb0b16f5b']=(Image.open(os.path.join(HERE,'textures','tb0b16f5b.png')),512,False)
TEXTURES['tfe709db9']=(Image.open(os.path.join(HERE,'textures','tfe709db9.png')),512,False)
TEXTURES['tf457f513']=(Image.open(os.path.join(HERE,'textures','tf457f513.png')),512,False)
TEXTURES['t55246a20']=(Image.open(os.path.join(HERE,'textures','t55246a20.png')),512,False)
TEXTURES['ta04b9a82']=(Image.open(os.path.join(HERE,'textures','ta04b9a82.png')),512,False)
TEXTURES['t812dd69f']=(Image.open(os.path.join(HERE,'textures','t812dd69f.png')),512,False)
TEXTURES['t430cd6cf']=(Image.open(os.path.join(HERE,'textures','t430cd6cf.png')),512,False)
TEXTURES['tf0689eba']=(Image.open(os.path.join(HERE,'textures','tf0689eba.png')),512,False)
TEXTURES['tba400ffc']=(Image.open(os.path.join(HERE,'textures','tba400ffc.png')),512,False)
TEXTURES['t09a0525e']=(Image.open(os.path.join(HERE,'textures','t09a0525e.png')),512,False)
TEXTURES['tbc9f39d0']=(Image.open(os.path.join(HERE,'textures','tbc9f39d0.png')),512,False)
TEXTURES['ta262c1a4']=(Image.open(os.path.join(HERE,'textures','ta262c1a4.png')),512,False)
TEXTURES['t28ee05f4']=(Image.open(os.path.join(HERE,'textures','t28ee05f4.png')),512,False)
TEXTURES['t24d7ff70']=(Image.open(os.path.join(HERE,'textures','t24d7ff70.png')),512,False)
TEXTURES['tf7a365bb']=(Image.open(os.path.join(HERE,'textures','tf7a365bb.png')),512,False)
TEXTURES['t4237b493']=(Image.open(os.path.join(HERE,'textures','t4237b493.png')),512,False)
TEXTURES['tce522641']=(Image.open(os.path.join(HERE,'textures','tce522641.png')),512,False)
TEXTURES['tbed0efc1']=(Image.open(os.path.join(HERE,'textures','tbed0efc1.png')),512,False)
TEXTURES['t47e0d94d']=(Image.open(os.path.join(HERE,'textures','t47e0d94d.png')),512,False)
TEXTURES['ta7d411ec']=(Image.open(os.path.join(HERE,'textures','ta7d411ec.png')),512,False)
TEXTURES['t7e5a5d21']=(Image.open(os.path.join(HERE,'textures','t7e5a5d21.png')),512,False)
TEXTURES['tc5faf267']=(Image.open(os.path.join(HERE,'textures','tc5faf267.png')),512,False)
TEXTURES['t03c74121']=(Image.open(os.path.join(HERE,'textures','t03c74121.png')),512,False)
TEXTURES['t3d33967e']=(Image.open(os.path.join(HERE,'textures','t3d33967e.png')),512,False)
TEXTURES['t4a5417ec']=(Image.open(os.path.join(HERE,'textures','t4a5417ec.png')),512,False)
TEXTURES['tefdc41f1']=(Image.open(os.path.join(HERE,'textures','tefdc41f1.png')),512,False)
TEXTURES['tb477e726']=(Image.open(os.path.join(HERE,'textures','tb477e726.png')),512,False)
TEXTURES['t14ddc268']=(Image.open(os.path.join(HERE,'textures','t14ddc268.png')),512,False)
TEXTURES['tfd57f22c']=(Image.open(os.path.join(HERE,'textures','tfd57f22c.png')),512,False)
MATERIALS={'htvectrac_frame': ('textured', 'ta25c30f4'), 'htvectrac_interior_metal': ('textured', 'tb4093013'), 'htvectrac_interior': ('textured', 'tb0b16f5b'), 'htvectrac_body': ('plain', 'paint'), 'clearglass': ('textured', 'tfe709db9'), 'htvectrac_glass': ('plain', 'glass'), 'htvectrac_bord': ('textured', 'tf457f513'), 'htvectrac_int_parkingbrake': ('textured', 't55246a20'), 'htvectrac_int_highbeam': ('textured', 'ta04b9a82'), 'htvectrac_int_lowbeam': ('textured', 't812dd69f'), 'htvectrac_int_signal_R': ('textured', 't430cd6cf'), 'htvectrac_int_signal_L': ('textured', 'tf0689eba'), 'htvectrac_metal_gray': ('textured', 'tba400ffc'), 'htvectrac_metal': ('textured', 't09a0525e'), 'htvectrac_plastic_black': ('textured', 'tbc9f39d0'), 'htvectrac_wood': ('textured', 'ta262c1a4'), 'htvectrac_gauge': ('textured', 't28ee05f4'), 'htvectrac_intlight': ('textured', 't24d7ff70'), 'htvectrac_chrome': ('plain', 'chrome'), 'htvectrac_highbeam': ('textured', 'tf7a365bb'), 'htvectrac_signal_R': ('textured', 't4237b493'), 'htvectrac_lowbeam': ('textured', 'tce522641'), 'htvectrac_signal_L': ('textured', 'tbed0efc1'), 'htvectrac_glass_lights': ('textured', 't47e0d94d'), 'htvectrac_chmsl': ('textured', 'ta7d411ec'), 'htvectrac_reverse': ('textured', 't7e5a5d21'), 'htvectrac_taillight': ('textured', 'tc5faf267'), 'htvectrac_blue': ('textured', 't03c74121'), 'htvectrac_yellow': ('textured', 't3d33967e'), 'htvectrac_white': ('textured', 't4a5417ec'), 'htvectrac_engine_symbols': ('textured', 'tefdc41f1'), 'htvectrac_black': ('textured', 'tb477e726'), 'htvectrac_lights': ('textured', 't14ddc268'), 'mirror': ('plain', 'chrome'), 'glass_invisible': ('textured', 'tfd57f22c')}
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
STEER=(-0.34, 0.5789245283018868, 0.4)
HIPS=(-0.34, 0.2885471698113208, -0.05)
EYE=(-0.34, 1.0068490566037736, 0.0)
DRIVER_ANIMS_ZIP=None
AVPINS_TEMPLATE=None
PRESENT={'paint': '6b92b1', 'use_make': (304, '_&857996988'), 'depends': 'owen-daily05'}
PHYSICS={'car_id': 5009, 'make_offset': 108, 'make': 'Opel', 'make_profile': 'Opel', 'make_code': 'OPE', 'make_country': 7, 'make_icon': 'ARI', 'string_base': 65224, 'colour_offset': 2300, 'name': 'Vectra C', 'short_name': 'Vectra C', 'engine': {'name': '1.8L I4', 'sound': 'FOR_Fiesta_09', 'mass': 110.0, 'compression': 10.5, 'config': 3, 'cylinders': 1, 'aspiration': 1, 'boost': 0.0, 'inertia': 0.16, 'tank': 35, 'displacement': 1796, 'peak_hp': 120, 'peak_nm': 167, 'redline': 6500, 'stall': 750.0, 'start': 3000.0, 'curve': [(0, 50.1), (1000, 83.5), (2000, 133.6), (3500, 167), (4500, 158.65), (5500, 150.3), (6000, 133.6), (6500, 91.85000000000001)]}, 'drivetrain': {'drivetype': 1, 'mounting': 2, 'shift_system': 1, 'gears': [3.545, 1.904, 1.281, 0.951, 0.756], 'final_drive': 3.7, 'reverse': -3.214, 'shift_time': 0.35, 'lsd': (0.0, 0.0, 0.0, 0.0), 'clutch_nm': 250.5}, 'body': {'mass': 1400, 'weight_front': 0.6, 'cm_height': 0.48, 'block': (1.9750061664941176, 1.3550739934984253, 4.511995567465728), 'height': 1.3550739934984253, 'length': 4.511995567465728, 'width': 1.9750061664941176, 'wheelbase': 2.7, 'model_wheelbase': 2.7, 'track_front': 'auto', 'track_rear': 'auto', 'ride_height': 0.16, 'bbox': (-0.9875030832470588, 0.9875030832470588, 0.01205697481137355, 1.3671309683097987, -2.175176716253892, 2.3368188512118357)}, 'tyres': {'width_front': 185, 'width_rear': 185, 'aspect_front': 55, 'aspect_rear': 55, 'rim_in': 16, 'compound': 3}, 'brakes': {'front_mm': 280, 'front_type': 2, 'front_pistons': 1, 'rear_mm': 230, 'rear_type': 2, 'rear_pistons': 1, 'friction': 1.0}, 'suspension': {'front': (66.55917525773195, 4.763319587628866, 7.145051546391752), 'rear': (42.55422680412371, 3.0455051546391756, 4.568185567010309), 'swaybar_front': 5.910828865979382, 'swaybar_rear': 3.9405525773195875}, 'aero_front': (5.0, 5.0, 0.0, 0.0), 'aero_rear': (0.0, 0.0, 0.0, 0.0), 'car': {'year': 2003, 't60': 12.0, 't100': 50.0, 'top_mph': 110.0, 'price': 10000, 'pi': 0.15, 'drag': 150.0, 'downforce_front': 0.0, 'downforce_rear': -1.0, 'wi_force': 0.45, 'ratings': (3.0, 3.5, 3.0, 3.5, 3.0), 'steer_deg': 35.0, 'class': 1, 'family_model': 1, 'family_body': 1, 'family_special': 1, 'engine_placement': 1, 'powertrain': 0, 'material': 1, 'open_cockpit': 0, 'open_wheel': 0, 'thumbnail_of': 1086, 'bucket': 23}}
ARCH_MATERIALS=['htvectrac_body']
UPGRADE_PROFILE='upgrade_profile.py'

# Reviewed source wheel; mandatory custom geometry, no shared Charger face.
RIM_MATERIALS=['SOURCE_RIM']
RIM_R_REF=0.2032
RIM_SOURCE_TEXTURE='source_rim'
RIM_CLEAR_DONOR=True
MATERIALS['SOURCE_RIM']=None
TEXTURES['source_rim']=(Image.open(os.path.join(HERE,'textures','source_rim.png')).convert('RGB'),1024,False)
PHYSICS['tyres']={'width_front': 195, 'width_rear': 195, 'aspect_front': 55, 'aspect_rear': 55, 'rim_in': 16, 'compound': 3}
REQUIRE_SOURCE_WHEELS=True
