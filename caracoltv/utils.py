import threading
import re
import time
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Union, List, Tuple
import json
import m3u8
from m3u8 import M3U8
import requests

from .constants import HEADERS, HOST


session = requests.Session()


def congelar(segundos):
    inicio = datetime.now()
    fin = inicio + timedelta(seconds=segundos)
    while datetime.now() < fin:
        segundos_faltantes = int((fin - datetime.now()).total_seconds())
        print(segundos_faltantes, end="\r")
        time.sleep(1)


def get_playlist(master_m3u8: M3U8, resolution: Union[int, Tuple[int]]):
    """Devuelve una playlist de master con la resolución especificada, si no existe devuelve la última resolutión."""
    for playlist_m3u8 in master_m3u8.playlists:
        if (
            type(resolution) is tuple
            and resolution == playlist_m3u8.stream_info.resolution
        ):
            return playlist_m3u8
        elif (
            type(resolution) is int
            and resolution in playlist_m3u8.stream_info.resolution
        ):
            return playlist_m3u8
    return master_m3u8.playlists[-1]


def get_filename(url):
    regex = re.compile("media_.*?.ts")
    return regex.search(url).group()


def ejecutar_tarea(folder, master_m3u8, resolution, segments_descargados: list):
    while True:
        playlist_m3u8 = get_playlist(master_m3u8, resolution)
        response = session.get(playlist_m3u8.uri, headers=HEADERS)
        try:
            m3u8_playlist = m3u8.loads(response.text)
            for segment in m3u8_playlist.segments:
                filename = get_filename(segment.uri)

                if filename in segments_descargados:
                    continue

                response = session.get(segment.uri, headers=HEADERS)
                path = Path(folder).joinpath(str(resolution) + "p", filename)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(response.content)
                segments_descargados.append(filename)
                print(path)
        except:
            pass
        congelar(30)


def get_master() -> M3U8:
    # proxies = {
    #     "http": "200.25.254.193:54240",
    #     "https": "200.25.254.193:54240",
    # }

    response = session.get(HOST, headers=HEADERS)
    try:
        print(json.loads(response.text))
        exit()
    except json.decoder.JSONDecodeError:
        master_m3u8 = m3u8.loads(response.text)
    return master_m3u8


def check_type_resolution(resolution: List[int]):
    try:
        resolution = int(resolution)
        return resolution
    except Exception as e:
        raise TypeError(e)


def get_resolutions(master_m3u8):
    """Devuelve las resoluciones disponibles."""
    resolutions = []
    for playlist in master_m3u8.playlists:
        resolutions.append(playlist.stream_info.resolution[1])
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


def get_available_qualities(master: M3U8) -> list[int]:
    """Devuelve las calidades disponibles."""
    resolutions = []
    for playlist in master.playlists:
        resolutions.append(playlist.stream_info.resolution[1])
    return resolutions


def get_playlist(master: M3U8, quality: int) -> M3U8:
    """Devuelve una playlist con la calidad de video especifico.
    Una playlist es un m3u8 que contiene una lista de segmentos.
    """
    for playlist in master.playlists:
        if playlist.stream_info.resolution[1] == quality:
            response = session.get(playlist.uri, headers={})
            playlist = m3u8.loads(response.text)
            return playlist

    qualities = get_available_qualities(master)
    print(f"\nLa calidad {quality} no existe. Las disponibles son: ")
    for quality in qualities:
        print("\t", quality)
