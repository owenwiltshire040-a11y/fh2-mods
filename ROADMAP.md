# Roadmap: "drop in a model, get a car back" (no donor-picking)
Written 29 Oct 2026. Work branch: claude/upbeat-ride-q9oqy7. ⏸ = waiting on an in-game check by Owen.

## Done
- STR1 builds end to end on the Charger donor; wheels land on the STR1 axle lines in game (v0.4.0/v0.4.1).
- Track width follows the database (confirmed on the 207 and STR1).
- preview/asgame.py: as-game placement checks + renders.
- fh2re/granny.py: reads FH2 .gr2 files (Oodle1 decoder ported) and writes them back uncompressed; can move bones.

## Phase 1: the deciding test ⏸ (about 10 min of Owen's time)
Install v0.4.3-gr2test; in the Autoshow, look straight down at the STR1.
- Left-front wheel 10 cm further out than the right-front → the .gr2 skeleton drives wheels. Go to Phase 2 (gr2 route).
- Wheels symmetrical, car loads → try the same 10 cm on the carbin transform instead (one quick build, one more check).
- Car won't load → send FH2_ExtraOptions.log; fix the writer first.
Also waiting: v0.4.2 (open-cockpit driver/camera template) — is the driver sitting in the cockpit?

## Phase 2: automatic wheel fitting (1–2 sessions + 1 check)
- Rescaler: move all four hubs (whichever route Phase 1 proves) to the model's axle points.
- Fold into build_str1.py; asgame.py checks the result. STR1 rebuilt with it as proof.

## Phase 3: template cars (a few sessions + a check per template)
- Road-car template (Charger-style: no suspension animations, simplest).
- Open-wheeler template (STR1: driver pose, seat, cockpit camera).
- Maybe a small hatchback/van template later.
- Driver seat position and hand/steering-wheel placement rescaled per model.

## Phase 4: model-in, car-out pipeline (the long one: several sessions)
- Auto-detect wheels/axles, body vs glass vs lights vs interior from any model.
- Materials (carpaint vs textured vs chrome vs glass) and textures.
- Lights wired up automatically (head/brake/reverse/indicator).
- Interior: use the template's cockpit and dials unless the model has a usable one.
- Physics from the car type (mass, power, gearing, aero) + database entry + packaging.
- asgame.py grows a check for each rule as it's confirmed in game.

## Phase 5: polish (any time)
STR1's own F1 wheels/tyres; downforce tuning; rain light; move traffic mods' colour IDs; 207 vinyl mapping.

## How far away
Wheel fitting without picking a donor: one in-game check + ~1–2 sessions, if Phase 1 works.
Reliable "any model in, finished car out": weeks of sessions, with roughly 5–10 quick in-game checks along the way.
