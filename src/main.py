import os
import shutil
import sys
from typing import Iterable, Tuple, Dict, List

from solid2 import cube, linear_extrude, polygon, cylinder, hull, scale, intersection, P3
from solid2.core.object_base import OpenSCADObject
from solid2_utils.utils import save_to_str_scad, StlTask

verbose = False
unprintable_thickness = 0.01
preview_fix = 0.05

pipe_r = 8 / 2


def cube_example() -> Tuple[OpenSCADObject, P3]:
    return cube(1), (0, 0, 0)


def main(output_scad_basename, output_stl_basename):
    output: List[StlTask] = [
        (cube_example(), "cube_example"),
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
