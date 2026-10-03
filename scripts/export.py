"""Export the tangent and fit coupon.

    uv run python scripts/export.py [--param key=value ...] [--out DIR]

STEP is in the installed orientation; STLs are flipped face-down for printing.
"""

import argparse
from dataclasses import fields
from pathlib import Path

from build123d import export_step, export_stl

from lk_bilresa.params import TangentParams
from lk_bilresa.tangent import build, fit_coupon, print_orientation


def parse_overrides(pairs: list[str]) -> dict:
    types = {f.name: f.type for f in fields(TangentParams)}
    out = {}
    for pair in pairs:
        key, _, value = pair.partition("=")
        if key not in types:
            raise SystemExit(f"unknown parameter {key!r}; choose from: {', '.join(types)}")
        out[key] = value if types[key] in (str, "str") else float(value)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--param", action="append", default=[], metavar="KEY=VALUE")
    ap.add_argument("--out", type=Path, default=Path("out"))
    args = ap.parse_args()

    p = TangentParams().with_overrides(**parse_overrides(args.param))
    args.out.mkdir(parents=True, exist_ok=True)

    tangent = build(p)
    export_step(tangent, str(args.out / "tangent.step"))
    export_stl(print_orientation(tangent), str(args.out / "tangent.stl"))
    export_stl(print_orientation(fit_coupon(p)), str(args.out / "coupon.stl"))
    print(f"wrote {args.out}/tangent.step, tangent.stl, coupon.stl (OFF stop {p.off_stop_len:.2f} mm)")


if __name__ == "__main__":
    main()
