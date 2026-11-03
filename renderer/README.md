# FH2 Renderer experiment

A separate local program folder hosting the actual FH2 engine through Azimuth/CrossOver. This is an experimental engine integration, not a completed lightweight renderer.

## Launch

Double-click **Open Car Browser.command** to open the local car collection. It reuses an existing browser service when available. The browser lists installed mod cars and matching packages from `Passat B3 Build/output`, with thumbnails and search.

Choose **View car** to queue a car and start the private viewer. Automatic startup handles Continue and opens the preview using the faster preview bootstrap. **Start viewer** can also open the native selector before you choose a car. The new experimental route opens the native Autoshow selector, with its purchase screen replaced by the native 3D car viewer. Browser selections focus and confirm the matching stock model; ownership is not required by that selector. The user confirmed that the Passat opened, then the yellow Jordan appeared automatically in the same engine session. Selection of every catalogue entry has not been individually checked. Changing a choice while viewing a car returns to the selector automatically.

**Stop Renderer.command** or **Close viewer** closes only this private instance. **Check Renderer.command** reports diagnostics and checks the original settings, load order and saves against their starting hashes. **Launch Renderer.command** remains the direct engine launcher.

Automatic startup is user-tested on the Passat: Continue, loading and entering its car view completed with no user input, with steel wheels visible. The matching restore point is `build/known-working-startup`; evidence is in `logs/startup-validation.json`.

The private startup hook works as follows: the private UI hook invokes the title screen’s own Continue action, then waits for the driving HUD and free-roam input to remain ready before asking the existing WaitForPause state to take its onPause transition. The native pause-block counter and state-exit checks remain in place. It uses the game’s UI update callback and does not send desktop keyboard events. `Launch Manually.command` (or `python3 renderer.py showroom --manual-startup`) keeps the manual Continue/Pause route available.

The default browser and direct launcher now use a reduced bootstrap with native city streaming explicitly disabled. Traffic, festival cars, road restoration, streaming waits and map/tutorial startup are omitted. The user confirmed normal Passat rendering, showroom background and orbit camera. In one normal run versus two lean runs, the measured phase from free-roam XML parsing to car-view initialization fell from 42.1 seconds to 29.3 seconds. This is not total process launch time or an averaged benchmark. Shared main-track archive discovery and core engine/player initialization remain; full removal of world-related initialization is not achieved.

`Launch Full Startup.command` restores the prior automatic full startup; `Launch Manually.command` also leaves Continue/Pause to the user. `--lean-boot` opts into the reduced bootstrap for the developer CLI. The confirmed fast-preview build is saved at `build/known-working-fast-preview`; measurements and visual confirmation are recorded in `logs/lean-streaming-disabled.json`. The earlier garage-based viewer and live visual refresh were user-tested on the Passat B3: an earlier donor-wheel build and the current steel-wheel build loaded in the same engine session. Those working builds remain in the checkpoints below. The stock-preview switching checkpoint is `build/known-working-catalog`, with evidence in `logs/catalog-validation.json`. Live visual refresh in this stock-preview route was checked by loading the Passat’s earlier donor wheels; the user confirmed the visible change. The current steel-wheel build was then restored.

New built packages are copied independently into the private renderer at the next launch, with dependency checks and verified APFS clones. Previous private packages are kept in `backups/package-sync`. Visual-only rebuilds of a currently installed car can use **Refresh build** without restarting. Database changes require a restart. The browser service listens only on this computer and requires a per-session token for actions.

## Refresh a rebuilt car

The **Refresh Car.command** button is currently configured for the Passat B3 package under `Passat B3 Build/output/Volkswagen Passat B3`.

1. Rebuild the car package as usual.
2. Keep that car open in **View Car** in this private renderer.
3. Double-click **Refresh Car.command**, then return to the car view.
4. The viewer briefly unloads and reloads the UI car. It does not restart Azimuth.

Each revision has fresh asset paths and fresh custom-texture GUIDs. Previously mounted revisions are retained instead of overwritten. Requests are serialized, native database work runs on the verified owning callback thread, and the UI triggers the native reload transition. Earlier requests are archived at the next launch so they cannot silently replay in a new session.

This first version updates **visual assets only**. Physics, tyre sizes, upgrade tables and database camera values remain those of the package installed in the private renderer. Changing those requires updating that private package and restarting. The prototype currently allows 16 applied visual revisions per engine session; a rejected request leaves the current car intact. New car packages must already be installed in the private renderer before they can be refreshed.

`refresh-target.json` identifies the one-click button's package. The developer command `python3 refresh.py --package /absolute/path/to/package` can stage another already-installed single-car mod. `python3 refresh.py --status` reports the matching native acknowledgment; initialization alone is not proof of a visible change.


## Capture an inspection

Use **Capture inspection** in the car browser after a car opens. The viewer enters its own orbit camera and saves front, rear, left, right and two quarter views, then restores the original camera mode and pose. The latest set appears above the collection; click an image for its full-size PNG. Sets are stored under `captures/<id>/`, with car selection, live visual revision, camera pose, runtime identity and image checksums in `manifest.json`.

`Capture Preview.command` saves the current car view. `python3 capture.py --inspection` performs the six-view inspection; `python3 capture.py --list` lists recent sets. These local commands let an assistant select, refresh, capture and inspect cars without asking for user screenshots. The macOS helper targets the exact private renderer process and window. It requires Screen Recording permission; `Enable Capture.command` requests it. In this session the user granted ChatGPT the permission and actual renderer-window captures were verified.

The native camera work runs in the car-view callback. Selection and refresh staging are locked during capture, and a changed process, browser-selected car or visual revision aborts the set. Only complete inspections are published. Camera locks expire after 25 seconds if the client disappears. The native camera reset also clears locks when a new car view loads. Camera requests are archived on engine restart.

The exterior views were visually checked on the Passat and Jordan EJ11. They retain the current game's image quality, materials and UI overlay. Wheel closeups, automated lamp-state changes and cockpit views are not yet dedicated presets; driving behaviour requires separate validation. The selected-car metadata follows the browser selection, so use the browser to choose the car being inspected.

Run `python3 build_capture.py` to rebuild and locally sign `build/Car Studio Capture.app` with the installed Apple SDK. This macOS helper uses Apple's ScreenCaptureKit window filter and screenshot API; it does not need access to other windows in the capture workflow.

## Isolation

`runtime/` has independent settings, saves and mod files. `game/Anthem/` is an independent APFS clone of the existing game tree; unchanged files share disk blocks until either copy changes. There are no directory links in the active game clone. Azimuth rejected linked runtime-storage folders in earlier tests.

The current integration keeps `stateflow.zip` and `zipmanifest.xml` byte-identical to the originals. Its private `winmm.dll` uses the existing Extra Options XML parse hook to route the native pause entry to its existing stock car-list node. Normal boot and the native pause/UI ownership wrappers are retained. That avoids changing archive offsets or feeding an edited archive through platform content processing. The main installation's DLLs and game files are not replaced.

The launcher refuses to change mode while any Azimuth session is active. Keep the `runtime/` directory between sessions to retain the experimental save copy; preparation refuses to overwrite it.

## Diagnostics and builds

Run from this folder:

- `python3 renderer.py diagnostics`: normal startup, unmodified Extra Options, diagnostic plugin only.
- `python3 renderer.py showroom`: original archives plus the private in-memory showroom hook.
- `python3 renderer.py status`: diagnostic results and startup hook markers. These do not establish what is visible on screen.
- `python3 renderer.py stop`: stop only this private executable.
- `python3 renderer.py verify`: compare original settings/load order/save hashes with the initial baseline.
- `python3 build.py`: rebuild the probe and private Extra Options DLL using the checksum-verified Zig compiler under `tools/`.
- `python3 -m unittest discover -s tests`: check archive preservation, injected XML/anchor validity and exact process ownership for Stop.

The normal-boot control reached native local-car callbacks and enabled driving input. The first in-memory shortcut reached the native car-view UI, but showed an empty/clipped scene. Interrupting startup to open menus was also premature. The current version leaves startup unchanged and uses the native pause context and selector. The user confirmed the preview and both visible live wheel swaps. The original viewer checkpoint is under build/known-working/; the tested refresh checkpoint is under build/known-working-refresh/. See `logs/experiment-results.json` and `logs/normal-boot-control-passed.json` for evidence.

## Source

The supplied Extra Options source is pinned to official revision `44acf35c0fc4` (EO 0.3.9). The added transform is in `src/extra-options/features/garage.c`; the observation plugin is `src/probe.c`. GPL-3.0 licensing is retained alongside the source. The proprietary runtime and game assets are local dependencies and must not be redistributed.
