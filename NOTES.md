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
Don't decrypt protected mod files (CTDP GMTs are encrypted), don't edit/decrypt saves, personal use only.
(The "no ripped assets from other games" rule was removed by Owen on 30 Oct.)

## Formats (see fh2re/, tex/, f1/fhmat.py)
- swatchbin: data @0x53, BC7 = fmt 0x2e, GCN tiled (mips 0–2 2D, 3+ 1D). `tex/swatch.py write_like(template, rgba)`.
- MatI = Grub bundle (MATI base path + MTPR params; texture param = LEB128 path + crc32(lower path)).
- Modl blob: u16 counts @0 meshes, @2 buffers, @4 layouts, @6 materials. TRef lists crc32 of texture paths.
  New render meshes must go after ALL existing meshes (shadow ranges).
- Lights.bin: name table + 58 x 76-byte light entries (see DONOR ZIP ANATOMY). Engine sound = Data_Engine.MediaName → FMOD PG events (traffic cars have none).
- Torque table max 121 entries @100 rpm → 12,000 rpm cap; STR1 rescales rpm by K=11900/16700.

## Peugeot 207 (car 3207, media PEU_207SEHDi_08) — done ("it'll do")
car207/, sheik/, wheel/, tex/gauges_207.py. Latest: PEU_207_5door_v14.zip + peugeot207_database_v7.json.

## Toro Rosso STR1 — v0.6.0 on the Charger: wheels, track, driver all right in game (Owen, 29 Oct 23:20: "perfect!")
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

### Driving feel (29 Oct, Owen: "doesn't want to push past 170 and flips over at high speed")
Gearing checked: NumGears = forward gears + 1 (GearRatio0 = reverse) on every vanilla car, so 8 = 7 forward; 7th
tops at 192 mph at the 11,900 limiter. The 170 cap is DRAG: top speed ~ (hp/drag)^(1/3) scaled from the P1
(903 hp, drag 149 -> 253 mph) gives 171 mph for 723 hp / 390 units. v0.6.1: body drag 230 -> 170, wings
15-30 / 30-60 (total ~240 -> ~200 mph predicted). Downforce was 2-3x the strongest vanilla car (P1 310/575, best
wing row 34-91) on a 530 kg car — the likely flip: now body 300/500, wings 60-120 / 90-150. Owen to report; if it
still flips, next suspects: CMHeight 0.27, the 160/140 spring rates (Atom 46), BlockDimY.

### Next
Nothing blocking. The build is reproducible from the Charger donor + in/atom/ARI_Atom_13.zip (driver animations):
`make_media.py`, `str1_geo.py`, `build_str1.py in/donor_STR_ToroRosso_1_06.zip in/str1.zip`, `build_str1_db.py`,
mod_diff + id_conflicts nearest, `preview/asgame.py`, package. Possible polish: driver recline (Hips orientation
constant, same patch mechanism), seat height a few cm, STR1 rim styling, downforce feel.

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

## GENERIC BUILDER: build_car.py / build_car_db.py + cars/<car>/spec.py (29 Oct)
Any model on the Charger template. Per car: `cars/<car>/spec.py` (media name, material map, textures, steering wheel,
hips, eye, physics dict), model in `cars/<car>/src/` (gitignored). Steps, from the repo root:
  python3 f1/make_media.py f1/in/DOD_ChargerSRT8_12.zip cars/<car>/donor_<MEDIA>.zip <MEDIA>   (18-char media name)
  python3 fh2re/objgeo.py <model.obj> cars/<car>/geo.pkl <tyre material> --ground <0.149 - tyre radius> --axle-mid 0.0867
  python3 build_car.py cars/<car>/spec.py cars/<car>/car.zip
  python3 build_car_db.py cars/<car>/spec.py cars/<car>/custom.slt cars/<car>/strings.json; mod_diff -> database.json; nearest
  python3 preview/asgame.py cars/<car>/car.zip cars/<car>/database.json --donor f1/in/DOD_ChargerSRT8_12.zip --geo cars/<car>/geo.pkl
  package: cars/<car>/pkg/<Name>/ (mod.json, CREDITS.txt) + database.json + strings.json + media/cars/<MEDIA>.zip
Body goes into body_a (paint = the game's 'carpaint' so it is paintable, chrome = 'frame', black = 'blkplastic_hgl',
textured keys via the interior_lod1 MatI), glass into glassF_a ('gls_windsheild'); every other donor part dropped, so
no working lights yet (Lights.bin names the 12 light parts and places 58 light sources on them; a later job). Soup vertices are
welded on position+normal (SketchUp OBJs have a uv per corner; a 470k-face model still makes a 48 MB body_a).

### Peugeot 208 (2021, tonielpro520, CC BY) — v0.1.4 (30 Oct 00:20): done to the STR1's standard
cars/peugeot208: car 3208, make Peugeot (id 203, nearest), media PEU_208PureTech_21, 1.2 PureTech 130 EAT8 FWD physics
(Fiesta Mk7 suspension scaled by mass), model track 1.397 used (real 1.496), wheelbase 2.55 model / 2.54 physics,
tyres 205/45 R17, drag sized for 129 mph. Driver: Charger set, hips (-0.33, 0.44, 0.0), steering (-0.385, 0.72, 0.40)
from the model's own wheel (its interior is kept as black plastic, so the Charger steering wheel part is dropped).
asgame PASS (wheels within 1 cm). IN GAME (Owen, 23:53): loads, paintable red, clear glass with the black interior
behind it, driver at the wheel, tyres in the arches, drives. Rims: "not attached to the tyre, and don't move"
(stills show them centred; the complaint is rotation). v0.1.1 (23:58): build_car.py now also moves the gr2
hubXX/controlArm_XX bones and the carbin wheel/brake transforms to the car's wheel centres, so every source agrees
with the database (asgame now warns when the built carbin disagrees with the DB position instead of with the
donor). Owen (00:00): the rims that "don't move" were the 208 model's OWN wheels, baked into the body as black metal
(Carro_Metal_Preto is exactly the four wheel envelopes); the Charger rims underneath spin fine. v0.1.2 (00:05): the
model's wheel (Carro_Roda, Roda_1, Metal_Preto, Cromado cap) goes into the donor wheel part instead, the way
wheel/build_wheel.py did the 207's — fh2re/rimbuild.py: scale the LF wheel to R 0.1397 in the part's space
(x = depth outward -x), single-sided by the model's normals, size morphs (width -0.9 on x>0.5, diameter 1.3247 y/z,
unknown row from the nearest donor vertex), AO UVs from the nearest front-facing donor rim vertex, the donor's
inner_rim barrel kept, its hub/lugs/badge dropped. Spec: RIM_MATERIALS. 21k tris. Not yet seen in game.
IN GAME v0.1.2 (Owen 00:08): rims spin and look right, but "floating nuts" and "wheels too close together".
v0.1.3 (00:12): the rim's unknown morph row is now zero (the donor's values, up to +/-0.037, had displaced the nut
bosses); track from the spec (real 1.496/1.483 — the model's wheels sit 5 cm in from its arches) for the database,
the carbin and the gr2 alike (build_car.py uses PHYSICS body track for wheel x; the rim is still cut from the model's
own wheel centre). asgame --tol 0.06 for such deliberate offsets.
v0.1.3 in game (00:14): nuts still floating, wheels still a little inboard. v0.1.4 (00:20): (a) rim winding no
longer trusts the model's normals on the face planes — triangles facing +/-x near the front are wound to face out,
deeper ones to face the barrel (243 black-spoke triangles were inward: the nut recesses, which made the nut heads
look detached); (b) RIM_BLACK_MATERIALS -> the wheel part's group 1 'black' material (Metal_Preto spokes), the
machined faces + cap stay 'rim' silver; (c) track 1.55 / 1.54 by eye (arch lips measure 0.838 F / 0.850 R, so the
tyre face already reached the lip at 1.496 — the inboard look is probably the rim sitting deep in the tyre, see
whether this helps).
v0.1.4 in game (00:20, rear-low and side wheel close-ups): black spokes with machined faces, lion cap, nuts in
their recesses, Brembo through the spokes, tyre flush with the arch front and rear. KEEPER.
Left for both cars: working lights (the donor light parts are dropped; Lights.bin names them — a later job), and
cosmetic polish on request. Generic-builder lessons from the 208, now in build_car.py / rimbuild.py: a model's wheels
must come OUT of the body (find them by material bounding boxes = the wheel envelopes) and go into the wheel part;
never trust SketchUp normals for winding on the face planes; the unknown morph row stays zero; track by eye.
(Earlier open question, now moot: do the STR1's rims rotate? v0.6.2-origskel can be ignored.) If neither car's do, suspect the raw-rewritten skeleton gr2
(test: ship the ORIGINAL compressed skeleton gr2 with no bone edits and see if rims turn; the driver's hands would
go back to the Charger wheel for that test).

### Volvo V70 T5 (P2, 2005; model by KOElkast1007, Sketchfab free licence; GTA-like art style only: GTA has no V70, so not a game rip (Owen, 30 Oct)) — v0.1.0 (30 Oct 00:35)
cars/volvov70: car 3700, make Volvo (204), media VOL_V70T5_2005_P2_ (18 chars — a 16-char name silently corrupted the
renamed modelbins: make_media must keep the length), 2.4 T5 260 hp / 350 Nm, M66 6-speed, FWD, 1,515 kg, Focus RS
'09 sound (Volvo I5). fh2re/glbgeo.py: the glb's body nodes are Z-up/Y-forward and its wheel nodes sit in their own
Y-up frame, so the body frame is given (--frame=-x,z,y), wheel centres come from the body's arches (y 2.2 / -0.8,
lip 0.73 -> centre 0.31, half track 0.86, model units; scale 0.9183 for a 2.755 wheelbase) and the rim from the
wheel_lf.child_ node's local coords (face at min x, as the wheel part wants). asgame PASS. Not yet seen in game.
Pipeline note: never `| head` a script that writes its output at the end (SIGPIPE killed glbgeo before the dump).
IN GAME v0.1.0 (00:39): "looks good other than the tracking" — wheels deep in the arches. TRACK RULE OF THUMB (208
and V70): the game draws the wheel ~5 cm per side inboard of x = ModelTrackOuter/1.012/2; set the track so the
DB tyre face (x + width/2) sits ~4 cm beyond the body's arch lip (208: lip 0.838 -> 1.55; V70: lip 0.90 -> 1.65).
v0.1.1 (00:42): track 1.65.

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
  RESULT v0.5.2 (front + side 23:11): the `driver` bone move did NOTHING (same spot as v0.5.1, still on the car's
  right, still on top). So v0.5.1's move came from boneSteeringWheel alone. FOUND the seat: every driver animation
  (scene/Drivers/default/*.gr2) has a 'Hips' transform track whose PositionCurve is a D3Constant32f:
  Charger (-0.397, 0.507, -0.039) = its LHD seat, Atom (+0.313, 0.202, -0.238) = its RHD seat — relative to the
  steering bone (the v0.5.1 evidence; absolute would not have moved him). Orientation is a D4Constant32f (pelvis
  angle), the root track is identity, InitialPlacement is zero.
  v0.5.3-hips (23:20): Atom driver set with Hips constant = (0, 0.14, 0.18) - wheel (0, 0.373, 0.69) = (0, -0.233,
  -0.51) in all 13 files (4 have a constant Hips curve: set; 9 are quantised keyframes D3K8uC8u / D3I1K8uC8u with
  ControlScales ~1e-6 and ControlOffsets = the seat: offsets shifted by the same delta), skeleton gr2
  with boneSteeringWheel at the STR1 wheel and the `driver` bone left as the Charger's. If he lands in the bucket:
  tune y/z, then recline via the Hips orientation constant, then fold both patches into build_str1.py.
  RESULT v0.5.3 (23:17): driver INVISIBLE. Either the Hips position is absolute in car space (then (0, -0.233, -0.51)
  put him 5 cm above the ground inside the engine cover) or the raw-rewritten animation gr2s are rejected.
  v0.5.4-hipsabs (23:22): same patch with Hips = (0, 0.14, 0.18) absolute. In the bucket -> absolute; high over the
  nose -> relative to the wheel bone; still invisible -> the animation rewrite is the problem (test: ship ONE
  rewritten file, e.g. idle.gr2 unmodified but re-written raw, with the other 12 original).
  RESULT v0.5.4 (23:20): "perfect!" — in the bucket, head level with the airbox, hands on the wheel. So the Hips
  position is ABSOLUTE in car space. DRIVER RULE: hands follow the skeleton gr2's boneSteeringWheel; seat = the
  'Hips' track position in every scene/Drivers/default/*.gr2 (absolute); the `driver` bone and the avpins template
  do nothing visible; the animation set only changes the pose (Atom set = low sports pose, kept).
  Folded into build_str1.py (v0.6.0, 23:25): patch_skel_gr2 (boneSteeringWheel -> SW_CENTRE), driver animations
  from DRIVER_ANIMS_ZIP (in/atom/ARI_Atom_13.zip; falls back to the donor's set) with Hips -> DRIVER_HIPS
  (0, 0.14, 0.18) via granny.set_track_position, avpins Template -> LMP_OpenCockpit (harmless). Rebuilt media
  matches the hand-built v0.5.4 (only float last-bits and texture GUIDs differ); asgame PASS.
  v0.4.2 (29 Oct) = v0.4.1 + both of those: the 13 `scene/Drivers/default/*.gr2` from the Atom and the avpins
  Template set to LMP_OpenCockpit (made by hand from in/str1.zip, not by build_str1.py yet — fold it in once it's
  known to work; the Atom's driver sits at its RHD seat, x +0.3, so he may land off-centre).

## DONOR ZIP ANATOMY (30 Oct, every file in DOD_ChargerSRT8_12.zip and what build_car.py does with it)
Everything not listed as "rewritten" is carried over with the Charger's values (make_media.py only renames the media).
- `<media>.carbin` (41 KB): the part list = what the game loads for each upgrade part id (1422000 CarBody, 1422001
  FrontBumper race, 11038 WheelStyle...), each part's modelbin path and transform; type 2 = body parts, 43 = wheel
  spindles, 4 = brakes. Rewritten: pruned to KEEP_PARTS + wheels/brakes, wheel/brake transforms moved.
  `.carbin_debug` = the exporter's part-name table (PG-LEAM-BS08, 2014/08/14), unused by the game.
- `physicsdefinition.bin` (2,244 B): the COLLISION HULL. Header 1,0,20,1; bbox half-extents at byte 84 (x 0.951,
  y 0.650, z 2.532 + 2.672); then two blocks (hdr 48 B: 0.650, 0.0025, 2, 5, 1040, flags, 0, 48, 0, 62, 0, 1040) of
  62 vertices x 16 B (u32 0, x, y, z): block 1 = the convex hull of the Charger (x +/-0.951, y 0..1.301, z -2.530..
  2.535, 112 faces, 8.97 m3), block 2 = the same hull with every y < 0.2 raised to 0.2 (the underbody hull: ground
  clearance). NOT rewritten: the 208 (4.06 m) and V70 (4.73 m) collide as a 5.07 x 1.90 m Charger; Data_CarBody
  PristineBoundingBox* is set from spec but is probably only the camera/garage box. Fix = emit the model's own hull
  (scipy ConvexHull of the body soup, decimated to ~60 verts) in this layout — not done yet.
- `Locators.xml` (62 locators, 4x4 SceneTransform in car space + bone): camera/UI anchors (carLocator_wheelLF
  -0.940,0.152,1.591; headlightL; hood; trunk; seatCamLF -0.38,1.05,-0.20; steeringWheel -0.375,0.754,0.371;
  gauges; dashboard; doorLF..RR + door handles on the door bones; entryDoor*; skirt*), audio points (Audio_Engine,
  Audio_Intake, Audio_Exhaust, Exhaust_001/002 = the backfire flames at the tailpipes, engineSmoke), paddleShift*,
  stickShift, Handbrake. The Hero cinematic cameras attach to these. Rewritten: wheel locators only (build_str1).
- `Lights.bin` (DEADBEEF, ver 1): u32 count=12, then 12 x (u32 len, modelbin path, u16 flag 1 or 27) naming the
  light parts, then u32 58 + 58 entries x 76 B = (u32 type, u32 flags, u32 part index, pos xyz, 0, quaternion xyzw,
  pos2 xyz, 0, quat2 xyzw) + 4 zero bytes. Types: 0 CHMSL LEDs (10 in a row), 1 DRL?, 2 fog, 3 indicators F,
  4 side repeaters?, 5/6 high beam L/R, 8/9 low beam L/R (quat tilts 10 deg down), 7 tail (flags 0x20045), 10 reverse,
  11 tail LEDs (15 per side). Each light = a point ON the lit part; glow sprites/beam come from LightPresets.bin.
  Since the light parts are dropped, nothing lights up. A custom car needs: lit material names on the body
  (`*_custom_head/_brake/_reverse/_turn` in the 207 mod) or re-pointing these entries at body_a + new positions.
- `LightPresets.bin` (LDIB/PRST): per-light-type look (colour, intensity, cone, the xenon headlight beam projection
  textures from cars/_library). `_debug` = same with names. Carried over.
- `<media>.avpins` (XML, Template="4Door_Sedan"): Forzavista points of interest: 5 views (EngineView, 4 seat cams on
  the seatCam locators), 64 POIs (open/close each door/hood/trunk, ChangeColor, Dimensions, EngineInfo...) each with
  cursor Pos, Apex/Distance, preconditions and PartVisibilityAffects. Rewritten: Template only (STR1).
- `Animations/*.gr2` (16): door/hood/trunk open+close, fuel/speedo/tacho needles, wiperFront — one transform track
  each on the skeleton bone (boneDoorLF...). `Animations/<media>.gsf` = Granny state file: the AnimationSlots (16)
  -> these files, model hint `..\carscene\DOD_ChargerSRT8_12\Export\scene\DOD_ChargerSRT8_12_fullMesh.gr2`.
  Carried over (the parts they move are gone, harmless).
- `scene/<media>_skeleton.gr2` (56 bones; listed by `fh2re/granny.py info`): root -> root_bone{Wipers,Hood,Door*,
  Gauges,SteeringWheel,Trunk} (pivots in a y-up/forward export frame, 1.7-1.87 m), hubLF..RR = controlArm_LF..RR =
  the wheel centres (-0.832,0.212,1.272 / -0.840,0.236,-1.523), spindleXX under the hubs, boneSteeringWheel +
  boneSteeringWheelSpindle, body, driver (0,0.1,-0.1 under body), rotor*_center, wiper blades + locators, hood
  struts. Rewritten: boneSteeringWheel, hubXX/controlArm_XX. `_skeleton.modelbin` = the same skeleton as a Grub
  Skel blob (steering spindle patched).
- `scene/Drivers/default/*.gr2` (13): driver animations, 130 tracks (Hips = seat, absolute), ...
- `scene/Exterior/**`, `scene/Interior/**`: 90 modelbins, one per part, grouped by upgrade slot; `*_AO.swatchbin`
  beside them = per-part baked occlusion; `__SLOD` = the super-low LOD used at distance. Kept: body_a, glassF_a
  (rewritten), wheelLF, calipers/rotors, controlArms; everything else dropped.
- `Materials/*.materialbin` (paint, glass, INT_*): the car-specific shader instances (paint -> livery test textures,
  glass -> mask) referenced by the MatIs; `Shaders/*.shaderbin + 256 .vso/.pso` = compiled HLSL per material x
  scenario x platform (pc/durango). Carried over.
- `Textures/`: AO (30), Damage (impactMask/splatterMask), wiper masks, gauges DIFF/LITE, interior DIFF/GLOS/LITE,
  LOD, lp (licence plate), symbol; `Textures/Livery/Swatches` + `LiveryMasks/*.swatchbin` + `Masks.xml` = the
  livery editor projections (per-view origin/scale/axes); `UI/*.xaml` + `DigitalGauge/` = the Charger's LCD
  odometer/gear display (WPF page: UseMPH, MaxSpeed 120, Shift_D/R storyboards). Carried over.
- `ManufacturerColors.bin` (burG/LCNM): the 5 stock paints (Redline Red Pearl, Black, Tungsten, Bright Silver,
  White) as library carcolor materialbins + RGB. Carried over (Charger colours in the paint shop).
- `Cinematics/AV_Hero_Tour.xml` + 13 subtitle files: the Forzavista hero-tour camera path (cameras attached to
  carLocator_wheelLF/hood/headlightL/gauges...). `SizeReport.xml`, `BuildNumber.txt`: exporter reports, unused.


## Owen's workflow: "drop in a model, get a car back"
Owen will often be away from his Mac (laptop at home, possibly off) and will drop a new 3D model
into a cloud session from his phone. He expects back a **finished, installable car mod zip** plus the
Terminal install command, without having to answer questions along the way. So:
- Do the whole pipeline unattended with build_car.py on the Charger generic donor (no donor-picking any more:
  ModelWheelbase/track in the DB place the wheels): write cars/<car>/spec.py, build body/rims/glass, set up the
  DB entry (sensible name, make, price, physics for the car type), package as an Extra Options mod
  folder with mod.json/database.json/strings.json/CREDITS.txt, `id_conflicts: nearest`.
- Run the game-accurate preview and fix anything that fails before handing it over; include the
  PASS/FAIL report and top/side images.
- Make sensible choices instead of asking; list them briefly at the end (what donor, what was guessed).
- Only use models he has the right to use (licence that allows it); credit the author in CREDITS.txt.
  Never commit game files or third-party models to GitHub — code only.
- In-game testing happens when he's back at his Mac; expect a round or two of tweaks then.

## AUTOSHOW PRESENTATION: thumbnails, make logos (30 Oct, Opus)
Learned from a working add-on car (the ZS/MSF Williams FW24, structure only):
- UI swatchbins (tex/uiswatch.py): 84-byte header (car textures: 83), ONE BC7 level, GCN 2D-tiled like car textures,
  zero-padded to 4 KB. Thumbnails 816x459 (_Big) / 192x108 (_Small); make logos 220x184 (Manu_Logo_<CODE>) and
  440x376 (L_Manu_Logo_<CODE>); transparent backgrounds. Files go in the mod's media/stripped/RC0/.
- Data_Car.Thumbnail = game:\Media\Stripped\RC0\Thumbnail_<carId>.png (the game appends _Big/_Small, .swatchbin).
- List_CarMake.IconPath / IconPathLarge point at the logo swatchbins; IconPathBase = make name without spaces
  (vanilla: 'AstonMartin'). Our older builds borrowed ARI/REN logos and other cars' thumbnails.
- The 207's old thumbnails had an 83-byte header (car-texture style) — wrong for UI swatchbins.
Tools: fh2re/carpreview.py (any car zip -> glb, --paint, --tyres from DB sizes since the game draws tyres itself),
scan/viewer/thumb.html + thumb.js (transparent 3/4 render, `node thumb.js car.glb out.png 816 459 -50 10`),
fh2re/presentation.py (writes thumbnails + logos into a mod folder, rewires the DB, or moves a car onto an existing make).
Applied 30 Oct: STR1 (own TORO ROSSO wordmark), 207 (PEUGEOT wordmark, new thumbnails), 208 (onto the 207 mod's
Peugeot make 201, depends on owen-peugeot-207), V70 (onto vanilla Volvo make 53, real logo).
RULES: make string_base unique across ALL of Owen's mods (the 208's 64208 overwrote the 207's short name; now 64218).
Use a vanilla make when one exists (List_CarMake: Volvo 53, Ferrari 13, ...). build_car_db.py should grow a
`use_make` option and call presentation.py at the end — not done yet.

## STR1 own rims (30 Oct, Opus): f1/str1_rims.py
Post-processes a built STR1 car zip with fh2re/rimbuild.py (the 208 route): model HUB_LF rims from str1_geo.pkl,
MCLHUB -> wheel part 'rim' (silver), MCLRIM + MCLSPOKES_OP -> 'black' (the model's rims are anthracite, ~RGB 62);
*_BLUR motion-blur copies and the see-through MCLSPOKES duplicate left out. Model rim radius 0.195 m (incl. flange)
-> R 0.1397. v2 (30 Oct): spokes/hub recentred on the barrel axis (they were 6-8 mm off: wheel wobbled), scale
reference = tyre inner radius 0.167 (rimbuild r_ref) with the under-tyre lip trimmed. v3: rimbuild trust_normals=True —
the 208's SketchUp rule 'flat faces deeper than 3 cm face the barrel' turned the STR1's dished hub/spokes inside out
(invisible rims in game). Use trust_normals for models with good normals (AC/rFactor sources). Waiting on in-game check.
