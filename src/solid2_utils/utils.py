from typing import Iterable, Tuple, List, Optional
from solid2 import cube, P3
from solid2.core.object_base import OpenSCADObject
from pathlib import Path
import subprocess

StlTask = Tuple[Tuple[OpenSCADObject, P3], str]


def _render_to_stl_file(root: OpenSCADObject, filename: str, verbose: bool = False) -> str:
    if verbose:
        scad_file = Path(filename).with_suffix(".scad")
        root.save_as_scad(scad_file.absolute().as_posix())
        args = ["openscad", "-o", filename, scad_file]
        subprocess.check_output(args)
        return Path(filename).absolute().as_posix()
    else:
        return root.save_as_stl(filename)


def _stl_task_function(stl_task: Tuple[OpenSCADObject, str, bool]) -> str:
    (obj, filename, verbose) = stl_task
    return _render_to_stl_file(obj, filename, verbose)


def save_to_str_scad(output_scad_basename: str, output_stl_basename: str | None, output: Iterable[StlTask],
                     verbose: bool = False) -> None:
    if verbose:
        from multiprocessing.dummy import Pool
    else:
        from multiprocessing import Pool

    stl_task: List[Tuple[OpenSCADObject, str, bool]] = []
    all_obj: Optional[OpenSCADObject] = None
    next_pos = [0, 0]
    for obj_and_dim, filename_prefix in output:
        obj, dim = obj_and_dim
        filename = output_scad_basename + filename_prefix + ".scad"
        stl_task.append((obj, output_scad_basename + filename_prefix + ".stl", verbose))
        obj.save_as_scad(filename)
        if all_obj is None:
            all_obj = obj.left(next_pos[0]).fwd(next_pos[1])
        else:
            all_obj += obj.left(next_pos[0]).fwd(next_pos[1])
        next_pos = (next_pos[0] - (dim[0] * 1.05), next_pos[1] - (dim[1] * 1.05))

    filename = output_scad_basename + f"{Path(__file__).stem}_all.scad"
    all_obj.save_as_scad(filename)
    stl_task.append((all_obj, output_scad_basename + f"{Path(__file__).stem}_all.stl", verbose))
    if output_stl_basename is not None:
        with Pool() as pool:
            pool.map(_stl_task_function, stl_task)
