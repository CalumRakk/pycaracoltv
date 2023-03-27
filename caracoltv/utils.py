import requests
from datetime import datetime, timedelta
import m3u8
from m3u8 import M3U8
import re
from requests.exceptions import ConnectionError

from typing import List
import time
import os
import sys
import lxml.html

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

session = requests.Session()

if not os.path.exists(SEGMENT_FOLDER):
    os.makedirs(SEGMENT_FOLDER)

class TvShow:
    def __init__(self, title, source_time) -> None:
        self.title= title or ""
        self.source_time= source_time        
        self.start_time= source_time.split(" - ")[0]
        self.end_time= source_time.split(" - ")[1]       

    def get_start_time(self):
        now_string= datetime.now().strftime('%d-%m-%y')
        return datetime.strptime(f"{now_string} {self.start_time}", "%d-%m-%y %I:%M %p")
    def get_end_time(self):
        now_string= datetime.now().strftime('%d-%m-%y')
        return datetime.strptime(f"{now_string} {self.end_time}", "%d-%m-%y %I:%M %p")
    
    def __str__(self) -> str:
        return self.title + " - " + datetime.now().strftime('%d-%m-%y ') + self.source_time
    
    def dirname(self):
        title= self.title.replace(" ","_")
        time_= self.source_time.replace(" ","").replace(":",".")
        return f"{self.title}_{datetime.now().strftime('%d-%m-%y')}_{time_}"

def get_schedule_day()->List[dict]:
    """
    Devuelve la programacion del día actual, como una lista de TvShow.
    """
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

def select_tvshow(schedules: List[TvShow]) -> dict:
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

def waiting(programa: dict) -> None:
    """
    Congela el script hasta que el programa empiece
    """
    
    day= datetime.now().day
    moth= datetime.now().month
    year= datetime.now().year
    start= datetime.strptime(f'{day}-{moth}-{year} {programa["start"]}', '%d-%m-%Y %I:%M%p')

    difference = start-datetime.now()
    if difference.days == 0:
        print("El programa inicia a las:", start.strftime("%I:%M%p"))
        time.sleep(difference.seconds+2)

def get_resolutions_available(m3u8_media: M3U8) -> List[int]:
    """
    Itera sobre un objeto m3u8 (master) para obtener las resoluciones disponibles y devolverla como una lista de enteros.
    """
    resolutions = []
    for playlist in m3u8_media.playlists:
        resolutions.append(playlist.stream_info.resolution[1])
    return resolutions


def select_resolution(resolutions: List[int]) -> int:
    """
    Itera sobre una lista de enteros y devuelve el entero (resolución) seleccionada por el usuario.
    """
    print("Seleccione la resolución:")
    for index, resolution in enumerate(resolutions):
        index += 1
        print(index, resolution)

    user_input = int(input("\n>>>"))
    index = user_input-1
    print(":", resolutions[index], "\n")
    return resolutions[index]


def get_url_of_segments():
    """
    Devuelve la URL de la transmisión en vivo en la resolución especificada. Es una URL que contiene las URLs de los segmentos.
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


def capture(tvshow: dict):
    """
    Captura la transmision en vivo  
    """
    url, resolution = get_url_of_segments()

    # minutos extras para agregarlos a end porque la finalizaicón del programa no es exacta.
    extraminutes= 6
    title = tvshow["title"]
    day = datetime.now().strftime("%d-%m-%y")    
    ending_time_str= tvshow["end"] +" - "+ datetime.now().strftime("%d %B, %Y") 
    ending_time_object = datetime.strptime(ending_time_str, "%I:%M%p - %d %B, %Y") + timedelta(minutes=extraminutes)
    start = datetime.now()

    folder = f"{title} {str(resolution)}_{day}_{start.strftime('%I%M%p')}-{ending_time_object.strftime('%I%M%p')}+{str(extraminutes)}min"

    path = os.path.join(SEGMENT_FOLDER, folder)
    if not os.path.exists(path):
        os.makedirs(path)

    waiting(tvshow)
    while ending_time_object > datetime.now():
        print("Downloading...", folder, end="\r")
        download_playlist(url, path)
        time.sleep(45)

    return folder


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
