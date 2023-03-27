from utils import (
    capture,
    select_tvshow,
    concatenate_segments,
    get_schedule_day,
    HEADERS,
    session,
    get_filename,
    TvShow,
)

from queue import Queue
from threading import Thread
import os
import m3u8
import time
from m3u8 import M3U8
import csv
from datetime import datetime, timedelta


WORKTABLE = r"D:\.TEMP\caracoltv"


class Folder:
    def __init__(self, path) -> None:
        self.path = path
    
    @property
    def segments(self):
        attr = "__segments"        
        if hasattr(self, attr) is False:            
            setattr(self, attr, Segments(self))            
        return getattr(self,attr)
    
    def __str__(self) -> str:
        return self.path

class Segments:
    def __init__(self, folder: Folder) -> None:
        self.folder = folder

        self.dirname="segments"
        self.filename="segments.csv"
        self.path_csv= os.path.join(folder.path, self.filename) # path del archivo csv que guarda un registro de segmentos.
    @property
    def class_name(self):
        return self.__class__.__name__ 
     
    def __getattr__(self, attr): 
        class_name = self.class_name  
        # Se añade adelante el nombre de la clase para que el nombre de los atributos encaje con el enmascaramiento de nombre natural de Python    
        if f"_{class_name}__files" == attr:
            files=[]          
            if os.path.exists(self.path_csv):
                with open(self.path_csv, newline="") as archivo_csv:
                    lector_csv = csv.DictReader(archivo_csv)                    
                    for fila in lector_csv:
                        files.append(fila)
            setattr(self, attr, files)  
            return self.__dict__[attr]      
        elif f"_{class_name}__filenames" == attr:
            filenames=[file["filename"] for file in self.files]
            setattr(self, attr, filenames)
            return self.__dict__[attr]
        elif f"_{class_name}__path" == attr:
            path= os.path.join(self.folder.path, self.dirname) # carpeta donde se guardan los segmentos            
            if not os.path.exists(path):
                os.makedirs(path)
            setattr(self, attr, path)
            return self.__dict__[attr]
    @property
    def path(self):
        class_name = self.__class__.__name__
        return getattr(self, f"_{class_name}__path")
       
    @property
    def files(self)->list:
        class_name = self.__class__.__name__
        return getattr(self, f"_{class_name}__files")  
        
    @property
    def filenames(self)->list:
        class_name = self.__class__.__name__
        return getattr(self, f"_{class_name}__filenames")
    
    def exists(self, segment):
        filename = get_filename.search(segment.uri).group()
        return filename in self.filenames
    
    def add(self, segment):
        url = segment.uri
        filename = get_filename.search(url).group()

        path = os.path.join(self.path, filename)
        
        response = session.get(url, headers=HEADERS)
        with open(path, "wb") as f:
            f.write(response.content)
        
        file= {"filename":filename, "url":url}
        self.files.append(file)
        self.filenames.append(file["filename"])
        return file
    
    def save(self):
        with open(self.path_csv, 'w', newline='') as archivo_csv:
            campos = ['filename', 'url']
            escritor_csv = csv.DictWriter(archivo_csv, fieldnames=campos)

            escritor_csv.writeheader()            
            rows=[{"filename":row["filename"], "url":row["url"]} for row in self.files]            
            escritor_csv.writerows(rows)

        

    def save_segments(self, segments):
        pass
    
    def __str__(self) -> str:
        return self.path
    
    def _download_segment(self, url, path):
        response = session.get(url, headers=HEADERS)
        with open(path, "wb") as f:
            f.write(response.content)
            return True

def congelar(segundos):
    inicio = datetime.now()
    fin = inicio + timedelta(seconds=segundos)
    while datetime.now() < fin:
        segundos_faltantes = int((fin - datetime.now()).total_seconds())
        print(segundos_faltantes, end='\r')
        time.sleep(1)


def capture(tvshow: TvShow, quality):
    """
    Captura la transmision en vivo
    """
    title= tvshow.title.replace(" ","_")
    time_= tvshow.source_time.replace(" ","").replace(":",".")
    dirname= f"{title}_{quality}p_{datetime.now().strftime('%d-%m-%y')}_{time_}"
    folder = Folder(os.path.join(WORKTABLE, dirname))

    url = "https://mdstrm.com/live-stream-playlist/574463697b9817cf0886fc17.m3u8"

    response = session.get(url, headers=HEADERS)
    m3u8_media = m3u8.loads(response.text)

    url_playlist = m3u8_media.playlists[-1].uri
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
        congelar(45)


def schedule():
    schedule_day = get_schedule_day()
    tvshow = select_tvshow(schedule_day)

    qualities = []
    if len(qualities) < 2:
        capture(tvshow, quality=720)

    else:
        numero_de_hilos = len(qualities)
        queue = Queue(maxsize=3)
        hilos = []
        resultados = []
        for index in range(0, numero_de_hilos):
            hilos.append(Thread(target=capture, args=(tvshow, qualities[index])))

        for hilo in hilos:
            hilo.start()


schedule()
