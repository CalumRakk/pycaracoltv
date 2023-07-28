#
import m3u8
import threading
from typing import List

from .utils import ejecutar_tarea, get_master


def get_resolutions(master_m3u8):
    """Devuelve las resoluciones disponibles."""
    resolutions = []
    for playlist in master_m3u8.playlists:
        resolutions.append(playlist.stream_info.resolution[0])
    return resolutions


def check_resolutions(master_m3u8, resolutions: List[int]):
    """Comprueba que las resoluciones dada por el usuario existan.

    Args:
        master_m3u8 (M3U8): master contiene la lista de playlist de las diferentes resoluciones
        resolutions (List[int]): resoluciones dada por el usuario como enteros.
    """
    resolutions_not_encontradas = []
    for resolution in resolutions:
        exists_resolution = False

        for playlist in master_m3u8.playlists:
            if resolution in playlist.stream_info.resolution:
                exists_resolution = True
                break
        if not exists_resolution:
            resolutions_not_encontradas.append(resolution)

    if resolutions_not_encontradas:
        print(f"No se encontró la resolución dada por el usuario")
        for resolution in resolutions_not_encontradas:            
            print(resolution)

        print("Estas son las resolutiones disponibles:")
        for resolution in get_resolutions(master_m3u8):
            print(resolution)
        exit()


def run(folder, resolutions):
    master = get_master()
    check_resolutions(master, resolutions)
    segments_descargados = []
    hilos = []
    for resolution in resolutions:
        hilo = threading.Thread(
            target=ejecutar_tarea,
            args=(
                folder,
                master,
                resolution,
                segments_descargados,
            ),
        )
        hilos.append(hilo)

    for hilo in hilos:
        hilo.start()


if __name__ == "__main__":
    run(resolutions)
