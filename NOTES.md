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
STR1 rim styling (the tyres are already F1-sized from the DB; only the Charger's normalised rim shows); downforce tuning; rain light; move traffic mods' Combo_Colors IDs away
from other mods (ZS Formula pack clashed with owen-traffic-trucks — fixed with id_conflicts nearest).

## GENERIC DONOR (goal: no more donor-picking; rescale one template car's wheel positions to fit any model)
Step 1 proof of concept (29 Oct, built, awaiting Owen's Autoshow check): `fh2re/granny.py` reads FH2's .gr2 files
(Granny v7, 64-bit LE; Oodle1 decoder ported from LunaticInAHat/liboodle, public domain; layout from LSLib — LSLib
itself has no Oodle code, it calls granny2.dll) and writes them back with every section raw (compression 0, CRC =
zlib crc32 of everything after byte 104). Verified: a raw file (Atom suspensionLF.gr2) round-trips byte-identical;
the Charger skeleton decompresses and parses (56 bones) in 0.1 s; `granny.py movebone` shifts a bone's local position
and fixes the InverseWorldTransform of it and its descendants.
Test build v0.4.3-gr2test = v0.4.1 media with `scene/STR_ToroRosso_1_06_skeleton.gr2` rewritten: hubLF (parent root,
child spindleLF) moved 10 cm outward (x -0.832 -> -0.932). Carbin untouched (asgame PASS). The game accepts raw gr2
files (the Atom's suspension*.gr2 are raw) — if this one loads and the left-front wheel sits 10 cm further out than
the right-front, the gr2 skeleton drives the wheels on a car without suspension animations.
What the gr2s say (granny.py info): Atom skeleton hubLF world (-0.908, 0.182, 1.171) = in-game (-0.892, 0.182, 1.186),
with the wheels on a control-arm chain animated by Animations/suspension*.gr2 (tracks boneControlArmLF... per corner).
Charger skeleton hubLF/spindleLF world (-0.832, 0.212, 1.272), hubLR (-0.84, 0.236, -1.523) = 2.80 m, but the game
draws the Charger's wheel at the carbin spindle (-0.93, 0.151, 1.591), 3.01 m. So on the Charger the gr2 rest pose is
NOT where the wheel is; either the game ignores it (then the carbin transform rules on cars without suspension
animations, and the generic donor is just carbin edits) or it adds something. The test decides.
RESULT 29 Oct (Owen's Autoshow overhead, v0.4.3-gr2test): the car loads with the raw gr2 (so the rewrite is accepted
by the game) and the left-front wheel did NOT move — measured on the screenshot: nose-cone centre row 342.5, front
tyre outer edges at rows 150 / 534 → half-spans 192 / 191.5 px, symmetric to 1 px where 10 cm would be ~27 px.
Outcome (b). Next test built: v0.4.4-carbintest = v0.4.1 media with the carbin's type-43 spindleLF wheel transform
x -0.93 -> -1.03 (asgame WARNs on it, as designed). Driver in that screenshot: still the upright sedan pose, seated
left of centre (v0.4.1 flags alone do not fix it; v0.4.2's Atom animations still untested).
RESULT v0.4.4-carbintest (Owen's overhead, 29 Oct): no move either (nose centre row 291.5, tyre outer edges 67 / 515,
half-spans 224.5 / 223.5 px; 10 cm = ~29 px). LESSON: both tests moved x, and the DB's ModelFront/RearTrackOuter sets
x (it is what pulled the Charger track in to the STR1's) — so neither test could have shown anything. Wheelbase (z) is
the open question. Two builds, 29 Oct 22:45:
  v0.4.5-ztest = v0.4.1 media with gr2 hubLF z +0.10 (LEFT front) AND carbin spindleRF wheel transform z +0.10
  (RIGHT front): whichever front wheel sits 10 cm ahead of the other names the source (left -> gr2, right -> carbin,
  both -> both, neither -> neither).
  v0.4.6-wbtest = v0.4.1 media, database only: Data_CarBody Wheelbase & ModelWheelbase 3.05 -> 3.25. If both fronts
  (or all four) move, the DB wheelbase places the wheels on a car without suspension animations (on the Atom it
  did nothing — but the Atom's wheels follow its suspension*.gr2 animations).
RESULTS 29 Oct 22:45 (Owen's overheads, measured in pixels; method below):
  v0.4.5-ztest: left and right front tyre centres identical (fractions of nose-tip->rear-wing 0.2214 / 0.2228, equal
  in every other measure) -> NEITHER the gr2 skeleton (left) NOR the carbin spindle transform (right) moves a wheel
  fore/aft on the Charger. With the x tests: on a car without suspension animations the gr2 and carbin wheel
  transforms are irrelevant to where the game draws the wheel.
  v0.4.6-wbtest (DB Wheelbase & ModelWheelbase 3.05 -> 3.25): front tyres ~10 cm closer to the nose than in the three
  baseline shots (fraction 0.192/0.201 vs 0.209-0.223; front-centre-to-nose-tip 0.84 m vs 0.89-0.95 m at tyre-height
  scale). Rear tyres are sunlit on one side so their edge is unreliable (front-centre to rear leading edge 2.84 m vs
  2.70-2.79 baseline: +5..+13 cm, fits +10 or +20). So: THE DATABASE WHEELBASE MOVES THE WHEELS, at least the fronts.
  Likely rule (fits every number so far, incl. the Charger's own 1.592/-1.418 = 3.018/2 -/+ 0.087): wheel z =
  +/- Wheelbase/2 - BottomCenterWheelbasePosZ, x = +/- ModelTrack/1.012/2. I.e. the Charger-style donor already IS
  the generic donor: media from any car without suspension*.gr2, wheel positions from Data_CarBody. No Granny port
  needed for those (granny.py stays for Atom-style cars / other edits).
  Not yet separated: Wheelbase vs ModelWheelbase (both were changed), and whether the rears move too.
  v0.4.7-wb365 built (22:55): Wheelbase 3.65, ModelWheelbase 3.05, v0.4.1 media. +30 cm per axle is unmistakable:
  the front tyres would sit level with the front wing's trailing edge. Moved -> Wheelbase alone places them (and the
  rear move becomes visible); not moved -> ModelWheelbase (then test that one alone).
RESULT v0.4.7-wb365 (22:55 shot): front tyres NOT moved (fraction 0.234 vs baselines 0.220-0.224; tyre leading edge
to nose 0.54 m vs 0.49-0.52; the 3.25/3.25 build gave 0.19 / 0.42-0.51). So Wheelbase alone does nothing to the
drawn wheels -> ModelWheelbase is the lever (it moved them when both changed). v0.4.8-mwb365 built (23:00):
ModelWheelbase 3.65, Wheelbase 3.05, to confirm (+30 cm per axle: front tyres level with the front wing's trailing
edge). Then the rule becomes: wheel z = +/- ModelWheelbase/2 - BottomCenterWheelbasePosZ (to verify the rear/offset
part from that shot), x = +/- ModelTrack/1.012/2; Wheelbase is physics only.
RESULT v0.4.8-mwb365 (22:58 shot): unmistakable — front tyres at the front-wing endplates, rears out at the
rear-wing endplates: BOTH axles moved ~30 cm, so ModelWheelbase places the wheel models, symmetrically about the
wheelbase centre. CONCLUSION (29 Oct): on a car without Animations/suspension*.gr2, the drawn wheel positions are
  z = +/- ModelWheelbase/2 - BottomCenterWheelbasePosZ, x = +/- ModelTrackOuter/1.012/2 (both Data_CarBody);
  y = still unproven (the donor's spindle y, 0.15, is used; candidates: ModelStockRideHeight, tyre radius).
  Wheelbase is physics only. The gr2 skeleton and the carbin wheel transforms do not matter for those cars.
  => The generic donor is the Charger media + database numbers. Already what the STR1 build does (ModelWheelbase
  3.05, STR1 track, body centred on z +0.087 = -BottomCenterWheelbasePosZ). granny.py is only needed for cars with
  suspension animations (Atom-style) — none planned. preview/asgame.py rule 1 now uses the DB (29 Oct 23:05).
Measuring an overhead: nose cone (orange) leftmost column = tip; rear wing white plate leftmost column = wing;
front tyre = dark run (<55/255) across the rows of each front wheel; the top-of-image wheel is the car's RIGHT when
the nose points left. Framing differs per shot, so compare ratios (tyre centre - tip)/(wing - tip) or distances
scaled by the front tyre's pixel diameter (0.66 m); the baseline spread is about +/-0.01 of body length.
Outcomes (for the old x tests, superseded): (a) wheel moved -> gr2 drives it: step 2 = rescale all four hub bones (and the Atom-style animation tracks
when present) to the model's axle points. (b) wheel did not move, car loads -> try the same 10 cm on the carbin
spindleLF transform (one-line build; `preview/asgame.py` will WARN on it by design). (c) car fails to load -> check
FH2_ExtraOptions.log; the raw rewrite needs fixing before anything else.
Later steps: pick the template car (Charger-style, no suspension animations, simplest chain), bone/transform rescaler
driven by str1_geo-style axle points, fold into build_str1.py, drop the per-model donor hunt.

## RULE: wheel positions come from the database (z, x) and the UNMODIFIED donor zip (y)
Superseded in part on 29 Oct (see GENERIC DONOR): wheel z and x are set by Data_CarBody (ModelWheelbase,
BottomCenterWheelbasePosZ, ModelFront/RearTrackOuter). The donor's carbin spindle transforms (part type 43) are still
read from the ORIGINAL donor zip for wheel y and as a reference; never from our built car, and `preview/asgame.py`
warns when a build changed them (the game does not read them, so such an edit is a mistake).
Original rule text:
Read wheel positions from the donor's carbin spindle transforms (part type 43) in the original donor zip, never from
our built car: the game ignores edited spindle transforms (it follows the .gr2 animations), so a built car's carbin
says nothing about where the wheels will be. `preview/asgame.py` takes `--donor` for this and warns when a build has
changed those transforms. (Decided 29 Oct after the Atom and Charger carbins both matched the game; no Granny reader.)

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
**Done 29 Oct: `preview/asgame.py built.zip database.json --donor DONOR.zip [--geo f1/str1_geo.pkl] [--out DIR]`**
(needs the viewer server for PNGs). Rules in it: 1 wheel y/z from the donor carbin spindles (type 43) with a warning
if the build changed them; 2 x from ModelFront/RearTrackOuter / 1.012; 3 body + steering wheel as built;
4 tyre radius/width from Data_Car rim/width/aspect (the car's wheel modelbin is a normalised rim, x 0..1, that the
game scales to the DB rim size and draws its own tyre on — so the STR1 already runs 13" / 330 mm tyres in game).
Checks: each wheel within 3 cm of the str1_geo axle point, tyre bottom on the body's ground, floor not below it,
uprights (DISK/FW15C_MECANICS/Material_98/MCLHUB in the HUB_* parts) reaching the wheel's inner face.
STR1 on the Charger: all PASS (front wheels 2.2–2.5 cm behind the model's axle, rear 1–2 cm ahead: the 3.011 vs
3.05 m difference). Negative test with the Atom as donor FAILs with the old -0.43 / +0.28 m. Rule 4 still wants a
side-on screenshot; lights / gauge needles / material types not done.
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
  RESULT v0.5.0 (= v0.4.2 content; side-on shot 29 Oct 23:02): no change — still upright, high, behind the cockpit,
  hands reaching to about (y 0.75, z 0.4) = the Charger gr2 skeleton's boneSteeringWheel world position
  (-0.374, 0.763, 0.388), not the STR1 wheel (0, 0.373, 0.69). The gr2 skeleton also has a `driver` bone (parent
  `body`, local (0, 0.10, -0.10)) where his hips are. So the driver is placed by the gr2 skeleton: `driver` bone =
  body root, `boneSteeringWheel` = hand target; the animation set and avpins template did nothing visible.
  v0.5.1-drivertest (23:10): v0.5.0 media with the skeleton gr2 edited by granny.py: boneSteeringWheel moved to the
  STR1 wheel (+0.374, -0.390, +0.302) and `driver` by (0, -0.15, +0.25) -> (0, -0.05, +0.15). If he follows:
  next tune the driver bone's position/rotation for a reclined seat (rotation = pitch the root back), and fold the
  two bone edits into build_str1.py (the skeleton.modelbin bone patch already does the same for the wheel model).
  RESULT v0.5.1 (3/4 + front shots 23:07/23:09): BOTH bones work — hands on the STR1 wheel, body moved forward/down.
  But he sits ON the tub, not in the bucket, and on the car's RIGHT (x ~ +0.3). Reading: the `driver` bone is the
  floor point under the seat (Charger: y 0.10 ~ its floor), the driver animation set adds the seat height (~0.3-0.5)
  and the seat's lateral offset (Charger set: -0.37 LHD; Atom set: +0.30 RHD — v0.5.x carry the Atom set).
  STR1 bucket from str1_geo (COCKPIT material): seat pan y ~0.08 at z 0.2-0.6, backrest z 0-0.1 rising to y 0.46,
  deck around the opening y 0.45-0.50, pedal area to z 1.6. v0.5.2-drivertest2 (23:12): driver bone (-0.30, -0.30,
  0.20) (cancel the Atom offset, 25 cm lower than v0.5.1, hips over the seat pan); steering bone as v0.5.1.
  Then: recline (driver bone pitch; convention verified: Granny matrices are row-vector, M[:3,:3] = R^T, chain
  world = local @ parent, inverse-world = inv(world) — max error 0.0 on all 56 Charger bones), then fold the
  skeleton gr2 edits into build_str1.py (constants DRIVER_POS / DRIVER_PITCH / steering = SW_CENTRE).
  v0.4.2 (29 Oct) = v0.4.1 + both of those: the 13 `scene/Drivers/default/*.gr2` from the Atom and the avpins
  Template set to LMP_OpenCockpit (made by hand from in/str1.zip, not by build_str1.py yet — fold it in once it's
  known to work; the Atom's driver sits at its RHD seat, x +0.3, so he may land off-centre).
