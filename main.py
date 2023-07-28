
import caracoltv
import m3u8
from m3u8 import M3U8
import requests
from typing import Union, List, Tuple
import threading
import re
import time
import os
from datetime import datetime, timedelta
from pathlib import Path

url = "https://mdstrm.com/live-stream-playlist/574463697b9817cf0886fc17.m3u8"

session = requests.Session()

response = session.get(url, headers=caracoltv.HEADERS)
master_m3u8 = m3u8.loads(response.text)

resolutions= [playlist_m3u8.stream_info.resolution for playlist_m3u8 in master_m3u8.playlists]
def congelar(segundos):
    inicio = datetime.now()
    fin = inicio + timedelta(seconds=segundos)
    while datetime.now() < fin:
        segundos_faltantes = int((fin - datetime.now()).total_seconds())
        print(segundos_faltantes, end='\r')
        time.sleep(1)

def get_playlist(master_m3u8:M3U8, resolution:Union[int, Tuple[int]]):
    """Devuelve una playlist de master con la resolución especificada, si no existe devuelve la última resolutión."""
    for playlist_m3u8 in master_m3u8.playlists:
        if type(resolution) is tuple and resolution == playlist_m3u8.stream_info.resolution:
            return playlist_m3u8
        elif type(resolution) is int and resolution in playlist_m3u8.stream_info.resolution:
            return playlist_m3u8
    return master_m3u8.playlists[-1]
def get_filename(url):
    regex= re.compile("media_.*?.ts")
    return regex.search(url).group()

def ejecutar_tarea(master_m3u8, resolution, segments_descargados:list):            
    while True:
        playlist_m3u8 = get_playlist(master_m3u8, resolution)
        response = session.get(playlist_m3u8.uri, headers=caracoltv.HEADERS)  # m3u8 media playlist
        try:
            m3u8_playlist = m3u8.loads(response.text)
            for segment in m3u8_playlist.segments:
                filename= get_filename(segment.uri)
                
                if filename in segments_descargados:
                    continue

                response= session.get(segment.uri, headers=caracoltv.HEADERS)  
                path= Path("segments").joinpath(str(resolution)+"p", filename)             
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_bytes(response.content)
                segments_descargados.append(filename)
                print(path)
        except:
            pass       
        congelar(30)

segments_descargados=[]
hilos=[]
for resolution in [480, 1080]:
    hilo = threading.Thread(target=ejecutar_tarea, args=(master_m3u8, resolution, segments_descargados,))
    hilos.append(hilo)

for hilo in hilos:
    hilo.start()