
from utils import capture, select_tvshow,concatenate_segments,get_schedule_day, HEADERS, session,get_filename

from queue import Queue
from threading import Thread
import os
import m3u8
import time
from m3u8 import M3U8

def capture(tvshow, quality):
    """
    Captura la transmision en vivo  
    """
    url = "https://mdstrm.com/live-stream-playlist/574463697b9817cf0886fc17.m3u8"

    response = session.get(url, headers=HEADERS)
    m3u8_media = m3u8.loads(response.text)

    url_playlist= m3u8_media.playlists[-1].uri
    while True:        
        response = session.get(url_playlist, headers=HEADERS)  # m3u8 media playlist
        try: 
            m3u8_playlist = m3u8.lo1ads(response.text)
        except ValueError:
            # Cuando se está en publicidad las urls de segmentos no funcionan para descargarse
            pass

        for segment in m3u8_playlist.segments:
            filename = get_filename.search(segment.uri).group()
            path = os.path.join("segments", filename)                
            with open(path, 'wb') as f:
                f.write(session.get(segment.uri, headers=HEADERS).content)
            print(filename)
        time.sleep(45)

def schedule():    
    schedule_day= get_schedule_day()
    tvshow= select_tvshow(schedule_day)

    qualities=[]
    if len(qualities)<2:
        capture(tvshow, quality=0)

    else:
        numero_de_hilos = len(qualities)
        queue = Queue(maxsize=3)
        hilos=[]
        resultados= []
        for index in range(0, numero_de_hilos):   
            hilos.append(Thread(target=capture, args=(tvshow, qualities[index])))
        
        for hilo in hilos: hilo.start()


schedule()