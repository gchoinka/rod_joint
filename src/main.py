import math  # noqa
import multiprocessing
import os
import shutil
import sys

from solid2 import *

view_helper = 0.05


def cube_example():
    return cube()


def task(stl_task):
    obj, filename = stl_task
    obj.save_as_stl(filename)


def main(output_scad_basename, output_stl_basename):
    output = [
        (cube_example(), "cube_example"),
    ]

    stl_task = []
    all_obj = None
    obj_distance = 25
    next_pos = [obj_distance, obj_distance]

    for obj, filename_prefix in output:
        filename = output_scad_basename + filename_prefix + ".scad"
        stl_task.append((obj, output_scad_basename + filename_prefix + ".stl"))
        obj.save_as_scad(filename)
        if all_obj is None:
            all_obj = obj
        else:
            all_obj += obj.left(next_pos[0]).fwd(next_pos[1])
            next_pos[0] += obj_distance
            next_pos[1] += obj_distance

    filename = output_scad_basename + "all.scad"
    all_obj.save_as_scad(filename)
    stl_task.append((all_obj, output_scad_basename + "all.stl"))
    if output_stl_basename is not None:
        with multiprocessing.Pool() as pool:
            pool.map(task, stl_task)


if __name__ == "__main__":
    skip_stl = True if len(sys.argv) > 1 and sys.argv[1] == "--fast" else False
    build_path = os.path.dirname(os.path.realpath(__file__))
    output_path = os.path.abspath(os.path.join(build_path, '..', 'build')) + os.path.sep
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    stl_output_path = output_path
    if shutil.which("openscad") is None or skip_stl:
        stl_output_path = None
    main(output_scad_basename=output_path, output_stl_basename=stl_output_path)
