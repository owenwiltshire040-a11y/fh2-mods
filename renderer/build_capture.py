"""Build the local macOS renderer-window capture helper with the Apple SDK."""
from pathlib import Path
import plistlib,subprocess
R=Path(__file__).resolve().parent;app=R/'build/Car Studio Capture.app';mac=app/'Contents/MacOS';mac.mkdir(parents=True,exist_ok=True)
subprocess.run(['swiftc','-parse-as-library','-O','-module-cache-path',str(R/'build/swift-cache'),str(R/'src/CapturePreview.swift'),'-o',str(mac/'CapturePreview'),'-framework','AppKit','-framework','ScreenCaptureKit','-framework','CoreGraphics','-framework','ImageIO'],check=True)
info={'CFBundleExecutable':'CapturePreview','CFBundleIdentifier':'local.owen.fh2renderer.capture','CFBundleName':'Car Studio Capture','CFBundleDisplayName':'Car Studio Capture','CFBundlePackageType':'APPL','CFBundleVersion':'1','CFBundleShortVersionString':'0.1','LSMinimumSystemVersion':'14.0','LSUIElement':True,'NSHighResolutionCapable':True}
(app/'Contents/Info.plist').write_bytes(plistlib.dumps(info));subprocess.run(['codesign','--force','--sign','-','--identifier','local.owen.fh2renderer.capture',str(app)],check=True)
print(app)
