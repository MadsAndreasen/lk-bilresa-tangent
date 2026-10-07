"""Geometry for the locked-ON tangent. See params.py for the coordinate frames."""

from math import radians, sin

from build123d import (
    Align,
    Axis,
    Box,
    Cone,
    Cylinder,
    Location,
    GridLocations,
    Part,
    Plane,
    Pos,
    Rot,
    SlotOverall,
    extrude,
    fillet,
)

from .params import TangentParams

DOWN = (Align.CENTER, Align.CENTER, Align.MAX)  # solid hangs below z=0
UP = (Align.CENTER, Align.CENTER, Align.MIN)  # solid sits on z=0


def snap_boss(p: TangentParams) -> Part:
    """One slotted split tube with a snap bead, hanging from z=0."""
    r = (p.boss_od + p.fit_clearance) / 2
    tube = Cylinder(r, p.boss_height, align=DOWN) - Cylinder(p.boss_id / 2, p.boss_height, align=DOWN)
    # Lead-in cone: narrow at the tip, widening to the bead behind it.
    bead_base = -p.boss_height + p.boss_lip_h
    bead = Pos(0, 0, bead_base) * Cone(r, r + p.boss_lip, p.boss_lip_h, align=DOWN)
    bead -= Pos(0, 0, bead_base) * Cylinder(p.boss_id / 2, p.boss_lip_h, align=DOWN)
    slot_depth = p.boss_height * 0.7
    slot = Pos(0, 0, -p.boss_height) * Box(p.boss_slot_w, 2 * (r + p.boss_lip) + 1, slot_depth, align=UP)
    return tube + bead - slot


def bosses(p: TangentParams) -> Part:
    boss = snap_boss(p)
    return Part() + [loc * boss for loc in GridLocations(p.boss_pitch_x, p.boss_pitch_y, 2, 2)]


def stops(p: TangentParams) -> Part:
    """ON-side pin at the original length; OFF-side pin lengthened to block OFF."""
    y_off = p.tilt_sign * p.stop_pitch / 2  # ON=bottom pressed in -> OFF stop is the top pin
    on_pin = Pos(0, -y_off, 0) * Cylinder(p.stop_d / 2, p.stop_len, align=DOWN)
    off_pin = Pos(0, y_off, 0) * Cylinder(p.stop_d / 2, p.off_stop_len, align=DOWN)
    return on_pin + off_pin


def skirt(p: TangentParams) -> Part:
    outer = Box(p.width, p.height, p.skirt_depth, align=DOWN)
    inner = Box(p.width - 2 * p.skirt_wall, p.height - 2 * p.skirt_wall, p.skirt_depth, align=DOWN)
    ring = outer - inner
    notch_z = -p.skirt_depth
    for sx in (-1, 1):
        x = sx * (p.width - p.skirt_wall) / 2
        ring -= Pos(x, 0, notch_z) * Box(p.skirt_wall + 0.2, p.side_notch_h, p.side_notch_depth, align=UP)
    return ring


def tilt(p: TangentParams) -> Location:
    """Carrier frame -> wall frame: rotate into ON about the pivot axis."""
    d = p.pivot_depth
    return Pos(0, 0, -d) * Rot(X=p.tilt_sign * p.on_tilt_deg) * Pos(0, 0, d)


def carrier_part(p: TangentParams) -> Part:
    """Everything attached to the rocker, in the wall frame, clipped at the cap's back face."""
    # Solid neck tall enough that, once tilted, it reaches the cap everywhere.
    neck_h = p.cap_back_z + p.height / 2 * sin(radians(p.on_tilt_deg)) + 1.0
    neck = Box(p.width, p.height, neck_h, align=UP)
    part = tilt(p) * (neck + skirt(p) + bosses(p) + stops(p))
    big = 4 * max(p.cap_width, p.cap_height, p.off_stop_len + p.pivot_depth)
    keep = Pos(0, 0, p.cap_back_z) * Box(big, big, big, align=DOWN)
    return part & keep


def cap(p: TangentParams) -> Part:
    c = Pos(0, 0, p.cap_back_z) * Box(p.cap_width, p.cap_height, p.cap_thickness, align=UP)
    return fillet(c.edges().filter_by(Axis.Z), p.cap_edge_radius)


def shroud(p: TangentParams) -> Part:
    """Perimeter wall behind the cap that fits over the switch frame."""
    inner = p.frame_size + 2 * p.shroud_clearance
    outer = Box(p.cap_width, p.cap_height, p.shroud_depth, align=DOWN)
    ring = fillet(outer.edges().filter_by(Axis.Z), p.cap_edge_radius) - Box(inner, inner, p.shroud_depth, align=DOWN)
    return Pos(0, 0, p.cap_back_z) * ring


def magnet_pocket(p: TangentParams) -> Part:
    front = Plane.XY.offset(p.cap_back_z + p.cap_thickness)
    outline = front * Pos(0, p.pocket_offset_y) * SlotOverall(
        p.plate_l + p.pocket_clearance, p.plate_w + p.pocket_clearance, rotation=90
    )
    return extrude(outline, amount=-p.pocket_depth)


def build(p: TangentParams = TangentParams()) -> Part:
    """Finished tangent in the installed (wall) frame."""
    return carrier_part(p) + cap(p) + shroud(p) - magnet_pocket(p)


def fit_coupon(p: TangentParams = TangentParams()) -> Part:
    """Thin plate with only bosses and stops, in the carrier frame, for a quick fit print."""
    w = p.boss_pitch_x + p.boss_od + 2 * p.coupon_margin
    h = p.stop_pitch + p.stop_d + 2 * p.coupon_margin
    plate = Box(w, h, p.coupon_thickness, align=UP)
    return plate + bosses(p) + stops(p)


def print_orientation(part: Part) -> Part:
    """Flip front-face-down and drop onto z=0."""
    flipped = Rot(X=180) * part
    return Pos(0, 0, -flipped.bounding_box().min.Z) * flipped
