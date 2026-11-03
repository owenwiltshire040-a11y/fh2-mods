"""Bounded camera presets, consumed on the native car-view update callback."""
from pathlib import Path
import json,os,struct,time
R=Path(__file__).resolve().parent
REQUEST=struct.Struct('<8sIIII40x');ACK=struct.Struct('<8sIIIIfffII9f48x')
assert REQUEST.size==64 and ACK.size==128
PRESETS={'front':2,'right':3,'rear':4,'left':1,'front-quarter':6,'rear-quarter':5}

def read_ack():
 p=R/'runtime/refresh/camera-ack.bin'
 try:raw=p.read_bytes()
 except FileNotFoundError:return None
 if len(raw)!=128:return None
 magic,version,serial,code,view,fov,pitch,yaw,outer,inner,*orbit=ACK.unpack(raw)
 if magic!=b'FH2CACK\0' or version!=1:return None
 return dict(serial=serial,code=code,view=view,yaw=yaw,pitch=pitch,fov=fov,camera_type=hex(outer),inner_type=hex(inner),orbit=orbit)

def command(kind,view=0,allow_unsupported=False):
 if kind not in [0,1,2,3] or view not in range(7):raise ValueError('Invalid camera command')
 q=R/'runtime/refresh';q.mkdir(exist_ok=True);p=q/'camera.bin'
 try:last=REQUEST.unpack(p.read_bytes())[2]
 except FileNotFoundError:last=0
 serial=last+1;tmp=q/'camera.tmp';tmp.write_bytes(REQUEST.pack(b'FH2CAM1',1,serial,kind,view));os.replace(tmp,p)
 until=time.monotonic()+8
 while time.monotonic()<until:
  ack=read_ack()
  if ack and ack['serial']==serial:
   if ack['code']>=10 and not allow_unsupported:raise ValueError('Native camera unavailable: '+json.dumps(ack))
   return ack
  time.sleep(.1)
 raise ValueError('The car-view camera did not respond')
if __name__=='__main__':print(json.dumps(command(0),indent=2))
