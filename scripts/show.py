"""Show models in the OCP CAD Viewer (VS Code extension "OCP CAD Viewer").

    uv run python scripts/show.py [--param key=value ...]   # live tangent + fit coupon
    uv run python scripts/show.py out/tangent.step pics/x.stl  # any STEP/STL files

Open the viewer first in VS Code: Ctrl+Shift+P -> "OCP CAD Viewer: Open viewer".
"""

import argparse
from pathlib import Path

from build123d import Pos, import_step, import_stl
from ocp_vscode import show

from export import parse_overrides
from lk_bilresa.params import TangentParams
from lk_bilresa.tangent import build, fit_coupon


def load(path: Path):
    suffix = path.suffix.lower()
    if suffix in (".step", ".stp"):
        return import_step(path)
    if suffix == ".stl":
        return import_stl(path)
    raise SystemExit(f"unsupported file type: {path}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*", type=Path)
    ap.add_argument("--param", action="append", default=[], metavar="KEY=VALUE")
    args = ap.parse_args()

    if args.files:
        show(*[load(f) for f in args.files], names=[f.name for f in args.files])
        return

    p = TangentParams().with_overrides(**parse_overrides(args.param))
    coupon_x = p.cap_width + 15  # place the coupon beside the tangent
    show(build(p), Pos(coupon_x, 0, 0) * fit_coupon(p), names=["tangent", "coupon"])


if __name__ == "__main__":
    main()
