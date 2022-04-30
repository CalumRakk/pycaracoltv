import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import m3u8
from m3u8 import M3U8
import re

from typing import List
import time
import os
import sys
get_filename = re.compile("media_.*?.ts")

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

if not os.path.exists(SEGMENT_FOLDER):
    os.makedirs(SEGMENT_FOLDER)

def get_schedule_day()->List[dict]:
    """
    Devuelve la programacion del día actual, como una lista de diccionarios.
    """
    response = requests.get(
        "https://www.caracoltv.com/programacion", headers=HEADERS)

    # Captura la programación del día
    soup = BeautifulSoup(response.text, 'html.parser')
    schedule_day = []
    for tr in soup.find('tbody').find_all("tr"):
        programa, time = tr.find("a").get("title").split("-", 1)

        document = {
            "title": programa.strip(),
            "time": time.strip(),
        }
        schedule_day.append(document)
    return schedule_day

def select_tvshow(programacion: List[dict]) -> dict:
    """
    Devuelve el tiempo de esperar para capturar el programa
    """
    if sys.platform.startswith('linux'):
        os.system("clear")
    else:
        os.system("cls")
        
    print("Seleccione el programa que desea capturar:")
    for index, programa in enumerate(programacion):
        index += 1
        print(index, programa["title"], programa["time"])

    user_input = int(input("\n>>>"))
    index = user_input-1
    title = programacion[index]["title"]
    time = programacion[index]["time"]

    start, end = time.split("-")
    document = {
        "title": title,
        "time": time,
        "start": start,
        "end": end,
    }
    return document

def waiting(programa: dict) -> None:
    """
    Espera hasta que el programa empiece
    """
    start = datetime.strptime(programa["start"], '%I:%M%p')

    difference = start-datetime.now()
    if difference.days == 0:
        print("El programa inicia a las:", start.strftime("%I:%M%p"))
        time.sleep(difference.seconds+2)

def get_resolutions_available(m3u8_media: M3U8) -> list:
    resolutions = []
    for playlist in m3u8_media.playlists:
        resolutions.append(playlist.stream_info.resolution[1])
    return resolutions


def select_resolution(resolutions: list) -> int:
    print("Seleccione la resolución:")
    for index, resolution in enumerate(resolutions):
        index += 1
        print(index, resolution)

    user_input = int(input("\n>>>"))
    index = user_input-1
    return resolutions[index]


def get_url_of_segments():
    """
    Devuelve la URL de la transmisión en vivo. Es una URL que contiene las URLs de los segmentos.
    """
    url = "https://mdstrm.com/live-stream-playlist/574463697b9817cf0886fc17.m3u8"
    # m3u8 master playlist
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        m3u8_media = m3u8.loads(response.text)

        resolutions = get_resolutions_available(m3u8_media)
        resolution = select_resolution(resolutions)

        for playlist in m3u8_media.playlists:
            if playlist.stream_info.resolution[1] == resolution:
                url = playlist.uri
                return url, resolution

    print("respuesta del servidor:", "\n", response.text, "\n")
    print("La señal en vivo solo está disponible para IP colombianas.")
    exit()


def download_playlist(url: str, folder) -> None:
    """
    Entra a un Bucle y hace una solicitud a la URL de la playlist de segmentos (cada 75 segundos) y descarga los segmentos.
    url: es una URL que contiene las URLs de los segmentos. 
    folder: es el path (folder) donde se guardarán los segmentos.
    """
    response = requests.get(url, headers=HEADERS)  # m3u8 media playlist

    m3u8_media = m3u8.loads(response.text)

    for segment in m3u8_media.segments:
        url = segment.uri

        filename = get_filename.search(url).group()
        path = os.path.join(folder, filename)
        if not os.path.isfile(path):
            with open(path, 'wb') as f:
                f.write(requests.get(segment.uri, headers=HEADERS).content)

    time.sleep(75)


def capture(tvshow: dict):
    """
    Captura la transmision en vivo  

    tvshow: Diccionario que contiene nombre, hora de inicio y fin del programa    
    return: devuelve la carpeta donde se guardaron los segmentos
    """
    url, resolution = get_url_of_segments()

    waiting(tvshow)

    title = tvshow["title"]
    day = datetime.now().strftime("%d-%m-%y")
    end = datetime.now().strptime(tvshow["end"], '%I:%M%p')
    start = datetime.now()

    folder = f"{title} {str(resolution)}_{day}_{start.strftime('%I%M%p')}-{end.strftime('%I%M%p')}+10min"

    path = os.path.join(SEGMENT_FOLDER, folder)
    if not os.path.exists(path):
        os.makedirs(path)

    while datetime.now() < end or (end < datetime.now()):
        download_playlist(url, path)

    return folder


def concatenate_segments(folder) -> None:
    """
    Concatena todos los segmentos que encuentre en folder, en un archivo .ts
    folder: la carpeta donde estan los segmentos para ser concatenados.
    """
    filename = folder+EXT_TS
    path = os.path.join(os.getcwd(), filename)
    with open(path, 'wb') as file:
        for string in os.listdir(folder):
            path = f"{folder}/{string}"
            with open(path, 'br') as video:
                file.write(video.read())
