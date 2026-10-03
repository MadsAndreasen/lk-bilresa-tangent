# LK switch tangent → BILRESA magnet seat

A 3D-printable replacement tangent (rocker cover) for a 1-module **LK NES / Fuga** wall switch that

- **locks the switch ON**, so a smart bulb always has power, and
- holds the magnet plate of an **IKEA BILRESA** scroll-wheel remote, so the remote clicks onto the old switch.

It snaps onto the switch's rocker like the original. The OFF-side end-stop pin is lengthened so the rocker can't leave the ON position, and the front cap is angled so the remote sits parallel to the wall.

Parametric [Build123d](https://github.com/gumyr/build123d) model. All dimensions are in `src/lk_bilresa/params.py`. Values marked `TO VERIFY` were measured from photos (`pics/`) and may need tuning for your switch.

## Usage

```sh
uv sync
uv run pytest                                   # geometry checks
uv run python scripts/export.py                 # out/tangent.step, tangent.stl, coupon.stl
uv run python scripts/export.py --param boss_od=4.3 --param on_tilt_deg=5
uv run python scripts/show.py                   # view in VS Code "OCP CAD Viewer"
```

## Printing

PETG, face-down, no supports. Print `coupon.stl` first: it has only the snap pegs and stop pins, so you can check the fit in about 10 minutes. Then print `tangent.stl` and glue the 48 × 19 × 1 mm BILRESA plate into the front pocket.

⚠️ Work on mains switches at your own risk. The tangent only clips onto the front of the switch, so nothing has to be rewired.
