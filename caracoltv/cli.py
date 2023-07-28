#
from typing import List
import argparse
import os
from caracoltv.utils import check_type_resolution
from caracoltv.script import run


def run_script():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "folder",
        type=str,
        help="ruta de la carpeta donde se encuentra guardar los archivos",
    )
    parser.add_argument("-r", "--resolutions", nargs="*", type=check_type_resolution)

    args = parser.parse_args()

    run(folder=args.folder, resolutions=args.resolutions)
