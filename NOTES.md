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

### Next steps (Charger rebuild)
1. make_media.py: OLD='DOD_ChargerSRT8_12', new 18-char media name e.g. 'STR_ToroRosso_1_06';
   update MEDIA in build_str1.py and build_str1_db.py.
2. build_str1_db.py: clone from 1422/882/830 instead of 1651/1112/1059; keep all STR1 physics.
3. str1_geo.py: Charger wheel centres F ±0.93, y≈0.149, z≈1.592; R ±0.94, y≈0.153, z≈-1.418.
   GROUND_FH2 = ~0.15 - 0.33; centre the body on the Charger axle midpoint (z≈+0.087).
4. build_str1.py: Charger materials — body_a group 0 = carpaint + frame (LODs 3/4/8/16/32),
   group 1 = blkplastic_hgl, group 2 = undercarriage, LOD64 groups 3/4/5.
   textured_like {0:'carpaint',3:'carpaint'}; plain black → (1,'blkplastic_hgl'); mirror → (0,'frame').
   steeringWheel_a (scene/Interior/Dash/) group 0 has blkplastic_mgl → steering textured_like {0:'blkplastic_mgl'}.
   Replace atom_wheel refs, delete AXLE_SHIFT/patch_skel suspension shifts, keep locator logic.
5. Rebuild, preview (f1/preview_str1.py; viewer = `python3 -m http.server 8765` in scan/viewer + `shot.js`),
   package, give Owen the unzip command, ask for an overhead screenshot.

### Later
STR1's own F1 wheels/tyres; downforce tuning; rain light; move traffic mods' Combo_Colors IDs away
from other mods (ZS Formula pack clashed with owen-traffic-trucks — fixed with id_conflicts nearest).
