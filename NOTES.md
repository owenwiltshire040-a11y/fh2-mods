# FH2 custom car mods — handover notes

Owen's Forza Horizon 2 custom cars, played on a Mac via Azimuth/CrossOver with the
Extra Options mod loader:
`~/Library/Application Support/CrossOver/Bottles/Azimuth/drive_c/azimuth-windows/mods`
(each mod = folder with mod.json, database.json, strings.json, media/; `loadorder.txt` sets priority;
`FH2_ExtraOptions.log` shows what loaded). FH2 Manager does NOT run on Mac — install by unzipping
a packaged mod folder into `mods/` with a terminal command.

Delivered builds live on the Mac in `~/Downloads/FH2Manager-1/fh2re` (old versions in `_parts/`).
Never delete Owen's files — move them to `_parts/`.

## Not in this repo (upload to the session when needed)
- Donor car zips (game files): `~/Downloads/FH2Manager-1/DOD_ChargerSRT8_12.zip`, `ARI_Atom_13.zip`
- `vanilla.slt` (stock game database) — needed by both `build_*_db.py` scripts
- `f1/src/nefolder.glb` — the 2006 Toro Rosso STR1 model (CTDP F1 2006, via Sketchfab). Owen states
  he has CTDP's permission for personal use. Credit CTDP; never redistribute.
- `f1/matI_lod1.bin` (MatI template, extracted from the built 207 `interior_lod1`)
- Third-party tools: Extra Options repo (`eo/`, needs `eo/tools/mod_diff.py`), FH2 Manager (`fh2m/`), ftx.

## Ground rules
Don't decrypt protected mod files (CTDP GMTs are encrypted), don't edit/decrypt saves,
don't port ripped assets from other games (no ZS/FM5 donors), personal use only.

## Formats (see fh2re/, tex/, f1/fhmat.py)
- swatchbin: data @0x53, BC7 = fmt 0x2e, GCN tiled (mips 0–2 2D, 3+ 1D). `tex/swatch.py write_like(template, rgba)`.
- MatI = Grub bundle (MATI base path + MTPR params; texture param = LEB128 path + crc32(lower path)).
- Modl blob: u16 counts @0 meshes, @2 buffers, @4 layouts, @6 materials. TRef lists crc32 of texture paths.
  New render meshes must go after ALL existing meshes (shadow ranges).
- Lights.bin: 76-byte entries. Engine sound = Data_Engine.MediaName → FMOD PG events (traffic cars have none).
- Torque table max 121 entries @100 rpm → 12,000 rpm cap; STR1 rescales rpm by K=11900/16700.

## Peugeot 207 (car 3207, media PEU_207SEHDi_08) — done ("it'll do")
car207/, sheik/, wheel/, tex/gauges_207.py. Latest: PEU_207_5door_v14.zip + peugeot207_database_v7.json.

## Toro Rosso STR1 — IN PROGRESS
Scripts: `f1/str1_geo.py` (glb → str1_geo.pkl), `f1/make_media.py` (rename donor media),
`f1/build_str1.py donor.zip out.zip`, `f1/build_str1_db.py` (→ custom_str1.slt, then
`eo/tools/mod_diff.py database vanilla.slt custom_str1.slt -o database_str1.json --updates override --force`,
then set `id_conflicts` to `nearest`). Package = `f1/pkg/Toro Rosso STR1/` (mod id owen-toro-rosso-str1, v0.3.3).
Car 3651, make "Toro Rosso", price 1 CR, Carrera GT sound, V10 to 11,900 rpm, 8 gears, works in game and passes 140 mph.

### Current problem: wheelbase
On the Ariel Atom donor the wheels sit ~2.3 m apart; STR1 axles are 3.05 m apart.
DB Wheelbase/ModelWheelbase, carbin transforms and skeleton bones all had NO effect —
wheel positions come from the donor's .gr2 animations (can't edit). Fix = new donor with the
right wheelbase: **Dodge Charger SRT8 2012** (car 1422, engine 882, drivetrain 830, make 11,
wheelbase 3.052).

### Charger rebuild — scripts done (steps 1–4), build not yet run
1. make_media.py: DOD_ChargerSRT8_12 -> STR_ToroRosso_1_06 (18 chars both); MEDIA updated in build_str1.py,
   build_str1_db.py, preview_str1.py. Package bumped to v0.4.0, mod.json/CREDITS say Charger.
2. build_str1_db.py clones 1422/882/830; STR1 physics unchanged. donor_peak = 637 Nm (SRT8 470 lb-ft) —
   check the printed donor TorqueScale looks sane. Prints a warning if the Charger has no stock aero row
   (front bumper / rear wing) to clone. Still reads TJ2005_engine.ini from /mnt/user-data/uploads/... (CTDP files).
3. str1_geo.py: DONOR_WHEELS (Charger centres), GROUND_FH2 = 0.151 - 0.33, body centred on z = +0.087;
   pkl now carries donor_wheels (build_str1.py refuses an old Atom pkl).
4. build_str1.py: Charger materials as planned (body {0,3: carpaint}, black -> (1, blkplastic_hgl), mirror ->
   (0, frame); steering {0: blkplastic_mgl}, black -> blkplastic_mgl). AXLE_SHIFT / suspension bone shifts and
   the no-op wheel transform loop are gone; it now just lists the kept wheel/brake transforms. Locators unchanged.

Known gap: the Charger's track is ~1.86 m, the STR1's ~1.49 m, so the wheels will likely sit ~19 cm outboard
of the STR1's suspension arms (ModelFront/RearTrackOuter is still set to the STR1 track — see if it does anything).

### Next steps
1. Upload DOD_ChargerSRT8_12.zip, vanilla.slt, nefolder.glb, matI_lod1.bin, eo/ tools and the CTDP ini.
2. `python3 make_media.py DOD_ChargerSRT8_12.zip donor_STR_ToroRosso_1_06.zip`, `python3 str1_geo.py`,
   `python3 build_str1.py donor_STR_ToroRosso_1_06.zip str1.zip`, `python3 build_str1_db.py`, mod_diff, id_conflicts.
   If fill() errors on a material name, print material_names() for body_a / steeringwheel_a and fix the map.
3. Preview (f1/preview_str1.py; viewer = `python3 -m http.server 8765` in scan/viewer + `shot.js`),
   package, give Owen the unzip command, ask for an overhead screenshot.

### Later
STR1's own F1 wheels/tyres; downforce tuning; rain light; move traffic mods' Combo_Colors IDs away
from other mods (ZS Formula pack clashed with owen-traffic-trucks — fixed with id_conflicts nearest).
