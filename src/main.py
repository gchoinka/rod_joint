import os
import shutil
import sys
from typing import Iterable, Tuple, Dict, List

from solid2 import cube, linear_extrude, polygon, cylinder, hull, scale, intersection, union, P3
from solid2.core.object_base import OpenSCADObject
from solid2_utils.utils import save_to_str_scad, StlTask
from solid2.extensions.bosl2.threading import buttress_threaded_rod
from solid2.extensions.bosl2.screw_drive import torx_mask2d, torx_mask

verbose = True
unprintable_thickness = 0.01
preview_fix = 0.05
pipe_r = 8 / 2
bold_d = 15
pitch = 2

15+4+15+4+20+5+5+20+5+5
def middle_bolt() -> List[Tuple[Tuple[OpenSCADObject, P3], str]]:
    bolt_l = 120
    nut_l = 15
    bolt = buttress_threaded_rod(d=bold_d, l=bolt_l, pitch=2, _fa=1, _fs=0.5, internal=False).up(bolt_l / 2)
    bolt -= cylinder(r=3.5/2, h=bolt_l+2*preview_fix, center=True,_fn=30).up(bolt_l / 2)
    flat_face_box = cube([0.75 * bold_d, bold_d, bolt_l], center=True).up(bolt_l / 2)

    floated_bolt = intersection()(bolt, flat_face_box)

    inside_thread = buttress_threaded_rod(d=bold_d, l=nut_l + preview_fix * 3, pitch=2, _fa=1, _fs=0.5, internal=True,
                                          _slop=0.3).rotate([180, 0, 0]).up(nut_l / 2 - preview_fix)
    top_chamfer_h = 3
    torx_mask_base = torx_mask2d(size=60, _fa=1, _fs=1)
    torx_nut = scale([2, 2, 1])(
        linear_extrude(height=nut_l - top_chamfer_h, center=False, scale=1.17)(torx_mask_base))
    torx_nut += scale([2.34, 2.34, 1])(
        linear_extrude(height=top_chamfer_h / 2, center=False, scale=0.9625)(torx_mask_base)).up(
        nut_l - top_chamfer_h + top_chamfer_h / 2 * 0)
    torx_nut += scale([2.25, 2.25, 1])(
        linear_extrude(height=top_chamfer_h / 2, center=False, scale=0.8)(torx_mask_base)).up(
        nut_l - top_chamfer_h + top_chamfer_h / 2 * 1)
    torx_nut += cylinder(r1=bold_d / 2 * 1.8, r2=bold_d / 2, h=5).up(2)
    torx_nut += cylinder(r=bold_d / 2 * 1.8, h=2)

    nut = torx_nut - inside_thread

    return [((floated_bolt, (bold_d, bold_d, bolt_l)), "middle_bolt"),
            ((nut, (bold_d, bold_d, bolt_l)), "nut01"),

            ]


# def middle_end_nut() -> Tuple[OpenSCADObject, P3]:
#     l = 10
#     nut = union()(buttress_threaded_nut(nutwidth=d * 2, id=d, l=l, pitch=1.5, _fa=1, _fs=0.5))
#     # nut = intersection()(nut.up(l / 2), cube([0.75 * d, d, l], center=True).up(l / 2))
#     return nut.rotate([0, 180, 0]).up(l / 2), (30, 30, l)


def main(output_scad_basename, output_stl_basename):
    output: List[StlTask] = [
        *middle_bolt(),
        # (middle_end_nut(), "middle_end_nut")
    ]
    save_to_str_scad(output_scad_basename, output_stl_basename, output, verbose)


if __name__ == "__main__":
    skip_stl: bool = True if len(sys.argv) > 1 and sys.argv[1] == "--fast" else False
    build_path: str = os.path.dirname(os.path.realpath(__file__))
    output_path: str = os.path.abspath(os.path.join(build_path, '..', 'build')) + os.path.sep
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    stl_output_path: str | None = output_path
    if shutil.which("openscad") is None or skip_stl:
        stl_output_path = None
    main(output_scad_basename=output_path, output_stl_basename=stl_output_path)
