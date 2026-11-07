"""Step 10 (Claude 7 Nov, v0.1.6): the steering wheel's live screen, as on the RB22 (cars/redbullrb22/tyres_screen.py).
The source wheel's LCD (SW_LIT2, a 9.8 x 5.4 cm 'digitalgauge' panel) is built into the steering part as material
SW_SCREEN (prepare_source.py); here its MatI becomes the game's digitalgauge material (DIGITAL_MATI, as used by the
Williams FW24 / Dallara DW12 wheels) and its UV0 is set to the page (the source LCD UVs normalised to 0..1, so the
page keeps the source artwork's orientation). The page UI/<MEDIA>.xaml (1280 x 720, MaxRpm 9000 = the 919's limit,
15 shift lights from 70 to 90 percent of the rev range, flashing at 93 percent) and its LED images are written.
  python3 cars/porsche919/screen.py PKG_DIR"""
from pathlib import Path
import sys,json,re,struct,zipfile
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path[:0]=[str(ROOT/'fh2re'),str(ROOT/'f1'),str(ROOT/'tex')]
from geometry import Part
from body_swap import material_names
from gltf_bridge import layout_of,O_UVT
import uiswatch
MEDIA='POR_Porsche919_17_';CAR=Path(f'media/cars/{MEDIA}.zip')
DIGITAL_MATI=bytes.fromhex('627572470100020060000000bc0000004954414d0100020040000000600000004b0000004b0000005250544d020000005d000000ac0000000d0000000d000000656d614ec000100054535441110014006469676974616c6761756765000000004a47616d653a5c4d656469615c636172735c5f6c6962726172795c6d6174657269616c735c626173656d6174657269616c735c6469676974616c67617567652e6d6174657269616c62696e0000000000000000000000000000000000')


def led_images():
    """84 x 84 LED images (own artwork): a bright lens with a soft halo, for the page's shift lights"""
    yy, xx = np.mgrid[0:84, 0:84]; r = np.hypot(xx - 41.5, yy - 41.5) / 42
    out = {}
    for name, rgb in (('Green', (40, 255, 90)), ('Red', (255, 40, 40)), ('Blue', (60, 140, 255)), ('Off', (70, 70, 76))):
        core = np.clip((0.62 - r) / 0.06, 0, 1); halo = np.clip(1 - r, 0, 1) ** 3 * (0.0 if name == 'Off' else 0.55)
        a = np.clip(core + halo, 0, 1)
        col = np.array(rgb, float)[None, None] * (0.75 + 0.25 * core[..., None]) + 255 * 0.35 * core[..., None] ** 4
        rgba = np.dstack([np.clip(col, 0, 255), a * 255]).astype(np.uint8)
        out[f'UI/Textures/P919_LED_{name}.swatchbin'] = uiswatch.encode(rgba)
    return out


def page_xaml(max_rpm=9000):
    """the Porsche 919's 1280 x 720 display page (same building blocks as the game's DW12 / Williams FW24 pages)"""
    tex = f'game:/media/cars/{MEDIA}/UI/Textures'
    lights = [('Green', i) for i in range(1, 6)] + [('Red', i) for i in range(1, 6)] + [('Blue', i) for i in range(1, 6)]
    names = [f'{c}{i}' for c, i in lights]
    on_at = np.linspace(0.70, 0.90, 15); flash_at = 0.93
    t = lambda x: f'0:0:{x:.3f}'
    prog = []
    for nm, at in zip(names, on_at):
        prog.append(f'\t\t\t<DoubleAnimationUsingKeyFrames Storyboard.TargetProperty="(UIElement.Opacity)" Storyboard.TargetName="{nm}_On">\n'
                    f'\t\t\t\t<DiscreteDoubleKeyFrame KeyTime="{t(at)}" Value="1"/>\n\t\t\t</DoubleAnimationUsingKeyFrames>')
    for nm, at in zip(names, on_at):
        prog.append(f'\t\t\t<ObjectAnimationUsingKeyFrames Storyboard.TargetProperty="(UIElement.Visibility)" Storyboard.TargetName="{nm}_On">\n'
                    f'\t\t\t\t<DiscreteObjectKeyFrame KeyTime="{t(at)}" Value="{{x:Static Visibility.Visible}}"/>\n'
                    f'\t\t\t\t<DiscreteObjectKeyFrame KeyTime="{t(flash_at)}" Value="{{x:Static Visibility.Hidden}}"/>\n\t\t\t</ObjectAnimationUsingKeyFrames>')
    prog.append(f'\t\t\t<ObjectAnimationUsingKeyFrames Storyboard.TargetProperty="(UIElement.Visibility)" Storyboard.TargetName="FLASHING">\n'
                f'\t\t\t\t<DiscreteObjectKeyFrame KeyTime="0" Value="{{x:Static Visibility.Hidden}}"/>\n'
                f'\t\t\t\t<DiscreteObjectKeyFrame KeyTime="{t(flash_at)}" Value="{{x:Static Visibility.Visible}}"/>\n\t\t\t</ObjectAnimationUsingKeyFrames>')
    flash = []
    for nm in names:
        flash.append(f'\t\t\t<ObjectAnimationUsingKeyFrames Storyboard.TargetProperty="(UIElement.Visibility)" Storyboard.TargetName="{nm}_Flashing">\n'
                     f'\t\t\t\t<DiscreteObjectKeyFrame KeyTime="0" Value="{{x:Static Visibility.Visible}}"/>\n'
                     f'\t\t\t\t<DiscreteObjectKeyFrame KeyTime="0:0:0.08" Value="{{x:Static Visibility.Hidden}}"/>\n'
                     f'\t\t\t\t<DiscreteObjectKeyFrame KeyTime="0:0:0.16" Value="{{x:Static Visibility.Hidden}}"/>\n\t\t\t</ObjectAnimationUsingKeyFrames>')
    def row(state, opacity, extra=''):
        imgs = []
        for k, (c, i) in enumerate(lights):
            src = f'{tex}/P919_LED_{"Off" if state == "Off" else c}.png'
            imgs.append(f'\t\t\t\t<Image x:Name="{c}{i}_{state}" Height="76" Width="76" Source="{src}" Stretch="Fill" '
                        f'Canvas.Left="{k * 80}" Canvas.Top="0" Opacity="{opacity}"/>')
        return '\n'.join(imgs)
    text = lambda name, binding, left, top, width, size, align='Center', fg=None: (
        f'\t\t\t<TextBlock x:Name="{name}" TextAlignment="{align}" Canvas.Left="{left}" Canvas.Top="{top}" Width="{width}" '
        f'FontSize="{size}" Style="{{StaticResource TextBlockStyle}}"' + (f' Foreground="{fg}"' if fg else '') +
        (f' Text="{{Binding {binding}}}"/>' if binding else '/>'))
    rpm = '\n'.join(text(f'Text_Rpm_{b}', b, 860, 300, 400, 120) for b in ('Rpm', 'RPM', 'EngineRpm', 'TextTach', 'TachText', 'Revs'))
    label = lambda s, left, top, width, size: (f'\t\t\t<TextBlock TextAlignment="Center" Canvas.Left="{left}" Canvas.Top="{top}" Width="{width}" '
                                               f'FontSize="{size}" Style="{{StaticResource TextBlockStyle}}" Foreground="#FFB8B8BE" Text="{s}"/>')
    return f'''<Page
	xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
	xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
	xmlns:d="http://schemas.microsoft.com/expression/blend/2008"
	xmlns:System="clr-namespace:System;assembly=mscorlib"
	xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
	xmlns:local="clr-namespace:ForzaUI"
	mc:Ignorable="d"
	x:Class="DigitalGauge.{MEDIA}"
	DataContext="{{Binding RelativeSource={{x:Static RelativeSource.Self}}}}">

	<Page.Resources>
		<Style x:Key="TextBlockStyle" TargetType="{{x:Type TextBlock}}">
			<Setter Property="FontFamily" Value="DG5_QuartzMS"/>
			<Setter Property="Foreground" Value="White"/>
			<Setter Property="TextWrapping" Value="NoWrap"/>
			<Setter Property="TextAlignment" Value="Right"/>
		</Style>

		<local:DigitalGaugeConfig x:Key="Config" HasClock="False" HasExternalTemp="False" UseDegreesF="True" UseMPH="True" UsePsi="True" MaxBoost="0" MinBoost="0" MaxSpeed="000" HasAbsLight="False" HasStmLight="False" HasTcsLight="False" HasGAccelX="False" HasGAccelY="False" HasShiftLights="True" HasTextTach="True" HasLapPlaceInfo="True" HasTextBoost="False" HasTextGAccel="False" HasTextOdometer="False" HasTextFuel="False" MaxFuel="0" MaxGear="0" MaxRpm="{max_rpm}"></local:DigitalGaugeConfig>

		<Storyboard x:Key="Start Up Animation">
			<DoubleAnimationUsingKeyFrames Storyboard.TargetProperty="(UIElement.Opacity)" Storyboard.TargetName="Start_Up_Mask">
				<EasingDoubleKeyFrame KeyTime="0" Value="1"/>
				<EasingDoubleKeyFrame KeyTime="0:0:1" Value="0"/>
			</DoubleAnimationUsingKeyFrames>
		</Storyboard>
		<Storyboard x:Key="Shift Lights Progress">
{chr(10).join(prog)}
		</Storyboard>
		<Storyboard x:Key="Shift Lights Flash" RepeatBehavior="Forever">
{chr(10).join(flash)}
		</Storyboard>
	</Page.Resources>
	<Page.Triggers>
		<EventTrigger RoutedEvent="FrameworkElement.Loaded" SourceName="LayoutRoot">
			<BeginStoryboard Storyboard="{{StaticResource Shift Lights Flash}}"/>
		</EventTrigger>
	</Page.Triggers>

	<Canvas x:Name="LayoutRoot" Background="Transparent" Width="1280" Height="720">
		<VisualStateManager.VisualStateGroups>
			<VisualStateGroup x:Name="NightDaySplit">
				<VisualState x:Name="Day"/>
				<VisualState x:Name="Night"/>
			</VisualStateGroup>
		</VisualStateManager.VisualStateGroups>
		<Canvas x:Name="Background" Height="720" Width="1280">
			<Rectangle Fill="#FF05060A" Height="720" Canvas.Left="0" Canvas.Top="0" Width="1280"/>
			<Rectangle Fill="#FFB3001B" Height="6" Canvas.Left="40" Canvas.Top="128" Width="1200"/>
			<Rectangle Fill="#FFB3001B" Height="420" Canvas.Left="438" Canvas.Top="170" Width="6"/>
			<Rectangle Fill="#FFB3001B" Height="420" Canvas.Left="836" Canvas.Top="170" Width="6"/>
		</Canvas>
		<Canvas x:Name="Shift_Lights" Height="76" Canvas.Left="42" Canvas.Top="30">
			<Canvas x:Name="OFF" Canvas.Left="0" Canvas.Top="0">
{row("Off", 1)}
			</Canvas>
			<Canvas x:Name="ON" Canvas.Left="0" Canvas.Top="0" Opacity="1">
{row("On", 0)}
			</Canvas>
			<Canvas x:Name="FLASHING" Canvas.Left="0" Canvas.Top="0" Opacity="1" Visibility="Hidden">
{row("Flashing", 1)}
			</Canvas>
		</Canvas>
		<Canvas x:Name="Text" Height="720" Width="1280">
{text("Text_Speed", "Speed", 20, 300, 400, 150)}
{label("MPH", 20, 480, 400, 54)}
{text("Text_Gear", "Gear", 444, 150, 392, 400, fg="#FFFFD200")}
{rpm}
{label("RPM", 860, 480, 400, 54)}
{label("PORSCHE 919 HYBRID", 0, 630, 1280, 46)}
			<TextBlock x:Name="Text_Place_Min" Visibility="Hidden" TextAlignment="Left" Canvas.Left="60" Canvas.Top="630" Width="190" FontSize="60" Style="{{StaticResource TextBlockStyle}}">
				<Run Text="P"/>
				<Run Text="{{Binding CurPlace}}"/>
			</TextBlock>
		</Canvas>
		<Rectangle x:Name="Start_Up_Mask" Fill="Black" Height="720" Width="1280" Canvas.Left="0" Canvas.Top="0" Opacity="0"/>

		<!-- Storyboard binding controllers -->
		<local:StoryboardController SeekPct="{{Binding Tach}}" Target="{{StaticResource Shift Lights Progress}}"/>
	</Canvas>
</Page>
'''


def check_xaml(text):
    import xml.etree.ElementTree as ET
    root = ET.fromstring(text)
    names = set(re.findall(r'x:Name="([^"]+)"', text))
    targets = set(re.findall(r'Storyboard\.TargetName="([^"]+)"', text))
    assert targets <= names, f'storyboard targets without an element: {sorted(targets - names)}'
    keys = set(re.findall(r'x:Key="([^"]+)"', text)); used = set(re.findall(r'StaticResource ([^}]+)\}', text))
    assert used <= keys, sorted(used - keys)
    srcs = sorted(set(re.findall(r'Source="([^"]+)"', text)))
    return dict(elements=len(names), storyboard_targets=len(targets), images=srcs)



def set_screen(raw,mat_name):
 """the screen meshes (built into steering group 0, whose layout has no TEXCOORD0) move to group 2, whose layout
 NORMAL0 / TEXCOORD0 / TEXCOORD2 is the Williams FW24's digitalGauge layout; TEXCOORD0 = the page (the built texture
 UVs normalised to 0..1, keeping the source LCD artwork's orientation)"""
 from gltf_bridge import decode_group,encode_group
 from geometry import O_LAYOUT,O_NVB,O_VB0
 p=Part(raw);names=material_names(p)
 blobs=[b for b in p.b.blobs if b['tag']=='MatI' and p.b.meta(b,'Name').decode()==mat_name];assert blobs,mat_name
 for b in blobs:b['data']=bytearray(DIGITAL_MATI)
 rs=[r for r in p.render if names[id(r['blob'])]==mat_name];assert rs and all(r['group']==0 for r in rs)
 ids=sorted({i for r in rs for i in r['indices']})
 others={i for r in p.render if r['group']==0 and r not in rs for i in r['indices']};assert not (set(ids)&others),'screen vertices shared'
 A0,els0=decode_group(p,0);uvk='TEXCOORD0' if 'TEXCOORD0' in A0 else 'TEXCOORD1'
 uv=A0[uvk][ids].astype(np.float64);lo,hi=uv.min(0),uv.max(0);page=(uv-lo)/np.maximum(hi-lo,1e-9)
 G=2;g=p.groups[G];A2,els2=decode_group(p,G);assert [e['name'] for e in els2]==['NORMAL0','TEXCOORD0','TEXCOORD2'],els2
 n2=len(g['positions'])
 new={'POSITION':A0['POSITION'][ids],'NORMAL0':A0['NORMAL0'][ids],'TEXCOORD0':page.astype(np.float32),'TEXCOORD2':A0['TEXCOORD2'][ids]}
 allA={k:np.concatenate([np.asarray(A2[k],np.float32),np.asarray(new[k],np.float32)]) for k in ['POSITION','NORMAL0','TEXCOORD0','TEXCOORD2']}
 rows,uvt=encode_group(p,G,allA);g['positions']=[tuple(map(float,v)) for v in allA['POSITION']];g['attrs']=rows
 if g['morph'] is not None:g['morph']=list(g['morph'])+[g['morph'][0]]*len(ids)
 ref=next(r for r in p.render if r['group']==G);lay=struct.unpack_from('<I',ref['blob']['data'],O_LAYOUT)[0]
 stride=p.bufs[('VerB',G)]['stride'];remap={o:n2+k for k,o in enumerate(ids)}
 for r in p.render:
  if r['group']==G:struct.pack_into('<20f',r['blob']['data'],O_UVT,*uvt)
 for r in rs:
  d=r['blob']['data'];struct.pack_into('<I',d,O_LAYOUT,lay);moved=0
  for k in range(struct.unpack_from('<I',d,O_NVB)[0]):
   vid=struct.unpack_from('<i',d,O_VB0+16*k)[0]
   if vid==0:struct.pack_into('<i',d,O_VB0+16*k,G);struct.pack_into('<i',d,O_VB0+16*k+8,stride);moved+=1
  assert moved==1,moved
  r['group']=G;r['indices']=[remap[i] for i in r['indices']];struct.pack_into('<20f',d,O_UVT,*uvt)
 out=p.build();q=Part(out);qn=material_names(q)
 qs=[r for r in q.render if qn[id(r['blob'])]==mat_name];assert qs and all(r['group']==G for r in qs)
 QA,_=decode_group(q,G);pg=QA['TEXCOORD0'][sorted({i for r in qs for i in r['indices']})]
 assert pg.min()>-1e-3 and pg.max()<1+1e-3,(pg.min(),pg.max())
 return out,dict(meshes=len(rs),vertices=len(ids),group=G,uv_source=uvk,screen_size_m=[round(float(x),4) for x in np.ptp(A0['POSITION'][ids],0)])

def apply(pkg):
 A=json.loads((HERE/'source-analysis.json').read_text());mat=f"{MEDIA.lower()}_{A['mapping']['SW_SCREEN'][1]}"
 arc=pkg/CAR
 with zipfile.ZipFile(arc) as z:infos=z.infolist();E={i.filename:z.read(i) for i in infos}
 have={i.filename for i in infos}
 sw=next(n for n in E if n.lower().endswith('steeringwheel_a.modelbin'));E[sw],rep=set_screen(E[sw],mat)
 xaml=page_xaml();rep['page']=check_xaml(xaml)
 ui=next((n for n in E if n.lower()==f'ui/{MEDIA.lower()}.xaml'),f'UI/{MEDIA}.xaml');new={}
 E[ui]=xaml.encode('utf-8')
 if ui not in have:new[ui]=E[ui]
 for k,v in led_images().items():
  E[k]=v
  if k not in have:new[k]=v
 for src in rep['page']['images']:assert 'UI/Textures/'+src.rsplit('/',1)[1][:-4]+'.swatchbin' in E,src
 tmp=arc.with_suffix('.tmp')
 with zipfile.ZipFile(tmp,'w') as z:
  for i in infos:z.writestr(i,E[i.filename])
  for k,v in new.items():
   zi=zipfile.ZipInfo(k,date_time=(1980,1,1,0,0,0));zi.compress_type=zipfile.ZIP_DEFLATED;z.writestr(zi,v)
 tmp.replace(arc)
 with zipfile.ZipFile(arc) as z:assert z.testzip() is None
 rep.update(valid=True,ui=ui,max_rpm=9000,runtime_status='Pending cockpit view')
 (pkg/'screen-check.json').write_text(json.dumps(rep,indent=2)+'\n');print(json.dumps(rep)[:400])
if __name__=='__main__':apply(Path(sys.argv[1]))
