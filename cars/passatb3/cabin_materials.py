"""Procedural cabin textures; static gauge artwork, no live instrument claims."""
from PIL import Image,ImageDraw
import numpy as np,math

def textures():
 rng=np.random.default_rng(35)
 def grain(rgb):
  a=rng.normal(0,1,(512,512));a=(a+np.roll(a,1,0)+np.roll(a,1,1))/3
  return Image.fromarray(np.clip(np.array(rgb)[None,None,:]+a[:,:,None]*5,0,255).astype('uint8'))
 cloth=grain((43,45,47));d=ImageDraw.Draw(cloth)
 for x in range(0,512,8):d.line((x,0,x,511),fill=(35,37,39))
 gauges=Image.new('RGB',(1024,320),(12,14,15));d=ImageDraw.Draw(gauges)
 for cx,title,maximum in [(275,'km/h',240),(750,'rpm x1000',8)]:
  cy=160;radius=140;d.ellipse((cx-radius,cy-radius,cx+radius,cy+radius),outline=(100,104,107),width=3)
  for i in range(25):
   a=math.radians(140+i*260/24);r0=112 if i%3==0 else 124;r1=134
   xy=(cx+math.cos(a)*r0,cy+math.sin(a)*r0,cx+math.cos(a)*r1,cy+math.sin(a)*r1)
   d.line(xy,fill=(220,225,220) if i<21 else (185,45,35),width=3)
   if i%3==0:
    txt=str(round(maximum*i/24));d.text((cx+math.cos(a)*92-6,cy+math.sin(a)*92-5),txt,fill=(220,225,220),stroke_width=1)
  d.text((cx-30,cy+48),title,fill=(200,208,200))
 d.text((480,277),'PASSAT 16V',fill=(160,170,165))
 return {'cloth':(cloth,512,False),'dash':(grain((27,29,30)),512,False),'trim':(grain((45,46,47)),512,False),'gauges':(gauges,1024,False),'needle':(Image.new('RGB',(64,64),(215,75,38)),512,False)}
