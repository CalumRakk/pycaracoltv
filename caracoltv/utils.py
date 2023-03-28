from typing import List, TYPE_CHECKING
import time
import os
import sys
from datetime import datetime, timedelta
import re

import requests
from requests.exceptions import ConnectionError
import lxml.html
import m3u8
from m3u8 import M3U8
if TYPE_CHECKING:
    from .tvshow import TvShow

get_filename = re.compile("media_.*?.ts")

WORKTABLE = r"D:\.TEMP\caracoltv"
SEGMENT_FOLDER = "segments"
EXT_TS = ".ts"

HEADERS = {
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Sec-Fetch-Site': 'cross-site',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Dest': 'iframe',
}

session = requests.Session()

if not os.path.exists(SEGMENT_FOLDER):
    os.makedirs(SEGMENT_FOLDER)


def congelar(segundos):
    inicio = datetime.now()
    fin = inicio + timedelta(seconds=segundos)
    while datetime.now() < fin:
        segundos_faltantes = int((fin - datetime.now()).total_seconds())
        print(segundos_faltantes, end='\r')
        time.sleep(1)

def get_schedule_day()->List[dict]:
    """
    Devuelve la programacion del día actual, como una lista de TvShow.
    """
    from .tvshow import TvShow
    response = session.get(
        "https://www.caracoltv.com/programacion", headers=HEADERS)

    root = lxml.html.fromstring(response.text)
    schedule_day = []
    for tr in root.xpath('//table[@class="ScheduleDay-table"]')[0].xpath(".//tbody/tr"):
        td_time, td_programa,  = tr.xpath('.//td')[:2]

        if len(td_programa.xpath(".//a"))>1:
            title= td_programa.xpath(".//a")[1].text
        else:
            title= td_programa.xpath(".//a")[0].text
        time_string= td_time.text
        tvshow= TvShow(title=title, source_time=time_string)
        schedule_day.append(tvshow)
    return schedule_day

def select_tvshow(schedules:List['TvShow']):
    if sys.platform.startswith('linux'):
        os.system("clear")
    else:
        os.system("cls")
        
    print("Seleccione el programa que desea capturar:")
    for index, programa in enumerate(schedules, start=1):
        print(index, programa)

    user_input = int(input("\n>>>"))
    index = user_input-1
    return schedules[index]

def select_resolution() -> int:
    def get_resolutions_available(m3u8_media: M3U8) -> List[int]:
        """
        Itera sobre un objeto m3u8 (master) para obtener las resoluciones disponibles y devolverla como una lista de enteros.
        """
        resolutions = []
        for playlist in m3u8_media.playlists:
            resolutions.append(playlist.stream_info.resolution[1])
        return resolutions
    
    url = "https://mdstrm.com/live-stream-playlist/574463697b9817cf0886fc17.m3u8"
    response = session.get(url, headers=HEADERS)
    m3u8_media = m3u8.loads(response.text)

    print("Seleccione la resolución:")
    resolutions= get_resolutions_available(m3u8_media)
    for index, resolution in enumerate(resolutions):
        index += 1
        print(index, resolution)

    user_input = int(input("\n>>>"))
    index = user_input-1
    print(":", resolutions[index], "\n")
    return resolutions[index]


def download_playlist(url: str, folder) -> None:
    """
    Hace una solicitud a la URL de la playlist de segmentos y descarga los segmentos devueltos.
    url: es una URL que contiene las URLs de los segmentos. 
    folder: es el path (folder) donde se guardarán los segmentos.
    """
    while True:
        try:
            response = requests.get(url, headers=HEADERS)  # m3u8 media playlist

            m3u8_media = m3u8.loads(response.text)

            for segment in m3u8_media.segments:
                url = segment.uri

                filename = get_filename.search(url).group()
                path = os.path.join(folder, filename)
                if not os.path.isfile(path):
                    with open(path, 'wb') as f:
                        f.write(requests.get(segment.uri, headers=HEADERS).content)
            break
        except ConnectionError:
            print("\n\n No se pudo conectar al servidor.")
            continue

def capture(tvshow, quality):
    """
    Captura la transmision en vivo
    """
    from .folder import Folder
    
    title= tvshow.title.replace(" ","_")
    time_= tvshow.source_time.replace(" ","").replace(":",".")
    dirname= f"{title}_{quality}p_{datetime.now().strftime('%d-%m-%y')}_{time_}"
    folder = Folder(os.path.join(WORKTABLE, dirname))

    url = "https://mdstrm.com/live-stream-playlist/574463697b9817cf0886fc17.m3u8"

    response = session.get(url, headers=HEADERS)
    m3u8_media = m3u8.loads(response.text)
    for playlist in m3u8_media.playlists:
        if playlist.stream_info.resolution[1] == quality:
            url_playlist = playlist.uri
            break

    while True:
        response = session.get(url_playlist, headers=HEADERS)  # m3u8 media playlist
        try:
            m3u8_playlist = m3u8.loads(response.text)
            for segment in m3u8_playlist.segments:
                if not folder.segments.exists(segment):
                    segment_dict= folder.segments.add(segment)
                    print(segment_dict["filename"])

            folder.segments.save()
        except ValueError:
            # Error 1
            pass       
        congelar(30)

def concatenate_segments(folder) -> None:
    """
    Concatena todos los segmentos que encuentre en folder en un archivo .ts
    folder: la carpeta donde estan los segmentos para ser concatenados.
    """
    filename = folder+EXT_TS
    path = os.path.join(os.getcwd(), filename)
    with open(path, 'wb') as file:
        for string in os.listdir(folder):
            path = f"{folder}/{string}"
            with open(path, 'br') as video:
                file.write(video.read())
