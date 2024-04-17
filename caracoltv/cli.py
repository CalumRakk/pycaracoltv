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
        help="ruta de la carpeta donde se guardarán los segmentos",
    )
    parser.add_argument("-r", "--resolutions",help="Una lista de resoluciones como numeros enteros", nargs="*", type=check_type_resolution)

    args = parser.parse_args()

    run(folder=args.folder, resolutions=args.resolutions)
