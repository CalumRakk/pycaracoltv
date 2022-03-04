import requests
import m3u8
import time
import re
import os

url = "https://mdstrm.com/live-stream-playlist/574463697b9817cf0886fc17.m3u8"

payload={}
headers = {
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
# m3u8 master playlist
response = requests.get(url, headers=headers)

url = response.text.split()[-1] # url media playlist
while True:      
    response = requests.get(url, headers=headers) # m3u8 media playlist  
    
    m3u8_media = m3u8.loads(response.text)  
    for segment in m3u8_media.segments:
        with open("test.mp4", "ab") as f:
            f.write(requests.get(segment.uri, headers=headers).content)
    
    # for segment in m3u8_media.segments:
    #     name= re.search("media.*ts", segment.uri).group()
    #     if not os.path.exists(name):
    #         with open(name, "wb") as f:
    #             f.write(requests.get(segment.uri, headers=headers).content) 
    #     else:
    #         print("File already exists: " + name)    
        
    time.sleep(75)