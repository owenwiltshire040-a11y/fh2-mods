# Car build quality

Owen wants source cars prepared thoroughly before the first in-game test. Do not use a generic donor wheel as a silent fallback or describe an incomplete prototype as finished.

- Select and record each car's source wheels, or explicitly identify an appropriate replacement when source wheels are absent. Preserve wheel-face textures and remove original static wheel geometry from the body.
- Packaging must reject missing custom wheels and unchanged Charger wheel faces. Keep `fh2re/wheelcheck.py` in the packaging path. Inspect the actual built model, its nominal rim diameter, axial depth, all detail levels and diameter/width morphs; spec-only checks are insufficient.
- Check that source spokes face outward. Replace the donor inner backing plate with an open barrel; retained plates can hide the source face. Preview brake parts must retain their own inward offsets instead of being placed at the rim spindle reference.
- Check model and physical wheelbase, rim-face convention, axle midpoint/height, tyre width/aspect and database consistency before installation. Never bypass a failed fit check to finish a batch.
- Review the built previews of every car. Look for detached parts, missing panels, duplicated rims, mixed wheel variants, blank texture-based hubcaps and remaining donor badges.
- Run the relevant regression and package checks. Stage updates, preserve the installed version and verify copied files before changing the active batch.
- Distinguish source-accurate geometry, provisional physics/cockpit placement, functional versus decorative lighting, and runtime validation. Offline previews cannot establish that a car works correctly in the running game; say so clearly.
- Preserve existing confirmed Passat, Model Y, Peugeot and Jordan builds. Do not overwrite a hand-curated spec/geometry by rerunning the initial batch generator.
