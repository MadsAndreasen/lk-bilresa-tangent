import pytest

from lk_bilresa.params import TangentParams
from lk_bilresa.tangent import build, cap, carrier_part, fit_coupon, magnet_pocket, print_orientation, shroud, stops, tilt

P = TangentParams()


@pytest.fixture(scope="module")
def tangent():
    return build(P)


def test_single_valid_solid(tangent):
    assert tangent.is_valid
    assert len(tangent.solids()) == 1


def test_cap_footprint(tangent):
    size = tangent.bounding_box().size
    assert size.X == pytest.approx(P.cap_width, abs=0.01)
    assert size.Y == pytest.approx(P.cap_height, abs=0.01)


def test_front_is_flat_and_wall_parallel(tangent):
    assert tangent.bounding_box().max.Z == pytest.approx(P.cap_back_z + P.cap_thickness, abs=1e-6)


def test_pocket_floor_and_end_walls():
    assert P.pocket_floor >= P.min_floor
    end_wall = (P.cap_height - P.plate_l - P.pocket_clearance) / 2 - abs(P.pocket_offset_y)
    assert end_wall >= 1.5


def test_pocket_is_cut(tangent):
    uncut = carrier_part(P) + cap(P) + shroud(P)
    assert uncut.volume - tangent.volume == pytest.approx(magnet_pocket(P).volume, rel=1e-3)


def test_shroud_covers_frame_and_clears_wall():
    bb = shroud(P).bounding_box()
    rim_front = P.cap_back_z - P.cap_gap
    wall_z = rim_front - P.frame_depth
    assert P.cap_width - 2 * P.shroud_wall > P.frame_size
    assert bb.min.Z < rim_front  # reaches past the frame rim
    assert bb.min.Z == pytest.approx(wall_z + P.wall_gap, abs=1e-6)


def test_off_stop_longer_than_on_stop():
    assert P.off_stop_len > P.stop_len


@pytest.mark.parametrize("side", ["top", "bottom"])
def test_both_stops_touch_base_in_on(side):
    """Locked: in the ON tilt both pin tips reach the same base plane."""
    p = P.with_overrides(on_side=side)
    tips = [s.bounding_box().min.Z for s in (tilt(p) * stops(p)).solids()]
    assert tips[0] == pytest.approx(tips[1], abs=0.02)


def test_bosses_inside_skirt():
    inner_half_w = P.width / 2 - P.skirt_wall
    inner_half_h = P.height / 2 - P.skirt_wall
    r = (P.boss_od + P.fit_clearance) / 2 + P.boss_lip
    assert P.boss_pitch_x / 2 + r < inner_half_w
    assert P.boss_pitch_y / 2 + r < inner_half_h
    assert P.stop_pitch / 2 + P.stop_d / 2 < inner_half_h


def test_coupon_and_print_orientation():
    coupon = fit_coupon(P)
    assert coupon.is_valid and len(coupon.solids()) == 1
    assert print_orientation(coupon).bounding_box().min.Z == pytest.approx(0, abs=1e-6)
