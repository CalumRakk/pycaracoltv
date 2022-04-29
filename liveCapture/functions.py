import requests
from bs4 import BeautifulSoup
from datetime import datetime,timedelta
import m3u8
import re

from typing import List
import time
import os
import sys
get_filename= re.compile("media_.*?.ts")

OUT= "segments"
EXT_TS= ".ts"

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

def get_tvshow()-> List[dict]:
    response = requests.get("https://www.caracoltv.com/programacion", headers=HEADERS)

    # Captura la programación del día
    soup = BeautifulSoup(response.text, 'html.parser')
    programacion=[]
    for tr in soup.find('tbody').find_all("tr"):
        programa, time= tr.find("a").get("title").split("-",1)
        
        document={
            "title": programa.strip(),
            "time": time.strip(),            
        }
        programacion.append(document)
    return programacion

def print_tvshow(programacion: List[dict])-> None:
    if sys.platform.startswith('linux'):
        os.system("clear")
    else:
        os.system("cls")
        
    for index, programa in enumerate(programacion):
        index+=1
        print(index, programa["title"], programa["time"])     

def select_tvshow(programacion:List[dict])-> dict:
    """
    Devuelve el tiempo de esperar para capturar el programa
    """
    print_tvshow(programacion)
     
    user_input= int(input("\nSeleccione el programa>>>"))
    index= user_input-1
    title= programacion[index]["title"]
    time= programacion[index]["time"]
    
    start,end = time.split("-")
    document= {
        "title": title,
        "time": time,
        "start": start,
        "end": end,
    }
    return document
    
def waiting(programa:dict)-> None:
    """
    Espera hasta que el programa empiece
    """
    start= datetime.strptime(programa["start"], '%I:%M%p')
    
    difference= start-datetime.now()        
    if difference.days==0:
        print("El programa inicia a las:", start.strftime("%I:%M%p"))
        time.sleep(difference.seconds+2)

def get_url():
    """
    Devuelve la URL en 720p de la transmisión en vivo
    """
    url = "https://mdstrm.com/live-stream-playlist/574463697b9817cf0886fc17.m3u8"

    # m3u8 master playlist
    response = requests.get(url, headers=HEADERS)
    
    m3u8_media= m3u8.loads(response.text)    
    return m3u8_media.playlists[-1].uri 
def download_playlist(url:str)-> None:  
    response = requests.get(url, headers=HEADERS) # m3u8 media playlist  

    m3u8_media = m3u8.loads(response.text) 
    for segment in m3u8_media.segments:
        url= segment.uri
        
        filename=get_filename.search(url).group()
        path= f"{OUT}/{filename}"
        if not os.path.isfile(path):
            with open(path, 'wb') as f:
                f.write(requests.get(segment.uri, headers=HEADERS).content)
        
    time.sleep(75)
     
def capture(programa:dict):
    """
    Inicia un Bucle de captura de la transmisión en vivo
    programa: Diccionario que contiene la hora de inicio y fin del programa
    """
    
    waiting(programa)
            
    url = get_url()
    
    title= programa["title"]
    day= datetime.now().strftime("%d-%m-%y")
    end= datetime.now().strptime(programa["end"], '%I:%M%p')
    start= datetime.now()
    
    filename= f"{title} {day}_{start.strftime('%I%M%p')}-{end.strftime('%I%M%p')}+10min.ts"
    
    while datetime.now() < end or (end < datetime.now()):
        download_playlist(url) 
    
    return filename
        
def concatenate_segments(filename:str)-> None:
    """
    filename: nombre final del video.
    """
    filename= filename+EXT_TS
    path= os.path.join(os.getcwd(), filename)
    with open(path, 'wb') as file:  
        for string in os.listdir(OUT):
            path= f"{OUT}/{string}"
            with open(path, 'br') as video:
                file.write(video.read())
              
        
        