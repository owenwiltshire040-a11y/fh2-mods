from pathlib import Path
import subprocess,os
R=Path(__file__).resolve().parent;zig=next((R/'tools').glob('zig-*/zig'));out=R/'build';out.mkdir(exist_ok=True)
env=dict(os.environ,ZIG_GLOBAL_CACHE_DIR=str(R/'tools/zig-cache'),ZIG_LOCAL_CACHE_DIR=str(R/'build/zig-cache'))
subprocess.run([str(zig),'cc','-target','x86_64-windows-gnu','-shared','-O2','-Wall','-Wextra','-Werror','-fno-stack-protector',str(R/'src/probe.c'),'-o',str(out/'RendererProbe.dll'),'-lkernel32'],check=True,env=env)
print('Built',out/'RendererProbe.dll')

# Build the private engine integration from the pinned, supplied EO source.
subprocess.run(["python3",str(R/"src/extra-options/build.py"),str(zig),"--azimuth","--output",str(out/"winmm-renderer.dll"),"--build-dir",str(out/"extra-options")],check=True,env=env)
