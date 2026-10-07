"""All dimensions for the locked-ON tangent, in millimetres / degrees.

Coordinate frames
-----------------
* Carrier frame: origin at the centre of the tangent's back face (where the
  bosses start), +Z away from the wall, +Y up, untilted (rocker neutral).
* Wall frame: same origin, but the rocker is rotated into the ON position
  about the pivot axis. The front cap is built in this frame, so its face is
  parallel to the wall.

Values marked "TO VERIFY" were scaled from ruler photos in pics/ (±1 mm) and
should be confirmed with calipers or the fit coupon.
"""

from dataclasses import dataclass, replace
from math import radians, tan


@dataclass(frozen=True)
class TangentParams:
    # --- Original tangent body (fits inside the frame opening) ---
    width: float = 43.0  # TO VERIFY: frame opening is ~44.5
    height: float = 43.0  # TO VERIFY
    orig_face_thickness: float = 2.0  # TO VERIFY: original face plate, sets neutral front
    skirt_depth: float = 4.0  # TO VERIFY: skirt height behind the back face
    skirt_wall: float = 1.2
    side_notch_h: float = 15.0  # TO VERIFY: relief in left/right skirt (screw clearance)
    side_notch_depth: float = 3.0  # TO VERIFY

    # --- Front cap (wall-parallel, covers the whole frame) ---
    cap_thickness: float = 2.6
    cap_gap: float = 0.8  # air gap between cap back and frame rim
    rim_offset: float = 0.0  # TO VERIFY: rim front minus original tangent front (neutral)
    cap_edge_radius: float = 1.0

    # --- Shroud (perimeter wall from the cap back towards the wall, hides the frame) ---
    frame_size: float = 50.0  # TO VERIFY: outside of the square switch frame
    frame_depth: float = 9.0  # TO VERIFY: frame rim front to wall surface
    shroud_wall: float = 1.6
    shroud_clearance: float = 0.5  # per side, shroud inside to frame outside
    wall_gap: float = 1.0  # shroud edge stops short of the wall (uneven paint)

    # --- Snap bosses (4x split tubes into the carrier holes) ---
    boss_pitch_x: float = 10.5  # TO VERIFY
    boss_pitch_y: float = 12.5  # TO VERIFY
    boss_od: float = 4.4  # TO VERIFY
    boss_id: float = 2.0
    boss_slot_w: float = 0.8
    boss_height: float = 5.0  # TO VERIFY
    boss_lip: float = 0.2  # radial snap bead at the tip
    boss_lip_h: float = 1.0
    fit_clearance: float = 0.0  # added to the boss OD; negative = tighter

    # --- End stops (2x pins on the vertical centreline) ---
    stop_pitch: float = 29.0  # TO VERIFY
    stop_d: float = 3.5  # TO VERIFY
    stop_len: float = 5.0  # same as boss_height, like the original
    on_tilt_deg: float = 4.0  # TO VERIFY: rocker tilt from neutral to ON
    on_side: str = "bottom"  # edge pressed in when the light is ON
    pivot_depth: float = 8.0  # TO VERIFY: pivot axis distance behind the back face

    # --- BILRESA magnet plate pocket (stadium, vertical) ---
    plate_l: float = 48.0
    plate_w: float = 19.0
    plate_t: float = 1.0
    pocket_clearance: float = 0.2
    pocket_offset_y: float = 0.0
    min_floor: float = 1.2

    # --- Fit coupon ---
    coupon_thickness: float = 1.6
    coupon_margin: float = 3.0

    # ---------- derived values ----------
    @property
    def tilt_sign(self) -> int:
        """+1 rotates the bottom edge towards the wall."""
        if self.on_side not in ("top", "bottom"):
            raise ValueError(f"on_side must be 'top' or 'bottom', got {self.on_side!r}")
        return 1 if self.on_side == "bottom" else -1

    @property
    def off_stop_len(self) -> float:
        """OFF-side pin length so it already touches the base in the ON position.

        With the pivot behind the back face, a pin tip at y=p swings by
        p*sin(tilt) each way; equating the base contact in OFF (original pin)
        and ON (long pin) gives L_off = L + 2*p*tan(tilt).
        """
        return self.stop_len + self.stop_pitch * tan(radians(self.on_tilt_deg))

    @property
    def cap_width(self) -> float:
        return self.frame_size + 2 * (self.shroud_clearance + self.shroud_wall)

    @property
    def cap_height(self) -> float:
        return self.cap_width

    @property
    def shroud_depth(self) -> float:
        """Shroud length behind the cap's back face: past the frame, short of the wall."""
        return self.cap_gap + self.frame_depth - self.wall_gap

    @property
    def cap_back_z(self) -> float:
        """Wall-frame Z of the cap's back face."""
        return self.orig_face_thickness + self.rim_offset + self.cap_gap

    @property
    def pocket_depth(self) -> float:
        return self.plate_t  # plate sits flush with the front

    @property
    def pocket_floor(self) -> float:
        return self.cap_thickness - self.pocket_depth

    def with_overrides(self, **kw) -> "TangentParams":
        return replace(self, **kw)
