"""Read-only inventory for an FH2 engine-backed preview host. Never launches or patches the game."""
from pathlib import Path
import argparse,hashlib,json,struct,zipfile,sqlite3,xml.etree.ElementTree as E,shutil
BASE=Path(__file__).resolve().parent
DEFAULT=Path('/Users/owen/Library/Application Support/CrossOver/Bottles/Azimuth/drive_c')
def pe(path):
 data=path.read_bytes();u16=lambda o:struct.unpack_from('<H',data,o)[0];u32=lambda o:struct.unpack_from('<I',data,o)[0]
 nt=u32(0x3c);opt=nt+24;plus=u16(opt)==0x20b;dd=opt+(112 if plus else 96);sections=[]
 for i in range(u16(nt+6)):
  o=opt+u16(nt+20)+i*40;sections.append((u32(o+12),max(u32(o+8),u32(o+16)),u32(o+20)))
 def off(r):
  for start,size,raw in sections:
   if start<=r<start+size:return raw+r-start
  return r
 def string(r):
  n=off(r);return data[n:data.index(b'\0',n)].decode('ascii',errors='replace')
 imports=[];r=u32(dd+8)
 if r:
  o=off(r)
  while any(data[o:o+20]):imports.append(string(u32(o+12)));o+=20
 exports=[];r=u32(dd)
 if r:
  o=off(r);count=u32(o+24);names=off(u32(o+32))
  exports=[string(u32(names+i*4)) for i in range(count)]
 return dict(path=str(path),bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),machine=hex(u16(nt+4)),image_size=u32(opt+56),imports=imports,exports=exports)
def main():
 a=argparse.ArgumentParser();a.add_argument('--drive-c',type=Path,default=DEFAULT);x=a.parse_args();drive=x.drive_c
 game=drive/'Anthem_1.0.0.64_x64__8wekyb3d8bbwe/Mount';host=drive/'azimuth-windows';media=game/'media';src=BASE/'eo-0.3.9-source'
 manifest=json.loads((src/'patches.json').read_text());binary=pe(game/'forza_durango_release_final.exe')
 binaries={p.name:pe(p) for p in [host/'azimuth.exe',host/'winmm.dll',host/'d3d12.dll']}
 z=zipfile.ZipFile(media/'stateflow.zip');flow={};states={}
 for name in z.namelist():
  if not name.endswith('.xml'):continue
  root=E.fromstring(z.read(name));group=root.get('id',Path(name).stem)
  for s in root.findall('state'):states[group+'.'+s.get('id','')]=(name,s)
 selected=['garage.view_car_in_homespace','global.load_homespace','global.show_homespace','global.load_ui_car','global.unload_ui_car','global.setup_ui_car_for_in_memory_homespace','ui_screens.show_view_car_from_pause','boot.root']
 evidence=BASE/'flow-evidence';evidence.mkdir(exist_ok=True)
 for key in selected:
  if key not in states:continue
  name,state=states[key];(evidence/(key+'.xml')).write_text(E.tostring(state,encoding='unicode')+'\n')
  flow[key]=dict(archive_entry=name,nodes=[dict(n.attrib) for n in state.findall('node')],behaviors=[dict(n.attrib) for n in state.findall('behavior')])
 shader=zipfile.ZipFile(media/'_library/Shaders.zip');ns=shader.namelist()
 counts=dict(total=len(ns),shaderbin=sum(n.endswith('.shaderbin') for n in ns),pc_vertex=sum(n.endswith('.pc.vso') for n in ns),pc_pixel=sum(n.endswith('.pc.pso') for n in ns),durango_vertex=sum(n.endswith('.durango.vso') for n in ns),durango_pixel=sum(n.endswith('.durango.pso') for n in ns))
 inventory={}
 for rel in ['tracks/homespace02','shaderpatch','renderscenarios']:
  files=[p for p in (media/rel).rglob('*') if p.is_file()];inventory[rel]=dict(files=len(files),bytes=sum(p.stat().st_size for p in files))
 c=sqlite3.connect((media/'stripped/gamedbRC.slt').as_uri()+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
 cols=[r[1] for r in c.execute('pragma table_info(Tracks)')];idcol=next(k for k in cols if k.lower() in ('id','trackid'));track=[dict(r) for r in c.execute('SELECT * FROM Tracks WHERE "'+idcol+'"=308')];c.close()
 log=(host/'FH2_ExtraOptions.log').read_text(errors='replace');versions=[s for s in log.splitlines() if s.startswith('Forza Horizon 2 Extra Options') or s.startswith('AZIMUTH: 1.')]
 requirements=dict(status='Static feasibility audit; engine preview not built or runtime-tested',preferred_route='Windows preview plugin hosted by the existing Azimuth/CrossOver stack, using native homespace/UI-car rendering',retain_existing_installation=True,already_available=['FH2 executable matching official Extra Options supported input','Original shader library and shader patch files','Homespace02 scene, render scenarios, time-of-day and camera assets','Game DB and Extra Options merged mod DB/media mechanism','Working Azimuth 1.0.3 / Extra Options 0.3.9 installation reported by logs'],unknowns=['Boot to homespace without first loading free roam','Resolve native car-selection data before requesting LoadUICar','Unload/reload rebuilt geometry and textures rather than cached resources','Reload database/upgrade changes; current EO database merge is tied to initialization','Establish readiness and run requests on the owning game/UI thread','Orbit/cockpit camera and lights/brake/indicator controls in UI-car context','Capture actual rendered frames and optionally suspension/steering state'],standalone_native_mac='No callable standalone engine library identified in inspected files. A native host would require a separate port/reimplementation or supported engine/runtime interface; shaders alone are insufficient.',first_proof=['Use an isolated profile and settings/media overlay; preserve live saves and mods','Initialize a diagnostics plugin on the installed versions, guarded by exact binary identity','Display one stock car using garage.view_car_in_homespace and identify world-loading dependencies','Switch to the Passat and compare paint/glass/lights/wheel morphs with normal in-game rendering','Rebuild one uniquely marked texture/model; unload and reload; prove cache invalidation before promising live refresh'],minimum_asset_subset='Undetermined until successful boot and asset-read tracing; keep full existing installation available and share it read-only rather than duplicate it.')
 result=dict(game=binary,game_supported_by_audited_source=binary['sha256'] in manifest['supported_inputs'],host_binaries=binaries,installed_version_evidence=versions,source_version=manifest['version'],source_provenance=json.loads((BASE/'installed-source-provenance.json').read_text()),shader_counts=counts,asset_inventory=inventory,homespace_track_308=track,flows=flow,toolchain={k:shutil.which(k) for k in ['zig','clang','x86_64-w64-mingw32-gcc']},requirements=requirements)
 requirements['hook_limitations']=['The inspected plugin SDK exposes initialization, vehicle-update and database callbacks; it does not expose a standalone render/create-scene API. A UI/render-thread hook must be researched separately.','UIPageCarView force_reload=true is evidence of a car-view reload path, not proof that model, texture, archive or database caches are invalidated.','Plugin private media roots are documented as immutable while in use. Do not implement refresh by overwriting actively mounted files.','The release tag Azimuth_v1.0.0 points to EO 0.3.0; use the pinned 0.3.9 source revision in installed-source-provenance.json, then validate installed signatures before any patching.']
 (BASE/'inventory.json').write_text(json.dumps(result,indent=2)+'\n');(BASE/'requirements.json').write_text(json.dumps(requirements,indent=2)+'\n')
 print('Audit saved. Game hash supported:',result['game_supported_by_audited_source']);print('Shader entries:',counts);print('Homespace assets:',inventory['tracks/homespace02']);print('Track 308:',track);print('Host exports:',{k:len(v['exports']) for k,v in binaries.items()})
if __name__=='__main__':main()
