import Foundation
import AppKit
import ScreenCaptureKit
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers

@main struct CapturePreview {
 static func emit(_ object: [String: Any]) {
  if let data = try? JSONSerialization.data(withJSONObject: object, options: [.sortedKeys]), let text = String(data: data, encoding: .utf8) { print(text) }
 }
 @MainActor static func main() async {
  _ = NSApplication.shared
  let args = CommandLine.arguments
  if args.contains("--check") { emit(["screen_capture_allowed": CGPreflightScreenCaptureAccess()]); return }
  if args.contains("--request-access") { emit(["screen_capture_allowed": CGRequestScreenCaptureAccess()]); return }
  guard let at = args.firstIndex(of: "--pid"), at + 1 < args.count, let pid = Int32(args[at+1]), pid > 0 else { emit(["error":"A private renderer process is required"]); exit(2) }
  guard let outAt = args.firstIndex(of: "--output"), outAt + 1 < args.count else { emit(["error":"An output path is required"]); exit(2) }
  guard CGPreflightScreenCaptureAccess() else { emit(["error":"Screen Recording permission is required for CapturePreview", "permission_required":true]); exit(3) }
  do {
   let content = try await SCShareableContent.excludingDesktopWindows(true, onScreenWindowsOnly: false)
   let candidates = content.windows.filter { $0.owningApplication?.processID == pid && $0.windowLayer == 0 && $0.frame.width >= 320 && $0.frame.height >= 180 }
   guard let window = candidates.max(by: { $0.frame.width * $0.frame.height < $1.frame.width * $1.frame.height }) else { emit(["error":"No renderer window belongs to the verified process", "pid":pid]); exit(4) }
   let filter = SCContentFilter(desktopIndependentWindow: window)
   let config = SCStreamConfiguration()
   config.width = Int(filter.contentRect.width * CGFloat(filter.pointPixelScale))
   config.height = Int(filter.contentRect.height * CGFloat(filter.pointPixelScale))
   config.showsCursor = false
   config.ignoreShadowsSingleWindow = true
   let image = try await SCScreenshotManager.captureImage(contentFilter: filter, configuration: config)
   let url = URL(fileURLWithPath: args[outAt+1])
   guard !FileManager.default.fileExists(atPath: url.path) else { emit(["error":"Capture already exists"]); exit(5) }
   guard let destination = CGImageDestinationCreateWithURL(url as CFURL, UTType.png.identifier as CFString, 1, nil) else { emit(["error":"Cannot create capture"]); exit(5) }
   CGImageDestinationAddImage(destination, image, nil)
   guard CGImageDestinationFinalize(destination) else { emit(["error":"Cannot save capture"]); exit(5) }
   emit(["path":url.path,"width":image.width,"height":image.height,"window_id":window.windowID,"pid":pid,"window_title":window.title ?? ""])
  } catch { emit(["error":error.localizedDescription]); exit(6) }
 }
}
