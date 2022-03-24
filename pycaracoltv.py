from isort import file
import requests
import json
import m3u8
from m3u8.model import M3U8
import numpy as np
import threading
import re
import os
url = "https://eu-gateway.inmobly.com/feed?season_id=MTI6ZTQyNTU2M2VjYjUwNGJjY2I5ZWE5ZDc2NTI2Mzg4Njc="
headers = {
  'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
  'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2NDgxODM3ODUsImlhdCI6MTY0ODA5NzM4NSwibmJmIjoxNjQ4MDk3Mzg1LCJzdWIiOnsiYXBwbGljYXRpb24iOnsibWVkaWF0aW9uX2FwcF9zZWNyZXQiOiI2NGRlYzAwYTY5ODliYTgzZDA4NzYyMTQ2NWI1ZTVkMzhiZGFjMjIwMzNiMDYxM2I2NTljNDQyYzc4OTc2ZmEwIiwiYXBwX2lkZW50aWZpZXIiOiI3OTVjZDljMDg5YTFmYzQ4MDk0NTI0YTVlYmE4NWEzZmNhMTMzMTgxN2M4MDJmNjAxNzM1OTA3YzhiYmI0ZjUwIiwiaWQiOjE0LCJleHRlcm5hbF9rZXkiOiIiLCJhcHBfY29uZmlnIjp7Imxhbmd1YWdlIjp7ImRlZmF1bHQiOnsia2V5IjoiZXMiLCJuYW1lIjoiU3BhbmlzaCJ9LCJsYW5ndWFnZXMiOlt7ImtleSI6ImVzIiwibmFtZSI6IlNwYW5pc2gifV19LCJkZWZhdWx0X3BsYW5zIjp7ImVuIjp7IjMwIjoiTW9udGhseSIsIjE4MCI6IkJpYW5udWFsIiwiMzY1IjoiWWVhcmx5In0sImVzIjp7IjMwIjoiTW9udGhseSIsIjE4MCI6IkJpYW5udWFsIiwiMzY1IjoiWWVhcmx5In19LCJlbWFpbF9jb25maXJtYXRpb24iOiIxIiwiYXV0aGVudGljYXRpb25fcHJvdmlkZXJfY29uZmlybWF0aW9uIjpmYWxzZX19fX0.W3oQfI8CI_OE15HtzSgev4fMtyucGa7nOw2cT2SDkb4',
  'Content-Type': 'application/json',
  'sec-ch-ua-mobile': '?0',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36',
  'sec-ch-ua-platform': '"Windows"',
  'Country-Code': 'CO',
  'Accept': '*/*'
}

response = requests.get(url, headers=headers)
document=json.loads(response.text)['items']
regex= re.compile(r'seg-.*?\.ts') 
worktable= "segments"

def index_exists(list_, chapter):
    try:
        list_[chapter]
        return True
    except IndexError:
        return False
    
with open("chapter.txt","r") as file:
    chapter= int(file.read())-1

def best_quality(m3u8:M3U8):
    """Devuelve la URL de la mejor calidad de un m3u8 master"""
    height=(element.stream_info.resolution[0] for element in m3u8.playlists)
    best= max(height)
    for element in m3u8.playlists:
        if element.stream_info.resolution[1]==best:
            return element.uri       
def filter(m3u8:M3U8, resolution:int):
    """Filtra una lista de playlists para obtener solo las de video"""
    for element in m3u8.playlists:
        if element.stream_info.resolution[1]==resolution:
            return element.uri
    raise ValueError("No se encontró la resolución")
def a_thread_func(part):    
    for element in part:
        filename= regex.search(element).group()
        response = requests.get(element, headers=headers)
        with open(f"{worktable}{filename}", "wb") as file:
            file.write(response.content)  
        print(filename)  
def concatenate(segments):

    with open("video.ts","wb") as video:
        for segment in segments:
            filename= regex.search(segment).group()
            
            with open(f"{worktable}{filename}", "rb") as file:
                video.write(file.read())
            os.remove(f"{worktable}{filename}")
                
if index_exists(document, chapter):
    url= document[chapter]["download_url"] 
    response = requests.get(url, headers=headers)
    m3u8_obj = m3u8.loads(response.text)
    
    url= filter(m3u8_obj,480)
    response = requests.get(url, headers=headers)
    m3u8_obj = m3u8.loads(response.text)
    m3u8_obj.segments.uri
    part1,part2,part3= np.array_split(m3u8_obj.segments.uri, 3)
       
    t1 = threading.Thread(target=a_thread_func, args=(part1,))
    t2 = threading.Thread(target=a_thread_func, args=(part2,))
    t3 = threading.Thread(target=a_thread_func, args=(part3,))

    t1.start()    
    t2.start()   
    t3.start()    
    t1.join()
    t2.join()
    t3.join()
    
    concatenate(m3u8_obj.segments.uri)

