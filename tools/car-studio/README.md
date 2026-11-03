# FH2 Car Studio

A local browser interface for the repository's custom-car pipeline. It uploads a single GLB, previews it, lists its dimensions and materials, lets you edit a car spec and package details, runs `glbgeo.py` and `package_car.py`, then copies the finished mod to an Extra Options mods folder.

## Start

From the repository root:

```sh
python3 tools/car-studio/studio.py
```

The app opens at `http://127.0.0.1:8766`. Stop it with Ctrl+C in the Terminal window. Project uploads and generated intermediates are kept under `cars/_studio/` and are ignored by Git. Port 8765 stays available for the repository's thumbnail renderer.

For the Python model tools, create and activate a virtual environment, then install `tools/car-studio/requirements.txt`. In `scan/viewer`, install the existing Three.js dependency plus Playwright, then install Playwright's Chromium browser (`npx playwright install chromium`). Start the app with the same Python environment activated.

## Before building

Use the **Build requirements** panel in the app. It discovers your local FH2 and CrossOver paths, the Charger donor and 207 zip in `Desktop/untitled folder`, and the stock database in either the desktop folder or the FH2 install. On the first build it copies the stock database into the repo's ignored input path and creates `matI_lod1.bin` from the 207 zip. It does not modify the game install. The remaining inputs are:

- Python with the builder's libraries available: NumPy, trimesh, SciPy, Pillow, and the texture-decoding/compression packages required by this repo.
- `scan/viewer/node_modules/three` and Playwright/Chromium for the Autoshow thumbnail render.
- `eo/tools/mod_diff.py` from the Extra Options source tools described in `NOTES.md`.
- Three.js and Playwright/Chromium installed in `scan/viewer/node_modules`.

The app never downloads game data. It reads files from your own installation and copies only the stock database and generated material template to ignored local build-input paths.

## Guided workflow

The interface uses five separate screens with Back and Continue controls and a clickable step list. Its dark palette, blue selection state and focused panels take inspiration from OTV. The source-model viewer stays alongside the active step; narrow screens stack the panels.

1. **Your model** — name the project, choose a starting car, and upload an embedded-texture GLB. The model is inspected before continuing.
2. **Wheel fit** — enter a target wheelbase and apply measured wheel suggestions when four distinct tyres are found. Manual measurements and wheel options are under a disclosure, opened automatically when measurements need review. The source preview does not apply fit changes; use **View built fit** after building for the fitted result.
3. **Car setup** — work through identity, materials/lights and driving/cockpit settings. The existing Python spec editor remains necessary for model-specific choices. Guidance and engine sound selection are on this screen. Both dictionary and keyword-style sound entries are supported.
4. **Package** — enter the mod’s name, unique ID, version and credits.
5. **Build & install** — review a summary, build, inspect the built fit, then install. Logs are available under **Build details** and open automatically when a failed build supplies diagnostics. Existing mod folders are not overwritten. Fully restart the game after installation.

**Save project** is available from every screen. Reopening a saved project restores the settings, target wheelbase and current screen. Existing saved project files remain supported. The current page is held in memory until saved; reloading does not automatically save edits. Starting-point changes reload that template; **Reload template** replaces the spec while retaining the package metadata.

Build results are invalidated when inputs change or a different project is opened. Controls are locked during a build so its result belongs to the settings submitted. A reopened project must be rebuilt before installation. **Requirements** opens a separate dialog and can be closed with Escape.

The sound list reads `Data_Engine` from the stock database, installed Azimuth mods, and the FM5 Addon Packs ZIPs. FM5 sounds need their pack enabled in the game’s load order.

Validation: exercised real GLB upload and tyre analysis, all five screens, measurement validation, sound editing, saving and reopening, and desktop/mobile layouts in Playwright. Build success/failure and installation responses were simulated for UI checks, without changing installed game files. Existing wheel-fit regression checks also passed.

GLB files only are supported for now. The preview and model inspection are guides; they do not replace an in-game check for wheel fit, collision, camera placement, lighting, and handling.

## Measured wheel fitting

Uploads now report candidate tyre meshes, measured centres, width and outer radius. **Use measured wheels** fills the frame, lateral centre, axle positions and ground offset. Set the optional target wheelbase first to calculate a uniform scale. Suggestions require four distinct tyre meshes; a single rim or a model with merged/unrecognised tyres stays in review mode. Check front/rear direction before accepting.

Choose the wheel profile deliberately:

- `charger_rim_face`: the Model Y's confirmed convention. A normalised rim's outer face is local X=0. The reference sits at the measured arch lip + `RIM_FACE_GAP` (default 10 mm). Runtime height comes from the donor spindles. The tyre centre is half a tyre width inward from that face.
- `charger_legacy`: preserves the Passat's established arch fit and geometry height. This does not reinterpret existing successful cars.

New specs declare `WHEEL_FIT=dict(profile='charger_rim_face')`, `TRACK_REFERENCE='rim_face'` and an explicit `RIM_R_REF` for custom rims. `RIM_R_REF` is the source **nominal** rim radius, not its outer lip radius. An intentional tyre-size change over 30 mm of radius needs `WHEEL_FIT['allow_tyre_resize']=True` after review. Unprofiled older specs emit a review warning; they are not silently migrated.

Packaging writes `build/wheel-fit.json` before building and stops on known errors (wrong donor signature, uncentred body, wheelbase disagreement, rim reference/lip mismatch, large source tyre mismatch or donor height mismatch). The report is copied into the package. **View built fit** opens `build/fit-preview.glb`: actual specification tyre widths/aspects/diameters, selected reference points, donor spindle heights and the builder's rim diameter morph. The ordinary uploaded GLB view remains a source-model view.

Donor barrel-width deformation is an approximation, and this does not reproduce the full game suspension/steering solver. The preview and report reduce fit iterations; they do not replace the final in-game check. Historical `--tyres` preview calls still warn that aspect was assumed; package builds use `--fit-spec` instead.

Checks: `python -m unittest discover -s tests -v` in the active build workspace includes the two confirmed cars, source tyre detection, rejection of the old Tesla rim/height errors, rim diameter morph and the upload analysis endpoint.

For a standalone check, run `python fh2re/wheelfit.py cars/<car>/spec.py --out fit.json`. The older `preview/asgame.py` now accepts `--spec cars/<car>/spec.py` to use the same report and corrected preview. Its old mode prints a warning because it assumes tyre centres and schematic rims.

The fit check also runs after database generation. It rejects upgrade hooks that change the stock tyre widths/rim sizes or move the database track/axle midpoint away from the fitted spec.
