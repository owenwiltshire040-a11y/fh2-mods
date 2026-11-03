"""Opel Zafira A — personal prototype. Dimensions based on source axle measurements.
Engine, handling, cockpit and lamps need an in-game review; see BUILD-NOTES.txt.
"""
import os
from PIL import Image
HERE=os.path.dirname(os.path.abspath(__file__))
MEDIA='OPE_daily10_2002__'
DONOR_ZIP=os.path.join(HERE,'donor_'+MEDIA+'.zip')
GEO=os.path.join(HERE,'geo.pkl')
TEXTURES={}
TEXTURES['ta6f9cfff']=(Image.open(os.path.join(HERE,'textures','ta6f9cfff.png')),512,False)
TEXTURES['td9215183']=(Image.open(os.path.join(HERE,'textures','td9215183.png')),512,False)
TEXTURES['t30c91e7d']=(Image.open(os.path.join(HERE,'textures','t30c91e7d.png')),512,False)
TEXTURES['t49bbcc7c']=(Image.open(os.path.join(HERE,'textures','t49bbcc7c.png')),512,False)
TEXTURES['tf0ba5745']=(Image.open(os.path.join(HERE,'textures','tf0ba5745.png')),512,False)
TEXTURES['t45926fc3']=(Image.open(os.path.join(HERE,'textures','t45926fc3.png')),512,False)
TEXTURES['t46b99c22']=(Image.open(os.path.join(HERE,'textures','t46b99c22.png')),512,False)
TEXTURES['t6ba1a94c']=(Image.open(os.path.join(HERE,'textures','t6ba1a94c.png')),512,False)
TEXTURES['tf4bf9773']=(Image.open(os.path.join(HERE,'textures','tf4bf9773.png')),512,False)
TEXTURES['ta59248a2']=(Image.open(os.path.join(HERE,'textures','ta59248a2.png')),512,False)
TEXTURES['t5dd26889']=(Image.open(os.path.join(HERE,'textures','t5dd26889.png')),512,False)
TEXTURES['t884dc97d']=(Image.open(os.path.join(HERE,'textures','t884dc97d.png')),512,False)
MATERIALS={'Carro_Vidros_Vermelhos': ('textured', 'ta6f9cfff'), 'Carro_Vidros1': ('plain', 'glass'), 'Carro_Vidros': ('plain', 'glass'), 'Carro_Vidro_Laranja': ('textured', 'td9215183'), 'Carro_Refletor_Lanterna': ('textured', 't30c91e7d'), 'Carro_Refletor_Farol_1': ('textured', 't49bbcc7c'), 'Carro_Refletor_Farol': ('textured', 'tf0ba5745'), 'Carro_Plastico': ('textured', 't45926fc3'), 'Carro_Pintura': ('plain', 'paint'), 'Carro_Metal_Preto': ('textured', 't46b99c22'), 'Carro_Metal_Laranja': ('textured', 't6ba1a94c'), 'Carro_Metal_Lanterna_Traseira': ('textured', 'tf4bf9773'), 'Carro_Metal_Farol': ('textured', 'ta59248a2'), 'Carro_Metal_Amarelo': ('textured', 't5dd26889'), 'Carro_Interno': ('textured', 't884dc97d')}
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
STEER=(-0.34, 0.5754996991150442, 0.4)
HIPS=(-0.34, 0.28744633185840707, -0.05)
EYE=(-0.34, 0.9999993982300884, 0.0)
DRIVER_ANIMS_ZIP=None
AVPINS_TEMPLATE=None
PRESENT={'paint': '6b92b1', 'use_make': (304, '_&857996988'), 'depends': 'owen-daily05'}
PHYSICS={'car_id': 5010, 'make_offset': 109, 'make': 'Opel', 'make_profile': 'Opel', 'make_code': 'OPE', 'make_country': 7, 'make_icon': 'ARI', 'string_base': 65227, 'colour_offset': 2400, 'name': 'Zafira A', 'short_name': 'Zafira A', 'engine': {'name': '1.8L I4', 'sound': 'FOR_Fiesta_09', 'mass': 110.0, 'compression': 10.5, 'config': 3, 'cylinders': 1, 'aspiration': 1, 'boost': 0.0, 'inertia': 0.16, 'tank': 35, 'displacement': 1796, 'peak_hp': 123, 'peak_nm': 170, 'redline': 6500, 'stall': 750.0, 'start': 3000.0, 'curve': [(0, 51.0), (1000, 85.0), (2000, 136.0), (3500, 170), (4500, 161.5), (5500, 153.0), (6000, 136.0), (6500, 93.50000000000001)]}, 'drivetrain': {'drivetype': 1, 'mounting': 2, 'shift_system': 1, 'gears': [3.545, 1.904, 1.281, 0.951, 0.756], 'final_drive': 3.7, 'reverse': -3.214, 'shift_time': 0.35, 'lsd': (0.0, 0.0, 0.0, 0.0), 'clutch_nm': 255.0}, 'body': {'mass': 1393, 'weight_front': 0.6, 'cm_height': 0.48, 'block': (1.9476408299091643, 1.507189645967653, 4.310370178349251), 'height': 1.507189645967653, 'length': 4.310370178349251, 'width': 1.9476408299091643, 'wheelbase': 2.694, 'model_wheelbase': 2.694, 'track_front': 'auto', 'track_rear': 'auto', 'ride_height': 0.16, 'bbox': (-0.9738204149545822, 0.9738204149545822, 0.0031776829783680127, 1.510367328946021, -2.072294670724447, 2.2380755076248033)}, 'tyres': {'width_front': 185, 'width_rear': 185, 'aspect_front': 55, 'aspect_rear': 55, 'rim_in': 16, 'compound': 3}, 'brakes': {'front_mm': 280, 'front_type': 2, 'front_pistons': 1, 'rear_mm': 230, 'rear_type': 2, 'rear_pistons': 1, 'friction': 1.0}, 'suspension': {'front': (66.2263793814433, 4.739502989690721, 7.109326288659793), 'rear': (42.341455670103095, 3.030277628865979, 4.545344639175257), 'swaybar_front': 5.910828865979382, 'swaybar_rear': 3.9405525773195875}, 'aero_front': (5.0, 5.0, 0.0, 0.0), 'aero_rear': (0.0, 0.0, 0.0, 0.0), 'car': {'year': 2002, 't60': 12.0, 't100': 50.0, 'top_mph': 110.0, 'price': 10000, 'pi': 0.15, 'drag': 150.0, 'downforce_front': 0.0, 'downforce_rear': -1.0, 'wi_force': 0.45, 'ratings': (3.0, 3.5, 3.0, 3.5, 3.0), 'steer_deg': 35.0, 'class': 1, 'family_model': 1, 'family_body': 1, 'family_special': 1, 'engine_placement': 1, 'powertrain': 0, 'material': 1, 'open_cockpit': 0, 'open_wheel': 0, 'thumbnail_of': 1086, 'bucket': 23}}
ARCH_MATERIALS=['Carro_Pintura']
UPGRADE_PROFILE='upgrade_profile.py'

# Reviewed source wheel; mandatory custom geometry, no shared Charger face.
RIM_MATERIALS=['SOURCE_RIM']
RIM_R_REF=0.2032
RIM_SOURCE_TEXTURE='source_rim'
RIM_CLEAR_DONOR=True
MATERIALS['SOURCE_RIM']=None
TEXTURES['source_rim']=(Image.open(os.path.join(HERE,'textures','source_rim.png')).convert('RGB'),1024,False)
PHYSICS['tyres']={'width_front': 195, 'width_rear': 195, 'aspect_front': 50, 'aspect_rear': 50, 'rim_in': 16, 'compound': 3}
REQUIRE_SOURCE_WHEELS=True
