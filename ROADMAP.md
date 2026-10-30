# Roadmap: "drop in a model, get a car back"
Updated 30 Oct 2026 after merging Fable's branch. Details per car in NOTES.md.

## Done
- No more donor-picking: the Charger is the generic donor. Wheels are placed by Data_CarBody ModelWheelbase
  (fore/aft) and ModelFront/RearTrackOuter (side to side); the gr2/carbin wheel transforms don't matter on it.
- build_car.py + build_car_db.py + cars/<car>/spec.py: model in, mod out. fh2re/objgeo.py (OBJ), fh2re/glbgeo.py (glb),
  fh2re/rimbuild.py (the model's own rims in the game's wheel part), fh2re/granny.py (gr2 read/write).
- preview/asgame.py checks wheel placement against the database rules.
- Cars: STR1 v0.6.1 (driver in the cockpit, aero in range), Peugeot 208 v0.1.4 (keeper), Volvo V70 v0.1.3 (track pick pending).
- Track rule of thumb: set the track so the tyre face sits ~4 cm beyond the body's arch lip.

## Next
1. Working lights: map the model's lamp materials onto the donor's 12 light parts / Lights.bin (see DONOR ZIP ANATOMY).
2. Fold the track rule of thumb into build_car.py (measure the arch lips automatically).
3. Interior: the model's own interior is kept as black plastic; use real materials/textures; dials.
4. STR1 polish: own rim styling, driver recline, top-speed/stability feel.
5. Odds and ends: rain light, traffic mods' colour IDs, 207 vinyls.

## Each new car costs
One spec.py + a build + 1–3 quick in-game checks (track, rims, driver).
