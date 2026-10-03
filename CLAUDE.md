# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A 3D-printed (PETG, FDM) replacement tangent for a 1-module LK switch (the original is stamped "LK NES", Fuga's predecessor). It:
1. snaps onto the switch's rocker carrier with 4 split bosses, like the original;
2. locks the rocker in ON, using a lengthened OFF-side end-stop pin, so the smart lamp always has power;
3. has a flush stadium pocket on a wall-parallel front cap for the IKEA BILRESA scroll-wheel's 48×19×1 mm magnet plate.

Reference photos with a ruler are in `pics/`. Dimensions taken from them are marked `# TO VERIFY` in `params.py`.

## Commands

```sh
uv sync                                    # install (Python 3.12, pinned via .python-version; OCP has no 3.14 wheels)
uv run pytest                              # all geometry tests
uv run pytest tests/test_tangent.py::test_both_stops_touch_base_in_on   # single test
uv run python scripts/export.py            # -> out/tangent.step, tangent.stl, coupon.stl
uv run python scripts/export.py --param on_tilt_deg=5 --param boss_od=4.3   # tune without editing code
uv run python scripts/show.py [--param k=v]       # live view in VS Code "OCP CAD Viewer" (open the viewer first)
uv run python scripts/show.py out/tangent.step    # view any STEP/STL file
```

## Architecture

- `src/lk_bilresa/params.py`: a frozen `TangentParams` dataclass. It is the single source of every dimension. Derived values (`off_stop_len`, `cap_back_z`, `pocket_floor`, `tilt_sign`) are properties, never stored.
- `src/lk_bilresa/tangent.py`: pure functions `Params -> Part` (Build123d algebra mode).
- **Two coordinate frames** (this is the key idea):
  - **Carrier frame**: rocker neutral, origin at the back face. The skirt, bosses, stops and neck are built here.
  - **Wall frame**: the carrier frame rotated by `tilt(p)` into ON about the pivot axis. `carrier_part()` tilts the rocker features and clips them at `cap_back_z`. `cap()` and `magnet_pocket()` are built directly in the wall frame, so the BILRESA face is parallel to the wall.
- Lock condition: `off_stop_len = stop_len + stop_pitch·tan(on_tilt)`, which makes both pin tips touch the base plate in ON. `test_both_stops_touch_base_in_on` guards this.
- STEP is exported in the installed orientation. STLs go through `print_orientation()`, which flips them face-down on the bed so no supports are needed.
- `fit_coupon()` is a small plate with only the bosses and stops. Print it first to validate the interface before printing the full tangent.

## Conventions

- Build123d by default. Use CadQuery only if a sweep or an export pipeline requires it. No OpenSCAD.
- Every key dimension is a `TangentParams` field: no magic numbers in the geometry code. Replicate repeated features with locations (`GridLocations`, `Pos`) rather than redefining them.
- Keep the geometry print-friendly: no supports when printed face-down, and PETG-appropriate clearances.
