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
- `f1/matI_lod1.bin` (MatI template; `f1/extract_mati.py PEU_207_5door_v14.zip` regenerates it)
- Third-party tools: Extra Options repo (`eo/`, github.com/RokkuDayo/ForzaHorizon2_ExtraOptions, needs `eo/tools/mod_diff.py`), FH2 Manager (`fh2m/`), ftx.
- `f1/in/`: the donor zip, PEU_207_5door_v14.zip, TJ2005_engine.ini and build outputs (gitignored).

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

## Toro Rosso STR1 — v0.4.0 built on the Charger, awaiting Owen's in-game check
Scripts (run from `f1/`, inputs in `f1/in/` which is gitignored):
`make_media.py in/DOD_ChargerSRT8_12.zip in/donor_STR_ToroRosso_1_06.zip` (rename donor media),
`str1_geo.py` (glb → str1_geo.pkl), `build_str1.py in/donor_STR_ToroRosso_1_06.zip in/str1.zip`,
`build_str1_db.py` (→ custom_str1.slt + strings_str1.json; reads `in/TJ2005_engine.ini`), then
`python3 ../eo/tools/mod_diff.py database ../car207/vanilla.slt custom_str1.slt -o database_str1.json --updates override --force`
and set `policy.id_conflicts` to `nearest` in the JSON. `extract_mati.py in/PEU_207_5door_v14.zip` regenerates matI_lod1.bin.
Package = `f1/pkg/Toro Rosso STR1/` (mod.json, CREDITS.txt) + database.json + strings.json + `media/cars/STR_ToroRosso_1_06.zip`;
mod id owen-toro-rosso-str1, v0.4.0. Car 3651, make "Toro Rosso" (id 202), price 1 CR, Carrera GT sound, V10 to 11,900 rpm.
Python deps: numpy trimesh scipy pillow texture2ddecoder etcpak. Extra Options repo = github.com/RokkuDayo/ForzaHorizon2_ExtraOptions (clone to `eo/`).

### Donor: Dodge Charger SRT8 2012 (car 1422, engine 882, drivetrain 830, media DOD_ChargerSRT8_12)
Chosen for its 3.052 m wheelbase: wheel positions come from the donor's .gr2 animations (DB Wheelbase, carbin
transforms and skeleton bones had no effect on the Atom), so the donor has to match the STR1's 3.05 m.
- Media renamed DOD_ChargerSRT8_12 -> STR_ToroRosso_1_06 (18 chars each). make_media.fix_model now just rewrites the
  crc32 after every renamed texture path (the Charger's headlight MatIs use a param type fhmat.retexture doesn't know;
  ErrorShader MatIs are empty).
- Charger body_a materials: group 0 carpaint + frame (LODs 3..32), 1 blkplastic_hgl, 2 undercarriage, LOD64 groups 3/4/5.
  Build uses textured_like {0,3: carpaint}, black -> (1, blkplastic_hgl), mirror -> (0, frame); steering wheel group 0
  blkplastic_mgl. Wheels/brakes keep the Charger's transforms; only the steering spindle bone moves.
- Charger wheel centres (FH2 space): F ±0.93, y 0.149, z 1.592; R ±0.94, y 0.153, z -1.418. Body centred on z +0.087,
  GROUND_FH2 = 0.151 - 0.33. STR1's own hubs land at F ±0.74 z 1.616, R ±0.71 z -1.434 — so the Charger wheels sit
  ~19 cm outboard of the STR1 suspension arms (track 1.86 m vs 1.49 m). ModelFront/RearTrackOuter is set to the STR1
  track in the DB; see whether that pulls the wheels in (it probably doesn't, like Wheelbase didn't).
- donor_peak = 637 Nm (the Charger's TorqueScale is 637.79, i.e. its peak torque; STR1 scale -> 445.8).
- Preview: `preview_str1.py in/str1.zip in/str1_preview.glb`, then in scan/viewer: `npm install three@0.160.0` somewhere
  and copy `build/` + `examples/jsm/` to `scan/viewer/vendor/three/` (CDNs are blocked in the cloud session),
  `python3 -m http.server 8765` and `node shot.js str1.glb out.png '[[0,9,0.01],[7,1.5,0]]' '[0,0.4,0.09]'`.
  Preview of v0.4.0 looked right (body on the Charger axles, livery OK, wheels at the axles but wide).

### Next
1. Owen installs v0.4.0 and sends an overhead screenshot: wheelbase should now be right; check the track.
2. If the wheels are too wide: try smaller ModelFront/RearTrackOuter, else widen the STR1 suspension arms in
   str1_geo.py (stretch the HUB_* / arm parts in x to the Charger track) or accept it.
3. Then the Charger's wheel models: replace with STR1-style F1 wheels/tyres (13" rims, 0.33 m radius; the Charger's
   wheels are 20" and show through the sidepods) — new render meshes in str_tororosso_1_06_wheellf.modelbin.

### Later
STR1's own F1 wheels/tyres; downforce tuning; rain light; move traffic mods' Combo_Colors IDs away
from other mods (ZS Formula pack clashed with owen-traffic-trucks — fixed with id_conflicts nearest).

## TASK: game-accurate preview ("as-game" check, so Owen needn't screenshot every build)
Goal: a script `preview/asgame.py car.zip database.json` that places everything the way FH2 does
and prints PASS/FAIL checks plus top/side/3-4 PNGs (three.js viewer in scan/viewer, `shot.js`).
1. **Wheels from the .gr2.** FH2 wheel positions come from `scene/<media>_skeleton.gr2`
   / Animations/*.gr2 (Granny v7, compressed), NOT the carbin transforms or DB wheelbase.
   Write a read-only Granny reader (port the relevant parts of an open-source reader,
   e.g. LSLib's Granny/BitKnit/Oodle0-1 code) to get wheel/suspension bone rest positions.
   Validate: Atom donor must come out ≈2.3 m wheelbase (what the game showed), Charger ≈3.05 m.
2. Track width = DB ModelFrontTrackOuter/ModelRearTrackOuter (≈ centre-to-centre × 1.012) — confirmed on the 207.
3. Checks: each wheel centre vs the body's intended axle point (str1_geo wheels) — fail if > 3 cm;
   tyre bottom vs ground; wheel inside the arch/wishbone ends.
4. Then add, one rule at a time: lights from Lights.bin (lit material names `*_custom_brake/_head/_reverse/_turn`),
   gauge needle bones, material types (carpaint vs textured).
Every rule added should be checked against a real in-game screenshot before trusting it.
Status 29 Oct: the repo has NO Granny reader yet. The wheel centres used so far are the carbin's spindle transforms
(`fh2re/carbin.py`, part type 43): Atom 2.344 m / Charger 3.011 m wheelbase, and both matched the game (the Atom
showed ~2.3 m; the Charger build's overhead screenshot has the wheels on the STR1 axle lines). The Charger's gr2
files are all Oodle1-compressed (section compression type 2), as are the Atom's skeleton and driver animations;
only the Atom's `Animations/suspension*.gr2` are uncompressed. The Charger has no suspension*.gr2 at all, which is
probably why its carbin transforms place the wheels. Track: the overhead screenshot measured ~1.64 m outer-to-outer
at the front = the DB's ModelFrontTrackOuter 1.504 pulled the Charger wheels in (rule 2 confirmed on the STR1 too).

## Setup gotchas (files the scripts expect)
- Viewer: `cd scan/viewer && npm install` (three@0.160). Serve with `python3 -m http.server 8765` there; `node shot.js ...`.
- build_str1.py reads two texture templates from `../tex/`: `PEU_207SEHDi_08_Interior_DIFF_7b3d1f55-...swatchbin`
  (zip path Textures/LOD/Swatches/) and `PEU_207SEHDi_08_Rad_Fixed_DiffuseFrontReflector_fa6144d2-...swatchbin`
  (Textures/lp/Swatches/). Extract both from PEU_207_5door_v14.zip into tex/.
- build_str1_db.py hard-codes an old TJ2005_engine.ini path — point it at the uploaded file.
- Python deps: numpy, trimesh, scipy, scikit-learn, pillow, etcpak, texture2ddecoder (pip --break-system-packages).
- matI_lod1.bin: `cd f1 && python3 extract_mati.py in/PEU_207_5door_v14.zip`.
- Cloud session: CDNs (cdnjs, jsdelivr) are blocked, registry.npmjs.org and PyPI are not — hence the local three in node_modules.
- Driver pose: avpins is the points-of-interest XML, `Template="LMP_OpenCockpit"` on the Atom vs `"4Door_Sedan"` on the
  Charger; both cars also carry their own `scene/Drivers/default/*.gr2` (compressed). Data_Car.IsOpenCockpit=1 on every
  open car in the vanilla DB (set from v0.4.1). If the driver still sits upright, next tries: the Atom's avpins
  Template, then the Atom's scene/Drivers/ gr2s (in/atom/ARI_Atom_13.zip, uploaded 29 Oct) in the STR1 media.
