# Roadmap: "drop in a model, get a car back"
Updated 30 Oct 2026 (Opus). Details per car in NOTES.md.

## Done
- Generic donor (Charger): wheels placed by Data_CarBody ModelWheelbase / ModelTrackOuter.
- `package_car.py spec out/` = one command to a finished mod folder: body, glass, own rims (rimbuild), working lamps
  (lightbuild: head, tail/brake by day, reverse, CHMSL), database + strings (string IDs checked across mods),
  Autoshow thumbnail rendered from the car, make logo or an existing make.
- Cars: STR1 (own rims, logo, thumbnail), Peugeot 208 (lamps confirmed day + night), Volvo V70 (vanilla Volvo make),
  Peugeot 207 (logo, fixed thumbnail), Williams FW24 (ZS mod repackaged for Extra Options).

## Next
1. Automatic track width: measure the arch lips, tyre face ~4 cm past the lip.
2. Interiors: real materials/textures instead of flat black; dials.
3. V70 lamps (needs its source model again: "Volvo V70" by KOElkast1007, Sketchfab).
4. Small jobs: traffic mods' Combo_Colors IDs, STR1 rain light / driver recline / stability, indicators where a model
   has separate indicator lamps (lightbuild 'turn_f' / 'turn_r'), real logo artwork from PNGs.

## Each new car costs
One spec.py (materials, lamp boxes, physics) + `package_car.py` + 1-2 quick in-game checks.
